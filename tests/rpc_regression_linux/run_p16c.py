import sys
# -*- coding: utf-8 -*-
"""P16c：可选参数逐位实测终版（重建 GTF + 修 SPEC 路径 + 类型化填充 + 8 轮）"""
import io, os, json, re, time, subprocess, urllib.request, random

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
for k in ("HTTP_PROXY","http_proxy","HTTPS_PROXY","https_proxy","ALL_PROXY","all_proxy"):
    os.environ.pop(k, None)
os.environ["NO_PROXY"] = "127.0.0.1,localhost"; os.environ["no_proxy"] = "127.0.0.1,localhost"
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P16C_LOG.md", "w", encoding="utf-8", newline="\n")
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
XMLE  = T + r"\out\p12\p12_blast_f5.txt"
OUT = T + r"\out\p16"; os.makedirs(OUT, exist_ok=True)
DBPREFIX = OUT + r"\blastdb_subject"
def O(n): return OUT + "\\" + n

# ---- 1) 重建 0 字节的 p9_test.gtf ----
if not os.path.exists(GTF) or os.path.getsize(GTF) == 0:
    rows = []
    tx2gene = {}
    for l in io.open(GFF3b, encoding="utf-8", errors="replace"):
        if l.startswith("#") or not l.strip(): continue
        f = l.rstrip("\n").split("\t")
        if len(f) < 9: continue
        typ, s, e, attr = f[2], f[3], f[4], f[8]
        def av(k, attr=attr):
            for kv in attr.split(";"):
                kv = kv.strip()
                if kv.startswith(k + "="): return kv[len(k)+1:].strip('"')
            return ""
        if typ == "gene":
            rows.append((f[0], f[1], "gene", s, e, ".", f[6], ".", f'gene_id "{av("ID")}";'))
            tx2gene[av("ID")] = av("ID")
        elif typ in ("mRNA", "transcript"):
            tid = av("ID"); gid = av("Parent"); tx2gene[tid] = gid
            rows.append((f[0], f[1], "transcript", s, e, ".", f[6], ".", f'gene_id "{gid}"; transcript_id "{tid}";'))
        elif typ in ("exon", "CDS"):
            tid = av("Parent")
            rows.append((f[0], f[1], typ, s, e, ".", f[6], f[7] if typ == "CDS" else ".",
                         f'gene_id "{tx2gene.get(tid, tid)}"; transcript_id "{tid}";'))
    with io.open(GTF, "w", encoding="utf-8", newline="\n") as fo:
        for r in rows: fo.write("\t".join(r) + "\n")
    print(f"GTF regenerated: {len(rows)} rows", flush=True)
w(f"# P16c\n\n- GTF 重建: {os.path.getsize(GTF)} bytes\n")

# ---- 2) 建 BLAST 库前缀（BlastZone/FastqBlast 需要 .nhr）----
if not os.path.exists(DBPREFIX + ".p*1") and not os.path.exists(DBPREFIX + ".pin"):
    try:
        rc = subprocess.run(["makeblastdb", "-in", FA2, "-dbtype", "prot", "-out", DBPREFIX],
                            capture_output=True, timeout=120)
        print("makeblastdb rc=", rc.returncode, flush=True)
    except FileNotFoundError:
        print("makeblastdb not found", flush=True)

# ---- 3) 真实基因 ID ----
GENE1 = ""
for l in io.open(GFF3, encoding="utf-8", errors="replace"):
    if l.startswith("#"): continue
    f = l.split("\t")
    if len(f) >= 9 and f[2] == "gene":
        m = re.search(r'ID=([^;]+)', f[8])
        if m: GENE1 = m.group(1); break
IDARR = [GENE1 or "gene1"]

# ---- 4) SPEC ----
src = io.open(T + r"\run_p13.py", encoding="utf-8").read()
mvar = re.search(r"(^random\.seed\(7\).*?)(^names = json\.loads)", src, re.S | re.M)
SPEC = {}
if mvar:
    _env = {"os": os, "re": re, "random": __import__("random"), "io": io,
            "T": T, "PUB": T + r"\data\public", "OUT": T + r"\out\p13", "E": E,
            "genome_small": GEN, "msa": MSA, "cds": T + r"\out\p13\cds.fa",
            "prom": T + r"\out\p13\promoters.fa",
            "regions_fix": T + r"\out\p10\p10_regions.tsv",
            "XMLE": XMLE}
    exec(mvar.group(1), _env)
    SPEC = _env.get("SPEC") or {}
