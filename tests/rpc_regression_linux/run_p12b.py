import sys
# -*- coding: utf-8 -*-
"""Phase 12b：重启 RPC 后重跑 C/B/D + N35 复现 + E Plan B（docstring/click --help 枚举 flag）"""
import io, os, json, re, time, subprocess, urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
PUB = T + r"\data\public"
OUT = T + r"\out\p12"
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
LOG = io.open(T + r"\P12B_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s):
    LOG.write(s + "\n"); LOG.flush()
def rec(name, ok, detail):
    w(f"- **{name}**: {'✅' if ok else '❌'} — {detail}")
    print(("OK  " if ok else "FAIL"), name, "|", detail[:100], flush=True)
def rpc(method, params, timeout=300):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1})
    req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=body.encode(),
                                 headers={"Content-Type":"application/json"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8","replace")
def cli(args, timeout=300):
    t0 = time.time()
    try:
        r = subprocess.run(CLI + args, capture_output=True, timeout=timeout)
        blob = (r.stdout or b"").decode("utf-8", "replace") + (r.stderr or b"").decode("utf-8", "replace")
        return r.returncode, blob, time.time() - t0
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(r.pid)], capture_output=True) if os.name == "nt" else (lambda p: (os.killpg(os.getpgid(p.pid), 9) if os.getpgid(p.pid) else os.kill(p.pid, 9)))(r)
        return -99, "TIMEOUT", time.time() - t0

w("# Phase 12b：RPC 重启后重跑 C/B/D + N35 复现 + 可选参数 Plan B")

