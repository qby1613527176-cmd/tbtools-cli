import sys
#!/usr/bin/env python
"""Phase1: 159 条分组命令全量测试，逐条原样捕获输出"""
import io, os, re, subprocess, sys, time

os.environ.setdefault("TBTOOLS_JAR", "C:/Program Files/TBtools/TBtools_JRE1.6.jar")
ROOT = os.environ["TBROOT"]
PY = sys.executable
os.chdir(os.path.dirname(os.path.abspath(__file__)))
LOG = io.open("P1_LOG.md", "w", encoding="utf-8", newline="\n")

def w(s=""):
    LOG.write(s + "\n"); LOG.flush()

PEP = "out/pin_family_full.fa"; PEP10 = "out/pin10.fa"
NACL = "data/monarda_chloro.clean.fa"; CDS = "data/monarda_chloro_cds.fa"
CHPEP = "data/monarda_chloro_pep.fa"; GFF = "data/monarda_chloro.gff3"
GFFF = "out/chloro_filtered.gff3"; IDS = "out/chloro_ids.txt"
ATIDS = "out/at_ids.txt"; SIIDS = "out/si_ids.txt"
MSA = "out/pin_msa3.fa"; TREE = "out/pin_tree2/TBtools.IQtree.treefile"
GTREE = "out/pin8_genetree.treefile"; SPECIES = "out/species_tree.nwk"
TAB6 = "out/blast_atpin_si.tab"; EXPR = "out/pin_expr.tsv"; DEG = "out/pin_deg.tsv"
MAT = "out/atpin_sipin_matrix.tsv"; FQ = "out/sim_reads.fq"
OBO = "data/go.obo"; CHRL = "data/chloro_chrlen.tsv"
RNM = "out/si_rename_map.tsv"; XML = "out/t2b5.xml"

def run(cmd, timeout=180):
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        out, err, ec = r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        out, err, ec = "", f"⏱ [harness] 超时（>{timeout}s）终止", -99
    except Exception as e:
        out, err, ec = "", f"[harness] {e}", -98
    return out, err, ec, time.time() - t0

def block(out, err, ec, dt, limit=7000):
    p = []
    if out.strip():
        o = out if len(out) <= limit else out[:limit] + f"\n…[截断, 共{len(out)}字符]"
        p.append("```\n" + o.rstrip() + "\n```")
    if err.strip():
        e = err if len(err) <= limit else err[:limit] + f"\n…[截断, 共{len(err)}字符]"
        p.append("**stderr:**\n```\n" + e.rstrip() + "\n```")
    if not p:
        p.append("```\n(无输出)\n```")
    p.append(f"退出码 `{ec}` · {dt:.1f}s")
    return "\n\n".join(p)

def T(group, cmd, argv, note=None, tmo=180):
    label = f"tbtools {group} {cmd}" if group != "-" else f"tbtools {cmd}"
    w(f"\n### {label}")
    if note: w(note)
    base = [PY, "-m", "tbtools_cli.cli"] + ([group] if group != "-" else []) + [cmd]
    w("**实际命令:**\n```bash\n" + " ".join(base + argv) + "\n```")
    out, err, ec, dt = run(base + argv, timeout=tmo)
    w(block(out, err, ec, dt))

# ---------- 预置输入 ----------
simpl = []
for l in io.open(GFF):
    if "\tmRNA\t" in l:
        f = l.split("\t")
        gid = re.search(r"ID=([^;]+)", f[8]).group(1)
        simpl.append((gid, f[0], f[3], f[4]))
io.open("out/chloro_simpl.tsv", "w", newline="\n").write(
    "\n".join(f"{g}\t{c}\t{s}\t{e}" for g, c, s, e in simpl) + "\n")
# 简化 gff（数字染色体名格式，chr gene start end -> 供 mcscanx 系）
with io.open("out/chloro_simpl_mc.gff", "w", newline="\n") as f:
    for i, (g, c, s, e) in enumerate(simpl):
        f.write(f"1\t{g}\t{s}\t{e}\n")