SPEC.update({
    "QuickGeneFamilyIdentification": {"queryFastaPath": FA, "subjectFastaPath": FA2, "referenceGeneSetPath": IDLIST, "outputPath": O("qgfi")},
    "QuickProteinAnno": {"proteinPath": FA, "swissProtDbPath": FA2, "outputPath": O("qpa.tsv")},
    "GxfCat": {"inputPaths": [GFF3, GFF3b], "conflictPrefixPath": O("conflict.tsv"), "outputPath": O("gxfcat.gff3")},
    "FastxExtract": {"inputPath": FA, "id": [l[1:].split()[0] for l in io.open(FA, encoding="utf-8", errors="replace") if l.startswith(">")][0], "outputPath": O("fastx.fa")},
    "FastaWindowStat": {"inputPath": GEN, "windowSize": 1000, "outputPath": O("fws.xls")},
    "GxfToGenePos": {"inputPath": GTF, "chrLenPath": CHRL, "outputPath": O("gtp.pos")},
    "TableRowManipulator": {"inputPath": DEG, "selectedColumn": 1, "idListPath": IDLIST, "outputPath": O("trm.tsv")},
    "GffExtractRegion": {"gxfPath": GFF3b, "regionListPath": T + r"\out\p10\p10_regions.tsv", "outputPath": O("ger.gff3")},
    "BlastXmlToTable": {"inputXmlPath": BXMLE, "outputPath": O("b5.tsv"), "tableFormat": "Summary"},
    "MemeSuiteXmlToTab": {"inputPath": MAST, "outputPath": O("meme.tsv")},
    "GxfFilter": {"inputPath": GTF, "idList": IDARR, "outputPath": O("gxffilter.gff3")},
    "GffCdsPhase": {"inputPath": GFF3b, "outputPath": O("cdsphase.tsv")},
    "GffFeatureExtract": {"inputPath": GFF3b, "uniqId": GENE1 or "gene1", "outputPath": O("gfffeat.gff3")},
    "GtfFeatureExtract": {"inputPath": GTF, "uniqId": GENE1 or "gene1", "outputPath": O("gtffeat.gtf")},
    "GffReconstructorBatch": {"inputPath": GFF3b, "notGoodIdsPath": O("notgood.txt"), "outputPath": O("recon.gff3")},
    "GxfSeqExtract": {"inputPath": GTF, "featureTag": "gene", "outputPath": O("gxfseq.fa")},
    "GxfGeneFamilyStructErrorDetect": {"cdsIdListPath": IDLIST, "outputPath": O("gxferr.tsv")},
    "BlastZone": {"subjectDbPrefixPath": DBPREFIX, "queryPath": FA, "outputPath": O("blastzone.tsv")},
    "FastqBlast": {"dbPrefixPath": DBPREFIX, "inputPath": FA, "outputPath": O("fqblast.tsv")},
    "AmazingFastaExtract": {"inputPath": FA, "idListPath": IDLIST, "outputPath": O("amz.fa")},
    "FastaExtract": {"inputPath": FA, "idListPath": IDLIST, "outputPath": O("fx.fa")},
    "ExpressionRpkm": {"countTablePath": EXPR, "lengthTablePath": CHRL, "outputPath": O("rpkm.tsv")},
    "ExpressionTpm": {"countTablePath": EXPR, "lengthTablePath": CHRL, "outputPath": O("tpm.tsv")},
    "FastaSsrMiner": {"inputPath": GEN, "outputPath": O("ssr.tsv")},
    "FastaStat": {"inputPath": FA, "outputPath": O("fstat.tsv")},
    "TableToFasta": {"inputPath": DEG, "outputPath": O("t2f.fa")},
    "CheckPrimer": {"inputPath": FA, "outputPath": O("primer.tsv")},
    "GfaToFasta": {"inputPath": os.path.abspath(f"{E}/fasta/sample.gfa") if os.path.exists(f"{E}/fasta/sample.gfa") else FA, "outputPath": O("gfa.fa")},
    "ReciprocalBlast": {"queryPath": FA, "subjectPath": FA2, "outputPath": O("rb.tsv")},
    "BestIdConverter": {"inputPath": DEG, "outputPath": O("bic.tsv")},
    "AmazingHeatMap": {"inputPath": EXPR, "outputPath": O("ahm.png")},
    "FastaPatternLocate": {"inputPath": FA, "pattern": "ATG", "outputPath": O("fpl.tsv")},
    "BlastCompareTwoSeqRegion": {"queryPath": FA, "subjectPath": FA2, "outputPath": O("bcr.tsv")},
    "BlatAlign": {"queryPath": FA, "subjectPath": FA2, "outputPath": O("blat.psl")},
})

GUARD = {"deg.txt": DEG, "query.fa": FA, "gene_structure.gff": GFF3b}
BK = T + r"\backup_examples_data_p16"
def guard_zeroed():
    z = []
    for k, v in GUARD.items():
        if os.path.exists(v) and os.path.getsize(v) == 0:
            z.append(k)
            s = os.path.join(BK, k)
            if os.path.exists(s): io.open(v, "wb").write(io.open(s, "rb").read())
    return z

POOL = [(r"xml|mast", MAST), (r"blastxml", BXMLE),
        (r"dbprefix|db_prefix", DBPREFIX),
        (r"swissprot|sprot|db\b", FA2), (r"query|protein|pep", FA),
        (r"subject|target|ref", FA2), (r"msa|align", MSA), (r"genome|window", GEN),
        (r"gtf", GTF), (r"gff3|gene_struct", GFF3b), (r"gxf|gff", GTF),
        (r"vcf", VCF), (r"collinear|synteny|block", COLL),
        (r"chrlen|len", CHRL), (r"idlist|ids", IDLIST), (r"expr|fpkm", EXPR),
        (r"nwk|tree|newick", NWK), (r"map|rename", MAPF),
        (r"fa\b|fasta|seq|cds|blast", FA), (r"expr|deg|table|tsv|xls|txt", DEG)]
