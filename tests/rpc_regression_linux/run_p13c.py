import sys
# -*- coding: utf-8 -*-
"""P13c：33 个失败方法——每次调用前确保服务存活（N35 对策），3 次重试"""
import io, os, json, re, time, subprocess, urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
PUB = T + r"\data\public"
OUT = T + r"\out\p13"
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
E = "examples/data"
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P13C_LOG.md", "w", encoding="utf-8", newline="\n")
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
    for attempt in range(3):
        if not ensure():
            return None, "SERVER_UNRECOVERABLE"
        try:
            return rpc(method, params, timeout=240), "ok"
        except Exception as ex:
            last = str(ex)
            time.sleep(1)
    return None, last

w("# P13c：33 方法三次重试（每调用前自动拉活服务）")

FA = os.path.abspath(f"{E}/blast/query.fa"); FA2 = os.path.abspath(f"{E}/blast/subject.fa")
GFF3 = os.path.abspath(f"{E}/gxf/input.gff3"); GFF3b = os.path.abspath(f"{E}/gene_structure.gff")
GTF_SYN = T + r"\out\p9\p9_test.gtf"; EXPR = os.path.abspath(f"{E}/expr/expr.tsv")
DEG = os.path.abspath(f"{E}/deg.txt"); VCF = os.path.abspath(f"{E}/gwas/sample.vcf")
GFA = os.path.abspath(f"{E}/fasta/sample.gfa"); MAST = os.path.abspath(f"{E}/meme/sample.mast.xml")
IDLIST = os.path.abspath(f"{E}/fasta/extract.idlist.txt"); RENMAP = os.path.abspath(f"{E}/gxf/rename.map.tsv")
XMLE = OUT + r"\p12_blast_f5.txt"; genome_small = OUT + r"\genome2m.fa"
msa = OUT + r"\msa.fa"; cds = OUT + r"\cds.fa"; prom = OUT + r"\promoters.fa"
TBL = T + r"\out\p12\t2f.tsv"; regions_fix = OUT + r"\regions_fix.tsv"
def O(n): return OUT + "\\" + n

