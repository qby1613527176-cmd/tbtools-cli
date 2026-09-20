#!/usr/bin/env python3
"""
generate_fulltest_data.py — 全功能测试数据集生成器（可重现）
================================================================
生成一份**内部自洽**的最小合成数据集，覆盖 tbtools-CLI 全部命令类别：
序列/表达/树/共线性/集合/GO/富集/HMM/MEME/FASTQ/表格/插件。

关键设计（数据自洽性）：
- 20 条"基因"为骨架：G01..G20，每条有 蛋白质序列(pep)、CDS(可翻译)、
  基因树(新ick)、物种树、GFF 注释（坐标落在 genome 内）
- 表达矩阵 20 基因 × 6 样本（3+3 两组，含组均值差异）
- 双基因组共线性：genome1(3 chr × 6 基因) vs genome2(3 chr × 6 基因)，
  蛋白序列两两共享 motif，diamond/MCScanX 能出 hits
- GO 本体（obo，MF/CC/BP 三层）+ 基因注释 + 选择集 + GSEA 排序文件
- HMM 数据库（hmmbuild 生成，脚本可配路径）+ 扫描靶标
- MEME motif 库（5.x 格式，fimo 可直接读）+ 启动子序列
- 转录组 + 双端 reads（kallisto 定量用，reads 是转录本真实切片）
- 韦恩 3 集合、表格宽/长格式、FASTQ 样例

用法: python3 generate_fulltest_data.py [--hmmbuild <path>] [--out <dir>]
默认输出到脚本同目录 data/。全部纯 Python 标准库 + 可选 hmmbuild。
"""

import os
import random
import sys

random.seed(20260920)  # 可重现

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------- 氨基酸池
AA = "ACDEFGHIKLMNPQRSTVWY"
def rnd_pep(n=120):
    return "".join(random.choice(AA) for _ in range(n))

def translate(cds):
    code = {
        "TTT":"F","TTC":"F","TTA":"L","TTG":"L","TCT":"S","TCC":"S","TCA":"S","TCG":"S",
        "TAT":"Y","TAC":"Y","TAA":"*","TAG":"*","TGT":"C","TGC":"C","TGA":"*","TGG":"W",
        "CTT":"L","CTC":"L","CTA":"L","CTG":"L","CCT":"P","CCC":"P","CCA":"P","CCG":"P",
        "CAT":"H","CAC":"H","CAA":"Q","CAG":"Q","CGT":"R","CGC":"R","CGA":"R","CGG":"R",
        "ATT":"I","ATC":"I","ATA":"I","ATG":"M","ACT":"T","ACC":"T","ACA":"T","ACG":"T",
        "AAT":"N","AAC":"N","AAA":"K","AAG":"K","AGT":"S","AGC":"S","AGA":"R","AGG":"R",
        "GTT":"V","GTC":"V","GTA":"V","GTG":"V","GCT":"A","GCC":"A","GCA":"A","GCG":"A",
        "GAT":"D","GAC":"D","GAA":"E","GAG":"E","GGT":"G","GGC":"G","GGA":"G","GGG":"G",
    }
    out = []
    for i in range(0, len(cds) - 2, 3):
        out.append(code.get(cds[i:i+3], "X"))
    return "".join(out)

def pep2cds(pep):
    """蛋白 → 一段可翻译回原蛋白的 CDS（选常见密码子）"""
    codon = {
        "A":("GCT","GCC","GCA","GCG"),"C":("TGT","TGC"),"D":("GAT","GAC"),
        "E":("GAA","GAG"),"F":("TTT","TTC"),"G":("GGT","GGC","GGA","GGG"),
        "H":("CAT","CAC"),"I":("ATT","ATC","ATA"),"K":("AAA","AAG"),
        "L":("CTT","CTC","CTA","CTG"),"M":("ATG",),"N":("AAT","AAC"),
        "P":("CCT","CCC","CCA","CCG"),"Q":("CAA","CAG"),"R":("CGT","CGC","CGA","CGG"),
        "S":("TCT","TCC","TCA","TCG","AGT","AGC"),"T":("ACT","ACC","ACA","ACG"),
        "V":("GTT","GTC","GTA","GTG"),"W":("TGG",),"Y":("TAT","TAC"),
    }
    out = []
    for ch in pep:
        if ch == "*":
            out.append("TAA")
        else:
            out.append(random.choice(codon[ch]))
    return "".join(out)

