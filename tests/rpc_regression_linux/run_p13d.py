import sys
# -*- coding: utf-8 -*-
"""P13d：迭代补参收敛——解析 'X is required' 回显自动填池重试，至多 8 轮"""
import io
import os
import json
import re
import time
import subprocess
import urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
OUT = T + r"\out\p13"
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
E = "examples/data"
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P13D_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s):
    LOG.write(s + "\n"); LOG.flush()

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
def call(method, params):
    for _ in range(3):
        if not ensure(): return None, "SERVER_UNRECOVERABLE"
        try:
            return rpc(method, params, timeout=240), "ok"
        except Exception as ex:
            last = str(ex); time.sleep(1)
    return None, last

FA = os.path.abspath(f"{E}/blast/query.fa"); FA2 = os.path.abspath(f"{E}/blast/subject.fa")
GFF3 = os.path.abspath(f"{E}/gxf/input.gff3"); GFF3b = os.path.abspath(f"{E}/gene_structure.gff")
GTF_SYN = T + r"\out\p9\p9_test.gtf"; EXPR = os.path.abspath(f"{E}/expr/expr.tsv")
DEG = os.path.abspath(f"{E}/deg.txt"); VCF = os.path.abspath(f"{E}/gwas/sample.vcf")
GFA = os.path.abspath(f"{E}/fasta/sample.gfa"); MAST = os.path.abspath(f"{E}/meme/sample.mast.xml")
IDLIST = os.path.abspath(f"{E}/fasta/extract.idlist.txt"); RENMAP = os.path.abspath(f"{E}/gxf/rename.map.tsv")
XMLE = OUT + r"\p12_blast_f5.txt"; genome_small = OUT + r"\genome2m.fa"
msa = OUT + r"\msa.fa"; cds = OUT + r"\cds.fa"; prom = OUT + r"\promoters.fa"
TBL = T + r"\out\p12\t2f.tsv"; regions_fix = OUT + r"\regions_fix.tsv"
# 类型化文件值清单（按类型优先）
TYPED = {
    "fastq": os.path.abspath(f"{E}/fastq/sample.fq") if os.path.exists(f"{E}/fastq/sample.fq") else FA,
    "fastq2": os.path.abspath(f"{E}/fastq/sample2.fq") if os.path.exists(f"{E}/fastq/sample2.fq") else FA2,
}
POOL_ORDER = [  # (名称/描述关键词, 值)
    (r"meme|mast", MAST), (r"vcf", VCF), (r"gfa", GFA), (r"gtf", GTF_SYN), (r"gff", GFF3b),
    (r"msa|align|trim", msa), (r"promot|plantcare", prom), (r"cds|protein|pep|to.?prot", cds),
    (r"genome|orf|window|region|blat|reconstruct", genome_small), (r"expr|fpkm|tpm|rpkm|tau|corr|exp", EXPR),
    (r"collinearity|mcscanx|synteny", os.path.abspath(f"{E}/synteny/test.collinearity")),
    (r"map|rename|convert|replace|best", RENMAP), (r"id.?list|idlist|extract|fastx|fastq", IDLIST),
    (r"xml", XMLE), (r"table|row|tab", TBL), (r"gxf|recall|patch|split|stat|cat|filter|append|represent|diagnos|density|genepos", GFF3),
    (r"query|subject|in.?fa|fasta|seq|fa$|fa\b|tree|merge|pattern|subseq|ssr", FA),
]

def fill(pname, desc):
    pl = pname.lower()
    if "output" in pl or pl.startswith("out") or "prefix" in pl or pl.endswith("dir"):
        return OUT + rf"\p13d_{pname}.out"
    for pat, v in POOL_ORDER:
        if re.search(pat, pl): return v
    for pat, v in POOL_ORDER:
        if re.search(pat, desc.lower()): return v
    return DEG

