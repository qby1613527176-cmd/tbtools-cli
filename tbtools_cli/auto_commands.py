"""自动生成的 click 命令（从 tbplot.sh 元数据提取，直调 Java）"""
import click, sys, os, subprocess
from tbtools_cli.core import JAR, run_java, run_plot, ensure_bridge, resolve_output, ROOT, BUILD_DIR


def _admixture_impl(args, verbose=False, quiet=False):
    """admixture: admixture <qFiles.lst> <out> [sampleIDFile] [groupFile] [sor"""
    ensure_bridge("AdmixtureCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "AdmixtureCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _amazingmeta_impl(args, verbose=False, quiet=False):
    """amazingmeta: amazingmeta <meme.xml> <newick.treefile> <out.svg|png|pdf> ["""
    ensure_bridge("AmazingMetaCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "AmazingMetaCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _annocompare_impl(args, verbose=False, quiet=False):
    """annocompare: annocompare <before.gff3> <after.gff3> <outDir> [runName] [r"""
    ensure_bridge("StructAnnoCompareCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "StructAnnoCompareCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _bamMerge_impl(args, verbose=False, quiet=False):
    """bamMerge: bamMerge <gtf> <bamDir> <outDir>   # 按区域覆盖合并 BAM（多样本择优）"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAnnotation.BAMMergeByRegionCoverage"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _bamindex_impl(args, verbose=False, quiet=False):
    """bamindex: bamindex <in.sorted.bam> [out.bai]"""
    ensure_bridge("BamIndexCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "BamIndexCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _bamsort_impl(args, verbose=False, quiet=False):
    """bamsort: bamsort <in.bam> <out.bam> [sortOrder] [tmpDir]"""
    ensure_bridge("BamSortCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "BamSortCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _bamstate_impl(args, verbose=False, quiet=False):
    """bamstate: bamstate <out.tsv> <gff3> <bam1> [<bam2> ...]"""
    ensure_bridge("BamStateCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "BamStateCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _barplot_impl(args, verbose=False, quiet=False):
    """barplot: barplot <enrichment.tsv> <out> <termCol> <pvalCol> [classCol"""
    ensure_bridge("BarplotCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "BarplotCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _barplotter_impl(args, verbose=False, quiet=False):
    """barplotter: barplotter -g <gff> -s <synteny> -c <ctl> -o <out.png>"""
    ensure_bridge("BarPlotterCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "BarPlotterCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _batchReplace_impl(args, verbose=False, quiet=False):
    """batchReplace: batchReplace <inFile> <outFile> <patternMap.tsv> [--partial]"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.BatchStringReplace"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _calcRepeat_impl(args, verbose=False, quiet=False):
    """calcRepeat: calcRepeat <genome.fa> <outRepeat.txt> [--kmerSize N] [--min"""
    ensure_bridge("CalcRepeatCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "CalcRepeatCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _cddmotif_impl(args, verbose=False, quiet=False):
    """cddmotif: cddmotif <cdd.hitdata.txt> <in.fasta> <out.svg|png|pdf> [new"""
    ensure_bridge("CddMotifCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "CddMotifCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _circlegene_impl(args, verbose=False, quiet=False):
    """circlegene: circlegene <gff> <geneID.txt> <out> [--rename f --link f --r"""
    ensure_bridge("CircleGeneViewerCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "CircleGeneViewerCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _circos_impl(args, verbose=False, quiet=False):
    """circos: circos <chrLen.txt> <link.txt> <genePos.txt> <outFile> [w] ["""
    ensure_bridge("CircosCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "CircosCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _collinearRegion_impl(args, verbose=False, quiet=False):
    """collinearRegion: collinearRegion <in.collinearity> <simGff> <out.txt>"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.ComparativeGenomics.MCScanX.CollinearityToRegion"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _colorscheme_impl(args, verbose=False, quiet=False):
    """colorscheme: colorscheme <inTab> <outTab> <refColIndex>"""
    ensure_bridge("ColorSchemeCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "ColorSchemeCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _conflictpaf_impl(args, verbose=False, quiet=False):
    """conflictpaf: conflictpaf <in.paf> <out.tsv> [binSize]"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.CalculateConflictByRefAlignPAF"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _ctgGroup_impl(args, verbose=False, quiet=False):
    """ctgGroup: ctgGroup <in.miniprot.gff> <polyPoid> <outContigGrpMap>"""
    ensure_bridge("CtgGroupCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "CtgGroupCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _cubeheatmap_impl(args, verbose=False, quiet=False):
    """cubeheatmap: cubeheatmap <expr.tsv> <group.tsv> <out> [--log10 --minColor"""
    ensure_bridge("CubeHeatmapCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "CubeHeatmapCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _degramdom_impl(args, verbose=False, quiet=False):
    """degramdom: degramdom <in.tsv> [out.nwk]"""
    ensure_bridge("DegramdomCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "DegramdomCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _distance_impl(args, verbose=False, quiet=False):
    """distance: distance <in.tsv> <col1> <col2> <euclidean|pearson|pearsonDi"""
    ensure_bridge("DistanceCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "DistanceCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _dotplot_impl(args, verbose=False, quiet=False):
    """dotplot: dotplot --inGff <gff> --genePair <pairs> --chrLayout <layout"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.DotPlot.dotdotdot"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _dualsyn_impl(args, verbose=False, quiet=False):
    """dualsyn: dualsyn <simplifiedGff> <collinearity> <out> [--chr1 "1,2"] """
    ensure_bridge("DualSynCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "DualSynCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _efpHeat_impl(args, verbose=False, quiet=False):
    """efpHeat: efpHeat <inTGA> <sample2cc.txt> <expMat.tsv> <geneId> <out.s"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.SimpleEfpBrowser.generateSuperHeatMap"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _exprCorr_impl(args, verbose=False, quiet=False):
    """exprCorr: exprCorr <inFPKM> <outCorrMat>"""
    ensure_bridge("ExprCorrCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "ExprCorrCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _fastaExtract_impl(args, verbose=False, quiet=False):
    """fastaExtract: fastaExtract <in.fa> <idList.txt> <out.fa> [--mode Match|Con"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Fasta.ExtractFasta"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _fastaSubseq_impl(args, verbose=False, quiet=False):
    """fastaSubseq: fastaSubseq <in.fa> <pos.txt> <out.fa>   # 按坐标提子序列（第92引擎，Ext"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Fasta.ExtractFastaSubseq"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _filesplit_impl(args, verbose=False, quiet=False):
    """filesplit: filesplit <inFile> <numParts>"""
    ensure_bridge("FileSplitCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "FileSplitCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _filterCScore_impl(args, verbose=False, quiet=False):
    """filterCScore: filterCScore <in.blast.tab6> <out.tab6> [--cscore 0.5]"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.BLAST.FilterBlastResultByCScore"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _findblockdual_impl(args, verbose=False, quiet=False):
    """findblockdual: findblockdual <queryGenome.fa> <query.gff> <subjectGenome.fa"""
    ensure_bridge("FindBlockDualCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "FindBlockDualCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _findblockmultiple_impl(args, verbose=False, quiet=False):
    """findblockmultiple: findblockmultiple <queryGenome.fa> <query.gff> <queryId> <ou"""
    ensure_bridge("FindBlockMultipleCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "FindBlockMultipleCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _findpath_impl(args, verbose=False, quiet=False):
    """findpath: findpath --inGffArr <gff1,gff2,...> --inGenePairs <pairs> --"""
    ensure_bridge("FindPathCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "FindPathCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _fqTrim_impl(args, verbose=False, quiet=False):
    """fqTrim: fqTrim <in.fq> <out.fq> [--b5 N] [--b3 N] [--threads N]"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Fastq.FastqParallelTrimmer"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _fqfaConv_impl(args, verbose=False, quiet=False):
    """fqfaConv: fqfaConv <input> <output> <fq2fa|fa2fq>   # FASTQ/FASTA 互转（第"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.LinuxPipe.FastqAndFasta"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gel_impl(args, verbose=False, quiet=False):
    """gel: gel <FragmentRangeArr> <LaneLabels> <MarkerRange> <out>"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.GelImage.Marker"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _genedensity_impl(args, verbose=False, quiet=False):
    """genedensity: genedensity <in.gff3> <out.tsv> [binSize]"""
    ensure_bridge("GeneDensityCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "GeneDensityCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _genelocation_impl(args, verbose=False, quiet=False):
    """genelocation: genelocation --ChrLen <chrlen> --FeaturePos <pos> --OutGraph"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.GeneLocation.GeneLocation"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _genelocgff_impl(args, verbose=False, quiet=False):
    """genelocgff: genelocgff <gff3> <idList> <out> [--chrLen len.tsv] [--renam"""
    ensure_bridge("GeneLocGffCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "GeneLocGffCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _generic_impl(args, verbose=False, quiet=False):
    """generic: generic <engineClass> <method[+method2]> <out> [--set field """
    ensure_bridge("GenericCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "GenericCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gfa_impl(args, verbose=False, quiet=False):
    """gfa: gfa <in.gfa> <out> [width] [height]"""
    ensure_bridge("VizGFACli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "VizGFACli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gfa2fa_impl(args, verbose=False, quiet=False):
    """gfa2fa: gfa2fa <in.gfa> <out.fa>   # GFA 组装图 → FASTA（第91引擎，GFAtoFast"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Fasta.Tools.GFAtoFasta"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _goParse_impl(args, verbose=False, quiet=False):
    """goParse: goParse <gene2Go.txt> <oboFile> [--level N]   # GO 词典解析（第103"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GeneOntology.littleTools.GOtermParser"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _groupCol_impl(args, verbose=False, quiet=False):
    """groupCol: groupCol <inTable.tsv> <inGrpInfo.tsv> <outTable> [Sum|Mean|"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableColCollaspe"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _groupedbar_impl(args, verbose=False, quiet=False):
    """groupedbar: groupedbar <data.tsv> <out> [plotType] [errorBarType] [hasHe"""
    ensure_bridge("GroupedBarCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "GroupedBarCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gsadiag_impl(args, verbose=False, quiet=False):
    """gsadiag: gsadiag <in.fixed.gff3> <out.stat.xls> [genome.fasta] [relax"""
    ensure_bridge("GsaDiagCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "GsaDiagCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxfAppend_impl(args, verbose=False, quiet=False):
    """gxfAppend: gxfAppend <in.gff3> <out.gff3> <prefix>   # GFF seqid+ID 加前缀"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GxfIDAppender"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxfFix_impl(args, verbose=False, quiet=False):
    """gxfFix: gxfFix <in.gff3> <out.gff3>   # GFF 修复（重复ID前缀/CDS phase/dang"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFfixer.GXFFix"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxfGenepos_impl(args, verbose=False, quiet=False):
    """gxfGenepos: gxfGenepos <in.gff3> <outGenepos> <outChrLen> [feature]  # G"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFToGenePosFile"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxfMatch_impl(args, verbose=False, quiet=False):
    """gxfMatch: gxfMatch <in.gff3> <inGenome.fa>"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GxfGenomeMatch"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxfOverlap_impl(args, verbose=False, quiet=False):
    """gxfOverlap: gxfOverlap <in.gff3> <region.txt> <out.gff3> [--ignoreStrand"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFOverlaper"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxfRecall_impl(args, verbose=False, quiet=False):
    """gxfRecall: gxfRecall <in.gff3> <out.gff3>   # 从 gene 行恢复 mRNA 特征（第82引擎，"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.RecallmRNAFeature"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxfRegion_impl(args, verbose=False, quiet=False):
    """gxfRegion: gxfRegion <in.gff3> <region.txt> <out.gff3> [--ignoreStrand]"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFRegionSummary"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxfRename_impl(args, verbose=False, quiet=False):
    """gxfRename: gxfRename <in.gff3> <out.gff3> <renameMap.tsv>"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFRenamer"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxfRepGXF_impl(args, verbose=False, quiet=False):
    """gxfRepGXF: gxfRepGXF <in.gff3> <out.gff3> [--featureID CDS] [--attachID"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFToRepresentativeGXF"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxfRepIDs_impl(args, verbose=False, quiet=False):
    """gxfRepIDs: gxfRepIDs <in.gff3> <out.txt>"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFToRepresentativeIDs"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxfStat_impl(args, verbose=False, quiet=False):
    """gxfStat: gxfStat <in.gff3> <outStat.xls>   # GFF 统计（基因/mRNA/外显子/内含子/C"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.GXFfixer.GXFstat"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxffilter_impl(args, verbose=False, quiet=False):
    """gxffilter: gxffilter <in.gff3|gtf> <idList.txt> <out.gff3|gtf>"""
    ensure_bridge("GxfFilterCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "GxfFilterCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _gxfsort_impl(args, verbose=False, quiet=False):
    """gxfsort: gxfsort <in.gff3|gtf> <out.sorted>"""
    ensure_bridge("GxfSortCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "GxfSortCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _hicEnzyme_impl(args, verbose=False, quiet=False):
    """hicEnzyme: hicEnzyme <inHiC.fastq>   # HiC 限制酶预测（第76引擎）"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.HiCRestrictionEnzymePrediction"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _hmmExtract_impl(args, verbose=False, quiet=False):
    """hmmExtract: hmmExtract <in.hmm> <idList.txt> <out.hmm>   # 从 HMM 文件按 NAM"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.LinuxPipe.hmmInfoExtracter"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _homoPhase_impl(args, verbose=False, quiet=False):
    """homoPhase: homoPhase <inContigGrpMap> <outPhasedMap>"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.HomoConflictBasedPartition"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _layoutheatmap_impl(args, verbose=False, quiet=False):
    """layoutheatmap: layoutheatmap <layout.tsv> <expr.tsv> <out> [--options]"""
    ensure_bridge("LayoutHeatmapCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "LayoutHeatmapCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _levelGo_impl(args, verbose=False, quiet=False):
    """levelGo: levelGo <gene2Go.txt> <outTable> <oboFile> [--level N]"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GeneOntology.Grapher.LevelDoer"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _marker_impl(args, verbose=False, quiet=False):
    """marker: marker <MarkerDist|MarkerFilter|SampleDist|BigMarkerRandomDe"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.markerDesign.BigMarkerRandomDesign"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _markertools_impl(args, verbose=False, quiet=False):
    """markertools: markertools <filter|dist|sampledist> <in.marker.tab> [maxPoi"""
    ensure_bridge("MarkerToolsCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "MarkerToolsCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _mast2tab_impl(args, verbose=False, quiet=False):
    """mast2tab: mast2tab <mast|meme.xml> <out.tab>"""
    ensure_bridge("Mast2TabCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "Mast2TabCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _mastExtract_impl(args, verbose=False, quiet=False):
    """mastExtract: mastExtract <in.fa> <mast.xml> <out.txt>   # 从 MAST XML 提取命中"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.MEME.ExtractSeq.ExtractSeqFromMastXML"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _mastrun_impl(args, verbose=False, quiet=False):
    """mastrun: mastrun <meme.xml> <seq.fasta> <workingDir> [--motifs M] [--"""
    ensure_bridge("MastRunCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "MastRunCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _mcscanx_impl(args, verbose=False, quiet=False):
    """mcscanx: mcscanx <gff> <blast> <outPrefix> [--html]   # 共线性检测"""
    ensure_bridge("MCScanXCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "MCScanXCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _memerun_impl(args, verbose=False, quiet=False):
    """memerun: memerun <in.fasta> <workingDir> [--motif N] [--minW N] [--ma"""
    ensure_bridge("MemeRunCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "MemeRunCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _mggxf_impl(args, verbose=False, quiet=False):
    """mggxf: mggxf <inGenePair|blastTab6> <in.simplified.gff> <out.Linked"""
    ensure_bridge("MgGxfCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "MgGxfCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _microgenome_impl(args, verbose=False, quiet=False):
    """microgenome: microgenome <inGBK> <anno.tsv> <out> [micro|macro]"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.MicroGenomeViz.MicroGenomeAnnotationCircosPlot"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _microsyn_impl(args, verbose=False, quiet=False):
    """microsyn: microsyn <gxf1> <gxf2> <collinearity> <out> [--chr1 C --star"""
    ensure_bridge("MicroSynCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "MicroSynCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _mirnaIdentify_impl(args, verbose=False, quiet=False):
    """mirnaIdentify: mirnaIdentify <genome.fa> <targetSo.tsv> <outPredict.txt> [o"""
    ensure_bridge("MirIdentifyCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "MirIdentifyCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _mirnaTarget2_impl(args, verbose=False, quiet=False):
    """mirnaTarget2: mirnaTarget2 <mirna.fa> <target.fa> <out.txt> [--revCom true"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.miRNA.Target2TablePipe"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _mirnatarget_impl(args, verbose=False, quiet=False):
    """mirnatarget: mirnatarget <mirna.fa> <target.fa> <out.tsv> [--evalue X] [-"""
    ensure_bridge("TargetScoreCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "TargetScoreCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _mountain_impl(args, verbose=False, quiet=False):
    """mountain: mountain <fold.txt> <out.tsv>"""
    ensure_bridge("MountainPlotCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "MountainPlotCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _msy_impl(args, verbose=False, quiet=False):
    """msy: msy <simplifiedGff.pos> <links.txt> <chrLayout.txt> <out> [w"""
    ensure_bridge("GenericCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "GenericCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _multiEfp_impl(args, verbose=False, quiet=False):
    """multiEfp: multiEfp <inTGA> <sample2cc> <expMat1[,expMat2,...]> <geneId"""
    ensure_bridge("MultiSuperHeatCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "MultiSuperHeatCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _multisyn_impl(args, verbose=False, quiet=False):
    """multisyn: multisyn <gxf.lst> <collinear.lst> <out> [--genes idlist.txt"""
    ensure_bridge("SeveralSpeciesCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "SeveralSpeciesCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _nwAlign_impl(args, verbose=False, quiet=False):
    """nwAlign: nwAlign <inSeq1.txt> <inSeq2.txt> <out>   # Needleman-Wunsch"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Aligner.NeedleMan.SimpleBatchProcess"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _pafcomp_impl(args, verbose=False, quiet=False):
    """pafcomp: pafcomp --inPaf <paf> --outGraph <out> [--colorMode Target|Q"""
    ensure_bridge("PafGC")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "PafGC"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _pafref_impl(args, verbose=False, quiet=False):
    """pafref: pafref --inPaf <paf> --outTab <out.tsv>"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.Paf.PafRefBaseCoverCalc"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _pafviz_impl(args, verbose=False, quiet=False):
    """pafviz: pafviz <in.paf> <out> [graphSize] [colorMode] [switchQT] [mi"""
    ensure_bridge("PafVizCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "PafVizCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _partitionconflict_impl(args, verbose=False, quiet=False):
    """partitionconflict: partitionconflict <inConflictFreq.tsv> <polyPoid> <outCluste"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.ParititionByConflictFreq"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _peakanno_impl(args, verbose=False, quiet=False):
    """peakanno: peakanno <gxf> <macs2_peak.xls> <out.tsv> [--dist N]"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakAnno"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _peakdist_impl(args, verbose=False, quiet=False):
    """peakdist: peakdist <chrLen.tsv> <macs2_peak.xls> <out> [--chrHeight H]"""
    ensure_bridge("PeakDistCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "PeakDistCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _peaktss_impl(args, verbose=False, quiet=False):
    """peaktss: peaktss <gxf> <macs2_peak.xls> <out.svg/png> [--dist N] [--b"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakTssHeatMap"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _pep2codon_impl(args, verbose=False, quiet=False):
    """pep2codon: pep2codon <cds.fa> <pep.aln.fa> <codon.aln.out>"""
    ensure_bridge("Pep2CodonCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "Pep2CodonCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _pfammotif_impl(args, verbose=False, quiet=False):
    """pfammotif: pfammotif <pfamscan.txt> <in.fasta> <out.svg|png|pdf> [newic"""
    ensure_bridge("PfamMotifCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "PfamMotifCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _phylotree_impl(args, verbose=False, quiet=False):
    """phylotree: phylotree <in.nwk> <out> [vertical] [width] [height]"""
    ensure_bridge("PhyloTreeCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "PhyloTreeCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _pileup_impl(args, verbose=False, quiet=False):
    """pileup: pileup <blast.xml> <out.svg> [--query NAME]"""
    ensure_bridge("PileUpCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "PileUpCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _plotrna_impl(args, verbose=False, quiet=False):
    """plotrna: plotrna <genomeFA> <region> <SAM> [--directPDF out.pdf]"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.JIGplotToolkit.miRCoverage.PlotRNAfold"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _preparespecies_impl(args, verbose=False, quiet=False):
    """preparespecies: preparespecies <prefix> <inGenome.fa> <inGFF> <outGenome.fa>"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.ComparativeGenomics.PrepareSpecies"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _qpcr_impl(args, verbose=False, quiet=False):
    """qpcr: qpcr <data.txt> <out> [w] [h]   (data: name\tmean\tsd)"""
    ensure_bridge("QpcrCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "QpcrCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _qpcrExp_impl(args, verbose=False, quiet=False):
    """qpcrExp: qpcrExp <in.qpcr.tab> <out.xls>"""
    ensure_bridge("QpcrDdctCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "QpcrDdctCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _qpcrproc_impl(args, verbose=False, quiet=False):
    """qpcrproc: qpcrproc <in.qpcr.tab> <out.xls>"""
    ensure_bridge("QpcrProcCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "QpcrProcCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _quickFamily_impl(args, verbose=False, quiet=False):
    """quickFamily: quickFamily <refPep.fa> <familyIds.txt> <queryPep.fa> <outPr"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.BLAST.ReciprocalBlast.QuickGeneFamilyIdentification"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _recipBlast_impl(args, verbose=False, quiet=False):
    """recipBlast: recipBlast <query.fa> <subject.fa> <outPrefix> [--queryIds i"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.BLAST.ReciprocalBlast.ReciprocalBlast"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _regionAnno_impl(args, verbose=False, quiet=False):
    """regionAnno: regionAnno <in.gff3> <region.txt> <outTab> [--flankLen N] [-"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GXFUtils.RegionGXFOverlapAnnotation"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _regiondepth_impl(args, verbose=False, quiet=False):
    """regiondepth: regiondepth <in.sam> <region> <out.depth> [scaleFactor]"""
    ensure_bridge("RegionDepthCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "RegionDepthCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _rnaplot_impl(args, verbose=False, quiet=False):
    """rnaplot: rnaplot <seq.fa|rawSeq> <out> [--colorMap "seq1=R,G,B;seq2=R"""
    ensure_bridge("RNAplotCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "RNAplotCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _sambamcov_impl(args, verbose=False, quiet=False):
    """sambamcov: sambamcov <in.bam> <out.tsv> [binSize] [countMode]"""
    ensure_bridge("SamBamCovCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "SamBamCovCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _sepChr_impl(args, verbose=False, quiet=False):
    """sepChr: sepChr <gene2chr.tsv> <in.miniprot.gff> <outMap>"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.GenomeAssembly.SeperateChrByAlleles"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _seqconvert_impl(args, verbose=False, quiet=False):
    """seqconvert: seqconvert -i <in> -o <out> -iF <fmt> -oF <fmt>"""
    ensure_bridge("SeqConverterCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "SeqConverterCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _seqlentrack_impl(args, verbose=False, quiet=False):
    """seqlentrack: seqlentrack <seqlen.txt> <out.svg|png|pdf> [newick.treefile]"""
    ensure_bridge("SeqLenTrackCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "SeqLenTrackCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _simplehmmscan_impl(args, verbose=False, quiet=False):
    """simplehmmscan: simplehmmscan <pfamA.hmm> <target.pep> <idList.txt> <out.txt"""
    ensure_bridge("SimpleHmmscanCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "SimpleHmmscanCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _supercircos_impl(args, verbose=False, quiet=False):
    """supercircos: supercircos <config.cfg> <out> [width] [height]"""
    ensure_bridge("SuperCircosCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "SuperCircosCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _tableAppend_impl(args, verbose=False, quiet=False):
    """tableAppend: tableAppend <inTab1> <inTab2> <outTab> [--c1 N] [--c2 N]   #"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableAppend"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _tableCast_impl(args, verbose=False, quiet=False):
    """tableCast: tableCast <inLong.txt> <outMatrix>"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableCast"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _tableColSel_impl(args, verbose=False, quiet=False):
    """tableColSel: tableColSel <inTable> <outTable> <idList.txt> [--mode Match|"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableColSelector"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _tableColSelect_impl(args, verbose=False, quiet=False):
    """tableColSelect: tableColSelect <inTable> <outTable> <colName1> [colName2...]"""
    ensure_bridge("TableColManipCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "TableColManipCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _tableCollapse_impl(args, verbose=False, quiet=False):
    """tableCollapse: tableCollapse <inTable> <keyColIndex> <outTable> [hasHeader """
    ensure_bridge("TableCollapseCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "TableCollapseCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _tableMelt_impl(args, verbose=False, quiet=False):
    """tableMelt: tableMelt <inTable> <outTable>   # 宽表转长表（第88引擎，TableMelt）"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableMelt"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _tableMerge_impl(args, verbose=False, quiet=False):
    """tableMerge: tableMerge <outTable> <inFile1> [<inFile2>...] [--keyCols 0,"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableMerger"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _tableSplit_impl(args, verbose=False, quiet=False):
    """tableSplit: tableSplit <inTab> <outDir> [--colIndex N] [--suffix .txt]"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableSplitByCol"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _tableTranspose_impl(args, verbose=False, quiet=False):
    """tableTranspose: tableTranspose <inTable> <outTable>   # 表格转置（第95引擎，TableTran"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableTransposer"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _tableUniq_impl(args, verbose=False, quiet=False):
    """tableUniq: tableUniq <inTab> <outFile> [--colIndex N] [--showFreq true|"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.Table.TableUniq"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _tauIndex_impl(args, verbose=False, quiet=False):
    """tauIndex: tauIndex <inExpTab> <outTAU>"""
    ensure_bridge("TauCalcCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "TauCalcCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _trimmsa_impl(args, verbose=False, quiet=False):
    """trimmsa: trimmsa <in.aln.fa> <out.aln.fa> [ratio]"""
    ensure_bridge("TrimMSACli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "TrimMSACli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _twoSeqBlast_impl(args, verbose=False, quiet=False):
    """twoSeqBlast: twoSeqBlast <query.fa> <subject.fa> <out.txt> [--prog blastp"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.BLAST.CompareTwoSeqSet"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _upset_impl(args, verbose=False, quiet=False):
    """upset: upset <sets.txt> <outFile> [w] [h]"""
    ensure_bridge("UpSetCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "UpSetCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _venn2_impl(args, verbose=False, quiet=False):
    """venn2: venn2 --List1 <setA.txt> --List2 <setB.txt> --label1 A --label2 B --graph <out> --prefix <out> [--bgNum N]"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx2g", "-cp", JAR,
                 "biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn2"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _venn3_impl(args, verbose=False, quiet=False):
    """venn3: venn3 --List1 <A> --List2 <B> --List3 <C> --label1..3 <labels> --graph <out> --prefix <out>"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx2g", "-cp", JAR,
                 "biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn3"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _venn4_impl(args, verbose=False, quiet=False):
    """venn4: venn4 --List1 <A> --List2 <B> --List3 <C> --List4 <D> --label1..4 <labels> --graph <out> --prefix <out>"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx2g", "-cp", JAR,
                 "biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn4Ellipse"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _venn5_impl(args, verbose=False, quiet=False):
    """venn5: venn5 <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> [labels]"""
    ensure_bridge("Venn5Cli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "Venn5Cli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _venn6_impl(args, verbose=False, quiet=False):
    """venn6: venn6 <out> <setA..F.txt> [labels]"""
    ensure_bridge("Venn6Cli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "Venn6Cli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _violin_impl(args, verbose=False, quiet=False):
    """violin: violin <in.tsv> <out> [width] [height]"""
    ensure_bridge("ViolinCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "ViolinCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _virusRecomb_impl(args, verbose=False, quiet=False):
    """virusRecomb: virusRecomb <inDB.fa> <inContig.fa> <outDir>   # 病毒重组分析（第77引"""
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", JAR, "biocjava.bioDoer.VirusDetect.RecombinationAnalysis"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

def _visualizeblock_impl(args, verbose=False, quiet=False):
    """visualizeblock: visualizeblock <inBlockOut> <out.pdf> [--labels "Genome1,Gen"""
    ensure_bridge("VisualizeCli")
    java_args = ["xvfb-run", "-a", "java", "-Xmx3g", "-cp", f"{BUILD_DIR}:{JAR}", "VisualizeCli"] + args
    return run_plot(java_args, verbose=verbose, quiet=quiet)

# 共生成 127 个命令实现