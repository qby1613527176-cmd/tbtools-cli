import sys
#!/usr/bin/env python
"""Phase2: tbtools tool <name> 全量——先无参抓引擎 [Usage]，再对可映射工具带参实跑"""
import io, os, re, subprocess, sys, time

os.environ.setdefault("TBTOOLS_JAR", "C:/Program Files/TBtools/TBtools_JRE1.6.jar")
os.environ["PATH"] = "C:\\Program Files\\TBtools\\bin;" + os.environ.get("PATH", "")  # 确保子进程能找到 java（Windows PATH 需反斜杠）
ROOT = os.environ["TBROOT"]
PY = sys.executable
os.chdir(os.path.dirname(os.path.abspath(__file__)))
LOG = io.open("P2_LOG.md", "w", encoding="utf-8", newline="\n")

def w(s=""):
    LOG.write(s + "\n"); LOG.flush()

def run(cmd, timeout=180):
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL)
    try:
        out, err = p.communicate(timeout=timeout)
        return (out.decode("utf-8", "replace"), err.decode("utf-8", "replace"),
                p.returncode, time.time() - t0)
    except subprocess.TimeoutExpired:
        # Windows: 杀整棵进程树释放管道，防止孙进程（GUI/守护 java）握住句柄
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
        try:
            out, err = p.communicate(timeout=5)
        except Exception:
            out, err = b"", b""
        return (out.decode("utf-8", "replace"), err.decode("utf-8", "replace"),
                -99, time.time() - t0)

def block(out, err, ec, dt, limit=7000):
    p = []
    if out.strip():
        o = out if len(out) <= limit else out[:limit] + f"\n…[截断, 共{len(out)}字符]"
        p.append("```\n" + o.rstrip() + "\n```")
    if err.strip():
        e = err if len(err) <= limit else err[:limit] + f"\n…[截断, 共{len(err)}字符]"
        p.append("**stderr:**\n```\n" + e.rstrip() + "\n```")
    if not p: p.append("```\n(无输出)\n```")
    p.append(f"退出码 `{ec}` · {dt:.1f}s")
    return "\n\n".join(p)

NACL = "data/monarda_chloro.clean.fa"; CDS = "data/monarda_chloro_cds.fa"
CHPEP = "data/monarda_chloro_pep.fa"; GFF = "data/monarda_chloro.gff3"
PEP = "out/pin_family_full.fa"; PEP10 = "out/pin10.fa"; MSA = "out/pin_msa3.fa"
EXPR = "out/pin_expr.tsv"; MAT = "out/atpin_sipin_matrix.tsv"; XML = "out/t2b5.xml"; FQ = "out/sim_reads.fq"
IDS = "out/chloro_ids.txt"; TAB6 = "out/blast_atpin_si.tab"; EMBL = "data/monarda_chloro.embl"

# 注册表工具清单
reg = {}
for l in io.open(os.path.join(ROOT, "tbtools_cli", "cli_tools_registry.py")):
    m = re.match(r'\s+"([^"]+)":\s+"([^"]+)",', l)
    if m: reg[m.group(1)] = m.group(2)

w("# Phase 2：CLI 工具层全量测试（tbtools tool <name>）\n")
w(f"注册表工具 {len(reg)} 个。每个工具先无参运行抓引擎真实 `[Usage]`（签名权威来源），"
  "再对能构造真实输入的工具带参实跑。\n")

