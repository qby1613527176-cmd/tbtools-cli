import sys
# -*- coding: utf-8 -*-
"""P16d：终局微调（重建 IDLIST/N37第四起 + SRA XML 样本 + 类型解析重试可选位）"""
import io, os, json, re, time, subprocess, urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
for k in ("HTTP_PROXY","http_proxy","HTTPS_PROXY","https_proxy","ALL_PROXY","all_proxy"):
    os.environ.pop(k, None)
os.environ["NO_PROXY"] = "127.0.0.1,localhost"; os.environ["no_proxy"] = "127.0.0.1,localhost"
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P16D_LOG.md", "w", encoding="utf-8", newline="\n")
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
FA  = os.path.abspath(f"{E}/blast/query.fa"); FA2 = os.path.abspath(f"{E}/blast/subject.fa")
GFF3= os.path.abspath(f"{E}/gxf/input.gff3"); GFF3b= os.path.abspath(f"{E}/gene_structure.gff")
DEG = os.path.abspath(f"{E}/deg.txt"); CHRL = os.path.abspath(f"{E}/synteny/chrlen.txt")
IDLIST=os.path.abspath(f"{E}/fasta/extract.idlist.txt")
GTF = T + r"\out\p9\p9_test.gtf"; MSA = T + r"\out\p13\msa.fa"; GEN = T + r"\out\p13\genome2m.fa"
NWK = os.path.abspath(f"{E}/phylogeny/phylo.nwk"); EXPR = os.path.abspath(f"{E}/expr/expr.tsv")
VCF = os.path.abspath(f"{E}/gwas/sample.vcf"); COLL = os.path.abspath(f"{E}/synteny/test.collinearity")
MAPF= os.path.abspath(f"{E}/gxf/rename.map.tsv")
MAST= os.path.abspath(f"{E}/meme/sample.mast.xml")
BXMLE = T + r"\out\p10\p10_blast.xml"
PCARE= T + r"\out\p4b_plantcare.tsv"
OUT = T + r"\out\p16"; DBPREFIX = OUT + r"\blastdb_subject"
def O(n): return OUT + "\\" + n

# ---- 1) 重建 0 字节 extract.idlist.txt（N37 第四起）----
n37_note = ""
if os.path.getsize(IDLIST) == 0:
    ids = [l[1:].split()[0] for l in io.open(FA, encoding="utf-8", errors="replace") if l.startswith(">")]
    io.open(IDLIST, "w", encoding="utf-8", newline="\n").write("\n".join(ids) + "\n")
    n37_note = f"extract.idlist.txt 曾为 0 字节，已由 query.fa 重建（{len(ids)} IDs）——**N37 第四起输入清空**"
    w(f"# N37 第四起：{n37_note}\n")
    print("N37 #4: extract.idlist.txt rebuilt", flush=True)

# ---- 2) SRA XML 最小样本 ----
SRAXML = O("sra_sample.xml")
io.open(SRAXML, "w", encoding="utf-8", newline="\n").write(
    '<?xml version="1.0"?>\n<EXPERIMENT_PACKAGE_SET><EXPERIMENT_PACKAGE>'
    '<EXPERIMENT><IDENTIFIERS><PRIMARY_ID>SRX1</PRIMARY_ID></IDENTIFIERS>'
    '<TITLE>test</TITLE></EXPERIMENT_PACKAGE></EXPERIMENT_PACKAGE_SET>')

GENE1 = ""
for l in io.open(GFF3, encoding="utf-8", errors="replace"):
    if l.startswith("#"): continue
    f = l.split("\t")
    if len(f) >= 9 and f[2] == "gene":
        m = re.search(r'ID=([^;]+)', f[8])
        if m: GENE1 = m.group(1); break
IDARR = [GENE1 or "gene1"]

