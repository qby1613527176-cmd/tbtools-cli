#!/usr/bin/env python
"""Phase8: 官方 examples/data 权威输入重跑全部此前失败命令"""
import io
import os
import subprocess
import time

os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
EX = "examples/data"
OUT = r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test\out\p8"
os.makedirs(OUT, exist_ok=True)
LOG = io.open(r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test\P8_LOG.md", "w", encoding="utf-8", newline="\n")

def w(s=""):
    LOG.write(s + "\n"); LOG.flush()

def run(cmd, timeout=300):
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL, shell=True)
    try:
        out, err = p.communicate(timeout=timeout)
        return (out.decode("utf-8", "replace"), err.decode("utf-8", "replace"),
                p.returncode, time.time() - t0)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
        try: out, err = p.communicate(timeout=5)
        except Exception: out, err = b"", b""
        return (out.decode("utf-8", "replace"), err.decode("utf-8", "replace"),
                -99, time.time() - t0)

PYEXE = r"C:\Users\16135\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
CLI = f'"{PYEXE}" -m tbtools_cli.cli'
w("# Phase 8：官方 examples/data 权威输入重跑此前失败命令\n")
w("> 输入全部来自 CLI 自带 examples/data/（201 个文件，官方预期格式）。输出到 tbtools-test/out/p8/。\n")

def T(title, cmdline, tmo=300):
    w(f"\n### {title}")
    w("```bash\n" + cmdline.replace(EX, "examples/data") + "\n```")
    out, err, ec, dt = run(cmdline, timeout=tmo)
    p = []
    if out.strip():
        o = out if len(out) <= 3500 else out[:3500] + "…[截断]"
        p.append("```\n" + o.rstrip() + "\n```")
    if err.strip():
        p.append("**stderr:**\n```\n" + err.rstrip()[:3500] + "\n```")
    if not p: p.append("```\n(无输出)\n```")
    p.append(f"退出码 `{ec}` · {dt:.1f}s")
    w("\n\n".join(p))
    print(("✅" if ec == 0 and "❌" not in out + err else "❌"), title)

# ===== 8.1 expr 组失败命令（官方数据） =====
w("\n## 8.1 expr 组此前失败命令 × 官方数据\n")
T("cubeheatmap（官方 cube_group.tsv）",
  f'{CLI} expr cubeheatmap {EX}/expr/expr.tsv {EX}/expr/cube_group.tsv {OUT}/cubeheat.svg')
T("groupedbar（官方 groupbar.tsv）",
  f'{CLI} expr groupedbar {EX}/expr/groupbar.tsv {OUT}/groupbar.svg')
T("layoutheatmap（官方 layout.tsv）",
  f'{CLI} expr layoutheatmap {EX}/expr/layout.tsv {EX}/expr/expr.tsv {OUT}/layout.svg')
T("qpcr（官方 qpcr.txt）", f'{CLI} expr qpcr {EX}/expr/qpcr.txt {OUT}/qpcr.svg')
T("qpcrExp（官方 qpcr.txt）", f'{CLI} expr qpcrExp {EX}/expr/qpcr.txt {OUT}/qpcrExp.xls')
T("distance（官方 dist.tsv）", f'{CLI} expr distance {EX}/expr/dist.tsv 1 2 pearson')
T("dehist（官方 deg_hist.tsv）", f'{CLI} expr dehist {EX}/expr/deg_hist.tsv {OUT}/dehist.svg')
T("efpHeat（官方 efp 三件套）",
  f'{CLI} expr efpHeat {EX}/efp/plant_bg.tga {EX}/efp/sample2cc.txt {EX}/efp/expmat.tsv AT1G01010 {OUT}/efp.svg')
T("multiEfp（官方 efp 三件套）",
  f'{CLI} expr multiEfp {EX}/efp/plant_bg.tga {EX}/efp/sample2cc.txt {EX}/efp/expmat.tsv AT1G01010 {OUT}/multiefp.svg')

# ===== 8.2 blast 组失败命令（官方 recipblast/quickfamily 全套） =====
w("\n## 8.2 blast/工具层失败命令 × 官方数据\n")
T("ReciprocalBlast 官方全套",
  f'{CLI} tool ReciprocalBlast --querySeqFile {EX}/blast/recipblast/query.short.fa --subjectSeqFile {EX}/blast/recipblast/subject.short.fa --outDirAndPrefix {OUT}/recip_ex')
T("quickGeneFamilyIdentification 官方全套",
  f'{CLI} tool quickGeneFamilyIdentification --QueryPepSet {EX}/blast/quickfamily/query.fa --ReferencePepSet {EX}/blast/quickfamily/ref.fa --ReferenceFamilyId {EX}/blast/quickfamily/family.IDset.txt --OutFilePrefix {OUT}/qf_ex --NumOfThreads 4', tmo=600)
T("getLongestCompleteORF（官方 genome fasta）",
  f'{CLI} tool getLongestCompleteORF --inFasta {EX}/comparative/input.genome.fa --outFasta {OUT}/orfc_ex.pep')
T("extractFeatureFromGTF（官方 gene_structure.gff 转 GTF 场景）",
  f'{CLI} tool extractFeatureFromGTF --inGtf {EX}/gene_structure.gff --inGenome {EX}/comparative/input.genome.fa --outFile {OUT}/gtffeat_ex.fa')
T("gffCdsPhaseCorrector（官方 gene_structure.gff）",
  f'{CLI} tool gffCdsPhaseCorrector --inGff {EX}/gene_structure.gff --outGff {OUT}/phase_ex.gff3')