with io.open("out/fake_peak.xls", "w", newline="\n") as f:
    f.write("chr\tstart\tend\tlength\tsummit\tpileup\tpvalue\tfold\tFDR\n")
    for st, en in [(2000, 5200), (20000, 24500), (60000, 64000)]:
        f.write(f"monarda_chloro\t{st}\t{en}\t{en-st}\t{(st+en)//2}\t100\t1e-20\t30\t0.01\n")
io.open("out/region.txt", "w", newline="\n").write("monarda_chloro\t1\t40000\nmonarda_chloro\t40001\t151812\n")
pairs = [f"{simpl[i][0]}\t{simpl[i+5][0]}\t0.95\t0" for i in range(min(5, len(simpl)-5))]
io.open("out/fake_collinearity.tsv", "w", newline="\n").write("\n".join(pairs) + "\n")
pin10 = [l.split()[0][1:] for l in io.open(PEP10) if l.startswith(">")]
gos = ["GO:0010310\tauxin efflux transmembrane transporter activity",
       "GO:0006833\tauxin transport", "GO:0005886\tplasma membrane"]
with io.open("out/gene2go.tsv", "w", newline="\n") as f:
    for i, g in enumerate(pin10): f.write(f"{g}\t{gos[i % 3]}\n")
io.open("out/pin10_ids.txt", "w", newline="\n").write("\n".join(pin10) + "\n")
io.open("out/hclust_dist.tsv", "w", newline="\n").write("G1\tG2\t0.5\nG1\tG3\t0.8\nG2\tG3\t0.3\n")
io.open("out/coords.bed", "w", newline="\n").write("monarda_chloro\t100\t500\n")
io.open("out/qpcr.tab", "w", newline="\n").write(
    "Gene\tSample\tCt\nAt_PIN1\tControl\t20.1\nAt_PIN1\tTreat\t18.3\nAt_PIN2\tControl\t22.0\nAt_PIN2\tTreat\t21.5\n")
io.open("out/marker.tab", "w", newline="\n").write("SNP1\tA\tG\t0.2\nSNP2\tC\tT\t0.5\n")
io.open("out/gene2chr.tsv", "w", newline="\n").write("matK\tmonarda_chloro\nrps16\tmonarda_chloro\n")
with io.open("out/layout.txt", "w", newline="\n") as f:
    f.write("Layout: Grid 6 1\nRow: " + " ".join(pin10[:6]) + "\n")
with io.open("out/group.tsv", "w", newline="\n") as f:
    f.write("\n".join(f"{g}\tGroup{i%2+1}" for i, g in enumerate(pin10)) + "\n")
with io.open("out/circle_group.txt", "w", newline="\n") as f:
    f.write("\n".join(pin10[:3]) + "\n")
# l1 venn id files
io.open("out/ids3.txt", "w", newline="\n").write("\n".join(pin10[:5]) + "\n")
io.open("out/rna.fa", "w", newline="\n").write(
    ">trnH\nGGCCTAATAGCTCAGTTGGTAGAGCGCGGGTTTTATGTAAACCGACCTTCGGTTCGATTCCCGGGTTTCGCAATCC\n")

w("# tbtools-cli 全量测试详录 Phase 1：分组命令（159 条）\n")
w("> 每条命令记录：实际执行的完整命令行 + 原样 stdout/stderr + 退出码 + 耗时。\n"
  "> 参数签名以各命令 `--help` 与引擎 `[Usage]` 真实输出为准；\"参数不接受\"类输出本身即为有价值的测试反馈。\n")

CMDS = {}  # (g,c) -> (argv, note, timeout)
def add(g, c, argv, note=None, tmo=180): CMDS[(g, c)] = (argv, note, tmo)

