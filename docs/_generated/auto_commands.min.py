'auto_commands：命令实现层（表驱动化 v2）。\n\n144 个同构命令（86 bridge + 58 direct Java 调用）由 ENGINE_REGISTRY 数据驱动生成，\n13 个特殊实现手写保留（hmmsearch 转发 / gxfAttr 原生 / kallisto 二进制 / fimo 二进制 /\nnotung 插件 / newickRename 插件 / hmmerSearch / memeViz / gsea / tfbsShift /\nmcscanxd / quickAnno / smart —— 各含独立预检/环境/参考数据逻辑）。\n\ncli.py 通过 dir(_ac) 反射 _xxx_impl 名字注册命令，函数形态必须保留。\ndoc 值为旧模块运行时 __doc__（已含编译器 docstring 处理后的真实字符）。\n'
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from tbtools_cli.core import BUILD_DIR, JAR, ROOT, cp, ensure_bridge, run_java, run_plot, safe_temp
ENGINE_REGISTRY = [('admixture', 'bridge', 'AdmixtureCli', '3g', 'plot', 'admixture: admixture <qFiles.lst> <out> [sampleIDFile] [groupFile] [sor'), ('admixtureViz', 'bridge', 'AdmixtureCli', '3g', 'plot', 'admixtureViz: admixtureViz <q1.txt> <q2.txt> [<q3.txt>...] <out.svg> [--id samples.txt] [--group group.txt] [--sort Qraito|Lexical|None]   # ADMIXTURE Q 矩阵可视化（GUI 逆向接口；Q 文件纯数值矩阵，样本 ID 单独 --id）'), ('amazingmeta', 'bridge', 'AmazingMetaCli', '3g', 'plot', 'amazingmeta: amazingmeta <meme.xml> <newick.treefile> <out.svg|png|pdf> ['), ('annocompare', 'bridge', 'StructAnnoCompareCli', '3g', 'plot', 'annocompare: annocompare <before.gff3> <after.gff3> <outDir> [runName] [r'), ('bamMerge', 'direct', 'biocjava.bioDoer.GenomeAnnotation.BAMMergeByRegionCoverage', '3g', 'plot', 'bamMerge: bamMerge <gtf> <bamDir> <outDir>   # 按区域覆盖合并 BAM（多样本择优）'), ('bamindex', 'bridge', 'BamIndexCli', '3g', 'plot', 'bamindex: bamindex <in.sorted.bam> [out.bai]'), ('bamsort', 'bridge', 'BamSortCli', '3g', 'plot', 'bamsort: bamsort <in.bam> <out.bam> [sortOrder] [tmpDir]'), ('bamstate', 'bridge', 'BamStateCli', '3g', 'plot', 'bamstate: bamstate <out.tsv> <gff3> <bam1> [<bam2> ...]'), ('barplot', 'bridge', 'BarplotCli', '3g', 'plot', 'barplot: barplot <enrichment.tsv> <out> <termCol> <pvalCol> [classCol'), ('barplotter', 'bridge', 'BarPlotterCli', '3g', 'plot', 'barplotter: barplotter -g <gff> -s <synteny> -c <ctl> -o <out.png>'), ('batchReplace', 'direct', 'biocjava.bioDoer.Table.BatchStringReplace', '3g', 'plot', 'batchReplace: batchReplace <inFile> <outFile> <patternMap.tsv> [--partial]'), ('calcRepeat', 'bridge', 'CalcRepeatCli', '3g', 'plot', 'calcRepeat: calcRepeat <genome.fa> <outRepeat.txt> [--kmerSize N] [--min'), ('cddmotif', 'bridge', 'CddMotifCli', '3g', 'plot', 'cddmotif: cddmotif <cdd.hitdata.txt> <in.fasta> <out.svg|png|pdf> [new'), ('circlegene', 'bridge', 'CircleGeneViewerCli', '3g', 'plot', 'circlegene: circlegene <gff> <geneID.txt> <out> [--rename f --link f --r'), ('circos', 'bridge', 'CircosCli', '3g', 'plot', 'circos: circos <chrLen.txt> <link.txt> <genePos.txt> <outFile> [w] ['), ('collinearRegion', 'direct', 'biocjava.bioDoer.ComparativeGenomics.MCScanX.CollinearityToRegion', '3g', 'plot', 'collinearRegion: collinearRegion <in.collinearity> <simGff> <out.txt>'), ('colorscheme', 'bridge', 'ColorSchemeCli', '3g', 'plot', 'colorscheme: colorscheme <inTab> <outTab> <refColIndex>'), ('conflictpaf', 'direct', 'biocjava.bioDoer.GenomeAssembly.CalculateConflictByRefAlignPAF', '3g', 'plot', 'conflictpaf: conflictpaf <in.paf> <out.tsv> [binSize]'), ('ctgGroup', 'bridge', 'CtgGroupCli', '3g', 'plot', 'ctgGroup: ctgGroup <in.miniprot.gff> <polyPoid> <outContigGrpMap>'), ('cubeheatmap', 'bridge', 'CubeHeatmapCli', '3g', 'plot', 'cubeheatmap: cubeheatmap <expr.tsv> <group.tsv> <out> [--log10 --minColor <c> --midColor <c> --maxColor <c>]   # 3D 立方体热图（N4: group.tsv 引擎对列数有严格假设，官方 cube_group.tsv 仍会 ArrayIndexOutOfBounds——引擎缺陷；喂分组格式: 行=样本/基因，列数须与引擎预期一致，建议先 tbtools check）'), ('degramdom', 'bridge', 'DegramdomCli', '3g', 'plot', 'degramdom: degramdom <in.tsv> [out.nwk]'), ('distance', 'bridge', 'DistanceCli', '3g', 'plot', 'distance: distance <in.tsv> <col1> <col2> <euclidean|pearson|pearsonDi'), ('dotplot', 'direct', 'biocjava.bioDoer.JIGplotToolkit.DotPlot.dotdotdot', '3g', 'plot', 'dotplot: dotplot --inGff <gff> --genePair <pairs> --chrLayout <layout'), ('dualsyn', 'bridge', 'DualSynCli', '3g', 'plot', 'dualsyn: dualsyn <simplifiedGff> <collinearity> <out> [--chr1 "1,2"] '), ('efpHeat', 'direct', 'biocjava.bioDoer.SimpleEfpBrowser.generateSuperHeatMap', '3g', 'plot', 'efpHeat: efpHeat <inTGA> <sample2cc.txt> <expMat.tsv> <geneId> <out.s'), ('eggnog', 'bridge', 'EggnogCli', '4g', 'java', 'eggnog: eggnog <in.fa> -o <prefix> --output_dir <outDir> --data_dir <eggNOGdb> [--cpu N] [--evalue 0.001]   # eggNOG 直系同源注释（GUI 逆向接口 EmapperPipeline；⚠️ 需先就位 eggNOG 数据库）'), ('exprCorr', 'bridge', 'ExprCorrCli', '3g', 'plot', 'exprCorr: exprCorr <inFPKM> <outCorrMat>'), ('fastaExtract', 'direct', 'biocjava.bioDoer.Fasta.ExtractFasta', '3g', 'plot', 'fastaExtract: fastaExtract <in.fa> <idList.txt> <out.fa> [--mode Match|Con'), ('fastaSubseq', 'direct', 'biocjava.bioDoer.Fasta.ExtractFastaSubseq', '3g', 'plot', 'fastaSubseq: fastaSubseq <in.fa> <pos.txt> <out.fa>   # 按坐标提子序列（第92引擎，Ext'), ('filesplit', 'bridge', 'FileSplitCli', '3g', 'plot', 'filesplit: filesplit <inFile> <numParts>'), ('filterCScore', 'direct', 'biocjava.bioDoer.BLAST.FilterBlastResultByCScore', '3g', 'plot', 'filterCScore: filterCScore <in.blast.tab6> <out.tab6> [--cscore 0.5]'), ('findblockdual', 'bridge', 'FindBlockDualCli', '3g', 'plot', 'findblockdual: findblockdual <queryGenome.fa> <query.gff> <subjectGenome.fa'), ('findblockmultiple', 'bridge', 'FindBlockMultipleCli', '3g', 'plot', 'findblockmultiple: findblockmultiple <queryGenome.fa> <query.gff> <queryId> <ou'), ('findpath', 'bridge', 'FindPathCli', '3g', 'plot', 'findpath: findpath --inGffArr <gff1,gff2,...> --inGenePairs <pairs> --'), ('fqTrim', 'direct', 'biocjava.bioDoer.Fastq.FastqParallelTrimmer', '3g', 'plot', 'fqTrim: fqTrim <in.fq> <out.fq> [--b5 N] [--b3 N] [--threads N]'), ('fqfaConv', 'direct', 'biocjava.bioDoer.LinuxPipe.FastqAndFasta', '3g', 'plot', 'fqfaConv: fqfaConv <input> <output> <fq2fa|fa2fq>   # FASTQ/FASTA 互转（第'), ('gbar', 'bridge', 'GroupedBarCli', '3g', 'plot', 'gbar: gbar <data.tsv> <out.svg> [--header|--no-header] [--errorbar SEM|SD|CI95] [--plot BAR_ERROR|BOXPLOT|VIOLIN|SWARM] [--homoscedastic-t]   # 分组柱状图+显著性标注（GUI 逆向接口 buildPanel；数据=每行 group value）'), ('gdensity', 'bridge', 'GeneDensityCli', '3g', 'java', 'gdensity: gdensity <in.gff3> <out.geneRecords> <binSize> [--feature <tag>] [--chrlen <file>]   # 基因密度 bin 分析（GUI 逆向接口 GeneDensityProfiler）'), ('gel', 'direct', 'biocjava.bioDoer.JIGplotToolkit.GelImage.Marker', '3g', 'plot', 'gel: gel <FragmentRangeArr> <LaneLabels> <MarkerRange> <out>   # 凝胶电泳图（GelImage.Marker；⚠️ 无参调用会挂起 N32）'), ('genedensity', 'bridge', 'GeneDensityCli', '3g', 'plot', 'genedensity: genedensity <in.gff3> <out.tsv> [binSize]'), ('genelocation', 'direct', 'biocjava.bioDoer.JIGplotToolkit.GeneLocation.GeneLocation', '3g', 'plot', 'genelocation: genelocation --ChrLen <chrlen> --FeaturePos <pos> --OutGraph'), ('genelocgff', 'bridge', 'GeneLocGffCli', '3g', 'plot', 'genelocgff: genelocgff <gff3> <idList> <out> [--chrLen len.tsv] [--renam'), ('generic', 'bridge', 'GenericCli', '3g', 'plot', 'generic: generic <engineClass> <method[+method2]> <out> [--set field '), ('gfa', 'bridge', 'VizGFACli', '3g', 'plot', 'gfa: gfa <in.gfa> <out> [width] [height]'), ('gfa2fa', 'direct', 'biocjava.bioDoer.Fasta.Tools.GFAtoFasta', '3g', 'plot', 'gfa2fa: gfa2fa <in.gfa> <out.fa>   # GFA 组装图 → FASTA（第91引擎，GFAtoFast'), ('goEnrich', 'bridge', 'GoEnrichCli', '4g', 'java', 'goEnrich: goEnrich <go.obo> <gene2go.tsv> <selectGenes.txt> <outDir>   # GO 富集分析（MF/CC/BP，P+BH 校正，G4 补齐）'), ('goParse', 'direct', 'biocjava.bioDoer.GeneOntology.littleTools.GOtermParser', '3g', 'plot', 'goParse: goParse <gene2Go.txt> <oboFile> [--level N]   # GO 词典解析（第103'), ('golevel', 'bridge', 'GoLevelCli', '3g', 'plot', 'golevel: golevel <go.obo> <gene2go.tsv> <outPrefix> [--level N] [--graph] [--width W] [--height H]   # GO 层级统计+柱状图（GUI 逆向接口；统计表纯逻辑，图需 xvfb）'), ('groupCol', 'direct', 'biocjava.bioDoer.Table.TableColCollaspe', '3g', 'plot', 'groupCol: groupCol <inTable.tsv> <inGrpInfo.tsv> <outTable> [Sum|Mean|'), ('groupedbar', 'bridge', 'GroupedBarCli', '3g', 'plot', 'groupedbar: groupedbar <data.tsv> <out> [plotType] [errorBarType] [hasHeader] [title]   # 分组柱状图（N5: 数据格式=每行 <group>\t<value>（重复行成组），非常规基因×样本矩阵；矩阵输入会在 GroupedBarRawData.load 崩溃——引擎缺陷）'), ('gsadiag', 'bridge', 'GsaDiagCli', '3g', 'plot', 'gsadiag: gsadiag <in.fixed.gff3> <out.stat.xls> [genome.fasta] [relax'), ('gxfAppend', 'direct', 'biocjava.bioDoer.GXFUtils.GxfIDAppender', '3g', 'plot', 'gxfAppend: gxfAppend <in.gff3> <out.gff3> <prefix>   # GFF seqid+ID 加前缀'), ('gxfFix', 'direct', 'biocjava.bioDoer.GXFUtils.GXFfixer.GXFFix', '3g', 'plot', 'gxfFix: gxfFix <in.gff3> <out.gff3>   # GFF 修复（重复ID前缀/CDS phase/dang'), ('gxfGenepos', 'direct', 'biocjava.bioDoer.GXFUtils.GXFToGenePosFile', '3g', 'plot', 'gxfGenepos: gxfGenepos <in.gff3> <outGenepos> <outChrLen> [feature]  # G'), ('gxfMatch', 'direct', 'biocjava.bioDoer.GXFUtils.GxfGenomeMatch', '3g', 'plot', 'gxfMatch: gxfMatch <in.gff3> <inGenome.fa>'), ('gxfOverlap', 'direct', 'biocjava.bioDoer.GXFUtils.GXFOverlaper', '3g', 'plot', 'gxfOverlap: gxfOverlap <in.gff3> <region.txt> <out.gff3> [--ignoreStrand'), ('gxfRecall', 'direct', 'biocjava.bioDoer.GXFUtils.RecallmRNAFeature', '3g', 'plot', 'gxfRecall: gxfRecall <in.gff3> <out.gff3>   # 从 gene 行恢复 mRNA 特征（第82引擎，'), ('gxfRegion', 'direct', 'biocjava.bioDoer.GXFUtils.GXFRegionSummary', '3g', 'plot', 'gxfRegion: gxfRegion <in.gff3> <region.txt> <out.gff3> [--ignoreStrand]'), ('gxfRename', 'direct', 'biocjava.bioDoer.GXFUtils.GXFRenamer', '3g', 'plot', 'gxfRename: gxfRename <in.gff3> <out.gff3> <renameMap.tsv>'), ('gxfRepGXF', 'direct', 'biocjava.bioDoer.GXFUtils.GXFToRepresentativeGXF', '3g', 'plot', 'gxfRepGXF: gxfRepGXF <in.gff3> <out.gff3> [--featureID CDS] [--attachID'), ('gxfRepIDs', 'direct', 'biocjava.bioDoer.GXFUtils.GXFToRepresentativeIDs', '3g', 'plot', 'gxfRepIDs: gxfRepIDs <in.gff3> <out.txt>'), ('gxfStat', 'direct', 'biocjava.bioDoer.GXFUtils.GXFfixer.GXFstat', '3g', 'plot', 'gxfStat: gxfStat <in.gff3> <outStat.xls>   # GFF 统计（基因/mRNA/外显子/内含子/C'), ('gxffilter', 'bridge', 'GxfFilterCli', '3g', 'plot', 'gxffilter: gxffilter <in.gff3|gtf> <idList.txt> <out.gff3|gtf>'), ('gxfsort', 'bridge', 'GxfSortCli', '3g', 'plot', 'gxfsort: gxfsort <in.gff3|gtf> <out.sorted>'), ('hicEnzyme', 'direct', 'biocjava.bioDoer.GenomeAssembly.HiCRestrictionEnzymePrediction', '3g', 'plot', 'hicEnzyme: hicEnzyme <inHiC.fastq>   # HiC 限制酶预测（第76引擎）'), ('hmmExtract', 'direct', 'biocjava.bioDoer.LinuxPipe.hmmInfoExtracter', '3g', 'plot', 'hmmExtract: hmmExtract <in.hmm> <idList.txt> <out.hmm>   # 从 HMM 文件按 NAM'), ('homoPhase', 'direct', 'biocjava.bioDoer.GenomeAssembly.HomoConflictBasedPartition', '3g', 'plot', 'homoPhase: homoPhase <inContigGrpMap> <outPhasedMap>'), ('keggEnrich', 'bridge', 'KeggEnrichCli', '4g', 'java', 'keggEnrich: keggEnrich <reference.keg> <annotation.tsv> <selectIds.txt> <out.xls>   # KEGG 富集分析（G4 补齐，需真实 .keg 参考文件）'), ('layoutheatmap', 'bridge', 'LayoutHeatmapCli', '3g', 'plot', 'layoutheatmap: layoutheatmap <layout.tsv> <expr.tsv> <out> [--options]'), ('levelGo', 'direct', 'biocjava.bioDoer.GeneOntology.Grapher.LevelDoer', '3g', 'plot', 'levelGo: levelGo <gene2Go.txt> <outTable> <oboFile> [--level N]'), ('makemotif', 'bridge', 'MakeMotifCli', '3g', 'java', 'makemotif: makemotif <in.seqs.txt> <out.meme> [--mol DNA|RNA|Protein]   # 等长序列→MEME motif 文件（GUI 逆向接口；产物可直接喂 fimo/mast）'), ('marker', 'direct', 'biocjava.bioDoer.markerDesign.BigMarkerRandomDesign', '3g', 'plot', 'marker: marker <MarkerDist|MarkerFilter|SampleDist|BigMarkerRandomDe'), ('markertools', 'bridge', 'MarkerToolsCli', '3g', 'plot', 'markertools: markertools <filter|dist|sampledist> <in.marker.tab> [maxPoi'), ('mast', 'bridge', 'MastCli', '3g', 'java', 'mast: mast <sequence.fa> <motifs.meme|meme.xml> <workingDir> [--motif-to-use N] [--max-motif-pvalue 0.0001] [--max-seq-evalue 10]   # MAST motif 搜索（GUI 逆向接口 QuickRunMAST，需系统 mast；产物 mast.html/txt/xml）'), ('mast2tab', 'bridge', 'Mast2TabCli', '3g', 'plot', 'mast2tab: mast2tab <mast|meme.xml> <out.tab>'), ('mastExtract', 'direct', 'biocjava.bioDoer.MEME.ExtractSeq.ExtractSeqFromMastXML', '3g', 'plot', 'mastExtract: mastExtract <in.fa> <mast.xml> <out.txt>   # 从 MAST XML 提取命中'), ('mastrun', 'bridge', 'MastRunCli', '3g', 'plot', 'mastrun: mastrun <meme.xml> <seq.fasta> <workingDir> [--motifs M] [--'), ('mcscanx', 'bridge', 'MCScanXCli', '3g', 'plot', 'mcscanx: mcscanx <gff> <blast> <outPrefix> [--html]   # 共线性检测'), ('meme', 'bridge', 'MemeCli', '3g', 'java', 'meme: meme <in.fa> <workingDir> <outMemeXml> [--nmotifs N] [--minw N] [--maxw N] [--evt 0.05] [--mod zoops|oops|anr]   # MEME motif 发现（GUI 逆向接口 QuickRunMEME，需系统 meme；产物可与 memeViz/fimo 串联）'), ('meme2tab', 'bridge', 'Meme2TabCli', '3g', 'java', 'meme2tab: meme2tab <meme.xml|mast.xml> <out.tab>   # MEME/MAST XML→motif 域表（GUI 逆向接口 MEMESuiteXMLtoTab）'), ('memerun', 'bridge', 'MemeRunCli', '3g', 'plot', 'memerun: memerun <in.fasta> <workingDir> [--motif N] [--minW N] [--ma'), ('mggxf', 'bridge', 'MgGxfCli', '3g', 'plot', 'mggxf: mggxf <inGenePair|blastTab6> <in.simplified.gff> <out.Linked'), ('microgenome', 'direct', 'biocjava.bioDoer.JIGplotToolkit.MicroGenomeViz.MicroGenomeAnnotationCircosPlot', '3g', 'plot', 'microgenome: microgenome <inGBK> <anno.tsv> <out> [micro|macro]'), ('microsyn', 'bridge', 'MicroSynCli', '3g', 'plot', 'microsyn: microsyn <gxf1> <gxf2> <collinearity> <out> [--chr1 C --star'), ('mirnaIdentify', 'bridge', 'MirIdentifyCli', '3g', 'plot', 'mirnaIdentify: mirnaIdentify <genome.fa> <targetSo.tsv> <outPredict.txt> <outChecklog.txt> [--checkARM BOTH|FIVE|THREE] [--maxAsy N] [--maxBulge N]   # miRNA 前体鉴定（GUI 逆向 #78 MirIdentifyCli；⚠️ 第 4 参 outChecklog 必需，docstring 原漏写 N29）'), ('mirnaTarget2', 'direct', 'biocjava.bioDoer.miRNA.Target2TablePipe', '3g', 'plot', 'mirnaTarget2: mirnaTarget2 <mirna.fa> <target.fa> <out.txt> [--revCom true'), ('mountain', 'bridge', 'MountainPlotCli', '3g', 'plot', 'mountain: mountain <fold.txt> <out.tsv>'), ('mpattern', 'bridge', 'MotifPatternCli', '3g', 'plot', 'mpattern: mpattern <mast.xml> <out.svg> [--max-motif N] [--shape RoundRect|Rect|Oval] [--line Middle|Up|Down|Splice] [--gradient] [--show-num]   # MEME/MAST motif 序列标注图（GUI 逆向接口，postGraph(String,panel) 重载绕弹窗）'), ('multiEfp', 'bridge', 'MultiSuperHeatCli', '3g', 'plot', 'multiEfp: multiEfp <inTGA> <sample2cc> <expMat1[,expMat2,...]> <geneId'), ('multisyn', 'bridge', 'SeveralSpeciesCli', '3g', 'plot', 'multisyn: multisyn <gxf.lst> <collinear.lst> <out> [--genes idlist.txt'), ('nwAlign', 'bridge', 'NeedlemanWunschCli', '3g', 'plot', 'nwAlign: nwAlign <seq1.fa> <seq2.fa> <out> [--protein|--dna] [--format EMBOSS|FASTA] [--gap-open N] [--gap-extend N] [--end-gap-open N] [--end-gap-extend N] [--end-weight]   # Needleman-Wunsch 全局比对（GUI 逆向接口 NeedleManWunschAlign；旧 SimpleBatchProcess 静默无产物已替换）'), ('pafcomp', 'bridge', 'PafGC', '3g', 'plot', 'pafcomp: pafcomp --inPaf <paf> --outGraph <out> [--colorMode Target|Q'), ('pafref', 'direct', 'biocjava.bioDoer.JIGplotToolkit.Paf.PafRefBaseCoverCalc', '3g', 'plot', 'pafref: pafref --inPaf <paf> --outTab <out.tsv>'), ('pafviz', 'bridge', 'PafVizCli', '3g', 'plot', 'pafviz: pafviz <in.paf> <out.svg> [--graph-size N] [--color Target|Query|None] [--seed N] [--min-len N] [--switch-qnt] [--rc-color]   # PAF 比对 dot 图（GUI 逆向接口 PafViz.process，绕 quickShow）'), ('partitionconflict', 'direct', 'biocjava.bioDoer.GenomeAssembly.ParititionByConflictFreq', '3g', 'plot', 'partitionconflict: partitionconflict <inConflictFreq.tsv> <polyPoid> <outCluste'), ('peakanno', 'direct', 'biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakAnno', '3g', 'plot', 'peakanno: peakanno <gxf> <macs2_peak.xls> <out.tsv> [--dist N]'), ('peakdist', 'bridge', 'PeakDistCli', '3g', 'plot', 'peakdist: peakdist <chrLen.tsv> <macs2_peak.xls> <out> [--chrHeight H]'), ('peaktss', 'direct', 'biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakTssHeatMap', '3g', 'plot', 'peaktss: peaktss <gxf> <macs2_peak.xls> <out.svg/png> [--dist N] [--b'), ('pep2codon', 'bridge', 'Pep2CodonCli', '3g', 'plot', 'pep2codon: pep2codon <cds.fa> <pep.aln.fa> <codon.aln.out>'), ('pfammotif', 'bridge', 'PfamMotifCli', '3g', 'plot', 'pfammotif: pfammotif <pfamscan.txt> <in.fasta> <out.svg|png|pdf> [newic'), ('phylotree', 'bridge', 'PhyloTreeCli', '3g', 'plot', 'phylotree: phylotree <in.nwk> <out> [vertical] [width] [height]'), ('pileup', 'bridge', 'PileUpCli', '3g', 'plot', 'pileup: pileup <blast.xml> <out.svg> [--query NAME]'), ('plotrna', 'direct', 'biocjava.bioDoer.JIGplotToolkit.miRCoverage.PlotRNAfold', '3g', 'plot', 'plotrna: plotrna <genomeFA> <region> <SAM> [--directPDF out.pdf]'), ('preparespecies', 'direct', 'biocjava.bioDoer.ComparativeGenomics.PrepareSpecies', '3g', 'plot', 'preparespecies: preparespecies <prefix> <inGenome.fa> <inGFF> <outGenome.fa>'), ('qdot', 'bridge', 'QuickGenomeDotCli', '3g', 'plot', 'qdot: qdot <blast.tab> <in.gff> <chrLayout.txt> <out.svg> [--point-size N] [--highlight genes.txt]   # 基因组 dot plot（插件 P00380 CLI 化；blast/gff/chrLayout 可由 mcscanxd 产出，绕开插件 quickShow GUI 崩溃直驱 dotdotdot）'), ('qpcr', 'bridge', 'QpcrCli', '3g', 'plot', 'qpcr: qpcr <data.txt> <out> [w] [h]   (data: name       mean    sd)'), ('qpcrExp', 'bridge', 'QpcrDdctCli', '3g', 'plot', 'qpcrExp: qpcrExp <in.qpcr.tab> <out.xls>'), ('qpcrproc', 'bridge', 'QpcrProcCli', '3g', 'plot', 'qpcrproc: qpcrproc <in.qpcr.tab> <out.xls>'), ('quickFamily', 'direct', 'biocjava.bioDoer.BLAST.ReciprocalBlast.QuickGeneFamilyIdentification', '3g', 'plot', 'quickFamily: quickFamily <refPep.fa> <familyIds.txt> <queryPep.fa> <outPr'), ('recipBlast', 'direct', 'biocjava.bioDoer.BLAST.ReciprocalBlast.ReciprocalBlast', '3g', 'plot', 'recipBlast: recipBlast --querySeqFile q.fa --subjectSeqFile s.fa --outDirAndPrefix outPrefix [--queryIdListFile ids.txt] [--evalue 1e-5] [--NumOfthreads 4]   # RBH 双向最优比对（ArgsParser 风格：参数必须 --key value 形态；依赖系统 blastp/makeblastdb）'), ('regionAnno', 'direct', 'biocjava.bioDoer.GXFUtils.RegionGXFOverlapAnnotation', '3g', 'plot', 'regionAnno: regionAnno <in.gff3> <region.txt> <outTab> [--flankLen N] [-'), ('regiondepth', 'bridge', 'RegionDepthCli', '3g', 'plot', 'regiondepth: regiondepth <in.sam> <region> <out.depth> [scaleFactor]'), ('rnaplot', 'bridge', 'RNAplotCli', '3g', 'plot', 'rnaplot: rnaplot <seq.fa|rawSeq> <out> [--colorMap "seq1=R,G,B;seq2=R'), ('sambamcov', 'bridge', 'SamBamCovCli', '3g', 'plot', 'sambamcov: sambamcov <in.bam> <out.tsv> [binSize] [countMode]'), ('sepChr', 'direct', 'biocjava.bioDoer.GenomeAssembly.SeperateChrByAlleles', '3g', 'plot', 'sepChr: sepChr <gene2chr.tsv> <in.miniprot.gff> <outMap>'), ('seqconvert', 'bridge', 'SeqConverterCli', '3g', 'plot', 'seqconvert: seqconvert -i <in> -o <out> -iF <fmt> -oF <fmt>'), ('seqlentrack', 'bridge', 'SeqLenTrackCli', '3g', 'plot', 'seqlentrack: seqlentrack <seqlen.txt> <out.svg|png|pdf> [newick.treefile]'), ('simplehmmscan', 'bridge', 'SimpleHmmscanCli', '3g', 'plot', 'simplehmmscan: simplehmmscan <pfamA.hmm> <target.pep> <idList.txt> <out.txt'), ('sricher', 'bridge', 'SimpleEnricherCli', '3g', 'java', 'sricher: sricher <in.tsv> <out.xls> <totalAnnoIdx> <totalHitIdx> <selAnnoIdx> <selHitIdx> [--header]   # 简单富集（GUI 逆向接口 SimpleEnricher，超几何+BH；goEnrich 轻量版无需 OBO）'), ('supercircos', 'bridge', 'SuperCircosCli', '3g', 'plot', 'supercircos: supercircos <config.cfg> <out> [width] [height]'), ('tableAppend', 'direct', 'biocjava.bioDoer.Table.TableAppend', '3g', 'plot', 'tableAppend: tableAppend <inTab1> <inTab2> <outTab> [--c1 N] [--c2 N]   #'), ('tableCast', 'direct', 'biocjava.bioDoer.Table.TableCast', '3g', 'plot', 'tableCast: tableCast <inLong.txt> <outMatrix>'), ('tableColSel', 'direct', 'biocjava.bioDoer.Table.TableColSelector', '3g', 'plot', 'tableColSel: tableColSel <inTable> <outTable> <idList.txt> [--mode Match|'), ('tableColSelect', 'bridge', 'TableColManipCli', '3g', 'plot', 'tableColSelect: tableColSelect <inTable> <outTable> <colName1> [colName2...]'), ('tableCollapse', 'bridge', 'TableCollapseCli', '3g', 'plot', 'tableCollapse: tableCollapse <inTable> <keyColIndex> <outTable> [hasHeader '), ('tableMelt', 'direct', 'biocjava.bioDoer.Table.TableMelt', '3g', 'plot', 'tableMelt: tableMelt <inTable> <outTable>   # 宽表转长表（第88引擎，TableMelt）'), ('tableMerge', 'direct', 'biocjava.bioDoer.Table.TableMerger', '3g', 'plot', 'tableMerge: tableMerge --inFileArr "f1,f2,..." --inColIndexArr "0,1,..." --outTable <out> [--defaultNAvalue NA] [--appendMergedKey true|false] [--rmKeyColumns true|false]   # 按键合并多个表格(TableMerger；⚠️ ArgsParser 式，旧 docstring 位置参数写法已废弃 N3；位置参数兼容见 _tableMerge_impl)'), ('tableSplit', 'direct', 'biocjava.bioDoer.Table.TableSplitByCol', '3g', 'plot', 'tableSplit: tableSplit <inTab> <outDir> [--colIndex N] [--suffix .txt]'), ('tableTranspose', 'direct', 'biocjava.bioDoer.Table.TableTransposer', '3g', 'plot', 'tableTranspose: tableTranspose <inTable> <outTable>   # 表格转置（第95引擎，TableTran'), ('tableUniq', 'direct', 'biocjava.bioDoer.Table.TableUniq', '3g', 'plot', 'tableUniq: tableUniq <inTab> <outFile> [--colIndex N] [--showFreq true|'), ('tauIndex', 'bridge', 'TauCalcCli', '3g', 'plot', 'tauIndex: tauIndex <inExpTab> <outTAU>'), ('trimmsa', 'bridge', 'TrimMSACli', '3g', 'plot', 'trimmsa: trimmsa <in.aln.fa> <out.aln.fa> [ratio]'), ('twoSeqBlast', 'direct', 'biocjava.bioDoer.BLAST.CompareTwoSeqSet', '3g', 'plot', 'twoSeqBlast: twoSeqBlast <query.fa> <subject.fa> <out.txt> [--prog blastp'), ('upset', 'bridge', 'UpSetCli', '3g', 'plot', 'upset: upset <set1.txt> <set2.txt> [<set3.txt>...] <out.svg> [--min-overlap N] [--rank1 Size|Count|Name] [--rank2 ...] [--rank3 ...] [--size-mode/--count-mode/--name-mode Increasing|Decreasing]   # UpSet 集合图（GUI 逆向接口 UpSetPlot.plot，绕 show 弹窗）'), ('venn2', 'direct', 'biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn2', '2g', 'plot', 'venn2: venn2 --List1 <setA.txt> --List2 <setB.txt> --label1 A --label2 B --graph <out> --prefix <out> [--bgNum N]'), ('venn3', 'direct', 'biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn3', '2g', 'plot', 'venn3: venn3 --List1 <A> --List2 <B> --List3 <C> --label1..3 <labels> --graph <out> --prefix <out>'), ('venn4', 'direct', 'biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn4Ellipse', '2g', 'plot', 'venn4: venn4 --List1 <A> --List2 <B> --List3 <C> --List4 <D> --label1..4 <labels> --graph <out> --prefix <out>'), ('venn5', 'bridge', 'Venn5Cli', '3g', 'plot', 'venn5: venn5 <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> [labels]'), ('venn6', 'bridge', 'Venn6Cli', '3g', 'plot', 'venn6: venn6 <out> <setA..F.txt> [labels]'), ('violin', 'bridge', 'ViolinCli', '3g', 'plot', 'violin: violin <in.tsv> <out> [width] [height]'), ('virusRecomb', 'direct', 'biocjava.bioDoer.VirusDetect.RecombinationAnalysis', '3g', 'plot', 'virusRecomb: virusRecomb <inDB.fa> <inContig.fa> <outDir>   # 病毒重组分析（第77引'), ('visualizeblock', 'bridge', 'VisualizeCli', '3g', 'plot', 'visualizeblock: visualizeblock <inBlockOut> <out.pdf> [--labels "Genome1,Gen'), ('kaks', 'direct', 'biocjava.bioIO.BioSoftPipeServer.PairWiseKaKsCalculator', '2g', 'java', 'kaks --inCDS <cds.fa> --inGenePair <pairs.txt> --outKaks <out.xls> [--inCPU N] [--inPep pep.fa]   # 成对 Ka/Ks 计算（GUI 逆向 PairWiseKaKsCalculator；自带 ArgsParser：--key value；inGenePair 为 ID1\\tID2 每行，缺文件时自动全两两配对并翻译 CDS）'), ('sixframe', 'bridge', 'SixFrameTranlaterCli', '2g', 'java', 'sixframe <in.fa> <out.fa>   # 六框翻译（GUI 逆向 #16 SixFrameTranlater：setInFile/setOutFile/process；输出每条序列 6 框 12 条；注意引擎类名拼写 SixFrameTranlater 少一个 s）'), ('longestorf', 'direct', 'biocjava.bioIO.ORF.GetLongestORF', '2g', 'java', 'longestorf --inFa <seq.fa> --outORFs <out.fa>   # 批量最长完整 ORF 预测（GUI 逆向 #17 GetLongestORF：setFastaFile/setOutFile/startPredict；自带 ArgsParser）'), ('protparam', 'direct', 'biocjava.bioWeb.ProtParamWrapper', '2g', 'java', 'protparam --inFa <pep.fa> --outTab <out.txt>   # 蛋白理化性质批量计算（GUI 逆向 #18 ProtParamWrapper.batchCalc；⚠️ 联网 POST Expasy。输出：分子量/pI/不稳定指数/脂肪族指数/GRAVY）'), ('seqpattern', 'direct', 'biocjava.bioIO.FastX.QuickLocateSeqPattern', '2g', 'java', 'seqpattern --inFasta <seq.fa> --pattern <ATG|regex> --outTab <out.gff3> [--overlap] [--maxSeqLen <len>]   # 序列模式定位（GUI 逆向 #20 QuickLocateSeqPattern：正则找模式→GFF3；--key value 空格分隔）'), ('bed2gff3', 'bridge', 'RegionBedToGFF3Cli', '2g', 'java', 'bed2gff3 <in.bed> <out.gff3> [genome.fa]   # exon BED→GFF3（GUI 逆向 #21 RegionBedToGFF3；⚠️ BED 第4列须为 ID:链向:编码 如 G01:+:C；同 ID 多行合并出 mRNA+exon）'), ('careclassify', 'bridge', 'PlantCAREResultClassifyCli', '2g', 'java', 'careclassify <plantcare.tab> <out.xls>   # PlantCARE 顺式元件分类（GUI 逆向 #22；第8列 motif 名查 jar 内置 97 类表，行尾追加大类/亚类；查不到 NA）'), ('subtree', 'bridge', 'GetSubNewickTreeCli', '2g', 'java', 'subtree <tree.nwk> <idList.txt> <out.nwk> [--contain]   # Newick 子树提取（GUI 逆向 #23 GetSubNewickTreeGUIPanel→PhyloTreeMan.getSubTree；--contain 模糊匹配；引擎重算诱导子树内部枝长）'), ('protsim', 'bridge', 'CalculateSimilarityCli', '2g', 'java', 'protsim <pep.fa> <out.matrix>   # 蛋白两两相似度矩阵（GUI 逆向 #24 ProteinPairwiseSimilarityMatrixGUIPanel→CalculateSimilarity；百分比矩阵 TSV）'), ('iqtree', 'bridge', 'QuickRunIQtreeCli', '2g', 'java', 'iqtree <aln.fa> <outPrefix> [--model MFP] [--ufboot 1000] [--boot N] [--freerate] [--asc] [--threads N] [--redo]   # IQ-TREE ML 建树（GUI 逆向 #28 QuickRunIQtree；⚠️ UFBoot 须 ≥1000 否则引擎静默失败；产物 outPrefix.treefile；依赖系统 iqtree）'), ('trimal', 'bridge', 'QuickTrimALCli', '2g', 'java', 'trimal <in.aln> <out.aln> [--mode gappyout|strict|strictplus|automated1] [--format fasta|clustal|phylip|nexus|mega|nbrf] [--keepheader]   # trimAl 比对修剪（GUI 逆向 #29 QuickTrimAL；默认 automated1；依赖系统 trimal；muscle→trimal→iqtree 管线）'), ('gblocks', 'bridge', 'JgblocksCli', '2g', 'java', 'gblocks <in.aln.fa> <out.aln.fa> [--is 0.5] [--fs 0.85] [--cp 8] [--bl1 15] [--bl2 10] [--nongap 0.5] [--gaptreat none|half|all]   # Gblocks 保守区修剪（GUI 逆向 #30 Jgblocks 纯 Java 实现；main 仅 in/out 全参数须 setter；⚠️ 高歧异比对可能 validSites=0 合法）'), ('goAnno', 'direct', 'biocjava.bioDoer.GeneOntology.Annotation.GoAnnoPipe', '3g', 'java', 'goAnno --IdmappingDb <idmapping.DB.gz> --BlastxAnnoFile <blastx.xml> [--inPutFileType BlastxXml|Query2GiTable] [--maxEvalue 1e-5] [--minQueryCov 0.33] [--outDir dir] [--isDoDbFormat]   # GO 注释管道（GUI 逆向 #32 GoAnnotationGUIPanel→GoAnnoPipe；自带 ArgsParser；⚠️ idmappingDb 须 gzip 格式「ID; ID\\tGO:num; GO:num」；产物 outDir/<输入名>.xls）'), ('fasplit', 'direct', 'biocjava.bioIO.FastX.FastaIndex.QuickSpiltFasta', '2g', 'java', 'fasplit --inFa <in.fa> --outPre <prefix> --NumPerFile <N> [--byCount true]   # FASTA 按记录数拆分（GUI 逆向 #33 QuickSpiltFasta；⚠️ 与 filesplit 不同：按记录不切行，产物 prefix.N.split.fa）'), ('famerge', 'bridge', 'FastaMergerCli', '2g', 'java', 'famerge <out.fa> <in1.fa> <in2.fa> [...]   # 多 FASTA 合并（GUI 逆向 #33 FastaMergerAndSpliter.Merge）'), ('clearchar', 'bridge', 'FileCleanerCli', '2g', 'java', 'clearchar <in.txt> <out.txt>   # 文件非法字符清理（GUI 逆向 #34 FileCleaner.simplifyFile；非可打印 ASCII/非 tab→_，空白行跳过，逐行报告）'), ('gb2fa', 'bridge', 'GenBank2FastaCli', '2g', 'java', 'gb2fa <in.gb> <out.fa>   # GenBank→FASTA 转换（GUI 逆向 #36 genBank2Fasta；头含 locus/accession/organism/definition）'), ('findhomolog', 'direct', 'biocjava.bioIO.BioSoftPipeServer.FindBestHomology', '3g', 'java', 'findhomolog --inQueryProteinSet <query.pep> --inSubjectProteinSet <subject.pep> --targetIDs <ID[,ID2]> --outDir <dir> [--threads N] [--extendClade] [--sensitive N] [--similarity 0.x] [--weightCov 0.x] [--plot] [--directGraph]   # 最优同源查找（GUI 逆向 #37 FindBestHomology，同引擎覆盖 GenomeAnnotationSlim+FindBestHomology 两面板；自带 ArgsParser；BLAST+可选建树）'), ('taxparse', 'bridge', 'TaxonomyBatchCli', '2g', 'java', 'taxparse <idList.txt> <out.xls>   # 物种名批量分类解析（GUI 逆向 #38 TaxonomyParserGUIPanel→NCBITaxonomy；⚠️ 联网 NCBI eutils；输出 9 级分类+透传列；单次版=tbtools tool NCBITaxonomy）'), ('srr2ena', 'bridge', 'GetENALinksCli', '2g', 'java', 'srr2ena <srrList.txt> <out.xls>   # SRR→ENA 下载链接解析（GUI 逆向 #39 GetENALinksOfSRR；⚠️ 联网 ENA filereport API+引擎自带 0~3s 限速；17 字段含 fastq_ftp/aspera）'), ('sraxml2tab', 'direct', 'biocjava.bioIO.SRAtools.ParseSRAXml2Table', '2g', 'java', 'sraxml2tab --sraFullXML <sra.xml> --outTab <out.xls>   # SRA XML→信息表（GUI 逆向 #40 ParseSRAXml2Table；自带 ArgsParser；离线 JDOM 解析；XML 从 efetch db=sra 获取）'), ('sranum2info', 'direct', 'biocjava.bioWeb.EntrezUtils.BatchGetSRARecordInfo', '2g', 'java', 'sranum2info --sraIdList <srrList.txt> --outTabInfo <out.xls>   # SRR 批量信息表（GUI 逆向 #41 BatchGetSRARecordInfo；⚠️ 联网 NCBI Entrez+限速；自带 ArgsParser；SRA 组 3/3 全清）'), ('blat', 'bridge', 'BlatExecutorCli', '2g', 'java', 'blat <db.fa> <query.fa> <out> [--format blast9|psl|pslx|axt|maf|sim4|wublast|blast|blast8] [--minScore N] [--minIdentity 0.x] [--noHead] [--mode auto|dnadna|dnarna] [--tileSize N] [--stepSize N] [--maxGap N] [--maxIntron N] [--extra "opts"]   # BLAT 序列比对（GUI 逆向 #42 BlatExecutor；org.ucsc.blat 纯 Java 实现内嵌 jar 无需外部二进制）'), ('seqrecommend', 'bridge', 'AssemblyRecommandCli', '2g', 'java', 'seqrecommend <genomeSize1n_bp> [--polyploid] [--het 0.01] [--level Minimum|Draft|Haplotyped_Resolved|Haplotyped_T2T]   # 基因组组装测序量推荐（GUI 逆向 #43 AssemblyGenomeDataSizeRecommand；纯计算离线；Hifi/HiC 深度+数据量）'), ('seqfetch', 'direct', 'biocjava.bioWeb.EntrezUtils.NcbiSmartSeqFetchEntrezUtils', '2g', 'java', 'seqfetch --inFile <idList.txt> --outSeqFile <out.fa> --outReport <report.txt> [--targetDb nuccore|protein] [--preferDb db] [--format fasta] [--greedyMode] [--apiKey KEY] [--auditFile f]   # NCBI 智能序列下载（GUI 逆向 #44 NcbiSmartSeqFetchEntrezUtils；⚠️ 联网 Entrez+限速；ID 自动检测/转换/审计；支持 apiKey 提速）'), ('pubmed', 'bridge', 'PubmedSearchCli', '2g', 'java', 'pubmed <query> <out.xls>   # PubMed 文献检索汇总（GUI 逆向 #45 PubmedSearch.process；⚠️ 联网 eutils；输出期刊/标题/年份/IF/DOI 表）'), ('vcfAddID', 'direct', 'biocjava.bioDoer.GWAS.VCFAddID', '2g', 'java', 'vcfAddID: vcfAddID --inFile <vcf> --outFile <out.vcf>   # VCF 加 ID 列（GWAS；ArgsParser --inFile/--outFile，支持 .gz）'), ('mimicVqsr', 'direct', 'biocjava.bioDoer.GWAS.MimicVqsrCutoffFind', '2g', 'java', 'mimicVqsr: mimicVqsr --inFile <vcf> --outFile <out.txt>   # VCF 质量指标（QD/MQ/FS/SOR；GWAS）')]
_IMPL_REGISTRY = {}
def parse_kv_args(args, spec, raw_flags=()):
    """
    通用参数解析(替代各 impl 重复的 while 循环)。

spec: {flag: (attr, converter)} —— 取值 flag,converter 可选(如 int);
raw_flags: 出现即收集到 raw 的 flag(如 --super5)。
返回 (kwargs, positional, raw);kwargs 只含出现的 flag,缺省值由调用方自行默认。
    """

    ...
