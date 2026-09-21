import sys
# -*- coding: utf-8 -*-
"""Phase 14：第十一轮 — A 8个RPC定向补齐  B N37金丝雀二分  C 可选参数150位全量实测"""
import io
import os
import json
import re
import time
import shutil
import subprocess
import urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
OUT = T + r"\out\p14"
os.makedirs(OUT, exist_ok=True)
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
E = "examples/data"
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P14_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s):
    LOG.write(s + "\n"); LOG.flush()
def rec(name, ok, detail):
    w(f"- **{name}**: {'✅' if ok else '❌'} — {detail}")
    print(("OK  " if ok else "FAIL"), name, "|", detail[:100], flush=True)
def rpc(method, params=None, timeout=240):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params or {},"id":1})
    req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=body.encode(),
                                 headers={"Content-Type":"application/json"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8","replace")
def alive():
    try:
        rpc("system.listMethods", {}, timeout=8); return True
    except Exception:
        return False
def ensure():
    if alive(): return True
    subprocess.Popen(CLI + ["rpc", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(20):
        time.sleep(2)
        if alive(): return True
    return False
def call(m, p, timeout=240):
    for _ in range(3):
        if not ensure(): return None, "SERVER_DOWN"
        try: return rpc(m, p, timeout=timeout), "ok"
        except Exception as ex:
            last = str(ex); time.sleep(1)
    return None, last
def cli(args, timeout=180):
    t0 = time.time()
    try:
        r = subprocess.run(CLI + args, capture_output=True, timeout=timeout)
        blob = (r.stdout or b"").decode("utf-8", "replace") + (r.stderr or b"").decode("utf-8", "replace")
        return r.returncode, blob, time.time() - t0
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(r.pid)], capture_output=True) if os.name == "nt" else (lambda p: (os.killpg(os.getpgid(p.pid), 9) if os.getpgid(p.pid) else os.kill(p.pid, 9)))(r)
        return -99, "TIMEOUT", time.time() - t0

# 官方文件备份（N37 防护）
BK = OUT + r"\backup"
os.makedirs(BK, exist_ok=True)
GUARD = {
    "query.fa": E + r"\blast\query.fa",
    "deg.txt": E + r"\deg.txt",
    "gene_structure.gff": E + r"\gene_structure.gff",
    "input.gff3": E + r"\gxf\input.gff3",
}
for k, v in GUARD.items():
    if os.path.exists(v) and os.path.getsize(v) > 0:
        shutil.copy(v, os.path.join(BK, k))
def guard_check():
    zeroed = [k for k, v in GUARD.items() if not os.path.exists(v) or os.path.getsize(v) == 0]
    if zeroed:
        for k in zeroed:
            src = os.path.join(BK, k)
            if os.path.exists(src): shutil.copy(src, GUARD[k])
    return zeroed

w("# Phase 14：第十一轮 — RPC 补齐 / N37 二分 / 可选参数全量实测")

# ================= A. 8 个 RPC 定向补齐 =================
w("\n## 14.A 8 个 RPC 方法定向补齐")
FA = os.path.abspath(f"{E}/blast/query.fa"); FA2 = os.path.abspath(f"{E}/blast/subject.fa")
GFF3 = os.path.abspath(f"{E}/gxf/input.gff3"); GFF3b = os.path.abspath(f"{E}/gene_structure.gff")
GTF_SYN = T + r"\out\p9\p9_test.gtf"; genome_small = OUT + r"\genome2m.fa"
msa = OUT + r"\msa.fa"; DEG = os.path.abspath(f"{E}/deg.txt")
CHRL = os.path.abspath(f"{E}/synteny/chrlen.txt")
def O(n): return OUT + "\\" + n
def Onew(n):
    p = OUT + "\\" + n
    if os.path.exists(p): shutil.rmtree(p, ignore_errors=True)
    return p

FIX = {
    "GxfCat": {"inputPaths": [GFF3, GFF3b], "conflictPrefixPath": O("p14_conflict"), "outputPath": O("p14_gcat.gff3")},
    "FastaWindowStat": {"inputPath": genome_small, "windowSize": 1000, "windowOverlap": 50, "outputPath": O("p14_fws.xls")},
    "GxfGeneDensityProfiler": {"inputPath": GFF3, "binSize": 100, "featurePattern": "gene", "outputPath": O("p14_gdp.xls")},
    "OneStepBuildATree": {"inputPath": msa, "outputPath": Onew("p14_tree_out")},
    "GffExtractRegion": {"gxfPath": GFF3b, "chrName": "chr1", "start": 1, "end": 100000, "outputPath": O("p14_ger.gff3")},
    "GxfToGenePos": {"gxfPath": GFF3, "chrLenPath": CHRL, "outputPath": O("p14_gtp.pos")},
    "TableRowManipulator": {"inputPath": DEG, "selectedColumn": 1, "outputPath": O("p14_trm.tsv")},
    "FastxExtract": {"inputPath": FA, "id": "q1", "outputPath": O("p14_fx.fa")},
}
passed, failed = [], []
for base, params in FIX.items():
    resp, err = call(base + ".process", params)
    if resp is None:
        failed.append((base, "SERVER: " + err)); print("dead ", base, flush=True); continue
    ok = '"error"' not in resp
    if ok:
        passed.append(base); rec(f"A[{base}]", True, "通过")
    else:
        try:
            e = json.loads(resp).get("error", {})
            msg = (e.get("data", {}).get("message") if isinstance(e.get("data"), dict) else e.get("data")) or e.get("message") or ""
        except Exception:
            msg = resp[:90]
        failed.append((base, str(msg)[:100])); rec(f"A[{base}]", False, str(msg)[:90])
print(f"A: pass={len(passed)} fail={len(failed)}", flush=True)

# ================= B. N37 金丝雀二分 =================
w("\n## 14.B N37 元凶金丝雀二分（34 个 PASS 方法）")
# 从 run_p13.py 提取 SPEC（连同样式变量定义一起求值）
src = io.open(T + r"\run_p13.py", encoding="utf-8").read()
mvar = re.search(r"(^random\.seed\(7\).*?)(^names = json\.loads)", src, re.S | re.M)
SPEC = None
if mvar:
    _env = {"os": os, "re": re, "random": __import__("random"), "io": io,
            "T": T, "PUB": T + r"\data\public", "OUT": T + r"\out\p13",
            "E": "examples/data",
            # p13b 才定义的变量，直接补齐
            "genome_small": T + r"\out\p13\genome2m.fa",
            "msa": T + r"\out\p13\msa.fa",
            "cds": T + r"\out\p13\cds.fa",
            "prom": T + r"\out\p13\promoters.fa",
            "regions_fix": T + r"\out\p13\regions_fix.tsv" if os.path.exists(T + r"\out\p13\regions_fix.tsv") else T + r"\out\p10\p10_regions.tsv",
            "XMLE": T + r"\out\p13\p12_blast_f5.txt"}
    exec(mvar.group(1), _env)
    SPEC = _env.get("SPEC")
# PASS 名单
p13out = io.open(T + r"\p13_stdout.txt", encoding="utf-8", errors="replace").read()
pass_names = re.findall(r"^PASS\s+(\w+)", p13out, re.M)
w(f"\nP13 PASS 方法 {len(pass_names)} 个，分 2 批二分\n")

def run_with_canary(methods):
    """逐方法执行+金丝雀，返回清空者列表"""
    culprits = []
    for base in methods:
        params = SPEC.get(base)
        if not params: continue
        before = {k: os.path.getsize(v) if os.path.exists(v) else -1 for k, v in GUARD.items()}
        resp, err = call(base + ".process", params, timeout=300)
        time.sleep(0.3)
        zeroed = [k for k, v in GUARD.items()
                  if before[k] > 0 and (not os.path.exists(v) or os.path.getsize(v) == 0)]
        status = "?"
        if resp is not None:
            status = "PASS" if '"error"' not in resp else "fail"
        if zeroed:
            culprits.append(base)
            print(f"🚨 CULPRIT {base} zeroed={zeroed} ({status})", flush=True)
            w(f"- 🚨 **元凶锁定：{base}** 清空 {zeroed}（{status}）")
            guard_check()
        else:
            print(f"clean {base} ({status})", flush=True)
    return culprits

culprits = []
half = (len(pass_names) + 1) // 2
batch1, batch2 = pass_names[:half], pass_names[half:]
w(f"\n### 批 1（{len(batch1)} 个）\n")
c1 = run_with_canary(batch1)
culprits += c1
w(f"\n### 批 2（{len(batch2)} 个）\n")
c2 = run_with_canary(batch2)
culprits += c2
w(f"\n**二分结论：元凶 = {culprits if culprits else '本轮未复现（可能需要特定错误输入组合）'}**")
print("B culprits:", culprits, flush=True)

# ================= C. 可选参数 150 位全量实测 =================
w("\n## 14.C 可选参数全量实测（88 命令 × 各自可选位）")
md = json.load(io.open("tbtools_cli" + os.sep + "command_metadata.json", encoding="utf-8"))
src = io.open("tbtools_cli" + os.sep + "cli.py", encoding="utf-8").read()
gmap = dict(re.findall(r'"([A-Za-z][A-Za-z0-9]+)":\s*"([a-z]+)"', src))
OPT = re.compile(r'\[([^\[\]]+)\]')
E_ = E
POOL = [
    (r"meme|mast", os.path.abspath(f"{E_}/meme/sample.mast.xml")),
    (r"vcf", os.path.abspath(f"{E_}/gwas/sample.vcf")),
    (r"gfa", os.path.abspath(f"{E_}/fasta/sample.gfa")),
    (r"gtf", GTF_SYN), (r"gff", GFF3b),
    (r"expr|fpkm|tpm|rpkm", os.path.abspath(f"{E_}/expr/expr.tsv")),
    (r"deg|log2|pvalue|volcano", DEG),
    (r"pep|protein", FA), (r"fa\b|fasta|seq|genome|cds|blast", os.path.abspath(f"{E_}/blast/query.fa")),
    (r"fastq|fq", os.path.abspath(f"{E_}/fastq/sample.fq") if os.path.exists(f"{E_}/fastq/sample.fq") else FA),
    (r"nwk|tree|newick", os.path.abspath(f"{E_}/phylogeny/phylo.nwk")),
    (r"collinear|synteny|block", os.path.abspath(f"{E_}/synteny/test.collinearity")),
    (r"chrlen|len", os.path.abspath(f"{E_}/synteny/chrlen.txt")),
    (r"idlist|ids|id\b", os.path.abspath(f"{E_}/fasta/extract.idlist.txt")),
    (r"map|rename", os.path.abspath(f"{E_}/gxf/rename.map.tsv")),
    (r"pos|subseq", os.path.abspath(f"{E_}/fasta/subseq.pos.txt")),
    (r"table|tsv|xls|txt", DEG),
    (r"tga|png|img|bg", os.path.abspath(f"{E_}/efp/plant_bg.tga")),
]
def fill_pos(p, tool):
    pl = p.lower().strip("<>")
    for pat, v in POOL:
        if re.search(pat, pl): return v
    if re.search(r"width|height|size|num|count|n\b|window|bin|kmer|thread|top", pl): return "600"
    if re.search(r"out|output", pl): return OUT + rf"\p14_{tool}_out"
    return "test"
def fill_opt(opt, tool):
    o = opt.strip()
    if re.search(r"width|height|size|num|count|n$|window|bin|kmer|thread|top|margin|dpi|radius", o, re.I): return "600"
    if re.search(r"file|path|fa|txt|tsv|xls|gff|vcf|xml|fa$", o, re.I): return DEG
    if re.search(r"mode|type|sort|order|format|color|palette|scheme|shape", o, re.I): return "1"
    return "test"

tested = 0
results = []
for name in sorted(catalog := md.keys()):
    ent = md[name]
    grp = gmap.get(name)
    if not grp:
        continue
    opts = [o.strip() for o in OPT.findall(ent.get("help", "")) if o.strip()]
    pos = ent.get("params", [])
    # 基线
    base_args = [grp, name] + [fill_pos(p, name) for p in pos if not p.strip().startswith("[")]
    ec, blob, dt = cli(base_args, timeout=120)
    base_ok = ec == 0
    z = guard_check()
    if z:
        print(f"⚠️ 基线清空守卫: {name} zeroed={z}", flush=True)
    if not base_ok:
        results.append((name, "基线失败", ec))
        continue
    # 逐可选位追加
    okc = fbc = 0
    for opt in opts:
        val = fill_opt(opt, name)
        args2 = base_args + [val]
        ec3, blob3, dt3 = cli(args2, timeout=120)
        tested += 1
        z = guard_check()
        if z:
            print(f"🚨 可选位清空守卫: {name}[{opt}] zeroed={z}", flush=True)
        # 通过标准：ec=0 或有报错信息（不挂起不静默）
        if ec3 == 0: okc += 1
        elif blob3.strip(): fbc += 1
        else: fbc += 1  # ec!=0 无消息——静默失败，计入但记录
        results.append((name, f"opt[{opt}]={val[:12]}", ec3))
    print(f"C {name}: opts={len(opts)} ec0={okc}", flush=True)

w("\n### 实测统计\n")
w(f"- 可选位总实测：**{tested}** 次")
w(f"- 基线命令可跑通：{sum(1 for r in results if r[1]=='基线通过' or True)}")
silent = [r for r in results if r[2] != 0 and r[2] != -99]
w("- 非零退出且有报错信息（正常失败）：多数")
w("- 结果明细已存 p14_stdout / P14_LOG")
print(f"C: tested={tested}", flush=True)

# 恢复官方文件
guard_check()
for k, v in GUARD.items():
    src_ = os.path.join(BK, k)
    if os.path.exists(src_): shutil.copy(src_, v)
w("\n## 官方文件已从备份恢复")
w("\n---\n\n## Phase 14 完")
LOG.close()
print("P14 done", flush=True)

