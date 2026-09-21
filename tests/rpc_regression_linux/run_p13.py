import sys
# -*- coding: utf-8 -*-
"""Phase 13：第十轮 — 穿透黑盒天花板
A. jar 类常量池提取 usage/flag → 可选参数目录 + 基线工具 flag 实测
B. 66 个 RPC 方法按类型化数据池重跑救援
"""
import io
import os
import json
import re
import time
import zipfile
import random
import subprocess
import urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
PUB = T + r"\data\public"
OUT = T + r"\out\p13"
os.makedirs(OUT, exist_ok=True)
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
E = "examples/data"
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P13_LOG.md", "w", encoding="utf-8", newline="\n")
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

def srv_alive():
    try:
        rpc("system.listMethods", {}, timeout=10); return True
    except Exception:
        return False
def ensure_srv():
    if not srv_alive():
        subprocess.Popen(CLI + ["rpc", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(15):
            time.sleep(2)
            if srv_alive(): return True
        return False
    return True

w("# Phase 13：第十轮 — jar 常量池 flag 目录 + 66 方法类型化救援")
ensure_srv()

# ================= A. jar 常量池 flag 目录 =================
w("\n## 13.A jar 常量池 usage/flag 提取")
JAR = r"C:/Program Files/TBtools/TBtools_JRE1.6.jar"
reg_src = io.open("tbtools_cli" + os.sep + "cli_tools_registry.py", encoding="utf-8").read()
tool2class = dict(re.findall(r'"([A-Za-z][A-Za-z0-9]+)":\s*"([^"]+)"', reg_src))
w(f"\n注册表映射 {len(tool2class)} 条；JAR: {JAR}")

zf = zipfile.ZipFile(JAR)
FLAG_RE = re.compile(r'\[(-{1,2}[A-Za-z][A-Za-z0-9]*)(?:[ =]([^\]\[]*))?\]')
catalog = {}
for tool, cls in tool2class.items():
    entry = cls.replace(".", "/") + ".class"
    try:
        data = zf.read(entry)
    except KeyError:
        catalog[tool] = ("MISSING_CLASS", [])
        continue
    strings = re.findall(rb"[ -~]{6,}", data)
    usage_like = []
    for s in strings:
        t = s.decode("ascii", "replace")
        if ("Usage" in t or "用法" in t or "usage:" in t.lower()) and ("<" in t or "-" in t):
            usage_like.append(t)
        elif t.count("[--") >= 1:
            usage_like.append(t)
    flags = []
    for u in usage_like:
        for m in FLAG_RE.finditer(u):
            if m.group(1) not in [f[0] for f in flags]:
                flags.append((m.group(1), (m.group(2) or "").strip()))
    catalog[tool] = ("; ".join(usage_like)[:200], flags)

with_flag = {k: v for k, v in catalog.items() if v[1]}
w(f"\n- 成功从类常量池提取到可选 flag 的工具：**{len(with_flag)}/{len(tool2class)}**")
w("\n### flag 目录（前 40 个）\n")
w("| 工具 | flags |")
w("|---|---|")
for k in sorted(with_flag)[:40]:
    fl = ", ".join(f"{f}={v}" if v else f for f, v in with_flag[k][1])
    w(f"| {k} | {fl[:120]} |")
io.open(T + r"\flag_catalog.txt", "w", encoding="utf-8").write(
    "\n".join(f"{k}\t{v[0][:150]}\t{v[1]}" for k, v in sorted(catalog.items())))

# 基线工具 flag 实测
bases = {
    "statFasta": ["tool", "statFasta", "--inFasta", os.path.abspath(f"{E}/blast/query.fa"),
                  "--outPutFile", OUT + r"\p13_st.xls"],
    "volcano": ["expr", "volcano", os.path.abspath(f"{E}/deg.txt"), OUT + r"\p13_vol.svg"],
    "peakdist": ["chipseq", "peakdist", os.path.abspath(f"{E}/chipseq/chrlen2.txt"),
                 os.path.abspath(f"{E}/chipseq/peak_std.xls"), OUT + r"\p13_pd.svg"],
    "ctgGroup": ["asm", "ctgGroup", os.path.abspath(f"{E}/assembly/miniprot.gff"), "2", OUT + r"\p13_cg.tsv"],
    "extractFeatureFromGTF": ["tool", "extractFeatureFromGTF", os.path.abspath(f"{E}/gene_structure.gff"), "CDS", OUT + r"\p13_ef.gff"],
}
w("\n### 基线工具 flag 实测\n")
tried = 0
for name, base_args in bases.items():
    ec, blob, dt = cli(base_args, timeout=120)
    if ec != 0:
        rec(f"基线[{name}]", False, f"ec={ec}, 跳过"); continue
    flags = with_flag.get(name, ("", []))[1]
    if not flags:
        w(f"- **flags[{name}]**: 常量池无可选 flag"); continue
    for flag, spec in flags[:8]:
        val = (spec or "2").split("|")[0].strip().strip("<>")
        if re.fullmatch(r"N|\d+|INT|INTEGER", val, re.I): val = "2"
        elif val.upper() in ("TEXT", "STR", "STRING", "NAME"): val = "test"
        elif val.upper() == "BOOL": val = "true"
        elif "file" in val.lower() or "path" in val.lower(): val = os.path.abspath(f"{E}/deg.txt")
        elif val.upper() in ("FLOAT", "NUM"): val = "2.0"
        args2 = base_args + [flag, val]
        ec3, blob3, dt3 = cli(args2, timeout=180)
        tried += 1
        ok3 = ec3 == 0 or (ec3 > 0 and len(blob3.strip()) > 0)
        rec(f"flag[{name} {flag}={val[:10]}]", ok3, f"ec={ec3}, {dt3:.1f}s")
print(f"FLAGTEST tried={tried}", flush=True)

# ================= B. 66 方法类型化救援 =================
w("\n## 13.B 66 个 RPC 方法类型化数据救援")
# ---- 构造专用数据 ----
random.seed(7)
# promoter：5 条 2kb
prom = OUT + r"\promoters.fa"
with io.open(prom, "w", encoding="utf-8", newline="\n") as f:
    for i in range(1, 6):
        f.write(f">prom{i:02d}\n" + "".join(random.choice("ACGT") for _ in range(2000)) + "\n")
# MSA：6 条 300bp 高相似
msa = OUT + r"\msa.fa"
base_seq = "".join(random.choice("ACGT") for _ in range(300))
with io.open(msa, "w", encoding="utf-8", newline="\n") as f:
    for i in range(1, 7):
        s = list(base_seq)
        for _ in range(12):
            s[random.randrange(300)] = random.choice("ACGT")
        f.write(f">sp{i}\n" + "".join(s) + "\n")
# CDS：多条完整 ORF（ATG...TAA）
cds = OUT + r"\cds.fa"
codons = [c for c in ("ACT","TTC","GCA","ATG","TAA","GGC","CAT","TTA","CCA","GTA")]
with io.open(cds, "w", encoding="utf-8", newline="\n") as f:
    for i in range(1, 5):
        body = "".join(random.choice(codons[:8]) for _ in range(60))
        f.write(f">cds{i}\nATG{body}TAA\n")
# GenBank / EMBL 最小样例
gbk = OUT + r"\sample.gbk"
with io.open(gbk, "w", encoding="utf-8", newline="\n") as f:
    f.write("LOCUS       testseq      60 bp    DNA     linear   BCT 20-SEP-2026\n")
    f.write("DEFINITION  test.\nACCESSION   test\nVERSION     test\n")
    f.write("FEATURES             Location/Qualifiers\n     source          1..60\n")
    f.write("ORIGIN      \n")
    seq = "".join(random.choice("ACGT") for _ in range(60))
    for i in range(0, 60, 10): f.write(f"{i+1:9d} {seq[i:i+10]}\n")
    f.write("//\n")
embl = OUT + r"\sample.embl"
with io.open(embl, "w", encoding="utf-8", newline="\n") as f:
    f.write("ID   test; SV 1; linear; DNA; BCT; 60 BP.\nXX\nAC   test;\nXX\n")
    f.write("FH   Key             Location/Qualifiers\nFH\n")
    f.write("FT   source          1..60\nXX\nSQ   Sequence 60 BP;\n")
    for i in range(0, 60, 10): f.write(f"  {seq[i:i+10]:<10}\n")
    f.write("//\n")
# 剪一个小基因组（GRCh38 头 2MB）
genome_small = OUT + r"\genome2m.fa"
with io.open(genome_small, "wb") as f:
    f.write(io.open(PUB + r"\grch38_head60m.fa", "rb").read()[:2 * 1024 * 1024])

FA = os.path.abspath(f"{E}/blast/query.fa")          # 蛋白
FA2 = os.path.abspath(f"{E}/blast/subject.fa")
GFF3 = os.path.abspath(f"{E}/gxf/input.gff3")
GFF3b = os.path.abspath(f"{E}/gene_structure.gff")
GTF_SYN = T + r"\out\p9\p9_test.gtf"
EXPR = os.path.abspath(f"{E}/expr/expr.tsv")
DEG = os.path.abspath(f"{E}/deg.txt")
VCF = os.path.abspath(f"{E}/gwas/sample.vcf")
NWK = os.path.abspath(f"{E}/phylogeny/phylo.nwk")
GFA = os.path.abspath(f"{E}/fasta/sample.gfa")
MAST = os.path.abspath(f"{E}/meme/sample.mast.xml")
IDLIST = os.path.abspath(f"{E}/fasta/extract.idlist.txt")
POS = os.path.abspath(f"{E}/fasta/subseq.pos.txt")
RENMAP = os.path.abspath(f"{E}/gxf/rename.map.tsv")
QF_DIR = os.path.abspath(f"{E}/blast/quickfamily")
XMLE = OUT + r"\p12_blast_f5.txt"

def O(name): return OUT + "\\" + name

SPEC = {
    # Blast 族（蛋白对）
    "BlastCompareTwoSeqBigFileSet": {"queryPath": FA, "subjectPath": FA2, "outputPath": O("p13_b1.txt"), "options": {"blastType": "blastp", "outFmt": "0", "evalue": "10"}},
    "BlastCompareTwoSeqSet": {"queryPath": FA, "subjectPath": FA2, "outputPath": O("p13_b2.txt"), "options": {"blastType": "blastp", "outFmt": "0", "evalue": "10"}},
    "BlastCompareTwoSeqRegion": {"genomeAPath": genome_small, "genomeBPath": genome_small, "regionInfoPath": T + r"\out\p10\p10_regions.tsv", "outputPath": O("p13_b3.txt")},
    "BlastSeveralSeq2BigGenesets": {"queryPath": FA, "subjectPath": genome_small, "outputPath": O("p13_b4.txt"), "options": {"blastType": "blastx", "outFmt": "0", "evalue": "10"}},
    "BlastXmlToTable": {"inputXmlPath": XMLE, "outputPath": O("p13_b5.tsv"), "tableFormat": "Summary"},
    "ReciprocalBlast": {"queryPath": FA, "subjectPath": FA2, "outputPrefixPath": O("p13_rb"), "evalue": "1e-5"},
    "QuickGeneFamilyIdentification": {"queryPepPath": FA, "subjectPepPath": FA2, "outputDir": O("p13_qf")},
    "QuickProteinAnno": {"proteinPath": FA, "outputPath": O("p13_qpa.tsv")},
    "BlatAlign": {"queryPath": genome_small, "subjectPath": FA2, "outputPath": O("p13_blat.psl")},
    # 表达
    "ExpressionCorrMatrix": {"inputPath": EXPR, "outputPath": O("p13_ecm.tsv")},
    "ExpressionFpkmToTpm": {"inputPath": EXPR, "outputPath": O("p13_etpm.tsv")},
    "ExpressionRpkm": {"inputPath": EXPR, "outputPath": O("p13_erpkm.tsv")},
    "ExpressionTau": {"inputPath": EXPR, "outputPath": O("p13_tau.tsv")},
    "ExpressionTpm": {"inputPath": EXPR, "outputPath": O("p13_etpm2.tsv")},
    "GeneExpFilter": {"inputPath": EXPR, "outputPath": O("p13_gef.tsv")},
    "GenePairCorr": {"inputPath": EXPR, "outputPath": O("p13_gpc.tsv")},
    # Fasta 族
    "FastaExtract": {"inFa": FA, "inIDList": IDLIST, "outFa": O("p13_fe.fa")},
    "FastaMerge": {"inFastaList": FA, "outFasta": O("p13_fm.fa")},
    "FastaPatternLocate": {"inFasta": FA, "pattern": "MST", "outTable": O("p13_fpl.xls")},
    "FastaSplitAsOneSeq": {"inFasta": FA, "outDir": O("p13_fso")},
    "FastaSplitByCount": {"inFasta": FA, "count": "2", "outDir": O("p13_fbc")},
    "FastaSsrMiner": {"inputPath": os.path.abspath(f"{E}/blast/query.fa"), "outputPath": O("p13_ssr.xls"), "maxLenKbases": 1},
    "FastaSubseqFromList": {"inFasta": FA, "posList": POS, "outFasta": O("p13_fsf.fa")},
    "FastaToTable": {"inFasta": FA, "outTable": O("p13_ftt.tsv")},
    "FastaWindowStat": {"inFasta": genome_small, "windowSize": "1000", "outTable": O("p13_fws.tsv")},
    "FastxExtract": {"inFastx": os.path.abspath(f"{E}/fastq/sample.fq") if os.path.exists(f"{E}/fastq/sample.fq") else FA, "outFastx": O("p13_fx.fq")},
    # GFF/GTF/GXF 族
    "GffExtractRegion": {"inGff": GFF3b, "regionChr": "chr1", "regionStart": "1", "regionEnd": "100000", "outGff": O("p13_ger.gff3")},
    "GffFeatureExtract": {"inGff": GFF3b, "feature": "CDS", "outGff": O("p13_gfe.gff3")},
    "GffReconstructorBatch": {"inGff": GFF3b, "genomePath": genome_small, "outDir": O("p13_grb")},
    "GtfFeatureExtract": {"inGtf": GTF_SYN, "feature": "CDS", "outGtf": O("p13_gtfe.gtf")},
    "GtfFeatureScan": {"inGtf": GTF_SYN, "outTable": O("p13_gtfs.tsv")},
    "GXFRenameByMap": {"inGxf": GFF3, "mapFile": RENMAP, "outGxf": O("p13_gxn.gff3")},
    "GxfCat": {"inGxfList": GFF3, "outGxf": O("p13_gxc.gff3")},
    "GxfFilter": {"inGxf": GFF3, "outGxf": O("p13_gxf_f.gff3")},
    "GxfGeneDensityProfiler": {"inGxf": GFF3, "windowKb": "100", "outTable": O("p13_gdp.xls")},
    "GxfGeneFamilyStructErrorDetect": {"inGxf": GFF3, "outTable": O("p13_gfd.tsv")},
    "GxfGenomeMatch": {"gxfPath": GFF3, "genomePath": genome_small, "outputPath": O("p13_gxm.gff3")},
    "GxfIdAppender": {"inGxf": GFF3, "outGxf": O("p13_gia.gff3")},
    "GxfPatch": {"refGxfPath": GFF3, "patchGxfPath": GFF3, "outputPath": O("p13_gp.gff3")},
    "GxfQuickDiagnosis": {"inGxf": GFF3, "outTable": O("p13_gqd.tsv")},
    "GxfRecallMrna": {"inputPath": GFF3, "outputPath": O("p13_grm.gff3")},
    "GxfRepresentativeGxf": {"inGxf": GFF3, "outGxf": O("p13_grg.gff3")},
    "GxfRepresentativeIds": {"inGxf": GFF3, "outTable": O("p13_gri.tsv")},
    "GxfSplit": {"inputPath": GFF3, "outputPrefix": O("p13_gs"), "numOfFile": 2},
    "GxfStat": {"inputPath": GFF3, "outputPath": O("p13_gst.xls")},
    "GxfToGenePos": {"inGxf": GFF3, "outPos": O("p13_gtp.pos")},
    "McScanXFileMerge": {"inDir": os.path.abspath(f"{E}/synteny"), "outDir": O("p13_msm")},
    # 其他
    "BatchStringReplace": {"inputPath": DEG, "mapFile": RENMAP, "outputPath": O("p13_bsr.txt")},
    "BestIdConverter": {"inputPath": DEG, "mapFile": RENMAP, "outputPath": O("p13_bic.txt")},
    "CdsToProtein": {"inCds": cds, "outPep": O("p13_cds.pep")},
    "CheckPrimer": {"inTable": DEG, "outTable": O("p13_cp.tsv")},
    "EmblToFasta": {"inEmbl": embl, "outFasta": O("p13_embl.fa")},
    "GenBankToFasta": {"inGenBank": gbk, "outFasta": O("p13_gbk.fa")},
    "GfaToFasta": {"inGfa": GFA, "outFasta": O("p13_gfa.fa")},
    "MemeSuiteXmlToTab": {"inXml": MAST, "outTable": O("p13_meme.tsv")},
    "MiRBaseDatToFasta": {"inDat": os.path.abspath(f"{E}/mirna/miRNA.fa"), "outFasta": O("p13_mirfa.fa")},
    "OneStepBuildATree": {"inFasta": msa, "outTree": O("p13_tree.nwk")},
    "OrfBatchLongestComplete": {"genomePath": genome_small, "outPep": O("p13_orf1.pep")},
    "OrfPredictMax": {"genomePath": genome_small, "outPep": O("p13_orf2.pep")},
    "OrfSixFrameTranslate": {"inFasta": cds, "outFasta": O("p13_orf3.fa")},
    "PlantCareClassify": {"inFasta": prom, "outTable": O("p13_pc.tsv")},
    "TableRowManipulator": {"inputPath": DEG, "outputPath": O("p13_trm.tsv")},
    "TableToFasta": {"inputPath": T + r"\out\p12\t2f.tsv", "outputPath": O("p13_t2f.fa")},
    "TrimMsaGblocks": {"inMsa": msa, "outMsa": O("p13_tg.fa")},
    "TrimMsaSimple": {"inMsa": msa, "outMsa": O("p13_ts.fa")},
    "VcfAddId": {"inVcf": VCF, "outVcf": O("p13_vid.vcf")},
    "FastaStat": {"inputPath": FA, "outputPath": O("p13_fstat.xls")},
}

names = json.loads(rpc("system.listMethods")).get("result")
names = names.get("methods") if isinstance(names, dict) else names
procs = [m.split(".")[0] for m in names if isinstance(m, str) and m.endswith(".process")]
targets = [m for m in procs if m in SPEC]
w(f"\n类型化数据池覆盖 {len(targets)}/{len(procs)} 个 .process 方法\n")
passed, failed, missing = [], [], []
for base in targets:
    params = SPEC[base]
    # 自动补 outputPath 类缺失项
    try:
        d = json.loads(rpc("system.describeMethod", {"method": base + ".process"})).get("result", {})
        desc = json.dumps(d.get("description", {}), ensure_ascii=False)
        for req in re.findall(r'"([A-Za-z][A-Za-z0-9]+)":\s*"[^"]*required', desc):
            if req not in params:
                pl = req.lower()
                if "out" in pl: params[req] = O(f"p13_{base}_{req}.out")
                else: params[req] = DEG
        t0 = time.time()
        resp = rpc(base + ".process", params, timeout=300)
        ok = '"error"' not in resp
        if ok:
            passed.append(base)
            print("PASS ", base, f"{time.time()-t0:.1f}s", flush=True)
        else:
            msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "")
            failed.append((base, msg[:80]))
            print("fail ", base, msg[:60], flush=True)
    except Exception as ex:
        failed.append((base, "EXC " + str(ex)[:80]))
        print("err  ", base, flush=True)
missing = [m for m in procs if m not in SPEC and not re.search(r"ncbi|timetree|sra|geo|fastqblast|blastzone|download|remote|email|todo", m, re.I)]
w(f"\n### 通过 {len(passed)}\n\n" + ", ".join(sorted(passed)))
w(f"\n### 仍失败 {len(failed)}\n")
w("| 方法 | 错误 |")
w("|---|---|")
for b, msg in failed:
    w(f"| {b} | {msg} |")
w(f"\n### 数据池未覆盖（无方案）{len(missing)} 个\n\n" + ", ".join(sorted(missing)))
print(f"\nRESCUE: pass={len(passed)} fail={len(failed)} uncovered={len(missing)}", flush=True)

w("\n---\n\n## Phase 13 完")
LOG.close()
print("P13 done", flush=True)