def _warn_gtf_input(args, cmd):
    """N28/N22/N36: Gxf 族命令输入格式预检——GTF 引擎 NPE、BED 误报 GFF3/GTF 识别。"""

    ...
_NOARG_HANG = {'gel'}
def _make_impl(cmd, kind, cls, xmx, runner, doc):
    """工厂：按注册表条目生成 _xxx_impl 闭包（保持 (args, verbose, quiet) 签名）"""

    ...
_HANDWRITTEN = {} if False else None
for _cmd, _kind, _cls, _xmx, _runner, _doc in ENGINE_REGISTRY:
    if hasattr(sys.modules[__name__], f'_{_cmd}_impl'):
        raise SystemError(f"注册表与手写实现冲突: {_cmd}(手写 {f'_{_cmd}_impl'} 存在)——请从 ENGINE_REGISTRY 删除该条目")
    _fn = _make_impl(_cmd, _kind, _cls, _xmx, _runner, _doc)
    _IMPL_REGISTRY[_cmd] = _fn
    globals()[f'_{_cmd}_impl'] = _fn
def _hmmsearch_impl(args, verbose=False, quiet=False):
    """hmmsearch: hmmsearch <pfamA.hmm> <target.pep> <idList.txt> <out.txt>   # HMM Search 域扫描（= simpleHmmscan 引擎，调系统 hmmsearch，G1 补齐别名）"""

    ...
