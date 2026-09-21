import sys
#!/usr/bin/env python
"""全量命令测试台架：逐条运行 tbtools 命令，原样捕获 stdout/stderr 到 DETAILED_LOG.md"""
import io, os, re, subprocess, sys, time

os.environ.setdefault("TBTOOLS_JAR", "C:/Program Files/TBtools/TBtools_JRE1.6.jar")
ROOT = os.environ["TBROOT"]
PY = sys.executable
D = os.path.dirname(os.path.abspath(__file__))
os.chdir(D)
LOG = io.open("DETAILED_LOG.md", "w", encoding="utf-8", newline="\n")

def w(s=""):
    LOG.write(s + "\n")
    LOG.flush()

PEP = "out/pin_family_full.fa"
PEP10 = "out/pin10.fa"
NACL = "data/monarda_chloro.clean.fa"
CDS = "data/monarda_chloro_cds.fa"
CHPEP = "data/monarda_chloro_pep.fa"
GFF = "data/monarda_chloro.gff3"
GFFF = "out/chloro_filtered.gff3"
IDS = "out/chloro_ids.txt"
ATIDS = "out/at_ids.txt"
SIIDS = "out/si_ids.txt"
MSA = "out/pin_msa3.fa"
TREE = "out/pin_tree2/TBtools.IQtree.treefile"
GTREE = "out/pin8_genetree.treefile"
SPECIES = "out/species_tree.nwk"
TAB6 = "out/blast_atpin_si.tab"
EXPR = "out/pin_expr.tsv"
DEG = "out/pin_deg.tsv"
MAT = "out/atpin_sipin_matrix.tsv"
FQ = "out/sim_reads.fq"
OBO = "data/go.obo"
CHRL = "data/chloro_chrlen.tsv"
RNM = "out/si_rename_map.tsv"

def run(cmd, timeout=150):
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace", shell=False)
        out, err, ec = r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        out, err, ec = "", "⏱ [harness] 超时被终止（> %ds）" % timeout, -99
    except Exception as e:
        out, err, ec = "", f"[harness] 启动失败: {e}", -98
    dt = time.time() - t0
    return out, err, ec, dt

def fmt_block(out, err, ec, dt, limit=6000):
    parts = []
    if out.strip():
        o = out if len(out) <= limit else out[:limit] + f"\n…[截断，共 {len(out)} 字符]"
        parts.append("```\n" + o.rstrip() + "\n```")
    if err.strip():
        e = err if len(err) <= limit else err[:limit] + f"\n…[截断，共 {len(err)} 字符]"
        parts.append("**stderr:**\n```\n" + e.rstrip() + "\n```")
    if not parts:
        parts.append("```\n(无输出)\n```")
    parts.append(f"退出码: `{ec}` · 耗时: {dt:.1f}s")
    return "\n\n".join(parts)

def test(group, cmd, argv=None, note=None, skip=None, timeout=150):
    label = f"tbtools {group} {cmd}" if group != "-" else f"tbtools {cmd}"
    w(f"\n### `{label}`")
    if note:
        w(note)
    if skip:
        w(f"**未执行**：{skip}")
        return
    # Phase A: --help
    base = [PY, "-m", "tbtools_cli.cli"] + ([group] if group != "-" else []) + [cmd]
    out, err, ec, dt = run(base + ["--help"])
    w("**`--help` 真实输出:**")
    w(fmt_block(out, err, ec, dt))
    if argv is None:
        w("**执行:** 未提供适配参数（按数据可用性跳过实际执行）")
        return
    # Phase B: 实际执行
    w("**实际执行:**")
    w("```bash\n" + " ".join(base + argv) + "\n```")
    out, err, ec, dt = run(base + argv, timeout=timeout)
    w(fmt_block(out, err, ec, dt, limit=8000))

# ---------------- 预置合成输入 ----------------
os.makedirs("out", exist_ok=True)
# 简化 GFF（共线性类用）：chr gene start end
simpl = []
seen = set()
for l in io.open(GFF):
    if "\tmRNA\t" in l:
        f = l.split("\t")
        gid = re.search(r"ID=([^;]+)", f[8]).group(1)
        simpl.append(f"{gid}\t{f[0]}\t{f[3]}\t{f[4]}")
io.open("out/chloro_simpl.tsv", "w", newline="\n").write("\n".join(simpl) + "\n")
# MACS2 风格 peak xls
with io.open("out/fake_peak.xls", "w", newline="\n") as f:
    f.write("chr\tstart\tend\tlength\tsummit\tpileup\tpvalue\tfold\tFDR\n")
    for i, (st, en) in enumerate([(2000, 5200), (20000, 24500), (60000, 64000)]):
        f.write(f"monarda_chloro\t{st}\t{en}\t{en-st}\t{(st+en)//2}\t100\t1e-20\t30\t0.01\n")
# region 文件
io.open("out/region.txt", "w", newline="\n").write(
    "monarda_chloro\t1\t40000\nmonarda_chloro\t40001\t151812\n")
# collinearity 文件（简化 gff 基因对）
pairs = ["monarda_chloro\tmonarda_chloro\t1\t5"]
if len(simpl) >= 10:
    pairs = [f"{simpl[i][0]}\t{simpl[i+5][0]}\t0.95\t0" for i in range(5)]
io.open("out/fake_collinearity.tsv", "w", newline="\n").write("\n".join(pairs) + "\n")
# gene2go
recs = [l.split()[0] for l in io.open(PEP10) if l.startswith(">")]
gos = ["GO:0010310\tauxin efflux transmembrane transporter activity",
       "GO:0006833\tauxin transport", "GO:0005886\tplasma membrane"]
with io.open("out/gene2go.tsv", "w", newline="\n") as f:
    for i, g in enumerate(recs):
        f.write(f"{g}\t{gos[i % 3]}\n")
