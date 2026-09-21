import sys
# -*- coding: utf-8 -*-
"""Phase 10：第七轮 — 公开数据测试（NCBI/EBI 真实数据）
A. pileup 真 BLAST XML；B. N28 真 GTF 验证；C. 大文件性能（GRCh38 240MB）；
D. Unicode ID 专项；E. 长路径 >260；F. 只读目录；G. BlastCompareTwoSeqRegion 真数据 rescue
"""
import io, os, json, time, stat, shutil, urllib.request, subprocess

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
PUB = T + r"\data\public"
OUT = T + r"\out\p10"
os.makedirs(OUT, exist_ok=True)
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
LOG = io.open(T + r"\P10_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s):
    LOG.write(s + "\n"); LOG.flush()

def rpc(method, params, timeout=900):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1})
    req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=body.encode(),
                                 headers={"Content-Type":"application/json"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8","replace")

def cli(args, timeout=900):
    t0 = time.time()
    r = subprocess.run(CLI + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return r.returncode, r.stdout or "", r.stderr or "", time.time() - t0

def rec(name, ok, detail):
    w(f"- **{name}**: {'✅' if ok else '❌'} — {detail}")
    print(("OK  " if ok else "FAIL"), name, "|", detail[:100], flush=True)

w("# Phase 10：第七轮 — 公开数据测试")
w("\n数据源：EBI/GENCODE（GRCh38.p14 基因组前 60MB 解压 240MB、gencode.v47.basic 前 5 万行 GTF 23.9MB）、"
  "自产 NCBI 格式 BLAST XML（blastp，6,933B）。NCBI/Ensembl 直连被网络策略阻断，EBI 可达。\n")

# ---------- A. pileup 真 XML ----------
w("\n## 10.A pileup（真 BLAST XML，chipseq 分组）")
ec, so, se, dt = cli(["chipseq", "pileup", OUT + r"\p10_blast.xml", OUT + r"\p10_pileup.svg"])
svg = os.path.exists(OUT + r"\p10_pileup.svg")
rec("pileup 真 XML", ec == 0 and svg, f"ec={ec}, {dt:.1f}s, svg={'有 '+str(os.path.getsize(OUT + chr(92)+'p10_pileup.svg'))+'B' if svg else '无'}")
w("\n> 注：此前 P8 用 `plot pileup` 报「未知命令: plot」——pileup 在 chipseq 分组（cli.py:899 映射），非缺陷。")

# ---------- B. N28 真 GTF ----------
w("\n## 10.B N28 验证：GENCODE 真 GTF（5 万行，23.9MB）")
gtf = PUB + r"\gencode_head50k.gtf"
tests = [
    ("GxfSplit ← GENCODE GTF", "GxfSplit.process", {"inputPath": gtf, "outputPrefix": OUT + r"\p10_gsplit", "numOfFile": 2}),
    ("GxfPatch ← GENCODE GTF ×2", "GxfPatch.process", {"refGxfPath": gtf, "patchGxfPath": gtf, "outputPath": OUT + r"\p10_gpatch.gtf"}),
    ("GxfRecallMrna ← GENCODE GTF", "GxfRecallMrna.process", {"inputPath": gtf, "outputPath": OUT + r"\p10_grecall.gff3"}),
]
for name, method, params in tests:
    t0 = time.time()
    try:
        resp = rpc(method, params)
        ok = '"error"' not in resp
        msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "") if not ok else ""
        rec(name, ok, f"{time.time()-t0:.1f}s {msg}")
    except Exception as ex:
        rec(name, False, f"EXC {str(ex)[:80]}")

# ---------- C. 大文件性能（GRCh38 240MB） ----------
w("\n## 10.C 大文件性能：GRCh38 chr1 头段 240,801,800 B（~1.2 亿碱基）")
genome = PUB + r"\grch38_head60m.fa"
t0 = time.time()
ec, so, se, dt = cli(["tool", "statFasta", "--inFasta", genome, "--outPutFile", OUT + r"\p10_bigstat.xls"])
ok = ec == 0 and os.path.exists(OUT + r"\p10_bigstat.xls")
rec("CLI statFasta 240MB", ok, f"ec={ec}, 墙钟 {dt:.1f}s")

t0 = time.time()
try:
    resp = rpc("FastaStat.process", {"inputPath": genome, "outputPath": OUT + r"\p10_bigrpc.xls"})
    ok = '"error"' not in resp and os.path.exists(OUT + r"\p10_bigrpc.xls")
    rec("RPC FastaStat 240MB", ok, f"{time.time()-t0:.1f}s")
except Exception as ex:
    rec("RPC FastaStat 240MB", False, f"EXC {str(ex)[:80]}")

# FastaSsrMiner（真数据 rescue 候选）
t0 = time.time()
try:
    resp = rpc("FastaSsrMiner.process", {"inputPath": genome, "outputPath": OUT + r"\p10_ssr.xls"})
    ok = '"error"' not in resp
    msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "") if not ok else ""
    rec("RPC FastaSsrMiner 240MB", ok, f"{time.time()-t0:.1f}s {msg}")