def fill_val(pname, typ, desc):
    pl = pname.lower(); tl = (typ or "").lower()
    if "output" in pl or pl.startswith("out") or "prefix" in pl and "db" not in pl or "report" in pl or "notgood" in pl:
        return O("p16c_" + pname + ".out")
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
    if re.search(r"featuretag|feature_pattern|pattern", pl): return "gene"
    if re.search(r"color|colour", pl): return "#FF0000"
    if re.search(r"mode|type|sort|order|format|scheme|shape|tag", pl): return "gene"
    return "test"

SKIP = {"OneStepBuildATree", "SendEmail"}
if not ensure(): raise SystemExit("server down")
_names = json.loads(rpc("system.listMethods")).get("result")
_names = _names.get("methods") if isinstance(_names, dict) else _names
methods = [m for m in (_names or []) if isinstance(m, str) and m.endswith(".process")]
w(f"\n跳过: {', '.join(sorted(SKIP))}\n")
total = okc = errc = 0
base_fail = []; detail = []
for m in sorted(methods):
    base = m[:-len(".process")]
    if base in SKIP: continue
    try:
        d = json.loads(rpc("system.describeMethod", {"method": m})).get("result", {})
        descj = d.get("description", {}); desc = json.dumps(descj, ensure_ascii=False)
        pdefs = descj.get("params", {}) if isinstance(descj.get("params", {}), dict) else {}
    except Exception as ex:
        w(f"- {base}: describe 失败 {ex}"); continue
    req = [(p, str(v)) for p, v in pdefs.items() if "required" in str(v)]
    opt = [(p, str(v)) for p, v in pdefs.items() if "required" not in str(v)]
    if not req: continue
    params = dict(SPEC.get(base, {}))
    ok = False; msg = ""; tried = {}
    for rnd in range(8):
        resp, err = call(m, params, 200)
        if resp is None: msg = "SERVER:" + err; break
        if '"error"' not in resp: ok = True; break
        try:
            e = json.loads(resp).get("error", {})
            msg = (e.get("data", {}).get("message") if isinstance(e.get("data"), dict) else e.get("data")) or e.get("message") or ""
            msg = str(msg)
        except Exception: msg = resp[:120]
        filled = False
        for p in re.findall(r'([A-Za-z][A-Za-z0-9]+) is required', msg):
            if p not in params: params[p] = fill_val(p, pdefs.get(p, ""), desc); filled = True
        nm = re.search(r'([A-Za-z][A-Za-z0-9]+) is not a (?:readable|valid)[^:]*file', msg)
        if nm and nm.group(1) in params and tried.get(nm.group(1), 0) < 2:
            tried[nm.group(1)] = tried.get(nm.group(1), 0) + 1
            params[nm.group(1)] = fill_val(nm.group(1), pdefs.get(nm.group(1), ""), desc); filled = True
        if not filled: break
    z = guard_zeroed()
    if z: print(f"🚨 N37: {base} {z}", flush=True); w(f"- 🚨 **{base} 清空 {z}**")
    if not ok:
        base_fail.append((base, msg[:80])); print(f"base-fail {base}: {msg[:70]}", flush=True)
        w(f"- {base}: 基线未通（{msg[:80]}）")
        continue
    for pname, pd in opt:
        if pname in params: continue
        p2 = dict(params); p2[pname] = fill_val(pname, pd, desc)
        resp2, err2 = call(m, p2, 200)
        total += 1
        z = guard_zeroed()
        if resp2 is not None and '"error"' not in resp2: okc += 1
        else:
            errc += 1
            try:
                e2 = json.loads(resp2).get("error", {}) if resp2 else {}
                m2 = (e2.get("data", {}).get("message") if isinstance(e2.get("data"), dict) else e2.get("data")) or e2.get("message") or err2
                detail.append((base, pname, str(m2)[:90]))
            except Exception: detail.append((base, pname, str(resp2 or err2)[:90]))
        if z: print(f"🚨 N37: {base}[{pname}] {z}", flush=True); w(f"- 🚨 **{base}[{pname}] 清空 {z}**")
    print(f"P16c {base}: req={len(req)} opt={len(opt)}", flush=True)
w(f"\n## 总计\n- 基线未通：{len(base_fail)}\n- 可选位实测：{total}，通过 {okc}，拒绝 {errc}\n\n### 报错明细（前 50）\n")
for b, p, m2 in detail[:50]: w(f"- {b}[{p}]: {m2}")
w("\n## Phase 16c 完")
LOG.close()
print(f"\nP16C: opt={total} ok={okc} err={errc} base_fail={len(base_fail)}", flush=True)
print("P16c done", flush=True)

