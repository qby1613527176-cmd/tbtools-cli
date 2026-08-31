# TBtools CLI 命令参考手册（COMMAND REFERENCE）

> 自动提取自 `tbplot.sh` + `bridges/*.java` + `tbcli.py`。用法注释来自源码，坑位来自 2026-08-31 全量回归测试实测。

## 目录

- [一、快速导航](#一快速导航)
- [二、绘图引擎 tbplot.sh 命令（88）](#二绘图引擎-tbplotsh-命令88)
- [三、CLI 工具 tbtools tool（82）](#三cli-工具-tbtools-tool82)
- [四、桥文档 bridges/*.java（80）](#四桥文档-bridgesjava80)
- [五、已知坑（实测）](#五已知坑实测)
- [六、engine 通用反射](#六engine-通用反射)
- [七、RPC 188 方法](#七rpc-188-方法)

## 一、快速导航

| 层 | 入口 | 用途 | 数量 |
|:---|:-----|:-----|:----:|
| 绘图/分析引擎 | `tbplot.sh <命令>` | 出图类引擎（SVG/PNG/PDF） | 88 命令 / 123 引擎 |
| 命令行工具 | `tbtools tool <名称>` | 数据处理类工具（自带 ArgsParser） | 82 |
| 通用反射 | `tbtools engine <类> key=value` | 任意 TBtools 引擎万能兜底 | 任意 |
| RPC 数据工具 | `tbtools rpc <方法> '<json>'` | 188 个数据方法 | 188 |

```bash
# 快速自检：所有命令一览
tbtools list plots          # 绘图命令（转发 tbplot.sh help）
tbtools list tools         # CLI 工具（CLI_TOOLS）
tbtools methods            # RPC 方法
tbplot.sh help             # 绘图命令 + 用法一屏
```

## 二、绘图引擎 tbplot.sh 命令（88）

统一格式：`tbplot.sh <命令> [参数...]`。输出以 `.svg/.png/.pdf` 后缀指定，自动走 xvfb（headless）。

| # | 命令 | 用法 | 说明 |
|:--|:-----|:-----|:-----|
| 1 | `motif` | `用法: motif <meme.xml> <idList.txt> <outFile> [width] [height]` |  |
| 2 | `genelocation` | `用法: genelocation --ChrLen <chrlen> --FeaturePos <pos> --OutGraph <out> [--FeatureColor <map>]` |  |
| 3 | `dotplot` | `用法: dotplot --inGff <gff> --genePair <pairs> --chrLayout <layout> --outGraph <out>` | 简化GFF: Chr\tGene\tStart\tEnd\tStrand ; chrLayout: Genome: Chr1 Chr2... |
| 4 | `circos` | `用法: circos <chrLen.txt> <link.txt> <genePos.txt> <outFile> [w] [h]` | link.txt/genePos.txt 可空文件 |
| 5 | `pca` | `用法: pca <expr.matrix.tsv> <out> [row|col] [scale] [w] [h]` | 通用反射桥 GenericCli 驱动 PCAanalysis（doPCA+postGraph） |
| 6 | `generic` | `用法: generic <engineClass> <method[+method2]> <out> [--set field value ...] [--width N] [--height N]` | 通用反射桥：驱动任意 TBtools 引擎（setter + plot/process/postGraph + save2Graph） |
| 7 | `gfa2fa` | `用法: gfa2fa <in.gfa> <out.fa>   # GFA 组装图 → FASTA（第91引擎，GFAtoFasta）` |  |
| 8 | `qpcr` | `用法: qpcr <data.txt> <out> [w] [h]   (data: name\tmean\tsd)` |  |
| 9 | `hclust` | `用法: hclust <expr.matrix.tsv> <out.nwk> [distMethod] [clusterMethod]` |  |
| 10 | `volcano` | `用法: volcano <deg.txt> <outFile> [pvalCutoff] [fcCutoff] [w] [h]` | deg.txt: GeneID\tLog2FC\tpvalue |
| 11 | `upset` | `用法: upset <sets.txt> <outFile> [w] [h]` | sets.txt: 每行 "集合名\t成员1\t成员2..."（tab 分隔） |
| 12 | `msa` | `用法: msa <aligned.fasta> <outFile> [padding]` | 尺寸按子面板自动计算，勿传 w/h |
| 13 | `genelocgff` | `用法: genelocgff <gff3> <idList> <out> [--chrLen len.tsv] [--rename r.tsv] [--pairs p.tsv] [--color c.tsv] [--rankedChr list] [--onlyMapped true|false] [--showLabel true|false]` |  |
| 14 | `tree` | `用法: tree <treeMeta.config> <out> [pad]` | 配置格式见 TreeCli.java 注释（[TYPE]:Tree + [NEWICK] + [setting] + 可选 [TYPE]:TextAnno/HeatMap/BarPlot/... 轨道） |
| 15 | `phylotree` | `用法: phylotree <in.nwk> <out> [vertical] [width] [height]` | PhyloTreeView 系统发育树视图（08/31 攻下，纠正「需 TreeTab」误判） |
| 16 | `unrooted` | `用法: unrooted <in.nwk> <out> [layout] [width] [height] [iterations]` | 无根树可视化（引擎 115，unrootedtree 独立引擎，非 UnrootedTreeViz） |
| 17 | `violin` | `用法: violin <in.tsv> <out> [width] [height]` | 独立小提琴图（引擎 116，ViolinPlot.generate()；仅 SVG/PDF） |
| 18 | `barplotter` | `用法: barplotter -g <gff> -s <synteny> -c <ctl> -o <out.png>` | 合成共线性柱状图（引擎 117，bar_plotter.main1——main 是死代码） |
| 19 | `findpath` | `用法: findpath --inGffArr <gff1,gff2,...> --inGenePairs <pairs> --inRegion <geneID> [--flankGeneNum N] [--highlightGene ID] --outGraph <out>` | 共线性基因块进化路径（引擎 118，FindPathBySynteny.main1；main 硬编码演示） |
| 20 | `mcscanx` | `用法: mcscanx <gff> <blast> <outPrefix> [--html]   # 共线性检测` | mcscanx classify <gff> <blast> <outPrefix>  # 重复基因分类（WGD/tandem/proximal/dispersed/singleton） |
| 21 | `degramdom` | `用法: degramdom <in.tsv> [out.nwk]` | 亲子表构建 Newick 树（工具 73，BuildDegramdomFromTable.process；main 硬编码演示） |
| 22 | `sambamcov` | `用法: sambamcov <in.bam> <out.tsv> [binSize] [countMode]` | BAM bin 覆盖统计（工具 74，SamBamBINCov.process——main 硬编码演示） |
| 23 | `bamindex` | `用法: bamindex <in.sorted.bam> [out.bai]` | BAM 索引创建（工具 75，BAMIndexCreater.process——main 硬编码演示） |
| 24 | `bamsort` | `用法: bamsort <in.bam> <out.bam> [sortOrder] [tmpDir]` | BAM 排序（工具 76，SAMBAMSorter.process——main 硬编码演示） |
| 25 | `onesteptree` | `用法: onesteptree --inPepFie <in.pep> --outFilePrefix <outDir> [--bbTime N] [--clean true|false]` | 一步法 ML 系统发育树（引擎 119，OneStepMLTree——pep→muscle→trimal→IQ-TREE MFP+UFboot） |
| 26 | `simplehmmscan` | `用法: simplehmmscan <pfamA.hmm> <target.pep> <idList.txt> <out.txt>` | Pfam 域快速扫描（工具 83，simpleHmmscan——main 硬编码演示 → setter+process，调系统 hmmsearch） |
| 27 | `colorscheme` | `用法: colorscheme <in.tab> <out.tab> <refColIndex(1-based)>` | 表格分组着色（工具 86，ColorSchemeGenerator.process——main 硬编码演示） |
| 28 | `regiondepth` | `用法: regiondepth <in.sam> <region> <out.depth> [scaleFactor]` | SAM 区域覆盖深度（工具 88，CalcRegionDepth.init+processRegion——main 硬编码演示） |
| 29 | `markertools` | `用法: markertools <filter|dist|sampledist> <in.marker.tab> [maxPoint]` | 分子标记分析组（工具 89：MarkerFilter minor allele / MarkerDist / SampleDist——main 均硬编码） |
| 30 | `amazingmeta` | `用法: amazingmeta <meme.xml> <newick.treefile> <out.svg|png|pdf> [seqLen.txt] [geneRename.txt]` | Amazing Meta Plot（引擎 120，DrawAmazingMetaPlot——进化树+Motif模式+基因结构+蛋白域组合图） |
| 31 | `cddmotif` | `用法: cddmotif <cdd.hitdata.txt> <in.fasta> <out.svg|png|pdf> [newick.treefile]` | CDD 保守域模式图（引擎 121，DrawMotifPatternFromCDDResult.postGraph——GRAS hitdata 真实验证 56 基因全匹配） |
| 32 | `seqlentrack` | `用法: seqlentrack <seqlen.txt> <out.svg|png|pdf> [newick.treefile]` | 序列长度骨架图（引擎 122，DrawSequenceFromSeqLenInfo——AmazingMetaPlot CDD 面板底层） |
| 33 | `pfammotif` | `用法: pfammotif <pfamscan.txt> <in.fasta> <out.svg|png|pdf> [newick.treefile]` | Pfam 保守域模式图（引擎 123，DrawMotifPatternFromPfamResult——委托 PfamDomainHitsTableParser） |
| 34 | `pep2codon` | `用法: pep2codon <cds.fa> <pep.aln.fa> <codon.aln.out>` | 蛋白比对回译密码子比对（工具 91，pepAln2CodonAln.transformat 静态方法——Ka/Ks 刚需） |
| 35 | `mast2tab` | `用法: mast2tab <mast|meme.xml> <out.tab>` | MEME Suite XML→表格（工具 93，MEMESuiteXMLtoTab——main 全硬编码 → setter+process） |
| 36 | `qpcrproc` | `用法: qpcrproc <in.qpcr.tab> <out.xls>` | qPCR 相对表达分析（工具 97，SimpleQPCRProcessser——2^-ΔΔCt，Sample\tRefCt\tExpCt） |
| 37 | `filesplit` | `用法: filesplit <inFile> <numParts>` | 文件按份数分割（工具 99，FileLineSplit.Split 静态方法） |
| 38 | `memerun` | `用法: memerun <in.fasta> <workingDir> [--motif N] [--minW N] [--maxW N] [--evalue X] [--mode ...]` | 一步法 MEME motif 发现（工具 100，QuickRunMEME——调系统 meme） |
| 39 | `mastrun` | `用法: mastrun <meme.xml> <seq.fasta> <workingDir> [--motifs M] [--seqEvalue X] [--motifPvalue X] [--other "..."]` | 一步法 MAST motif 扫描（工具 101，QuickRunMAST——调系统 mast；与 memerun 配套） |
| 40 | `mggxf` | `用法: mggxf <inGenePair|blastTab6> <in.simplified.gff> <out.LinkedRegion> [GenePair|BlastTab6]` | 多 GFF 视图格式转换（工具 103，FormatTranformerForMultipleGffViewer——GenePair/BlastTab6→LinkedRegion） |
| 41 | `gsadiag` | `用法: gsadiag <in.fixed.gff3> <out.stat.xls> [genome.fasta] [relax] [--checkUTR]` | 基因结构快速诊断（工具 94，GsaQuickDiagnosis——相位验证+长度异常+可选编码潜能检查） |
| 42 | `gxfsort` | `用法: gxfsort <in.gff3|gtf> <out.sorted>` | GFF 按染色体+坐标排序（工具 95，GXFSort.sortByPretty——注释预处理刚需） |
| 43 | `gxffilter` | `用法: gxffilter <in.gff3|gtf> <idList.txt> <out.gff3|gtf>` | GFF 按 ID 列表过滤（工具 96，GXFfilter.setIDList+process——基因家族子注释提取刚需） |
| 44 | `annocompare` | `用法: annocompare <before.gff3> <after.gff3> <outDir> [runName] [reciprocalOverlap] [boundaryTol] [cdsChangePct] [utrChangePct] [geneScope] [overlapMode]` | 注释版本对比管线：对比同一基因组前后两版注释，产 change_summary.csv/change_log.csv/BED + |
| 45 | `genedensity` | `用法: genedensity <in.gff3> <out.tsv> [binSize]` | 基因密度谱：按窗口统计每染色体/contig 基因数（基因组轨道/密度分析） |
| 46 | `seqconvert` | `用法: seqconvert -i <in> -o <out> -iF <fmt> -oF <fmt>` | 序列格式转换（main1 入口；fmt: fasta|clustal|MEGA|nexus|PAML|phylip） |
| 47 | `trimmsa` | `用法: trimmsa <in.aln.fa> <out.aln.fa> [ratio]` | MSA 修剪（按列保留率），main 硬编码 → 桥 setter+process |
| 48 | `heatmap2` | `用法: heatmap2 <expr.matrix.tsv> <out> [options]` | 矩阵: 首列基因名 + 列名表头，其余数值。options 见 HeatmapCli.java 注释（--log2 --rowScale --clusterRow/Col --rowGroup/ColGroup --transpose 等） |
| 49 | `supercircos` | `用法: supercircos <config.cfg> <out> [width] [height]` | 配置格式见 SuperCircosCli.java 注释（[chrLen] [link] [gene] [track] 等行导向配置） |
| 50 | `barplot` | `用法: barplot <enrichment.tsv> <out> <termCol> <pvalCol> [classCol] [maxTerms] [xlab] [ylab] [mode]` | mode: Normal|TextOnLeft|BarOnLeft |
| 51 | `pafviz` | `用法: pafviz <in.paf> <out> [graphSize] [colorMode] [switchQT] [minAlnLen] [rcColor]` | colorMode: Target|Query|None |
| 52 | `admixture` | `用法: admixture <qFiles.lst> <out> [sampleIDFile] [groupFile] [sortMode] [width] [height] [panelInterval]` | sortMode: Qraito|Lexical|None |
| 53 | `groupedbar` | `用法: groupedbar <data.tsv> <out> [plotType] [errorBarType] [hasHeader] [title] [--options]` | plotType: BAR_ERROR|BOXPLOT|VIOLIN|SWARM |
| 54 | `layoutheatmap` | `用法: layoutheatmap <layout.tsv> <expr.tsv> <out> [--options]` | layout.tsv: 样本名矩阵（TSV，空格用 NA） |
| 55 | `cubeheatmap` | `用法: cubeheatmap <expr.tsv> <group.tsv> <out> [--log10 --minColor r,g,b --midColor r,g,b --maxColor r,g,b]` | expr.tsv: 表达矩阵（首列基因名 + 样本名表头） |
| 56 | `rnaplot` | `用法: rnaplot <seq.fa|rawSeq> <out> [--colorMap "seq1=R,G,B;seq2=R,G,B"] [--interactive false]` | RNA 二级结构图（第111引擎，RNAplotAdvance，需 RNAfold/RNAplot 可执行） |
| 57 | `circlegene` | `用法: circlegene <gff> <geneID.txt> <out> [--rename f --link f --rankedChr f --allChr --graphSize N --startAngle N --endAngle N --chrFill r,g,b --chrLabelColor r,g,b]` | geneID.txt: mRNA ID 每行一个（可第二列 1/0 控制颜色） |
| 58 | `genestructure` | `用法: genestructure <input.gff> <idList.txt> <outFile> [genome.fa] [width] [height]` |  |
| 59 | `seqlogo` | `用法: seqlogo <seq.fa|seq.txt> <out.svg/png> [--scaleIC true|false] [--showPos] [--startPos N] [--borderColor R,G,B] [--borderSize N] [--onlyBorder] [--xInterval N] [--yInterval N]` | seq 输入: FASTA 或 纯文本（每行一条序列，等长已比对） |
| 60 | `peaktss` | `用法: peaktss <gxf> <macs2_peak.xls> <out.svg/png> [--dist N] [--bin N] [--color]` | gxf: 基因注释（GFF/GXF，mRNA 行定义 TSS） |
| 61 | `peakdist` | `用法: peakdist <chrLen.tsv> <macs2_peak.xls> <out> [--chrHeight H] [--topLenRank N] [--width W] [--height H]` | chrLen.tsv: Chr\tLength（染色体长度） |
| 62 | `peakanno` | `用法: peakanno <gxf> <macs2_peak.xls> <out.tsv> [--dist N]` | macs2_peak.xls: MACS2 标准 peak 格式（chr start end length abs_summit ...） |
| 63 | `microgenome` | `用法: microgenome <inGBK> <anno.tsv> <out> [micro|macro]` | inGBK: GenBank 质体/质粒基因组文件 |
| 64 | `gel` | `用法: gel <FragmentRangeArr> <LaneLabels> <MarkerRange> <out>` | FragmentRangeArr: 分号分隔泳道/逗号分隔片段，如 "798;1233,228;1688,1598" |
| 65 | `gfa` | `用法: gfa <in.gfa> <out> [width] [height]` | GFA 格式: S 行=节点（S\tname\tseq），L 行=边（L\tfrom\tstrand\tto\tstrand\toverlap） |
| 66 | `pafcomp` | `用法: pafcomp --inPaf <paf> --outGraph <out> [--colorMode Target|Query|None] [--size N] [--minLen N]` | PAF 基因组比较图（⚠️ 入口是 main1 非 main） |
| 67 | `pafref` | `用法: pafref --inPaf <paf> --outTab <out.tsv>` | PAF 参考碱基覆盖计算（minimap2 -c --cs 输出） |
| 68 | `colorscheme` | `用法: colorscheme <inTab> <outTab> <refColIndex>` | inTab: tab 分隔表；refColIndex: 从 0 开始，取该列做配色 key（去重） |
| 69 | `distance` | `用法: distance <in.tsv> <col1> <col2> <euclidean|pearson|pearsonDist>` | in.tsv: tab 分隔表；col1/col2: 列索引（从0开始）；输出两列数值的距离/相关系数（第42引擎） |
| 70 | `mountain` | `用法: mountain <fold.txt> <out.tsv>` | fold.txt: RNA 二级结构折叠字符串（() 和 .）；输出每碱基山峰高度（第43引擎） |
| 71 | `pileup` | `用法: pileup <blast.xml> <out.svg> [--query NAME]` | blast.xml: BLAST+ XML 输出（-outfmt 5）；画 query 的 hits pile-up 图（第44引擎） |
| 72 | `plotrna` | `用法: plotrna <genomeFA> <region> <SAM> [--directPDF out.pdf]` | region: 'chr:startPos-endPos'；SAM: 比对 reads；画基因组区域覆盖度+RNA结构图（第45引擎） |
| 73 | `bamstate` | `用法: bamstate <out.tsv> <gff3> <bam1> [<bam2> ...]` | gff3: 标准 GFF3（gene/mRNA 特征）；bam: 比对 BAM（需 samtools 建索引） |
| 74 | `preparespecies` | `用法: preparespecies <prefix> <inGenome.fa> <inGFF> <outGenome.fa> <outGFF>` | 给基因组+GFF 加物种前缀（seqid + ID）——TBtools 多物种比较数据准备（第56引擎） |
| 75 | `partitionconflict` | `用法: partitionconflict <inConflictFreq.tsv> <polyPoid> <outCluster>` | inConflictFreq.tsv: conflictpaf 输出（contigA\tcontigB\tcount） |
| 76 | `mirnatarget` | `用法: mirnatarget <mirna.fa> <target.fa> <out.tsv> [--evalue X] [--threads N] [--scoreCutOff N] [--maxMismatch N]` | mirna.fa: miRNA 序列（建议每轮一条或一族）；target.fa: 转录本/基因组靶标 |
| 77 | `conflictpaf` | `用法: conflictpaf <in.paf> <out.tsv> [binSize]` | in.paf: 基因组比对 PAF（minimap2/minigraph） |
| 78 | `findblockmultiple` | `用法: findblockmultiple <queryGenome.fa> <query.gff> <queryId> <out.txt> <sub1Genome.fa> <sub1.gff> [<sub2Genome.fa> <sub2.gff> ...] [--leftEdge N --rightEdge N --expand N --threads N]` | 多基因组伪共线性区块（第52引擎）：1 query + N subject |
| 79 | `findblockdual` | `用法: findblockdual <queryGenome.fa> <query.gff> <subjectGenome.fa> <subject.gff> <queryId> <out.txt> [--leftEdge N --rightEdge N --expand N --threads N --evalue X --minIdentity X --bestHit N]` | ⚠️ 内部 blastp 找同源，需真实双基因组数据验证（第50引擎） |
| 80 | `visualizeblock` | `用法: visualizeblock <inBlockOut> <out.pdf> [--labels "Genome1,Genome2"]` | inBlockOut: FindBlockDual 输出（findblockdual 命令产物） |
| 81 | `marker` | `用法: marker <MarkerDist|MarkerFilter|SampleDist|BigMarkerRandomDesign> <inMarker> <out> [args...]` | inMarker: 标记 0-1 矩阵（行=locus，列=样本，tab 分隔，首行列名/首列 locus 名） |
| 82 | `dehist` | `用法: dehist <deg.txt> <out> [width] [height]` | deg.txt: 每行至少 3 列（tab）：任意ID\t值1\t值2（值1/值2 两样本数值，比较大小分左右直方图） |
| 83 | `msy` | `用法: msy <simplifiedGff.pos> <links.txt> <chrLayout.txt> <out> [width] [height]` | simplifiedGff.pos: Chr\tGeneName\tStart\tEnd\t[displayChr]\t[displayName]（多物种共线性区域/基因） |
| 84 | `venn5` | `用法: venn5 <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> [labelA-E]` | 每个 setN.txt: 每行一个成员 ID |
| 85 | `venn6` | `用法: venn6 <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> <setF.txt> [labelA-F]` | 引擎: Venn6（setInArrA~F + setOutGraph + getVennGraph） |
| 86 | `microsyn` | `用法: microsyn <gxf1> <gxf2> <collinearity> <out> [--chr1 C --start1 S --end1 E] [--chr2 C --start2 S --end2 E] [--highlight1 c:s:e] [--highlight2 c:s:e]` | gxf1/gxf2: 两物种 GFF/GXF 注释 |
| 87 | `dualsyn` | `用法: dualsyn <simplifiedGff> <collinearity> <out> [--chr1 "1,2"] [--chr2 "3,4"] [--rows N] [--gap N]` | simplifiedGff: Chr\tGeneName\tStart\tEnd（染色体名必须数字） |
| 88 | `multisyn` | `用法: multisyn <gxf.lst> <collinear.lst> <out> [--genes idlist.txt]` | gxf.lst: 每行一个 GXF/GFF 注释（染色体名须数字） |

### 各命令详细注释

#### `motif`

- 用法: motif <meme.xml> <idList.txt> <outFile> [width] [height]

#### `genelocation`

- 用法: genelocation --ChrLen <chrlen> --FeaturePos <pos> --OutGraph <out> [--FeatureColor <map>]

#### `dotplot`

- 用法: dotplot --inGff <gff> --genePair <pairs> --chrLayout <layout> --outGraph <out>
- 简化GFF: Chr\tGene\tStart\tEnd\tStrand ; chrLayout: Genome: Chr1 Chr2...

#### `circos`

- 用法: circos <chrLen.txt> <link.txt> <genePos.txt> <outFile> [w] [h]
- link.txt/genePos.txt 可空文件

#### `pca`

- 用法: pca <expr.matrix.tsv> <out> [row|col] [scale] [w] [h]
- 通用反射桥 GenericCli 驱动 PCAanalysis（doPCA+postGraph）

#### `generic`

- 用法: generic <engineClass> <method[+method2]> <out> [--set field value ...] [--width N] [--height N]
- 通用反射桥：驱动任意 TBtools 引擎（setter + plot/process/postGraph + save2Graph）
- 例: generic biocjava.bioDoer.JIGplotToolkit.PCAanalysis.PCAanalysis doPCA+postGraph out.svg --set inTabFile expr.tsv --set rowName true --set colName true --set processDirect Rows

#### `gfa2fa`

- 用法: gfa2fa <in.gfa> <out.fa>   # GFA 组装图 → FASTA（第91引擎，GFAtoFasta）

#### `qpcr`

- 用法: qpcr <data.txt> <out> [w] [h]   (data: name\tmean\tsd)

#### `hclust`

- 用法: hclust <expr.matrix.tsv> <out.nwk> [distMethod] [clusterMethod]

#### `volcano`

- 用法: volcano <deg.txt> <outFile> [pvalCutoff] [fcCutoff] [w] [h]
- deg.txt: GeneID\tLog2FC\tpvalue
- 通用反射桥 GenericCli 驱动 vocanoPlot.show()

#### `upset`

- 用法: upset <sets.txt> <outFile> [w] [h]
- sets.txt: 每行 "集合名\t成员1\t成员2..."（tab 分隔）

#### `msa`

- 用法: msa <aligned.fasta> <outFile> [padding]
- 尺寸按子面板自动计算，勿传 w/h

#### `genelocgff`

- 用法: genelocgff <gff3> <idList> <out> [--chrLen len.tsv] [--rename r.tsv] [--pairs p.tsv] [--color c.tsv] [--rankedChr list] [--onlyMapped true|false] [--showLabel true|false]

#### `tree`

- 用法: tree <treeMeta.config> <out> [pad]
- 配置格式见 TreeCli.java 注释（[TYPE]:Tree + [NEWICK] + [setting] + 可选 [TYPE]:TextAnno/HeatMap/BarPlot/... 轨道）

#### `phylotree`

- 用法: phylotree <in.nwk> <out> [vertical] [width] [height]
- PhyloTreeView 系统发育树视图（08/31 攻下，纠正「需 TreeTab」误判）
- build() 直接吃 newick，内部自动算坐标；支持枝长/Cladogram 自动降级/坐标轴

#### `unrooted`

- 用法: unrooted <in.nwk> <out> [layout] [width] [height] [iterations]
- 无根树可视化（引擎 115，unrootedtree 独立引擎，非 UnrootedTreeViz）
- layout: Circular|Radial|Force-Directed|Equal Angle|N-Body|Equal-Daylight（默认 Circular）

#### `violin`

- 用法: violin <in.tsv> <out> [width] [height]
- 独立小提琴图（引擎 116，ViolinPlot.generate()；仅 SVG/PDF）
- in.tsv: 组别\t值（每行一个观测）

#### `barplotter`

- 用法: barplotter -g <gff> -s <synteny> -c <ctl> -o <out.png>
- 合成共线性柱状图（引擎 117，bar_plotter.main1——main 是死代码）
- gff: chr\tgene\tend；synteny: MCScanX 式 collinearity；ctl: 4 行 xdim/ydim/xchr/ychr

#### `findpath`

- 用法: findpath --inGffArr <gff1,gff2,...> --inGenePairs <pairs> --inRegion <geneID> [--flankGeneNum N] [--highlightGene ID] --outGraph <out>
- 共线性基因块进化路径（引擎 118，FindPathBySynteny.main1；main 硬编码演示）
- gff 需简化格式 chr\tgene\tstart\tend\tstrand；genepairs 每行 geneA\tgeneB

#### `mcscanx`

- 用法: mcscanx <gff> <blast> <outPrefix> [--html]   # 共线性检测
- mcscanx classify <gff> <blast> <outPrefix>  # 重复基因分类（WGD/tandem/proximal/dispersed/singleton）
- 纯 Java MCScanX（工具 72，org.mcscanx.api.MCScanXAPI）——无需外部 MCScanX 二进制
- ⚠️ 与外部 MCScanX 输出 100% 一致验证（GRAS Co_wgd：334 blocks cmp 全同）；
- classify 的 String API 有 bug（validate 需 collinearityFile）→ 桥用完整 InputFiles/OutputOptions API

#### `degramdom`

- 用法: degramdom <in.tsv> [out.nwk]
- 亲子表构建 Newick 树（工具 73，BuildDegramdomFromTable.process；main 硬编码演示）
- in.tsv: 子节点\t父节点\t枝长（每行一个关系）

#### `sambamcov`

- 用法: sambamcov <in.bam> <out.tsv> [binSize] [countMode]
- BAM bin 覆盖统计（工具 74，SamBamBINCov.process——main 硬编码演示）
- binSize: 窗口 bp（默认 1000）；countMode: Overlap|StartPos|EndPos（默认 Overlap）

#### `bamindex`

- 用法: bamindex <in.sorted.bam> [out.bai]
- BAM 索引创建（工具 75，BAMIndexCreater.process——main 硬编码演示）

#### `bamsort`

- 用法: bamsort <in.bam> <out.bam> [sortOrder] [tmpDir]
- BAM 排序（工具 76，SAMBAMSorter.process——main 硬编码演示）
- sortOrder: coordinate|queryname|unsorted|duplicate（默认 coordinate）

#### `onesteptree`

- 用法: onesteptree --inPepFie <in.pep> --outFilePrefix <outDir> [--bbTime N] [--clean true|false]
- 一步法 ML 系统发育树（引擎 119，OneStepMLTree——pep→muscle→trimal→IQ-TREE MFP+UFboot）
- 需系统 muscle+iqtree；⚠️ --bbTime ≥1000（iqtree 限制）；序列需 ≥4 条唯一

#### `simplehmmscan`

- 用法: simplehmmscan <pfamA.hmm> <target.pep> <idList.txt> <out.txt>
- Pfam 域快速扫描（工具 83，simpleHmmscan——main 硬编码演示 → setter+process，调系统 hmmsearch）
- ⚠️ 需 Pfam-A.hmm 数据库（本地 ~/.eggnog-mapper/data/pfam/）；idList 每行一个 Pfam NAME（如 GRAS）

#### `colorscheme`

- 用法: colorscheme <in.tab> <out.tab> <refColIndex(1-based)>
- 表格分组着色（工具 86，ColorSchemeGenerator.process——main 硬编码演示）
- 输出 = 原表 + RGB 颜色列（分组键相同者同色组标记）

#### `regiondepth`

- 用法: regiondepth <in.sam> <region> <out.depth> [scaleFactor]
- SAM 区域覆盖深度（工具 88，CalcRegionDepth.init+processRegion——main 硬编码演示）
- region: ChrID:Start-End；输出每碱基覆盖深度

#### `markertools`

- 用法: markertools <filter|dist|sampledist> <in.marker.tab> [maxPoint]
- 分子标记分析组（工具 89：MarkerFilter minor allele / MarkerDist / SampleDist——main 均硬编码）
- in.marker.tab: 0/1 标记矩阵（行=样本，列=标记，首行列名+首列行名）

#### `amazingmeta`

- 用法: amazingmeta <meme.xml> <newick.treefile> <out.svg|png|pdf> [seqLen.txt] [geneRename.txt]
- Amazing Meta Plot（引擎 120，DrawAmazingMetaPlot——进化树+Motif模式+基因结构+蛋白域组合图）
- ⚠️ plot() 内部 JFrame 显示 → Window 反射提取 JIGBasePanel 后 save2SVG/PNG/PDF

#### `cddmotif`

- 用法: cddmotif <cdd.hitdata.txt> <in.fasta> <out.svg|png|pdf> [newick.treefile]
- CDD 保守域模式图（引擎 121，DrawMotifPatternFromCDDResult.postGraph——GRAS hitdata 真实验证 56 基因全匹配）
- hitdata: NCBI Batch CD-search hitsConcise；⚠️ fasta 需含 hitdata 全部基因 ID（否则 NPE）

#### `seqlentrack`

- 用法: seqlentrack <seqlen.txt> <out.svg|png|pdf> [newick.treefile]
- 序列长度骨架图（引擎 122，DrawSequenceFromSeqLenInfo——AmazingMetaPlot CDD 面板底层）
- seqlen.txt: gene\tlength（# 跳过）；GRAS 53 基因验证

#### `pfammotif`

- 用法: pfammotif <pfamscan.txt> <in.fasta> <out.svg|png|pdf> [newick.treefile]
- Pfam 保守域模式图（引擎 123，DrawMotifPatternFromPfamResult——委托 PfamDomainHitsTableParser）
- pfamscan.txt: PfamScan 16 列（seqid alnS alnE envS envE hmmAcc hmmName type hmmS hmmE hmmLen bitscore evalue ...）
- ⚠️ 可用 hmmscan --domtblout 转 PfamScan 格式；fasta 需含全部基因

#### `pep2codon`

- 用法: pep2codon <cds.fa> <pep.aln.fa> <codon.aln.out>
- 蛋白比对回译密码子比对（工具 91，pepAln2CodonAln.transformat 静态方法——Ka/Ks 刚需）
- ⚠️ CDS ID 需与 pep.aln 一致；gap 正确回译为 --- 密码子

#### `mast2tab`

- 用法: mast2tab <mast|meme.xml> <out.tab>
- MEME Suite XML→表格（工具 93，MEMESuiteXMLtoTab——main 全硬编码 → setter+process）
- 真实拟南芥 mast.xml 554 行验证（SeqID/SeqLength/MotifId/Start/Length）

#### `qpcrproc`

- 用法: qpcrproc <in.qpcr.tab> <out.xls>
- qPCR 相对表达分析（工具 97，SimpleQPCRProcessser——2^-ΔΔCt，Sample\tRefCt\tExpCt）
- ⚠️ 输入格式: Sample\t内参Ct\t目标Ct；同样本多行求均值/SD

#### `filesplit`

- 用法: filesplit <inFile> <numParts>
- 文件按份数分割（工具 99，FileLineSplit.Split 静态方法）

#### `memerun`

- 用法: memerun <in.fasta> <workingDir> [--motif N] [--minW N] [--maxW N] [--evalue X] [--mode ...]
- 一步法 MEME motif 发现（工具 100，QuickRunMEME——调系统 meme）
- ⚠️ 输出在 workingDir/meme_out/meme.xml

#### `mastrun`

- 用法: mastrun <meme.xml> <seq.fasta> <workingDir> [--motifs M] [--seqEvalue X] [--motifPvalue X] [--other "..."]
- 一步法 MAST motif 扫描（工具 101，QuickRunMAST——调系统 mast；与 memerun 配套）
- 输出 workingDir/mast_out/mast.{txt,html,xml}

#### `mggxf`

- 用法: mggxf <inGenePair|blastTab6> <in.simplified.gff> <out.LinkedRegion> [GenePair|BlastTab6]
- 多 GFF 视图格式转换（工具 103，FormatTranformerForMultipleGffViewer——GenePair/BlastTab6→LinkedRegion）

#### `gsadiag`

- 用法: gsadiag <in.fixed.gff3> <out.stat.xls> [genome.fasta] [relax] [--checkUTR]
- 基因结构快速诊断（工具 94，GsaQuickDiagnosis——相位验证+长度异常+可选编码潜能检查）
- 真实 GRAS GFF 验证：0 注释问题；注释质控刚需

#### `gxfsort`

- 用法: gxfsort <in.gff3|gtf> <out.sorted>
- GFF 按染色体+坐标排序（工具 95，GXFSort.sortByPretty——注释预处理刚需）
- 真实 GRAS GFF 385 行排序验证（HiC_scaffold_3→1）

#### `gxffilter`

- 用法: gxffilter <in.gff3|gtf> <idList.txt> <out.gff3|gtf>
- GFF 按 ID 列表过滤（工具 96，GXFfilter.setIDList+process——基因家族子注释提取刚需）
- 保留 ID 列表中基因/转录本及其子特征；真实 GRAS 3 基因→10 特征行验证

#### `annocompare`

- 用法: annocompare <before.gff3> <after.gff3> <outDir> [runName] [reciprocalOverlap] [boundaryTol] [cdsChangePct] [utrChangePct] [geneScope] [overlapMode]
- 注释版本对比管线：对比同一基因组前后两版注释，产 change_summary.csv/change_log.csv/BED +
- Curation 图 + ABCD 四图（PNG/PDF/SVG）+ 单物种 ABCD 表（08/31 攻下）

#### `genedensity`

- 用法: genedensity <in.gff3> <out.tsv> [binSize]
- 基因密度谱：按窗口统计每染色体/contig 基因数（基因组轨道/密度分析）

#### `seqconvert`

- 用法: seqconvert -i <in> -o <out> -iF <fmt> -oF <fmt>
- 序列格式转换（main1 入口；fmt: fasta|clustal|MEGA|nexus|PAML|phylip）

#### `trimmsa`

- 用法: trimmsa <in.aln.fa> <out.aln.fa> [ratio]
- MSA 修剪（按列保留率），main 硬编码 → 桥 setter+process

#### `heatmap2`

- 用法: heatmap2 <expr.matrix.tsv> <out> [options]
- 矩阵: 首列基因名 + 列名表头，其余数值。options 见 HeatmapCli.java 注释（--log2 --rowScale --clusterRow/Col --rowGroup/ColGroup --transpose 等）

#### `supercircos`

- 用法: supercircos <config.cfg> <out> [width] [height]
- 配置格式见 SuperCircosCli.java 注释（[chrLen] [link] [gene] [track] 等行导向配置）
- track: [track] <Tile|Triangle|HeatMap|Point|Line|Bar|Arrow> <file> <startPos> <endPos> <c1> <c2> <c3> <binSize> [fillColor] [drawColor]

#### `barplot`

- 用法: barplot <enrichment.tsv> <out> <termCol> <pvalCol> [classCol] [maxTerms] [xlab] [ylab] [mode]
- mode: Normal|TextOnLeft|BarOnLeft

#### `pafviz`

- 用法: pafviz <in.paf> <out> [graphSize] [colorMode] [switchQT] [minAlnLen] [rcColor]
- colorMode: Target|Query|None

#### `admixture`

- 用法: admixture <qFiles.lst> <out> [sampleIDFile] [groupFile] [sortMode] [width] [height] [panelInterval]
- sortMode: Qraito|Lexical|None

#### `groupedbar`

- 用法: groupedbar <data.tsv> <out> [plotType] [errorBarType] [hasHeader] [title] [--options]
- plotType: BAR_ERROR|BOXPLOT|VIOLIN|SWARM
- errorBarType: SEM|SD|CI95
- data.tsv: Group\tValue (每组至少 2 重复)
- --options: --width --height --fontSize --barWidth --boxWidth --violinWidth --showOutliers --noOutliers --noNs --homoscedastic --yMin --yMax --pStar --pStar2 --pStar3 --color <i> <r,g,b> --order ALPHA

#### `layoutheatmap`

- 用法: layoutheatmap <layout.tsv> <expr.tsv> <out> [--options]
- layout.tsv: 样本名矩阵（TSV，空格用 NA）
- --options: --cellWidth --cellHeight --yGap --log2 --log10 --rowScale --minColor --midColor --maxColor --nanColor --noLegend --noValue --rename --topLeft

#### `cubeheatmap`

- 用法: cubeheatmap <expr.tsv> <group.tsv> <out> [--log10 --minColor r,g,b --midColor r,g,b --maxColor r,g,b]
- expr.tsv: 表达矩阵（首列基因名 + 样本名表头）
- group.tsv: Sample\tFirstDim\tSecondDim（三面立方体热图）

#### `rnaplot`

- 用法: rnaplot <seq.fa|rawSeq> <out> [--colorMap "seq1=R,G,B;seq2=R,G,B"] [--interactive false]
- RNA 二级结构图（第111引擎，RNAplotAdvance，需 RNAfold/RNAplot 可执行）
- ⚠️ 本机 RNAplot 2.7 不读 stdin 管道（generatePlotPsFile 失败）→ 桥自己 RNAplot -i 生成 EPS + transformat 解析

#### `circlegene`

- 用法: circlegene <gff> <geneID.txt> <out> [--rename f --link f --rankedChr f --allChr --graphSize N --startAngle N --endAngle N --chrFill r,g,b --chrLabelColor r,g,b]
- geneID.txt: mRNA ID 每行一个（可第二列 1/0 控制颜色）
- --link: 基因对文件 (GeneA\tGeneB\t[r,g,b]) 绘制共线性链接

#### `genestructure`

- 用法: genestructure <input.gff> <idList.txt> <outFile> [genome.fa] [width] [height]

#### `seqlogo`

- 用法: seqlogo <seq.fa|seq.txt> <out.svg/png> [--scaleIC true|false] [--showPos] [--startPos N] [--borderColor R,G,B] [--borderSize N] [--onlyBorder] [--xInterval N] [--yInterval N]
- seq 输入: FASTA 或 纯文本（每行一条序列，等长已比对）
- 引擎: biocjava.bioDoer.seqLogo.makeSeqLogo（自带 ArgsParser，开箱即用）

#### `peaktss`

- 用法: peaktss <gxf> <macs2_peak.xls> <out.svg/png> [--dist N] [--bin N] [--color]
- gxf: 基因注释（GFF/GXF，mRNA 行定义 TSS）
- macs2_peak.xls: MACS2 peaks 表格（chr/start/end 列）
- --dist: TSS 上下游窗口 bp（默认 2000）
- 引擎: biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakTssHeatMap（自带 CLI，开箱即用）

#### `peakdist`

- 用法: peakdist <chrLen.tsv> <macs2_peak.xls> <out> [--chrHeight H] [--topLenRank N] [--width W] [--height H]
- chrLen.tsv: Chr\tLength（染色体长度）
- macs2_peak.xls: MACS2 peaks 表格（chr/start/end 列）
- 引擎: peakDistribution（process() 是 private，反射调用）

#### `peakanno`

- 用法: peakanno <gxf> <macs2_peak.xls> <out.tsv> [--dist N]
- macs2_peak.xls: MACS2 标准 peak 格式（chr start end length abs_summit ...）
- 引擎: peakAnno（自带 ArgsParser，开箱即用；peak 坐标列必须标准 MACS2 格式）

#### `microgenome`

- 用法: microgenome <inGBK> <anno.tsv> <out> [micro|macro]
- inGBK: GenBank 质体/质粒基因组文件
- anno.tsv: 注释 5 列（startPos\tendPos\tname\t[+|-]\ttype）
- ⚠️ type 至少 2 种不同类型（CDS/RNA/tRNA）——单类型触发引擎 ColorMapper middleColor null NPE
- 引擎: MicroGenomeAnnotationCircosPlot（自带 ArgsParser，质体基因组环形图+GC轨道）

#### `gel`

- 用法: gel <FragmentRangeArr> <LaneLabels> <MarkerRange> <out>
- FragmentRangeArr: 分号分隔泳道/逗号分隔片段，如 "798;1233,228;1688,1598"
- LaneLabels: 泳道标签，如 "DL2000,Cultivar_1,Cultivar_2,Cultivar_3"
- MarkerRange: marker 范围，如 "2000,1500,1000,750,500,250,100"
- 引擎: GelImage.Marker（自带 ArgsParser，PCR 产物虚拟凝胶电泳图）

#### `gfa`

- 用法: gfa <in.gfa> <out> [width] [height]
- GFA 格式: S 行=节点（S\tname\tseq），L 行=边（L\tfrom\tstrand\tto\tstrand\toverlap）
- 引擎: VizGFA（GFAGraphLayout + VizGFA.visualize，组装图可视化）

#### `pafcomp`

- 用法: pafcomp --inPaf <paf> --outGraph <out> [--colorMode Target|Query|None] [--size N] [--minLen N]
- PAF 基因组比较图（⚠️ 入口是 main1 非 main）

#### `pafref`

- 用法: pafref --inPaf <paf> --outTab <out.tsv>
- PAF 参考碱基覆盖计算（minimap2 -c --cs 输出）

#### `colorscheme`

- 用法: colorscheme <inTab> <outTab> <refColIndex>
- inTab: tab 分隔表；refColIndex: 从 0 开始，取该列做配色 key（去重）
- outTab: 输出颜色代码表（第41引擎）

#### `distance`

- 用法: distance <in.tsv> <col1> <col2> <euclidean|pearson|pearsonDist>
- in.tsv: tab 分隔表；col1/col2: 列索引（从0开始）；输出两列数值的距离/相关系数（第42引擎）

#### `mountain`

- 用法: mountain <fold.txt> <out.tsv>
- fold.txt: RNA 二级结构折叠字符串（() 和 .）；输出每碱基山峰高度（第43引擎）

#### `pileup`

- 用法: pileup <blast.xml> <out.svg> [--query NAME]
- blast.xml: BLAST+ XML 输出（-outfmt 5）；画 query 的 hits pile-up 图（第44引擎）
- ⚠️ 绕过了引擎 GUI 弹窗，自动选第一个 query

#### `plotrna`

- 用法: plotrna <genomeFA> <region> <SAM> [--directPDF out.pdf]
- region: 'chr:startPos-endPos'；SAM: 比对 reads；画基因组区域覆盖度+RNA结构图（第45引擎）
- ⚠️ 只支持 PDF 输出（--directPDF）；不带该参数会弹窗

#### `bamstate`

- 用法: bamstate <out.tsv> <gff3> <bam1> [<bam2> ...]
- gff3: 标准 GFF3（gene/mRNA 特征）；bam: 比对 BAM（需 samtools 建索引）
- out.tsv: 每 BAM 的 coverage 比例/depth/总基因数/表达基因数（第57引擎）
- 示例: tbplot.sh bamstate out.tsv Co.gff3 SRR1.bam SRR2.bam

#### `preparespecies`

- 用法: preparespecies <prefix> <inGenome.fa> <inGFF> <outGenome.fa> <outGFF>
- 给基因组+GFF 加物种前缀（seqid + ID）——TBtools 多物种比较数据准备（第56引擎）
- 工作流: preparespecies → findblockdual/multiple → visualizeblock
- ⚠️ 大数据基因组全量重写耗时（3GB 级约 10-20 分钟）

#### `partitionconflict`

- 用法: partitionconflict <inConflictFreq.tsv> <polyPoid> <outCluster>
- inConflictFreq.tsv: conflictpaf 输出（contigA\tcontigB\tcount）
- polyPoid: 目标倍性；outCluster: 同源群分区（第54引擎）
- 链式: conflictpaf → partitionconflict（冲突检测 → 多倍体同源群分区）

#### `mirnatarget`

- 用法: mirnatarget <mirna.fa> <target.fa> <out.tsv> [--evalue X] [--threads N] [--scoreCutOff N] [--maxMismatch N]
- mirna.fa: miRNA 序列（建议每轮一条或一族）；target.fa: 转录本/基因组靶标
- out.tsv: 靶标表（miRNA target strand beg end score miRNAseq targetseq E bits）
- 完整管线: ssearch36 -i -m 10 → TargetSoEngine（TBtools 官方参数）
- ⚠️ 需 ssearch36 在 PATH（apt install fasta 或本地编译）
- Step 1: ssearch36 官方参数
- Step 2: TargetSoEngine 打分

#### `conflictpaf`

- 用法: conflictpaf <in.paf> <out.tsv> [binSize]
- in.paf: 基因组比对 PAF（minimap2/minigraph）
- out.tsv: contig 对冲突计数（query target bin冲突数）——组装冲突检测（第53引擎）

#### `findblockmultiple`

- 用法: findblockmultiple <queryGenome.fa> <query.gff> <queryId> <out.txt> <sub1Genome.fa> <sub1.gff> [<sub2Genome.fa> <sub2.gff> ...] [--leftEdge N --rightEdge N --expand N --threads N]
- 多基因组伪共线性区块（第52引擎）：1 query + N subject
- ⚠️ 大数据引擎：必须 -Djava.io.tmpdir=<磁盘>（/tmp tmpfs 16G 会被 3GB 基因组撑爆）

#### `findblockdual`

- 用法: findblockdual <queryGenome.fa> <query.gff> <subjectGenome.fa> <subject.gff> <queryId> <out.txt> [--leftEdge N --rightEdge N --expand N --threads N --evalue X --minIdentity X --bestHit N]
- ⚠️ 内部 blastp 找同源，需真实双基因组数据验证（第50引擎）

#### `visualizeblock`

- 用法: visualizeblock <inBlockOut> <out.pdf> [--labels "Genome1,Genome2"]
- inBlockOut: FindBlockDual 输出（findblockdual 命令产物）
- out.pdf: 输出 PDF（引擎只支持 PDF）
- --labels: 每行基因组标签（默认 Genome1/Genome2/...）

#### `marker`

- 用法: marker <MarkerDist|MarkerFilter|SampleDist|BigMarkerRandomDesign> <inMarker> <out> [args...]
- inMarker: 标记 0-1 矩阵（行=locus，列=样本，tab 分隔，首行列名/首列 locus 名）
- MarkerDist   : 找最大判别力 marker 组合 [--maxPoint N]
- MarkerFilter : 每样本 marker 计数（结果写 out）
- SampleDist   : marker 间成对距离（结果写 out）
- BigMarkerRandomDesign: 随机抽样找标记组合（无 out，直接打印到 stdout）
- [--targetMarkerNum N --numberOfTest N --batchSize N --numberOfThreads N]

#### `dehist`

- 用法: dehist <deg.txt> <out> [width] [height]
- deg.txt: 每行至少 3 列（tab）：任意ID\t值1\t值2（值1/值2 两样本数值，比较大小分左右直方图）
- # 开头行跳过
- 引擎: DiffExpDualHistPlot.process(File) 返回 JIGSubPanel[]（差异表达双直方图）

#### `msy`

- 用法: msy <simplifiedGff.pos> <links.txt> <chrLayout.txt> <out> [width] [height]
- simplifiedGff.pos: Chr\tGeneName\tStart\tEnd\t[displayChr]\t[displayName]（多物种共线性区域/基因）
- links.txt: GeneA\tGeneB\t[r,g,b]（跨物种同源基因对）
- chrLayout.txt: 基因组名:\s*染色体列表（如 GenomeA: A_Chr1 A_Chr2）；#DISPLAY_ORIG_CHR: 前缀行定义显示名
- 引擎: MultipleSpeciesSyteny.plot() 返回 JIGSubPanel（多物种微共线性图）

#### `venn5`

- 用法: venn5 <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> [labelA-E]
- 每个 setN.txt: 每行一个成员 ID
- 引擎: Venn5（setInArrA~E + setOutGraph + getVennGraph）

#### `venn6`

- 用法: venn6 <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> <setF.txt> [labelA-F]
- 引擎: Venn6（setInArrA~F + setOutGraph + getVennGraph）

#### `microsyn`

- 用法: microsyn <gxf1> <gxf2> <collinearity> <out> [--chr1 C --start1 S --end1 E] [--chr2 C --start2 S --end2 E] [--highlight1 c:s:e] [--highlight2 c:s:e]
- gxf1/gxf2: 两物种 GFF/GXF 注释
- collinearity: MCScanX 输出（*.collinearity）
- 引擎: MicroSyntenicAdvance（窗口遍历方案）双基因组微共线性图

#### `dualsyn`

- 用法: dualsyn <simplifiedGff> <collinearity> <out> [--chr1 "1,2"] [--chr2 "3,4"] [--rows N] [--gap N]
- simplifiedGff: Chr\tGeneName\tStart\tEnd（染色体名必须数字）
- collinearity: MCScanX 输出（*.collinearity）
- 引擎: DualSyntenyPlotterAdvance（旧 JJplot2 框架，反射扫描窗口树提取 GUI 实例保存）

#### `multisyn`

- 用法: multisyn <gxf.lst> <collinear.lst> <out> [--genes idlist.txt]
- gxf.lst: 每行一个 GXF/GFF 注释（染色体名须数字）
- collinear.lst: 每行一个 MCScanX collinearity（与 GXF 配对）
- --genes: 高亮基因 ID 列表（可选，缺省自动从第一个 GXF 提取）
- 引擎: SeveralSpeciesMicroSyntenicAnalysisAdvance（多物种微共线性，需真实数据验证输出）

## 三、CLI 工具 tbtools tool（82）

```bash
tbtools tool <工具名> [参数...]   # 工具名 = 引擎类名（大小写敏感）
tbtools tool list                 # 列出全部
```

每个工具都是 TBtools 引擎的**命令行直连**（自带 ArgsParser），参数格式与引擎 GUI 一致：`--参数名 值`。

> 参数名查法：`java -cp $TBTOOLS_JAR <完整类名>` 无参数运行会打印 `[Usage]` 参数表（含默认值），或参考下方桥 Javadoc。

共 82 个工具，按功能分类：

### BLAST（5）

| 工具名 | 引擎类 |
|:-------|:-------|
| `ReciprocalBlast` | `biocjava.bioDoer.BLAST.ReciprocalBlast.ReciprocalBlast` |
| `autoMakeBlastDb` | `biocjava.bioDoer.BLAST.makeblastdb` |
| `autoRemoteBlast` | `biocjava.bioDoer.BLAST.remoteblast` |
| `quickGeneFamilyIdentification` | `biocjava.bioDoer.BLAST.ReciprocalBlast.QuickGeneFamilyIdentification` |
| `regionBlast` | `biocjava.bioDoer.BLAST.wholeGenomeBlastN.regionBlast` |

### FASTA/序列（16）

| 工具名 | 引擎类 |
|:-------|:-------|
| `Fasta36m10toTable` | `biocjava.bioIO.FastaAligner.Fasta36m10toTable` |
| `FastaIDRenamer` | `biocjava.bioIO.FastX.FastaIndex.FastaIDRenamer` |
| `FastaIDSimplifier` | `biocjava.bioIO.FastX.FastaIndex.FastaIDSimplifier` |
| `FastaLongestRepresentater` | `biocjava.bioIO.FastX.FastaIndex.FastaLongestRepresentater` |
| `downLoadNCBIFasta` | `biocjava.bioWeb.DownLoadNCBIFasta` |
| `emblToFasta` | `biocjava.bioIO.Embl.emblToFasta` |
| `extractFasta` | `biocjava.bioDoer.Fasta.ExtractFasta` |
| `extractFastaSub` | `biocjava.bioDoer.Fasta.ExtractFastaSubseq` |
| `fastaFragmenter` | `biocjava.bioIO.FastX.FastaIndex.Fragment.FastaFragmenter` |
| `fastaIDAppender` | `biocjava.bioIO.FastX.FastaIndex.FastaIDAppender` |
| `fastqAndFasta` | `biocjava.bioDoer.LinuxPipe.FastqAndFasta` |
| `makeFastaIndex` | `biocjava.bioIO.FastX.FastaIndex.MakeFastaIndex` |
| `quickLocateSeqPattern` | `biocjava.bioIO.FastX.QuickLocateSeqPattern` |
| `quickSplitFasta` | `biocjava.bioIO.FastX.FastaIndex.QuickSpiltFasta` |
| `ssrMiner` | `biocjava.bioIO.FastX.FastaIndex.SSRminer` |
| `statFasta` | `biocjava.bioIO.FastX.FastaIndex.QuickStatFasta` |

### FASTQ/sRNA（8）

| 工具名 | 引擎类 |
|:-------|:-------|
| `DecodeIlluminaFqPool` | `biocjava.bioDoer.Fastq.DecodeIlluminaFqPool` |
| `fastqParallelSubBest` | `biocjava.bioDoer.Fastq.FastqParallelSubBest` |
| `fastqParallelTrimmer` | `biocjava.bioDoer.Fastq.FastqParallelTrimmer` |
| `sRNAReadTrimmer` | `biocjava.sRNA.Tools.sRNAReadTrimmer` |
| `sRNAseqAdaperRemover` | `biocjava.sRNA.Tools.sRNAseqAdaperRemover` |
| `sRNAseqCollasper` | `biocjava.sRNA.Tools.sRNAseqCollasper` |
| `sRNAseqDeCollasper` | `biocjava.sRNA.Tools.sRNAseqDeCollasper` |
| `sRNAseqReadLenStat` | `biocjava.sRNA.Tools.sRNAseqReadLenStat` |

### GO/KEGG（2）

| 工具名 | 引擎类 |
|:-------|:-------|
| `goEnrichMerge` | `biocjava.bioDoer.JIGplotToolkit.EnrichmentAnalysisGraph.GOEnrichmentMergeBubble` |
| `keggEnrichment` | `biocjava.bioDoer.Kegg.AdvancedForEnrichment.KeggEnrichment` |

### GWAS/VCF（3）

| 工具名 | 引擎类 |
|:-------|:-------|
| `mimicVqsr` | `biocjava.bioDoer.GWAS.MimicVqsrCutoffFind` |
| `vcfAddID` | `biocjava.bioDoer.GWAS.VCFAddID` |
| `vcfBinCount` | `biocjava.bioIO.HTSData.VCF.VCFBINCount` |

### GXF/GFF 注释（7）

| 工具名 | 引擎类 |
|:-------|:-------|
| `ExtractFeaturefromGFF3andGenome` | `biocjava.bioIO.GFF.ExtractFeaturefromGFF3andGenome` |
| `GXFOverlaper` | `biocjava.bioDoer.GXFUtils.GXFOverlaper` |
| `OverlapGeneModels` | `biocjava.bioIO.GXF.gxfTree.OverlapGeneModels` |
| `RegionGXFOverlapAnnotation` | `biocjava.bioDoer.GXFUtils.RegionGXFOverlapAnnotation` |
| `extractFeatureFromGTF` | `biocjava.bioIO.GTF.ExtractFeaturefromGTFandGenome` |
| `extractGff3Region` | `biocjava.bioIO.GFF.ExtractGff3Region` |
| `gffCdsPhaseCorrector` | `biocjava.bioDoer.GXFUtils.GffCdsPhase.GffCdsPhaseCorrector` |

### ORF/翻译（3）

| 工具名 | 引擎类 |
|:-------|:-------|
| `getLongestCompleteORF` | `biocjava.bioIO.ORF.ORF` |
| `getLongestORF` | `biocjava.bioIO.ORF.GetLongestORF` |
| `translater` | `biocjava.bioIO.ORF.Translater` |

### miRNA/RNA（8）

| 工具名 | 引擎类 |
|:-------|:-------|
| `FoldStructureStater` | `biocjava.bioIO.RNAfold.FoldStructureStater` |
| `MIRPrediionResultStat` | `biocjava.bioDoer.miRNA.MIRPrediionResultStat` |
| `OneStepMirGraph` | `biocjava.bioIO.RNAfold.OneStepMirGraph` |
| `PredictMirSTAR` | `biocjava.bioIO.RNAfold.PredictMirSTAR` |
| `mirIdentifierBasedOnTargetSo` | `biocjava.bioDoer.miRNA.MIRidentifierBasedOnTargetSoResult` |
| `plotRNAfoldloci` | `biocjava.bioDoer.JIGplotToolkit.miRCoverage.PlotRNAfold` |
| `target2TablePipe` | `biocjava.bioDoer.miRNA.Target2TablePipe` |
| `targetSoPipe` | `biocjava.bioDoer.miRNA.TargetSoPipe` |

### 共线性（2）

| 工具名 | 引擎类 |
|:-------|:-------|
| `collinearityToRegion` | `biocjava.bioDoer.ComparativeGenomics.MCScanX.CollinearityToRegion` |
| `prepareFileFromMCScanXtoTBtools` | `biocjava.bioDoer.JIGplotToolkit.Synteny.PrepareFileFromMCScanXtoTBtools` |

### 其他（7）

| 工具名 | 引擎类 |
|:-------|:-------|
| `GoCompareBar` | `biocjava.bioDoer.GeneOntology.Grapher.GoCompare` |
| `RNAplotAdvance` | `biocjava.bioDoer.JIGplotToolkit.miRCoverage.RNAplotAdvance` |
| `bigMarkerRandomDesign` | `biocjava.bioDoer.markerDesign.BigMarkerRandomDesign` |
| `findBestForkerRootTree` | `biocjava.bioDoer.JIGplotToolkit.newickParser.FindBestForkerRootTree` |
| `goAnnoPipe` | `biocjava.bioDoer.GeneOntology.Annotation.GoAnnoPipe` |
| `pafRefBaseCoverCalc` | `biocjava.bioDoer.JIGplotToolkit.Paf.PafRefBaseCoverCalc` |
| `simpleBatchProcess` | `biocjava.bioDoer.Aligner.NeedleMan.SimpleBatchProcess` |

### 分子进化/标记（3）

| 工具名 | 引擎类 |
|:-------|:-------|
| `checkPrimer` | `biocjava.bioIO.Primer.CheckPrimer` |
| `dnDsCalculate` | `biocjava.bioIO.KaKs.DnDsCalculate` |
| `pairWiseKaKsCalculator` | `biocjava.bioIO.BioSoftPipeServer.PairWiseKaKsCalculator` |

### 文件/批处理（1）

| 工具名 | 引擎类 |
|:-------|:-------|
| `parallelMD5Check` | `biocjava.bioDoer.FileUtils.ParallelMD5Check` |

### 格式转换（1）

| 工具名 | 引擎类 |
|:-------|:-------|
| `gbff2gff` | `biocjava.bioIO.GBff.gbff2gff` |

### 生物软件封装（7）

| 工具名 | 引擎类 |
|:-------|:-------|
| `eggNogMapperResult` | `biocjava.bioIO.BioSoftPipeServer.eggNogMapperResult` |
| `findBestHomologyBatch` | `biocjava.bioIO.BioSoftPipeServer.FindBestHomologyBatch` |
| `geneExpFilter` | `biocjava.bioIO.BioSoftPipeServer.GeneExpFilter` |
| `genePairExpCorr` | `biocjava.bioIO.BioSoftPipeServer.GenePairExpCorr` |
| `generateMotifFromSequences` | `biocjava.bioIO.BioSoftPipeServer.MEMEsuiteWrapper.GenerateMotifFromSequences` |
| `slurmScriptPrepare` | `biocjava.bioIO.BioSoftPipeServer.SlurmScriptPrepare` |
| `tandemDupFinder` | `biocjava.bioIO.BioSoftPipeServer.TandemDupFinder` |

### 网络数据库（1）

| 工具名 | 引擎类 |
|:-------|:-------|
| `NCBITaxonomy` | `biocjava.bioWeb.NCBITaxonomy.NCBITaxonomy` |

### 表格（5）

| 工具名 | 引擎类 |
|:-------|:-------|
| `TableCast` | `biocjava.bioDoer.Table.TableCast` |
| `TableColSelector` | `biocjava.bioDoer.Table.TableColSelector` |
| `TableMelt` | `biocjava.bioDoer.Table.TableMelt` |
| `blastXmlSummaryTable` | `biocjava.bioIO.BlastXml.BlastXMLSummaryTable` |
| `blastXmlToTable` | `biocjava.bioIO.BlastXml.BlastXmlToSelfDefinedTable` |

### 表达计算（3）

| 工具名 | 引擎类 |
|:-------|:-------|
| `fpkmToTpm` | `biocjava.bioDoer.ExpressionLevelCalculator.FPKMtoTPM` |
| `rpkmCal` | `biocjava.bioDoer.ExpressionLevelCalculator.RPKMcalculator` |
| `tpmCalc` | `biocjava.bioDoer.ExpressionLevelCalculator.TPMcalculator` |


## 四、桥文档 bridges/*.java（80）

桥是 tbplot.sh 与 TBtools 引擎之间的 Java 适配层（tbplot.sh 内部自动编译调用）。每个桥的 Javadoc 含**完整的输入格式说明**，是最权威的参考——当某命令输出异常时，先读对应桥的 Javadoc。

> 桥文件 ↔ tbplot.sh 命令的对应关系：桥名去掉 `Cli` 后缀基本就是命令名（如 `HclustCli` ↔ `hclust`，`MicroSynCli` ↔ `microsyn`）。

### `AdmixtureCli`

```
tbplot admixture — TBtools ADMIXTURE Q 矩阵堆叠图 CLI（08/29 重建）
*
* 用法: AdmixtureCli <qFiles.lst> <out> [sampleIDFile] [groupFile] [sortMode] [width] [height] [panelInterval]
*   qFiles.lst: 每行一个 Q 矩阵文件路径（ADMIXTURE 输出 *.Q，如 K=2、K=3）
*   sampleIDFile: 样本 ID 文件（每行一个，与 Q 矩阵行对应）
*   groupFile: 分组文件（可选）
*   sortMode: Qraito|Lexical|None（默认 None）
*
* 引擎: AdmixtureQmatViz
*   process(File[]) 返回 JIGSubPanel[]（每个 Q 文件一个面板）→ save2Graph

```

### `AmazingMetaCli`

```
tbcli amazmeta — Amazing Meta Plot CLI（08/31 第七十八波，引擎 120）
*
* 用法: AmazingMetaCli <meme.xml> <newick.treefile> <out.svg|png|pdf> [seqLen.txt] [geneRename.txt]
*   meme.xml:      MEME 结果（必选）
*   newick.treefile: 进化树（必选，控制基因顺序）
*   seqLen.txt:    可选序列长度文件（gene\tlen）
*   geneRename.txt: 可选基因重命名
*
* 引擎: DrawAmazingMetaPlot.plot() —— 组合 进化树+Motif模式+基因结构+蛋白域 到一张图
*   （论文级组合图；plot() 内部 JFrame 显示 → Window 反射取 JIGBasePanel → save2SVG/PNG/PDF）

```

### `BamIndexCli`

```
tbcli bamindex — BAM 索引创建 CLI（08/31 第七十二波）
*
* 用法: BamIndexCli <in.sorted.bam> [out.bai]
*   in.sorted.bam: 已排序 BAM
*   out.bai:       输出 .bai（默认 <in>.bai）
*
* 引擎: BAMIndexCreater.setInSortedBamFile/setOutBaiFile + process()
*   （main 硬编码演示 → setter+process）

```

### `BamSortCli`

```
tbcli bamsort — BAM 排序 CLI（08/31 第七十二波）
*
* 用法: BamSortCli <in.bam> <out.bam> [sortOrder] [tmpDir]
*   sortOrder: coordinate|queryname|unsorted|duplicate（默认 coordinate）
*   tmpDir:    临时目录（默认系统临时）
*
* 引擎: SAMBAMSorter.setInFile/setOutFile/setSo/setTmpDir + process()
*   （main 硬编码演示 → setter+process）

```

### `BamStateCli`

```
tbplot bamstate — BAM 覆盖状态评估 CLI（08/29，第 57 引擎）
*
* 用法: BamStateCli <gff3> <out.tsv> <bam1> [bam2 ...] [--coverageThr X] [--depthThr X]
*   gff3: 标准 GFF3（gene/mRNA/exon 特征）
*   out.tsv: 每 BAM 的 coverage 比例 / depth / 总基因数 / 表达基因数
*   bamN: 比对 BAM（需 samtools index 建立 .bai）
*
* ⚠️ BAM 参考染色体名必须与 GFF3 seqid 匹配（HiC_scaffold_* 等）
*    实测：GRAS RNA-seq bam_subset + arrb21 GFF3（HiC_scaffold）验证通过

```

### `BarPlotterCli`

```
tbcli barplotter 桥 — 合成共线性柱状图 CLI（08/31 第六十六波）
*
* 用法: BarPlotterCli -g <gff> -s <synteny> -c <ctl> -o <out.png>
*   gff: chr\tgene\tend（简化 GFF）
*   synteny: MCScanX 式 collinearity（# Alignment 分段，行=基因1\t基因2\t...）
*   ctl: 4 行 = xdim / ydim / xchr列表(逗号分隔) / ychr列表(逗号分隔)
*
* ⚠️ bar_plotter.main 是死代码（打印 -4）→ 真入口是 main1（main1≠main 规律）

```

### `BarplotCli`

```
Barplot CLI — 富集柱状图（-log10 P-value 横向柱状图）
*
* 用法:
*   java -cp JAR:tbplot BarplotCli <enrichment.xls> <outFile> <termCol> <pvalCol> [classCol] [maxTerms] [xlab] [ylab] [mode]
*
* 参数:
*   enrichment.xls  — 富集结果表（TSV 带表头）
*   outFile         — 输出文件 (.svg/.png/.pdf)
*   termCol         — Term 列名（如 GO_Name / Pathway）
*   pvalCol         — P-value 列名（如 P_value）
*   classCol        — 分 class 列名（可选，如 Class）
*   maxTerms        — 最多显示 Term 数（默认 50）
*   xlab            — X 轴标签（默认 "-log10(P-value)"）
*   ylab            — Y 轴标签（默认 "GO Term"）
*   mode            — 图模式: Normal|TextOnLeft|BarOnLeft（默认 Normal）
*
* 数据格式（TSV，首行表头）:
*   GO_Name\tP_value\tClass
*   photosynthesis\t0.0001\tBP
*   ...

```

### `CalcRepeatCli`

```
tbplot calcRepeat — TBtools 重复序列得分计算 CLI（tool 39，08/31 攻克）
*
* 用法: CalcRepeatCli <genome.fa> <outRepeat.txt> [--kmerSize N] [--minFreq N] [--threads N]
*   genome.fa: 基因组 FASTA
*   outRepeat.txt: 输出重复得分（chr\tstart\tend\tscore）
*
* 引擎: calcRepeatScore（需 jellyfish 可执行）
*   process() 内部用默认 numOfThreads=60 + -s 2000M 调 jellyfish count → 小数据/慢环境易挂
* 破解: 预生成 <genome>.<kmer>.kmer.jf 文件（ProcessBuilder 用合理线程数，参数 -m -L -C 同引擎），
*   process() 检测 .jf 已存在 → 跳过内部 jellyfish count → JellyfishServer 直接 query → 输出得分

```

### `CddMotifCli`

```
tbcli cddmotif — CDD 保守域模式图 CLI（08/31 第七十九波，引擎 121）
*
* 用法: CddMotifCli <cdd.hitdata.txt> <in.fasta> <out.svg|png|pdf> [newick.treefile]
*   cdd.hitdata.txt: NCBI Batch CD-search hitsConcise 结果（# 注释头 + Query/Hit type/PSSM-ID/From/To/... 表）
*   in.fasta:       蛋白序列（ID 与 hitdata 的 Query 一致）
*   newick.treefile: 可选进化树（排序基因）
*
* 引擎: DrawMotifPatternFromCDDResult.setInFile/setInFasta + postGraph(newick, jigPanel) → JIGSubPanel
*   （论文级 CDD 保守域模式图；GRAS 真实 hitdata.txt 验证）

```

### `CircleGeneViewerCli`

```
tbplot circlegene — TBtools 环形基因位置图 CLI（08/29 重建）
*
* 用法: CircleGeneViewerCli <gff> <geneID.txt> <out> [--rename f] [--link f] [--rankedChr f] [--onlyMapped true|false]
*   gff: 基因注释 GFF（含 mRNA 行）
*   geneID.txt: mRNA ID 列表（每行一个，可第二列 1/0 控制颜色）
*   --rename: 基因重命名文件（可选）
*   --link: 基因对文件 (GeneA\tGeneB\t[r,g,b]) 绘制共线性链接（可选）
*   --rankedChr: 染色体排序列表（可选）
*
* 引擎: CircleGeneViewer（process() 内部 JFrame 弹窗；核心 JIGCircos.plot() 返回 JIGSubPanel）
* 方案: 窗口遍历 —— process() 后遍历 Window 找 JIGBasePanel 再保存
*       （GRAS 13 染色体+40 基因+6 同源 link 验证 SVG 25KB，08/28）

```

### `CircosCli`

```
tbplot circos — TBtools Circos 共线性环形图 CLI（08/29 重建）
*
* 用法: CircosCli <chrLen.txt> <link.txt> <genePos.txt> <out> [width] [height]
*   chrLen.txt: ChrID\tLength（每行一条染色体）
*   link.txt:   chrA sA eA chrB sB eB [color]（共线性连线，可空文件）
*   genePos.txt: Chr\tGene\tStart\tEnd [color]（基因位置，可空文件）
*   out: 输出 SVG/PNG
*
* 引擎: AmazingSimpleCircos（process() 内部解析 3 文件 → JIGCircosAdvanced.plot() → JFrame）
* 方案: 窗口遍历 —— process() 后遍历 Window 找 JIGBasePanel 再保存
*       （08/28 原 CircosCli：JIGCircosAdvanced.plot，30 连线验证）

```

### `ColorSchemeCli`

```
tbcli colorscheme — 表格分组着色 CLI（08/31 第七十四波）
*
* 用法: ColorSchemeCli <in.tab> <out.tab> <refColIndex(1-based)>
*   in.tab: 输入表（任意列，取第 refColIndex 列为分组键）
*   out.tab: 输出 = 原表 + RGB 颜色列（如 255,0,0）
*
* 引擎: ColorSchemeGenerator.setInTab/setOutTab/setRefColIndex + process()
*   （⚠️ isContinue/predifinedColorFile 无 setter——固定走随机色板分支）

```

### `CtgGroupCli`

```
tbplot ctgGroup — miniprot 等位基因 contig 分组 CLI（08/29，第 72 引擎）
*
* 用法: CtgGroupCli <in.miniprot.gff> <polyPoid> <outContigGrpMap>
*   in.miniprot.gff: miniprot --gff 输出（蛋白→contigs）
*   polyPoid: 目标倍性；outContigGrpMap: contig → 同源组
*
* 组装辅助链: miniprot → CtgGroupCli → HomoConflictBasedPartition(自带CLI) → SeperateChrByAlleles
* ⚠️ main() 硬编码路径——改走 setInMiniprotGff/setPloyPoid/setOutContigGrpMap + process()。

```

### `CubeHeatmapCli`

```
tbplot cubeheatmap — TBtools 3D 立方体热图 CLI（08/29 重建）
*
* 用法: CubeHeatmapCli <expr.tsv> <group.tsv> <out> [--log10] [--minColor r,g,b] [--midColor r,g,b] [--maxColor r,g,b]
*   expr.tsv: 表达矩阵（首列基因名 + 样本名表头 + 数值）
*   group.tsv: Sample\tFirstDim\tSecondDim（定义 3D 三面维度）
*
* 引擎: CubeHeatMap（plot() 内部 JIGUtils.quickShow 创建窗口，不返回 panel）
* 方案: 窗口遍历 —— plot() 后遍历 Window 找 JIGBasePanel 再保存
*       （08/28 原 CubeHeatmapCli 同方案，需 -Xmx4g 避免 quickShow OOM）

```

### `DegramdomCli`

```
tbcli degramdom — 亲子表构建 Newick 树 CLI（08/31 第七十波）
*
* 用法: DegramdomCli <in.tsv> [out.nwk]
*   in.tsv: 子节点\t父节点\t枝长（每行一个父子关系；表头/空行自动跳过）
*   out.nwk: 输出 Newick（可选，默认打印到 stdout）
*
* 引擎: BuildDegramdomFromTable.process() 返回 Newick 字符串（main 硬编码演示 → setter+process）

```

### `DiffExpCli`

```
tbplot dehist — TBtools 差异表达双直方图 CLI（08/29 新增，第 27 引擎）
*
* 用法: DiffExpCli <deg.txt> <out> [width] [height]
*   deg.txt: 每行至少 3 列（tab 分隔）：任意ID\t值1\t值2
*     值1/值2: 两个样本/条件的数值（如表达量、Log2FC 对）
*     # 开头行跳过；第 2 列必须是数字
*     引擎按 值1 vs 值2 大小分左右两个直方图
*
* 引擎: DiffExpDualHistPlot.process(File) 返回 JIGSubPanel[]（双直方图）

```

### `DistanceCli`

```
tbplot distance — TBtools 距离计算 CLI（08/29，第 42 引擎）
*
* 用法: DistanceCli <in.tsv> <col1> <col2> <method>
*   in.tsv: tab 分隔表；col1/col2: 列索引（从 0 开始，取两列数值）
*   method: euclidean|pearson|pearsonDist
*   输出: 两列数值的距离/相关系数（所有行合并计算）
*
* 引擎: Distance 静态方法（getEuclideanDistance/getPearsonCorrelationCoefficient/getPearsonDistance）

```

### `DualSynCli`

```
tbplot dualsyn — TBtools 双基因组共线性图 CLI v3（08/31，旧 JJplot2 框架保存破解）
*
* 用法: DualSynCli <simplifiedGff> <collinearity> <out> [--chr1 "1,2"] [--chr2 "3,4"] [--rows N] [--gap N]
*   simplifiedGff: Chr\tGeneName\tStart\tEnd（染色体名必须数字！如 1/2/3 或 "1-1"）
*   collinearity: MCScanX 输出（*.collinearity）
*
* 引擎: DualSyntenyPlotterAdvance（旧 JJplot2 框架）
*   plot() 内部用静态工厂 prepareBackgroundCoordinateWithoutAxis 建 GUI，
*   GUI 实例被内部类（$5/$6/$7，含 Ljjplot2/JJplot2GUI 字段）以监听器形式挂在组件树上。
* 保存: 调 plot() 后反射深度扫描所有窗口+组件+监听器对象，提取 JJplot2GUI 实例
*       → saveImageAsPNG/PDF/SVG。

```

### `ExprCorrCli`

```
tbplot exprCorr — 表达相关矩阵 CLI（08/29，第 60 引擎）
*
* 用法: ExprCorrCli <inFPKM> <outCorrMat>
*   inFPKM: 表达矩阵（首列基因名 + 样本列）
*   outCorrMat: 样本间 Pearson 相关矩阵（共表达/聚类分析输入）
*
* ⚠️ main() 硬编码路径——改走 setInFPKM/setOutCorrMat + process()。

```

### `FileSplitCli`

```
tbcli filesplit — 文件按份数分割 CLI（工具 99）
* 用法: FileSplitCli <inFile> <numParts>
* 引擎: FileLineSplit.Split(File, int) 静态方法

```

### `FindBlockDualCli`

```
tbplot findBlockDual — 双基因组伪共线性区块搜索 CLI（08/29，第 50 引擎）
*
* 用法: FindBlockDualCli <queryGenome.fa> <query.gff> <subjectGenome.fa> <subject.gff> <queryId> <out.txt>
*   queryGenome.fa / subjectGenome.fa : 两物种基因组 FASTA
*   query.gff / subject.gff            : 两物种 GFF/GXF 注释（含 mRNA 行）
*   queryId                            : 查询基因 ID（mRNA ID，如 AT1G70000.2）
*   out.txt                            : 伪共线性区块匹配结果
*
* 可选参数（默认值）:
*   --leftEdge N(5) --rightEdge N(5) --expand N(10) --threads N(2) --evalue 1e-5 --minIdentity 0.33 --bestHit N(10)
*
* ⚠️ FindBlockDual.main() 硬编码路径——改走完整 setter + process()。
*    内部用 blastp 找 query 侧边缘基因在 subject 侧的同源，推断共线性区块。
*    ⚠️ 需真实双基因组数据验证（本地无拟南芥 TAIR10 对照数据）。

```

### `FindBlockMultipleCli`

```
tbplot findBlockMultiple — 多基因组伪共线性区块搜索 CLI（08/29，第 52 引擎）
*
* 用法: FindBlockMultipleCli <queryGenome.fa> <query.gff> <queryId> <out.txt> <sub1Genome.fa> <sub1.gff> [<sub2Genome.fa> <sub2.gff> ...] [--leftEdge N --rightEdge N --expand N --threads N]
*   queryGenome.fa / query.gff : 查询物种基因组 + 注释
*   queryId                    : 查询基因 ID（基因组中部，避开首个基因 get(-1) 边界 bug）
*   out.txt                    : 区块结果（含 query + 各 subject 行）
*   subNGenome.fa / subN.gff   : 1 或多个比对物种（成对给出）
*
* ⚠️ main1() 硬编码路径——改走完整 setter + processMultipleGenome()。
* ⚠️ 大数据引擎：必须 -Djava.io.tmpdir=<磁盘>（/tmp=tmpfs 16G 会被 3GB 基因组 init 撑爆）。
*
* 例: FindBlockMultipleCli Cr.fa Cr.gff evm.model.Chr06.1064 out.txt Cs.fa Cs.gff Ni.fa Ni.gff

```

### `FindPathCli`

```
tbcli findpath 桥 — 共线性基因块进化路径 CLI（08/31 第六十七波）
*
* 用法: FindPathCli --inGffArr <gff1,gff2,...> --inGenePairs <pairs> --inRegion <geneID> [--flankGeneNum N] [--highlightGene ID] --outGraph <out>
*
* ⚠️ FindPathBySynteny.main1 是完整 CLI，但 main 是硬编码演示 → 桥直接调 main1

```

### `GeneDensityCli`

```
tbplot genedensity — 基因密度谱 CLI（08/31 第五十三波）
*
* 用法: GeneDensityCli <in.gff3> <out> [binSize]
*   in.gff3: 基因组注释
*   out:     基因密度表 (tsv)
*   binSize: 窗口大小 bp（默认 100000）
*
* 引擎: GeneDensityProfiler.setBinSize/setInGXF/setOutGeneRecordFile/process()
*       （窗口内基因计数 → 染色体密度谱，供基因组轨道/密度热图）

```

### `GeneLocGffCli`

```
tbplot genelocgff — TBtools 基因染色体定位图（GFF+ID 输入）CLI（08/29 重建）
*
* 用法: GeneLocGffCli <gff3> <idList> <out> [--chrLen len.tsv] [--rename r.tsv] [--pairs p.tsv] [--color c.tsv]
*                     [--rankedChr list] [--onlyMapped true|false] [--showLabel true|false]
*
* 方案: 绕开 GeneLocationControlFromGff3AndIdList.process() 的 JFrame
*   复制核心逻辑: 解析 GFF（mRNA/gene 行）→ 生成 genePos 文件（featureName\tchrName\tstartPos\tendPos）
*               + genomeLen 文件（chr\tlength）→ GeneLocation.plot() → save2Graph
*   参考 08/28 原 GeneLocGffCli（GRAS 75 基因/15 染色体验证 SVG 108KB）

```

### `GeneStructureCli`

```
tbplot genestructure — TBtools 基因结构图 CLI（08/29 重建）
*
* 用法: GeneStructureCli <input.gff> <idList.txt> <outFile> [genome.fa] [width] [height]
*   input.gff: GFF/GXF 格式基因注释（含 mRNA 行）
*   idList.txt: mRNA ID 列表（每行一个）
*   genome.fa: 基因组序列（可选，用于显示 UTR 等）
*   outFile: 输出 SVG/PNG
*   width/height: 画布尺寸（默认 1200x600）
*
* 引擎: DrawGeneStructureFromGXFfile（继承 DrawMotifPatternFromMEMEResult）
*   核心: ParseGeneStructureFromGXF.parse(GFF) + setRetainIDList + insertSeqFromGenome
*   绘图: postGraph(null, basePanel) 返回 JIGSubPanel（第一参数 Newick 传 null 跳过）

```

### `GenericCli`

```
GenericCli — TBtools 通用反射绘图桥（08/29 新增，根治 /tmp 清理导致桥丢失）
*
* 用反射驱动任意 TBtools 引擎，覆盖统一模式：
*   setter(File/String/int/boolean/double/Color) → plot()/process()/makeGraph() → JIGSubPanel(JIGSubPanel[]) → save2Graph
*
* 用法:
*   java -cp JAR:tbplot_cli GenericCli <engineClass> <method> <outFile> [--set field value ...] [--width N] [--height N]
*
*   engineClass: 完整类名（如 biocjava.bioDoer.JIGplotToolkit.Synteny.MultipleSpeciesSyteny）
*   method:      绘图方法名，可用 + 连接按序调用（如 doPCA+postGraph => 先 doPCA 再 postGraph）
*                plot / process / makeGraph / postGraph 等，返回 JIGSubPanel(JIGSubPanel[]) 的作为结果
*   outFile:     输出 SVG/PNG
*   --set:       调用 set<Field>(value)，类型自动推断:
*                  File   -> new File(value)
*                  String -> value
*                  int    -> Integer.parseInt
*                  double -> Double.parseDouble
*                  float  -> Float.parseFloat
*                  boolean-> Boolean.parseBoolean
*                  Color  -> 解析 "r,g,b" 或 名字（RED/GREEN/...）
*                  Enum   -> Enum.valueOf(type, value)
*   --width/--height: JIGBasePanel 尺寸（默认 1000x800）

```

### `GroupedBarCli`

```
tbplot groupedbar — TBtools 分组柱图+显著性 CLI（08/29 重建）
*
* 用法: GroupedBarCli <data.tsv> <out> [plotType] [errorBarType] [hasHeader] [title] [--options]
*   plotType: BAR_ERROR|BOXPLOT|VIOLIN|SWARM（默认 BAR_ERROR）
*   errorBarType: SEM|SD|CI95（默认 SEM）
*   hasHeader: true/false（默认 true）
*   data.tsv: Group\tValue（每组至少 2 重复）
*   --options: --width --height --fontSize --yMin --yMax --pStar --pStar2 --pStar3 --noNs --color <i> <r,g,b> --order ALPHA|FIRST --homoscedastic
*
* 引擎: GroupedBarRawData.load → GroupedBarStatistics.analyze → buildPanel（自动 T-test/ANOVA + Bonferroni）

```

### `GsaDiagCli`

```
tbcli gsadiag — 基因结构快速诊断 CLI（08/31 第八十四波，工具 94）
*
* 用法: GsaDiagCli <in.fixed.gff3> <out.stat.xls> [genome.fasta] [relax] [--checkUTR]
*   in.fixed.gff3: 注释 GFF3（建议已相位校正）
*   out.stat.xls: 诊断统计输出
*   genome.fasta: 可选基因组（编码潜能检查）
*   relax: 长度异常 relax 参数（默认 0.5）
*   --checkUTR: 检查 UTR 比例异常
*
* 引擎: GsaQuickDiagnosis.setInFixedGXF/setOutStat/setOptionalGenomeSequence/setRelax + process()
*   （main 硬编码演示 → setter+process；Gff3PhaseValidator + LengthAnomalyChecker 内部检查）

```

### `GxfFilterCli`

```
tbcli gxffilter — GFF 按 ID 列表过滤 CLI（08/31 第八十六波，工具 96）
*
* 用法: GxfFilterCli <in.gff3|gtf> <idList.txt> <out.gff3|gtf>
*   idList.txt: 每行一个基因/转录本 ID
*
* 引擎: GXFfilter.setInGXF/setIDList/setOutGXF + process()（main 硬编码演示 → setter+process）
*   （保留 ID 列表中基因/转录本及其子特征的子注释——基因家族子注释提取刚需）

```

### `GxfSortCli`

```
tbcli gxfsort — GFF 按坐标排序 CLI（08/31 第八十五波，工具 95）
*
* 用法: GxfSortCli <in.gff3|gtf> <out.sorted>
*   in/out: 注释文件（按染色体+坐标排序，注释预处理刚需）
*
* 引擎: GXFSort.sortByPretty(File, File)（main 硬编码演示 → 实例方法直接调）

```

### `HclustCli`

```
tbplot hclust — TBtools Hclust 聚类 CLI（08/29 重建）
*
* 用法: HclustCli <expr.matrix.tsv> <out.nwk> [distMethod] [clusterMethod]
*   expr.matrix.tsv: 首列基因名 + 列样本名表头，其余数值
*   distMethod: 距离方法（默认 Euclidean，如 PearsonCorrelation / Manhattan 等）
*   clusterMethod: 聚类方法（默认 UPGA，如 NeighborJoining / ML / MP 等）
*
* 引擎: Hclust.buildDendrogram() 返回 Newick 字符串
* 注意: 此引擎输出 Newick 树文本（不是图）

```

### `HeatmapCli`

```
tbplot heatmap2 — TBtools 热图（引擎级，支持聚类/缩放/颜色映射）CLI（08/29 重建）
*
* 用法: HeatmapCli <expr.matrix.tsv> <out> [--options]
*   expr.matrix.tsv: 首列基因名 + 列名表头 + 数值
*   --options:
*     --log2 / --log10         对数变换
*     --rowScale               行归一化
*     --clusterRow / --clusterCol  行列聚类
*     --noRowNames / --noColNames  隐藏行列名
*     --noLegend / --noValue   隐藏图例/数值
*     --minColor r,g,b --midColor r,g,b --maxColor r,g,b
*     --width px --height px
*
* 引擎: HeatMap.heatmap.show() 返回 JIGBasePanel（GRAS 70基因×81样本验证 SVG 2.08MB，08/28）

```

### `LayoutHeatmapCli`

```
tbplot layoutheatmap — TBtools 布局热图 CLI（08/29 重建）
*
* 用法: LayoutHeatmapCli <layout.tsv> <expr.tsv> <out> [--options]
*   layout.tsv: 样本名矩阵（TSV，定义样本在热图中的布局位置；空位用 NA）
*   expr.tsv: 表达矩阵（首列基因名 + 样本名表头 + 数值）
*   --options: --cellWidth --cellHeight --yGap --log2 --log10 --rowScale --minColor r,g,b
*              --midColor r,g,b --maxColor r,g,b --nanColor r,g,b --noLegend --noValue --rename f --topLeft
*
* 引擎: LayoutHeatmap.plot() 返回 JIGSubPanel[]（3×3 布局+5 基因验证 SVG 67KB，08/28）

```

### `MCScanXCli`

```
tbcli mcscanx — 纯 Java MCScanX 共线性检测 + 重复基因分类 CLI（08/31 第六十八波）
*
* 用法:
*   MCScanXCli <gff> <blast> <outPrefix> [--html]              # 共线性检测
*   MCScanXCli classify <gff> <blast> <outPrefix>              # 重复基因分类（WGD/tandem 等）
*
*   gff:      简化 GFF（MCScanX 格式）
*   blast:    BLAST tab 结果（12 列，蛋白互相比对）
*   outPrefix: 输出前缀（生成 <prefix>.collinearity / .duptype）
*   --html:   可选生成 HTML 可视化
*
* 引擎: org.mcscanx.api.MCScanXAPI — 纯 Java 实现，无需外部 MCScanX 二进制
*   （GRAS WGD/共线性分析刚需；与外部 MCScanX 输出 100% 一致验证）

```

### `MSACli`

```
tbplot msa — TBtools MSA 序列比对图 CLI（08/29 重建，替代损坏的恢复件）
*
* 用法: MSACli <aligned.fasta> <out> [padding]
*   尺寸按子面板自动计算，勿传 w/h（NPE 根因=缺 setInMSAtextFile）
*
* 引擎: MSAviewer.setInMSAtextFile + processed() 返回 panel 列表
*       （PIN 14 序列验证 SVG 4.1MB；长序列建议 PNG，08/28）

```

### `MarkerDesignCli`

```
tbplot marker — TBtools 标记设计工具 CLI（08/29，第 46-48 引擎）
*
* 用法: MarkerDesignCli <engineClass> <inMarker> <out.txt> [--maxPoint N]
*   engineClass: MarkerDist|MarkerFilter|SampleDist（biocjava.bioDoer.markerDesign 下）
*   inMarker: 标记 0-1 矩阵（tab 分隔）
*   --maxPoint: MarkerDist 专用（最大点数）
*
* ⚠️ 引擎输出模式差异（08/29 反编译确认，统一兼容）：
*   - MarkerDist:   process() 返回结果字符串（result 非空）→ 直接写文件
*   - MarkerFilter: process() 返回 null，结果走 System.err.println
*   - SampleDist:   process() 返回 ""，结果走 System.err.println
*   桥在 process() 期间重定向 System.err 到缓冲，若返回字符串为空则把捕获的 stderr 写入文件。

```

### `MarkerToolsCli`

```
tbcli markertools — 分子标记分析 CLI（08/31 第七十七波）
*
* 用法:
*   MarkerToolsCli filter <in.marker.tab>            # 标记过滤(minor allele 统计,输出 stderr)
*   MarkerToolsCli dist <in.marker.tab> <maxPoint>   # 标记距离计算
*   MarkerToolsCli sampledist <in.marker.tab>        # 样本距离计算
*
* in.marker.tab: 0/1 标记矩阵,行=样本/个体,列=标记,首行列名+首列行名
*
* 引擎: MarkerFilter/MarkerDist/SampleDist 的 setInMarker + process()（main 均硬编码演示）

```

### `Mast2TabCli`

```
tbcli mast2tab — MEME/Mast XML → tab CLI（08/31 第八十三波，工具 93）
*
* 用法: Mast2TabCli <mast|meme.xml> <out.tab>
*   mast/meme.xml: MEME Suite XML 输出（mast.xml 或 meme.xml）
*   out.tab: 表格化结果
*
* 引擎: MEMESuiteXMLtoTab.setInMastXML/setOutTab + process()（main 完全硬编码演示 → setter+process）

```

### `MastRunCli`

```
tbcli mastrun — 一步法 MAST motif 扫描 CLI（08/31 第八十九波，工具 101）
*
* 用法: MastRunCli <meme.xml> <seq.fasta> <workingDir> [--motifs M] [--seqEvalue X] [--motifPvalue X] [--other "..."]
*   meme.xml:  MEME 输出（motif 定义）
*   seq.fasta: 待扫描序列
*   workingDir: 输出目录
*
* 引擎: QuickRunMAST.setMotifFile/setSequenceFile/setWorkingDir/... + process()
*   （调系统 mast；与 memerun 配套——memerun 发现 motif → mastrun 扫描）

```

### `MemeRunCli`

```
tbcli memerun — 一步法 MEME motif 发现 CLI（08/31 第八十八波，工具 100）
*
* 用法: MemeRunCli <in.fasta> <workingDir> [--motif N] [--minW N] [--maxW N] [--evalue X] [--mode ZeroOrOneOccurPerSeq|OneOccurPerSeq|AnyNumberOfOccurPerSeq]
*   in.fasta:   未比对蛋白/核酸序列
*   workingDir: 输出目录
*
* 引擎: QuickRunMEME.setInFile/setWorkingDir/... + process()（main 硬编码演示 → setter+process）
*   （调系统 meme；GRAS motif 分析统一 CLI 入口）

```

### `MgGxfCli`

```
tbcli mggxf — 多 GFF 视图格式转换 CLI（08/31 第九十波，工具 103）
*
* 用法: MgGxfCli <inGenePair|blastTab6> <in.simplified.gff> <out.LinkedRegion> [GenePair|BlastTab6]
*   inGenePair: 基因对文件（GenePair 模式）
*   in.simplified.gff: 简化 GFF（chr\tgene\tstart\tend）
*   out.LinkedRegion: 输出共线性区域
*
* 引擎: FormatTranformerForMultipleGffViewer.setInFile/setInGffFile/setOutFile/setInputFormat + transform()
*   （main 硬编码演示 → setter+process；多物种共线性可视化的格式转换）

```

### `MicroSynCli`

```
tbplot microsyn — TBtools 双基因组微共线性图 CLI（08/29 新增，第 31 引擎）
*
* 用法: MicroSynCli <gxf1> <gxf2> <collinearity> <out>
*       [--chr1 LG03 --start1 13207612 --end1 13990030]
*       [--chr2 chr08 --start2 10660849 --end2 11367883]
*       [--highlight1 chr1:start:end] [--highlight2 chr2:start:end]
*   gxf1/gxf2: 两物种 GFF/GXF 注释
*   collinearity: MCScanX 输出（*.collinearity 文件）
*   区域默认取全基因范围（若不指定则自动）
*
* 引擎: MicroSyntenicAdvance（setInGxf/setInGxf2/setCollinerFile/setRegion/setRegion2 + process）
* 方案: 窗口遍历 —— process() 后遍历 Window 找 JIGBasePanel 再保存

```

### `MirIdentifyCli`

```
tbplot mirIdentify — miRNA 前体鉴定 CLI（08/29，第 78 引擎）
*
* 用法: MirIdentifyCli <inGenome.fa> <inTargetSo.tsv> <outPredict> <outChecklog> [--checkARM BOTH|FIVE|THREE] [--maxAsy N] [--maxMatureAsy N] [--maxStarAsy N] [--maxBulge N]
*   inGenome.fa : 参考基因组（HiC_scaffold 命名，如油茶 Co_chroms.fa）
*   inTargetSo.tsv : TargetSo 引擎输出（mirnatarget 命令产物：miRNA target strand beg end score ...）
*   outPredict : miRNA 前体预测表；outChecklog : 检查日志表
*
* ⚠️ 前体提取需要 RNAfold（检查 PATH）；基因组大（2.7GB 级）需 -Xmx>=8g + -Djava.io.tmpdir=<磁盘>
* ⚠️ 靶标表 subject 染色体名必须与基因组 fasta 头匹配

```

### `MotifCli`

```
tbplot motif — TBtools Motif 分布图 CLI（08/29 重建）
*
* 用法: MotifCli <meme.xml> <idList.txt> <out.svg/png> [width] [height]
*   meme.xml: MEME suite 输出（含 motif 定义）
*   idList.txt: 序列 ID 列表（每行一个，指定画哪些序列）
*   outFile: 输出 SVG/PNG
*   width/height: 画布尺寸（默认 1200x600）
*
* 引擎: DrawMotifPatternFromMEMEResult
*   关键: setMaxMotif 设大避免 isTooMuchMotif 弹窗（headless 卡死）
*   postGraph(null, basePanel) 返回 JIGSubPanel（第一参数 Newick 传 null）

```

### `MountainPlotCli`

```
tbplot mountain — TBtools RNA 山峰图数据 CLI（08/29，第 43 引擎）
*
* 用法: MountainPlotCli <fold.txt> <out.tsv>
*   fold.txt: RNA 二级结构折叠字符串（() 和 . 表示），如 ".((((..))))"
*   out.tsv: 每碱基位置的山峰高度（位置\t高度）
*
* 引擎: MountainPlot.process() 逻辑（fold 字符串→堆积高度）

```

### `MultiSuperHeatCli`

```
tbplot multiEfp — TBtools 多矩阵组织表达热图 CLI（engine 110，08/31 攻克）
*
* 用法: MultiSuperHeatCli <inTGA> <sample2cc> <expMat1.tsv[,expMat2.tsv,...]> <geneId> <out> [--imageWidth N] [--imageHeight N]
*   inTGA: 底图（植物/组织示意图，必须 TrueColor RGB 非灰度）
*   sample2cc: SampleName\tRGB 映射
*   expMat(逗号分隔): 首列基因名 + 样本列，可多个矩阵叠加
*   geneId: 要可视化的基因
*   out: .svg/.pdf/.png
*
* 引擎: generateMultipleSuperHeatMap
*   main() 硬编码了第二个矩阵路径（ExpressData1.txt）→ 不能直接用 main
*   核心 API 完好：setter + private initExp()（反射）+ showHeatMapOf(geneId) → JIGBasePanel → save2SVG/PNG/PDF
*   ⚠️ 需 fake DatatypeConverter（build/javax/xml/bind/，JDK9+ jaxb hack）

```

### `PafGC`

```
tbplot pafcomp — TBtools PAF 基因组比较图 CLI（08/29，第 38 引擎）
*
* 用法: PafGC <--inPaf paf> <--outGraph out> [--colorMode Target|Query|None] [--size N] [--colorSeed N] [--switchQnT] [--minLen N]
*
* ⚠️ 入口是 main1（不是 main）——main 不 setInPaf 用默认路径；main1 完整 ArgsParser + quickSave

```

### `PafVizCli`

```
tbplot pafviz — TBtools PAF 比对 Dot-plot CLI（08/29 重建）
*
* 用法: PafVizCli <in.paf> <out> [graphSize] [colorMode] [switchQT] [minAlnLen] [rcColor]
*   colorMode: Target|Query|None（默认 Target）
*   switchQT: true/false 交换 Query/Target 轴（默认 false）
*   minAlnLen: 最小比对长度过滤（默认 0）
*   rcColor: true/false 反向互补段反色（默认 false）
*
* 引擎: PafViz
*   setInPaf + setCurColorMode(枚举) + process() 返回 JIGSubPanel

```

### `PeakDistCli`

```
tbplot peakdist — TBtools Peak 染色体分布图 CLI（08/29 新增，第 26 引擎）
*
* 用法: PeakDistCli <chrLen.tsv> <macs2_peak.xls> <out> [--chrHeight H] [--topLenRank N] [--width W] [--height H]
*   chrLen.tsv: Chr\tLength（染色体长度）
*   macs2_peak.xls: MACS2 peaks 表格（chr/start/end 列）
*
* 引擎: peakDistribution（process() 是 private，用反射 setAccessible 调用）
*   setInChrLen + setInMACS2Peak + process() -> JIGSubPanel -> save2Graph

```

### `Pep2CodonCli`

```
tbcli pep2codon — 蛋白比对回译密码子比对 CLI（08/31 第八十二波，工具 91）
*
* 用法: Pep2CodonCli <cds.fa> <pep.aln.fa> <codon.aln.out>
*   cds.fa:       CDS 序列（ID 与 pep.aln 一致）
*   pep.aln.fa:   蛋白比对（含 gap 的比对结果）
*   codon.aln.out: 输出密码子比对（Ka/Ks 分析输入）
*
* 引擎: pepAln2CodonAln.transformat(File, File, File) —— 静态方法直接调用（main 硬编码演示）
*   （PairWiseKaKsCalculator 内部回译逻辑的独立版——Ka/Ks 分析刚需）

```

### `PfamMotifCli`

```
tbcli pfammotif — Pfam 保守域模式图 CLI（08/31 第八十一波，引擎 123）
*
* 用法: PfamMotifCli <pfamscan.txt> <in.fasta> <out.svg|png|pdf> [newick.treefile]
*   pfamscan.txt: PfamScan/pfam_scan.pl 16 列输出（seqid alnStart alnEnd envStart envEnd hmmAcc hmmName type hmmStart hmmEnd hmmLen bitscore evalue ...）
*   in.fasta:     蛋白序列（ID 与 pfamscan 一致）
*   newick.treefile: 可选进化树
*
* 引擎: DrawMotifPatternFromPfamResult.setInFile/setInFasta + postGraph(newick, jigPanel) → JIGSubPanel
*   （⚠️ 委托 PfamDomainHitsTableParser，期望 PfamScan 16/15 列；可用 hmmscan --domtblout 转换）

```

### `PhyloTreeCli`

```
tbplot phylotree — 系统发育树视图 CLI（08/31 第五十一波）
*
* 用法: PhyloTreeCli <in.nwk> <out> [vertical] [width] [height]
*   in.nwk: Newick 树文件（支持枝长）
*   out:    .svg / .png / .pdf
*   vertical: true=纵向（默认 false 横向）
*
* 引擎: PhyloTreeMan.build() → calcForPlotEignine() 生成 TreeTab →
*       PhyloTreeView.showTree() 返回 JIGSubPanel
*       （08/29 误判「需 TreeTab 格式跳过」——实际 build 直接吃 newick，
*         calcForPlotEignine 内部自动算坐标；08/31 复核攻下）

```

### `PileUpCli`

```
tbplot pileup — TBtools BLAST pile-up 可视化 CLI（08/29，第 44 引擎）
*
* 用法: PileUpCli <blast.xml> <out.svg> [--query NAME]
*   blast.xml: BLAST XML 输出（BLAST+ -outfmt 5）
*   --query: 指定 query（缺省自动选第一个）
*
* 引擎: ncbiPileUpPlot.showIteration(Iteration)（绕过 GUI 弹窗，自动选 query）

```

### `QpcrCli`

```
tbplot qpcr — TBtools qPCR 柱状图（带误差棒）CLI（08/29 重建）
*
* 用法: QpcrCli <data.txt> <out.svg/png> [width] [height]
*   data.txt: name\tmean\tsd（每行一个样本/处理）
*
* 引擎: barPlotWithErrorBar（plot() 只弹窗不返回 panel）
* 方案: 窗口遍历 —— plot() 后遍历所有 java.awt.Window 找到 JIGBasePanel 再保存
*       （参考 08/28 原 QpcrCli 的窗口遍历方案）

```

### `QpcrDdctCli`

```
tbplot qpcrDdct — qPCR 相对定量（ΔΔCt）CLI（08/29，第 58 引擎）
*
* 用法: QpcrDdctCli <in.qpcr.tab> <out.xls>
*   in.qpcr.tab: tab 分隔 3 列（基因名\t对照Ct\t实验Ct），同名多行取平均
*   out.xls: 相对表达量（2^-ΔΔCt 等）
*
* ⚠️ main() 硬编码路径——改走 setInqPCRTabFile/setOutProcessedFile + process()。
*    多基因重复样本自动平均。TBtools 官方用于 qPCR 相对定量。

```

### `QpcrProcCli`

```
tbcli qpcrproc — qPCR 相对表达分析 CLI（08/31 第八十七波，工具 97）
*
* 用法: QpcrProcCli <in.qpcr.tab> <out.xls>
*   in.qpcr.tab: Sample\tRefCt\tExpCt（列1=内参基因 Ct，列2=目标基因 Ct；同样本多行求均值）
*   out.xls: Sample\tMean\tStdev（2^-ΔΔCt 相对表达）
*
* 引擎: SimpleQPCRProcessser.setInqPCRTabFile/setOutProcessedFile + process()
*   （main 硬编码演示 → setter+process；qPCR 数据分析，与绘图类 qpcr 互补）

```

### `RNAplotCli`

```
tbplot rnaplot — TBtools RNA 二级结构绘图 CLI（engine 111，08/31 攻克）
*
* 用法: RNAplotCli <seq.fa|rawSeq> <out> [--colorMap "seq1=R,G,B;seq2=R,G,B"] [--interactive false]
*   seq: FASTA 或单行序列
*   out: .svg/.pdf/.png
*
* 引擎: RNAplotAdvance（需要 RNAfold/RNAplot 可执行）
*   main() 用 RNAplotInvoker.generatePlotPsFile 管道调 RNAplot → 本机 RNAplot 2.7 不读 stdin 管道，
*   导致 temp PS 文件不生成 → FileNotFoundException
* 破解: 绕开 generatePlotPsFile——
*   1) RNAfoldInvoker.fold(seq) 拿 FoldInfo（seq+structure+mfe）
*   2) 写 temp.fa（>seq + seq + structure(mfe)）→ 本机 RNAplot -i 生成 EPS（含 /sequence /coor /pairs）
*   3) RNAplotAdvance.transform(EPS, interactive) → JIGSubPanel
*   4) JIGBasePanel + addSubPanel + save2SVG/PNG/PDF

```

### `RegionDepthCli`

```
tbcli regiondepth — SAM 区域覆盖深度 CLI（08/31 第七十六波）
*
* 用法: RegionDepthCli <in.sam> <region> <out.depth> [scaleFactor]
*   in.sam: 已排序或未排序 SAM（内部自动按位置排序+建索引）
*   region: ChrID:Start-End 或 ChrID#Start#End（1-based）
*   out.depth: 每碱基覆盖深度
*   scaleFactor: 缩放因子（默认 1）
*
* 引擎: CalcRegionDepth.init() + processRegion()（main 硬编码演示 → setter+process）

```

### `SamBamCovCli`

```
tbcli sambamcov — BAM bin 覆盖统计 CLI（08/31 第七十一波）
*
* 用法: SamBamCovCli <in.bam> <out.tsv> [binSize] [countMode]
*   binSize:   窗口大小 bp（默认 1000）
*   countMode: Overlap|StartPos|EndPos（默认 Overlap）
*
* 引擎: SamBamBINCov.setInXamFile/setOutBINCovFile/setBINsize/setCountMode + process()
*   （main 硬编码演示 → setter+process）

```

### `SeqConverterCli`

```
tbcli seqConverter 桥 — 序列格式转换 CLI（08/31）
*
* 用法: SeqConverterCli -i <in> -o <out> -iF <fmt> -oF <fmt>
*   fmt: fasta|clustal|MEGA|nexus|PAML|phylip
*
* ⚠️ SeqConverter.main 是硬编码演示 → 真实 CLI 入口是 main1(public static)
*   （main1 ≠ main 规律：PafGenomeComp/SeqConverter 同型）

```

### `SeqLenTrackCli`

```
tbcli seqlentrack — 序列长度骨架图 CLI（08/31 第八十波，引擎 122）
*
* 用法: SeqLenTrackCli <seqlen.txt> <out.svg|png|pdf> [newick.treefile]
*   seqlen.txt: gene\tlength（每行一个基因；# 开头跳过）
*   newick.treefile: 可选进化树（排序基因）
*
* 引擎: DrawSequenceFromSeqLenInfo（继承 DrawMotifPatternFromMEMEResult.postGraph(newick, panel)）
*   （AmazingMetaPlot 的 CDD 面板底层——基因长度骨架图）

```

### `SeveralSpeciesCli`

```
tbplot multisyn — TBtools 多物种微共线性分析图 CLI（08/29 新增，第 33 引擎）
*
* 用法: SeveralSpeciesCli <gxf.lst> <collinear.lst> <out> [--genes idlist.txt]
*   gxf.lst: 每行一个 GXF/GFF 注释文件路径
*   collinear.lst: 每行一个 MCScanX collinearity 文件路径（与 GXF 对应配对）
*   --genes: 高亮基因 ID 列表（可选）
*
* 引擎: SeveralSpeciesMicroSyntenicAnalysisAdvance
*   setGxfArr(ArrayList<File>) + setCollinearFileArr + setSpecificGenesList
*   process() 内部用 JIG 引擎（JIGBasePanel）→ 窗口遍历保存

```

### `SimpleHmmscanCli`

```
tbcli simpleHmmscan — Pfam 域快速扫描 CLI（08/31 第七十三波）
*
* 用法: SimpleHmmscanCli <pfamA.hmm> <target.pep> <idList.txt> <out.txt>
*   pfamA.hmm: Pfam-A.hmm 数据库（需已 hmmindex）
*   target.pep: 待扫描蛋白
*   idList.txt: 感兴趣 Pfam ID 列表（每行一个，如 GRAS）
*   out.txt: 输出
*
* 引擎: simpleHmmscan.setPfamHmmA/setTargetPep/setPfamIdList/setFinalOutFile + process()
*   （main 硬编码演示 → setter+process；调系统 hmmsearch）

```

### `StructAnnoCompareCli`

```
tbplot annoCompare — 注释版本对比管线 CLI（08/31 第五十二波）
*
* 用法: StructAnnoCompareCli <before.gff3> <after.gff3> <outDir> [runName] [reciprocalOverlap] [boundaryTol] [cdsChangePct] [utrChangePct] [geneScope] [overlapMode]
*   before/after.gff3: 同一基因组两个版本的注释
*   outDir: 输出目录（自动建）
*   runName: 运行名（默认 "annoCompare"）
*   reciprocalOverlap: 双向重叠阈值（默认 0.5）
*   boundaryTol: 边界容差（默认 100）
*   cdsChangePct / utrChangePct: CDS/UTR 变化百分比阈值（默认 0.1 / 0.1）
*   geneScope: all|mrna_only（默认 all）
*   overlapMode: reciprocal|any（默认 reciprocal）
*
* 产物: <runName>_change_summary.csv / _change_log.csv / tracks/*_annotation_changes.bed /
*       curation_summary_table.csv / curation_core_metrics.csv / figures/*_curation_summary_jigplot.{png,pdf,svg} /
*       figures/*_ABCD_single_species_jigplot.{png,pdf,svg}
*
* 引擎: StructAnnoCompareService.run(StructAnnoCompareConfig)（纯 headless，无弹窗）

```

### `SuperCircosCli`

```
SuperCircos CLI — 多轨道环形图
*
* 用法:
*   java -cp JAR:tbplot SuperCircosCli <config.cfg> <outFile> [width] [height]
*
* 配置格式（行导向，# 注释）:
*   [chrLen] <file>                    # 染色体长度文件: ChrName\tStart-End 或 ChrName\tLength
*   [link] <file>                      # 连接文件: ChrA\tStartA\tEndA\tChrB\tStartB\tEndB\t[Color]
*   [gene] <file>                      # 基因位置文件: Chr\tGeneName\tStart\tEnd
*   [track] <type> <file> <startPos> <endPos> <color1> <color2> <color3> <binSize> [fillColor] [drawColor]
*     type: Tile|Triangle|HeatMap|Point|Line|Bar|Arrow
*     color: RGB 格式 "255,0,0" 或 颜色名 RED|ORANGE|BLUE|YELLOW|CYAN|GREEN|BLACK|WHITE|GRAY|DARK_GRAY|LIGHT_GRAY
*   [width] <int>                      # 画布宽度 (默认 800)
*   [height] <int>                     # 画布高度 (默认 800)
*   [linkColor] <r,g,b>               # 连线颜色
*   [linkStroke] <float>              # 连线粗细 (默认 1.0)
*   [chrFillColor] <r,g,b>            # 染色体填充色
*   [chrLabelColor] <r,g,b>           # 染色体标签色
*   [chrLabelFont] <name> <style> <size>  # 染色体标签字体
*   [geneLabelShow] true|false        # 是否显示基因标签
*   [chrLabelShow] true|false         # 是否显示染色体标签
*   [chrBarShow] true|false           # 是否显示染色体条
*   [tickShow] true|false             # 是否显示刻度
*   [majorTickInterval] <int>         # 主刻度间隔 (bp)
*   [minorTickInterval] <int>         # 次刻度间隔 (bp)
*   [startAngle] <int>                # 起始角度
*   [endAngle] <int>                  # 结束角度
*   [circlize] true|false             # 是否环形

```

### `TableColManipCli`

```
TableColManipulator CLI bridge (engine 84)
* 表格列选择/筛选：根据列名从表中选择列输出
* Usage: TableColManipCli <inTable> <outTable> <colName1> [colName2 ...] [--sep tab|comma|space] [--header true|false] [--caseSensitive true|false]
*   inTable: 输入表格（支持 .gz）；colNames: 要保留的列名（表头）

```

### `TableCollapseCli`

```
tbplot tableCollapse — 表格按键折叠 CLI（08/29，第 63 引擎）
*
* 用法: TableCollapseCli <inTable> <keyColIndex> <outTable> [hasHeader true|false] [colSep]
*   inTable: 输入表格；keyColIndex: 折叠键列（0 起）
*   outTable: 按键折叠（同键行合并，值用分隔符连接）
*   hasHeader: 是否有表头（默认 true）
*   colSep: 分隔符（默认 \t）
*
* ⚠️ main() 硬编码路径——改走 setInTable/setKeyColumnIndex/setOutTable 等 setter + process()。

```

### `TargetScoreCli`

```
tbplot targetScore — miRNA 靶标打分 CLI（08/29，第 55 引擎）
*
* 用法: TargetScoreCli <in.ssearch36.m10> <outTable> [--scoreCutOff N] [--maxMismatch N] [--recCom true|false] [--revTargetSo true|false]
*   in.m10: ssearch36 官方参数输出（-w 100 -W 25 -E 1 -m 10 -i -U <mirna.fa> <target.fa>）
*   outTable: 靶标表（miRNA  target  strand  beg  end  score  miRNAseq  targetseq  E  bits）
*
* ⚠️ 关键坑（08/29 实锤）：
*   1. 必须 setCurAligner(Ssearch36)——默认 Fasta36 会 NPE（frame null）
*   2. ssearch36 必须带 -i（reverse-complement）才有 sw_frame 行
*   3. 完整管线：ssearch36 -i -m 10 → TargetScoreCli → 靶标表

```

### `TauCalcCli`

```
tbplot tauIndex — 组织特异性 τ 指数 CLI（08/29，第 59 引擎）
*
* 用法: TauCalcCli <inExpTab> <outTAU>
*   inExpTab: 表达矩阵（首列基因名 + 样本列）
*   outTAU: 每基因 Preferred Sample + TAU Index（0=均匀, 1=完全组织特异）
*
* ⚠️ main() 硬编码路径——改走 setInExpTab/setOutTAU + process()。
*    τ 指数：1 - Σ(1-x̂)/(n-1)，组织表达分析的通用特异性指标。

```

### `TreeCli`

```
tbplot tree — TBtools 树+注释图 CLI（08/29 重建）
*
* 用法: TreeCli <treeMeta.config> <out> [pad] [width] [height]
*   treeMeta.config: 行导向配置（# 注释）:
*     [TYPE]:Tree                # 树类型（必须）
*     [NEWICK]:<newick 同行>      # Newick 树（与 [NEWICK]: 同行，允许含冒号）
*     [setting]                  # 设置节（可选）
*     [TYPE]:TextAnno/HeatMap/BarPlot/Tile/StackBar/Domain/GeneStructure/Motifs/ManualAssigned <file> ...
*   pad: 面板间距（默认 20）
*
* 引擎: TreeTreeTree.showMeYourPower() 返回 ArrayList<JIGSubPanel>（各轨道）
*       （GRAS 12sp 树 926 叶 + TextAnno + HeatMap 轨道验证 SVG 1.19MB，08/28）

```

### `TreeRootingCli`

```
tbplot treeRooting — MAD 系统发育定根 CLI（08/29，第 49 引擎）
*
* 用法: TreeRootingCli <in.nwk> <out.nwk>
*   in.nwk: 未定根 NEWICK 树（单树）
*   out.nwk: MAD 定根后的 NEWICK 树
*
* ⚠️ MAD.main() 硬编码输入路径（args 被覆盖）——不能直接调 main。
*    改用公开静态入口 quickMadRoot(String)：NEWICK 字符串 → 定根后字符串。
*    算法引用：Tria et al. 2017, Nat Ecol Evol (MAD rooting, DOI:10.1038/s41559-017-0193)

```

### `TrimMSACli`

```
tbcli trimMSA 桥 — MSA 修剪 CLI（08/31）
*
* 用法: TrimMSACli <in.aln.fa> <out.aln.fa> [ratio]
*   in.aln.fa: 多序列比对 (Fasta)
*   out.aln.fa: 修剪后比对
*   ratio: 每列保留阈值 (默认 0.5)
*
* ⚠️ trimMSA.main 是硬编码演示路径（不走 ArgsParser）→ 桥直接用 setter + process()

```

### `UnrootedTreeCli`

```
tbplot unrooted — 无根树可视化 CLI（08/31 第六十四波）
*
* 用法: UnrootedTreeCli <in.nwk> <out> [layout] [width] [height] [iterations]
*   in.nwk: Newick 树文件
*   out:    .svg / .png / .pdf
*   layout: Circular|Radial|Force-Directed|Equal Angle|N-Body|Equal-Daylight（默认 Circular）
*   iterations: Force-Directed/N-Body 迭代次数（默认 200）
*
* 引擎: UnrootedTreePanelNew.loadNewickFile() → getJIGPanel() 返回 JIGBasePanel
*       （独立引擎，与已判死局的 UnrootedTreeViz 无关；08/31 攻下）

```

### `UpSetCli`

```
tbplot upset — TBtools UpSetPlot 交集图 CLI（08/29 重建）
*
* 用法: UpSetCli <sets.txt> <out.svg/png> [width] [height]
*   sets.txt: 每行 "集合名\t成员1\t成员2..."（tab 分隔，集合名后跟成员）
*   out: 输出 SVG/PNG（按扩展名判断）
*   width/height: 画布尺寸（默认 1000x800）
*
* 引擎: UpSetPlot.plot() 返回 JIGBasePanel（直接 save2Graph）

```

### `Venn5Cli`

```
tbplot venn5 — TBtools 五集合韦恩图 CLI（08/29 新增，第 29 引擎）
*
* 用法: Venn5Cli <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> [labelA] [labelB] [labelC] [labelD] [labelE]
*   每个 setN.txt: 每行一个成员 ID
*
* 引擎: Venn5（setInArrA~E + setTitleA~E + setOutGraph + getVennGraph）

```

### `Venn6Cli`

```
tbplot venn6 — TBtools 六集合韦恩图 CLI（08/29 新增，第 30 引擎）
*
* 用法: Venn6Cli <out> <setA.txt> ... <setF.txt> [labelA-F]
*   每个 setN.txt: 每行一个成员 ID
*
* 引擎: Venn6（setInArrA~F + setTitleA~F + setOutGraph + getVennGraph）

```

### `ViolinCli`

```
tbplot violin — 独立小提琴图 CLI（08/31 第六十五波）
*
* 用法: ViolinCli <in.tsv> <out> [width] [height]
*   in.tsv: 组别\t值（每行一个观测；第一行可作表头）
*   out:    .svg / .png / .pdf
*
* 引擎: ViolinPlot.generate() + saveToSVG/PNG/PDF（独立引擎，非 groupedbar VIOLIN 模式）

```

### `VisualizeCli`

```
tbplot visualizePseudoBlock — 伪共线性区块可视化 CLI（08/29，第 51 引擎）
*
* 用法: VisualizeCli <inBlockOut> <outGraph.pdf> [--labels "Genome1,Genome2"]
*   inBlockOut: FindBlockDual 输出（行=一个基因组区块; 基因格式 name(chr:start-end):strand[:matchIDs]）
*   outGraph:  输出 PDF（引擎只支持 PDF）
*   --labels:  每行对应的基因组标签（默认 Genome1,Genome2,...；不传则自动加）
*
* ⚠️ main() 硬编码 13 个 queryId 循环——改直接调 visualize(File outGraph)。
* ⚠️ Visualize 输入格式要求每行 `标签:基因1\t基因2...`（第一个冒号前是标签），
*    FindBlockDual 输出无标签 → 桥自动补齐（默认 Genome1/Genome2/...，或用 --labels 指定）。
*
* 例: VisualizeCli examples/data/findblockdual/block_Cr_Cs_real.out.txt out.pdf --labels "Camellia_reticulata,Camellia_sinensis"

```

### `VizGFACli`

```
VizGFACli — TBtools GFA 网络图 CLI（子任务 A 新增）
*
* 引擎链: GFAGraphLayout.process(gfa, w, h) → NetworkInfo → VizGFA.visualize(info, w, h) → JIGSubPanel
* GFA 格式（tab 分隔）:
*   S\t<nodeName>\t<sequence>          # 节点
*   L\t<from>\t<strand1>\t<to>\t<strand2>\t<overlap>   # 边
*
* 用法: VizGFACli <in.gfa> <out.svg|png> [width] [height]

```


## 五、已知坑（实测）

> 2026-08-31 全量回归测试（76 用例五波复测）实测踩中的参数格式坑，全部已验证修正。**调用前先扫一遍本表。**

- **hclust**: 输入是**三列距离文件** `GeneA\tGeneB\tdist`，**不是表达矩阵**！矩阵喂进去 NPE（CulateClusterDistance）
- **venn2/3/4**: **不是 tbplot.sh 命令**！开箱即用直接 java：`java -cp $TBTOOLS_JAR biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn2 --List1 a --List2 b --label1 A --label2 B --graph out.svg --prefix out --bgNum 30000`；venn3/venn4 **不认 --bgNum**（去掉）；venn4 类是 `Venn4Ellipse`
- **gel**: LaneLabels **逗号分隔**且**第一个标签给 marker 泳道**（共 1+N 个）；MarkerRange 逗号降序 `2000,1500,1000,750,500,250,100`；FragmentRangeArr 分号泳道/逗号片段 `798;1233,228;1688,1598`
- **supercircos**: 配置文件 `[chrLen] <文件路径>`——**后跟文件名**，非内联数据；[link]/[gene]/[track] 同理都指向文件；gene 文件列序 `Chr\tName\tStart\tEnd`
- **barplot**: termCol/pvalCol 是**列名**（如 `Term` / `Pvalue`），**不是列索引**（传 1 2 会 IndexOutOfBounds）
- **cubeheatmap / admixture**: group 文件**第一行会被当数据**（引擎不跳表头）→ 喂前先去表头
- **admixture**: 第一个参数是 qFiles.lst（**每行一个 Q 矩阵文件路径**），不是 Q 矩阵内容本身
- **dotplot**: --chrLayout 传**文件路径**（文件内容 `Genome: Chr1 Chr2...`，冒号分隔），不是内联字符串；染色体名须匹配简化 GFF
- **dualsyn**: 简化 GFF 染色体名**必须数字**（parseInt）；需显式 `--chr1/--chr2`；合成小数据时图尺寸小（引擎按元素边界定 SVG 尺寸）
- **microsyn**: 给 `--chr1/--chr2` 区域参数更稳（自动取全基因区也行）；collinearity 用 MCScanX 输出
- **peaktss**: 签名 `<gxf> <macs2_peak.xls> <out>`——**gxf 是必给第 1 参**，不给报用法错误
- **peakanno**: peak 用 **MACS2 格式**，位置取**第 5 列 abs_summit**（info[4]）；GFF 坐标范围太小（<10kb）与 binSize=10000 索引冲突→用真实范围 GFF
- **rpkmCal**: **不是 tbplot.sh 命令**，是 CLI 工具：`tbtools tool rpkmCal --countsTable x --lenInfo y --outTable z`
- **distance**: 方法名小写 `euclidean|pearson|pearsonDist`；**结果输出到 stdout**（不是文件）
- **goParse**: 产物写到**输入文件同目录**（`<输入名>.TBtools.Parsed.*` 三个文件），无独立输出参数
- **levelGo / goParse**: 需要本地 obo 文件（如 GSEABase 的 goslim_plant.obo）
- **pep2codon**: 参数顺序 `<cds.fa> <pep.aln.fa> <out>`（先 CDS 后蛋白比对）
- **motif**: 需**真 meme.xml** + 与 XML 序列 ID 匹配的 ID 列表（`grep -oP 'name="[^"]+"' meme.xml` 提取）
- **pafviz**: PAF 必须 **13 列**（split("\t",13)，不足 13 列 [12] 越界）
- **msy/microsyn/multisyn**: 简化 GFF 染色体名**必须数字**；msy 的基因名在第 2 列、坐标列不连 `-`；multisyn 的 gxf.lst 里路径不能是旧 /tmp/rebuild 硬编码
- **mcscanx**: gff 用简化格式（chr\tgene\tstart\tend），blast 用 tab6；`classify` 模式须同时给 collinearityFile + geneTypeFile
- **efpHeat / multiEfp**: TGA 底图必须 TrueColor(type2) 非灰度(type3)；需 build 里的 fake javax.xml.bind.DatatypeConverter（JDK9+ 无 jaxb）
- **annocompare**: 输入两个 GFF3 + 输出目录；生成 change_summary.csv + figures/*（纯 headless 直出）
- **onesteptree**: --bbTime 必须 ≥1000（iqtree 限制）；序列须 ≥4 条唯一（太相似会被 uniqueseq 合并报错）
- **simplehmmscan**: 类在 bioDoer.LinuxPipe（非 BioSoftPipeServer）；测试蛋白要选对（非目标家族蛋白 0 命中是正常的）
- **pairWiseKaKsCalculator**: CDS 头 ID 须与 gene pair 完全匹配（`>id` 无分隔符）
- **plotrna**: 必须带 `--directPDF` 否则弹窗；只支持 PDF 输出
- **mountain**: 输入 RNA fold 字符串（如 `.((((..))))..`）→ 每碱基山峰高度

## 六、engine 通用反射

万能兜底：驱动任意 TBtools 引擎，无需预先写桥。

```bash
tbtools engine <引擎完整类名> key=value [key=value...] [--call 方法1+方法2] [--out out.ext]

# 例：PCA 引擎（doPCA + postGraph 链式调用）
tbtools engine biocjava.bioDoer.JIGplotToolkit.PCAanalysis.PCAanalysis \
    --set inTabFile expr.tsv --set rowName true --set colName true \
    --set processDirect Rows --call doPCA+postGraph --out pca.svg

# 例：Venn2（带 --List1 等原生 ArgsParser 参数）
tbtools engine biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn2 \
    --List1 a.txt --List2 b.txt --label1 A --label2 B --graph out.svg --prefix out --bgNum 30000
```

支持的 setter 类型：File / String / int / double / boolean / Color / 枚举（自动推断）。`--call` 支持方法链（`doPCA+postGraph`）、JIGSubPanel 数组、`System.exit(0)` 防悬挂。

## 七、RPC 188 方法

```bash
tbtools rpc server start       # 启动 RPC 服务器（端口 8765）
tbtools rpc <方法名> '<json>'   # 调用任意方法
tbtools methods               # 列出 188 方法
tbtools heatmap <matrix> <out.png> [group]   # 热图快捷
```

完整方法参考（含参数/返回值）：**`docs/rpc_methods_reference.md`**（89KB，183+ 方法）。