except Exception as ex:
    rec("RPC FastaSsrMiner 240MB", False, f"EXC {str(ex)[:80]}")

# GxfGenomeMatch：真 GTF + 真基因组（PARAM rescue）
t0 = time.time()
try:
    resp = rpc("GxfGenomeMatch.process", {"inputGxfPath": gtf, "inputGenomePath": genome,
                                          "outputPath": OUT + r"\p10_gmatch.gff3"})
    ok = '"error"' not in resp
    msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "") if not ok else ""
    rec("RPC GxfGenomeMatch（真 GTF+真基因组）", ok, f"{time.time()-t0:.1f}s {msg}")
except Exception as ex:
    rec("RPC GxfGenomeMatch", False, f"EXC {str(ex)[:80]}")

# ---------- G. BlastCompareTwoSeqRegion（真数据 rescue） ----------
w("\n## 10.G BlastCompareTwoSeqRegion（真基因组区域）")
region = OUT + r"\p10_regions.tsv"
with io.open(region, "w", encoding="utf-8", newline="\n") as f:
    f.write("chr1\t1000000\t1010000\tchr1\t2000000\t2010000\n")
    f.write("chr1\t5000000\t5010000\tchr1\t6000000\t6010000\n")
t0 = time.time()
try:
    resp = rpc("BlastCompareTwoSeqRegion.process",
               {"genomeAPath": genome, "genomeBPath": genome,
                "regionInfoPath": region, "outputPath": OUT + r"\p10_regionblast.tsv"})
    ok = '"error"' not in resp
    msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "") if not ok else ""
    rec("BlastCompareTwoSeqRegion", ok, f"{time.time()-t0:.1f}s {msg}")
except Exception as ex:
    rec("BlastCompareTwoSeqRegion", False, f"EXC {str(ex)[:80]}")

# ---------- D. Unicode ID 专项 ----------
w("\n## 10.D Unicode 序列 ID（中文 ID FASTA）")
uni = OUT + r"\p10_中文ID.fa"
with io.open(uni, "w", encoding="utf-8", newline="\n") as f:
    for i in range(1, 4):
        f.write(f">中文序列{i}|基因-α\n")
        f.write("ACGT" * 25 + "\n")
ec, so, se, dt = cli(["tool", "statFasta", "--inFasta", uni, "--outPutFile", OUT + r"\p10_unistat.xls"])
ok = ec == 0 and os.path.exists(OUT + r"\p10_unistat.xls")
rec("CLI statFasta 中文 ID", ok, f"ec={ec}")
try:
    resp = rpc("FastaStat.process", {"inputPath": uni, "outputPath": OUT + r"\p10_unirpc.xls"})
    ok = '"error"' not in resp and os.path.exists(OUT + r"\p10_unirpc.xls")
    rec("RPC FastaStat 中文 ID", ok, f"{'' if ok else resp[:150]}")
except Exception as ex:
    rec("RPC FastaStat 中文 ID", False, f"EXC {str(ex)[:80]}")

# ---------- E. 长路径 >260 ----------
w("\n## 10.E 长路径（>260 字符）")
deep = OUT + r"\p10_deep"
leaf = deep
while len(leaf) < 270:
    leaf = os.path.join(leaf, "级别" + "x" * 30)
os.makedirs(leaf, exist_ok=True)
lp = os.path.join(leaf, "序列.fa")
shutil.copy(OUT + r"\p10_中文ID.fa", lp)
w(f"- 路径长度 {len(lp)} 字符")
ec, so, se, dt = cli(["tool", "statFasta", "--inFasta", lp, "--outPutFile", os.path.join(leaf, "stat.xls")])
ok = ec == 0 and os.path.exists(os.path.join(leaf, "stat.xls"))
rec("statFasta 长路径", ok, f"ec={ec}, 输出={'有' if os.path.exists(os.path.join(leaf,'stat.xls')) else '无'}")

# ---------- F. 只读目录 ----------
w("\n## 10.F 只读目录（输出被拒时应报错且不静默）")
ro = OUT + r"\p10_readonly"
os.makedirs(ro, exist_ok=True)
rofile = os.path.join(ro, "in.fa")
shutil.copy(OUT + r"\p10_中文ID.fa", rofile)
os.chmod(ro, stat.S_IREAD | stat.S_IEXEC)
ec, so, se, dt = cli(["tool", "statFasta", "--inFasta", rofile, "--outPutFile", os.path.join(ro, "out.xls")])
out_exists = os.path.exists(os.path.join(ro, "out.xls"))
err_mentioned = any(k in (so + se) for k in ("拒绝", "denied", "Permission", "失败", "Error", "❌", "error"))
rec("只读目录输出", (ec != 0) and not out_exists and err_mentioned,
    f"ec={ec}, 产物={'意外存在!' if out_exists else '未创建(正确)'}, 错误信息={'有' if err_mentioned else '无(静默!)'}")
os.chmod(ro, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)

w("\n---\n\n## Phase 10 完")
LOG.close()
print("P10 done", flush=True)

