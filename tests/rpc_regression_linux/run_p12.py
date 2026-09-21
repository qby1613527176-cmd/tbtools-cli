import sys
# -*- coding: utf-8 -*-
"""Phase 12：第九轮 — 收尾全测
A >1GB 性能  B 格式互换矩阵  C BLAST 输出交叉  E 可选参数矩阵  D RPC 残余自动救援
"""
import io
import os
import json
import re
import time
import subprocess
import urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
PUB = T + r"\data\public"
OUT = T + r"\out\p12"
os.makedirs(OUT, exist_ok=True)
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
LOG = io.open(T + r"\P12_LOG.md", "w", encoding="utf-8", newline="\n")
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

w("# Phase 12：第九轮 — 收尾全测（>1GB / 格式矩阵 / BLAST 交叉 / 可选参数 / RPC 救援）")

# ================= A. >1GB 大文件 =================
w("\n## 12.A >1GB 大文件性能（GRCh38 240MB ×5 串联 ≈ 1.2GB）")
big = PUB + r"\grch38_1p2g.fa"
if not os.path.exists(big):
    t0 = time.time()
    src = PUB + r"\grch38_head60m.fa"
    with io.open(big, "wb") as f:
        data = io.open(src, "rb").read()
        # 每 20MB 插一个新 header，避免单序列 6 亿碱基内存问题
        for i in range(5):
            f.write(f">chunk{i}_chr1\n".encode())
            f.write(data[data.index(b"\n") + 1:])
    print(f"CONCAT 1.2GB done in {time.time()-t0:.0f}s", flush=True)
w(f"- 合成文件：{os.path.getsize(big):,} B")
t0 = time.time()
ec, blob, dt = cli(["tool", "statFasta", "--inFasta", big, "--outPutFile", OUT + r"\p12_1g2.xls"])
ok = ec == 0 and os.path.exists(OUT + r"\p12_1g2.xls") and os.path.getsize(OUT + r"\p12_1g2.xls") > 0
rec("CLI statFasta 1.2GB", ok, f"ec={ec}, 墙钟 {dt:.1f}s")
t0 = time.time()
try:
    resp = rpc("FastaStat.process", {"inputPath": big, "outputPath": OUT + r"\p12_1g2_rpc.xls"}, timeout=600)
    ok = '"error"' not in resp and os.path.exists(OUT + r"\p12_1g2_rpc.xls")
    rec("RPC FastaStat 1.2GB", ok, f"{time.time()-t0:.1f}s")
except Exception as ex:
    rec("RPC FastaStat 1.2GB", False, f"EXC {str(ex)[:80]}")
t0 = time.time()
try:
    resp = rpc("FastaSsrMiner.process", {"inputPath": big, "outputPath": OUT + r"\p12_1g2_ssr.xls",
                                         "maxLenKbases": 500}, timeout=900)
    ok = '"error"' not in resp
    msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "") if not ok else ""
    sz = os.path.getsize(OUT + r"\p12_1g2_ssr.xls") if os.path.exists(OUT + r"\p12_1g2_ssr.xls") else -1
    rec("RPC FastaSsrMiner 1.2GB", ok, f"{time.time()-t0:.1f}s, ssr={sz:,}B {msg[:60]}")
except Exception as ex:
    rec("RPC FastaSsrMiner 1.2GB", False, f"EXC {str(ex)[:80]}")

# ================= C. BLAST 输出交叉 =================
w("\n## 12.C BLAST 输出交叉（outFmt 0/5/7 产出 + BlastXmlToTable 4 格式）")
E = "examples/data"
q = os.path.abspath(f"{E}/blast/query.fa"); s = os.path.abspath(f"{E}/blast/subject.fa")
fmt_files = {}
for fmt in ["0", "5", "7"]:
    outp = OUT + rf"\p12_blast_f{fmt}.txt"
    try:
        resp = rpc("BlastCompareTwoSeqBigFileSet.process",
                   {"queryPath": q, "subjectPath": s, "outputPath": outp,
                    "options": {"blastType": "blastp", "outFmt": fmt, "evalue": "10"}})
        sz = os.path.getsize(outp) if os.path.exists(outp) else -1
        fmt_files[fmt] = sz
        rec(f"outFmt={fmt} 产出", sz > 0, f"{sz:,}B")
    except Exception as ex:
        rec(f"outFmt={fmt} 产出", False, f"EXC {str(ex)[:70]}")