def parse_typed(msg):
    """从校验报错解析期望值"""
    m = re.search(r'must be one of:\s*([A-Za-z0-9_|]+)', msg)
    if m: return m.group(1).split("|")[0]
    m = re.search(r'must be ([A-Z]\w*)(?:,| or )', msg)
    if m: return m.group(1)
    m = re.search(r'must be (\w+) or (\w+)', msg)
    if m: return m.group(1)
    if "must be a number" in msg or "must be number" in msg: return "1.5"
    return None

POOL = [(r"xml|mast", MAST), (r"blastxml", BXMLE), (r"dbprefix", DBPREFIX),
        (r"swissprot|sprot|db\b", FA2), (r"query|protein|pep", FA),
        (r"subject|target|ref", FA2), (r"msa|align", MSA), (r"genome|window", GEN),
        (r"gtf", GTF), (r"gff3|gene_struct", GFF3b), (r"gxf|gff", GTF),
        (r"vcf", VCF), (r"collinear|synteny|block", COLL),
        (r"chrlen|len", CHRL), (r"idlist|ids", IDLIST), (r"expr|fpkm", EXPR),
        (r"nwk|tree|newick", NWK), (r"map|rename", MAPF), (r"plantcare", PCARE),
        (r"fa\b|fasta|seq|cds|blast", FA), (r"expr|deg|table|tsv|xls|txt", DEG)]
def fill_val(pname, typ, desc):
    pl = pname.lower(); tl = (typ or "").lower()
    if "output" in pl or pl.startswith("out") or ("prefix" in pl and "db" not in pl) or "report" in pl or "notgood" in pl:
        return O("p16d_" + pname + ".out")
    if pl.endswith("paths"): return [GTF, GFF3b]
    if "array" in tl and not pl.endswith("path"): return IDARR
    if "int" in tl or "integer" in tl:
        return 100 if re.search(r"bin|window|width|height|size|top|margin|dpi|radius|kmer|hits", pl) else 2
    if "bool" in tl: return True
    for pat, v in POOL:
        if re.search(pat, pl): return v
    for pat, v in POOL:
        if re.search(pat, str(desc).lower()): return v
    if re.search(r"uniqid|^id$", pl): return GENE1 or "gene1"
    if re.search(r"featuretag|pattern", pl): return "gene"
    if re.search(r"color|colour", pl): return "#FF0000"
    if re.search(r"mode|type|sort|order|format|scheme|shape|tag", pl): return "gene"
    return "test"