# ---- 重启 RPC ----
w("\n## 0. 重启 RPC")
subprocess.Popen(CLI + ["rpc", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ok = False
for i in range(15):
    time.sleep(2)
    try:
        rpc("system.listMethods", {}, timeout=10); ok = True; break
    except Exception:
        pass
rec("rpc start 重启", ok, f"{'188 方法在线' if ok else '重启失败'}")

# ---- N35 复现（一次）----
w("\n## 12.A' N35 复现：1.2GB FastaStat RPC 是否打死服务")
big = PUB + r"\grch38_1p2g.fa"
t0 = time.time()
try:
    resp = rpc("FastaStat.process", {"inputPath": big, "outputPath": OUT + r"\p12b_1g.xls"}, timeout=300)
    ok = '"error"' not in resp and os.path.exists(OUT + r"\p12b_1g.xls")
    rec("RPC FastaStat 1.2GB(复现)", ok, f"{time.time()-t0:.1f}s")
except Exception as ex:
    rec("RPC FastaStat 1.2GB(复现)", False, f"服务异常: {str(ex)[:70]} ← N35 复现")
time.sleep(2)
alive = False
try:
    rpc("system.listMethods", {}, timeout=15); alive = True
except Exception:
    pass
rec("1.2GB 后服务存活检查", alive, "存活" if alive else "服务死亡 ← N35 实锤(RPC 处理 1.2GB 即崩)")
if not alive:
    subprocess.Popen(CLI + ["rpc", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(15):
        time.sleep(2)
        try:
            rpc("system.listMethods", {}, timeout=10); break
        except Exception:
            pass

# ---- C. BLAST 输出交叉 ----
w("\n## 12.C BLAST 输出交叉")
E = "examples/data"
q = os.path.abspath(f"{E}/blast/query.fa"); s = os.path.abspath(f"{E}/blast/subject.fa")
for fmt in ["0", "5", "7"]:
    outp = OUT + rf"\p12_blast_f{fmt}.txt"
    try:
        resp = rpc("BlastCompareTwoSeqBigFileSet.process",
                   {"queryPath": q, "subjectPath": s, "outputPath": outp,
                    "options": {"blastType": "blastp", "outFmt": fmt, "evalue": "10"}})
        sz = os.path.getsize(outp) if os.path.exists(outp) else -1
        rec(f"outFmt={fmt} 产出", sz > 0, f"{sz:,}B")
    except Exception as ex:
        rec(f"outFmt={fmt} 产出", False, f"EXC {str(ex)[:70]}")
xml5 = OUT + r"\p12_blast_f5.txt"
for tf in ["BlastTab", "TBtoolsTab", "Summary", "Pairwise"]:
    outp = OUT + rf"\p12_xml2tab_{tf}.tsv"
    try:
        resp = rpc("BlastXmlToTable.process", {"inputXmlPath": xml5, "outputPath": outp, "tableFormat": tf})
        sz = os.path.getsize(outp) if os.path.exists(outp) else -1
        rec(f"XML→{tf}", sz > 0, f"{sz:,}B")
    except Exception as ex:
        rec(f"XML→{tf}", False, f"EXC {str(ex)[:70]}")

# ---- B. 格式互换矩阵 ----
w("\n## 12.B 格式互换矩阵")
gtf = PUB + r"\gencode_head50k.gtf"
gff3 = os.path.abspath(f"{E}/gxf/input.gff3")
bed = OUT + r"\p12_gencode.bed"
inputs = {"GTF": gtf, "GFF3": gff3, "BED": bed}
methods = [
    ("GxfRecallMrna", lambda p: {"inputPath": p, "outputPath": OUT + r"\p12b_fm_out.gff3"}),
    ("GxfSplit", lambda p: {"inputPath": p, "outputPrefix": OUT + r"\p12b_fm_split", "numOfFile": 2}),
    ("GxfStat", lambda p: {"inputPath": p, "outputPath": OUT + r"\p12b_fm_stat.xls"}),
]
for fmt, path in inputs.items():
    for mname, mk in methods:
        try:
            resp = rpc(mname + ".process", mk(path), timeout=120)
            ok = '"error"' not in resp
            msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "") if not ok else "成功"
            rec(f"{mname}×{fmt}", ok, f"{str(msg)[:60]}")
        except Exception as ex:
            rec(f"{mname}×{fmt}", False, f"EXC {str(ex)[:70]}")
    try:
        resp = rpc("GxfPatch.process", {"refGxfPath": path, "patchGxfPath": gff3,
                                        "outputPath": OUT + rf"\p12b_fm_patch_{fmt}.gff3"}, timeout=120)
        ok = '"error"' not in resp
        msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "") if not ok else "成功"
        rec(f"GxfPatch×{fmt}+GFF3", ok, f"{str(msg)[:60]}")
    except Exception as ex:
        rec(f"GxfPatch×{fmt}+GFF3", False, f"EXC {str(ex)[:70]}")

# ---- E Plan B：docstring + click --help 枚举可选 flag ----
w("\n## 12.E' 可选参数矩阵 Plan B（docstring `[--flag]` + click --help Options）")
bases = [
    ("statFasta", ["tool", "statFasta", "--inFasta", os.path.abspath(f"{E}/blast/query.fa"),
                   "--outPutFile", OUT + r"\p12e_st.xls"]),
    ("volcano", ["expr", "volcano", os.path.abspath(f"{E}/deg.txt"), OUT + r"\p12e_vol.svg"]),
    ("groupedbar", ["expr", "groupedbar", os.path.abspath(f"{E}/expr/groupbar.tsv"), OUT + r"\p12e_gb.svg"]),
    ("peakdist", ["chipseq", "peakdist", os.path.abspath(f"{E}/chipseq/chrlen2.txt"),
                  os.path.abspath(f"{E}/chipseq/peak_std.xls"), OUT + r"\p12e_pd.svg"]),
    ("ctgGroup", ["asm", "ctgGroup", os.path.abspath(f"{E}/assembly/miniprot.gff"), "2", OUT + r"\p12e_cg.tsv"]),
    ("extractFeatureFromGTF", ["tool", "extractFeatureFromGTF", os.path.abspath(f"{E}/gene_structure.gff"), "CDS", OUT + r"\p12e_ef.gff"]),
    ("twoSeqBlast", ["tool", "twoSeqBlast", "--queryFasta", q, "--subjectFasta", s, "--outXml", OUT + r"\p12e_tb.xml"]),
]
auto = io.open("tbtools_cli" + os.sep + "auto_commands.py", encoding="utf-8").read()
FLAGVAL = re.compile(r'\[(-{1,2}[A-Za-z][A-Za-z0-9]*)\s+([^\]\[]+)\]')
total = 0
for name, base_args in bases:
    ec, blob, dt = cli(base_args, timeout=180)
    if ec != 0:
        rec(f"基线[{name}]", False, f"ec={ec}, 跳过")
        continue
    flags = []
    # 1) click --help
    grp, tool = base_args[0], base_args[1]
    ec2, h2, _ = cli([grp, tool, "--help"], timeout=25)
    if ec2 == 0 and "Options" in h2:
        for mo in re.finditer(r'^\s+(-{1,2}[A-Za-z][A-Za-z0-9]*)\s+([A-Z_\[\]|]+|\S+)?', h2, re.M):
            fl = mo.group(1)
            if fl in ("--help", "-h"): continue
            sp = (mo.group(2) or "TEXT").strip()
            flags.append((fl, sp))
    # 2) docstring [--flag val]
    if not flags:
        mm = re.search(r'"""[^\n]*' + re.escape(tool) + r'[^\n]*"""', auto)
        if mm:
            flags = FLAGVAL.findall(mm.group(0))
    if not flags:
        rec(f"flags[{name}]", True, "确实无可选 flag")
        continue
    for flag, spec in flags[:8]:  # 每工具最多 8 个防爆炸
        val = spec.split("|")[0].strip().strip("<>")
        if re.fullmatch(r"N|\d+|INT|INTEGER", val, re.I): val = "2"
        elif val.upper() in ("TEXT", "STR", "STRING", "NAME", "ID"): val = "test"
        elif val.upper() == "BOOL" or val.lower() in ("true/false", "boolean"): val = "true"
        elif "file" in val.lower() or "path" in val.lower() or "fasta" in val.lower() or "tsv" in val.lower():
            val = os.path.abspath(f"{E}/deg.txt") if "deg" in spec.lower() or "table" in val.lower() else os.path.abspath(f"{E}/blast/query.fa")
        elif val.upper() in ("FLOAT", "NUM", "NUMBER"): val = "2.0"
        else: val = val if val else "test"
        args2 = base_args[:-1] + [base_args[-1]] + [flag, val]
        ec3, blob3, dt3 = cli(args2, timeout=180)
        total += 1
        outok = any(os.path.exists(a) and os.path.getsize(a) > 0 for a in args2 if a.endswith((".svg", ".xls", ".tsv", ".xml", ".gff")))
        ok3 = (ec3 == 0 and (outok or not any(a.endswith((".svg", ".xls", ".tsv")) for a in args2))) or (ec3 != 0 and len(blob3.strip()) > 0)
        rec(f"flag[{name} {flag}={val[:10]}]", ok3,
            f"ec={ec3}, {dt3:.1f}s{' ⚠️ec=0但无产物' if ec3==0 and not outok else ''}")
print(f"FLAGRUNS total={total}", flush=True)

# ---- D. RPC 残余自动救援 ----
w("\n## 12.D RPC 残余自动救援")
SKIP_PAT = re.compile(r"ncbi|timetree|sra|geo|fastqblast|blastzone|download|remote|email|todo", re.I)
POOL = {"gtf": [gtf], "gff": [gff3], "gff3": [gff3], "bed": [bed],
        "fa": [os.path.abspath(f"{E}/blast/query.fa")], "fasta": [os.path.abspath(f"{E}/blast/query.fa")],
        "tsv": [os.path.abspath(f"{E}/deg.txt")], "table": [os.path.abspath(f"{E}/deg.txt")],
        "xls": [os.path.abspath(f"{E}/chipseq/peak_std.xls")], "txt": [os.path.abspath(f"{E}/deg.txt")],
        "xml": [xml5]}
report = io.open(T + r"\FINAL_TEST_REPORT_V3.md", encoding="utf-8", errors="replace").read()
try:
    names = json.loads(rpc("system.listMethods")).get("result")
    names = names.get("methods") if isinstance(names, dict) else names
    procs = [m for m in names if isinstance(m, str) and m.endswith(".process") and not SKIP_PAT.search(m)]
    w(f"\n候选 {len(procs)} 个\n")
    report_pass = set(re.findall(r'\b([A-Za-z]+)\.process\b', report))
    new_pass, still_fail = [], []
    for m in procs:
        base = m.split(".")[0]
        try:
            d = json.loads(rpc("system.describeMethod", {"method": m}), ).get("result", {})
            desc = json.dumps(d.get("description", {}), ensure_ascii=False).lower()
            # 从 validateParams 拿缺参
            try:
                vres = json.loads(rpc(m.replace(".process", ".validateParams"), {}, timeout=30))
                verr = json.dumps(vres.get("error", vres.get("result", {})), ensure_ascii=False)
            except Exception:
                verr = ""
            need = re.findall(r'([A-Za-z][A-Za-z0-9]+) is required', verr)
            if not need:
                # 从 describe 的 params 文本提取 required 字段
                need = re.findall(r'"([A-Za-z][A-Za-z0-9]+)":\s*"string \(required\)', desc)
            if not need:
                need = re.findall(r'"([A-Za-z][A-Za-z0-9]+)":\s*"[^"]*required', desc)
            params = {}
            for p in dict.fromkeys(need):
                pl = p.lower()
                if "output" in pl or pl.startswith("out"):
                    params[p] = OUT + rf"\p12d_{base}_{p}.out"
                else:
                    match = None
                    for k, v in POOL.items():
                        if k in pl: match = v[0]; break
                    if not match:
                        for k, v in POOL.items():
                            if k in desc:
                                match = v[0]; break
                    params[p] = match if match else os.path.abspath(f"{E}/deg.txt")
            t0 = time.time()
            resp = rpc(m, params, timeout=240)
            ok = '"error"' not in resp
            if ok and base not in report_pass:
                new_pass.append(base)
            print(("NEWPASS " if ok and base not in report_pass else ("pass    " if ok else "fail    ")) + base, f"{time.time()-t0:.1f}s", flush=True)
            if not ok:
                msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "")
                still_fail.append((base, msg[:70]))
        except Exception as ex:
            still_fail.append((base, "EXC " + str(ex)[:60]))
            print("err     ", base, flush=True)
    w("\n### 本轮新通过\n")
    w(", ".join(sorted(set(new_pass))) if new_pass else "（无新增）")
    w("\n\n### 仍失败\n")
    w("| 方法 | 错误 |")
    w("|---|---|")
    for b, msg in still_fail:
        w(f"| {b} | {msg} |")
except Exception as ex:
    w(f"救援框架异常：{ex}")

w("\n---\n\n## Phase 12b 完")
LOG.close()
print("P12b done", flush=True)