def _gxfAttr_impl(args, verbose=False, quiet=False):
    """gxfAttr: gxfAttr <in.gff3|gtf> <out.tsv> [--feature mRNA] [--attrs ID,Name,Parent]   # GXF 属性/ID 对照表提取（G7 补齐，Python 原生，jar 无此引擎）"""

    ...
def _kallisto_impl(args, verbose=False, quiet=False):
    """kallisto: kallisto <transcriptome.fa> <reads.fq[,reads2.fq]> <outAbundance> [--kmer N] [--threads N] [--bootstrap N] [--bias] [--single] [--frag-len N] [--frag-sd N]   # RNA-seq 定量（插件 P00740 CLI 化，直调 kallisto 二进制——插件 wrapper 的 Linux 分支有拼接 bug 已绕开）"""

    ...
def _fimo_impl(args, verbose=False, quiet=False):
    """fimo: fimo --o <outDir> <motifs.meme> <promoter.fa>   # MEME FIMO motif 扫描（插件 P00552 等价，直调系统 fimo；meme-suite）"""

    ...
def _xml2blasttab_impl(args, verbose=False, quiet=False):
    """xml2blasttab: xml2blasttab <in.xml> <out.txt>   # BLAST XML→标准 12 列表（GUI 逆向 #25 BlastXmlToBlastFoolTable.xml2ShowerTable；QueryID/SubjectID/Identity/E-value/BitScore...）"""

    ...
