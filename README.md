# TBtools CLI — TBtools-II 全功能命令行封装

> 把 [TBtools-II](https://github.com/CJ-Chen/TBtools)（2.535+）的全部功能封装成命令行，Linux/WSL 下免 GUI 直接使用。
> **48+ 个绘图引擎 + 188 个 RPC 数据工具 + 37 个命令行工具 + 任意引擎反射**，全部实测出图。

<div align="center">

**English** | [中文](#中文)

</div>

---

## ✨ Features

| Layer | Capability | Entry |
|:------|:-----------|:------|
| 🎨 **绘图引擎** | 48+ 个（基因结构/Motif/热图/树/共线性/韦恩/ChIP-seq/柱图/环形图/标记设计等） | `tbtools <plotName>` |
| 📊 **RPC 数据工具** | 188 个（FASTA/GFF/表达/Blast/富集/建树/引物等） | `tbtools rpc <method> '<json>'` |
| 🛠️ **命令行工具** | 37 个（extractFasta/statFasta/rpkmCal/tpmCalc/mimicVqsr 等） | `tbtools tool <name>` |
| 🔬 **任意引擎反射** | 万能兜底（任意 TBtools 引擎类） | `tbtools engine <class> key=value` |

All engines are driven **headlessly** (via xvfb on Linux/WSL), no GUI needed. Verified with real biological data (oil-Camellia GRAS gene family etc).

---

## 📦 Installation

### Requirements
- **Linux / WSL2**（需要 `xvfb-run`）
- **JDK 11+**（`java`、`javac`）
- **TBtools_JRE1.6.jar**（TBtools-II 主 jar，~55MB）

### 1. Download TBtools jar
```bash
# Option A: GitHub releases
wget -O lib/TBtools_JRE1.6.jar https://github.com/CJ-Chen/TBtools/releases/download/v2.xxx/TBtools_JRE1.6.jar

# Option B: TBtools official site
# https://www.tbtools.com
```

### 2. Install
```bash
git clone https://github.com/<you>/tbtools-cli.git
cd tbtools-cli
./install.sh --jar /path/to/TBtools_JRE1.6.jar
```

Or set environment variable:
```bash
export TBTOOLS_JAR=/path/to/TBtools_JRE1.6.jar
export PATH="$PWD/bin:$PATH"
```

### 3. Verify
```bash
tbtools help
```

---

## 🎨 Plotting Engines (48+)

### Gene structure / Motif / Sequence logo
```bash
# Gene structure (exons/UTR from GFF)
tbtools genestructure <input.gff> <mRNA_ids.txt> <out.svg> [genome.fa] [w] [h]

# Motif distribution (MEME XML)
tbtools motif <meme.xml> <idList.txt> <out.svg> [w] [h]

# Sequence LOGO
tbtools seqlogo <seqs.fa> <out.svg> [--scaleIC true --showPos false ...]
```

### Expression / Statistics
```bash
# Volcano plot (DEG: GeneID Log2FC pvalue)
tbtools volcano <deg.txt> <out.svg> [pvalCutoff] [fcCutoff] [w] [h]

# Expression level calculators (counts+len → RPKM/TPM; FPKM → TPM)
tbtools tool rpkmCal    --countsTable counts.tsv --lenInfo gene_len.tsv --outTable RPKM.out.tsv
tbtools tool tpmCalc    --countsTable counts.tsv --lenInfo gene_len.tsv --outTable TPM.out.tsv
tbtools tool fpkmToTpm  --fpkmTable RPKM.out.tsv --tpmTable TPM2.out.tsv

# GWAS VQSR mimic: VCF → QD/MQ/FS/SOR quality metrics table
tbtools tool mimicVqsr  --inFile sample.vcf --outFile vqsr.txt

# Marker design (0-1 matrix: rows=locus, cols=sample)
tbtools marker MarkerDist   markers_0-1.tsv out.txt [--maxPoint N]   # max-discrimination marker combo
tbtools marker MarkerFilter markers_0-1.tsv out.txt                   # per-sample marker count
tbtools marker SampleDist   markers_0-1.tsv out.txt                   # marker pairwise distance
tbtools marker BigMarkerRandomDesign markers_0-1.tsv --targetMarkerNum 10 --numberOfTest 200  # random marker combo search

# Phylogenetic tree rooting (MAD: Tria et al. 2017)
tbtools treeRooting unrooted.nwk rooted.out.nwk                        # MAD minimum-ancestor-deviation rooting

# FASTA ID prefix appender
tbtools tool fastaIDAppender --inFa seqs.fa --outFa prefixed.fa --prefix SAMPLE_

# Heatmap (engine-level: clustering / grouping / tree)
tbtools heatmap2 <expr.matrix.tsv> <out.svg> [--log2 --rowScale --clusterRow --clusterCol ...]

# 3D cube heatmap (3 tissues × 3 stages)
tbtools cubeheatmap <expr.tsv> <group.tsv> <out.svg> [--log10]

# Layout heatmap (sample position matrix)
tbtools layoutheatmap <layout.tsv> <expr.tsv> <out.svg> [--cellWidth N ...]

# PCA
tbtools pca <expr.tsv> <out.svg> [rows|cols] [scale] [w] [h]

# qPCR bar plot (with error bars)
tbtools qpcr <data.txt> <out.svg> [w] [h]

# Grouped bar plot with significance (T-test/ANOVA + Bonferroni)
tbtools groupedbar <data.tsv> <out.svg> [BAR_ERROR|BOXPLOT|VIOLIN|SWARM] [SEM|SD|CI95]
```

### Phylogeny / Tree
```bash
# Tree + annotation tracks (TextAnno/HeatMap/BarPlot/Tile/StackBar/Domain...)
tbtools tree <treeMeta.cfg> <out.svg> [pad]

# Hclust → Newick
tbtools hclust <distance_matrix.tsv> <out.nwk>
```

### Genomic location / Circos / Synteny
```bash
# Gene chromosome location (GFF + IDs)
tbtools genelocgff <gff3> <ids.txt> <out.svg> [--chrLen l.tsv --pairs p.tsv ...]

# Gene location (native CLI)
tbtools genelocation --ChrLen <chrlen.tsv> --FeaturePos <pos.tsv> --OutGraph <out.svg>

# Circos circular synteny
tbtools circos <chrLen.txt> <link.txt> <genePos.txt> <out.svg> [w] [h]

# SuperCircos (7 track types: Tile/Triangle/HeatMap/Point/Line/Bar/Arrow)
tbtools supercircos <config.cfg> <out.svg> [w] [h]

# Dot plot (synteny scatter)
tbtools dotplot --inGff <gff> --genePair <pairs> --chrLayout <layout> --outGraph <out.svg>

# PAF dot-plot (minimap2 output)
tbtools pafviz <in.paf> <out.svg> [graphSize] [colorMode]

# PAF genome-comparison plot (13-col PAF required)
tbtools pafcomp --inPaf <in.paf> --outGraph <out.svg> [--colorMode Target|Query|None]

# PAF reference-base coverage calc
tbtools pafref --inPaf <in.paf> --outTab <out.tsv>

# PAF conflict detection (assembly conflict bins, GenomeAssembly module)
tbtools conflictpaf <in.paf> <out.tsv> [binSize]

# Assembly conflict partitioning (polyploid group clustering, chains after conflictpaf)
tbtools partitionconflict <inConflict.tsv> <polyPoid> <outCluster>

# Multi-species data prep (add species prefix to genome+GFF IDs — feed into findblockdual/multiple)
tbtools preparespecies <prefix> <inGenome.fa> <inGFF> <outGenome.fa> <outGFF>

# BAM coverage/depth state assessment (RNA-seq/genome BAM vs GFF genes)
tbtools bamstate <out.tsv> <gff3> <bam1> [bam2 ...]

# qPCR relative quantification (2^-ΔΔCt; input: gene\tcontrolCt\tExprCt)
tbtools qpcrExp <in.qpcr.tab> <out.xls>

# Tissue-specificity tau index (0=ubiquitous, 1=tissue-specific)
tbtools tauIndex <inExpTab> <outTAU>

# Sample expression correlation matrix (Pearson, for co-expression/clustering)
tbtools exprCorr <inFPKM> <outCorrMat>

# Collapse expression matrix samples by group (Sum|Mean|Max|Min|Var|Std)
tbtools groupCol <inTable.tsv> <inGrpInfo.tsv> <outTable> [Mean]

# Batch string replace (pattern map: old\tnew; --partial for substring mode)
tbtools batchReplace <inFile> <outFile> <patternMap.tsv> [--partial]

# Collapse table rows by key column (merge values with ;)
tbtools tableCollapse <inTable> <keyColIndex> <outTable> [hasHeader]

# miRNA target prediction (full pipeline: ssearch36 -i -m10 → TargetSoEngine scoring)
tbtools mirnatarget <mirna.fa> <target.fa> <out.tsv> [--evalue X --threads N --scoreCutOff N --maxMismatch N]

# Dual-genome micro-synteny
tbtools microsyn <gxf1> <gxf2> <collinearity> <out.svg> [--chr1 C --start1 S --end1 E ...]

# Multi-species micro-synteny
tbtools multisyn <gxf.lst> <collinear.lst> <out.svg> [--genes idlist.txt]

# Multi-species synteny
tbtools msy <simplifiedGff.pos> <links.txt> <chrLayout.txt> <out.svg> [w] [h]

# Circular gene viewer
tbtools circlegene <gff> <geneID.txt> <out.svg> [--link f --rankedChr f ...]
```

### Venn / Sets
```bash
# Venn 2/3/4 (native CLI)
tbtools engine biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn2 --List1 a.txt --List2 b.txt --label1 A --label2 B --graph out.svg --prefix out --bgNum 30000
# Venn3: --List1..3 ; Venn4Ellipse: --List1..4

# Venn 5/6 (bridge)
tbtools venn5 <out.svg> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> [labels]
tbtools venn6 <out.svg> <setA.txt> ... <setF.txt> [labels]

# UpSet intersection plot
tbtools upset <sets.txt> <out.svg> [w] [h]
```

### ChIP-seq / Others
```bash
# Peak-TSS heatmap
tbtools peaktss <gxf> <macs2_peak.xls> <out.svg> [--dist N]

# Peak chromosome distribution
tbtools peakdist <chrLen.tsv> <macs2_peak.xls> <out.svg> [--width W --height H]

# Peak annotation to genes
tbtools peakanno <gxf> <macs2_peak.xls> <out.tsv> [--dist N]

# Differential expression dual histogram
tbtools dehist <deg.txt> <out.svg> [w] [h]

# Enrichment bar plot
tbtools barplot <enrichment.tsv> <out.svg> <termCol> <pvalCol> [classCol] [maxTerms]

# Color scheme generator (from a table column)
tbtools colorscheme <inTab> <outTab> <refColIndex>

# Distance / correlation between two columns
tbtools distance <in.tsv> <col1> <col2> <euclidean|pearson|pearsonDist>

# RNA mountain plot (secondary-structure heights)
tbtools mountain <fold.txt> <out.tsv>

# BLAST XML pile-up (per-query hit coverage)
tbtools pileup <blast.xml> <out.svg> [--query NAME]

# Genome-coverage + RNA structure (PDF output)
tbtools plotrna <genomeFA> <region> <SAM> --directPDF out.pdf

# ADMIXTURE Q-matrix stacked plot
tbtools admixture <qFiles.lst> <out.svg> [sampleIDFile] [groupFile] [sortMode]

# MSA alignment viewer
tbtools msa <aligned.fasta> <out.svg> [padding]

# Virtual gel electrophoresis (PCR fragments)
tbtools gel <FragmentRangeArr> <LaneLabels> <MarkerRange> <out.svg>

# GFA assembly graph viz
ntbtools gfa <in.gfa> <out.svg> [w] [h]

# Plastome circular map (GenBank → annotation)
tbtools microgenome <in.gbk> <anno.tsv> <out.svg> [micro|macro]

# Pseudo-synteny block search across two genomes (real-data verified: Camellia Chr06 ↔ tea Chr01)
tbtools findblockdual <qGenome.fa> <q.gff> <sGenome.fa> <s.gff> <qId> <out.txt> [--leftEdge N --rightEdge N --expand N --threads N --evalue X --minIdentity X --bestHit N]

# Multi-genome pseudo-synteny blocks (1 query + N subjects)
tbtools findblockmultiple <qGenome.fa> <q.gff> <qId> <out.txt> <s1Genome.fa> <s1.gff> [<s2Genome.fa> <s2.gff> ...]

# Visualize pseudo-synteny blocks (PDF; input = findblockdual/multiple output)
tbtools visualizeblock <inBlockOut> <out.pdf> [--labels "Genome1,Genome2"]

# Generic reflection bridge (drive ANY TBtools engine)
tbtools generic <engineClass> <method> <out.svg> [--set field value ...] [--width W] [--height H]
```

---

## 📊 RPC Data Tools (188 methods)

```bash
tbtools server start                       # start RPC server (port 8765)
tbtools methods                            # list all 188 methods
tbtools rpc FastaStat.process '{"inputPath":"in.fa","outputPath":"out.xls"}'
tbtools rpc OneStepBuildATree.process '{"inputPath":"seqs.fa","outputPath":"outdir","options":{"ultraFastBS":true}}'
tbtools heatmap matrix.tsv out.png [group.tsv]   # quick heatmap
```

| Method | Function |
|:-------|:---------|
| `FastaStat.process` | sequence stats (N50/GC/length) |
| `FastaExtract.process` | extract by ID |
| `CdsToProtein.process` | CDS → protein |
| `FastaSsrMiner.process` | SSR search |
| `OneStepBuildATree.process` | one-step phylogeny (MUSCLE+trimAl+IQ-TREE) |
| `FetchATimeTree.process` | TimeTree |
| `AmazingHeatMap.process` | heatmap |
| `ExpressionCorrMatrix.process` | expression correlation |
| `GxfToGenePos.process` | GFF → gene position |
| `QuickGeneFamilyIdentification.process` | gene family identification |
| `TableTools.*` | 17 table tools |
| `CheckPrimer.process` | primer check |

---

## 🛠️ CLI Tools (30)

```bash
tbtools tool extractFasta          # extract sequences by ID
tbtools tool statFasta             # sequence statistics
tbtools tool cdsTranslater         # CDS → protein
tbtools tool rpkmCal               # RPKM calculation
tbtools tool autoMakeBlastDb       # build blast db
# ... full list: tbtools list tools
```

---

## 🔬 Any Engine Reflection (universal fallback)

```bash
tbtools engine <full.class.Name> key=value [--call method]
# example: QuickStatFasta
tbtools engine biocjava.bioIO.FastX.FastaIndex.QuickStatFasta inFile=seqs.fa --call stat
```

---

## 📁 Project Structure

```
tbtools-cli/
├── bin/
│   ├── tbtools            # unified entry (33 plots + RPC + tools + engine)
│   ├── tbplot.sh          # plotting engines
│   ├── tbtools_rpc.sh     # RPC server & calls
│   ├── tbcli.py           # tool list & CLI tools
│   └── tbengine.sh        # reflection launcher
├── bridges/               # 27 Java bridge sources
├── build/                 # compiled bridges (auto-generated)
├── config/config.sh       # unified config (TBTOOLS_JAR etc.)
├── examples/              # example data + scripts
├── docs/                  # detailed documentation
├── install.sh             # one-command installer
└── README.md
```

---

## ⚠️ Known Limitations

| Engine | Status |
|:-------|:-------|
| RNAplotAdvance | needs RNAfold |
| MicroGenomeViz | doesn't handle `join(complement(...))` |
| UnrootedTreeViz | hardcoded demo main |
| geneOnGenome CLI | jar compile-level bug |
| dualsyn (DualSyntenyPlotterAdvance) | uses legacy JJplot2 framework (save limited) |
| PhyloTreeView | needs TreeTab format (not pure Newick) |

---

## 🙏 Credits

- [TBtools](https://github.com/CJ-Chen/TBtools) — the underlying toolkit by Chengjie Chen
- This project is an independent CLI wrapper, not affiliated with TBtools

## 📄 License

This CLI wrapper: **MIT License** (see [LICENSE](LICENSE)). TBtools itself is MIT-licensed by its authors.

---

## 中文

# TBtools CLI — TBtools-II 全功能命令行封装

## ✨ 功能总览

| 层 | 能力 | 入口 |
|:---|:-----|:-----|
| 🎨 **绘图引擎** | 48+ 个（基因结构/Motif/热图/树/共线性/韦恩/ChIP-seq/柱图/环形图/标记设计等） | `tbtools <图名>` |
| 📊 **RPC 数据工具** | 188 个（FASTA/GFF/表达/Blast/富集/建树/引物等） | `tbtools rpc <方法> '<json>'` |
| 🛠️ **命令行工具** | 37 个（extractFasta/statFasta/rpkmCal/tpmCalc/mimicVqsr 等） | `tbtools tool <名称>` |
| 🔬 **任意引擎反射** | 万能兜底（任意 TBtools 引擎类） | `tbtools engine <类名> key=value` |

所有引擎在 Linux/WSL 下 **headless 运行**（xvfb），无需 GUI。已用真实生物数据验证（油茶 GRAS 基因家族等）。

## 📦 安装

1. 下载 TBtools jar（GitHub releases 或官网 tbtools.com）
2. `git clone` 本项目
3. `./install.sh --jar /path/to/TBtools_JRE1.6.jar`

## 🎨 绘图命令速查

```bash
# 基因结构 / Motif / LOGO
tbtools genestructure <gff> <ids> <out.svg> [genome.fa] [w] [h]
tbtools motif <meme.xml> <ids> <out.svg> [w] [h]
tbtools seqlogo <seqs.fa> <out.svg>

# 表达 / 统计
tbtools volcano <deg.txt> <out.svg> [pval] [fc] [w] [h]
tbtools heatmap2 <matrix> <out.svg> [--log2 --rowScale --clusterRow --clusterCol]
tbtools cubeheatmap <expr> <group> <out.svg>
tbtools layoutheatmap <layout> <expr> <out.svg>
tbtools pca <expr> <out.svg> [rows|cols]
tbtools qpcr <data> <out.svg>
tbtools groupedbar <data> <out.svg> [BAR_ERROR|BOXPLOT|VIOLIN|SWARM]

# 树
tbtools tree <treeMeta.cfg> <out.svg>
tbtools hclust <distance.tsv> <out.nwk>

# 定位 / Circos / 共线性
tbtools genelocgff <gff3> <ids> <out.svg>
tbtools genelocation --ChrLen <len> --FeaturePos <pos> --OutGraph <out>
tbtools circos <chrLen> <links> <genePos> <out.svg>
tbtools supercircos <config.cfg> <out.svg>
tbtools dotplot --inGff <gff> --genePair <pairs> --chrLayout <layout> --outGraph <out>
tbtools pafviz <in.paf> <out.svg>
tbtools microsyn <gxf1> <gxf2> <collinearity> <out.svg>
tbtools multisyn <gxf.lst> <collinear.lst> <out.svg>
tbtools msy <pos> <links> <layout> <out.svg>
tbtools circlegene <gff> <ids> <out.svg>

# 韦恩
tbtools venn5 <out> <5 sets> [labels]
tbtools venn6 <out> <6 sets> [labels]
tbtools upset <sets.txt> <out.svg>

# ChIP-seq / 其他
tbtools peaktss <gxf> <peak.xls> <out.svg>
tbtools peakdist <chrLen> <peak.xls> <out.svg>
tbtools dehist <deg.txt> <out.svg>
tbtools barplot <enrich.tsv> <out.svg> <termCol> <pvalCol>
tbtools admixture <qFiles.lst> <out.svg>
tbtools msa <aligned.fa> <out.svg>
tbtools generic <engineClass> <method> <out.svg> [--set f v ...]
```

## ⚠️ 已知限制

见上方英文表格。

## 📄 许可

本 CLI 封装为 MIT License。TBtools 本身由其作者 Chengjie Chen 以 MIT 许可发布。