TARGETS = {
    "BlastZone": {"queryPath": FA, "subjectDbPrefixPath": DBPREFIX, "outputPath": O("bzone.tsv")},
    "FastqBlast": {"inputPath": FA, "dbPrefixPath": DBPREFIX, "outputPath": O("fqbl.tsv")},
    "PlantCareClassify": {"inputPath": PCARE, "outputPath": O("pccls.tsv")},
    "SraXmlToTable": {"inputPath": SRAXML, "outputPath": O("sra.tsv")},
    "TableRowManipulator": {"inputPath": DEG, "selectedColumn": 1, "idListPath": IDLIST, "outputPath": O("trm.tsv")},
    "GxfIdAppender": {"inputPath": GTF, "outputPath": O("gxfapp.gff3")},
    "GxfRepresentativeGxf": {"inputPath": GTF, "outputPath": O("gxfrep.gff3")},
    "GxfRepresentativeIds": {"inputPath": GTF, "outputPath": O("gxfrepid.txt")},
    "GXFRenameByMap": {"inGxf": GTF, "mapFile": MAPF, "outGxf": O("gxn.gff3")},
    "ExpressionRpkm": {"countTablePath": EXPR, "lengthTablePath": CHRL, "outputPath": O("rpkm.tsv")},
    "ExpressionTpm": {"countTablePath": EXPR, "lengthTablePath": CHRL, "outputPath": O("tpm.tsv")},
    "ReciprocalBlast": {"queryPath": FA, "subjectPath": FA2, "outputPath": O("rb.tsv")},
    "BestIdConverter": {"inputPath": DEG, "outputPath": O("bic.tsv")},
    "CheckPrimer": {"inputPath": FA, "outputPath": O("primer.tsv")},
    "GffReconstructorBatch": {"inputPath": GFF3b, "notGoodIdsPath": O("notgood.txt"), "outputPath": O("recon.gff3")},
    "GxfGeneFamilyStructErrorDetect": {"cdsIdListPath": IDLIST, "outputPath": O("gxferr.tsv")},
    "AmazingFastaExtract": {"inputPath": FA, "idListPath": IDLIST, "outputPath": O("amz.fa")},
    "GffExtractRegion": {"gxfPath": GFF3b, "regionListPath": T + r"\out\p10\p10_regions.tsv", "outputPath": O("ger.gff3")},
    "QuickGeneFamilyIdentification": {"queryFastaPath": FA, "subjectFastaPath": FA2, "referenceGeneSetPath": IDLIST, "outputPath": O("qgfi")},
    "GffFeatureScan": {"inputPath": GTF, "outputPath": O("gffscan.tsv")},
}
w("# P16d 终局微调\n")
if n37_note: w(f"\n> {n37_note}\n")
w("\n## 基线重试\n")
passed = {}; still_fail = []
for base, seed in TARGETS.items():
    params = dict(seed); ok = False; msg = ""
    for rnd in range(6):
        resp, err = call(base + ".process", params, 200)
        if resp is None: msg = "SERVER:" + err; break
        if '"error"' not in resp: ok = True; break
        try:
            e = json.loads(resp).get("error", {})
            msg = (e.get("data", {}).get("message") if isinstance(e.get("data"), dict) else e.get("data")) or e.get("message") or ""
            msg = str(msg)
        except Exception: msg = resp[:120]
        filled = False
        for p in re.findall(r'([A-Za-z][A-Za-z0-9]+) is required', msg):
            if p not in params: params[p] = fill_val(p, "", msg); filled = True
        nm = re.search(r'([A-Za-z][A-Za-z0-9]+) is not a (?:readable|valid)[^:]*', msg)
        if nm and nm.group(1) in params:
            params[nm.group(1)] = fill_val(nm.group(1), "", msg); filled = True
        if not filled: break
    if ok: passed[base] = params; print(f"PASS {base}", flush=True); w(f"- ✅ {base}")
    else: still_fail.append((base, msg[:80])); print(f"fail {base}: {msg[:70]}", flush=True); w(f"- ❌ {base}: {msg[:80]}")

# ---- 新通过基线的可选位补扫 ----
w("\n## 新通过基线的可选位补扫\n")
total = okc = errc = 0; detail = []
for base, params in passed.items():
    try:
        d = json.loads(rpc("system.describeMethod", {"method": base + ".process"})).get("result", {})
        descj = d.get("description", {}); desc = json.dumps(descj, ensure_ascii=False)
        pdefs = descj.get("params", {}) if isinstance(descj.get("params", {}), dict) else {}
    except Exception: continue
    opt = [(p, str(v)) for p, v in pdefs.items() if "required" not in str(v)]
    for pname, pd in opt:
        if pname in params: continue
        p2 = dict(params); p2[pname] = fill_val(pname, pd, desc)
        resp2, err2 = call(base + ".process", p2, 200)
        total += 1
        if resp2 is not None and '"error"' not in resp2: okc += 1
        else:
            errc += 1
            try:
                e2 = json.loads(resp2).get("error", {}) if resp2 else {}
                m2 = (e2.get("data", {}).get("message") if isinstance(e2.get("data"), dict) else e2.get("data")) or e2.get("message") or err2
                detail.append((base, pname, str(m2)[:90]))
            except Exception: detail.append((base, pname, str(resp2 or err2)[:90]))
    print(f"sweep {base}: opt={len(opt)}", flush=True)