def _xml2pairwise_impl(args, verbose=False, quiet=False):
    """xml2pairwise: xml2pairwise <in.xml> <out.txt>   # BLAST XML→网页 pairwise 对齐文本（GUI 逆向 #25 BlastXMLToPairwise.parse；⚠️ 需 Hsp_query-frame/Hsp_hit-frame 字段）"""

    ...
def _fa2tab_impl(args, verbose=False, quiet=False):
    """fa2tab: fa2tab <in.fa> <out.tab>   # FASTA→表格 ID\t序列（GUI 逆向 #26 FastaTable.fa2tab；与 tab2fa 往返一致）"""

    ...
def _tab2fa_impl(args, verbose=False, quiet=False):
    """tab2fa: tab2fa <in.tab> <out.fa>   # 表格→FASTA（GUI 逆向 #26 FastaTable.tab2fa）"""

    ...
def _muscle_impl(args, verbose=False, quiet=False):
    """muscle: muscle <in.fa> <out.aln> [--super5] [--threads N]   # MUSCLE 多序列比对（GUI 逆向 #27 MuscleGUIPanel→QuickRunMUSCLE；⚠️ 引擎硬编码 muscle3 -in/-out 语法在 v5 系统崩 → Python 直调自动适配；依赖系统 muscle）"""

    ...