SPEC = {
    "BestIdConverter": {"inputPath": DEG, "mapFile": RENMAP, "outputPath": O("p13c_bic.txt")},
    "BlastCompareTwoSeqRegion": {"genomeAPath": genome_small, "genomeBPath": genome_small, "regionInfoPath": regions_fix, "outputPath": O("p13c_bcr.tsv")},
    "BlastXmlToTable": {"inputXmlPath": XMLE, "outputPath": O("p13c_b2t.tsv"), "tableFormat": "BlastTab"},
    "BlatAlign": {"queryPath": genome_small, "subjectPath": FA2, "outputPath": O("p13c_blat.psl")},
    "FastaMerge": {"inFasta1": FA, "inFasta2": FA2, "outFasta": O("p13c_fmerge.fa")},
    "FastaPatternLocate": {"inFasta": FA, "pattern": "MST", "outTable": O("p13c_fpl.xls")},
    "FastaSplitByCount": {"inFasta": FA, "count": 2, "outDir": O("p13c_fbc")},
    "FastaWindowStat": {"inFasta": genome_small, "windowSize": 1000, "outTable": O("p13c_fws.xls")},
    "FastxExtract": {"inFastq": os.path.abspath(f"{E}/fastq/sample.fq") if os.path.exists(f"{E}/fastq/sample.fq") else FA,
                     "idList": IDLIST, "outFastq": O("p13c_fx.fq")},
    "GXFRenameByMap": {"inGxf": GFF3, "mapFile": RENMAP, "outGxf": O("p13c_gxn.gff3")},
    "GfaToFasta": {"inGfa": GFA, "outFasta": O("p13c_gfa.fa")},
    "GffExtractRegion": {"inGff": GFF3b, "chrName": "chr1", "start": 1, "end": 100000, "outGff": O("p13c_ger.gff3")},
    "GffFeatureExtract": {"inGff": GFF3b, "featureType": "CDS", "outGff": O("p13c_gfe.gff3")},
    "GffReconstructorBatch": {"inGff": GFF3b, "genomeFasta": genome_small, "outDir": O("p13c_grb")},
    "GtfFeatureScan": {"inGtf": GTF_SYN, "outTable": O("p13c_gtfs.xls")},
    "GxfCat": {"inGxf1": GFF3, "inGxf2": GFF3b, "outGxf": O("p13c_gcat.gff3")},
    "GxfFilter": {"inGxf": GFF3, "chrName": "chr1", "outGxf": O("p13c_gfil.gff3")},
    "GxfGeneDensityProfiler": {"inGxf": GFF3, "windowKb": 100, "outTable": O("p13c_gdp.xls")},
    "GxfGeneFamilyStructErrorDetect": {"inGxf": GFF3, "outTable": O("p13c_gfd.xls")},
    "GxfIdAppender": {"inGxf": GFF3, "prefix": "TB", "outGxf": O("p13c_gia.gff3")},
    "GxfRepresentativeGxf": {"inGxf": GFF3, "outGxf": O("p13c_grg.gff3")},
    "GxfRepresentativeIds": {"inGxf": GFF3, "outTable": O("p13c_gri.xls")},
    "GxfToGenePos": {"inGxf": GFF3, "outPos": O("p13c_gtp.pos")},
    "McScanXFileMerge": {"inCollinearity1": os.path.abspath(f"{E}/synteny/test.collinearity"),
                          "inCollinearity2": os.path.abspath(f"{E}/synteny/dual.collinearity"),
                          "outFile": O("p13c_msm.collinearity")},
    "MemeSuiteXmlToTab": {"inMemeXml": MAST, "outTable": O("p13c_meme.tsv")},
    "OrfPredictMax": {"inGenome": genome_small, "outPep": O("p13c_orf.pep")},
    "QuickGeneFamilyIdentification": {"queryPep": FA, "subjectPep": FA2, "outDir": O("p13c_qf")},
    "ReciprocalBlast": {"queryFasta": FA, "subjectFasta": FA2, "outputPrefix": O("p13c_rb"), "evalue": "1e-5"},
    "TableRowManipulator": {"inputPath": DEG, "outputPath": O("p13c_trm.tsv")},
    "TrimMsaGblocks": {"inAlignment": msa, "outAlignment": O("p13c_tg.fa")},
    "TrimMsaSimple": {"inAlignment": msa, "outAlignment": O("p13c_ts.fa")},
    "BlastCompareTwoSeqBigFileSet": {"queryPath": FA, "subjectPath": FA2, "outputPath": O("p13c_bb.txt"), "options": {"blastType": "blastp", "outFmt": "0", "evalue": "10"}},
    "BlastCompareTwoSeqSet": {"queryPath": FA, "subjectPath": FA2, "outputPath": O("p13c_bs.txt"), "options": {"blastType": "blastp", "outFmt": "0", "evalue": "10"}},
}

passed, failed = [], []
restarts = 0
for base, params in SPEC.items():
    resp, err = call(base + ".process", params)
    if resp is None:
        restarts += 1
        failed.append((base, "SERVER: " + err))
        print("dead  ", base, flush=True)
        continue
    try:
        ok = '"error"' not in resp
    except Exception:
        ok = False
    if ok:
        passed.append(base); print("PASS ", base, flush=True)
    else:
        try:
            msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "") or json.loads(resp).get("error", {}).get("message", "")
        except Exception:
            msg = resp[:80]
        failed.append((base, msg[:90])); print("fail ", base, msg[:60], flush=True)

w(f"\n## 三轮重试后通过 {len(passed)}\n\n" + (", ".join(sorted(passed)) if passed else "（无）"))
w(f"\n## 仍失败 {len(failed)}（服务不可用 {restarts}）\n")
w("| 方法 | 错误 |")
w("|---|---|")
for b, msg in failed:
    w(f"| {b} | {msg} |")
print(f"\nP13C: pass={len(passed)} fail={len(failed)} server_unavailable={restarts}", flush=True)
w("\n\n## Phase 13c 完")
LOG.close()
print("P13c done", flush=True)