# 可映射实跑参数（基于对签名族惯例的了解；错误输出同样是有效反馈）
M = {
 "statFasta": ["--inFasta", PEP, "--outPutFile", "out/p2_stat.xls"],
 "extractFasta": ["--inFa", CHPEP, "--inIDList", IDS, "--outFa", "out/p2_ext.fa"],
 "extractFastaSub": ["--inFa", "data/monarda_chloro.clean.fa", "--inRegion", "out/coords.bed", "--outFa", "out/p2_sub.fa"],
 "fastaIDAppender": ["--inFasta", PEP10, "--outFasta", "out/p2_idapp.fa", "--appendText", "MON_"],
 "FastaIDRenamer": ["--inFasta", PEP10, "--outFasta", "out/p2_idren.fa", "--mapFile", "out/si_rename_map.tsv"],
 "FastaIDSimplifier": ["--inFasta", PEP, "--outFasta", "out/p2_idsimp.fa"],
 "FastaLongestRepresentater": ["--inFasta", PEP, "--outFasta", "out/p2_longest.fa"],
 "fastaFragmenter": ["--inFasta", NACL, "--outFasta", "out/p2_frag.fa", "--fragmentSize", "10000"],
 "quickSplitFasta": ["--inFasta", PEP, "--outDir", "out/p2_split", "--seqsPerFile", "20"],
 "makeFastaIndex": ["--inFasta", "data/monarda_chloro.clean.fa", "--outIndex", "out/p2_faid.idx"],
 "getLongestORF": ["--inFasta", CDS, "--outFasta", "out/p2_orf.pep"],
 "getLongestCompleteORF": ["--inFasta", CDS, "--outFasta", "out/p2_orfc.pep"],
 "translater": ["--inFasta", CDS, "--outFasta", "out/p2_trans.pep"],
 "ssrMiner": ["--inFasta", NACL, "--outFile", "out/p2_ssr.xls"],
 "emblToFasta": ["--inFile", EMBL, "--outFile", "out/p2_embl.fa"],
 "gbff2gff": ["--inFile", "out/p2_fake.gbff", "--outFile", "out/p2_gbff.gff3"],
 "rpkmCal": ["--countsTable", "out/counts.tsv", "--lenInfo", "out/genelen.tsv", "--outTable", "out/p2_rpkm.tsv"],
 "tpmCalc": ["--countsTable", "out/counts.tsv", "--lenInfo", "out/genelen.tsv", "--outTable", "out/p2_tpm.tsv"],
 "fpkmToTpm": ["--fpkmTable", "out/p2_rpkm.tsv", "--tpmTable", "out/p2_fpkm2tpm.tsv"],
 "geneExpFilter": ["--inTable", EXPR, "--outTable", "out/p2_expfilter.tsv", "--minExp", "5"],
 "genePairExpCorr": ["--inTable", EXPR, "--outTable", "out/p2_paircorr.tsv"],
 "TableCast": ["--inLongTable", "out/long_table.tsv", "--outMatrix", "out/p2_cast.tsv"],
 "TableMelt": ["--inMatrix", EXPR, "--outLongTable", "out/p2_melt.tsv"],
 "TableColSelector": ["--inTable", EXPR, "--outTable", "out/p2_colselect.tsv", "--colName", "Root"],
 "tableColSelect": ["--inTable", EXPR, "--outTable", "out/p2_colselect2.tsv", "Root", "Leaf"],
 "tableColSel": ["--inTable", EXPR, "--outTable", "out/p2_colSel.tsv", "--idList", "out/pin10_ids.txt"],
 "tableCollapse": ["--inTable", EXPR, "--keyColIndex", "0", "--outTable", "out/p2_collapse.tsv"],
 "tableTranspose": ["--inTable", EXPR, "--outTable", "out/p2_transpose.tsv"],
 "tableUniq": ["--inTable", EXPR, "--outFile", "out/p2_uniq.txt", "--colIndex", "0"],
 "tableSplit": ["--inTable", EXPR, "--outDir", "out/p2_tsplit", "--colIndex", "0"],
 "tableAppend": ["--inTab1", EXPR, "--inTab2", MAT, "--outTab", "out/p2_append.tsv"],
 "tableMerge": ["--outTable", "out/p2_merge.tsv", "--inFileArr", f"{EXPR},{MAT}", "--inColIndexArr", "0,0"],
 "mimicVqsr": ["--inFile", "out/p2_fake.vcf", "--outFile", "out/p2_vqsr.txt"],
 "vcfAddID": ["--inVcf", "out/p2_fake.vcf", "--outVcf", "out/p2_vcfaddid.vcf"],
 "vcfBinCount": ["--inVcf", "out/p2_fake.vcf", "--outFile", "out/p2_vcfbin.tsv"],
 "tandemDupFinder": ["--inGff", GFF, "--outFile", "out/p2_tandem.tsv"],
 "blastXmlToTable": ["--inXml", XML, "--outTable", "out/p2_xml2tab.tsv"],
 "blastXmlSummaryTable": ["--inXml", XML, "--outTable", "out/p2_xmlsum.tsv"],
 "Fasta36m10toTable": ["--inFile", "out/p2_m10.txt", "--outTable", "out/p2_m10tab.tsv"],
 "regionBlast": ["--queryFasta", PEP10, "--blastDb", "out/smdb_manual", "--regionBed", "out/coords.bed", "--outFile", "out/p2_regionblast.tsv"],
 "autoMakeBlastDb": ["--inFasta", "data/si_proteome.fa", "--outDbName", "out/p2_db"],
 "quickLocateSeqPattern": ["--inFasta", NACL, "--pattern", "GAATTC", "--outFile", "out/p2_pattern.tsv"],
 "OverlapGeneModels": ["--inGxf1", GFF, "--inGxf2", "out/chloro_sorted_p1.gff3", "--outFile", "out/p2_overlap.tsv"],
 "GXFOverlaper": ["--inGxf", GFF, "--inRegion", "out/region.txt", "--outGxf", "out/p2_gxfoverlap.gff3"],
 "RegionGXFOverlapAnnotation": ["--inGxf", GFF, "--inRegion", "out/region.txt", "--outTable", "out/p2_regionanno.tsv"],
 "ExtractFeaturefromGFF3andGenome": ["--inGff", GFF, "--inGenome", "data/monarda_chloro.clean.fa", "--outFile", "out/p2_extractfeat.fa", "--featureType", "CDS"],
 "extractFeatureFromGTF": ["--inGtf", GFF, "--inGenome", "data/monarda_chloro.clean.fa", "--outFile", "out/p2_gtffeat.fa"],
 "extractGff3Region": ["--inGff", GFF, "--region", "monarda_chloro:1000-50000", "--outGff", "out/p2_gffregion.gff3"],
 "gffCdsPhaseCorrector": ["--inGff", GFF, "--outGff", "out/p2_phase.gff3"],
 "sRNAReadTrimmer": ["--inFastq", FQ, "--outFastq", "out/p2_srnafq.fq", "--minLen", "18"],
 "sRNAseqReadLenStat": ["--inFastq", FQ, "--outFile", "out/p2_srnastat.tsv"],
 "fastqAndFasta": ["--inFile", FQ, "--outFile", "out/p2_fqfa.fa", "--mode", "fq2fa"],
 "fastqParallelSubBest": ["--inFastq", FQ, "--outFastq", "out/p2_subbest.fq", "--numReads", "100"],
 "fastqParallelTrimmer": ["--inFastq", FQ, "--outFastq", "out/p2_ptrim.fq", "--bases5", "3"],
 "FoldStructureStater": ["--inFile", "out/p2_rnafold.txt", "--outTable", "out/p2_foldstat.tsv"],
 "RNAplotAdvance": ["--inFile", "out/p2_rnafold.txt", "--outFile", "out/p2_rnaplot.pdf"],
 "plotRNAfoldloci": ["--inFile", "out/p2_rnafold.txt", "--outFile", "out/p2_rnaloci.pdf"],
 "GenerateMotifFromSequences": ["--inFasta", MSA, "--outFile", "out/p2_genmotif.xml"],
 "checkPrimer": ["--inFasta", NACL, "--primerFile", "out/p2_primer.tsv", "--outFile", "out/p2_primerchk.tsv"],
 "parallelMD5Check": ["--inFile", PEP, "--outFile", "out/p2_md5.txt"],
 "simpleBatchProcess": ["--inFile", "out/p2_batch.cfg", "--outDir", "out/p2_batch"],
 "slurmScriptPrepare": ["--inConfig", "out/p2_batch.cfg", "--outScript", "out/p2_slurm.sh"],
 "ReciprocalBlast": ["--querySeqFile", PEP10, "--subjectSeqFile", CHPEP, "--outDirAndPrefix", "out/p2_recip"],
 "quickGeneFamilyIdentification": ["--QueryPepSet", PEP10, "--ReferencePepSet", PEP, "--ReferenceFamilyId", "out/pin10_ids.txt", "--OutFilePrefix", "out/p2_qf", "--NumOfThreads", "4"],
 "PairWiseKaKsCalculator": ["--inCdsFasta", CDS, "--inProteinAln", MSA, "--outFile", "out/p2_kaks.tsv"],
 "dnDsCalculate": ["--inCdsAln", CDS, "--inProteinAln", MSA, "--outFile", "out/p2_dnds.tsv"],
 "collinearityToRegion": ["--inCollinearity", "out/fake_collinearity.tsv", "--inSimplifiedGff", "out/chloro_simpl_mc.gff", "--outFile", "out/p2_collinreg.txt"],
 "eggNogMapperResult": ["--inFile", "out/p2_eggnog.tsv", "--outTable", "out/p2_eggnog_out.tsv"],
 "FastaLongestRepresentater2": None,
}