def _bestid_impl(args, verbose=False, quiet=False):
    """bestid: bestid --inQuery <query.pep> --Subject <subject.pep> --OutPrefix <outPrefix> [--useDiamond] [--threads N]   # 双向 BLAST 最优 ID 转换（GUI 逆向 #31 BestIDConverter；RBH 互撞 Excellent/Poor；⚠️ 引擎强制 --threads，CLI 公共 -t 会吃掉它——缺省自动注入 4，精确指定用 --config parameter.txt；依赖 blastp/diamond）"""

    ...
def _getseqdb_impl(args, verbose=False, quiet=False):
    """getseqdb: getseqdb <dbPrefix> <idList.txt> <out.fa> [--entry ID]   # 从 BLAST 库批量提取序列（GUI 逆向 #35 GetSeqFromBlastDBGUIPanel $5：blastdbcmd -db X -entry_batch ids -out Y；⚠️ 库须 makeblastdb -parse_seqids 建，否则 Skipped；依赖系统 blastdbcmd）"""

    ...
def _genomefilter_impl(args, verbose=False, quiet=False):
    """genomefilter: genomefilter <in.fa> <out.fa> --min-len <N> [--gxf <in.gff3>]   # 按序列长度过滤（GUI 逆向 #19 GenomeLengthFilterGUIPanel：QuickStatFasta 统计 → 按 minLen 过滤 ID → ExtractFasta 提取；可选 GXF 同过滤）"""

    ...
