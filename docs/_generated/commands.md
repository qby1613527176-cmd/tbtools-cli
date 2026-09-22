# 命令全量清单（自动生成,勿手改）

> 由 `python3 scripts/gen_metadata.py --render` 生成,来源 command_metadata.json。
> 分组归类参考 cli_load.CATEGORY_MAP;数字防漂移由 gen_metadata.py --check 与 pytest 保证。

## asm — 组装/注释（10 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `bamMerge` | 直连 | 按区域覆盖合并 BAM（多样本择优） |
| `bamindex` | 桥 | bamindex <in.sorted.bam> [out.bai] |
| `bamsort` | 桥 | bamsort <in.bam> <out.bam> [sortOrder] [tmpDir] |
| `bamstate` | 桥 | bamstate <out.tsv> <gff3> <bam1> [<bam2> ...] |
| `ctgGroup` | 桥 | ctgGroup <in.miniprot.gff> <polyPoid> <outContigGrpMap> |
| `hicEnzyme` | 直连 | HiC 限制酶预测（第76引擎） |
| `homoPhase` | 直连 | homoPhase <inContigGrpMap> <outPhasedMap> |
| `preparespecies` | 直连 | preparespecies <prefix> <inGenome.fa> <inGFF> <outGenome.fa> |
| `sepChr` | 直连 | sepChr <gene2chr.tsv> <in.miniprot.gff> <outMap> |
| `virusRecomb` | 直连 | 病毒重组分析（第77引 |