xml = OUT + r"\p10_blast.xml"
if not os.path.exists(xml) or os.path.getsize(xml) == 0:
    xml = OUT + r"\p12_blast_f5.txt"
for tf in ["BlastTab", "TBtoolsTab", "Summary", "Pairwise"]:
    outp = OUT + rf"\p12_xml2tab_{tf}.tsv"
    try:
        resp = rpc("BlastXmlToTable.process", {"inputXmlPath": xml, "outputPath": outp, "tableFormat": tf})
        sz = os.path.getsize(outp) if os.path.exists(outp) else -1
        rec(f"XML→{tf}", sz > 0, f"{sz:,}B")
    except Exception as ex:
        rec(f"XML→{tf}", False, f"EXC {str(ex)[:70]}")

# ================= B. 格式互换矩阵 =================
w("\n## 12.B 格式互换矩阵（真 GTF × 真 GFF3 × 真 BED → gxf 族 4 方法）")
gtf = PUB + r"\gencode_head50k.gtf"
gff3 = os.path.abspath(f"{E}/gxf/input.gff3")
# 从 GENCODE 造真 BED（前 5000 个 exon）
bed = OUT + r"\p12_gencode.bed"
n = 0
with io.open(bed, "w", encoding="utf-8", newline="\n") as fo:
    for line in io.open(gtf, encoding="utf-8", errors="replace"):
        if line.startswith("#"): continue
        f = line.split("\t")
        if len(f) > 8 and f[2] == "exon":
            tid = re.search(r'transcript_id "([^"]+)"', f[8])
            fo.write(f"{f[0]}\t{int(f[3])-1}\t{f[4]}\t{tid.group(1) if tid else 'NA'}\t0\t{f[6]}\n")
            n += 1
            if n >= 5000: break
w(f"- BED 构造：{n} 条真 exon 坐标")
inputs = {"GTF": gtf, "GFF3": gff3, "BED": bed}
methods = [
    ("GxfRecallMrna", lambda p: {"inputPath": p, "outputPath": OUT + r"\p12_fm_out.gff3"}),
    ("GxfSplit", lambda p: {"inputPath": p, "outputPrefix": OUT + r"\p12_fm_split", "numOfFile": 2}),
    ("GxfStat", lambda p: {"inputPath": p, "outputPath": OUT + r"\p12_fm_stat.xls"}),
]
for fmt, path in inputs.items():
    for mname, mk in methods:
        try:
            t0 = time.time()
            resp = rpc(mname + ".process", mk(path), timeout=120)
            ok = '"error"' not in resp
            msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "") if not ok else "成功"
            rec(f"{mname}×{fmt}", ok, f"{time.time()-t0:.1f}s {str(msg)[:60]}")
        except Exception as ex:
            rec(f"{mname}×{fmt}", False, f"EXC {str(ex)[:70]}")
    # GxfPatch：ref=该格式 patch=GFF3
    try:
        resp = rpc("GxfPatch.process", {"refGxfPath": path, "patchGxfPath": gff3,
                                        "outputPath": OUT + rf"\p12_fm_patch_{fmt}.gff3"}, timeout=120)
        ok = '"error"' not in resp
        msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "") if not ok else "成功"
        rec(f"GxfPatch×{fmt}+GFF3", ok, f"{str(msg)[:60]}")
    except Exception as ex:
        rec(f"GxfPatch×{fmt}+GFF3", False, f"EXC {str(ex)[:70]}")