def _notung_impl(args, verbose=False, quiet=False):
    """
    notung: notung <gene.nwk> -s <species.nwk> --out <out.nwk> [--reconcile 原生参数...]   # 基因树-物种树 reconcile（duplication/loss 推断，插件 P00651 CLI 化）
产物搬运: Notung 输出 <gene>.reconciled(基因树派生名) 到 --outputdir → 复制到 out。
out 用显式 --out 传参(不解析位置参数——Notung 带值 flag 众多(--speciestag/
--treeoutput/--mapping...), 黑名单解析脆弱: 曾把 --speciestag 的值 prefix 当
位置参数致 Notung 报 '--treeoutput is not a valid argument for --speciestag')。
    """

    ...
def _newickRename_impl(args, verbose=False, quiet=False):
    """newickRename: newickRename --inNwk <tree.nwk> --renameMap <map.tsv> --outNwk <out.nwk>   # 树叶批量重命名（插件 P00690 CLI 化，map 为 OldName\tNewName）"""

    ...
def _hmmerSearch_impl(args, verbose=False, quiet=False):
    """hmmerSearch: hmmerSearch <target.fa> <hmmDb> <out.tsv>   # Advanced HMMer 全库扫描+domtblout 解析（插件 P00680 CLI 化，无需 idList）"""

    ...