T("parallelMD5Check（官方 fasta）",
  f'{CLI} tool parallelMD5Check --inFile {EX}/blast/query.fa --outFile {OUT}/md5_ex.txt')

# ===== 8.3 mirna 组全量（官方 mirna 数据） =====
w("\n## 8.3 mirna 组 × 官方数据\n")
T("mirnatarget（官方 miRNA.fa × gras6_pep）",
  f'{CLI} mirna mirnatarget {EX}/mirna/miRNA.fa {EX}/rpc/gras6_pep.fa {OUT}/mirnatarget_ex.tsv --evalue 1')
T("mirnaTarget2（官方）",
  f'{CLI} mirna mirnaTarget2 {EX}/rpc/gras6_pep.fa {EX}/mirna/miRNA.fa {OUT}/mirnatarget2_ex.txt --revCom true')
T("mirnaIdentify（官方 positive_ctrl 全套）",
  f'{CLI} mirna mirnaIdentify {EX}/mirna/mirnaIdentify/positive_ctrl_genome.fa {EX}/mirna/mirnaIdentify/positive_ctrl_target.tsv {OUT}/mirnaid_ex.txt', tmo=600)

# ===== 8.4 syn 组失败命令（官方 synteny 数据） =====
w("\n## 8.4 syn 组 × 官方数据\n")
T("dualsyn（官方 dual.gff + dual.collinearity）",
  f'{CLI} syn dualsyn {EX}/synteny/dual.gff {EX}/synteny/dual.collinearity {OUT}/dualsyn.svg --chr1 1 --chr2 1')
T("multisyn（官方 multi 全套）",
  f'{CLI} syn multisyn {EX}/synteny/multi/gxf.lst {EX}/synteny/multi/collinear.lst {OUT}/multisyn.svg')
T("msy（官方 msy 全套）", f'{CLI} syn msy {EX}/synteny/msy/layout2.txt {EX}/synteny/msy/links2.txt {OUT}/msy.svg')
T("collinearRegion（官方 test.collinearity）",
  f'{CLI} syn collinearRegion {EX}/synteny/test.collinearity {EX}/synteny/dual.gff {OUT}/collinreg_ex.txt')
T("findblockdual（官方 genome 对）",
  f'{CLI} syn findblockdual {EX}/comparative/input.genome.fa {EX}/comparative/input.gff {EX}/comparative/input.genome.fa {EX}/comparative/input.gff sp1 {OUT}/fbdual_ex --threads 4', tmo=600)
T("visualizeblock（官方现成 block 输出）",
  f'{CLI} syn visualizeblock {EX}/findblockdual/block_Cr_Cs_real.out.txt {OUT}/visblock_ex.pdf --labels Cr,Cs')
T("dotplot（官方）",
  f'{CLI} syn dotplot --inGff {EX}/synteny/dual.gff --genePair {EX}/synteny/test.collinearity --chrLayout {EX}/chipseq/chrlen2.txt {OUT}/dotplot_ex.svg')

# ===== 8.5 tree/seq/asm 组 =====
w("\n## 8.5 tree/seq/asm 组 × 官方数据\n")
T("nwAlign（官方 align 三件套）",
  f'{CLI} tree nwAlign {EX}/align/nw.seq1.txt {EX}/align/nw.seq2.txt {OUT}/nw_ex.txt')
T("tree findpath（官方）",
  f'{CLI} tree findpath --inGffArr {EX}/comparative/input.gff --inGenePairs {EX}/synteny/test.collinearity {OUT}/findpath_ex')
T("seq pep2codon（官方 CDS+pep）",
  f'{CLI} seq pep2codon {EX}/comparative/input.genome.fa {EX}/comparative/input.gff {OUT}/pep2codon_ex.fa')
T("asm ctgGroup（官方 miniprot）",
  f'{CLI} asm ctgGroup {EX}/assembly/miniprot.gff {OUT}/ctggrp_ex.txt {OUT}/ctggrp_map.tsv')
T("asm sepChr（官方 gene2chr.tsv + miniprot.gff）",
  f'{CLI} asm sepChr {EX}/assembly/gene2chr.tsv {EX}/assembly/miniprot.gff {OUT}/sepchr_ex.map')
T("asm virusRecomb（官方 virus 全套）",
  f'{CLI} asm virusRecomb {EX}/virus/query.contig.fa {EX}/virus/virus.db.fa {OUT}/virus_ex', tmo=600)
T("chipseq peakdist（官方 peak_std.xls + chrlen2）",
  f'{CLI} chipseq peakdist {EX}/chipseq/peak_std.xls {OUT}/peakdist_ex.svg --chrHeight 100000')
T("chipseq pileup（官方 blast xml）",
  f'{CLI} chipseq pileup {EX}/blast/filtercscore/blast.tab6 {OUT}/pileup_ex.svg --query q1')

# ===== 8.6 GTF 交叉验证 N22 =====
w("\n## 8.6 GFF3/GTF 识别歧义族交叉验证（N22）\n")
head_gff = f'{OUT}/head600.gff3'
run(f'powershell -Command "Get-Content {EX}/gxf/gxfutils/cr_chr01_head600.gff3 | Select-Object -First 200 | Set-Content {head_gff}"')
T("GxfSplit 官方 head600.gff3", f'{CLI} gxf gxfSplit {head_gff} {OUT}/gxfsplit_ex --colIndex 0')
T("GxfIdAppender 官方（prefix 参数补全）",
  f'{CLI} gxf gxfIdAppender {head_gff} {OUT}/idapp_ex.gff3 --prefix MON_')
LOG.close()
print("PHASE8 DONE")