# ---- asm ----
add("asm","bamMerge",["--gtf",GFF,"--bamDir","out","--outDir","out/bammerge"],note="*无真实 BAM 输入，预期引擎报错——记录真实报错*")
add("asm","bamindex",["out/fake.bam","out/fake.bai"],note="*无真实 BAM*")
add("asm","bamsort",["out/fake.bam","out/fake.sorted.bam"],note="*无真实 BAM*")
add("asm","bamstate",["out/bamstate.tsv",GFF,"out/fake.bam"],note="*无真实 BAM*")
add("asm","ctgGroup",["out/fake.miniprot.gff","out/fake.polypoid","out/ctggrp.tsv"],note="*无 miniprot GFF*")
add("asm","hicEnzyme",[FQ],note="*用合成 FASTQ 实跑*")
add("asm","homoPhase",["out/fake.ctggrp.tsv","out/phased.tsv"],note="*无 contigGrpMap*")
add("asm","preparespecies",["monarda",NACL,GFF,"out/prepared_genome.fa"])
add("asm","sepChr",["out/gene2chr.tsv","out/fake.miniprot.gff","out/sepchr.map"],note="*无 miniprot GFF*")
add("asm","virusRecomb",[CDS,CHPEP,"out/virusrecomb"])
# ---- blast ----
add("blast","filterCScore",[TAB6,"out/filtered_cscore.tab","--cscore","0.5"])
add("blast","quickAnno",[PEP10,"data/si_proteome.fa","out/qa_p1.txt","4"])
add("blast","quickFamily",["--QueryPepSet",PEP10,"--ReferencePepSet",PEP,"--ReferenceFamilyId","out/pin10_ids.txt","--OutFilePrefix","out/qf_p1","--NumOfThreads","4"],tmo=300)
add("blast","recipBlast",["--querySeqFile",PEP10,"--subjectSeqFile",CHPEP,"--outDirAndPrefix","out/recip_p1"],tmo=300)
add("blast","twoSeqBlast",["--query",PEP10,"--subject",CHPEP,"--outBlastResult","out/t2b_p1.tab","--outFmt","6","--thread","4"],tmo=300)
# ---- chipseq ----
add("chipseq","peakanno",[GFF,"out/fake_peak.xls","out/peakanno_p1.tsv"])
add("chipseq","peakdist",["out/fake_peak.xls","out/peakdist_p1.svg","--chrHeight","151812"])
add("chipseq","peaktss",[GFF,"out/fake_peak.xls","out/peaktss_p1.svg"])
add("chipseq","pileup",[XML,"out/pileup_p1.svg","--query",pin10[0]])
# ---- engine ----
add("engine","admixture",["out/admix.lst","out/admix_p1.svg"],note="*无真实 ADMIXTURE Q 矩阵*")
add("engine","calcRepeat",[NACL,"out/repeat_p1.txt","--kmerSize","5"],tmo=600)
add("engine","filesplit",[PEP10,"3"])
add("engine","generic",["biocjava.bioIO.FastX.FastaIndex.QuickStatFasta","stat","out/generic_p1.txt","--set","inFile",PEP10],note="*预期触发包装层把类名当文件校验的 bug——如实记录*")
add("engine","gsadiag",[GFF,"out/gsadiag_p1.xls",NACL])
add("engine","gxffilter",[GFF,IDS,GFFF])
add("engine","gxfsort",[GFF,"out/chloro_sorted_p1.gff3"])
add("engine","marker",["MarkerRandomDesign","out/marker.tab","out/marker_p1.out"])
add("engine","markertools",["filter","out/marker.tab"])
add("engine","mggxf",[TAB6,"out/chloro_simpl_mc.gff","out/mggxf_p1.gff"])
add("engine","qpcrproc",["out/qpcr.tab","out/qpcr_p1.xls"])
add("engine","regiondepth",["out/fake.sam","monarda_chloro:1-1000","out/depth_p1.txt"],note="*无真实 SAM*")
add("engine","sambamcov",["out/fake.bam","out/sambamcov.tsv"],note="*无真实 BAM*")
add("engine","seqconvert",["-i",PEP10,"-o","out/seqconv.txt","-iF","fasta","-oF","table"])
add("engine","trimmsa",[MSA,"out/trimmed_msa.fa","0.5"])
# ---- expr ----
add("expr","barplot",[MAT,"out/barplot_p1.svg","A0A6I9SK11","0.05"])
add("expr","barplotter",["-g",GFF,"-s","out/fake_collinearity.tsv","-c","out/fake_ctl.txt","-o","out/barplotter_p1.png"],note="*无完整配置文件*")
add("expr","colorscheme",[MAT,"out/colorscheme.tsv","2"])
add("expr","cubeheatmap",[EXPR,"out/group.tsv","out/cubeheat_p1.svg"],note="*坑位文档：group 文件第一行会被当数据*")
add("expr","dehist",[DEG,"out/dehist_p1.svg"])
add("expr","distance",[EXPR,"Root","Leaf","pearson"])
add("expr","efpHeat",["out/fake.tga","out/sample2cc.txt","out/efp_exp.tsv","matK","out/efp_p1.svg"],note="*无 TGA 底图（eFP 专用格式）*")
add("expr","exprCorr",[EXPR,"out/expcorr_p1.tsv"])
add("expr","groupCol",[EXPR,"out/group.tsv","out/groupcol_p1.tsv"])
add("expr","groupedbar",[EXPR,"out/groupedbar_p1.svg","BOXPLOT"])
add("expr","hclust",["out/hclust_dist.tsv","out/hclust_p1.nwk"])
add("expr","heatmap",[EXPR,"out/heatmap_p1.svg"])
add("expr","kallisto",[CDS,FQ,"out/kallisto_p1.tsv","--kmer","31"],note="*预期触发 WinError 193（Linux 二进制）bug*")
add("expr","layoutheatmap",["out/layout.txt",EXPR,"out/layout_p1.svg"])
add("expr","mountain",[EXPR,"out/mountain_p1.svg"],note="*README：TBtools jar 内空实现*")
add("expr","multiEfp",["out/fake.tga","out/sample2cc.txt","out/efp_exp.tsv","matK","out/multiefp_p1.svg"],note="*无 TGA 底图*")
add("expr","pca",[EXPR,"out/pca_p1.svg","row"])
add("expr","qpcr",["out/qpcr.tab","out/qpcr_p1.svg"])
add("expr","qpcrExp",["out/qpcr.tab","out/qpcrExp_p1.xls"])
add("expr","tauIndex",[EXPR,"out/tau_p1.tsv"])
add("expr","violin",[EXPR,"out/violin_p1.svg"])
add("expr","volcano",[DEG,"out/volcano_p1.svg"])
# ---- fastq ----
add("fastq","fastaExtract",["--inFa",CHPEP,"--inIDList",IDS,"--outFa","out/fastaext_p1.fa"])
add("fastq","fastaSubseq",[NACL,"out/coords.bed","out/subseq_p1.fa"])
add("fastq","fqTrim",[FQ,"out/trim_p1.fq","--b5","5","--b3","5"])
add("fastq","fqfaConv",[FQ,"out/simreads_p1.fa","fq2fa"])
# ---- gxf ----
add("gxf","annocompare",[GFF,GFFF,"out/annocompare_p1","test"])
add("gxf","genedensity",[GFF,"out/genedensity_p1.tsv","10000"])
add("gxf","genelocation",["--ChrLen",CHRL,"--FeaturePos","out/rpc_genepos.tsv","--OutGraph","out/geneloc_p1.svg"])
add("gxf","genelocgff",[GFF,IDS,"out/genelocgff_p1.svg","--chrLen",CHRL])
add("gxf","gxfAppend",[GFFF,GFF,"out/gxfappend_p1.gff3"])
add("gxf","gxfAttr",[GFF,"out/gxfattr_p1.tsv","--feature","mRNA","--attrs","ID,product"])
add("gxf","gxfFix",[GFF,"out/gxffix_p1.gff3"])
add("gxf","gxfGenepos",[GFF,"out/gxfgenepos_p1.tsv","out/gxfchrlen_p1.tsv"])
add("gxf","gxfMatch",[GFF,NACL])
add("gxf","gxfOverlap",[GFF,"out/region.txt","out/gxfoverlap_p1.gff3"])
add("gxf","gxfRecall",[GFFF,"out/gxfrecall_p1.gff3"])
add("gxf","gxfRegion",[GFF,"out/region.txt","out/gxfregion_p1.gff3"])
add("gxf","gxfRename",[GFFF,"out/gxfrename_p1.gff3",RNM],note="*renameMap 键为 SiPINxx（树 ID），与 GFF 不匹配属预期*")
add("gxf","gxfRepGXF",[GFF,"out/gxfrepgxf_p1.gff3"])
add("gxf","gxfRepIDs",[GFF,"out/gxfrepids_p1.txt"])
add("gxf","gxfStat",[GFF,"out/gxfstat_p1.xls"])
add("gxf","regionAnno",[GFF,"out/region.txt","out/regionanno_p1.tsv"])
# ---- hmm ----
add("hmm","hmmExtract",["out/fake.pfam.hmm","out/pin10_ids.txt","out/hmmext_p1.hmm"],note="*本机无 Pfam-A.hmm，用占位文件记录真实报错*")
add("hmm","hmmerSearch",[CHPEP,"out/fake.pfam.hmm","out/hmmsearch_p1.tsv"],note="*同上*")
add("hmm","hmmsearch",["out/fake.pfam.hmm",CHPEP,IDS,"out/hmmsearch2_p1.txt"],note="*同上*")
# ---- mirna ----
add("mirna","mirnaIdentify",[NACL,"out/targetso.tsv","out/mirnaid_p1.txt"])
add("mirna","mirnaTarget2",[CHPEP,PEP10,"out/mirnatarget2_p1.txt","--revCom","true"])
add("mirna","mirnatarget",[CHPEP,PEP10,"out/mirnatarget_p1.tsv","--evalue","1"])
# ---- seq ----
add("seq","amazingmeta",["out/meme_pin/meme.xml",TREE,"out/amazingmeta_p1.svg"],note="*依赖 MEME XML（本机受限）*")
add("seq","cddmotif",["out/cdd_hitdata.txt",CHPEP,"out/cddmotif_p1.svg"],note="*无 CDD 数据*")
add("seq","fimo",["--oc","out/fimo_p1","out/tfbsshift_pin.motifs","out/promoters.fa"],note="*fimo 二进制缺失（已记录）*")
add("seq","gel",["out/gel_cfg.txt","out/gel_p1.svg"])
add("seq","gfa",["out/fake.gfa","out/gfa_p1.svg"],note="*无 GFA 图数据*")
add("seq","gfa2fa",["out/fake.gfa","out/gfa2fa_p1.fa"],note="*无 GFA*")
add("seq","logo",[MSA,"out/logo_p1.svg"])
add("seq","mast2tab",["out/mast_out/mast.xml","out/mast2tab_p1.tsv"],note="*无 MAST 输出*")
add("seq","mastExtract",["out/mast_out/mast.xml",IDS,"out/mastext_p1.xml"],note="*无 MAST 输出*")
add("seq","mastrun",["out/meme_pin/meme.xml",CHPEP,"out/mast_p1"],note="*依赖 MEME XML*")
add("seq","memeViz",["out/meme_pin/meme.xml","out/memeviz_p1.svg"],note="*依赖 MEME XML（本机受限）*")
add("seq","memerun",[PEP,"out/meme_p1"],note="*meme.exe 缺 etc 资源（已记录）；实测留档*")
add("seq","motif",["out/meme_pin/meme.xml",IDS,"out/motif_p1.svg"],note="*依赖 MEME XML*")
add("seq","msa",[MSA,"out/msa_p1.svg"])
add("seq","pep2codon",[CDS,MSA,"out/pep2codon_p1.fa"])
add("seq","pfammotif",["out/pin10_ids.txt","out/pfammotif_p1.svg"],note="*需 Pfam 库*")
add("seq","plotrna",["out/rna.fa","out/plotrna_p1.pdf","--directPDF"])
add("seq","rnaplot",["out/rna.fa","out/rnaplot_p1.pdf"])
add("seq","seqlentrack",[GFF,"out/seqlentrack_p1.svg"])
add("seq","simplehmmscan",[CHPEP,IDS,"out/hmmscan_p1.txt"],note="*需 Pfam-A.hmm*")
add("seq","smart",[PEP10,"out/smart_p1.txt"],note="*联网 EMBL，约 3-4 分钟*",tmo=600)
add("seq","structure",[GFF,IDS,"out/structure_p1.svg"])
add("seq","tfbsShift",[PEP10,"out/tfbs_p1","4"],tmo=600)
# ---- sets ----
add("sets","upset",["out/upset_sets.txt","out/upset_p1.svg"])
add("sets","venn2",["--List1",ATIDS,"--List2",SIIDS,"--label1","AtPIN","--label2","SiPIN","--graph","out/venn2_p1.svg","--prefix","out/venn2_p1"])
add("sets","venn3",["--List1",ATIDS,"--List2",SIIDS,"--List3","out/ids3.txt","--label1","A","--label2","B","--label3","C","--graph","out/venn3_p1.svg","--prefix","out/venn3_p1"])
add("sets","venn4",["--List1",ATIDS,"--List2",SIIDS,"--List3","out/ids3.txt","--List4","out/ids3.txt","--label1","A","--label2","B","--label3","C","--label4","D","--graph","out/venn4_p1.svg","--prefix","out/venn4_p1"])
add("sets","venn5",["out/venn5_p1.svg",ATIDS,SIIDS,"out/ids3.txt","out/ids3.txt","out/ids3.txt","A,B,C,D,E"])
add("sets","venn6",["out/venn6_p1.svg",ATIDS,SIIDS,"out/ids3.txt","out/ids3.txt","out/ids3.txt","out/ids3.txt","A,B,C,D,E,F"])
# ---- syn ----
add("syn","circlegene",[GFF,IDS,"out/circlegene_p1.svg"])
add("syn","circos",[CHRL,"out/circos_link.txt","out/rpc_genepos.tsv","out/circos_p1.svg"])
add("syn","collinearRegion",["out/fake_collinearity.tsv","out/chloro_simpl_mc.gff","out/collinreg_p1.txt"])
add("syn","conflictpaf",["out/fake.paf","out/conflictpaf_p1.tsv"],note="*无 PAF 数据*")
add("syn","dotplot",["--inGff",GFF,"--genePair","out/fake_collinearity.tsv","--chrLayout","out/chloro_chrlen.tsv","out/dotplot_p1.svg"])
add("syn","dualsyn",["out/chloro_simpl_mc.gff","out/fake_collinearity.tsv","out/dualsyn_p1.svg","--chr1","1","--chr2","1"])
add("syn","findblockdual",[NACL,GFF,NACL,GFF,"monarda_chloro","out/fbdual_p1.txt","--threads","4"],note="*README 已知限制：合成小数据触发 OOB——实测留档*",tmo=600)
add("syn","findblockmultiple",[NACL,GFF,"monarda_chloro","out/fbmulti_p1.txt",NACL,GFF],note="*同上*",tmo=600)
add("syn","mcscanx",["out/mcscanx_wd"],note="*需两基因组 MCScanX 工作目录*")
add("syn","mcscanxd",["out/mcscanxd_wd",NACL,NACL,GFF,GFF,"4"],note="*同上；diamond 实测会因小数据失败——留档*",tmo=600)
add("syn","microgenome",[GFF,CHRL,"out/microgenome_p1"])
add("syn","microsyn",["out/chloro_simpl_mc.gff","out/fake_collinearity.tsv","out/microsyn_p1.svg","--chr1","1","--start1","1","--end1","100000","--chr2","1","--start2","1","--end2","100000"])
add("syn","msy",["out/chloro_simpl_mc.gff",IDS,"out/msy_p1.svg"])
add("syn","multisyn",["out/chloro_simpl_mc.gff","out/fake_collinearity.tsv","out/multisyn_p1.svg"])
add("syn","pafcomp",["out/fake1.paf","out/fake2.paf","out/pafcomp_p1.svg"],note="*无 PAF*")
add("syn","pafref",["out/fake.paf","out/fake.paf","out/pafref_p1.svg"],note="*无 PAF*")
add("syn","pafviz",["out/fake.paf","out/pafviz_p1.svg"],note="*无 PAF*")
add("syn","partitionconflict",["out/fake.paf","out/partconf_p1.tsv"],note="*无 PAF*")
add("syn","qdot",[TAB6,GFF,"out/chloro_chrlen.tsv","out/qdot_p1.svg"])
add("syn","supercircos",["out/supercircos_cfg.txt","out/supercircos_p1.svg"])
add("syn","visualizeblock",["out/fbdual_p1.txt","out/visblock_p1.pdf","--labels","G1,G2"],note="*依赖 findblockdual 产物*")
# ---- table ----
add("table","batchReplace",[EXPR,"out/batchrep_p1.tsv","out/pattern_map.tsv"])
add("table","goEnrich",[OBO,"out/gene2go.tsv","out/pin10_ids.txt","out/goenrich_p1"])
add("table","goParse",["out/gene2go.tsv",OBO])
add("table","gsea",[OBO,"out/gene2go.tsv","out/pin10_rank.rnk","out/gsea_p1"],note="*预期 JDK26 模块冲突（已记录）*")
add("table","keggEnrich",["out/kegg_reference.keg","out/gene2go.tsv","out/pin10_ids.txt","out/kegg_p1"],note="*无 KEGG 参考库*")
add("table","levelGo",["out/gene2go.tsv","out/levelgo_p1.tsv",OBO,"--level","2"])
add("table","tableAppend",[EXPR,MAT,"out/tableappend_p1.tsv"])
add("table","tableCast",["out/long_table.tsv","out/tablecast_p1.tsv"])
add("table","tableColSel",[EXPR,"out/tablecolsel_p1.tsv","out/pin10_ids.txt"])
add("table","tableColSelect",[EXPR,"out/tablecolsel2_p1.tsv","Root","Leaf"])
add("table","tableCollapse",[EXPR,"0","out/tablecollapse_p1.tsv"])
add("table","tableMelt",[EXPR,"out/tablemelt_p1.tsv"])
add("table","tableMerge",["out/tablemerge_p1.tsv",EXPR,MAT,"--keyCols","0,0"])
add("table","tableSplit",[EXPR,"out/tablesplit_p1","--colIndex","0"])
add("table","tableTranspose",[EXPR,"out/tabletranspose_p1.tsv"])
add("table","tableUniq",[EXPR,"out/tableuniq_p1.txt","--colIndex","0"])
# ---- tree ----
add("tree","degramdom",["out/degramdom_in.tsv","out/degramdom_p1.nwk"])
add("tree","draw",["out/treetab_cfg.txt","out/draw_p1.svg"],note="*TreeTab 配置格式（坑位文档）*")
add("tree","findpath",["--inGffArr",GFF,"--inGenePairs","out/fake_collinearity.tsv","out/findpath_p1"])
add("tree","newickRename",["--inNwk",GTREE,"--renameMap","out/si_rename_map.tsv","--outNwk","out/newickrename_p1.nwk"])
add("tree","notung",[GTREE,"-s",SPECIES,"--reconcile"],note="*预期 JDK26 JApplet 缺失（已记录）*")
add("tree","nwAlign",["out/seq1.txt","out/seq2.txt","out/nwalign_p1.txt"])
add("tree","one-step",[PEP10,"out/onestep_p1","-b","100","-t","4"],note="*10 条序列快速复跑*",tmo=600)
add("tree","phylotree",[TREE,"out/phylotree_p1.svg"])
add("tree","rooting",[TREE,"out/rooting_p1.svg"])
add("tree","unrooted",[TREE,"out/unrooted_p1.svg"],note="*README：硬编码演示 main——实测留档*")

lines = [l.strip() for l in io.open("all_commands.tsv") if l.strip() and not l.startswith("-\t")]
w(f"\n共 {len(lines)} 条分组命令。")
N = len(lines)
for i, line in enumerate(lines, 1):
    g, c = line.split("\t")
    w(f"\n---\n\n## [{i}/{N}] {g} · {c}")
    if (g, c) in CMDS:
        argv, note, tmo = CMDS[(g, c)]
        T(g, c, argv, note=note, tmo=tmo)
    else:
        w("*（映射遗漏——仅记录到 TODO）*")
        print("MISSING", g, c)
LOG.close()
print("PHASE1 DONE")