SEED = {
    "TableRowManipulator": {"inputPath": DEG, "outputPath": OUT + r"\p13d_trm.tsv"},
    "TrimMsaGblocks": {"inAlignment": msa, "outAlignment": OUT + r"\p13d_tg.fa"},
    "TrimMsaSimple": {"inAlignment": msa, "outAlignment": OUT + r"\p13d_ts.fa"},
}
targets = ["BatchStringReplace","BestIdConverter","BlatAlign","FastaMerge","FastaPatternLocate",
    "FastaSplitByCount","FastaWindowStat","FastxExtract","GXFRenameByMap","GfaToFasta",
    "GffExtractRegion","GffFeatureExtract","GffReconstructorBatch","GtfFeatureScan","GxfCat","GxfFilter",
    "GxfGeneDensityProfiler","GxfGeneFamilyStructErrorDetect","GxfIdAppender","GxfRepresentativeGxf",
    "GxfRepresentativeIds","GxfToGenePos","McScanXFileMerge","MemeSuiteXmlToTab","OneStepBuildATree",
    "OrfPredictMax","QuickGeneFamilyIdentification","QuickProteinAnno","ReciprocalBlast","TableRowManipulator",
    "TrimMsaGblocks","TrimMsaSimple","FastaStat"]

w("# P13d：迭代补参收敛（回显驱动，至多 8 轮）\n")
final_pass, final_fail = [], []
for base in targets:
    # 种子参数：describeMethod 的 required 或 SEED
    try:
        d = json.loads(rpc("system.describeMethod", {"method": base + ".process"})).get("result", {})
        desc = json.dumps(d.get("description", {}), ensure_ascii=False)
    except Exception:
        desc = ""
    params = dict(SEED.get(base, {}))
    for pname in re.findall(r'"([A-Za-z][A-Za-z0-9]+)":\s*"[^"]*required', desc):
        if pname not in params:
            params[pname] = fill(pname, desc)
    # options
    mo = re.search(r'"options":\s*"([^"]*)"', desc)
    if mo and "blastType" in mo.group(1) and not any(k == "options" for k in params):
        params["options"] = {"blastType": "blastx" if "blastx" in mo.group(1) else "blastp", "outFmt": "0", "evalue": "10"}
    ok = False; msg = ""; rounds = 0
    for round_i in range(8):
        rounds = round_i + 1
        resp, err = call(base + ".process", params)
        if resp is None:
            msg = "SERVER: " + err; break
        if '"error"' not in resp:
            ok = True; msg = f"收敛于第 {rounds} 轮"; break
        try:
            e = json.loads(resp).get("error", {})
            msg = (e.get("data", {}).get("message") if isinstance(e.get("data"), dict) else e.get("data")) or e.get("message") or ""
            msg = str(msg)
        except Exception:
            msg = resp[:100]
        need = re.findall(r'([A-Za-z][A-Za-z0-9]+) is required', msg)
        filled = False
        for p in need:
            if p not in params or not params.get(p):
                params[p] = fill(p, desc); filled = True
        if not filled and not need:
            break  # 非缺参错误，终止
    if ok:
        final_pass.append((base, rounds)); print(f"PASS  {base} (rounds={rounds})", flush=True)
    else:
        final_fail.append((base, msg[:100])); print(f"fail  {base}: {msg[:80]}", flush=True)

w(f"\n## 迭代收敛通过 {len(final_pass)}\n")
w("| 方法 | 收敛轮数 |")
w("|---|---|")
for b, r in final_pass:
    w(f"| {b} | {r} |")
w(f"\n## 终局失败 {len(final_fail)}\n")
w("| 方法 | 终态错误 |")
w("|---|---|")
for b, msg in final_fail:
    w(f"| {b} | {msg} |")
print(f"\nP13D: pass={len(final_pass)} fail={len(final_fail)}", flush=True)
w("\n\n## Phase 13d 完")
LOG.close()
print("P13d done", flush=True)

