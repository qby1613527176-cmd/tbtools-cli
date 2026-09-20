"""自动生成的 click 命令（从 tbplot.sh 元数据提取，直调 Java）"""
import os
import subprocess
import sys

from tbtools_cli.core import BUILD_DIR, JAR, ROOT, cp, ensure_bridge, run_java, run_plot


def _admixture_impl(args, verbose=False, quiet=False):
    """admixture: admixture <qFiles.lst> <out> [sampleIDFile] [groupFile] [sor"""
    ensure_bridge("AdmixtureCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "AdmixtureCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="admixture")

def _amazingmeta_impl(args, verbose=False, quiet=False):
    """amazingmeta: amazingmeta <meme.xml> <newick.treefile> <out.svg|png|pdf> ["""
    ensure_bridge("AmazingMetaCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "AmazingMetaCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="amazingmeta")

def _annocompare_impl(args, verbose=False, quiet=False):
    """annocompare: annocompare <before.gff3> <after.gff3> <outDir> [runName] [r"""
    ensure_bridge("StructAnnoCompareCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "StructAnnoCompareCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="annocompare")

def _bamMerge_impl(args, verbose=False, quiet=False):
    """bamMerge: bamMerge <gtf> <bamDir> <outDir>   # 按区域覆盖合并 BAM（多样本择优）"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAnnotation.BAMMergeByRegionCoverage"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="bamMerge")

def _bamindex_impl(args, verbose=False, quiet=False):
    """bamindex: bamindex <in.sorted.bam> [out.bai]"""
    ensure_bridge("BamIndexCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "BamIndexCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="bamindex")

def _bamsort_impl(args, verbose=False, quiet=False):
    """bamsort: bamsort <in.bam> <out.bam> [sortOrder] [tmpDir]"""
    ensure_bridge("BamSortCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "BamSortCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="bamsort")

def _bamstate_impl(args, verbose=False, quiet=False):
    """bamstate: bamstate <out.tsv> <gff3> <bam1> [<bam2> ...]"""
    ensure_bridge("BamStateCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "BamStateCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="bamstate")

def _barplot_impl(args, verbose=False, quiet=False):
    """barplot: barplot <enrichment.tsv> <out> <termCol> <pvalCol> [classCol"""
    ensure_bridge("BarplotCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "BarplotCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="barplot")

def _barplotter_impl(args, verbose=False, quiet=False):
    """barplotter: barplotter -g <gff> -s <synteny> -c <ctl> -o <out.png>"""
    ensure_bridge("BarPlotterCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "BarPlotterCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="barplotter")

def _batchReplace_impl(args, verbose=False, quiet=False):
    """batchReplace: batchReplace <inFile> <outFile> <patternMap.tsv> [--partial]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.BatchStringReplace"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="batchReplace")

def _calcRepeat_impl(args, verbose=False, quiet=False):
    """calcRepeat: calcRepeat <genome.fa> <outRepeat.txt> [--kmerSize N] [--min"""
    ensure_bridge("CalcRepeatCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "CalcRepeatCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="calcRepeat")

def _cddmotif_impl(args, verbose=False, quiet=False):
    """cddmotif: cddmotif <cdd.hitdata.txt> <in.fasta> <out.svg|png|pdf> [new"""
    ensure_bridge("CddMotifCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "CddMotifCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="cddmotif")

def _circlegene_impl(args, verbose=False, quiet=False):
    """circlegene: circlegene <gff> <geneID.txt> <out> [--rename f --link f --r"""
    ensure_bridge("CircleGeneViewerCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "CircleGeneViewerCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="circlegene")

def _circos_impl(args, verbose=False, quiet=False):
    """circos: circos <chrLen.txt> <link.txt> <genePos.txt> <outFile> [w] ["""
    ensure_bridge("CircosCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "CircosCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="circos")

def _collinearRegion_impl(args, verbose=False, quiet=False):
    """collinearRegion: collinearRegion <in.collinearity> <simGff> <out.txt>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.ComparativeGenomics.MCScanX.CollinearityToRegion"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="collinearRegion")

def _colorscheme_impl(args, verbose=False, quiet=False):
    """colorscheme: colorscheme <inTab> <outTab> <refColIndex>"""
    ensure_bridge("ColorSchemeCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "ColorSchemeCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="colorscheme")

def _conflictpaf_impl(args, verbose=False, quiet=False):
    """conflictpaf: conflictpaf <in.paf> <out.tsv> [binSize]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.CalculateConflictByRefAlignPAF"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="conflictpaf")

def _ctgGroup_impl(args, verbose=False, quiet=False):
    """ctgGroup: ctgGroup <in.miniprot.gff> <polyPoid> <outContigGrpMap>"""
    ensure_bridge("CtgGroupCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "CtgGroupCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="ctgGroup")

def _cubeheatmap_impl(args, verbose=False, quiet=False):
    """cubeheatmap: cubeheatmap <expr.tsv> <group.tsv> <out> [--log10 --minColor"""
    ensure_bridge("CubeHeatmapCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "CubeHeatmapCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="cubeheatmap")

def _degramdom_impl(args, verbose=False, quiet=False):
    """degramdom: degramdom <in.tsv> [out.nwk]"""
    ensure_bridge("DegramdomCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "DegramdomCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="degramdom")

def _distance_impl(args, verbose=False, quiet=False):
    """distance: distance <in.tsv> <col1> <col2> <euclidean|pearson|pearsonDi"""
    ensure_bridge("DistanceCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "DistanceCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="distance")

def _dotplot_impl(args, verbose=False, quiet=False):
    """dotplot: dotplot --inGff <gff> --genePair <pairs> --chrLayout <layout"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.DotPlot.dotdotdot"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="dotplot")

def _dualsyn_impl(args, verbose=False, quiet=False):
    """dualsyn: dualsyn <simplifiedGff> <collinearity> <out> [--chr1 "1,2"] """
    ensure_bridge("DualSynCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "DualSynCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="dualsyn")

def _efpHeat_impl(args, verbose=False, quiet=False):
    """efpHeat: efpHeat <inTGA> <sample2cc.txt> <expMat.tsv> <geneId> <out.s"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.SimpleEfpBrowser.generateSuperHeatMap"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="efpHeat")

def _exprCorr_impl(args, verbose=False, quiet=False):
    """exprCorr: exprCorr <inFPKM> <outCorrMat>"""
    ensure_bridge("ExprCorrCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "ExprCorrCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="exprCorr")

def _fastaExtract_impl(args, verbose=False, quiet=False):
    """fastaExtract: fastaExtract <in.fa> <idList.txt> <out.fa> [--mode Match|Con"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Fasta.ExtractFasta"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="fastaExtract")

def _fastaSubseq_impl(args, verbose=False, quiet=False):
    """fastaSubseq: fastaSubseq <in.fa> <pos.txt> <out.fa>   # 按坐标提子序列（第92引擎，Ext"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Fasta.ExtractFastaSubseq"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="fastaSubseq")

def _filesplit_impl(args, verbose=False, quiet=False):
    """filesplit: filesplit <inFile> <numParts>"""
    ensure_bridge("FileSplitCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "FileSplitCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="filesplit")

def _filterCScore_impl(args, verbose=False, quiet=False):
    """filterCScore: filterCScore <in.blast.tab6> <out.tab6> [--cscore 0.5]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.BLAST.FilterBlastResultByCScore"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="filterCScore")

def _findblockdual_impl(args, verbose=False, quiet=False):
    """findblockdual: findblockdual <queryGenome.fa> <query.gff> <subjectGenome.fa"""
    ensure_bridge("FindBlockDualCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "FindBlockDualCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="findblockdual")

def _findblockmultiple_impl(args, verbose=False, quiet=False):
    """findblockmultiple: findblockmultiple <queryGenome.fa> <query.gff> <queryId> <ou"""
    ensure_bridge("FindBlockMultipleCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "FindBlockMultipleCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="findblockmultiple")

def _findpath_impl(args, verbose=False, quiet=False):
    """findpath: findpath --inGffArr <gff1,gff2,...> --inGenePairs <pairs> --"""
    ensure_bridge("FindPathCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "FindPathCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="findpath")

def _fqTrim_impl(args, verbose=False, quiet=False):
    """fqTrim: fqTrim <in.fq> <out.fq> [--b5 N] [--b3 N] [--threads N]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Fastq.FastqParallelTrimmer"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="fqTrim")

def _fqfaConv_impl(args, verbose=False, quiet=False):
    """fqfaConv: fqfaConv <input> <output> <fq2fa|fa2fq>   # FASTQ/FASTA 互转（第"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.LinuxPipe.FastqAndFasta"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="fqfaConv")

def _gel_impl(args, verbose=False, quiet=False):
    """gel: gel <FragmentRangeArr> <LaneLabels> <MarkerRange> <out>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.GelImage.Marker"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gel")

def _genedensity_impl(args, verbose=False, quiet=False):
    """genedensity: genedensity <in.gff3> <out.tsv> [binSize]"""
    ensure_bridge("GeneDensityCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GeneDensityCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="genedensity")

def _genelocation_impl(args, verbose=False, quiet=False):
    """genelocation: genelocation --ChrLen <chrlen> --FeaturePos <pos> --OutGraph"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.GeneLocation.GeneLocation"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="genelocation")

def _genelocgff_impl(args, verbose=False, quiet=False):
    """genelocgff: genelocgff <gff3> <idList> <out> [--chrLen len.tsv] [--renam"""
    ensure_bridge("GeneLocGffCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GeneLocGffCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="genelocgff")

def _generic_impl(args, verbose=False, quiet=False):
    """generic: generic <engineClass> <method[+method2]> <out> [--set field """
    ensure_bridge("GenericCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GenericCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="generic")

def _gfa_impl(args, verbose=False, quiet=False):
    """gfa: gfa <in.gfa> <out> [width] [height]"""
    ensure_bridge("VizGFACli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "VizGFACli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gfa")

def _gfa2fa_impl(args, verbose=False, quiet=False):
    """gfa2fa: gfa2fa <in.gfa> <out.fa>   # GFA 组装图 → FASTA（第91引擎，GFAtoFast"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Fasta.Tools.GFAtoFasta"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gfa2fa")

def _goParse_impl(args, verbose=False, quiet=False):
    """goParse: goParse <gene2Go.txt> <oboFile> [--level N]   # GO 词典解析（第103"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GeneOntology.littleTools.GOtermParser"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="goParse")

def _groupCol_impl(args, verbose=False, quiet=False):
    """groupCol: groupCol <inTable.tsv> <inGrpInfo.tsv> <outTable> [Sum|Mean|"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableColCollaspe"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="groupCol")

def _groupedbar_impl(args, verbose=False, quiet=False):
    """groupedbar: groupedbar <data.tsv> <out> [plotType] [errorBarType] [hasHe"""
    ensure_bridge("GroupedBarCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GroupedBarCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="groupedbar")

def _gsadiag_impl(args, verbose=False, quiet=False):
    """gsadiag: gsadiag <in.fixed.gff3> <out.stat.xls> [genome.fasta] [relax"""
    ensure_bridge("GsaDiagCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GsaDiagCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gsadiag")

def _gxfAppend_impl(args, verbose=False, quiet=False):
    """gxfAppend: gxfAppend <in.gff3> <out.gff3> <prefix>   # GFF seqid+ID 加前缀"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GxfIDAppender"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfAppend")

def _gxfFix_impl(args, verbose=False, quiet=False):
    """gxfFix: gxfFix <in.gff3> <out.gff3>   # GFF 修复（重复ID前缀/CDS phase/dang"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFfixer.GXFFix"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfFix")

def _gxfGenepos_impl(args, verbose=False, quiet=False):
    """gxfGenepos: gxfGenepos <in.gff3> <outGenepos> <outChrLen> [feature]  # G"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFToGenePosFile"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfGenepos")

def _gxfMatch_impl(args, verbose=False, quiet=False):
    """gxfMatch: gxfMatch <in.gff3> <inGenome.fa>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GxfGenomeMatch"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfMatch")

def _gxfOverlap_impl(args, verbose=False, quiet=False):
    """gxfOverlap: gxfOverlap <in.gff3> <region.txt> <out.gff3> [--ignoreStrand"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFOverlaper"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfOverlap")

def _gxfRecall_impl(args, verbose=False, quiet=False):
    """gxfRecall: gxfRecall <in.gff3> <out.gff3>   # 从 gene 行恢复 mRNA 特征（第82引擎，"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.RecallmRNAFeature"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfRecall")

def _gxfRegion_impl(args, verbose=False, quiet=False):
    """gxfRegion: gxfRegion <in.gff3> <region.txt> <out.gff3> [--ignoreStrand]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFRegionSummary"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfRegion")

def _gxfRename_impl(args, verbose=False, quiet=False):
    """gxfRename: gxfRename <in.gff3> <out.gff3> <renameMap.tsv>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFRenamer"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfRename")

def _gxfRepGXF_impl(args, verbose=False, quiet=False):
    """gxfRepGXF: gxfRepGXF <in.gff3> <out.gff3> [--featureID CDS] [--attachID"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFToRepresentativeGXF"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfRepGXF")

def _gxfRepIDs_impl(args, verbose=False, quiet=False):
    """gxfRepIDs: gxfRepIDs <in.gff3> <out.txt>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFToRepresentativeIDs"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfRepIDs")

def _gxfStat_impl(args, verbose=False, quiet=False):
    """gxfStat: gxfStat <in.gff3> <outStat.xls>   # GFF 统计（基因/mRNA/外显子/内含子/C"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFfixer.GXFstat"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfStat")

def _gxffilter_impl(args, verbose=False, quiet=False):
    """gxffilter: gxffilter <in.gff3|gtf> <idList.txt> <out.gff3|gtf>"""
    ensure_bridge("GxfFilterCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GxfFilterCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxffilter")

def _gxfsort_impl(args, verbose=False, quiet=False):
    """gxfsort: gxfsort <in.gff3|gtf> <out.sorted>"""
    ensure_bridge("GxfSortCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GxfSortCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfsort")

def _hicEnzyme_impl(args, verbose=False, quiet=False):
    """hicEnzyme: hicEnzyme <inHiC.fastq>   # HiC 限制酶预测（第76引擎）"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.HiCRestrictionEnzymePrediction"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="hicEnzyme")

def _hmmExtract_impl(args, verbose=False, quiet=False):
    """hmmExtract: hmmExtract <in.hmm> <idList.txt> <out.hmm>   # 从 HMM 文件按 NAM"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.LinuxPipe.hmmInfoExtracter"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="hmmExtract")

def _homoPhase_impl(args, verbose=False, quiet=False):
    """homoPhase: homoPhase <inContigGrpMap> <outPhasedMap>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.HomoConflictBasedPartition"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="homoPhase")

def _layoutheatmap_impl(args, verbose=False, quiet=False):
    """layoutheatmap: layoutheatmap <layout.tsv> <expr.tsv> <out> [--options]"""
    ensure_bridge("LayoutHeatmapCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "LayoutHeatmapCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="layoutheatmap")

def _levelGo_impl(args, verbose=False, quiet=False):
    """levelGo: levelGo <gene2Go.txt> <outTable> <oboFile> [--level N]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GeneOntology.Grapher.LevelDoer"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="levelGo")

def _marker_impl(args, verbose=False, quiet=False):
    """marker: marker <MarkerDist|MarkerFilter|SampleDist|BigMarkerRandomDe"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.markerDesign.BigMarkerRandomDesign"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="marker")