def _memeViz_impl(args, verbose=False, quiet=False):
    """memeViz: memeViz <meme.xml> <out.svg> [width] [height]   # MEME motif 批量可视化（插件 P00700 CLI 化，每 motif 一面板）"""

    ...
def _gsea_impl(args, verbose=False, quiet=False):
    """gsea: gsea <go.obo> <query2go.tsv> <rank.rnk> <outDir>   # GO 预排序 GSEA（插件 P00342 CLI 化，GSEAPreranked 全套报告；⚠️ set_min=15 小基因集会被过滤）"""

    ...
def _tfbsShift_impl(args, verbose=False, quiet=False):
    """tfbsShift: tfbsShift <query.pep> <outPrefix> [threads]   # 植物 TF 结合 motif 偏移分析（插件 P00551 CLI 化，参考数据内置 ath.pep+binding.motifs）"""

    ...
def _mcscanxd_impl(args, verbose=False, quiet=False):
    """mcscanxd: mcscanxd <wkDir> <genome1.fa> <genome2.fa> <gxf1> <gxf2> [threads] [blastHits] [evalue]   # OneStep MCScanX-SuperFast（插件 P00370 CLI 化，diamond 加速，二进制随包）"""

    ...
def _quickAnno_impl(args, verbose=False, quiet=False):
    """quickAnno: quickAnno <query.pep> <swissprotDb.fa> <out.txt> [threads] [maxHits]   # diamond 蛋白快速注释（插件 P00480 CLI 化；⚠️ db 需带描述行，否则 Top 词频为空报错）"""

    ...