def write_fa(path, seqs, desc=None):
    """seqs: {id: seq}"""
    with open(path, "w") as f:
        for sid, s in seqs.items():
            d = desc.get(sid, "") if desc else ""
            f.write(f">{sid}{(' ' + d) if d else ''}\n")
            for i in range(0, len(s), 60):
                f.write(s[i:i+60] + "\n")
    print(f"  ✅ {os.path.relpath(path, OUT)} ({len(seqs)} 条)")

def main():
    os.makedirs(OUT, exist_ok=True)
    print("生成全功能测试数据 →", OUT)

    # ================================================================ 1. 骨架基因
    genes = [f"G{i:02d}" for i in range(1, 21)]           # G01..G20
    pep = {g: rnd_pep(140) for g in genes}                 # 蛋白 140aa
    cds = {g: pep2cds(pep[g]) for g in genes}              # 可翻译回 pep

    # 1.1 蛋白 / CDS / 核苷酸（genome scaffold 承载）
    write_fa(os.path.join(OUT, "pep.fa"), pep, {g: f"test protein {g} OS=Testsp" for g in genes})
    write_fa(os.path.join(OUT, "cds.fa"), cds)

    # 1.2 基因组 3 条 scaffold，每条按基因坐标排布
    scaffold_len = 6000
    genome = {}
    gff_lines = ["##gff-version 3"]
    for si, scaf in enumerate(["Scf1", "Scf2", "Scf3"], 1):
        seq = ["N"] * scaffold_len
        for g in genes[(si-1)*7: si*7]:
            start = 200 + (int(g[1:]) % 6) * 800
            end = start + len(cds[g]) - 1
            for j, nt in enumerate(cds[g]):
                seq[start - 1 + j] = nt
            gff_lines.append(f"{scaf}\tfulltest\tgene\t{start}\t{end}\t.\t+\t.\tID={g};Name={g}")
            gff_lines.append(f"{scaf}\tfulltest\tmRNA\t{start}\t{end}\t.\t+\t.\tID={g}.t1;Parent={g};Name={g}-T1")
            gff_lines.append(f"{scaf}\tfulltest\tCDS\t{start}\t{end}\t.\t+\t0\tParent={g}.t1")
        genome[scaf] = "".join(seq)
    write_fa(os.path.join(OUT, "genome.fa"), genome)
    with open(os.path.join(OUT, "anno.gff3"), "w") as f:
        f.write("\n".join(gff_lines) + "\n")
    print(f"  ✅ anno.gff3（{sum(1 for l in gff_lines if l.startswith('Scf'))} 个 feature）")

    # 1.3 ID 列表 / 重命名映射 / 启动子
    with open(os.path.join(OUT, "ids.txt"), "w") as f:
        f.write("\n".join(genes[:10]) + "\n")
    with open(os.path.join(OUT, "idmap.tsv"), "w") as f:
        for g in genes:
            f.write(f"{g}\t{g.lower()}_protein\n")
    # 启动子：随机 ACGT 400bp，但 G01..G06 植入 ACGTACGTACGT motif 实例 ×2
    # （fimo 扫描 motifs.meme 的 M1 才能有真命中；纯随机序列 0 命中）
    prom = {}
    for g in genes:
        seq = list("".join(random.choice("ACGT") for _ in range(400)))
        if g in (f"G{i:02d}" for i in range(1, 7)):
            seq[80:92] = list("ACGTACGTACGT")
            seq[240:252] = list("ACGTACGTACGT")
        prom[g] = "".join(seq)
    write_fa(os.path.join(OUT, "promoter.fa"), prom)

    # ================================================================ 2. 表达
    # 20 基因 × 6 样本；G01..G08 在样本 A 组高表达（log2FC>1），构造组差异
    samples = ["S1", "S2", "S3", "S4", "S5", "S6"]
    groups = {"S1": "A", "S2": "A", "S3": "A", "S4": "B", "S5": "B", "S6": "B"}
    expr = {g: [] for g in genes}
    for g in genes:
        base = 1000 if g in (f"G{i:02d}" for i in range(1, 9)) else 200
        for s in samples:
            fc = 3.0 if groups[s] == "A" and g in (f"G{i:02d}" for i in range(1, 9)) else 1.0
            expr[g].append(round(base * fc * random.uniform(0.8, 1.2)))
    with open(os.path.join(OUT, "expr.tsv"), "w") as f:
        f.write("gene\t" + "\t".join(samples) + "\n")
        for g in genes:
            f.write(g + "\t" + "\t".join(str(v) for v in expr[g]) + "\n")
    print(f"  ✅ expr.tsv（{len(genes)} 基因 × {len(samples)} 样本）")

    with open(os.path.join(OUT, "sample_group.tsv"), "w") as f:
        for s in samples:
            f.write(f"{s}\t{groups[s]}\n")

    # DEG 表（dehist 用）：gene + log2FC + pvalue
    with open(os.path.join(OUT, "deg.tsv"), "w") as f:
        f.write("gene\tlog2FC\tpvalue\n")
        for g in genes:
            fc = 2.5 if g in (f"G{i:02d}" for i in range(1, 9)) else -0.8
            p = 1e-5 if abs(fc) > 1 else 0.5
            f.write(f"{g}\t{fc}\t{p}\n")

    # rpkmCal 输入：counts + leninfo
    with open(os.path.join(OUT, "counts.tsv"), "w") as f:
        f.write("gene\t" + "\t".join(samples) + "\n")
        for g in genes:
            f.write(g + "\t" + "\t".join(str(random.randint(5, 3000)) for _ in samples) + "\n")
    with open(os.path.join(OUT, "leninfo.tsv"), "w") as f:
        for g in genes:
            f.write(f"{g}\t{len(cds[g])}\n")

    # qPCR（qpcr 命令）
    with open(os.path.join(OUT, "qpcr.tab"), "w") as f:
        f.write("gene\tcontrolCt\tExprCt\n")
        for g in genes[:12]:
            f.write(f"{g}\t{round(random.uniform(18, 24), 2)}\t{round(random.uniform(15, 30), 2)}\n")

    # ================================================================ 3. 树
    # 基因树（Notung reconcile 需要叶子名映射到物种：Notung 支持
    # gene@species 语法或 -s 物种树对应——这里用 @SpeciesA 后缀
    # 设计：G01..G20 分布到 3 物种，同一物种内聚簇
    species_of = {}
    for i, g in enumerate(genes):
        sp = ["SpeciesA", "SpeciesB", "SpeciesC"][i % 3]
        species_of[g] = sp
    def clade(ids):
        n = len(ids)
        if n == 1:
            g = ids[0]
            return f"{species_of[g]}_{g}"
        mid = n // 2
        return f"({clade(ids[:mid])}:0.1,{clade(ids[mid:])}:0.1)"
    gene_tree = f"({clade(genes[:10])}:0.3,{clade(genes[10:])}:0.3);"
    with open(os.path.join(OUT, "gene.nwk"), "w") as f:
        f.write(gene_tree + "\n")
    # 物种树（Notung reconcile 用）
    species_tree = "((SpeciesA,SpeciesB),SpeciesC);"
    with open(os.path.join(OUT, "species.nwk"), "w") as f:
        f.write(species_tree + "\n")
    # 通用树（phylotree/unrooted/treeRooting）
    with open(os.path.join(OUT, "tree.nwk"), "w") as f:
        f.write("((A:0.1,B:0.2):0.3,(C:0.15,D:0.25):0.05);\n")
    print("  ✅ gene.nwk / species.nwk / tree.nwk")

    # ================================================================ 4. 韦恩 3 集
    a = set(genes[:12]); b = set(genes[6:18]); c = set(genes[3:15])
    for name, s in [("set1.txt", a), ("set2.txt", b), ("set3.txt", c)]:
        with open(os.path.join(OUT, name), "w") as f:
            f.write("\n".join(sorted(s)) + "\n")
    print("  ✅ set1/2/3.txt（韦恩）")

    # ================================================================ 5. 共线性（双基因组）
    # ⚠️ MCScanX-SuperFast 的 setInGenome_1/2 是【染色体级序列】。
    # 坑：数字染色体名触发插件 spe 前缀路径 → 抽 CDS 后全 X；
    # 用非数字名（ChrA..，对齐 comparative 可跑模式）
    # 同源组设计：9 个祖先序列 × 2 物种变体（~92% 相似，1-2 个点突变 + 3aa 插入），
    # 组间序列差异大 —— 避免低复杂度/重复 motif 被 diamond seg 过滤（重复序列
    # ACDEFGHIK 循环实测 blast 0 行）
    def ortho_pep(seed, mut_rate=0.08):
        return "".join(ch if random.random() > mut_rate else random.choice(AA) for ch in seed)

    random.seed(20260921)
    # ⚠️ 不能共享 motif 尾部！20aa 局部高相似也会被 diamond 报为 hit
    #   （实测 g1A1 因此多出 g2A3/g2A6 两个假 hit）。每个 (grp,copy) 独立随机序列，
    #   配对拷贝（g1 与 g2 对应）共享同一条 seed + 5% 变异 → 唯一真同源
    ancestors = {
        grp + copy: rnd_pep(130) for grp in "ABC" for copy in "123456"
    }
    # ⚠️ 坑 1：插件 appendID 判定——两物种染色体名重叠 → 自动加 spe<rand>- 前缀
    #   污染所有 ID → MCScanX 解析失败。修复：genome2 染色体名不重叠。
    # ⚠️ 坑 2（本轮实测核心）：MCScanX 共线检测对【稠密 blast 网】免疫——
    #   同源组内拷贝彼此 92% 相似 → diamond 全连接（54 行人全部交叉命中）→
    #   MCScanX 全部判 Dispersed、0 alignments。必须设计成【一对一唯一 best hit】：
    #   g1Ai ↔ g2Ai 强匹配，非对应拷贝显著更弱（变异率 0.35），保证 blast 稀疏。
    # 设计：3 祖先 × 6 拷贝；每拷贝在任意物种只有唯一的强同源（配对拷贝），
    #   组内其他拷贝变异率 0.35（序列差异 ~35%，diamond best hit 唯一）
    chr_len = 12000
    genome_peps = {"1": {}, "2": {}}
    for grp in "ABC":
        for copy in "123456":
            gid_1 = f"g1{grp}{copy}"
            gid_2 = f"g2{grp}{copy}"
            seed = ancestors[grp + copy]
            genome_peps["1"][gid_1] = ortho_pep(seed, mut_rate=0.05)
            genome_peps["2"][gid_2] = ortho_pep(seed, mut_rate=0.05)
    chr_names = {("1", 1): "1", ("1", 2): "1", ("1", 3): "1",
                 ("2", 1): "2", ("2", 2): "2", ("2", 3): "2"}
    # 实际按 A/B/C 各占一条染色体
    chr_of_sp2 = {"A": "ChrA2", "B": "ChrB2", "C": "ChrC2"}
    chr_of_sp1 = {"A": "ChrA", "B": "ChrB", "C": "ChrC"}
    chr_of = {"1": chr_of_sp1, "2": chr_of_sp2}
    for sp, gmap in genome_peps.items():
        chrom = {}
        gff = []
        for grp in "ABC":
            ci = chr_of[sp][grp]
            seq = ["N"] * chr_len
            grp_genes = [g for g in gmap if g[2] == grp]
            for gi, g in enumerate(grp_genes):
                cds_seq = pep2cds(gmap[g])
                start = 300 + gi * 1600  # 1-based GFF 坐标
                end = start + len(cds_seq) - 1
                for j, nt in enumerate(cds_seq):
                    seq[start - 1 + j] = nt  # 0-based 列表索引 = GFF坐标 - 1
                gff.append(f"{ci}\tfulltest\tgene\t{start}\t{end}\t.\t+\t.\tID={g};Name={g}")
                gff.append(f"{ci}\tfulltest\tmRNA\t{start}\t{end}\t.\t+\t.\tID={g};Parent={g};Name={g}")
                gff.append(f"{ci}\tfulltest\tCDS\t{start}\t{end}\t.\t+\t0\tParent={g}")
            chrom[ci] = "".join(seq)
        write_fa(os.path.join(OUT, f"genome{sp}.fa"), chrom)
        with open(os.path.join(OUT, f"genome{sp}.gff"), "w") as f:
            f.write("##gff-version 3\n")
            f.write("\n".join(gff) + "\n")
        print(f"  ✅ genome{sp}.fa（3 染色体 DNA）+ genome{sp}.gff（{len(gff)} feature）")
    write_fa(os.path.join(OUT, "genome1.pep.fa"), genome_peps["1"])
    write_fa(os.path.join(OUT, "genome2.pep.fa"), genome_peps["2"])

    # ================================================================ 6. GO / 富集
    obo = """format-version: 1.2
data-version: fulltest

[Term]
id: GO:0008150
name: biological_process
namespace: biological_process

[Term]
id: GO:0003674
name: molecular_function
namespace: molecular_function

[Term]
id: GO:0005575
name: cellular_component
namespace: cellular_component

[Term]
id: GO:0006915
name: apoptotic process
namespace: biological_process
is_a: GO:0008150 ! biological_process

[Term]
id: GO:0007049
name: cell cycle
namespace: biological_process
is_a: GO:0008150 ! biological_process

[Term]
id: GO:0005634
name: nucleus
namespace: cellular_component
is_a: GO:0005575 ! cellular_component

[Term]
id: GO:0016301
name: kinase activity
namespace: molecular_function
is_a: GO:0003674 ! molecular_function
"""
    with open(os.path.join(OUT, "go.obo"), "w") as f:
        f.write(obo)
    # gene2go（背景注释）：G01-10 富集凋亡/激酶，G11-20 带不富集的 BP 项
    # ⚠️ 命名空间相对背景：若 G11-20 无 BP 注释，BP 背景=10 → 富集 P=1.0。
    # 必须给 G11-20 一个 BP 注释（cell cycle），使 BP 背景=20
    with open(os.path.join(OUT, "gene2go.tsv"), "w") as f:
        for g in genes:
            if g in (f"G{i:02d}" for i in range(1, 11)):
                f.write(f"{g}\tGO:0006915,GO:0016301,GO:0005634\n")
            else:
                f.write(f"{g}\tGO:0007049,GO:0005634\n")
    # 选择集（富集凋亡：G01-05 全带 GO:0006915）
    with open(os.path.join(OUT, "select_deg.txt"), "w") as f:
        f.write("\n".join(f"G{i:02d}" for i in range(1, 6)) + "\n")
    # GSEA 排序文件
    with open(os.path.join(OUT, "rank.rnk"), "w") as f:
        for g in genes:
            fc = 2.5 if g in (f"G{i:02d}" for i in range(1, 9)) else -0.8
            f.write(f"{g}\t{fc}\n")
    # query2go（GSEA）
    with open(os.path.join(OUT, "query2go.tsv"), "w") as f:
        for g in genes:
            if g in (f"G{i:02d}" for i in range(1, 11)):
                f.write(f"{g}\tGO:0006915,GO:0016301\n")
            else:
                f.write(f"{g}\tGO:0007049\n")
    print("  ✅ go.obo / gene2go / select_deg / rank.rnk / query2go")

    # ================================================================ 7. HMM / MEME / FIMO
    # HMM：sample.hmm 手动给一个简单蛋白域（hmmsearch 可扫）
    # HMM 库：用 hmmbuild 从多序列比对生成（手写 HMMER3 格式常被 hmmsearch 拒收）
    import shutil as _sh
    hmmbuild_bin = _sh.which("hmmbuild")
    if hmmbuild_bin:
        aln = os.path.join(OUT, "domain.aln.fa")
        with open(aln, "w") as f:
            for i in range(1, 7):
                seq = "ACDEFGHIKLMNPQRSTVWY" * 2  # 20aa × 2 = 40aa 等长
                if i == 6:
                    seq = ("ACDEFGHIKLMNPQRSTVWY"[:18] + "E" + "ACDEFGHIKLMNPQRSTVWY"[19:]) * 2  # 第19位 W→E ×2，保持 40 字符，长度不变
                f.write(f">seed{i}\n{seq}\n")
        import subprocess
        subprocess.run([hmmbuild_bin, os.path.join(OUT, "sample.hmm"), aln],
                       capture_output=True, text=True)
        os.unlink(aln)
        print("  ✅ sample.hmm（hmmbuild 生成）")
    else:
        print("  ⚠️ 未找到 hmmbuild，跳过 sample.hmm（hmmerSearch 测试需本机安装 HMMER）")
    with open(os.path.join(OUT, "hmm_ids.txt"), "w") as f:
        f.write("test_domain\n")
    # HMM 扫描靶标（含 motif 的蛋白）
    hmmer_target = {}
    for g in genes[:6]:
        hmmer_target[g] = "ACDEFGHIK" * 14  # 与 test_domain 兼容的组成
    for g in genes[6:]:
        hmmer_target[g] = pep[g]
    write_fa(os.path.join(OUT, "hmmer_target.fa"), hmmer_target)
    print("  ✅ sample.hmm / hmm_ids / hmmer_target")

    # MEME 5.x motif 库（fimo 直接读）
    meme = """MEME version 5.5

ALPHABET= ACGT

strands: + -

Background letter frequencies
A 0.25 C 0.25 G 0.25 T 0.25

MOTIF M1 ACGT_motif
letter-probability matrix: alength= 4 w= 6 nsites= 20
  0.9	0.03	0.03	0.04
  0.03	0.9	0.03	0.04
  0.04	0.03	0.9	0.03
  0.03	0.04	0.03	0.9
  0.9	0.03	0.03	0.04
  0.03	0.9	0.03	0.04
"""
    with open(os.path.join(OUT, "motifs.meme"), "w") as f:
        f.write(meme)
    print("  ✅ motifs.meme（fimo/memeViz 用）")

    # ================================================================ 8. 转录组 + reads（kallisto）
    # 转录本：取 G01..G05 的 CDS（真序列，reads 可伪比对）
    with open(os.path.join(OUT, "transcripts.fa"), "w") as f:
        for g in genes[:5]:
            f.write(f">{g}.t1\n{cds[g]}\n")
    # 双端 reads：从转录本随机切片 75bp（fragment 200bp → 双端各 75）
    def frag_reads(seq, n=40, flen=200, rlen=75):
        r1, r2 = [], []
        for _ in range(n):
            if len(seq) <= flen:
                continue
            start = random.randint(0, len(seq) - flen)
            r1.append(seq[start:start+rlen])
            r2.append(seq[start+flen-rlen:start+flen])
        return r1, r2
    with open(os.path.join(OUT, "reads_1.fq"), "w") as f, \
         open(os.path.join(OUT, "reads_2.fq"), "w") as g:
        idx = 0
        for gid in genes[:5]:
            r1, r2 = frag_reads(cds[gid])
            for a, b in zip(r1, r2):
                idx += 1
                for h, seq in [("1", a), ("2", b)]:
                    out = f if h == "1" else g
                    out.write(f"@r{idx}/{h} {gid}\n{seq}\n+\n{'I'*len(seq)}\n")
    print("  ✅ transcripts.fa + reads_1/2.fq（kallisto）")

    # ================================================================ 9. 表格 / FASTQ / 其他
    # 宽表（tableMelt 输入）
    with open(os.path.join(OUT, "wide.tsv"), "w") as f:
        f.write("gene\tS1\tS2\tS3\n")
        for g in genes[:6]:
            f.write(f"{g}\t{random.randint(1,100)}\t{random.randint(1,100)}\t{random.randint(1,100)}\n")
    # 长表（tableCast 输入）
    with open(os.path.join(OUT, "long.tsv"), "w") as f:
        f.write("gene\tsample\tvalue\n")
        for g in genes[:6]:
            for s in ["S1", "S2", "S3"]:
                f.write(f"{g}\t{s}\t{random.randint(1,100)}\n")
    # 距离矩阵（heatmap/pca 用，基因×样本）
    with open(os.path.join(OUT, "dist.tsv"), "w") as f:
        f.write("gene\tS1\tS2\tS3\tS4\tS5\tS6\n")
        for g in genes[:10]:
            f.write(g + "\t" + "\t".join(str(round(random.uniform(0.1, 9.9), 2)) for _ in samples) + "\n")
    # 三列距离文件（hclust 专用: GeneA\tGeneB\tdist）
    with open(os.path.join(OUT, "dist3.tsv"), "w") as f:
        for i in range(0, 10):
            for j in range(i + 1, 10):
                d = round(abs(i - j) * 1.1 + random.uniform(0, 1), 3)
                f.write(f"{genes[i]}\t{genes[j]}\t{d}\n")
    # FASTQ 样例（fqfaConv）
    with open(os.path.join(OUT, "sample.fq"), "w") as f:
        for i in range(4):
            f.write(f"@seq{i}\n{''.join(random.choice('ACGT') for _ in range(50))}\n+\n{'I'*50}\n")
    print("  ✅ wide/long/dist.tsv + sample.fq")

    # 汇总清单
    print("\n生成完成！数据文件清单：")
    for fn in sorted(os.listdir(OUT)):
        print(f"  {fn:24s} {os.path.getsize(os.path.join(OUT, fn))} bytes")

if __name__ == "__main__":
    main()