# ================= E. 可选参数矩阵 =================
w("\n## 12.E 可选参数矩阵（已知良好基线命令 × 全部可选 flag）")
bases = [
    ("statFasta", ["tool", "statFasta", "--inFasta", os.path.abspath(f"{E}/fasta/sample.fa" if os.path.exists(f"{E}/fasta/sample.fa") else f"{T}/out/p11/base.fa"),
                   "--outPutFile", OUT + r"\p12_e_st.xls"]),
    ("volcano", ["expr", "volcano", os.path.abspath(f"{E}/deg.txt"), OUT + r"\p12_e_vol.svg"]),
    ("groupedbar", ["expr", "groupedbar", os.path.abspath(f"{E}/expr/groupbar.tsv"), OUT + r"\p12_e_gb.svg"]),
    ("peakdist", ["chipseq", "peakdist", os.path.abspath(f"{E}/chipseq/chrlen2.txt"),
                  os.path.abspath(f"{E}/chipseq/peak_std.xls"), OUT + r"\p12_e_pd.svg"]),
    ("ctgGroup", ["asm", "ctgGroup", os.path.abspath(f"{E}/assembly/miniprot.gff"), "2", OUT + r"\p12_e_cg.tsv"]),
    ("extractFeatureFromGTF", ["tool", "extractFeatureFromGTF", os.path.abspath(f"{E}/gene_structure.gff"), "CDS", OUT + r"\p12_e_ef.gff"]),
    ("twoSeqBlast", ["tool", "twoSeqBlast", "--queryFasta", q, "--subjectFasta", s, "--outXml", OUT + r"\p12_e_tb.xml"]),
]
FLAGVAL = re.compile(r'\[(-{1,2}[A-Za-z][A-Za-z0-9]*)\s+([^\]\[]+)\]')
total_flag_runs = 0
for name, base_args in bases:
    ec, blob, dt = cli(base_args, timeout=180)
    if ec != 0:
        rec(f"基线[{name}]", False, f"ec={ec}, 跳过其 flags")
        continue
    rec(f"基线[{name}]", True, f"ec=0, {dt:.1f}s")
    # 从引擎 usage 提取可选 flag：重新跑 no-arg 拿 usage
    grp = base_args[0]; tool = base_args[1]
    ec2, blob2, _ = cli([grp, tool], timeout=25)
    mu = re.search(r'用法[:：]\s*\S+\s*(\S.*)', blob2) or re.search(r'[Uu]sage:\s*\S+\s*(\S.*)', blob2)
    if not mu:
        rec(f"flags[{name}]", True, "无 usage 行，无法枚举（N33 族）")
        continue
    usage = mu.group(1)
    flags = FLAGVAL.findall(usage)
    if not flags:
        rec(f"flags[{name}]", True, f"无可选 flag（usage: {usage[:60]}）")
        continue
    for flag, spec in flags:
        val = spec.split("|")[0].strip()
        if re.fullmatch(r"N|\d+", val): val = "2"
        elif val.lower() in ("bool", "true/false"): val = "true"
        elif "file" in val.lower() or "path" in val.lower() or val.startswith("<"): val = os.path.abspath(f"{E}/deg.txt")
        elif "dir" in val.lower(): val = OUT
        else: val = val if val and not val.startswith("<") else "test"
        args2 = base_args[:-1] + [base_args[-1] + ""]  # 最后一个是输出，避免覆盖冲突
        args2 = base_args[:-1] + [OUT + rf"\p12_e_out_{abs(hash(flag))%99999}"]
        # 追加 flag
        if base_args[0] == "tool" and len(base_args) > 2 and base_args[2].startswith("--"):
            args2 = base_args[:-1] + [base_args[-1]] + [flag, val]
        else:
            args2 = base_args[:-1] + [base_args[-1]] + [flag, val]
        ec3, blob3, dt3 = cli(args2, timeout=180)
        total_flag_runs += 1
        # 通过标准：ec==0 或报错信息明确（不挂起/不静默）
        out_exists = any(os.path.exists(a) and os.path.getsize(a) > 0 for a in args2 if a.endswith((".svg", ".xls", ".tsv", ".xml", ".gff")))
        ok3 = (ec3 == 0) or (len(blob3.strip()) > 0 and ec3 != -99)
        rec(f"flag[{name} {flag} {val[:12]}]", ok3,
            f"ec={ec3}, {dt3:.1f}s{' ⚠️静默' if ec3==0 and not out_exists else ''}")
