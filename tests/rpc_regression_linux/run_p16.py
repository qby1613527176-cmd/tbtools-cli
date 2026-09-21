import sys
# -*- coding: utf-8 -*-
"""P16：RPC 层可选参数逐位实测（全方法 describe 枚举 + 基线收敛 + 逐位追加 + N37 守卫）"""
import io, os, json, re, time, subprocess, urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
for k in ("HTTP_PROXY","http_proxy","HTTPS_PROXY","https_proxy","ALL_PROXY","all_proxy"):
    os.environ.pop(k, None)
os.environ["NO_PROXY"] = "127.0.0.1,localhost"; os.environ["no_proxy"] = "127.0.0.1,localhost"
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P16_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s): LOG.write(s + "\n"); LOG.flush()
def rpc(m, p=None, timeout=200):
    b = json.dumps({"jsonrpc":"2.0","method":m,"params":p or {},"id":1}).encode()
    return urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:8765/rpc", data=b,
        headers={"Content-Type":"application/json"}), timeout=timeout).read().decode("utf-8","replace")
def alive():
    try: rpc("system.listMethods", {}, 8); return True
    except Exception: return False
def ensure():
    if alive(): return True
    subprocess.Popen(CLI + ["rpc", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(25):
        time.sleep(2)
        if alive(): return True
    return False
def call(m, p, timeout=200):
    for _ in range(2):
        if not ensure(): return None, "SERVER_DOWN"
        try: return rpc(m, p, timeout), "ok"
        except Exception as ex:
            last = str(ex); time.sleep(1)
    return None, last

E = "examples/data"
TDIR = T
FA   = os.path.abspath(f"{E}/blast/query.fa")
FA2  = os.path.abspath(f"{E}/blast/subject.fa")
GFF3 = os.path.abspath(f"{E}/gxf/input.gff3")
GFF3b= os.path.abspath(f"{E}/gene_structure.gff")
DEG  = os.path.abspath(f"{E}/deg.txt")
CHRL = os.path.abspath(f"{E}/synteny/chrlen.txt")
IDLIST=os.path.abspath(f"{E}/fasta/extract.idlist.txt")
GTF  = TDIR + r"\out\p9\p9_test.gtf"
MSA  = TDIR + r"\out\p13\msa.fa"
GEN  = TDIR + r"\out\p13\genome2m.fa"
NWK  = os.path.abspath(f"{E}/phylogeny/phylo.nwk")
EXPR = os.path.abspath(f"{E}/expr/expr.tsv")
VCF  = os.path.abspath(f"{E}/gwas/sample.vcf")
COLL = os.path.abspath(f"{E}/synteny/test.collinearity")
MAPF = os.path.abspath(f"{E}/gxf/rename.map.tsv")
GUARD = {"deg.txt": DEG, "query.fa": FA, "gene_structure.gff": GFF3b}
BK = TDIR + r"\backup_examples_data_p16"
def guard_zeroed():
    z = []
    for k, v in GUARD.items():
        if os.path.exists(v) and os.path.getsize(v) == 0:
            z.append(k)
            s = os.path.join(BK, k)
            if os.path.exists(s): io.open(v, "wb").write(io.open(s, "rb").read())
    return z

POOL = [(r"swissprot|sprot|db", FA2), (r"query|protein|pep", FA),
        (r"subject|target|ref", FA2), (r"msa|align", MSA), (r"genome|window", GEN),
        (r"gtf", GTF), (r"gff3|gene_struct", GFF3b), (r"gxf|gff", GFF3),
        (r"vcf", VCF), (r"collinear|synteny|block", COLL),
        (r"chrlen|len", CHRL), (r"idlist|ids", IDLIST), (r"expr|fpkm", EXPR),
        (r"nwk|tree|newick", NWK), (r"map|rename", MAPF),
        (r"fa\b|fasta|seq|cds|blast", FA), (r"expr|deg|table|tsv|xls|txt", DEG)]
OUT = TDIR + r"\out\p16"; os.makedirs(OUT, exist_ok=True)
def O(n): return OUT + "\\" + n

def fill_val(pname, typ, desc):
    pl = pname.lower(); tl = (typ or "").lower()
    if "output" in pl or pl.startswith("out") or "prefix" in pl or "report" in pl:
        return O("p16_" + pname + ".out")
    if "int" in tl or "integer" in tl:
        if re.search(r"bin|window|width|height|size|top|margin|dpi|radius|kmer|hits", pl): return 100
        return 2
    if "bool" in tl: return True
    if "array" in tl or "list" in tl: return [FA]
    for pat, v in POOL:
        if re.search(pat, pl): return v
    for pat, v in POOL:
        if re.search(pat, desc.lower()): return v
    if re.search(r"color|colour", pl): return "#FF0000"
    if re.search(r"mode|type|sort|order|format|scheme|shape|pattern|tag", pl): return "gene"
    return "test"

SKIP = {"OneStepBuildATree"}  # N40 挂起，跳过
if not ensure():
    raise SystemExit("RPC server failed to start")
_names = json.loads(rpc("system.listMethods")).get("result")
_names = _names.get("methods") if isinstance(_names, dict) else _names
methods = [m for m in (_names or []) if isinstance(m, str) and m.endswith(".process")]
w("# P16 RPC 可选参数逐位实测\n\n跳过: " + ", ".join(sorted(SKIP)) + "\n")
total_opt = ok_opt = err_opt = 0
base_fail = []
detail = []
for m in sorted(methods):
    base = m[:-len(".process")]
    if base in SKIP: continue
    try:
        d = json.loads(rpc("system.describeMethod", {"method": m})).get("result", {})
        descj = d.get("description", {})
        desc = json.dumps(descj, ensure_ascii=False)
        pdefs = descj.get("params", {})
    except Exception as ex:
        w(f"- {base}: describe 失败 {ex}"); continue
    # 解析必填
    req, opt = [], []
    for pname, pdef in (pdefs.items() if isinstance(pdefs, dict) else []):
        pd = str(pdef)
        if "required" in pd: req.append((pname, pd))
        else: opt.append((pname, pd))
    if not req: continue
    # 基线收敛（最多 5 轮）
    params = {}
    ok = False; msg = ""
    for rnd in range(5):
        resp, err = call(m, params, 200)
        if resp is None: msg = "SERVER:" + err; break
        if '"error"' not in resp: ok = True; break
        try:
            e = json.loads(resp).get("error", {})
            msg = (e.get("data", {}).get("message") if isinstance(e.get("data"), dict) else e.get("data")) or e.get("message") or ""
            msg = str(msg)
        except Exception: msg = resp[:120]
        need = re.findall(r'([A-Za-z][A-Za-z0-9]+) is required', msg)
        filled = False
        for p in need:
            if p not in params:
                pd = pdefs.get(p, "")
                params[p] = fill_val(p, pd, desc); filled = True
        nm = re.search(r'([A-Za-z][A-Za-z0-9]+) is not a readable file', msg)
        if nm and nm.group(1) in params:
            params[nm.group(1)] = fill_val(nm.group(1), pdefs.get(nm.group(1), ""), desc)
            filled = True
        if not filled: break
    z = guard_zeroed()
    if z: print(f"🚨 N37 基线清空: {base} {z}", flush=True); w(f"- 🚨 **{base} 基线清空 {z}**")
    if not ok:
        base_fail.append((base, msg[:90]))
        print(f"base-fail {base}: {msg[:80]}", flush=True)
        w(f"- {base}: 基线未通（{msg[:80]}），跳过其 {len(opt)} 个可选位")
        continue
    # 逐可选位追加
    for pname, pd in opt:
        p2 = dict(params)
        p2[pname] = fill_val(pname, pd, desc)
        resp2, err2 = call(m, p2, 200)
        total_opt += 1
        z = guard_zeroed()
        if resp2 is not None and '"error"' not in resp2:
            ok_opt += 1; tag = "✅"
        else:
            err_opt += 1; tag = "❌"
            try:
                e2 = json.loads(resp2).get("error", {}) if resp2 else {}
                m2 = (e2.get("data", {}).get("message") if isinstance(e2.get("data"), dict) else e2.get("data")) or e2.get("message") or err2
                detail.append((base, pname, str(m2)[:100]))
            except Exception:
                detail.append((base, pname, (resp2 or err2 or "")[:100]))
        if z: print(f"🚨 N37 可选位清空: {base}[{pname}] {z}", flush=True); w(f"- 🚨 **{base}[{pname}] 清空 {z}**")
    print(f"P16 {base}: req={len(req)} opt={len(opt)}", flush=True)
    w(f"- {base}: 必填{len(req)} 可选{len(opt)}")

w(f"\n## 总计\n")
w(f"- 方法枚举：{len(methods)-len(SKIP)}（跳过 {len(SKIP)}）")
w(f"- 基线未通：{len(base_fail)}")
w(f"- 可选位实测：{total_opt}，通过 {ok_opt}，报错/拒绝 {err_opt}")
w(f"\n### 可选位报错明细（前 40）\n")
for b, p, m2 in detail[:40]:
    w(f"- {b}[{p}]: {m2}")
w("\n## Phase 16 完")
LOG.close()
print(f"\nP16: opt_total={total_opt} ok={ok_opt} err={err_opt} base_fail={len(base_fail)}", flush=True)
print("P16 done", flush=True)