# id list from pin10
io.open("out/pin10_ids.txt", "w", newline="\n").write("\n".join(recs) + "\n")
# distance matrix hclust 用
with io.open("out/hclust_dist.tsv", "w", newline="\n") as f:
    f.write("G1\tG2\t0.5\nG1\tG3\t0.8\nG2\tG3\t0.3\n")
# BED 坐标
io.open("out/coords.bed", "w", newline="\n").write("monarda_chloro\t100\t500\n")
# 演示 qpcr
io.open("out/qpcr.tab", "w", newline="\n").write(
    "Gene\tSample\tCt\nAt_PIN1\tControl\t20.1\nAt_PIN1\tTreat\t18.3\nAt_PIN2\tControl\t22.0\nAt_PIN2\tTreat\t21.5\n")
# 演示 marker 表
io.open("out/marker.tab", "w", newline="\n").write(
    "SNP1\tA\tG\t0.2\nSNP2\tC\tT\t0.5\n")

# ---------------- 命令映射表 ----------------
M = {
 ("asm","bamMerge"): (["--gtf", GFF, "--bamDir", "out", "--outDir", "out/bammerge"], None),
 ("asm","bamindex"): (["out/fake.bam", "out/fake.bai"], None),
 ("asm","bamsort"): (["out/fake.bam", "out/fake.sorted.bam"], None),
 ("asm","bamstate"): (["out/bamstate.tsv", GFF, "out/fake.bam"], None),
 ("asm","ctgGroup"): (["out/fake.miniprot.gff", "out/fake.polypoid", "out/ctggrp.tsv"], None),
 ("asm","hicEnzyme"): ([FQ], None),
 ("asm","homoPhase"): (["out/fake.ctggrp.tsv", "out/phased.tsv"], None),
 ("asm","preparespecies"): (["monarda", NACL, GFF, "out/prepared_genome.fa"], None),
 ("asm","sepChr"): (["out/gene2chr.tsv", "out/fake.miniprot.gff", "out/sepchr.map"], None),
 ("asm","virusRecomb"): ([CDS, CHPEP, "out/virusrecomb"], None),
 ("blast","filterCScore"): ([TAB6, "out/filtered_cscore.tab", "--cscore", "0.5"], None),
 ("blast","quickAnno"): ([PEP10, "data/si_proteome.fa", "out/qa_test.txt", "4"], None),
 ("blast","quickFamily"): (["--QueryPepSet", PEP10, "--ReferencePepSet", PEP, "--ReferenceFamilyId", "out/pin10_ids.txt", "--OutFilePrefix", "out/qf2", "--NumOfThreads", "4"], None),
 ("blast","recipBlast"): ([PEP10, CHPEP, "out/recip", "--queryIds", "out/pin10_ids.txt"], None),
 ("blast","twoSeqBlast"): (["--query", PEP10, "--subject", CHPEP, "--outBlastResult", "out/t2b.tab", "--outFmt", "6", "--thread", "4"], None),
 ("chipseq","peakanno"): ([GFF, "out/fake_peak.xls", "out/peakanno.tsv"], None),
 ("chipseq","peakdist"): (["out/fake_peak.xls", "out/peakdist.svg", "--chrHeight", "151812"], None),
 ("chipseq","peaktss"): ([GFF, "out/fake_peak.xls", "out/peaktss.svg"], None),
 ("chipseq","pileup"): ([BLAST_XML, "out/pileup.svg"] if False else None, None),
 ("engine","admixture"): (["out/admix.lst", "out/admix.svg"], None),
 ("engine","calcRepeat"): ([NACL, "out/repeat.txt", "--kmerSize", "5"], None),
 ("engine","filesplit"): ([PEP10, "3"], None),
 ("engine","gsadiag"): ([GFF, "out/gsadiag.xls", NACL], None),
 ("engine","gxffilter"): ([GFF, IDS, GFFF], None),
 ("engine","gxfsort"): ([GFF, "out/chloro_sorted2.gff3"], None),
 ("engine","marker"): (["MarkerRandomDesign", "out/marker.tab", "out/marker.out"], None),
 ("engine","markertools"): (["filter", "out/marker.tab"], None),
 ("engine","mggxf"): ([TAB6, "out/chloro_simpl.tsv", "out/mggxf.gff"], None),
 ("engine","qpcrproc"): (["out/qpcr.tab", "out/qpcr.xls"], None),
 ("engine","regiondepth"): (["out/fake.sam", "monarda_chloro:1-1000", "out/depth.txt"], None),
}
# blast xml for pileup
BLAST_XML = None
r = subprocess.run([PY, "-m", "tbtools_cli.cli", "blast", "twoSeqBlast", "--query", PEP10,
                    "--subject", CHPEP, "--outBlastResult", "out/t2b5.xml", "--outFmt", "5"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
if os.path.isfile("out/t2b5.xml"):
    BLAST_XML = "out/t2b5.xml"
    M[("chipseq","pileup")] = (["out/t2b5.xml", "out/pileup.svg", "--query", recs[0]], None)

N = len([1 for f in io.open("all_commands.tsv") if f.strip()])
done = 0
for line in io.open("all_commands.tsv"):
    line = line.strip()
    if not line:
        continue
    g, c = line.split("\t")
    done += 1
    w(f"\n---\n\n## [{done}/{N}] ({g}) {c}")
    if (g, c) in M:
        argv, note = M[(g, c)]
        test(g, c, argv, note=note, timeout=200)
    elif (g, c) in SPECIAL:
        SPECIAL[(g, c)](g, c)
    else:
        test(g, c, None, note="*无适配真实数据输入，仅记录 `--help`；实际执行见对应章节的通用错误样本*" )

LOG.close()
print("DONE", done)