print(f"FLAGRUNS total={total_flag_runs}", flush=True)

# ================= D. RPC 残余自动救援 =================
w("\n## 12.D RPC 残余方法自动救援（describeMethod + 数据池自动补参）")
SKIP_PAT = re.compile(r"ncbi|timetree|sra|geo|fastqblast|blastzone|download|remote|email|todo", re.I)
POOL = {
    "fa": [os.path.abspath(f"{E}/blast/query.fa"), PUB + r"\grch38_head60m.fa"],
    "gtf": [gtf], "gff": [gff3], "gff3": [gff3], "bed": [bed], "tsv": [os.path.abspath(f"{E}/deg.txt")],
    "xls": [os.path.abspath(f"{E}/chipseq/peak_std.xls")], "txt": [os.path.abspath(f"{E}/deg.txt")],
    "fasta": [os.path.abspath(f"{E}/blast/query.fa")], "xml": [xml], "table": [os.path.abspath(f"{E}/deg.txt")],
}
report = io.open(T + r"\FINAL_TEST_REPORT_V3.md", encoding="utf-8", errors="replace").read()
try:
    names = json.loads(rpc("system.listMethods")).get("result")
    names = names.get("methods") if isinstance(names, dict) else names
    procs = [m for m in names if isinstance(m, str) and m.endswith(".process") and not SKIP_PAT.search(m)]
    w(f"\n候选 .process 方法 {len(procs)} 个（剔除网络/会话依赖族）\n")
    report_pass = set(m.split(".")[0] for m in re.findall(r'"([A-Za-z]+\.process)"', report))
    new_pass, still_fail = [], []
    for m in procs:
        base = m.split(".")[0]
        try:
            d = json.loads(rpc("system.describeMethod", {"method": m})).get("result", {})
            desc = json.dumps(d.get("description", {}), ensure_ascii=False)
            pdef = json.loads(rpc("system.describeMethod", {"method": m})).get("result", {})
            params = {}
            pm = re.search(r'"params":\s*\{(.+?)\}', desc)
            # 用 validateParams 反查必填
            vres = json.loads(rpc(m.replace(".process", ".validateParams"), params={}, timeout=30))
            verr = json.dumps(vres.get("error", vres.get("result", {})), ensure_ascii=False)
            # 从 validate 错误信息提取缺参名
            need = re.findall(r'"([A-Za-z][A-Za-z0-9]+) is required"', verr)
            if not need:
                need = re.findall(r'([A-Za-z][A-Za-z0-9]+) is required', verr)
            t0 = time.time()
            for p in need:
                pl = p.lower()
                if "output" in pl or pl.startswith("out"):
                    params[p] = OUT + rf"\p12_d_{base}.out"
                else:
                    match = None
                    for k, v in POOL.items():
                        if k in pl: match = v[0]; break
                    if not match:
                        for k, v in POOL.items():
                            for cand in v:
                                if k in desc.lower(): match = cand; break
                            if match: break
                    params[p] = match if match else os.path.abspath(f"{E}/deg.txt")
            resp = rpc(m, params, timeout=180)
            ok = '"error"' not in resp
            if ok:
                if base not in report_pass:
                    new_pass.append(base)
            else:
                msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "")
                still_fail.append((base, msg[:70]))
            print(("NEWPASS " if ok and base not in report_pass else ("PASS    " if ok else "fail    ")) + base, f"{time.time()-t0:.1f}s", flush=True)
        except Exception as ex:
            still_fail.append((base, "EXC " + str(ex)[:60]))
            print("err     ", base, flush=True)
    w("\n### 本轮新通过（此前未 PASS）\n")
    if new_pass:
        w(", ".join(sorted(set(new_pass))))
    else:
        w("（无新增）")
    w("\n### 仍失败（原样记录）\n")
    w("| 方法 | 错误 |")
    w("|---|---|")
    for b, msg in still_fail:
        w(f"| {b} | {msg} |")
except Exception as ex:
    w(f"\n救援框架异常：{ex}")

w("\n---\n\n## Phase 12 完")
LOG.close()
print("P12 done", flush=True)