# 合成 VCF / GBFF / 其他占位
io.open("out/p2_fake.vcf", "w", newline="\n").write(
 "##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\nmonarda_chloro\t1000\t.\tA\tG\t50\tPASS\tQD=20;MQ=60\nmonarda_chloro\t2000\t.\tC\tT\t30\tPASS\tQD=8;MQ=40\n")
io.open("out/p2_fake.gbff", "w", newline="\n").write(
 "LOCUS       monarda_chloro         151812 bp    DNA     PLN\nFEATURES             Location/Qualifiers\n     source          1..151812\nORIGIN      \n//\n")
io.open("out/p2_m10.txt", "w", newline="\n").write(
 "At_PIN1\t100\t50\t0\t0\t0\t0\t0\t0\t0\n")
io.open("out/p2_rnafold.txt", "w", newline="\n").write(
 ">trnH\nGGCCUAAUAGCUCAGUUGGUUAGAGCGCGGGUUUUAUGUAAACCGACCUUCGGUUCGAUUCCCGGGUUUCGCAAUCC\n..(((((..))))..(((((((.......)))))))...((((..))))......(((((.....)))))......). ( -21.50)\n")
io.open("out/p2_primer.tsv", "w", newline="\n").write("F1\tATGGCGAACGACGGGAATTG\tR1\tTTAGGCCTTAACATGCTCGG\n")
io.open("out/p2_batch.cfg", "w", newline="\n").write(
 "cmd1\tjava -version\n")