def _smart_impl(args, verbose=False, quiet=False):
    """smart: smart <in.fa> <out.txt>   # SMART 域注释（插件 P00060 CLI 化；⚠️ 联网 POST EMBL ismart.embl.de，约 10-60s，输出域位置+类型）"""

    ...
def _findBestHomologyBatch_impl(args, verbose=False, quiet=False):
    """
    findBestHomologyBatch: findBestHomologyBatch <query.pep> <subject.pep> <outDir> [--targetIds ID[,ID2...]] [--threads N] [--plot false] [--sensitive 5,10]
# 最优同源批量查找（FindBestHomologyBatch；N19 修复）
# ⚠️ 引擎真实参数: --inQueryProteinSet/--inSubjectProteinSet/--targetIdList(GeneName   ID1[,ID2])/--outDir；
#    旧写法 --queryFasta/--subjectFasta/--outTable 是错误参数名，引擎拒参仍返 ec=0（静默成功+输出不创建）。
# ⚠️ 引擎不自动创建 --outDir；targetIdList 必需，缺省时自动取 query 全部 ID（targetName=All）。
#    产物: <outDir>/<targetName>.s<subjectId>.ids（最佳同源 ID 对，逗号分隔）。
    """

    ...
def _gffCdsPhaseCorrector_impl(args, verbose=False, quiet=False):
    """
    gffCdsPhaseCorrector: gffCdsPhaseCorrector --inGff <in.gff3> --outGff <out.gff3> [--problemGff <p.gff3>] [--report <r.txt>]
# CDS phase 校正（GffCdsPhaseCorrector；N25 修复：引擎为位置参数式 <in> <correct> <problematic> <report>，
#    原注册表直通导致 --inGff/--outGff 被当字面量文件、警告覆盖输入——现显式转位置参数并避免覆盖已存在输出）。
    """

    ...
def _mirnatarget_impl(args, verbose=False, quiet=False):
    """
    mirnatarget: mirnatarget <mirna.fa> <target.fa> <out.tsv> [--evalue X]
# miRNA 靶标预测完整管线（N23 修复）：ssearch36 -w 100 -W 25 -E X -m 10 -T 1 -i -U <mirna> <target> → TargetScoreCli
#   原表驱动误把本命令直通 TargetScoreCli（其输入是 ssearch36 的 m10，不是 FASTA），
#   导致第 2 参数被当输出清零、第 3 参被忽略、输出永不落盘——现恢复完整管线并校验输出。
# 依赖: ssearch36（fasta36 套件）。产物: miRNA    target  strand  beg     end     score   ...
    """

    ...
def _msy_impl(args, verbose=False, quiet=False):
    """
    msy: msy <simplifiedGff.pos> <links.txt> <chrLayout.txt> <out> [w] [h]
# 多物种微共线性图 / microsynteny / collinearity plot（N26 修复：原表驱动把 msy 注册为裸 GenericCli 透传，用户参数被当
#   engineClass 导致 ClassNotFoundException——现按 tbplot.sh 已验证调用方式显式拼参数）
# 格式: pos=Chr\tGene\tStart\tEnd；links=GeneA\tGeneB\t[r,g,b]；layout=Genome: chr1 chr2
    """

    ...
def _getLongestCompleteORF_impl(args, verbose=False, quiet=False):
    """
    getLongestCompleteORF: getLongestCompleteORF --inFa <seq.fa> --outORFs <out.fa>
# 批量最长完整 ORF 预测（N24 修复：原注册到 JavaFX 无 main 的 biocjava.bioIO.ORF.ORF，
#   改映射到 GetLongestORF（longestorf 同引擎，ArgsParser --inFa/--outORFs 实测可用））
    """

    ...
def _efpHeat_impl(args, verbose=False, quiet=False):
    """
    efpHeat: efpHeat --inTGA <plant.tga> --inSample2CC <sample2cc.txt> --expMat <expMat.tsv> --geneId <ID> --outImg <out>
# eFP 组织表达热图（单矩阵，generateSuperHeatMap）——N27 附带修复：引擎是 --key value 式，
#   旧 docstring 写成位置参数导致拒参；支持位置参数 <tga> <sample2cc> <expmat> <geneId> <out> 自动转换
# ⚠️ 需 fake DatatypeConverter（build/，JDK9+ 无 javax.xml.bind，ensure_bridge 自动重建）
    """

    ...
def _tableMerge_impl(args, verbose=False, quiet=False):
    """
    tableMerge: tableMerge --inFileArr "f1,f2,..." --inColIndexArr "0,1,..." --outTable <out> [--defaultNAvalue NA] [--appendMergedKey true|false] [--rmKeyColumns true|false]
# 按键合并多个表格（N3 修复：引擎为 ArgsParser 式 --inFileArr/--inColIndexArr/--outTable，
#   旧 docstring 位置参数写法 <outTable> <inFile1> [...] 与引擎完全对不上；本 impl 兼容位置参数自动转换）
    """

    ...
def _parallelMD5Check_impl(args, verbose=False, quiet=False):
    """
    parallelMD5Check: parallelMD5Check <md5_list.txt> [threads]
# 并行校验 MD5 列表（N6 修复：位置参数式 <md5_list_file> [threads]；
#   每行 `md5sum  文件名`，与 md5sum -c 同格式；原 registry 直通在参数形态错误时 ec=3）
    """

    ...
def _extractFeatureFromGTF_impl(args, verbose=False, quiet=False):
    """
    extractFeatureFromGTF: extractFeatureFromGTF --inGtf <in.gtf> --inGenome <genome.fa> --outFile <out> [--targetFeature CDS|exon|...] [--targetIdTag transcript_id] [--retainAttr true|false]
# GTF 特征提取（N6 修复：引擎 main 硬编码 Windows 默认路径，但 toolsKit.ArgsParser 可覆盖 → 走 ArgsParser 路线；
#   旧注册表直通裸 main 必 FileNotFoundException；位置参数 <in.gtf> <genome.fa> <out> 兼容转换）
# ⚠️ 输入 GTF 坐标须与 genome 匹配（越界会 NPE）；输出 FASTA 头含 +/− 链/Location 注释
    """

    ...
def _gxfSplit_impl(args, verbose=False, quiet=False):
    """
    gxfSplit: gxfSplit <in.gff3|gtf> <outPrefix> [--numOfFile N]
# GXF 按记录数拆分（§8.B N13 家族命令面缺口修复：RPC GxfSplit.process，走 RPC 自动拉起）
    """

    ...
def _gxfIdAppender_impl(args, verbose=False, quiet=False):
    """
    gxfIdAppender: gxfIdAppender <in.gff3|gtf> <out.gff3> <prefix>
# GXF ID/染色体名前缀追加（§8.B N13 家族命令面缺口修复：RPC GxfIdAppender.process）
    """

    ...
