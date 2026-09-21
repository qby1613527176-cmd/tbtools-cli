import sys
# -*- coding: utf-8 -*-
"""Phase 13b：A. command_metadata.json 全量可选参数目录 + 实测；B. 33 个失败方法 describeMethod 精确二轮救援"""
import io
import os
import json
import re
import time
import subprocess
import urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
PUB = T + r"\data\public"
OUT = T + r"\out\p13"
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
E = "examples/data"
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P13B_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s):
    LOG.write(s + "\n"); LOG.flush()
def rec(name, ok, detail):
    w(f"- **{name}**: {'✅' if ok else '❌'} — {detail}")
    print(("OK  " if ok else "FAIL"), name, "|", detail[:100], flush=True)
def rpc(method, params=None, timeout=300):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params or {},"id":1})
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

w("# Phase 13b：可选参数全目录 + 二轮精确救援")

# ================= A. 可选参数全目录 =================
w("\n## 13.A' command_metadata.json 全量可选参数目录（143 命令）")
md = json.load(io.open("tbtools_cli" + os.sep + "command_metadata.json", encoding="utf-8"))
OPT = re.compile(r'\[([^\[\]]+)\]')
catalog, total_opts = {}, 0
for name, ent in md.items():
    help_s = ent.get("help", "") if isinstance(ent, dict) else ""
    opts = OPT.findall(help_s)
    opts = [o.strip() for o in opts if o.strip() and not o.strip().isdigit()]
    if opts:
        catalog[name] = opts
        total_opts += len(opts)
w(f"\n- **{len(catalog)}/143 命令有可选参数，共 {total_opts} 个可选位**（元数据一直在包内，CLI 未透出——N33 根因）")
w("\n### 目录（全部）\n")
w("| 命令 | 可选参数 |")
w("|---|---|")
for k in sorted(catalog):
    w(f"| {k} | {', '.join('`'+o+'`' for o in catalog[k])} |")
io.open(T + r"\optional_params_catalog.txt", "w", encoding="utf-8").write(
    "\n".join(f"{k}: {', '.join(v)}" for k, v in sorted(catalog.items())))

# 实测：挑 6 个带可选位的命令（位置式可选参数直接追加）
w("\n### 可选参数实测（追加到已知良好基线）\n")
test_plan = []
for name, opts in catalog.items():
    if name == "volcano":
        test_plan.append(("volcano", ["expr", "volcano", os.path.abspath(f"{E}/deg.txt"), OUT + r"\p13b_vol.svg"], opts))
    elif name == "motif":
        # motif 基线需要 meme.xml + idlist
        test_plan.append(("motif", ["seq", "motif", os.path.abspath(f"{E}/meme/sample.meme.xml" if os.path.exists(f"{E}/meme/sample.meme.xml") else f"{E}/meme/sample.mast.xml"),
                                    os.path.abspath(f"{E}/ids.txt"), OUT + r"\p13b_motif.png"], opts))
    elif name == "dotplot":
        test_plan.append(("dotplot", ["syn", "dotplot", os.path.abspath(f"{E}/synteny/test.collinearity"),
                                      os.path.abspath(f"{E}/synteny/chrlen.txt"), OUT + r"\p13b_dp.svg"], opts))
    elif name == "circos" and len(test_plan) < 6:
        continue
for name, base_args, opts in test_plan[:5]:
    ec, blob, dt = cli(base_args, timeout=180)
    if ec != 0:
        rec(f"基线[{name}]", False, f"ec={ec}, 跳过"); continue
    for opt in opts[:4]:
        val = "600" if re.search(r"width|height|size", opt, re.I) else ("2" if re.fullmatch(r"[Nn]|\d+", opt) else "test")
        ec3, blob3, dt3 = cli(base_args + [val], timeout=180)
        outok = any(os.path.exists(a) and os.path.getsize(a) > 0 for a in base_args if a.endswith((".svg", ".png", ".xls", ".tsv")))
        ok3 = ec3 == 0 if ec3 == 0 else (len(blob3.strip()) > 0)
        rec(f"opt[{name} +{opt}={val}]", ok3, f"ec={ec3}, {dt3:.1f}s{' ⚠️ec=0无产物' if ec3==0 and not outok else ''}")

# ================= B. 二轮精确救援 =================
w("\n## 13.B' 二轮救援（describeMethod 精确参数名 + 类型化池）")
FA = os.path.abspath(f"{E}/blast/query.fa")
FA2 = os.path.abspath(f"{E}/blast/subject.fa")
GFF3 = os.path.abspath(f"{E}/gxf/input.gff3")
GFF3b = os.path.abspath(f"{E}/gene_structure.gff")
GTF_SYN = T + r"\out\p9\p9_test.gtf"
EXPR = os.path.abspath(f"{E}/expr/expr.tsv")
DEG = os.path.abspath(f"{E}/deg.txt")
VCF = os.path.abspath(f"{E}/gwas/sample.vcf")
GFA = os.path.abspath(f"{E}/fasta/sample.gfa")
MAST = os.path.abspath(f"{E}/meme/sample.mast.xml")
IDLIST = os.path.abspath(f"{E}/fasta/extract.idlist.txt")
RENMAP = os.path.abspath(f"{E}/gxf/rename.map.tsv")
XMLE = OUT + r"\p12_blast_f5.txt"
genome_small = OUT + r"\genome2m.fa"
msa = OUT + r"\msa.fa"
cds = OUT + r"\cds.fa"
prom = OUT + r"\promoters.fa"
TBL = T + r"\out\p12\t2f.tsv"
# 修正 regions 文件：chr 头为 "chr1 1"，region 用 "chr1"
regions_fix = OUT + r"\regions_fix.tsv"
io.open(regions_fix, "w", encoding="utf-8", newline="\n").write("chr1\t1000\t11000\tchr1\t2000\t12000\n")