# ---- 类型解析重试（P16c 被拒的 25 位）----
w("\n## 类型解析重试\n")
RETRY = [
    ("BlastCompareTwoSeqRegion", "evalue", "1e-5"),
    ("BlatAlign", "outFormat", "psl"), ("BlatAlign", "minIdentity", "90"),
    ("FastaExtract", "processMode", "Extract"), ("FastaExtract", "matchMode", "Match"),
    ("FastxExtract", "mode", "byId"),
    ("GeneExpFilter", "minExpValue", "1.0"), ("GeneExpFilter", "minExpFilterRatio", "0.5"),
    ("GeneExpFilter", "minCV", "0.1"),
    ("GxfQuickDiagnosis", "utrRelax", "50"),
    ("GxfToGenePos", "featurePattern", "gene"),
    ("McScanXFileMerge", "mode", "PlainText"),
    ("NcbiDownloadBulk", "database", "nuccore"), ("NcbiDownloadBulk", "format", "Fasta"),
    ("NcbiDownloadSimple", "format", "Fasta"),
    ("TrimMsaGblocks", "IS", "100"), ("TrimMsaGblocks", "FS", "50"),
    ("TrimMsaGblocks", "nonGapRatio", "0.5"), ("TrimMsaGblocks", "gapTreatment", "NONE"),
    ("TrimMsaSimple", "ratio", "0.5"),
]
BASEPARAMS = {
    "BlastCompareTwoSeqRegion": {"queryPath": FA, "subjectPath": FA2, "outputPath": O("bcr.tsv")},
    "BlatAlign": {"queryPath": FA, "subjectPath": FA2, "outputPath": O("blat.psl")},
    "FastaExtract": {"inputPath": FA, "idListPath": IDLIST, "outputPath": O("fx.fa")},
    "FastxExtract": {"inputPath": FA, "id": IDARR[0], "outputPath": O("fx2.fa")},
    "GeneExpFilter": {"inputPath": EXPR, "outputPath": O("gef.tsv")},
    "GxfQuickDiagnosis": {"inputPath": GTF, "genomePath": GEN, "outputPath": O("gqd.tsv")},
    "GxfToGenePos": {"inputPath": GTF, "chrLenPath": CHRL, "outputPath": O("gtp2.pos")},
    "McScanXFileMerge": {"inputPaths": [COLL], "outputPath": O("mc.txt")},
    "NcbiDownloadBulk": {"idList": IDARR, "outputPath": O("ncbi")},
    "NcbiDownloadSimple": {"idList": IDARR, "outputPath": O("ncbi2")},
    "TrimMsaGblocks": {"inputPath": MSA, "outputPath": O("trimgb.fa")},
    "TrimMsaSimple": {"inputPath": MSA, "outputPath": O("trims.fa")},
}
rt = rok = 0
for base, pname, val in RETRY:
    bp = BASEPARAMS.get(base)
    if not bp: continue
    p2 = dict(bp); p2[pname] = val
    resp2, err2 = call(base + ".process", p2, 200)
    rt += 1
    if resp2 is not None and '"error"' not in resp2: rok += 1
    print(f"retry {base}[{pname}]={val}: {'ok' if resp2 and chr(34)+'error'+chr(34) not in resp2 else 'reject'}", flush=True)

w(f"\n## 总计\n- 基线重试通过 {len(passed)}/{len(TARGETS)}\n- 补扫可选位 {total}（通过 {okc}，拒绝 {errc}）\n- 类型重试 {rt}（通过 {rok}）")
w("\n### 补扫报错明细\n")
for b, p, m2 in detail: w(f"- {b}[{p}]: {m2}")
w("\n## Phase 16d 完")
LOG.close()
print(f"\nP16D: base_pass={len(passed)}/{len(TARGETS)} opt={total} ok={okc} typed_retry={rok}/{rt}", flush=True)
print("P16d done", flush=True)