io.open("out/p2_eggnog.tsv", "w", newline="\n").write(
 "At_PIN1\tGO:0010310\tPF03547\tmembrane transport\n")

names = sorted(reg)
w(f"\n## 一、无参运行（抓引擎 [Usage]，共 {len(names)} 个）\n")
usage_ok, usage_fail = 0, 0
for i, n in enumerate(names, 1):
    w(f"\n### tool {n}（无参）")
    w("```bash\ntbtools tool " + n + "\n```")
    out, err, ec, dt = run([PY, "-m", "tbtools_cli.cli", "tool", n], timeout=15)
    text = (out + err)
    if "[Usage]" in text or "Usage" in text: usage_ok += 1
    else: usage_fail += 1
    w(block(out, err, ec, dt, limit=5000))
    print(f"{i}/{len(names)} {n}")
w(f"\n**无参小结**：{usage_ok} 个返回 [Usage]，{usage_fail} 个直接执行/其他行为。\n")

w("\n## 二、带参实跑（可映射子集）\n")
done = 0
for n, argv in M.items():
    if argv is None or n not in reg:
        continue
    done += 1
    w(f"\n### tool {n}（带参）")
    w("```bash\ntbtools tool " + n + " " + " ".join(argv) + "\n```")
    out, err, ec, dt = run([PY, "-m", "tbtools_cli.cli", "tool", n] + argv, timeout=300)
    w(block(out, err, ec, dt))
    print(f"M {done} {n}")
LOG.close()
print("PHASE2 DONE")