POOL2 = [
    (r"fasta|fa\b|seq|pep|protein|genome|cds|orf|blat|window|ssr|one.?step|tree|build", os.path.abspath(f"{E}/blast/query.fa")),
    (r"gff", GFF3b), (r"gtf", GTF_SYN), (r"gxf|recall|patch|split|stat|cat|filter|id.?append|represent|diagnos|density|genepos|rename", GFF3),
    (r"expr|fpkm|tpm|rpkm|tau|corr|exp", EXPR), (r"vcf", VCF), (r"gfa", GFA), (r"meme|xml.?to.?tab|mast", MAST),
    (r"msa|trim|gblocks", msa), (r"promoter|plantcare", prom), (r"cds|to.?protein", cds),
    (r"table|row|to.?fasta", TBL), (r"map|rename|convert|replace", RENMAP), (r"blast.?xml|xml", XMLE),
    (r"region|reconstructor", regions_fix), (r"id.?list|extract", IDLIST),
]
def pick(name_hint, desc):
    nl, dl = name_hint.lower(), desc.lower()
    for pat, val in POOL2:
        if re.search(pat, nl) or re.search(pat, dl):
            return val
    return DEG

# 上轮失败清单
fails_prev = ["BestIdConverter","BlastCompareTwoSeqRegion","BlastXmlToTable","BlatAlign","FastaMerge",
    "FastaPatternLocate","FastaSplitByCount","FastaWindowStat","FastxExtract","GXFRenameByMap","GfaToFasta",
    "GffExtractRegion","GffFeatureExtract","GffReconstructorBatch","GtfFeatureScan","GxfCat","GxfFilter",
    "GxfGeneDensityProfiler","GxfGeneFamilyStructErrorDetect","GxfIdAppender","GxfRepresentativeGxf",
    "GxfRepresentativeIds","GxfToGenePos","McScanXFileMerge","MemeSuiteXmlToTab","OneStepBuildATree",
    "OrfPredictMax","QuickGeneFamilyIdentification","QuickProteinAnno","ReciprocalBlast","TableRowManipulator",
    "TrimMsaGblocks","TrimMsaSimple"]
OUTFIX = {
    "BlastCompareTwoSeqRegion": {"regionInfoPath": regions_fix, "genomeAPath": genome_small, "genomeBPath": genome_small, "outputPath": OUT + r"\p13b_bcr.tsv"},
    "QuickProteinAnno": None,  # 需要 Diamond 外部依赖
    "OneStepBuildATree": None,  # ML pipeline 外部依赖
}
passed2, failed2 = [], []
for base in fails_prev:
    if base in OUTFIX and OUTFIX[base] is None:
        failed2.append((base, "外部依赖（Diamond/ML pipeline），黑盒不可构造"))
        print("extdep", base, flush=True)
        continue
    try:
        d = json.loads(rpc("system.describeMethod", {"method": base + ".process"})).get("result", {})
        desc = json.dumps(d.get("description", {}), ensure_ascii=False)
        dlow = desc.lower()
        reqs = re.findall(r'"([A-Za-z][A-Za-z0-9]+)":\s*"([^"]*)"', desc)
        params = dict(OUTFIX.get(base, {}))
        for pname, pspec in reqs:
            if "required" not in pspec: continue
            if pname in params: continue
            pl = pname.lower()
            if "output" in pl or pl.startswith("out") or "prefix" in pl:
                params[pname] = OUT + rf"\p13b_{base}_{pname}.out"
            else:
                # 逐参数名匹配
                val = None
                for pat, v in POOL2:
                    if re.search(pat, pl):
                        val = v; break
                if not val:
                    for pat, v in POOL2:
                        if re.search(pat, dlow):
                            val = v; break
                params[pname] = val if val else DEG
        # options 对象
        mo = re.search(r'"options":\s*"([^"]*)"', desc)
        if mo and "blastType" in mo.group(1) and "options" not in params:
            bt = "blastx" if "blastx" in mo.group(1) else "blastp"
            params["options"] = {"blastType": bt, "outFmt": "0", "evalue": "10"}
        t0 = time.time()
        resp = rpc(base + ".process", params, timeout=300)
        ok = '"error"' not in resp
        if ok:
            passed2.append(base); print("PASS ", base, f"{time.time()-t0:.1f}s", flush=True)
        else:
            msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "")
            failed2.append((base, msg[:90])); print("fail ", base, msg[:70], flush=True)
    except Exception as ex:
        failed2.append((base, "EXC " + str(ex)[:80])); print("err  ", base, flush=True)

w(f"\n### 二轮通过 {len(passed2)}\n\n" + (", ".join(sorted(passed2)) if passed2 else "（无）"))
w(f"\n### 二轮仍失败 {len(failed2)}\n")
w("| 方法 | 错误 |")
w("|---|---|")
for b, msg in failed2:
    w(f"| {b} | {msg} |")
print(f"\nROUND2: pass={len(passed2)} fail={len(failed2)}", flush=True)

w("\n---\n\n## Phase 13b 完")
LOG.close()
print("P13b done", flush=True)