def _markertools_impl(args, verbose=False, quiet=False):
    """markertools: markertools <filter|dist|sampledist> <in.marker.tab> [maxPoi"""
    ensure_bridge("MarkerToolsCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MarkerToolsCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="markertools")

def _mast2tab_impl(args, verbose=False, quiet=False):
    """mast2tab: mast2tab <mast|meme.xml> <out.tab>"""
    ensure_bridge("Mast2TabCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "Mast2TabCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mast2tab")

def _mastExtract_impl(args, verbose=False, quiet=False):
    """mastExtract: mastExtract <in.fa> <mast.xml> <out.txt>   # 从 MAST XML 提取命中"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.MEME.ExtractSeq.ExtractSeqFromMastXML"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mastExtract")

def _mastrun_impl(args, verbose=False, quiet=False):
    """mastrun: mastrun <meme.xml> <seq.fasta> <workingDir> [--motifs M] [--"""
    ensure_bridge("MastRunCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MastRunCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mastrun")

def _mcscanx_impl(args, verbose=False, quiet=False):
    """mcscanx: mcscanx <gff> <blast> <outPrefix> [--html]   # 共线性检测"""
    ensure_bridge("MCScanXCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MCScanXCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mcscanx")

def _memerun_impl(args, verbose=False, quiet=False):
    """memerun: memerun <in.fasta> <workingDir> [--motif N] [--minW N] [--ma"""
    ensure_bridge("MemeRunCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MemeRunCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="memerun")

def _mggxf_impl(args, verbose=False, quiet=False):
    """mggxf: mggxf <inGenePair|blastTab6> <in.simplified.gff> <out.Linked"""
    ensure_bridge("MgGxfCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MgGxfCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mggxf")

def _microgenome_impl(args, verbose=False, quiet=False):
    """microgenome: microgenome <inGBK> <anno.tsv> <out> [micro|macro]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.MicroGenomeViz.MicroGenomeAnnotationCircosPlot"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="microgenome")

def _microsyn_impl(args, verbose=False, quiet=False):
    """microsyn: microsyn <gxf1> <gxf2> <collinearity> <out> [--chr1 C --star"""
    ensure_bridge("MicroSynCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MicroSynCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="microsyn")

def _mirnaIdentify_impl(args, verbose=False, quiet=False):
    """mirnaIdentify: mirnaIdentify <genome.fa> <targetSo.tsv> <outPredict.txt> [o"""
    ensure_bridge("MirIdentifyCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MirIdentifyCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mirnaIdentify")

def _mirnaTarget2_impl(args, verbose=False, quiet=False):
    """mirnaTarget2: mirnaTarget2 <mirna.fa> <target.fa> <out.txt> [--revCom true"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.miRNA.Target2TablePipe"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mirnaTarget2")

def _mirnatarget_impl(args, verbose=False, quiet=False):
    """mirnatarget: mirnatarget <mirna.fa> <target.fa> <out.tsv> [--evalue X] [-"""
    ensure_bridge("TargetScoreCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "TargetScoreCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mirnatarget")

def _mountain_impl(args, verbose=False, quiet=False):
    """mountain: mountain <fold.txt> <out.tsv>"""
    ensure_bridge("MountainPlotCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MountainPlotCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mountain")

def _msy_impl(args, verbose=False, quiet=False):
    """msy: msy <simplifiedGff.pos> <links.txt> <chrLayout.txt> <out> [w"""
    ensure_bridge("GenericCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GenericCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="msy")

def _multiEfp_impl(args, verbose=False, quiet=False):
    """multiEfp: multiEfp <inTGA> <sample2cc> <expMat1[,expMat2,...]> <geneId"""
    ensure_bridge("MultiSuperHeatCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MultiSuperHeatCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="multiEfp")

def _multisyn_impl(args, verbose=False, quiet=False):
    """multisyn: multisyn <gxf.lst> <collinear.lst> <out> [--genes idlist.txt"""
    ensure_bridge("SeveralSpeciesCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SeveralSpeciesCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="multisyn")

def _nwAlign_impl(args, verbose=False, quiet=False):
    """nwAlign: nwAlign <seq1.fa> <seq2.fa> <out> [--protein|--dna] [--format EMBOSS|FASTA] [--gap-open N] [--gap-extend N] [--end-gap-open N] [--end-gap-extend N] [--end-weight]   # Needleman-Wunsch 全局比对（GUI 逆向接口 NeedleManWunschAlign；旧 SimpleBatchProcess 静默无产物已替换）"""
    ensure_bridge("NeedlemanWunschCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "NeedlemanWunschCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="nwAlign")

def _pafcomp_impl(args, verbose=False, quiet=False):
    """pafcomp: pafcomp --inPaf <paf> --outGraph <out> [--colorMode Target|Q"""
    ensure_bridge("PafGC")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PafGC"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pafcomp")

def _pafref_impl(args, verbose=False, quiet=False):
    """pafref: pafref --inPaf <paf> --outTab <out.tsv>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.Paf.PafRefBaseCoverCalc"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pafref")

def _pafviz_impl(args, verbose=False, quiet=False):
    """pafviz: pafviz <in.paf> <out> [graphSize] [colorMode] [switchQT] [mi"""
    ensure_bridge("PafVizCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PafVizCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pafviz")

def _partitionconflict_impl(args, verbose=False, quiet=False):
    """partitionconflict: partitionconflict <inConflictFreq.tsv> <polyPoid> <outCluste"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.ParititionByConflictFreq"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="partitionconflict")

def _peakanno_impl(args, verbose=False, quiet=False):
    """peakanno: peakanno <gxf> <macs2_peak.xls> <out.tsv> [--dist N]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakAnno"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="peakanno")

def _peakdist_impl(args, verbose=False, quiet=False):
    """peakdist: peakdist <chrLen.tsv> <macs2_peak.xls> <out> [--chrHeight H]"""
    ensure_bridge("PeakDistCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PeakDistCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="peakdist")

def _peaktss_impl(args, verbose=False, quiet=False):
    """peaktss: peaktss <gxf> <macs2_peak.xls> <out.svg/png> [--dist N] [--b"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakTssHeatMap"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="peaktss")

def _pep2codon_impl(args, verbose=False, quiet=False):
    """pep2codon: pep2codon <cds.fa> <pep.aln.fa> <codon.aln.out>"""
    ensure_bridge("Pep2CodonCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "Pep2CodonCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pep2codon")

def _pfammotif_impl(args, verbose=False, quiet=False):
    """pfammotif: pfammotif <pfamscan.txt> <in.fasta> <out.svg|png|pdf> [newic"""
    ensure_bridge("PfamMotifCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PfamMotifCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pfammotif")

def _phylotree_impl(args, verbose=False, quiet=False):
    """phylotree: phylotree <in.nwk> <out> [vertical] [width] [height]"""
    ensure_bridge("PhyloTreeCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PhyloTreeCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="phylotree")

def _pileup_impl(args, verbose=False, quiet=False):
    """pileup: pileup <blast.xml> <out.svg> [--query NAME]"""
    ensure_bridge("PileUpCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PileUpCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pileup")

def _plotrna_impl(args, verbose=False, quiet=False):
    """plotrna: plotrna <genomeFA> <region> <SAM> [--directPDF out.pdf]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.miRCoverage.PlotRNAfold"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="plotrna")

def _preparespecies_impl(args, verbose=False, quiet=False):
    """preparespecies: preparespecies <prefix> <inGenome.fa> <inGFF> <outGenome.fa>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.ComparativeGenomics.PrepareSpecies"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="preparespecies")

def _qpcr_impl(args, verbose=False, quiet=False):
    """qpcr: qpcr <data.txt> <out> [w] [h]   (data: name\tmean\tsd)"""
    ensure_bridge("QpcrCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "QpcrCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="qpcr")

def _qpcrExp_impl(args, verbose=False, quiet=False):
    """qpcrExp: qpcrExp <in.qpcr.tab> <out.xls>"""
    ensure_bridge("QpcrDdctCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "QpcrDdctCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="qpcrExp")

def _qpcrproc_impl(args, verbose=False, quiet=False):
    """qpcrproc: qpcrproc <in.qpcr.tab> <out.xls>"""
    ensure_bridge("QpcrProcCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "QpcrProcCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="qpcrproc")

def _quickFamily_impl(args, verbose=False, quiet=False):
    """quickFamily: quickFamily <refPep.fa> <familyIds.txt> <queryPep.fa> <outPr"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.BLAST.ReciprocalBlast.QuickGeneFamilyIdentification"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="quickFamily")

def _recipBlast_impl(args, verbose=False, quiet=False):
    """recipBlast: recipBlast <query.fa> <subject.fa> <outPrefix> [--queryIds i"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.BLAST.ReciprocalBlast.ReciprocalBlast"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="recipBlast")

def _regionAnno_impl(args, verbose=False, quiet=False):
    """regionAnno: regionAnno <in.gff3> <region.txt> <outTab> [--flankLen N] [-"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.RegionGXFOverlapAnnotation"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="regionAnno")

def _regiondepth_impl(args, verbose=False, quiet=False):
    """regiondepth: regiondepth <in.sam> <region> <out.depth> [scaleFactor]"""
    ensure_bridge("RegionDepthCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "RegionDepthCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="regiondepth")

def _rnaplot_impl(args, verbose=False, quiet=False):
    """rnaplot: rnaplot <seq.fa|rawSeq> <out> [--colorMap "seq1=R,G,B;seq2=R"""
    ensure_bridge("RNAplotCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "RNAplotCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="rnaplot")

def _sambamcov_impl(args, verbose=False, quiet=False):
    """sambamcov: sambamcov <in.bam> <out.tsv> [binSize] [countMode]"""
    ensure_bridge("SamBamCovCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SamBamCovCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="sambamcov")

def _sepChr_impl(args, verbose=False, quiet=False):
    """sepChr: sepChr <gene2chr.tsv> <in.miniprot.gff> <outMap>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.SeperateChrByAlleles"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="sepChr")

def _seqconvert_impl(args, verbose=False, quiet=False):
    """seqconvert: seqconvert -i <in> -o <out> -iF <fmt> -oF <fmt>"""
    ensure_bridge("SeqConverterCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SeqConverterCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="seqconvert")

def _seqlentrack_impl(args, verbose=False, quiet=False):
    """seqlentrack: seqlentrack <seqlen.txt> <out.svg|png|pdf> [newick.treefile]"""
    ensure_bridge("SeqLenTrackCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SeqLenTrackCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="seqlentrack")

def _simplehmmscan_impl(args, verbose=False, quiet=False):
    """simplehmmscan: simplehmmscan <pfamA.hmm> <target.pep> <idList.txt> <out.txt"""
    ensure_bridge("SimpleHmmscanCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SimpleHmmscanCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="simplehmmscan")

def _supercircos_impl(args, verbose=False, quiet=False):
    """supercircos: supercircos <config.cfg> <out> [width] [height]"""
    ensure_bridge("SuperCircosCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SuperCircosCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="supercircos")

def _tableAppend_impl(args, verbose=False, quiet=False):
    """tableAppend: tableAppend <inTab1> <inTab2> <outTab> [--c1 N] [--c2 N]   #"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableAppend"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableAppend")

def _tableCast_impl(args, verbose=False, quiet=False):
    """tableCast: tableCast <inLong.txt> <outMatrix>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableCast"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableCast")

def _tableColSel_impl(args, verbose=False, quiet=False):
    """tableColSel: tableColSel <inTable> <outTable> <idList.txt> [--mode Match|"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableColSelector"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableColSel")

def _tableColSelect_impl(args, verbose=False, quiet=False):
    """tableColSelect: tableColSelect <inTable> <outTable> <colName1> [colName2...]"""
    ensure_bridge("TableColManipCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "TableColManipCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableColSelect")

def _tableCollapse_impl(args, verbose=False, quiet=False):
    """tableCollapse: tableCollapse <inTable> <keyColIndex> <outTable> [hasHeader """
    ensure_bridge("TableCollapseCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "TableCollapseCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableCollapse")

def _tableMelt_impl(args, verbose=False, quiet=False):
    """tableMelt: tableMelt <inTable> <outTable>   # 宽表转长表（第88引擎，TableMelt）"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableMelt"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableMelt")

def _tableMerge_impl(args, verbose=False, quiet=False):
    """tableMerge: tableMerge <outTable> <inFile1> [<inFile2>...] [--keyCols 0,"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableMerger"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableMerge")

def _tableSplit_impl(args, verbose=False, quiet=False):
    """tableSplit: tableSplit <inTab> <outDir> [--colIndex N] [--suffix .txt]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableSplitByCol"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableSplit")

def _tableTranspose_impl(args, verbose=False, quiet=False):
    """tableTranspose: tableTranspose <inTable> <outTable>   # 表格转置（第95引擎，TableTran"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableTransposer"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableTranspose")

def _tableUniq_impl(args, verbose=False, quiet=False):
    """tableUniq: tableUniq <inTab> <outFile> [--colIndex N] [--showFreq true|"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableUniq"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableUniq")

def _tauIndex_impl(args, verbose=False, quiet=False):
    """tauIndex: tauIndex <inExpTab> <outTAU>"""
    ensure_bridge("TauCalcCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "TauCalcCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tauIndex")

def _trimmsa_impl(args, verbose=False, quiet=False):
    """trimmsa: trimmsa <in.aln.fa> <out.aln.fa> [ratio]"""
    ensure_bridge("TrimMSACli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "TrimMSACli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="trimmsa")

def _twoSeqBlast_impl(args, verbose=False, quiet=False):
    """twoSeqBlast: twoSeqBlast <query.fa> <subject.fa> <out.txt> [--prog blastp"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.BLAST.CompareTwoSeqSet"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="twoSeqBlast")

def _upset_impl(args, verbose=False, quiet=False):
    """upset: upset <sets.txt> <outFile> [w] [h]"""
    ensure_bridge("UpSetCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "UpSetCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="upset")

def _venn2_impl(args, verbose=False, quiet=False):
    """venn2: venn2 --List1 <setA.txt> --List2 <setB.txt> --label1 A --label2 B --graph <out> --prefix <out> [--bgNum N]"""
    java_args = ["java", "-Xmx2g", "-cp", JAR,
                 "biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn2"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="venn2")

def _venn3_impl(args, verbose=False, quiet=False):
    """venn3: venn3 --List1 <A> --List2 <B> --List3 <C> --label1..3 <labels> --graph <out> --prefix <out>"""
    java_args = ["java", "-Xmx2g", "-cp", JAR,
                 "biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn3"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="venn3")

def _venn4_impl(args, verbose=False, quiet=False):
    """venn4: venn4 --List1 <A> --List2 <B> --List3 <C> --List4 <D> --label1..4 <labels> --graph <out> --prefix <out>"""
    java_args = ["java", "-Xmx2g", "-cp", JAR,
                 "biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn4Ellipse"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="venn4")

def _venn5_impl(args, verbose=False, quiet=False):
    """venn5: venn5 <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> [labels]"""
    ensure_bridge("Venn5Cli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "Venn5Cli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="venn5")

def _venn6_impl(args, verbose=False, quiet=False):
    """venn6: venn6 <out> <setA..F.txt> [labels]"""
    ensure_bridge("Venn6Cli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "Venn6Cli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="venn6")

def _violin_impl(args, verbose=False, quiet=False):
    """violin: violin <in.tsv> <out> [width] [height]"""
    ensure_bridge("ViolinCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "ViolinCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="violin")

def _virusRecomb_impl(args, verbose=False, quiet=False):
    """virusRecomb: virusRecomb <inDB.fa> <inContig.fa> <outDir>   # 病毒重组分析（第77引"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.VirusDetect.RecombinationAnalysis"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="virusRecomb")

def _visualizeblock_impl(args, verbose=False, quiet=False):
    """visualizeblock: visualizeblock <inBlockOut> <out.pdf> [--labels "Genome1,Gen"""
    ensure_bridge("VisualizeCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "VisualizeCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="visualizeblock")

# 共生成 127 个命令实现
def _goEnrich_impl(args, verbose=False, quiet=False):
    """goEnrich: goEnrich <go.obo> <gene2go.tsv> <selectGenes.txt> <outDir>   # GO 富集分析（MF/CC/BP，P+BH 校正，G4 补齐）"""
    ensure_bridge("GoEnrichCli")
    java_args = ["java", "-Xmx4g", "-cp", cp(BUILD_DIR, JAR), "GoEnrichCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="goEnrich")

def _keggEnrich_impl(args, verbose=False, quiet=False):
    """keggEnrich: keggEnrich <reference.keg> <annotation.tsv> <selectIds.txt> <out.xls>   # KEGG 富集分析（G4 补齐，需真实 .keg 参考文件）"""
    ensure_bridge("KeggEnrichCli")
    java_args = ["java", "-Xmx4g", "-cp", cp(BUILD_DIR, JAR), "KeggEnrichCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="keggEnrich")

def _hmmsearch_impl(args, verbose=False, quiet=False):
    """hmmsearch: hmmsearch <pfamA.hmm> <target.pep> <idList.txt> <out.txt>   # HMM Search 域扫描（= simpleHmmscan 引擎，调系统 hmmsearch，G1 补齐别名）"""
    return _simplehmmscan_impl(args, verbose=verbose, quiet=quiet)

def _gxfAttr_impl(args, verbose=False, quiet=False):
    """gxfAttr: gxfAttr <in.gff3|gtf> <out.tsv> [--feature mRNA] [--attrs ID,Name,Parent]   # GXF 属性/ID 对照表提取（G7 补齐，Python 原生，jar 无此引擎）"""
    import re as _re
    # 解析参数
    pos, feature, attrs = [], "mRNA", None
    i = 0
    while i < len(args):
        if args[i] == "--feature" and i + 1 < len(args):
            feature = args[i + 1]; i += 2
        elif args[i] == "--attrs" and i + 1 < len(args):
            attrs = [a.strip() for a in args[i + 1].split(",") if a.strip()]; i += 2
        else:
            pos.append(args[i]); i += 1
    if len(pos) < 2:
        print("用法: gxfAttr <in.gff3|gtf> <out.tsv> [--feature mRNA] [--attrs ID,Name,Parent]", file=sys.stderr)
        return 1
    in_gxf, out_tsv = pos[0], pos[1]
    if not os.path.isfile(in_gxf):
        print(f"❌ 输入文件不存在: {in_gxf}", file=sys.stderr)
        return 2
    def parse_attrs(field):
        """兼容 GFF3 (k=v;) 与 GTF (k "v";) 属性列"""
        d = {}
        for m in _re.finditer(r'([^\s;=]+)\s*=\s*"?([^";]+)"?\s*;?', field):
            d[m.group(1)] = m.group(2)
        if not d:  # GTF 风格
            for m in _re.finditer(r'([^\s;]+)\s+"([^"]+)"\s*;?', field):
                d[m.group(1)] = m.group(2)
        return d
    rows, attr_keys = [], []
    with open(in_gxf, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            feat = parts[2]
            if feature.lower() != "all" and feat.lower() != feature.lower():
                continue
            d = parse_attrs(parts[8])
            d["__feature__"] = feat
            d["__chr__"], d["__start__"], d["__end__"], d["__strand__"] = parts[0], parts[3], parts[4], parts[6]
            rows.append(d)
            for k in d:
                if not k.startswith("__") and k not in attr_keys:
                    attr_keys.append(k)
    if not rows:
        print(f"⚠️ 未提取到 feature={feature} 的记录（--feature all 提取全部）", file=sys.stderr)
        return 1
    # 列序: feature/坐标 + 用户指定 attrs + 其余按出现序
    lead = ["__feature__", "__chr__", "__start__", "__end__", "__strand__"]
    if attrs:
        ordered = attrs + [k for k in attr_keys if k not in attrs]
    else:
        preferred = ["ID", "Name", "Parent", "gene_id", "gene_name", "transcript_id", "symbol", "gene", "product", "Note"]
        ordered = [k for k in preferred if k in attr_keys] + [k for k in attr_keys if k not in preferred]
    header = ["feature", "chr", "start", "end", "strand"] + ordered
    with open(out_tsv, "w", encoding="utf-8") as f:
        f.write("\t".join(header) + "\n")
        for d in rows:
            f.write("\t".join([d.get(k, "") for k in lead] + [d.get(k, "") for k in ordered]) + "\n")
    if not quiet:
        print(f"[gxfAttr] {len(rows)} 条 {feature} 记录 × {len(ordered)} 属性列 → {out_tsv}", file=sys.stderr)
    return 0

def _notung_impl(args, verbose=False, quiet=False):
    """notung: notung <gene.nwk> -s <species.nwk> --reconcile [Notung 原生参数]   # 基因树-物种树 reconcile（duplication/loss 推断，插件 P00651 CLI 化）"""
    notung = os.path.join(ROOT, "plugins", "lib", "Notung-2.9.1.5.jar")
    if not os.path.isfile(notung):
        print(f"❌ Notung 引擎缺失: {notung}", file=sys.stderr)
        return 1
    java_args = ["java", "-Xmx2g", "-jar", notung] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="notung")

def _newickRename_impl(args, verbose=False, quiet=False):
    """newickRename: newickRename --inNwk <tree.nwk> --renameMap <map.tsv> --outNwk <out.nwk>   # 树叶批量重命名（插件 P00690 CLI 化，map 为 OldName\\tNewName）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_NewickRenamer.jar")
    if not os.path.isfile(pjar):
        print(f"❌ 插件缺失: {pjar}", file=sys.stderr)
        return 1
    java_args = ["java", "-Xmx1g", "-cp", f"{pjar}:{JAR}", "newickRenamer.NewickRenamer"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="newickRename")

def _hmmerSearch_impl(args, verbose=False, quiet=False):
    """hmmerSearch: hmmerSearch <target.fa> <hmmDb> <out.tsv>   # Advanced HMMer 全库扫描+domtblout 解析（插件 P00680 CLI 化，无需 idList）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_HmmerSuite.jar")
    if not os.path.isfile(pjar):
        print(f"❌ 插件缺失: {pjar}", file=sys.stderr)
        return 1
    ensure_bridge("HmmerSuiteCli")
    java_args = ["java", "-Xmx2g", "-cp", cp(BUILD_DIR, pjar, JAR), "HmmerSuiteCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="hmmerSearch")

def _memeViz_impl(args, verbose=False, quiet=False):
    """memeViz: memeViz <meme.xml> <out.svg> [width] [height]   # MEME motif 批量可视化（插件 P00700 CLI 化，每 motif 一面板）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Batch_MEME_Motif_Viz.jar")
    if not os.path.isfile(pjar):
        print(f"❌ 插件缺失: {pjar}", file=sys.stderr)
        return 1
    ensure_bridge("BatchVizMotifsCli")
    java_args = ["java", "-Xmx2g", "-cp", cp(BUILD_DIR, pjar, JAR), "BatchVizMotifsCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="memeViz")

def _gsea_impl(args, verbose=False, quiet=False):
    """gsea: gsea <go.obo> <query2go.tsv> <rank.rnk> <outDir>   # GO 预排序 GSEA（插件 P00342 CLI 化，GSEAPreranked 全套报告；⚠️ set_min=15 小基因集会被过滤）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_GSEAWrapper.jar")
    dep = os.path.join(ROOT, "plugins", "lib", "Dependency")
    if not (os.path.isfile(pjar) and os.path.isdir(dep)):
        print(f"❌ GSEA 插件或 Dependency 缺失: {pjar}", file=sys.stderr)
        return 1
    ensure_bridge("GSEAWrapperCli")
    java_args = ["java", "-Xmx4g", "-cp", cp(BUILD_DIR, pjar, JAR), "GSEAWrapperCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="gsea")

def _tfbsShift_impl(args, verbose=False, quiet=False):
    """tfbsShift: tfbsShift <query.pep> <outPrefix> [threads]   # 植物 TF 结合 motif 偏移分析（插件 P00551 CLI 化，参考数据内置 ath.pep+binding.motifs）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_PlantTFbindingMotifShift.jar")
    ath = os.path.join(ROOT, "plugins", "lib", "plantTF", "ath.pep")
    motifs = os.path.join(ROOT, "plugins", "lib", "plantTF", "binding.motifs")
    if not (os.path.isfile(pjar) and os.path.isfile(ath) and os.path.isfile(motifs)):
        print(f"❌ TFBS 插件或参考数据缺失: {pjar}", file=sys.stderr)
        return 1
    ensure_bridge("MotifShiftCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, pjar, JAR), "MotifShiftCli", ath, motifs] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="tfbsShift")

def _kallisto_impl(args, verbose=False, quiet=False):
    """kallisto: kallisto <transcriptome.fa> <reads.fq[,reads2.fq]> <outAbundance> [--kmer N] [--threads N] [--bootstrap N] [--bias] [--single] [--frag-len N] [--frag-sd N]   # RNA-seq 定量（插件 P00740 CLI 化，直调 kallisto 二进制——插件 wrapper 的 Linux 分支有拼接 bug 已绕开）"""
    bin_path = os.path.join(ROOT, "plugins", "lib", "bin", "kallisto")
    if not os.path.isfile(bin_path):
        print(f"❌ kallisto 二进制缺失: {bin_path}", file=sys.stderr)
        return 1
    libs_dir = os.path.join(ROOT, "plugins", "lib", "kallisto-libs")
    # 解析参数
    pos, kmer, threads, bootstrap, bias, single, frag_len, frag_sd = [], 31, 4, 0, False, False, 200, 30
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--kmer" and i + 1 < len(args): kmer = int(args[i + 1]); i += 2
        elif a == "--threads" and i + 1 < len(args): threads = int(args[i + 1]); i += 2
        elif a == "--bootstrap" and i + 1 < len(args): bootstrap = int(args[i + 1]); i += 2
        elif a == "--frag-len" and i + 1 < len(args): frag_len = int(args[i + 1]); i += 2
        elif a == "--frag-sd" and i + 1 < len(args): frag_sd = int(args[i + 1]); i += 2
        elif a == "--bias": bias = True; i += 1
        elif a == "--single": single = True; i += 1
        else: pos.append(a); i += 1
    if len(pos) < 3:
        print("用法: kallisto <transcriptome.fa> <reads.fq[,reads2.fq]> <outAbundance> [--kmer N] [--threads N] [--bootstrap N] [--bias] [--single] [--frag-len N] [--frag-sd N]", file=sys.stderr)
        return 1
    tx, reads_str, out_ab = pos[0], pos[1], pos[2]
    reads = [r.strip() for r in reads_str.split(",")]
    import shutil
    import tempfile
    env = dict(os.environ)
    env["PATH"] = os.path.dirname(bin_path) + os.pathsep + env.get("PATH", "")
    if os.path.isdir(libs_dir):
        env["LD_LIBRARY_PATH"] = libs_dir + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    idx = os.path.join(os.path.dirname(os.path.abspath(out_ab)), os.path.basename(out_ab) + ".kallisto.idx")
    try:
        # 1) index
        os.unlink(idx)
    except OSError:
        pass
    r = subprocess.run([bin_path, "index", "-k", str(kmer), "-i", idx, tx], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ kallisto index 失败:{chr(10)}{r.stderr[-800:]}", file=sys.stderr)
        return r.returncode
    # 2) quant
    tmp_dir = tempfile.mkdtemp(prefix="kallisto_quant_")
    try:
        q = [bin_path, "quant", "-i", idx, "-o", tmp_dir, "-t", str(threads)]
        if bias: q.append("--bias")
        if bootstrap: q += ["-b", str(bootstrap)]
        if single:
            q += ["--single", "-l", str(frag_len), "-s", str(frag_sd)]
        q += reads
        r = subprocess.run(q, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"❌ kallisto quant 失败:{chr(10)}{r.stderr[-800:]}", file=sys.stderr)
            return r.returncode
        abund = os.path.join(tmp_dir, "abundance.tsv")
        if not os.path.isfile(abund):
            print("❌ 未找到 abundance.tsv（quant 输出异常）", file=sys.stderr)
            return 1
        shutil.copy2(abund, out_ab)
        if not quiet:
            print(f"[kallisto] {os.path.basename(out_ab)} 已写出（kmer={kmer} threads={threads}{' bias' if bias else ''}{' single' if single else ''}）", file=sys.stderr)
        return 0
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        try: os.unlink(idx)
        except OSError: pass


def _mcscanxd_impl(args, verbose=False, quiet=False):
    """mcscanxd: mcscanxd <wkDir> <genome1.fa> <genome2.fa> <gxf1> <gxf2> [threads] [blastHits] [evalue]   # OneStep MCScanX-SuperFast（插件 P00370 CLI 化，diamond 加速，二进制随包）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_OneStepMCScanX_Diamond.jar")
    bin_dir = os.path.join(ROOT, "plugins", "lib", "bin")
    if not os.path.isfile(pjar):
        print(f"❌ 插件缺失: {pjar}", file=sys.stderr)
        return 1
    if not os.path.isfile(os.path.join(bin_dir, "diamond")):
        print(f"❌ diamond 二进制缺失: {bin_dir}/diamond", file=sys.stderr)
        return 1
    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
    ensure_bridge("MCScanXFastCli")
    java_args = ["java", "-Xmx4g", "-cp", cp(BUILD_DIR, pjar, JAR), "MCScanXFastCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="mcscanxd")

def _qdot_impl(args, verbose=False, quiet=False):
    """qdot: qdot <blast.tab> <in.gff> <chrLayout.txt> <out.svg> [--point-size N] [--highlight genes.txt]   # 基因组 dot plot（插件 P00380 CLI 化；blast/gff/chrLayout 可由 mcscanxd 产出，绕开插件 quickShow GUI 崩溃直驱 dotdotdot）"""
    ensure_bridge("QuickGenomeDotCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "QuickGenomeDotCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="qdot")

def _quickAnno_impl(args, verbose=False, quiet=False):
    """quickAnno: quickAnno <query.pep> <swissprotDb.fa> <out.txt> [threads] [maxHits]   # diamond 蛋白快速注释（插件 P00480 CLI 化；⚠️ db 需带描述行，否则 Top 词频为空报错）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_QuickProteinAnno.jar")
    bin_dir = os.path.join(ROOT, "plugins", "lib", "bin")
    if not os.path.isfile(pjar):
        print(f"❌ 插件缺失: {pjar}", file=sys.stderr)
        return 1
    if not os.path.isfile(os.path.join(bin_dir, "diamond")):
        print(f"❌ diamond 二进制缺失: {bin_dir}/diamond", file=sys.stderr)
        return 1
    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
    ensure_bridge("QuickProteinAnnoCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, pjar, JAR), "QuickProteinAnnoCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="quickAnno")

def _smart_impl(args, verbose=False, quiet=False):
    """smart: smart <in.fa> <out.txt>   # SMART 域注释（插件 P00060 CLI 化；⚠️ 联网 POST EMBL ismart.embl.de，约 10-60s，输出域位置+类型）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_BatchSMART.jar")
    if not os.path.isfile(pjar):
        print(f"❌ 插件缺失: {pjar}", file=sys.stderr)
        return 1
    ensure_bridge("SubmitSMARTCli")
    java_args = ["java", "-Xmx2g", "-cp", cp(BUILD_DIR, pjar, JAR), "SubmitSMARTCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="smart")

def _fimo_impl(args, verbose=False, quiet=False):
    """fimo: fimo --o <outDir> <motifs.meme> <promoter.fa>   # MEME FIMO motif 扫描（插件 P00552 等价，直调系统 fimo；meme-suite）"""
    import shutil as _sh
    fimo_bin = _sh.which("fimo")
    if not fimo_bin:
        print("❌ 未找到 fimo（meme-suite），安装: apt install meme-suite", file=sys.stderr)
        return 1
    r = subprocess.run([fimo_bin] + args, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ fimo 失败:\n{r.stderr[-600:]}", file=sys.stderr)
        return r.returncode
    if not quiet:
        print("[fimo] 完成 (退出码 0)", file=sys.stderr)
    return 0

def _eggnog_impl(args, verbose=False, quiet=False):
    """eggnog: eggnog <in.fa> -o <prefix> --output_dir <outDir> --data_dir <eggNOGdb> [--cpu N] [--evalue 0.001]   # eggNOG 直系同源注释（GUI 逆向接口 EmapperPipeline；⚠️ 需先就位 eggNOG 数据库）"""
    ensure_bridge("EggnogCli")
    java_args = ["java", "-Xmx4g", "-cp", cp(BUILD_DIR, JAR), "EggnogCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="eggnog")

def _pafviz_impl(args, verbose=False, quiet=False):
    """pafviz: pafviz <in.paf> <out.svg> [--graph-size N] [--color Target|Query|None] [--seed N] [--min-len N] [--switch-qnt] [--rc-color]   # PAF 比对 dot 图（GUI 逆向接口 PafViz.process，绕 quickShow）"""
    ensure_bridge("PafVizCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PafVizCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pafviz")

def _meme_impl(args, verbose=False, quiet=False):
    """meme: meme <in.fa> <workingDir> <outMemeXml> [--nmotifs N] [--minw N] [--maxw N] [--evt 0.05] [--mod zoops|oops|anr]   # MEME motif 发现（GUI 逆向接口 QuickRunMEME，需系统 meme；产物可与 memeViz/fimo 串联）"""
    ensure_bridge("MemeCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MemeCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="meme")

def _upset_impl(args, verbose=False, quiet=False):
    """upset: upset <set1.txt> <set2.txt> [<set3.txt>...] <out.svg> [--min-overlap N] [--rank1 Size|Count|Name] [--rank2 ...] [--rank3 ...] [--size-mode/--count-mode/--name-mode Increasing|Decreasing]   # UpSet 集合图（GUI 逆向接口 UpSetPlot.plot，绕 show 弹窗）"""
    ensure_bridge("UpSetCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "UpSetCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="upset")

def _gbar_impl(args, verbose=False, quiet=False):
    """gbar: gbar <data.tsv> <out.svg> [--header|--no-header] [--errorbar SEM|SD|CI95] [--plot BAR_ERROR|BOXPLOT|VIOLIN|SWARM] [--homoscedastic-t]   # 分组柱状图+显著性标注（GUI 逆向接口 buildPanel；数据=每行 group value）"""
    ensure_bridge("GroupedBarCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GroupedBarCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gbar")

def _amazingmeta_impl(args, verbose=False, quiet=False):
    """amazingmeta: amazingmeta <meme.xml> <newick.treefile> <out.svg|png|pdf> ["""
    ensure_bridge("AmazingMetaCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "AmazingMetaCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="amazingmeta")

def _annocompare_impl(args, verbose=False, quiet=False):
    """annocompare: annocompare <before.gff3> <after.gff3> <outDir> [runName] [r"""
    ensure_bridge("StructAnnoCompareCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "StructAnnoCompareCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="annocompare")

def _bamMerge_impl(args, verbose=False, quiet=False):
    """bamMerge: bamMerge <gtf> <bamDir> <outDir>   # 按区域覆盖合并 BAM（多样本择优）"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAnnotation.BAMMergeByRegionCoverage"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="bamMerge")

def _bamindex_impl(args, verbose=False, quiet=False):
    """bamindex: bamindex <in.sorted.bam> [out.bai]"""
    ensure_bridge("BamIndexCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "BamIndexCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="bamindex")

def _bamsort_impl(args, verbose=False, quiet=False):
    """bamsort: bamsort <in.bam> <out.bam> [sortOrder] [tmpDir]"""
    ensure_bridge("BamSortCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "BamSortCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="bamsort")

def _bamstate_impl(args, verbose=False, quiet=False):
    """bamstate: bamstate <out.tsv> <gff3> <bam1> [<bam2> ...]"""
    ensure_bridge("BamStateCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "BamStateCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="bamstate")

def _barplot_impl(args, verbose=False, quiet=False):
    """barplot: barplot <enrichment.tsv> <out> <termCol> <pvalCol> [classCol"""
    ensure_bridge("BarplotCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "BarplotCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="barplot")

def _barplotter_impl(args, verbose=False, quiet=False):
    """barplotter: barplotter -g <gff> -s <synteny> -c <ctl> -o <out.png>"""
    ensure_bridge("BarPlotterCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "BarPlotterCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="barplotter")

def _batchReplace_impl(args, verbose=False, quiet=False):
    """batchReplace: batchReplace <inFile> <outFile> <patternMap.tsv> [--partial]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.BatchStringReplace"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="batchReplace")

def _calcRepeat_impl(args, verbose=False, quiet=False):
    """calcRepeat: calcRepeat <genome.fa> <outRepeat.txt> [--kmerSize N] [--min"""
    ensure_bridge("CalcRepeatCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "CalcRepeatCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="calcRepeat")

def _cddmotif_impl(args, verbose=False, quiet=False):
    """cddmotif: cddmotif <cdd.hitdata.txt> <in.fasta> <out.svg|png|pdf> [new"""
    ensure_bridge("CddMotifCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "CddMotifCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="cddmotif")

def _circlegene_impl(args, verbose=False, quiet=False):
    """circlegene: circlegene <gff> <geneID.txt> <out> [--rename f --link f --r"""
    ensure_bridge("CircleGeneViewerCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "CircleGeneViewerCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="circlegene")

def _circos_impl(args, verbose=False, quiet=False):
    """circos: circos <chrLen.txt> <link.txt> <genePos.txt> <outFile> [w] ["""
    ensure_bridge("CircosCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "CircosCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="circos")

def _collinearRegion_impl(args, verbose=False, quiet=False):
    """collinearRegion: collinearRegion <in.collinearity> <simGff> <out.txt>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.ComparativeGenomics.MCScanX.CollinearityToRegion"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="collinearRegion")

def _colorscheme_impl(args, verbose=False, quiet=False):
    """colorscheme: colorscheme <inTab> <outTab> <refColIndex>"""
    ensure_bridge("ColorSchemeCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "ColorSchemeCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="colorscheme")

def _conflictpaf_impl(args, verbose=False, quiet=False):
    """conflictpaf: conflictpaf <in.paf> <out.tsv> [binSize]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.CalculateConflictByRefAlignPAF"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="conflictpaf")

def _ctgGroup_impl(args, verbose=False, quiet=False):
    """ctgGroup: ctgGroup <in.miniprot.gff> <polyPoid> <outContigGrpMap>"""
    ensure_bridge("CtgGroupCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "CtgGroupCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="ctgGroup")

def _cubeheatmap_impl(args, verbose=False, quiet=False):
    """cubeheatmap: cubeheatmap <expr.tsv> <group.tsv> <out> [--log10 --minColor"""
    ensure_bridge("CubeHeatmapCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "CubeHeatmapCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="cubeheatmap")

def _degramdom_impl(args, verbose=False, quiet=False):
    """degramdom: degramdom <in.tsv> [out.nwk]"""
    ensure_bridge("DegramdomCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "DegramdomCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="degramdom")

def _distance_impl(args, verbose=False, quiet=False):
    """distance: distance <in.tsv> <col1> <col2> <euclidean|pearson|pearsonDi"""
    ensure_bridge("DistanceCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "DistanceCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="distance")

def _dotplot_impl(args, verbose=False, quiet=False):
    """dotplot: dotplot --inGff <gff> --genePair <pairs> --chrLayout <layout"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.DotPlot.dotdotdot"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="dotplot")

def _dualsyn_impl(args, verbose=False, quiet=False):
    """dualsyn: dualsyn <simplifiedGff> <collinearity> <out> [--chr1 "1,2"] """
    ensure_bridge("DualSynCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "DualSynCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="dualsyn")

def _efpHeat_impl(args, verbose=False, quiet=False):
    """efpHeat: efpHeat <inTGA> <sample2cc.txt> <expMat.tsv> <geneId> <out.s"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.SimpleEfpBrowser.generateSuperHeatMap"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="efpHeat")

def _exprCorr_impl(args, verbose=False, quiet=False):
    """exprCorr: exprCorr <inFPKM> <outCorrMat>"""
    ensure_bridge("ExprCorrCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "ExprCorrCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="exprCorr")

def _fastaExtract_impl(args, verbose=False, quiet=False):
    """fastaExtract: fastaExtract <in.fa> <idList.txt> <out.fa> [--mode Match|Con"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Fasta.ExtractFasta"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="fastaExtract")

def _fastaSubseq_impl(args, verbose=False, quiet=False):
    """fastaSubseq: fastaSubseq <in.fa> <pos.txt> <out.fa>   # 按坐标提子序列（第92引擎，Ext"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Fasta.ExtractFastaSubseq"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="fastaSubseq")

def _filesplit_impl(args, verbose=False, quiet=False):
    """filesplit: filesplit <inFile> <numParts>"""
    ensure_bridge("FileSplitCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "FileSplitCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="filesplit")

def _filterCScore_impl(args, verbose=False, quiet=False):
    """filterCScore: filterCScore <in.blast.tab6> <out.tab6> [--cscore 0.5]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.BLAST.FilterBlastResultByCScore"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="filterCScore")

def _findblockdual_impl(args, verbose=False, quiet=False):
    """findblockdual: findblockdual <queryGenome.fa> <query.gff> <subjectGenome.fa"""
    ensure_bridge("FindBlockDualCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "FindBlockDualCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="findblockdual")

def _findblockmultiple_impl(args, verbose=False, quiet=False):
    """findblockmultiple: findblockmultiple <queryGenome.fa> <query.gff> <queryId> <ou"""
    ensure_bridge("FindBlockMultipleCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "FindBlockMultipleCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="findblockmultiple")

def _findpath_impl(args, verbose=False, quiet=False):
    """findpath: findpath --inGffArr <gff1,gff2,...> --inGenePairs <pairs> --"""
    ensure_bridge("FindPathCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "FindPathCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="findpath")

def _fqTrim_impl(args, verbose=False, quiet=False):
    """fqTrim: fqTrim <in.fq> <out.fq> [--b5 N] [--b3 N] [--threads N]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Fastq.FastqParallelTrimmer"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="fqTrim")

def _fqfaConv_impl(args, verbose=False, quiet=False):
    """fqfaConv: fqfaConv <input> <output> <fq2fa|fa2fq>   # FASTQ/FASTA 互转（第"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.LinuxPipe.FastqAndFasta"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="fqfaConv")

def _gel_impl(args, verbose=False, quiet=False):
    """gel: gel <FragmentRangeArr> <LaneLabels> <MarkerRange> <out>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.GelImage.Marker"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gel")

def _genedensity_impl(args, verbose=False, quiet=False):
    """genedensity: genedensity <in.gff3> <out.tsv> [binSize]"""
    ensure_bridge("GeneDensityCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GeneDensityCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="genedensity")

def _genelocation_impl(args, verbose=False, quiet=False):
    """genelocation: genelocation --ChrLen <chrlen> --FeaturePos <pos> --OutGraph"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.GeneLocation.GeneLocation"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="genelocation")

def _genelocgff_impl(args, verbose=False, quiet=False):
    """genelocgff: genelocgff <gff3> <idList> <out> [--chrLen len.tsv] [--renam"""
    ensure_bridge("GeneLocGffCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GeneLocGffCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="genelocgff")

def _generic_impl(args, verbose=False, quiet=False):
    """generic: generic <engineClass> <method[+method2]> <out> [--set field """
    ensure_bridge("GenericCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GenericCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="generic")

def _gfa_impl(args, verbose=False, quiet=False):
    """gfa: gfa <in.gfa> <out> [width] [height]"""
    ensure_bridge("VizGFACli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "VizGFACli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gfa")

def _gfa2fa_impl(args, verbose=False, quiet=False):
    """gfa2fa: gfa2fa <in.gfa> <out.fa>   # GFA 组装图 → FASTA（第91引擎，GFAtoFast"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Fasta.Tools.GFAtoFasta"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gfa2fa")

def _goParse_impl(args, verbose=False, quiet=False):
    """goParse: goParse <gene2Go.txt> <oboFile> [--level N]   # GO 词典解析（第103"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GeneOntology.littleTools.GOtermParser"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="goParse")

def _groupCol_impl(args, verbose=False, quiet=False):
    """groupCol: groupCol <inTable.tsv> <inGrpInfo.tsv> <outTable> [Sum|Mean|"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableColCollaspe"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="groupCol")

def _groupedbar_impl(args, verbose=False, quiet=False):
    """groupedbar: groupedbar <data.tsv> <out> [plotType] [errorBarType] [hasHe"""
    ensure_bridge("GroupedBarCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GroupedBarCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="groupedbar")

def _gsadiag_impl(args, verbose=False, quiet=False):
    """gsadiag: gsadiag <in.fixed.gff3> <out.stat.xls> [genome.fasta] [relax"""
    ensure_bridge("GsaDiagCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GsaDiagCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gsadiag")

def _gxfAppend_impl(args, verbose=False, quiet=False):
    """gxfAppend: gxfAppend <in.gff3> <out.gff3> <prefix>   # GFF seqid+ID 加前缀"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GxfIDAppender"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfAppend")

def _gxfFix_impl(args, verbose=False, quiet=False):
    """gxfFix: gxfFix <in.gff3> <out.gff3>   # GFF 修复（重复ID前缀/CDS phase/dang"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFfixer.GXFFix"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfFix")

def _gxfGenepos_impl(args, verbose=False, quiet=False):
    """gxfGenepos: gxfGenepos <in.gff3> <outGenepos> <outChrLen> [feature]  # G"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFToGenePosFile"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfGenepos")

def _gxfMatch_impl(args, verbose=False, quiet=False):
    """gxfMatch: gxfMatch <in.gff3> <inGenome.fa>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GxfGenomeMatch"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfMatch")

def _gxfOverlap_impl(args, verbose=False, quiet=False):
    """gxfOverlap: gxfOverlap <in.gff3> <region.txt> <out.gff3> [--ignoreStrand"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFOverlaper"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfOverlap")

def _gxfRecall_impl(args, verbose=False, quiet=False):
    """gxfRecall: gxfRecall <in.gff3> <out.gff3>   # 从 gene 行恢复 mRNA 特征（第82引擎，"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.RecallmRNAFeature"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfRecall")

def _gxfRegion_impl(args, verbose=False, quiet=False):
    """gxfRegion: gxfRegion <in.gff3> <region.txt> <out.gff3> [--ignoreStrand]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFRegionSummary"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfRegion")

def _gxfRename_impl(args, verbose=False, quiet=False):
    """gxfRename: gxfRename <in.gff3> <out.gff3> <renameMap.tsv>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFRenamer"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfRename")

def _gxfRepGXF_impl(args, verbose=False, quiet=False):
    """gxfRepGXF: gxfRepGXF <in.gff3> <out.gff3> [--featureID CDS] [--attachID"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFToRepresentativeGXF"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfRepGXF")

def _gxfRepIDs_impl(args, verbose=False, quiet=False):
    """gxfRepIDs: gxfRepIDs <in.gff3> <out.txt>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFToRepresentativeIDs"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfRepIDs")

def _gxfStat_impl(args, verbose=False, quiet=False):
    """gxfStat: gxfStat <in.gff3> <outStat.xls>   # GFF 统计（基因/mRNA/外显子/内含子/C"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFfixer.GXFstat"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfStat")

def _gxffilter_impl(args, verbose=False, quiet=False):
    """gxffilter: gxffilter <in.gff3|gtf> <idList.txt> <out.gff3|gtf>"""
    ensure_bridge("GxfFilterCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GxfFilterCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxffilter")

def _gxfsort_impl(args, verbose=False, quiet=False):
    """gxfsort: gxfsort <in.gff3|gtf> <out.sorted>"""
    ensure_bridge("GxfSortCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GxfSortCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gxfsort")

def _hicEnzyme_impl(args, verbose=False, quiet=False):
    """hicEnzyme: hicEnzyme <inHiC.fastq>   # HiC 限制酶预测（第76引擎）"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.HiCRestrictionEnzymePrediction"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="hicEnzyme")

def _hmmExtract_impl(args, verbose=False, quiet=False):
    """hmmExtract: hmmExtract <in.hmm> <idList.txt> <out.hmm>   # 从 HMM 文件按 NAM"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.LinuxPipe.hmmInfoExtracter"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="hmmExtract")

def _homoPhase_impl(args, verbose=False, quiet=False):
    """homoPhase: homoPhase <inContigGrpMap> <outPhasedMap>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.HomoConflictBasedPartition"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="homoPhase")

def _layoutheatmap_impl(args, verbose=False, quiet=False):
    """layoutheatmap: layoutheatmap <layout.tsv> <expr.tsv> <out> [--options]"""
    ensure_bridge("LayoutHeatmapCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "LayoutHeatmapCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="layoutheatmap")

def _levelGo_impl(args, verbose=False, quiet=False):
    """levelGo: levelGo <gene2Go.txt> <outTable> <oboFile> [--level N]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GeneOntology.Grapher.LevelDoer"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="levelGo")

def _marker_impl(args, verbose=False, quiet=False):
    """marker: marker <MarkerDist|MarkerFilter|SampleDist|BigMarkerRandomDe"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.markerDesign.BigMarkerRandomDesign"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="marker")

def _markertools_impl(args, verbose=False, quiet=False):
    """markertools: markertools <filter|dist|sampledist> <in.marker.tab> [maxPoi"""
    ensure_bridge("MarkerToolsCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MarkerToolsCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="markertools")

def _mast2tab_impl(args, verbose=False, quiet=False):
    """mast2tab: mast2tab <mast|meme.xml> <out.tab>"""
    ensure_bridge("Mast2TabCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "Mast2TabCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mast2tab")

def _mastExtract_impl(args, verbose=False, quiet=False):
    """mastExtract: mastExtract <in.fa> <mast.xml> <out.txt>   # 从 MAST XML 提取命中"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.MEME.ExtractSeq.ExtractSeqFromMastXML"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mastExtract")

def _mastrun_impl(args, verbose=False, quiet=False):
    """mastrun: mastrun <meme.xml> <seq.fasta> <workingDir> [--motifs M] [--"""
    ensure_bridge("MastRunCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MastRunCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mastrun")

def _mcscanx_impl(args, verbose=False, quiet=False):
    """mcscanx: mcscanx <gff> <blast> <outPrefix> [--html]   # 共线性检测"""
    ensure_bridge("MCScanXCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MCScanXCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mcscanx")

def _memerun_impl(args, verbose=False, quiet=False):
    """memerun: memerun <in.fasta> <workingDir> [--motif N] [--minW N] [--ma"""
    ensure_bridge("MemeRunCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MemeRunCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="memerun")

def _mggxf_impl(args, verbose=False, quiet=False):
    """mggxf: mggxf <inGenePair|blastTab6> <in.simplified.gff> <out.Linked"""
    ensure_bridge("MgGxfCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MgGxfCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mggxf")

def _microgenome_impl(args, verbose=False, quiet=False):
    """microgenome: microgenome <inGBK> <anno.tsv> <out> [micro|macro]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.MicroGenomeViz.MicroGenomeAnnotationCircosPlot"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="microgenome")

def _microsyn_impl(args, verbose=False, quiet=False):
    """microsyn: microsyn <gxf1> <gxf2> <collinearity> <out> [--chr1 C --star"""
    ensure_bridge("MicroSynCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MicroSynCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="microsyn")

def _mirnaIdentify_impl(args, verbose=False, quiet=False):
    """mirnaIdentify: mirnaIdentify <genome.fa> <targetSo.tsv> <outPredict.txt> [o"""
    ensure_bridge("MirIdentifyCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MirIdentifyCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mirnaIdentify")

def _mirnaTarget2_impl(args, verbose=False, quiet=False):
    """mirnaTarget2: mirnaTarget2 <mirna.fa> <target.fa> <out.txt> [--revCom true"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.miRNA.Target2TablePipe"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mirnaTarget2")

def _mirnatarget_impl(args, verbose=False, quiet=False):
    """mirnatarget: mirnatarget <mirna.fa> <target.fa> <out.tsv> [--evalue X] [-"""
    ensure_bridge("TargetScoreCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "TargetScoreCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mirnatarget")

def _mountain_impl(args, verbose=False, quiet=False):
    """mountain: mountain <fold.txt> <out.tsv>"""
    ensure_bridge("MountainPlotCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MountainPlotCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mountain")

def _msy_impl(args, verbose=False, quiet=False):
    """msy: msy <simplifiedGff.pos> <links.txt> <chrLayout.txt> <out> [w"""
    ensure_bridge("GenericCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GenericCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="msy")

def _multiEfp_impl(args, verbose=False, quiet=False):
    """multiEfp: multiEfp <inTGA> <sample2cc> <expMat1[,expMat2,...]> <geneId"""
    ensure_bridge("MultiSuperHeatCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MultiSuperHeatCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="multiEfp")

def _multisyn_impl(args, verbose=False, quiet=False):
    """multisyn: multisyn <gxf.lst> <collinear.lst> <out> [--genes idlist.txt"""
    ensure_bridge("SeveralSpeciesCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SeveralSpeciesCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="multisyn")

def _nwAlign_impl(args, verbose=False, quiet=False):
    """nwAlign: nwAlign <seq1.fa> <seq2.fa> <out> [--protein|--dna] [--format EMBOSS|FASTA] [--gap-open N] [--gap-extend N] [--end-gap-open N] [--end-gap-extend N] [--end-weight]   # Needleman-Wunsch 全局比对（GUI 逆向接口 NeedleManWunschAlign；旧 SimpleBatchProcess 静默无产物已替换）"""
    ensure_bridge("NeedlemanWunschCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "NeedlemanWunschCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="nwAlign")

def _pafcomp_impl(args, verbose=False, quiet=False):
    """pafcomp: pafcomp --inPaf <paf> --outGraph <out> [--colorMode Target|Q"""
    ensure_bridge("PafGC")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PafGC"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pafcomp")

def _pafref_impl(args, verbose=False, quiet=False):
    """pafref: pafref --inPaf <paf> --outTab <out.tsv>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.Paf.PafRefBaseCoverCalc"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pafref")

def _pafviz_impl(args, verbose=False, quiet=False):
    """pafviz: pafviz <in.paf> <out> [graphSize] [colorMode] [switchQT] [mi"""
    ensure_bridge("PafVizCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PafVizCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pafviz")

def _partitionconflict_impl(args, verbose=False, quiet=False):
    """partitionconflict: partitionconflict <inConflictFreq.tsv> <polyPoid> <outCluste"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.ParititionByConflictFreq"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="partitionconflict")

def _peakanno_impl(args, verbose=False, quiet=False):
    """peakanno: peakanno <gxf> <macs2_peak.xls> <out.tsv> [--dist N]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakAnno"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="peakanno")

def _peakdist_impl(args, verbose=False, quiet=False):
    """peakdist: peakdist <chrLen.tsv> <macs2_peak.xls> <out> [--chrHeight H]"""
    ensure_bridge("PeakDistCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PeakDistCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="peakdist")

def _peaktss_impl(args, verbose=False, quiet=False):
    """peaktss: peaktss <gxf> <macs2_peak.xls> <out.svg/png> [--dist N] [--b"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakTssHeatMap"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="peaktss")

def _pep2codon_impl(args, verbose=False, quiet=False):
    """pep2codon: pep2codon <cds.fa> <pep.aln.fa> <codon.aln.out>"""
    ensure_bridge("Pep2CodonCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "Pep2CodonCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pep2codon")

def _pfammotif_impl(args, verbose=False, quiet=False):
    """pfammotif: pfammotif <pfamscan.txt> <in.fasta> <out.svg|png|pdf> [newic"""
    ensure_bridge("PfamMotifCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PfamMotifCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pfammotif")

def _phylotree_impl(args, verbose=False, quiet=False):
    """phylotree: phylotree <in.nwk> <out> [vertical] [width] [height]"""
    ensure_bridge("PhyloTreeCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PhyloTreeCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="phylotree")

def _pileup_impl(args, verbose=False, quiet=False):
    """pileup: pileup <blast.xml> <out.svg> [--query NAME]"""
    ensure_bridge("PileUpCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PileUpCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pileup")

def _plotrna_impl(args, verbose=False, quiet=False):
    """plotrna: plotrna <genomeFA> <region> <SAM> [--directPDF out.pdf]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.miRCoverage.PlotRNAfold"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="plotrna")

def _preparespecies_impl(args, verbose=False, quiet=False):
    """preparespecies: preparespecies <prefix> <inGenome.fa> <inGFF> <outGenome.fa>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.ComparativeGenomics.PrepareSpecies"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="preparespecies")

def _qpcr_impl(args, verbose=False, quiet=False):
    """qpcr: qpcr <data.txt> <out> [w] [h]   (data: name\tmean\tsd)"""
    ensure_bridge("QpcrCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "QpcrCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="qpcr")

def _qpcrExp_impl(args, verbose=False, quiet=False):
    """qpcrExp: qpcrExp <in.qpcr.tab> <out.xls>"""
    ensure_bridge("QpcrDdctCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "QpcrDdctCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="qpcrExp")

def _qpcrproc_impl(args, verbose=False, quiet=False):
    """qpcrproc: qpcrproc <in.qpcr.tab> <out.xls>"""
    ensure_bridge("QpcrProcCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "QpcrProcCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="qpcrproc")

def _quickFamily_impl(args, verbose=False, quiet=False):
    """quickFamily: quickFamily <refPep.fa> <familyIds.txt> <queryPep.fa> <outPr"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.BLAST.ReciprocalBlast.QuickGeneFamilyIdentification"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="quickFamily")

def _recipBlast_impl(args, verbose=False, quiet=False):
    """recipBlast: recipBlast <query.fa> <subject.fa> <outPrefix> [--queryIds i"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.BLAST.ReciprocalBlast.ReciprocalBlast"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="recipBlast")

def _regionAnno_impl(args, verbose=False, quiet=False):
    """regionAnno: regionAnno <in.gff3> <region.txt> <outTab> [--flankLen N] [-"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.RegionGXFOverlapAnnotation"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="regionAnno")

def _regiondepth_impl(args, verbose=False, quiet=False):
    """regiondepth: regiondepth <in.sam> <region> <out.depth> [scaleFactor]"""
    ensure_bridge("RegionDepthCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "RegionDepthCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="regiondepth")

def _rnaplot_impl(args, verbose=False, quiet=False):
    """rnaplot: rnaplot <seq.fa|rawSeq> <out> [--colorMap "seq1=R,G,B;seq2=R"""
    ensure_bridge("RNAplotCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "RNAplotCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="rnaplot")

def _sambamcov_impl(args, verbose=False, quiet=False):
    """sambamcov: sambamcov <in.bam> <out.tsv> [binSize] [countMode]"""
    ensure_bridge("SamBamCovCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SamBamCovCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="sambamcov")

def _sepChr_impl(args, verbose=False, quiet=False):
    """sepChr: sepChr <gene2chr.tsv> <in.miniprot.gff> <outMap>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.SeperateChrByAlleles"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="sepChr")

def _seqconvert_impl(args, verbose=False, quiet=False):
    """seqconvert: seqconvert -i <in> -o <out> -iF <fmt> -oF <fmt>"""
    ensure_bridge("SeqConverterCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SeqConverterCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="seqconvert")

def _seqlentrack_impl(args, verbose=False, quiet=False):
    """seqlentrack: seqlentrack <seqlen.txt> <out.svg|png|pdf> [newick.treefile]"""
    ensure_bridge("SeqLenTrackCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SeqLenTrackCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="seqlentrack")

def _simplehmmscan_impl(args, verbose=False, quiet=False):
    """simplehmmscan: simplehmmscan <pfamA.hmm> <target.pep> <idList.txt> <out.txt"""
    ensure_bridge("SimpleHmmscanCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SimpleHmmscanCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="simplehmmscan")

def _supercircos_impl(args, verbose=False, quiet=False):
    """supercircos: supercircos <config.cfg> <out> [width] [height]"""
    ensure_bridge("SuperCircosCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SuperCircosCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="supercircos")

def _tableAppend_impl(args, verbose=False, quiet=False):
    """tableAppend: tableAppend <inTab1> <inTab2> <outTab> [--c1 N] [--c2 N]   #"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableAppend"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableAppend")

def _tableCast_impl(args, verbose=False, quiet=False):
    """tableCast: tableCast <inLong.txt> <outMatrix>"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableCast"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableCast")

def _tableColSel_impl(args, verbose=False, quiet=False):
    """tableColSel: tableColSel <inTable> <outTable> <idList.txt> [--mode Match|"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableColSelector"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableColSel")

def _tableColSelect_impl(args, verbose=False, quiet=False):
    """tableColSelect: tableColSelect <inTable> <outTable> <colName1> [colName2...]"""
    ensure_bridge("TableColManipCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "TableColManipCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableColSelect")

def _tableCollapse_impl(args, verbose=False, quiet=False):
    """tableCollapse: tableCollapse <inTable> <keyColIndex> <outTable> [hasHeader """
    ensure_bridge("TableCollapseCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "TableCollapseCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableCollapse")

def _tableMelt_impl(args, verbose=False, quiet=False):
    """tableMelt: tableMelt <inTable> <outTable>   # 宽表转长表（第88引擎，TableMelt）"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableMelt"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableMelt")

def _tableMerge_impl(args, verbose=False, quiet=False):
    """tableMerge: tableMerge <outTable> <inFile1> [<inFile2>...] [--keyCols 0,"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableMerger"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableMerge")

def _tableSplit_impl(args, verbose=False, quiet=False):
    """tableSplit: tableSplit <inTab> <outDir> [--colIndex N] [--suffix .txt]"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableSplitByCol"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableSplit")

def _tableTranspose_impl(args, verbose=False, quiet=False):
    """tableTranspose: tableTranspose <inTable> <outTable>   # 表格转置（第95引擎，TableTran"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableTransposer"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableTranspose")

def _tableUniq_impl(args, verbose=False, quiet=False):
    """tableUniq: tableUniq <inTab> <outFile> [--colIndex N] [--showFreq true|"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableUniq"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tableUniq")

def _tauIndex_impl(args, verbose=False, quiet=False):
    """tauIndex: tauIndex <inExpTab> <outTAU>"""
    ensure_bridge("TauCalcCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "TauCalcCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="tauIndex")

def _trimmsa_impl(args, verbose=False, quiet=False):
    """trimmsa: trimmsa <in.aln.fa> <out.aln.fa> [ratio]"""
    ensure_bridge("TrimMSACli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "TrimMSACli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="trimmsa")

def _twoSeqBlast_impl(args, verbose=False, quiet=False):
    """twoSeqBlast: twoSeqBlast <query.fa> <subject.fa> <out.txt> [--prog blastp"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.BLAST.CompareTwoSeqSet"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="twoSeqBlast")

def _upset_impl(args, verbose=False, quiet=False):
    """upset: upset <sets.txt> <outFile> [w] [h]"""
    ensure_bridge("UpSetCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "UpSetCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="upset")

def _venn2_impl(args, verbose=False, quiet=False):
    """venn2: venn2 --List1 <setA.txt> --List2 <setB.txt> --label1 A --label2 B --graph <out> --prefix <out> [--bgNum N]"""
    java_args = ["java", "-Xmx2g", "-cp", JAR,
                 "biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn2"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="venn2")

def _venn3_impl(args, verbose=False, quiet=False):
    """venn3: venn3 --List1 <A> --List2 <B> --List3 <C> --label1..3 <labels> --graph <out> --prefix <out>"""
    java_args = ["java", "-Xmx2g", "-cp", JAR,
                 "biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn3"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="venn3")

def _venn4_impl(args, verbose=False, quiet=False):
    """venn4: venn4 --List1 <A> --List2 <B> --List3 <C> --List4 <D> --label1..4 <labels> --graph <out> --prefix <out>"""
    java_args = ["java", "-Xmx2g", "-cp", JAR,
                 "biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn4Ellipse"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="venn4")

def _venn5_impl(args, verbose=False, quiet=False):
    """venn5: venn5 <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> [labels]"""
    ensure_bridge("Venn5Cli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "Venn5Cli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="venn5")

def _venn6_impl(args, verbose=False, quiet=False):
    """venn6: venn6 <out> <setA..F.txt> [labels]"""
    ensure_bridge("Venn6Cli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "Venn6Cli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="venn6")

def _violin_impl(args, verbose=False, quiet=False):
    """violin: violin <in.tsv> <out> [width] [height]"""
    ensure_bridge("ViolinCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "ViolinCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="violin")

def _virusRecomb_impl(args, verbose=False, quiet=False):
    """virusRecomb: virusRecomb <inDB.fa> <inContig.fa> <outDir>   # 病毒重组分析（第77引"""
    java_args = ["java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.VirusDetect.RecombinationAnalysis"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="virusRecomb")

def _visualizeblock_impl(args, verbose=False, quiet=False):
    """visualizeblock: visualizeblock <inBlockOut> <out.pdf> [--labels "Genome1,Gen"""
    ensure_bridge("VisualizeCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "VisualizeCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="visualizeblock")

# 共生成 127 个命令实现
def _goEnrich_impl(args, verbose=False, quiet=False):
    """goEnrich: goEnrich <go.obo> <gene2go.tsv> <selectGenes.txt> <outDir>   # GO 富集分析（MF/CC/BP，P+BH 校正，G4 补齐）"""
    ensure_bridge("GoEnrichCli")
    java_args = ["java", "-Xmx4g", "-cp", cp(BUILD_DIR, JAR), "GoEnrichCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="goEnrich")

def _keggEnrich_impl(args, verbose=False, quiet=False):
    """keggEnrich: keggEnrich <reference.keg> <annotation.tsv> <selectIds.txt> <out.xls>   # KEGG 富集分析（G4 补齐，需真实 .keg 参考文件）"""
    ensure_bridge("KeggEnrichCli")
    java_args = ["java", "-Xmx4g", "-cp", cp(BUILD_DIR, JAR), "KeggEnrichCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="keggEnrich")

def _hmmsearch_impl(args, verbose=False, quiet=False):
    """hmmsearch: hmmsearch <pfamA.hmm> <target.pep> <idList.txt> <out.txt>   # HMM Search 域扫描（= simpleHmmscan 引擎，调系统 hmmsearch，G1 补齐别名）"""
    return _simplehmmscan_impl(args, verbose=verbose, quiet=quiet)

def _gxfAttr_impl(args, verbose=False, quiet=False):
    """gxfAttr: gxfAttr <in.gff3|gtf> <out.tsv> [--feature mRNA] [--attrs ID,Name,Parent]   # GXF 属性/ID 对照表提取（G7 补齐，Python 原生，jar 无此引擎）"""
    import re as _re
    # 解析参数
    pos, feature, attrs = [], "mRNA", None
    i = 0
    while i < len(args):
        if args[i] == "--feature" and i + 1 < len(args):
            feature = args[i + 1]; i += 2
        elif args[i] == "--attrs" and i + 1 < len(args):
            attrs = [a.strip() for a in args[i + 1].split(",") if a.strip()]; i += 2
        else:
            pos.append(args[i]); i += 1
    if len(pos) < 2:
        print("用法: gxfAttr <in.gff3|gtf> <out.tsv> [--feature mRNA] [--attrs ID,Name,Parent]", file=sys.stderr)
        return 1
    in_gxf, out_tsv = pos[0], pos[1]
    if not os.path.isfile(in_gxf):
        print(f"❌ 输入文件不存在: {in_gxf}", file=sys.stderr)
        return 2
    def parse_attrs(field):
        """兼容 GFF3 (k=v;) 与 GTF (k "v";) 属性列"""
        d = {}
        for m in _re.finditer(r'([^\s;=]+)\s*=\s*"?([^";]+)"?\s*;?', field):
            d[m.group(1)] = m.group(2)
        if not d:  # GTF 风格
            for m in _re.finditer(r'([^\s;]+)\s+"([^"]+)"\s*;?', field):
                d[m.group(1)] = m.group(2)
        return d
    rows, attr_keys = [], []
    with open(in_gxf, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            feat = parts[2]
            if feature.lower() != "all" and feat.lower() != feature.lower():
                continue
            d = parse_attrs(parts[8])
            d["__feature__"] = feat
            d["__chr__"], d["__start__"], d["__end__"], d["__strand__"] = parts[0], parts[3], parts[4], parts[6]
            rows.append(d)
            for k in d:
                if not k.startswith("__") and k not in attr_keys:
                    attr_keys.append(k)
    if not rows:
        print(f"⚠️ 未提取到 feature={feature} 的记录（--feature all 提取全部）", file=sys.stderr)
        return 1
    # 列序: feature/坐标 + 用户指定 attrs + 其余按出现序
    lead = ["__feature__", "__chr__", "__start__", "__end__", "__strand__"]
    if attrs:
        ordered = attrs + [k for k in attr_keys if k not in attrs]
    else:
        preferred = ["ID", "Name", "Parent", "gene_id", "gene_name", "transcript_id", "symbol", "gene", "product", "Note"]
        ordered = [k for k in preferred if k in attr_keys] + [k for k in attr_keys if k not in preferred]
    header = ["feature", "chr", "start", "end", "strand"] + ordered
    with open(out_tsv, "w", encoding="utf-8") as f:
        f.write("\t".join(header) + "\n")
        for d in rows:
            f.write("\t".join([d.get(k, "") for k in lead] + [d.get(k, "") for k in ordered]) + "\n")
    if not quiet:
        print(f"[gxfAttr] {len(rows)} 条 {feature} 记录 × {len(ordered)} 属性列 → {out_tsv}", file=sys.stderr)
    return 0

def _notung_impl(args, verbose=False, quiet=False):
    """notung: notung <gene.nwk> -s <species.nwk> --reconcile [Notung 原生参数]   # 基因树-物种树 reconcile（duplication/loss 推断，插件 P00651 CLI 化）"""
    notung = os.path.join(ROOT, "plugins", "lib", "Notung-2.9.1.5.jar")
    if not os.path.isfile(notung):
        print(f"❌ Notung 引擎缺失: {notung}", file=sys.stderr)
        return 1
    java_args = ["java", "-Xmx2g", "-jar", notung] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="notung")

def _newickRename_impl(args, verbose=False, quiet=False):
    """newickRename: newickRename --inNwk <tree.nwk> --renameMap <map.tsv> --outNwk <out.nwk>   # 树叶批量重命名（插件 P00690 CLI 化，map 为 OldName\\tNewName）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_NewickRenamer.jar")
    if not os.path.isfile(pjar):
        print(f"❌ 插件缺失: {pjar}", file=sys.stderr)
        return 1
    java_args = ["java", "-Xmx1g", "-cp", f"{pjar}:{JAR}", "newickRenamer.NewickRenamer"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="newickRename")

def _hmmerSearch_impl(args, verbose=False, quiet=False):
    """hmmerSearch: hmmerSearch <target.fa> <hmmDb> <out.tsv>   # Advanced HMMer 全库扫描+domtblout 解析（插件 P00680 CLI 化，无需 idList）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_HmmerSuite.jar")
    if not os.path.isfile(pjar):
        print(f"❌ 插件缺失: {pjar}", file=sys.stderr)
        return 1
    ensure_bridge("HmmerSuiteCli")
    java_args = ["java", "-Xmx2g", "-cp", cp(BUILD_DIR, pjar, JAR), "HmmerSuiteCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="hmmerSearch")

def _memeViz_impl(args, verbose=False, quiet=False):
    """memeViz: memeViz <meme.xml> <out.svg> [width] [height]   # MEME motif 批量可视化（插件 P00700 CLI 化，每 motif 一面板）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Batch_MEME_Motif_Viz.jar")
    if not os.path.isfile(pjar):
        print(f"❌ 插件缺失: {pjar}", file=sys.stderr)
        return 1
    ensure_bridge("BatchVizMotifsCli")
    java_args = ["java", "-Xmx2g", "-cp", cp(BUILD_DIR, pjar, JAR), "BatchVizMotifsCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="memeViz")

def _gsea_impl(args, verbose=False, quiet=False):
    """gsea: gsea <go.obo> <query2go.tsv> <rank.rnk> <outDir>   # GO 预排序 GSEA（插件 P00342 CLI 化，GSEAPreranked 全套报告；⚠️ set_min=15 小基因集会被过滤）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_GSEAWrapper.jar")
    dep = os.path.join(ROOT, "plugins", "lib", "Dependency")
    if not (os.path.isfile(pjar) and os.path.isdir(dep)):
        print(f"❌ GSEA 插件或 Dependency 缺失: {pjar}", file=sys.stderr)
        return 1
    ensure_bridge("GSEAWrapperCli")
    java_args = ["java", "-Xmx4g", "-cp", cp(BUILD_DIR, pjar, JAR), "GSEAWrapperCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="gsea")

def _tfbsShift_impl(args, verbose=False, quiet=False):
    """tfbsShift: tfbsShift <query.pep> <outPrefix> [threads]   # 植物 TF 结合 motif 偏移分析（插件 P00551 CLI 化，参考数据内置 ath.pep+binding.motifs）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_PlantTFbindingMotifShift.jar")
    ath = os.path.join(ROOT, "plugins", "lib", "plantTF", "ath.pep")
    motifs = os.path.join(ROOT, "plugins", "lib", "plantTF", "binding.motifs")
    if not (os.path.isfile(pjar) and os.path.isfile(ath) and os.path.isfile(motifs)):
        print(f"❌ TFBS 插件或参考数据缺失: {pjar}", file=sys.stderr)
        return 1
    ensure_bridge("MotifShiftCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, pjar, JAR), "MotifShiftCli", ath, motifs] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="tfbsShift")

def _kallisto_impl(args, verbose=False, quiet=False):
    """kallisto: kallisto <transcriptome.fa> <reads.fq[,reads2.fq]> <outAbundance> [--kmer N] [--threads N] [--bootstrap N] [--bias] [--single] [--frag-len N] [--frag-sd N]   # RNA-seq 定量（插件 P00740 CLI 化，直调 kallisto 二进制——插件 wrapper 的 Linux 分支有拼接 bug 已绕开）"""
    bin_path = os.path.join(ROOT, "plugins", "lib", "bin", "kallisto")
    if not os.path.isfile(bin_path):
        print(f"❌ kallisto 二进制缺失: {bin_path}", file=sys.stderr)
        return 1
    libs_dir = os.path.join(ROOT, "plugins", "lib", "kallisto-libs")
    # 解析参数
    pos, kmer, threads, bootstrap, bias, single, frag_len, frag_sd = [], 31, 4, 0, False, False, 200, 30
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--kmer" and i + 1 < len(args): kmer = int(args[i + 1]); i += 2
        elif a == "--threads" and i + 1 < len(args): threads = int(args[i + 1]); i += 2
        elif a == "--bootstrap" and i + 1 < len(args): bootstrap = int(args[i + 1]); i += 2
        elif a == "--frag-len" and i + 1 < len(args): frag_len = int(args[i + 1]); i += 2
        elif a == "--frag-sd" and i + 1 < len(args): frag_sd = int(args[i + 1]); i += 2
        elif a == "--bias": bias = True; i += 1
        elif a == "--single": single = True; i += 1
        else: pos.append(a); i += 1
    if len(pos) < 3:
        print("用法: kallisto <transcriptome.fa> <reads.fq[,reads2.fq]> <outAbundance> [--kmer N] [--threads N] [--bootstrap N] [--bias] [--single] [--frag-len N] [--frag-sd N]", file=sys.stderr)
        return 1
    tx, reads_str, out_ab = pos[0], pos[1], pos[2]
    reads = [r.strip() for r in reads_str.split(",")]
    import shutil
    import tempfile
    env = dict(os.environ)
    env["PATH"] = os.path.dirname(bin_path) + os.pathsep + env.get("PATH", "")
    if os.path.isdir(libs_dir):
        env["LD_LIBRARY_PATH"] = libs_dir + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    idx = os.path.join(os.path.dirname(os.path.abspath(out_ab)), os.path.basename(out_ab) + ".kallisto.idx")
    try:
        # 1) index
        os.unlink(idx)
    except OSError:
        pass
    r = subprocess.run([bin_path, "index", "-k", str(kmer), "-i", idx, tx], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ kallisto index 失败:{chr(10)}{r.stderr[-800:]}", file=sys.stderr)
        return r.returncode
    # 2) quant
    tmp_dir = tempfile.mkdtemp(prefix="kallisto_quant_")
    try:
        q = [bin_path, "quant", "-i", idx, "-o", tmp_dir, "-t", str(threads)]
        if bias: q.append("--bias")
        if bootstrap: q += ["-b", str(bootstrap)]
        if single:
            q += ["--single", "-l", str(frag_len), "-s", str(frag_sd)]
        q += reads
        r = subprocess.run(q, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"❌ kallisto quant 失败:{chr(10)}{r.stderr[-800:]}", file=sys.stderr)
            return r.returncode
        abund = os.path.join(tmp_dir, "abundance.tsv")
        if not os.path.isfile(abund):
            print("❌ 未找到 abundance.tsv（quant 输出异常）", file=sys.stderr)
            return 1
        shutil.copy2(abund, out_ab)
        if not quiet:
            print(f"[kallisto] {os.path.basename(out_ab)} 已写出（kmer={kmer} threads={threads}{' bias' if bias else ''}{' single' if single else ''}）", file=sys.stderr)
        return 0
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        try: os.unlink(idx)
        except OSError: pass


def _mcscanxd_impl(args, verbose=False, quiet=False):
    """mcscanxd: mcscanxd <wkDir> <genome1.fa> <genome2.fa> <gxf1> <gxf2> [threads] [blastHits] [evalue]   # OneStep MCScanX-SuperFast（插件 P00370 CLI 化，diamond 加速，二进制随包）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_OneStepMCScanX_Diamond.jar")
    bin_dir = os.path.join(ROOT, "plugins", "lib", "bin")
    if not os.path.isfile(pjar):
        print(f"❌ 插件缺失: {pjar}", file=sys.stderr)
        return 1
    if not os.path.isfile(os.path.join(bin_dir, "diamond")):
        print(f"❌ diamond 二进制缺失: {bin_dir}/diamond", file=sys.stderr)
        return 1
    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
    ensure_bridge("MCScanXFastCli")
    java_args = ["java", "-Xmx4g", "-cp", cp(BUILD_DIR, pjar, JAR), "MCScanXFastCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="mcscanxd")

def _qdot_impl(args, verbose=False, quiet=False):
    """qdot: qdot <blast.tab> <in.gff> <chrLayout.txt> <out.svg> [--point-size N] [--highlight genes.txt]   # 基因组 dot plot（插件 P00380 CLI 化；blast/gff/chrLayout 可由 mcscanxd 产出，绕开插件 quickShow GUI 崩溃直驱 dotdotdot）"""
    ensure_bridge("QuickGenomeDotCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "QuickGenomeDotCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="qdot")

def _quickAnno_impl(args, verbose=False, quiet=False):
    """quickAnno: quickAnno <query.pep> <swissprotDb.fa> <out.txt> [threads] [maxHits]   # diamond 蛋白快速注释（插件 P00480 CLI 化；⚠️ db 需带描述行，否则 Top 词频为空报错）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_QuickProteinAnno.jar")
    bin_dir = os.path.join(ROOT, "plugins", "lib", "bin")
    if not os.path.isfile(pjar):
        print(f"❌ 插件缺失: {pjar}", file=sys.stderr)
        return 1
    if not os.path.isfile(os.path.join(bin_dir, "diamond")):
        print(f"❌ diamond 二进制缺失: {bin_dir}/diamond", file=sys.stderr)
        return 1
    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
    ensure_bridge("QuickProteinAnnoCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, pjar, JAR), "QuickProteinAnnoCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="quickAnno")

def _smart_impl(args, verbose=False, quiet=False):
    """smart: smart <in.fa> <out.txt>   # SMART 域注释（插件 P00060 CLI 化；⚠️ 联网 POST EMBL ismart.embl.de，约 10-60s，输出域位置+类型）"""
    pjar = os.path.join(ROOT, "plugins", "lib", "Plugin_BatchSMART.jar")
    if not os.path.isfile(pjar):
        print(f"❌ 插件缺失: {pjar}", file=sys.stderr)
        return 1
    ensure_bridge("SubmitSMARTCli")
    java_args = ["java", "-Xmx2g", "-cp", cp(BUILD_DIR, pjar, JAR), "SubmitSMARTCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="smart")

def _fimo_impl(args, verbose=False, quiet=False):
    """fimo: fimo --o <outDir> <motifs.meme> <promoter.fa>   # MEME FIMO motif 扫描（插件 P00552 等价，直调系统 fimo；meme-suite）"""
    import shutil as _sh
    fimo_bin = _sh.which("fimo")
    if not fimo_bin:
        print("❌ 未找到 fimo（meme-suite），安装: apt install meme-suite", file=sys.stderr)
        return 1
    r = subprocess.run([fimo_bin] + args, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ fimo 失败:\n{r.stderr[-600:]}", file=sys.stderr)
        return r.returncode
    if not quiet:
        print("[fimo] 完成 (退出码 0)", file=sys.stderr)
    return 0

def _eggnog_impl(args, verbose=False, quiet=False):
    """eggnog: eggnog <in.fa> -o <prefix> --output_dir <outDir> --data_dir <eggNOGdb> [--cpu N] [--evalue 0.001]   # eggNOG 直系同源注释（GUI 逆向接口 EmapperPipeline；⚠️ 需先就位 eggNOG 数据库）"""
    ensure_bridge("EggnogCli")
    java_args = ["java", "-Xmx4g", "-cp", cp(BUILD_DIR, JAR), "EggnogCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="eggnog")

def _pafviz_impl(args, verbose=False, quiet=False):
    """pafviz: pafviz <in.paf> <out.svg> [--graph-size N] [--color Target|Query|None] [--seed N] [--min-len N] [--switch-qnt] [--rc-color]   # PAF 比对 dot 图（GUI 逆向接口 PafViz.process，绕 quickShow）"""
    ensure_bridge("PafVizCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "PafVizCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="pafviz")

def _meme_impl(args, verbose=False, quiet=False):
    """meme: meme <in.fa> <workingDir> <outMemeXml> [--nmotifs N] [--minw N] [--maxw N] [--evt 0.05] [--mod zoops|oops|anr]   # MEME motif 发现（GUI 逆向接口 QuickRunMEME，需系统 meme；产物可与 memeViz/fimo 串联）"""
    ensure_bridge("MemeCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MemeCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="meme")

def _upset_impl(args, verbose=False, quiet=False):
    """upset: upset <set1.txt> <set2.txt> [<set3.txt>...] <out.svg> [--min-overlap N] [--rank1 Size|Count|Name] [--rank2 ...] [--rank3 ...] [--size-mode/--count-mode/--name-mode Increasing|Decreasing]   # UpSet 集合图（GUI 逆向接口 UpSetPlot.plot，绕 show 弹窗）"""
    ensure_bridge("UpSetCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "UpSetCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="upset")

def _gbar_impl(args, verbose=False, quiet=False):
    """gbar: gbar <data.tsv> <out.svg> [--header|--no-header] [--errorbar SEM|SD|CI95] [--plot BAR_ERROR|BOXPLOT|VIOLIN|SWARM] [--homoscedastic-t]   # 分组柱状图+显著性标注（GUI 逆向接口 buildPanel；数据=每行 group value）"""
    ensure_bridge("GroupedBarCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GroupedBarCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="gbar")

def _admixtureViz_impl(args, verbose=False, quiet=False):
    """admixtureViz: admixtureViz <q1.txt> <q2.txt> [<q3.txt>...] <out.svg> [--id samples.txt] [--group group.txt] [--sort Qraito|Lexical|None]   # ADMIXTURE Q 矩阵可视化（GUI 逆向接口；Q 文件纯数值矩阵，样本 ID 单独 --id）"""
    ensure_bridge("AdmixtureCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "AdmixtureCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="admixtureViz")

def _golevel_impl(args, verbose=False, quiet=False):
    """golevel: golevel <go.obo> <gene2go.tsv> <outPrefix> [--level N] [--graph] [--width W] [--height H]   # GO 层级统计+柱状图（GUI 逆向接口；统计表纯逻辑，图需 xvfb）"""
    ensure_bridge("GoLevelCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GoLevelCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="golevel")

def _mast_impl(args, verbose=False, quiet=False):
    """mast: mast <sequence.fa> <motifs.meme|meme.xml> <workingDir> [--motif-to-use N] [--max-motif-pvalue 0.0001] [--max-seq-evalue 10]   # MAST motif 搜索（GUI 逆向接口 QuickRunMAST，需系统 mast；产物 mast.html/txt/xml）"""
    ensure_bridge("MastCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MastCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="mast")

def _meme2tab_impl(args, verbose=False, quiet=False):
    """meme2tab: meme2tab <meme.xml|mast.xml> <out.tab>   # MEME/MAST XML→motif 域表（GUI 逆向接口 MEMESuiteXMLtoTab）"""
    ensure_bridge("Meme2TabCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "Meme2TabCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="meme2tab")

def _makemotif_impl(args, verbose=False, quiet=False):
    """makemotif: makemotif <in.seqs.txt> <out.meme> [--mol DNA|RNA|Protein]   # 等长序列→MEME motif 文件（GUI 逆向接口；产物可直接喂 fimo/mast）"""
    ensure_bridge("MakeMotifCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MakeMotifCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="makemotif")

def _mpattern_impl(args, verbose=False, quiet=False):
    """mpattern: mpattern <mast.xml> <out.svg> [--max-motif N] [--shape RoundRect|Rect|Oval] [--line Middle|Up|Down|Splice] [--gradient] [--show-num]   # MEME/MAST motif 序列标注图（GUI 逆向接口，postGraph(String,panel) 重载绕弹窗）"""
    ensure_bridge("MotifPatternCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "MotifPatternCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet, command_name="mpattern")

def _gdensity_impl(args, verbose=False, quiet=False):
    """gdensity: gdensity <in.gff3> <out.geneRecords> <binSize> [--feature <tag>] [--chrlen <file>]   # 基因密度 bin 分析（GUI 逆向接口 GeneDensityProfiler）"""
    ensure_bridge("GeneDensityCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "GeneDensityCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="gdensity")

def _sricher_impl(args, verbose=False, quiet=False):
    """sricher: sricher <in.tsv> <out.xls> <totalAnnoIdx> <totalHitIdx> <selAnnoIdx> <selHitIdx> [--header]   # 简单富集（GUI 逆向接口 SimpleEnricher，超几何+BH；goEnrich 轻量版无需 OBO）"""
    ensure_bridge("SimpleEnricherCli")
    java_args = ["java", "-Xmx3g", "-cp", cp(BUILD_DIR, JAR), "SimpleEnricherCli"] + args
    return run_java(java_args, verbose=verbose, quiet=quiet, command_name="sricher")
