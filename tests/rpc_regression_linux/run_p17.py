import sys
# -*- coding: utf-8 -*-
"""P17：最后一轮收口——自造匹配数据救 ExpressionRpkm/Tpm 等 + 波动项复测 + NCBI 网络试"""
import io, os, json, re, time, subprocess, urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
for k in ("HTTP_PROXY","http_proxy","HTTPS_PROXY","https_proxy","ALL_PROXY","all_proxy"):
    os.environ.pop(k, None)
os.environ["NO_PROXY"] = "127.0.0.1,localhost"; os.environ["no_proxy"] = "127.0.0.1,localhost"
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P17_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s): LOG.write(s + "\n"); LOG.flush()
def rpc(m, p=None, timeout=240):
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
def call(m, p, timeout=240):
    for _ in range(2):
        if not ensure(): return None, "SERVER_DOWN"
        try: return rpc(m, p, timeout), "ok"
        except Exception as ex:
            last = str(ex); time.sleep(1)
    return None, last

E = "examples/data"
FA  = os.path.abspath(f"{E}/blast/query.fa"); FA2 = os.path.abspath(f"{E}/blast/subject.fa")
GFF3= os.path.abspath(f"{E}/gxf/input.gff3"); GFF3b= os.path.abspath(f"{E}/gene_structure.gff")
DEG = os.path.abspath(f"{E}/deg.txt"); CHRL = os.path.abspath(f"{E}/synteny/chrlen.txt")
IDLIST=os.path.abspath(f"{E}/fasta/extract.idlist.txt")
GTF = T + r"\out\p9\p9_test.gtf"; MSA = T + r"\out\p13\msa.fa"
OUT = T + r"\out\p17"; os.makedirs(OUT, exist_ok=True)
def O(n): return OUT + "\\" + n

# ---- 自造匹配的表达/长度表（同基因 ID）----
GENES = {}
for l in io.open(GFF3b, encoding="utf-8", errors="replace"):
    if l.startswith("#") or not l.strip(): continue
    f = l.split("\t")
    if len(f) >= 9 and f[2] == "gene":
        m = re.search(r'ID=([^;]+)', f[8])
        if m:
            g = m.group(1)
            GENES[g] = int(f[4]) - int(f[3]) + 1
CNT = O("counts.tsv"); LEN = O("length.tsv")
with io.open(CNT, "w", encoding="utf-8", newline="\n") as fo:
    fo.write("gene\tcount\n")
    for i, g in enumerate(GENES): fo.write(f"{g}\t{(i+1)*137}\n")
with io.open(LEN, "w", encoding="utf-8", newline="\n") as fo:
    fo.write("gene\tlength\n")
    for g, L in GENES.items(): fo.write(f"{g}\t{max(L,1)}\n")

# ---- 自造较完整 SRA XML ----
SRAXML = O("sra_full.xml")
pkg = ""
for i in range(2):
    pkg += (f'<EXPERIMENT_PACKAGE><EXPERIMENT><IDENTIFIERS><PRIMARY_ID>SRX{i}</PRIMARY_ID></IDENTIFIERS>'
            f'<TITLE>demo{i}</TITLE><STUDY_REF accession="SRP0"/><DESIGN><SAMPLE_DESCRIPTOR accession="SRS{i}"/>'
            f'</DESIGN></EXPERIMENT><RUN_SET><RUN accession="SRR{i}" total_spots="100">'
            f'<SRAFiles><SRAFile><Alternatives><URL>ftp://x/{i}.sra</URL></Alternatives></SRAFile></SRAFiles>'
            f'</RUN></RUN_SET></EXPERIMENT_PACKAGE>')
io.open(SRAXML, "w", encoding="utf-8", newline="\n").write(
    '<?xml version="1.0"?>\n<EXPERIMENT_PACKAGE_SET>' + pkg + '</EXPERIMENT_PACKAGE_SET>')

GENE1 = next(iter(GENES), "gene1")
TARGETS = {
    "ExpressionRpkm": {"countTablePath": CNT, "lengthTablePath": LEN, "outputPath": O("rpkm.tsv")},
    "ExpressionTpm": {"countTablePath": CNT, "lengthTablePath": LEN, "outputPath": O("tpm.tsv")},
    "SraXmlToTable": {"inputPath": SRAXML, "outputPath": O("sra.tsv")},
    "GffReconstructorBatch": {"inputPath": GFF3, "notGoodIdsPath": O("notgood.txt"), "outputPath": O("recon.gff3")},
    "GxfGeneFamilyStructErrorDetect": {"cdsIdListPath": IDLIST, "outputPath": O("gxferr.tsv")},
    # 波动项复测
    "ReciprocalBlast": {"queryPath": FA, "subjectPath": FA2, "outputPath": O("rb.tsv")},
    "BestIdConverter": {"inputPath": DEG, "outputPath": O("bic.tsv")},
    "GXFRenameByMap": {"inGxf": GTF, "mapFile": os.path.abspath(f"{E}/gxf/rename.map.tsv"), "outGxf": O("gxn.gff3")},
    "GffExtractRegion": {"gxfPath": GFF3b, "regionListPath": T + r"\out\p10\p10_regions.tsv", "outputPath": O("ger.gff3")},
    "QuickGeneFamilyIdentification": {"queryFastaPath": FA, "subjectFastaPath": FA2, "referenceGeneSetPath": IDLIST, "outputPath": O("qgfi")},
    # NCBI（试网络）
    "NcbiDownloadSimple": {"idList": ["NM_000546"], "database": "nuccore", "format": "Fasta", "outputPath": O("ncbi")},
}
w("# P17 最后一轮收口\n")
passed, still = [], []
for base, seed in TARGETS.items():
    params = dict(seed); ok = False; msg = ""
    for rnd in range(6):
        resp, err = call(base + ".process", params, 240)
        if resp is None: msg = "SERVER:" + err; break
        if '"error"' not in resp: ok = True; break
        try:
            e = json.loads(resp).get("error", {})
            msg = (e.get("data", {}).get("message") if isinstance(e.get("data"), dict) else e.get("data")) or e.get("message") or ""
            msg = str(msg)
        except Exception: msg = resp[:120]
        filled = False
        for p in re.findall(r'([A-Za-z][A-Za-z0-9]+) is required', msg):
            if p not in params:
                pl = p.lower()
                params[p] = O("p17_" + p + ".out") if ("output" in pl or "report" in pl) else (GENES and list(GENES)[0] or FA)
                filled = True
        if not filled: break
    (passed if ok else still).append((base, msg[:90]))
    print(("PASS " if ok else "fail ") + base + ": " + msg[:70], flush=True)
w("\n## 结果\n")
for b, m2 in passed: w(f"- ✅ {b}")
for b, m2 in still: w(f"- ❌ {b}: {m2}")
w("\n## Phase 17 完")
LOG.close()
print(f"\nP17: pass={len(passed)} fail={len(still)}", flush=True)
print("P17 done", flush=True)