## blast — BLAST/比对（6 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `blat` | 桥 | 42 BlatExecutor；org.ucsc.blat 纯 Java 实现内嵌 jar 无需外部二进制） |
| `filterCScore` | 直连 | filterCScore <in.blast.tab6> <out.tab6> [--cscore 0.5] |
| `findhomolog` | 直连 | 37 FindBestHomology，同引擎覆盖 GenomeAnnotationSlim+FindBestHomol |
| `quickFamily` | 直连 | quickFamily <refPep.fa> <familyIds.txt> <queryPep.fa> <outPr |
| `recipBlast` | 直连 | recipBlast <query.fa> <subject.fa> <outPrefix> [--queryIds i |
| `twoSeqBlast` | 直连 | twoSeqBlast <query.fa> <subject.fa> <out.txt> [--prog blastp |

## chipseq — ChIP-seq（4 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `peakanno` | 直连 | peakanno <gxf> <macs2_peak.xls> <out.tsv> [--dist N] |
| `peakdist` | 桥 | peakdist <chrLen.tsv> <macs2_peak.xls> <out> [--chrHeight H] |
| `peaktss` | 直连 | peaktss <gxf> <macs2_peak.xls> <out.svg/png> [--dist N] [--b |
| `pileup` | 桥 | pileup <blast.xml> <out.svg> [--query NAME] |

## engine — 通用（113 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `DecodeIlluminaFqPool` | 工具 |  |
| `ExtractFeaturefromGFF3andGenome` | 工具 |  |
| `Fasta36m10toTable` | 工具 |  |
| `FastaIDRenamer` | 工具 |  |
| `FastaIDSimplifier` | 工具 |  |
| `FastaLongestRepresentater` | 工具 |  |
| `FoldStructureStater` | 工具 |  |
| `GXFOverlaper` | 工具 |  |
| `GoCompareBar` | 工具 |  |
| `MIRPrediionResultStat` | 工具 |  |
| `NCBITaxonomy` | 工具 |  |
| `OneStepMirGraph` | 工具 |  |
| `OverlapGeneModels` | 工具 |  |
| `PredictMirSTAR` | 工具 |  |
| `RNAplotAdvance` | 工具 |  |
| `ReciprocalBlast` | 工具 |  |
| `RegionGXFOverlapAnnotation` | 工具 |  |
| `TableCast` | 工具 |  |
| `TableColSelector` | 工具 |  |
| `TableMelt` | 工具 |  |
| `admixture` | 桥 | admixture <qFiles.lst> <out> [sampleIDFile] [groupFile] [sor |
| `admixtureViz` | 桥 | ADMIXTURE Q 矩阵可视化（GUI 逆向接口；Q 文件纯数值矩阵，样本 ID 单独 --id） |
| `autoMakeBlastDb` | 工具 |  |
| `autoRemoteBlast` | 工具 |  |
| `bigMarkerRandomDesign` | 工具 |  |
| `blastXmlSummaryTable` | 工具 |  |
| `blastXmlToTable` | 工具 |  |
| `calcRepeat` | 桥 | calcRepeat <genome.fa> <outRepeat.txt> [--kmerSize N] [--min |
| `call` | 手动 |  |
| `cds2protein` | 手动 |  |
| `checkPrimer` | 工具 |  |
| `collinearityToRegion` | 工具 |  |
| `dnDsCalculate` | 工具 |  |
| `downLoadNCBIFasta` | 工具 |  |
| `draw` | 手动 |  |
| `eggNogMapperResult` | 工具 |  |
| `eggnog` | 桥 | eggNOG 直系同源注释（GUI 逆向接口 EmapperPipeline；⚠️ 需先就位 eggNOG 数据库） |
| `emblToFasta` | 工具 |  |
| `extractFasta` | 工具 |  |
| `extractFastaSub` | 工具 |  |
| `extractFeatureFromGTF` | 工具 |  |
| `extractGff3Region` | 工具 |  |
| `fastaFragmenter` | 工具 |  |
| `fastaIDAppender` | 工具 |  |
| `fastqAndFasta` | 工具 |  |
| `fastqParallelSubBest` | 工具 |  |
| `fastqParallelTrimmer` | 工具 |  |
| `filesplit` | 桥 | filesplit <inFile> <numParts> |
| `findBestForkerRootTree` | 工具 |  |
| `findBestHomologyBatch` | 工具 |  |
| `fpkmToTpm` | 工具 |  |
| `gbff2gff` | 工具 |  |
| `geneExpFilter` | 工具 |  |
| `genePairExpCorr` | 工具 |  |
| `generateMotifFromSequences` | 工具 |  |
| `generic` | 桥 | generic <engineClass> <method[+method2]> <out> [--set field |
| `getLongestCompleteORF` | 工具 |  |
| `getLongestORF` | 工具 |  |
| `gffCdsPhaseCorrector` | 工具 |  |
| `goAnnoPipe` | 工具 |  |
| `goEnrichMerge` | 工具 |  |
| `gsadiag` | 桥 | gsadiag <in.fixed.gff3> <out.stat.xls> [genome.fasta] [relax |
| `gxffilter` | 桥 | gxffilter <in.gff3|gtf> <idList.txt> <out.gff3|gtf> |
| `gxfsort` | 桥 | gxfsort <in.gff3|gtf> <out.sorted> |
| `heatmap` | 手动 |  |
| `heatmap2` | 手动 |  |
| `keggEnrichment` | 工具 |  |
| `logo` | 手动 |  |
| `makeFastaIndex` | 工具 |  |
| `marker` | 直连 | marker <MarkerDist|MarkerFilter|SampleDist|BigMarkerRandomDe |
| `markertools` | 桥 | markertools <filter|dist|sampledist> <in.marker.tab> [maxPoi |
| `methods` | 手动 |  |
| `mggxf` | 桥 | mggxf <inGenePair|blastTab6> <in.simplified.gff> <out.Linked |
| `mirIdentifierBasedOnTargetSo` | 工具 |  |
| `pafRefBaseCoverCalc` | 工具 |  |
| `pairWiseKaKsCalculator` | 工具 |  |
| `parallelMD5Check` | 工具 |  |
| `plotRNAfoldloci` | 工具 |  |
| `prepareFileFromMCScanXtoTBtools` | 工具 |  |
| `qpcrproc` | 桥 | qpcrproc <in.qpcr.tab> <out.xls> |
| `quickGeneFamilyIdentification` | 工具 |  |
| `quickLocateSeqPattern` | 工具 |  |
| `quickSplitFasta` | 工具 |  |
| `regionBlast` | 工具 |  |
| `regiondepth` | 桥 | regiondepth <in.sam> <region> <out.depth> [scaleFactor] |
| `rooting` | 手动 |  |
| `rpkmCal` | 工具 |  |
| `sRNAReadTrimmer` | 工具 |  |
| `sRNAseqAdaperRemover` | 工具 |  |
| `sRNAseqCollasper` | 工具 |  |
| `sRNAseqDeCollasper` | 工具 |  |
| `sRNAseqReadLenStat` | 工具 |  |
| `sambamcov` | 桥 | sambamcov <in.bam> <out.tsv> [binSize] [countMode] |
| `seqconvert` | 桥 | seqconvert -i <in> -o <out> -iF <fmt> -oF <fmt> |
| `seqlogo` | 手动 |  |
| `seqrecommend` | 桥 | 43 AssemblyGenomeDataSizeRecommand；纯计算离线；Hifi/HiC 深度+数据量） |
| `simpleBatchProcess` | 工具 |  |
| `slurmScriptPrepare` | 工具 |  |
| `ssrMiner` | 工具 |  |
| `start` | 手动 |  |
| `statFasta` | 工具 |  |
| `status` | 手动 |  |
| `stop` | 手动 |  |
| `structure` | 手动 |  |
| `tandemDupFinder` | 工具 |  |
| `target2TablePipe` | 工具 |  |
| `targetSoPipe` | 工具 |  |
| `tpmCalc` | 工具 |  |
| `translater` | 工具 |  |
| `tree` | 手动 | tree <treeMeta.config> <out> [pad] |
| `trimmsa` | 桥 | trimmsa <in.aln.fa> <out.aln.fa> [ratio] |
| `vcfBinCount` | 工具 |  |
| `volcano` | 手动 |  |

## expr — 表达/统计（20 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `barplot` | 桥 | barplot <enrichment.tsv> <out> <termCol> <pvalCol> [classCol |
| `barplotter` | 桥 | barplotter -g <gff> -s <synteny> -c <ctl> -o <out.png> |
| `colorscheme` | 桥 | colorscheme <inTab> <outTab> <refColIndex> |
| `cubeheatmap` | 桥 | group.tsv 引擎对列数有严格假设，官方 cube_group.tsv 仍会 ArrayIndexOutOfBou |
| `dehist` | 手动 |  |
| `distance` | 桥 | distance <in.tsv> <col1> <col2> <euclidean|pearson|pearsonDi |
| `efpHeat` | 直连 | efpHeat <inTGA> <sample2cc.txt> <expMat.tsv> <geneId> <out.s |
| `exprCorr` | 桥 | exprCorr <inFPKM> <outCorrMat> |
| `gbar` | 桥 | 分组柱状图+显著性标注（GUI 逆向接口 buildPanel；数据=每行 group value） |
| `groupCol` | 直连 | groupCol <inTable.tsv> <inGrpInfo.tsv> <outTable> [Sum|Mean| |
| `groupedbar` | 桥 | 数据格式=每行 <group>	<value>（重复行成组），非常规基因×样本矩阵；矩阵输入会在 GroupedBarR |
| `hclust` | 手动 |  |
| `layoutheatmap` | 桥 | layoutheatmap <layout.tsv> <expr.tsv> <out> [--options] |
| `mountain` | 桥 | mountain <fold.txt> <out.tsv> |
| `multiEfp` | 桥 | multiEfp <inTGA> <sample2cc> <expMat1[,expMat2,...]> <geneId |
| `pca` | 手动 |  |
| `qpcr` | 桥 | qpcr <data.txt> <out> [w] [h]   (data: name       mean    sd |
| `qpcrExp` | 桥 | qpcrExp <in.qpcr.tab> <out.xls> |
| `tauIndex` | 桥 | tauIndex <inExpTab> <outTAU> |
| `violin` | 桥 | violin <in.tsv> <out> [width] [height] |

## fastq — FASTQ/FASTA（4 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `fastaExtract` | 直连 | fastaExtract <in.fa> <idList.txt> <out.fa> [--mode Match|Con |
| `fastaSubseq` | 直连 | 按坐标提子序列（第92引擎，Ext |
| `fqTrim` | 直连 | fqTrim <in.fq> <out.fq> [--b5 N] [--b3 N] [--threads N] |
| `fqfaConv` | 直连 | FASTQ/FASTA 互转（第 |

## gwas — GWAS（2 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `mimicVqsr` | 直连 | VCF 质量指标（QD/MQ/FS/SOR；GWAS） |
| `vcfAddID` | 直连 | VCF 加 ID 列（GWAS；ArgsParser --inFile/--outFile，支持 .gz） |

## gxf — GXF/表格（18 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `annocompare` | 桥 | annocompare <before.gff3> <after.gff3> <outDir> [runName] [r |
| `bed2gff3` | 桥 | 链向:编码 如 G01:+:C；同 ID 多行合并出 mRNA+exon） |
| `gdensity` | 桥 | 基因密度 bin 分析（GUI 逆向接口 GeneDensityProfiler） |
| `genedensity` | 桥 | genedensity <in.gff3> <out.tsv> [binSize] |
| `genelocation` | 直连 | genelocation --ChrLen <chrlen> --FeaturePos <pos> --OutGraph |
| `genelocgff` | 桥 | genelocgff <gff3> <idList> <out> [--chrLen len.tsv] [--renam |
| `gxfAppend` | 直连 | GFF seqid+ID 加前缀 |
| `gxfFix` | 直连 | GFF 修复（重复ID前缀/CDS phase/dang |
| `gxfGenepos` | 直连 | G |
| `gxfMatch` | 直连 | gxfMatch <in.gff3> <inGenome.fa> |
| `gxfOverlap` | 直连 | gxfOverlap <in.gff3> <region.txt> <out.gff3> [--ignoreStrand |
| `gxfRecall` | 直连 | 从 gene 行恢复 mRNA 特征（第82引擎， |
| `gxfRegion` | 直连 | gxfRegion <in.gff3> <region.txt> <out.gff3> [--ignoreStrand] |
| `gxfRename` | 直连 | gxfRename <in.gff3> <out.gff3> <renameMap.tsv> |
| `gxfRepGXF` | 直连 | gxfRepGXF <in.gff3> <out.gff3> [--featureID CDS] [--attachID |
| `gxfRepIDs` | 直连 | gxfRepIDs <in.gff3> <out.txt> |
| `gxfStat` | 直连 | GFF 统计（基因/mRNA/外显子/内含子/C |
| `regionAnno` | 直连 | regionAnno <in.gff3> <region.txt> <outTab> [--flankLen N] [- |

## hmm — HMM（1 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `hmmExtract` | 直连 | 从 HMM 文件按 NAM |

## mirna — miRNA（3 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `mirnaIdentify` | 桥 | 78 MirIdentifyCli；⚠️ 第 4 参 outChecklog 必需，docstring 原漏写 N29） |
| `mirnaTarget2` | 直连 | mirnaTarget2 <mirna.fa> <target.fa> <out.txt> [--revCom true |
| `mirnatarget` | 桥 | mirnatarget <mirna.fa> <target.fa> <out.tsv> [--evalue X] [- |

## seq — 序列/结构/域（35 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `amazingmeta` | 桥 | amazingmeta <meme.xml> <newick.treefile> <out.svg|png|pdf> [ |
| `careclassify` | 桥 | 22；第8列 motif 名查 jar 内置 97 类表，行尾追加大类/亚类；查不到 NA） |
| `cddmotif` | 桥 | cddmotif <cdd.hitdata.txt> <in.fasta> <out.svg|png|pdf> [new |
| `famerge` | 桥 | 33 FastaMergerAndSpliter.Merge） |
| `fasplit` | 直连 | 33 QuickSpiltFasta；⚠️ 与 filesplit 不同：按记录不切行，产物 prefix.N.spli |
| `gb2fa` | 桥 | 36 genBank2Fasta；头含 locus/accession/organism/definition） |
| `gblocks` | 桥 | 30 Jgblocks 纯 Java 实现；main 仅 in/out 全参数须 setter；⚠️ 高歧异比对可能 v |
| `gel` | 直连 | 凝胶电泳图（GelImage.Marker；⚠️ 无参调用会挂起 N32） |
| `genestructure` | 手动 |  |
| `gfa` | 桥 | gfa <in.gfa> <out> [width] [height] |
| `gfa2fa` | 直连 | GFA 组装图 → FASTA（第91引擎，GFAtoFast |
| `longestorf` | 直连 | 17 GetLongestORF：setFastaFile/setOutFile/startPredict；自带 Arg |
| `makemotif` | 桥 | 等长序列→MEME motif 文件（GUI 逆向接口；产物可直接喂 fimo/mast） |
| `mast` | 桥 | MAST motif 搜索（GUI 逆向接口 QuickRunMAST，需系统 mast；产物 mast.html/tx |
| `mast2tab` | 桥 | mast2tab <mast|meme.xml> <out.tab> |
| `mastExtract` | 直连 | 从 MAST XML 提取命中 |
| `mastrun` | 桥 | mastrun <meme.xml> <seq.fasta> <workingDir> [--motifs M] [-- |
| `meme` | 桥 | MEME motif 发现（GUI 逆向接口 QuickRunMEME，需系统 meme；产物可与 memeViz/fi |
| `meme2tab` | 桥 | MEME/MAST XML→motif 域表（GUI 逆向接口 MEMESuiteXMLtoTab） |
| `memerun` | 桥 | memerun <in.fasta> <workingDir> [--motif N] [--minW N] [--ma |
| `motif` | 手动 |  |
| `mpattern` | 桥 | MEME/MAST motif 序列标注图（GUI 逆向接口，postGraph(String,panel) 重载绕弹窗 |
| `msa` | 手动 |  |
| `pep2codon` | 桥 | pep2codon <cds.fa> <pep.aln.fa> <codon.aln.out> |
| `pfammotif` | 桥 | pfammotif <pfamscan.txt> <in.fasta> <out.svg|png|pdf> [newic |
| `plotrna` | 直连 | plotrna <genomeFA> <region> <SAM> [--directPDF out.pdf] |
| `protparam` | 直连 | 18 ProtParamWrapper.batchCalc；⚠️ 联网 POST Expasy。输出：分子量/pI/不稳 |
| `protsim` | 桥 | 24 ProteinPairwiseSimilarityMatrixGUIPanel→CalculateSimilari |
| `rnaplot` | 桥 | rnaplot <seq.fa|rawSeq> <out> [--colorMap "seq1=R,G,B;seq2=R |
| `seqfetch` | 直连 | 44 NcbiSmartSeqFetchEntrezUtils；⚠️ 联网 Entrez+限速；ID 自动检测/转换/审 |
| `seqlentrack` | 桥 | seqlentrack <seqlen.txt> <out.svg|png|pdf> [newick.treefile] |
| `seqpattern` | 直连 | 20 QuickLocateSeqPattern：正则找模式→GFF3；--key value 空格分隔） |
| `simplehmmscan` | 桥 | simplehmmscan <pfamA.hmm> <target.pep> <idList.txt> <out.txt |
| `sixframe` | 桥 | 16 SixFrameTranlater：setInFile/setOutFile/process；输出每条序列 6 框 |
| `trimal` | 桥 | 29 QuickTrimAL；默认 automated1；依赖系统 trimal；muscle→trimal→iqtre |

## sets — 集合/韦恩（6 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `upset` | 桥 | UpSet 集合图（GUI 逆向接口 UpSetPlot.plot，绕 show 弹窗） |
| `venn2` | 直连 | venn2 --List1 <setA.txt> --List2 <setB.txt> --label1 A --lab |
| `venn3` | 直连 | venn3 --List1 <A> --List2 <B> --List3 <C> --label1..3 <label |
| `venn4` | 直连 | venn4 --List1 <A> --List2 <B> --List3 <C> --List4 <D> --labe |
| `venn5` | 桥 | venn5 <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <set |
| `venn6` | 桥 | venn6 <out> <setA..F.txt> [labels] |

## syn — 共线性/基因组（20 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `circlegene` | 桥 | circlegene <gff> <geneID.txt> <out> [--rename f --link f --r |
| `circos` | 桥 | circos <chrLen.txt> <link.txt> <genePos.txt> <outFile> [w] [ |
| `collinearRegion` | 直连 | collinearRegion <in.collinearity> <simGff> <out.txt> |
| `conflictpaf` | 直连 | conflictpaf <in.paf> <out.tsv> [binSize] |
| `dotplot` | 直连 | dotplot --inGff <gff> --genePair <pairs> --chrLayout <layout |
| `dualsyn` | 桥 | dualsyn <simplifiedGff> <collinearity> <out> [--chr1 "1,2"] |
| `findblockdual` | 桥 | findblockdual <queryGenome.fa> <query.gff> <subjectGenome.fa |
| `findblockmultiple` | 桥 | findblockmultiple <queryGenome.fa> <query.gff> <queryId> <ou |
| `mcscanx` | 桥 | 共线性检测 |
| `microgenome` | 直连 | microgenome <inGBK> <anno.tsv> <out> [micro|macro] |
| `microsyn` | 桥 | microsyn <gxf1> <gxf2> <collinearity> <out> [--chr1 C --star |
| `msy` | 桥 | msy <simplifiedGff.pos> <links.txt> <chrLayout.txt> <out> [w |
| `multisyn` | 桥 | multisyn <gxf.lst> <collinear.lst> <out> [--genes idlist.txt |
| `pafcomp` | 桥 | pafcomp --inPaf <paf> --outGraph <out> [--colorMode Target|Q |
| `pafref` | 直连 | pafref --inPaf <paf> --outTab <out.tsv> |
| `pafviz` | 桥 | PAF 比对 dot 图（GUI 逆向接口 PafViz.process，绕 quickShow） |
| `partitionconflict` | 直连 | partitionconflict <inConflictFreq.tsv> <polyPoid> <outCluste |
| `qdot` | 桥 | 基因组 dot plot（插件 P00380 CLI 化；blast/gff/chrLayout 可由 mcscanxd |
| `supercircos` | 桥 | supercircos <config.cfg> <out> [width] [height] |
| `visualizeblock` | 桥 | visualizeblock <inBlockOut> <out.pdf> [--labels "Genome1,Gen |

## table — GO/表格（24 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `batchReplace` | 直连 | batchReplace <inFile> <outFile> <patternMap.tsv> [--partial] |
| `clearchar` | 桥 | 34 FileCleaner.simplifyFile；非可打印 ASCII/非 tab→_，空白行跳过，逐行报告） |
| `goAnno` | 直连 | num; GO:num」；产物 outDir/<输入名>.xls） |
| `goEnrich` | 桥 | GO 富集分析（MF/CC/BP，P+BH 校正，G4 补齐） |
| `goParse` | 直连 | GO 词典解析（第103 |
| `golevel` | 桥 | GO 层级统计+柱状图（GUI 逆向接口；统计表纯逻辑，图需 xvfb） |
| `keggEnrich` | 桥 | KEGG 富集分析（G4 补齐，需真实 .keg 参考文件） |
| `levelGo` | 直连 | levelGo <gene2Go.txt> <outTable> <oboFile> [--level N] |
| `pubmed` | 桥 | 45 PubmedSearch.process；⚠️ 联网 eutils；输出期刊/标题/年份/IF/DOI 表） |
| `sranum2info` | 直连 | 41 BatchGetSRARecordInfo；⚠️ 联网 NCBI Entrez+限速；自带 ArgsParser； |
| `sraxml2tab` | 直连 | 40 ParseSRAXml2Table；自带 ArgsParser；离线 JDOM 解析；XML 从 efetch d |
| `sricher` | 桥 | 简单富集（GUI 逆向接口 SimpleEnricher，超几何+BH；goEnrich 轻量版无需 OBO） |
| `srr2ena` | 桥 | 39 GetENALinksOfSRR；⚠️ 联网 ENA filereport API+引擎自带 0~3s 限速；17 |
| `tableAppend` | 直连 | tableAppend <inTab1> <inTab |
| `tableCast` | 直连 | tableCast <inLong.txt> <outMatrix> |
| `tableColSel` | 直连 | tableColSel <inTable> <outTable> <idList.txt> [--mode Match| |
| `tableColSelect` | 桥 | tableColSelect <inTable> <outTable> <colName1> [colName2...] |
| `tableCollapse` | 桥 | tableCollapse <inTable> <keyColIndex> <outTable> [hasHeader |
| `tableMelt` | 直连 | 宽表转长表（第88引擎，TableMelt） |
| `tableMerge` | 直连 | 按键合并多个表格(TableMerger；⚠️ ArgsParser 式，旧 docstring 位置参数写法已废弃 N |
| `tableSplit` | 直连 | tableSplit <inTab> <outDir> [--colIndex N] [--suffix .txt] |
| `tableTranspose` | 直连 | 表格转置（第95引擎，TableTran |
| `tableUniq` | 直连 | tableUniq <inTab> <outFile> [--colIndex N] [--showFreq true| |
| `taxparse` | 桥 | 38 TaxonomyParserGUIPanel→NCBITaxonomy；⚠️ 联网 NCBI eutils；输出  |

## tree — 树/进化（10 个）

| 命令 | 类型 | 说明 |
|---|---|---|
| `degramdom` | 桥 | degramdom <in.tsv> [out.nwk] |
| `findpath` | 桥 | findpath --inGffArr <gff1,gff2,...> --inGenePairs <pairs> -- |
| `iqtree` | 桥 | 28 QuickRunIQtree；⚠️ UFBoot 须 ≥1000 否则引擎静默失败；产物 outPrefix.tr |
| `kaks` | 直连 | 成对 Ka/Ks 计算（GUI 逆向 PairWiseKaKsCalculator；自带 ArgsParser：--ke |
| `nwAlign` | 桥 | Needleman-Wunsch 全局比对（GUI 逆向接口 NeedleManWunschAlign；旧 Simple |
| `onesteptree` | 手动 | onesteptree --inPepFie <in.pep> --outFilePrefix <outDir> [-- |
| `phylotree` | 桥 | phylotree <in.nwk> <out> [vertical] [width] [height] |
| `subtree` | 桥 | 23 GetSubNewickTreeGUIPanel→PhyloTreeMan.getSubTree；--contai |
| `treeRooting` | 手动 |  |
| `unrooted` | 手动 |  |

## 统计

- 命令总数: 276
- bridge: 102
- tool: 80
- direct: 70
- manual: 24
