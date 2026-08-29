#!/bin/bash
# tbplot — TBtools 绘图 CLI 统一入口（xvfb 免 GUI）
# 用法: tbplot.sh <plotName> [args...]
# 加载统一配置（JAR 路径 / 桥目录 / 构建目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
# shellcheck disable=SC1091
source "$ROOT/config/config.sh"
JAR="${TBTOOLS_JAR}"
# 桥源码目录（bridges/），javac 编译到 build/，java -cp 用 build/
TBCLI_DIR="$ROOT/build"
# 确保桥源码副本在 build/（含编译产物，防源目录污染）
mkdir -p "$TBCLI_DIR"
# 同步桥源码：bridges/ 比 build/ 新或缺失则复制（增量同步，新增桥立即生效）
for _src in "$ROOT"/bridges/*.java; do
    [ -f "$_src" ] || continue
    _name="$(basename "$_src")"
    if [ ! -f "$TBCLI_DIR/$_name" ] || [ "$_src" -nt "$TBCLI_DIR/$_name" ]; then
        cp -f "$_src" "$TBCLI_DIR/"
    fi
done
# jar 检查
tbtools_check_jar || exit 1

case "$1" in
  motif)
    # 用法: motif <meme.xml> <idList.txt> <outFile> [width] [height]
    shift
    javac -cp "$JAR" "$TBCLI_DIR/MotifCli.java" 2>/dev/null
    xvfb-run -a java -Xmx4g -cp "$TBCLI_DIR:$JAR" MotifCli "$@"
    ;;
  genelocation)
    # 用法: genelocation --ChrLen <chrlen> --FeaturePos <pos> --OutGraph <out> [--FeatureColor <map>]
    shift
    xvfb-run -a java -Xmx3g -cp "$JAR" biocjava.bioDoer.JIGplotToolkit.GeneLocation.GeneLocation "$@"
    ;;
  dotplot)
    # 用法: dotplot --inGff <gff> --genePair <pairs> --chrLayout <layout> --outGraph <out>
    #   简化GFF: Chr\tGene\tStart\tEnd\tStrand ; chrLayout: Genome: Chr1 Chr2...
    shift
    xvfb-run -a java -Xmx3g -cp "$JAR" biocjava.bioDoer.JIGplotToolkit.DotPlot.dotdotdot "$@"
    ;;
  circos)
    # 用法: circos <chrLen.txt> <link.txt> <genePos.txt> <outFile> [w] [h]
    #   link.txt/genePos.txt 可空文件
    shift
    javac -cp "$JAR" "$TBCLI_DIR/CircosCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" CircosCli "$@"
    ;;
  pca)
    # 用法: pca <expr.matrix.tsv> <out> [row|col] [scale] [w] [h]
    #   通用反射桥 GenericCli 驱动 PCAanalysis（doPCA+postGraph）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh pca <expr.tsv> <out> [row|col] [scale] [w] [h]"; exit 1; fi
    EXPR="$1"; OUT="$2"; shift 2
    DIRECT="Rows"; SCALE="true"; W="1000"; H="800"
    [ $# -ge 1 ] && [ "$1" = "col" ] && DIRECT="Columns" && shift
    [ $# -ge 1 ] && [ "$1" = "row" ] && DIRECT="Rows" && shift
    [ $# -ge 1 ] && SCALE="$1" && shift
    [ $# -ge 1 ] && W="$1" && shift
    [ $# -ge 1 ] && H="$1" && shift
    javac -cp "$JAR" "$TBCLI_DIR/GenericCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" GenericCli biocjava.bioDoer.JIGplotToolkit.PCAanalysis.PCAanalysis doPCA+postGraph "$OUT" --set inTabFile "$EXPR" --set rowName true --set colName true --set processDirect "$DIRECT" --set scale "$SCALE" --set pointSize 8.0 --set showLabel true --width "$W" --height "$H"
    ;;
  generic)
    # 用法: generic <engineClass> <method[+method2]> <out> [--set field value ...] [--width N] [--height N]
    #   通用反射桥：驱动任意 TBtools 引擎（setter + plot/process/postGraph + save2Graph）
    #   例: generic biocjava.bioDoer.JIGplotToolkit.PCAanalysis.PCAanalysis doPCA+postGraph out.svg --set inTabFile expr.tsv --set rowName true --set colName true --set processDirect Rows
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh generic <engineClass> <method> <out> [--set field value ...]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/GenericCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" GenericCli "$@"
    ;;
  tauIndex)
    # 用法: tauIndex <inExpTab> <outTAU>
    #   inExpTab: 表达矩阵（首列基因名 + 样本列）；outTAU: τ 指数表（0=均匀 1=完全组织特异）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh tauIndex <inExpTab> <outTAU>"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/TauCalcCli.java" 2>/dev/null
    xvfb-run -a java -Xmx1g -cp "$TBCLI_DIR:$JAR" TauCalcCli "$@"
    ;;
  exprCorr)
    # 用法: exprCorr <inFPKM> <outCorrMat>
    #   样本间 Pearson 相关矩阵（共表达/聚类分析输入）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh exprCorr <inFPKM> <outCorrMat>"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/ExprCorrCli.java" 2>/dev/null
    xvfb-run -a java -Xmx1g -cp "$TBCLI_DIR:$JAR" ExprCorrCli "$@"
    ;;
  qpcrExp)
    # 用法: qpcrExp <in.qpcr.tab> <out.xls>
    #   in.qpcr.tab: tab 分隔 3 列（基因名\t对照Ct\t实验Ct），同名多行取平均
    #   out.xls: 相对表达量 Mean/Stdev（2^-ΔΔCt 法）（第58引擎）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh qpcrExp <in.qpcr.tab> <out.xls>"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/QpcrDdctCli.java" 2>/dev/null
    xvfb-run -a java -Xmx1g -cp "$TBCLI_DIR:$JAR" QpcrDdctCli "$@"
    ;;
  qpcr)
    # 用法: qpcr <data.txt> <out> [w] [h]   (data: name\tmean\tsd)
    shift
    javac -cp "$JAR" "$TBCLI_DIR/QpcrCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" QpcrCli "$@"
    ;;
  hclust)
    # 用法: hclust <expr.matrix.tsv> <out.nwk> [distMethod] [clusterMethod]
    shift
    javac -cp "$JAR" "$TBCLI_DIR/HclustCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" HclustCli "$@"
    ;;
  volcano)
    # 用法: volcano <deg.txt> <outFile> [pvalCutoff] [fcCutoff] [w] [h]
    #   deg.txt: GeneID\tLog2FC\tpvalue
    #   通用反射桥 GenericCli 驱动 vocanoPlot.show()
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh volcano <deg.txt> <out> [pvalCut] [fcCut] [w] [h]"; exit 1; fi
    DEG="$1"; OUT="$2"; shift 2
    P="0.05"; FC="1.0"; W="1000"; H="800"
    [ $# -ge 1 ] && P="$1" && shift
    [ $# -ge 1 ] && FC="$1" && shift
    [ $# -ge 1 ] && W="$1" && shift
    [ $# -ge 1 ] && H="$1" && shift
    javac -cp "$JAR" "$TBCLI_DIR/GenericCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" GenericCli biocjava.bioDoer.JIGplotToolkit.VocanoPlot.vocanoPlot show "$OUT" --set inData "$DEG" --set log2FoldChange true --set negLogPvalue true --set pvalueCutOff "$P" --set foldChangeCutOff "$FC" --set normPointSize 5.0 --set showTopChangeNum 5 --width "$W" --height "$H"
    ;;
  upset)
    # 用法: upset <sets.txt> <outFile> [w] [h]
    #   sets.txt: 每行 "集合名\t成员1\t成员2..."（tab 分隔）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/UpSetCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" UpSetCli "$@"
    ;;
  msa)
    # 用法: msa <aligned.fasta> <outFile> [padding]
    #   尺寸按子面板自动计算，勿传 w/h
    shift
    javac -cp "$JAR" "$TBCLI_DIR/MSACli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" MSACli "$@"
    ;;
  genelocgff)
    # 用法: genelocgff <gff3> <idList> <out> [--chrLen len.tsv] [--rename r.tsv] [--pairs p.tsv] [--color c.tsv] [--rankedChr list] [--onlyMapped true|false] [--showLabel true|false]
    shift
    javac -cp "$JAR" "$TBCLI_DIR/GeneLocGffCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" GeneLocGffCli "$@"
    ;;
  tree)
    # 用法: tree <treeMeta.config> <out> [pad]
    #   配置格式见 TreeCli.java 注释（[TYPE]:Tree + [NEWICK] + [setting] + 可选 [TYPE]:TextAnno/HeatMap/BarPlot/... 轨道）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/TreeCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" TreeCli "$@"
    ;;
  heatmap2)
    # 用法: heatmap2 <expr.matrix.tsv> <out> [options]
    #   矩阵: 首列基因名 + 列名表头，其余数值。options 见 HeatmapCli.java 注释（--log2 --rowScale --clusterRow/Col --rowGroup/ColGroup --transpose 等）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/HeatmapCli.java" 2>/dev/null
    xvfb-run -a java -Xmx4g -cp "$TBCLI_DIR:$JAR" HeatmapCli "$@"
    ;;
  supercircos)
    # 用法: supercircos <config.cfg> <out> [width] [height]
    #   配置格式见 SuperCircosCli.java 注释（[chrLen] [link] [gene] [track] 等行导向配置）
    #   track: [track] <Tile|Triangle|HeatMap|Point|Line|Bar|Arrow> <file> <startPos> <endPos> <c1> <c2> <c3> <binSize> [fillColor] [drawColor]
    shift
    javac -cp "$JAR" "$TBCLI_DIR/SuperCircosCli.java" 2>/dev/null
    xvfb-run -a java -Xmx4g -cp "$TBCLI_DIR:$JAR" SuperCircosCli "$@"
    ;;
  barplot)
    # 用法: barplot <enrichment.tsv> <out> <termCol> <pvalCol> [classCol] [maxTerms] [xlab] [ylab] [mode]
    #   mode: Normal|TextOnLeft|BarOnLeft
    shift
    javac -cp "$JAR" "$TBCLI_DIR/BarplotCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" BarplotCli "$@"
    ;;
  pafviz)
    # 用法: pafviz <in.paf> <out> [graphSize] [colorMode] [switchQT] [minAlnLen] [rcColor]
    #   colorMode: Target|Query|None
    shift
    javac -cp "$JAR" "$TBCLI_DIR/PafVizCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" PafVizCli "$@"
    ;;
  admixture)
    # 用法: admixture <qFiles.lst> <out> [sampleIDFile] [groupFile] [sortMode] [width] [height] [panelInterval]
    #   sortMode: Qraito|Lexical|None
    shift
    javac -cp "$JAR" "$TBCLI_DIR/AdmixtureCli.java" 2>/dev/null
    xvfb-run -a java -Xmx1g -cp "$TBCLI_DIR:$JAR" AdmixtureCli "$@"
    ;;
  groupedbar)
    # 用法: groupedbar <data.tsv> <out> [plotType] [errorBarType] [hasHeader] [title] [--options]
    #   plotType: BAR_ERROR|BOXPLOT|VIOLIN|SWARM
    #   errorBarType: SEM|SD|CI95
    #   data.tsv: Group\tValue (每组至少 2 重复)
    #   --options: --width --height --fontSize --barWidth --boxWidth --violinWidth --showOutliers --noOutliers --noNs --homoscedastic --yMin --yMax --pStar --pStar2 --pStar3 --color <i> <r,g,b> --order ALPHA
    shift
    javac -cp "$JAR" "$TBCLI_DIR/GroupedBarCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" GroupedBarCli "$@"
    ;;
  layoutheatmap)
    # 用法: layoutheatmap <layout.tsv> <expr.tsv> <out> [--options]
    #   layout.tsv: 样本名矩阵（TSV，空格用 NA）
    #   --options: --cellWidth --cellHeight --yGap --log2 --log10 --rowScale --minColor --midColor --maxColor --nanColor --noLegend --noValue --rename --topLeft
    shift
    javac -cp "$JAR" "$TBCLI_DIR/LayoutHeatmapCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" LayoutHeatmapCli "$@"
    ;;
  cubeheatmap)
    # 用法: cubeheatmap <expr.tsv> <group.tsv> <out> [--log10 --minColor r,g,b --midColor r,g,b --maxColor r,g,b]
    #   expr.tsv: 表达矩阵（首列基因名 + 样本名表头）
    #   group.tsv: Sample\tFirstDim\tSecondDim（三面立方体热图）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/CubeHeatmapCli.java" 2>/dev/null
    xvfb-run -a java -Xmx4g -cp "$TBCLI_DIR:$JAR" CubeHeatmapCli "$@"
    ;;
  circlegene)
    # 用法: circlegene <gff> <geneID.txt> <out> [--rename f --link f --rankedChr f --allChr --graphSize N --startAngle N --endAngle N --chrFill r,g,b --chrLabelColor r,g,b]
    #   geneID.txt: mRNA ID 每行一个（可第二列 1/0 控制颜色）
    #   --link: 基因对文件 (GeneA\tGeneB\t[r,g,b]) 绘制共线性链接
    shift
    javac -cp "$JAR" "$TBCLI_DIR/CircleGeneViewerCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" CircleGeneViewerCli "$@"
    ;;
  genestructure)
    # 用法: genestructure <input.gff> <idList.txt> <outFile> [genome.fa] [width] [height]
    shift
    javac -cp "$JAR" "$TBCLI_DIR/GeneStructureCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" GeneStructureCli "$@"
    ;;
  seqlogo)
    # 用法: seqlogo <seq.fa|seq.txt> <out.svg/png> [--scaleIC true|false] [--showPos] [--startPos N] [--borderColor R,G,B] [--borderSize N] [--onlyBorder] [--xInterval N] [--yInterval N]
    #   seq 输入: FASTA 或 纯文本（每行一条序列，等长已比对）
    #   引擎: biocjava.bioDoer.seqLogo.makeSeqLogo（自带 ArgsParser，开箱即用）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh seqlogo <seq.fa> <out> [--scaleIC true --showPos ...]"; exit 1; fi
    INFILE="$1"; OUTFILE="$2"; shift 2
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.seqLogo.makeSeqLogo --inFile "$INFILE" --OutGraph "$OUTFILE" "$@"
    ;;
  peaktss)
    # 用法: peaktss <gxf> <macs2_peak.xls> <out.svg/png> [--dist N] [--bin N] [--color]
    #   gxf: 基因注释（GFF/GXF，mRNA 行定义 TSS）
    #   macs2_peak.xls: MACS2 peaks 表格（chr/start/end 列）
    #   --dist: TSS 上下游窗口 bp（默认 2000）
    #   引擎: biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakTssHeatMap（自带 CLI，开箱即用）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh peaktss <gxf> <macs2_peak.xls> <out> [--dist N]"; exit 1; fi
    INGXF="$1"; INPEAK="$2"; OUTGRAPH="$3"; shift 3
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakTssHeatMap --inGxf "$INGXF" --inPeak "$INPEAK" --outGraph "$OUTGRAPH" "$@"
    ;;
  peakdist)
    # 用法: peakdist <chrLen.tsv> <macs2_peak.xls> <out> [--chrHeight H] [--topLenRank N] [--width W] [--height H]
    #   chrLen.tsv: Chr\tLength（染色体长度）
    #   macs2_peak.xls: MACS2 peaks 表格（chr/start/end 列）
    #   引擎: peakDistribution（process() 是 private，反射调用）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh peakdist <chrLen.tsv> <macs2_peak.xls> <out> [--width W --height H]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/PeakDistCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" PeakDistCli "$@"
    ;;
  peakanno)
    # 用法: peakanno <gxf> <macs2_peak.xls> <out.tsv> [--dist N]
    #   macs2_peak.xls: MACS2 标准 peak 格式（chr start end length abs_summit ...）
    #   引擎: peakAnno（自带 ArgsParser，开箱即用；peak 坐标列必须标准 MACS2 格式）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh peakanno <gxf> <macs2_peak.xls> <out.tsv> [--dist N]"; exit 1; fi
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakAnno --inGXF "$1" --peakInfo "$2" --outTab "$3" "${@:4}"
    ;;
  microgenome)
    # 用法: microgenome <inGBK> <anno.tsv> <out> [micro|macro]
    #   inGBK: GenBank 质体/质粒基因组文件
    #   anno.tsv: 注释 5 列（startPos\tendPos\tname\t[+|-]\ttype）
    #     ⚠️ type 至少 2 种不同类型（CDS/RNA/tRNA）——单类型触发引擎 ColorMapper middleColor null NPE
    #   引擎: MicroGenomeAnnotationCircosPlot（自带 ArgsParser，质体基因组环形图+GC轨道）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh microgenome <inGBK> <anno.tsv> <out> [micro|macro]"; exit 1; fi
    INGBK="$1"; INANNO="$2"; OUTGRAPH="$3"; GTYPE="micro"
    [ $# -ge 4 ] && GTYPE="$4"
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.JIGplotToolkit.MicroGenomeViz.MicroGenomeAnnotationCircosPlot --inGBK "$INGBK" --inAnno "$INANNO" --graphType "$GTYPE" --outGraph "$OUTGRAPH"
    ;;
  gel)
    # 用法: gel <FragmentRangeArr> <LaneLabels> <MarkerRange> <out>
    #   FragmentRangeArr: 分号分隔泳道/逗号分隔片段，如 "798;1233,228;1688,1598"
    #   LaneLabels: 泳道标签，如 "DL2000,Cultivar_1,Cultivar_2,Cultivar_3"
    #   MarkerRange: marker 范围，如 "2000,1500,1000,750,500,250,100"
    #   引擎: GelImage.Marker（自带 ArgsParser，PCR 产物虚拟凝胶电泳图）
    shift
    if [ $# -lt 4 ]; then echo "用法: tbplot.sh gel <FragmentRangeArr> <LaneLabels> <MarkerRange> <out>"; exit 1; fi
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.JIGplotToolkit.GelImage.Marker --FragmentRangeArr "$1" --LaneLabels "$2" --MarkerRange "$3" --outGraph "$4"
    ;;
  gfa)
    # 用法: gfa <in.gfa> <out> [width] [height]
    #   GFA 格式: S 行=节点（S\tname\tseq），L 行=边（L\tfrom\tstrand\tto\tstrand\toverlap）
    #   引擎: VizGFA（GFAGraphLayout + VizGFA.visualize，组装图可视化）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh gfa <in.gfa> <out> [w] [h]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/VizGFACli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" VizGFACli "$@"
    ;;
  pafcomp)
    # 用法: pafcomp --inPaf <paf> --outGraph <out> [--colorMode Target|Query|None] [--size N] [--minLen N]
    #   PAF 基因组比较图（⚠️ 入口是 main1 非 main）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/PafGC.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" PafGC "$@"
    ;;
  pafref)
    # 用法: pafref --inPaf <paf> --outTab <out.tsv>
    #   PAF 参考碱基覆盖计算（minimap2 -c --cs 输出）
    shift
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.JIGplotToolkit.Paf.PafRefBaseCoverCalc "$@"
    ;;
  colorscheme)
    # 用法: colorscheme <inTab> <outTab> <refColIndex>
    #   inTab: tab 分隔表；refColIndex: 从 0 开始，取该列做配色 key（去重）
    #   outTab: 输出颜色代码表（第41引擎）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh colorscheme <inTab> <outTab> <refColIndex>"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/ColorSchemeCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" ColorSchemeCli "$@"
    ;;
  distance)
    # 用法: distance <in.tsv> <col1> <col2> <euclidean|pearson|pearsonDist>
    #   in.tsv: tab 分隔表；col1/col2: 列索引（从0开始）；输出两列数值的距离/相关系数（第42引擎）
    shift
    if [ $# -lt 4 ]; then echo "用法: tbplot.sh distance <in.tsv> <col1> <col2> <method>"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/DistanceCli.java" 2>/dev/null
    xvfb-run -a java -Xmx1g -cp "$TBCLI_DIR:$JAR" DistanceCli "$@"
    ;;
  mountain)
    # 用法: mountain <fold.txt> <out.tsv>
    #   fold.txt: RNA 二级结构折叠字符串（() 和 .）；输出每碱基山峰高度（第43引擎）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh mountain <fold.txt> <out.tsv>"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/MountainPlotCli.java" 2>/dev/null
    xvfb-run -a java -Xmx1g -cp "$TBCLI_DIR:$JAR" MountainPlotCli "$@"
    ;;
  pileup)
    # 用法: pileup <blast.xml> <out.svg> [--query NAME]
    #   blast.xml: BLAST+ XML 输出（-outfmt 5）；画 query 的 hits pile-up 图（第44引擎）
    #   ⚠️ 绕过了引擎 GUI 弹窗，自动选第一个 query
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh pileup <blast.xml> <out.svg> [--query NAME]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/PileUpCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" PileUpCli "$@"
    ;;
  plotrna)
    # 用法: plotrna <genomeFA> <region> <SAM> [--directPDF out.pdf]
    #   region: 'chr:startPos-endPos'；SAM: 比对 reads；画基因组区域覆盖度+RNA结构图（第45引擎）
    #   ⚠️ 只支持 PDF 输出（--directPDF）；不带该参数会弹窗
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh plotrna <genomeFA> <region> <SAM> [--directPDF out.pdf]"; exit 1; fi
    GENOME="$1"; REGION="$2"; SAMFILE="$3"; shift 3
    [ $# -eq 0 ] && { echo "⚠️ 必须带 --directPDF <out.pdf>（否则引擎弹窗）"; exit 1; }
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.JIGplotToolkit.miRCoverage.PlotRNAfold --genomeFA "$GENOME" --region "$REGION" --SAM "$SAMFILE" "$@"
    ;;
  bamstate)
    # 用法: bamstate <out.tsv> <gff3> <bam1> [<bam2> ...]
    #   gff3: 标准 GFF3（gene/mRNA 特征）；bam: 比对 BAM（需 samtools 建索引）
    #   out.tsv: 每 BAM 的 coverage 比例/depth/总基因数/表达基因数（第57引擎）
    #   示例: tbplot.sh bamstate out.tsv Co.gff3 SRR1.bam SRR2.bam
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh bamstate <out.tsv> <gff3> <bam1> [bam2 ...]"; exit 1; fi
    OUTB="$1"; GFFB="$2"; shift 2
    javac -cp "$JAR" "$TBCLI_DIR/BamStateCli.java" 2>/dev/null
    xvfb-run -a java -Xmx4g -cp "$TBCLI_DIR:$JAR" BamStateCli "$GFFB" "$OUTB" "$@"
    ;;
  preparespecies)
    # 用法: preparespecies <prefix> <inGenome.fa> <inGFF> <outGenome.fa> <outGFF>
    #   给基因组+GFF 加物种前缀（seqid + ID）——TBtools 多物种比较数据准备（第56引擎）
    #   工作流: preparespecies → findblockdual/multiple → visualizeblock
    #   ⚠️ 大数据基因组全量重写耗时（3GB 级约 10-20 分钟）
    shift
    if [ $# -lt 5 ]; then echo "用法: tbplot.sh preparespecies <prefix> <inGenome.fa> <inGFF> <outGenome.fa> <outGFF>"; exit 1; fi
    xvfb-run -a java -Xmx3g -cp "$JAR" biocjava.bioDoer.ComparativeGenomics.PrepareSpecies --prefix "$1" --inGenomeFa "$2" --inGXF "$3" --outGenomeFa "$4" --outGXF "$5"
    ;;
  partitionconflict)
    # 用法: partitionconflict <inConflictFreq.tsv> <polyPoid> <outCluster>
    #   inConflictFreq.tsv: conflictpaf 输出（contigA\tcontigB\tcount）
    #   polyPoid: 目标倍性；outCluster: 同源群分区（第54引擎）
    #   链式: conflictpaf → partitionconflict（冲突检测 → 多倍体同源群分区）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh partitionconflict <inConflict.tsv> <polyPoid> <outCluster>"; exit 1; fi
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.GenomeAssembly.ParititionByConflictFreq --inConflictFreq "$1" --polyPoid "$2" --outCluster "$3"
    ;;
  mirnatarget)
    # 用法: mirnatarget <mirna.fa> <target.fa> <out.tsv> [--evalue X] [--threads N] [--scoreCutOff N] [--maxMismatch N]
    #   mirna.fa: miRNA 序列（建议每轮一条或一族）；target.fa: 转录本/基因组靶标
    #   out.tsv: 靶标表（miRNA target strand beg end score miRNAseq targetseq E bits）
    #   完整管线: ssearch36 -i -m 10 → TargetSoEngine（TBtools 官方参数）
    #   ⚠️ 需 ssearch36 在 PATH（apt install fasta 或本地编译）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh mirnatarget <mirna.fa> <target.fa> <out.tsv> [--evalue X] [--threads N]"; exit 1; fi
    MIR="$1"; TGT="$2"; OUT="$3"; shift 3
    EVAL="1"; THREADS="1"; SCORE="5.0"; MISMATCH="6"
    while [ $# -ge 2 ]; do
      case "$1" in
        --evalue) EVAL="$2";;
        --threads) THREADS="$2";;
        --scoreCutOff) SCORE="$2";;
        --maxMismatch) MISMATCH="$2";;
        *) echo "未知选项: $1"; exit 1;;
      esac
      shift 2
    done
    # Step 1: ssearch36 官方参数
    M10="${OUT}.m10.tmp"
    ssearch36 -w 100 -W 25 -E "$EVAL" -m 10 -T "$THREADS" -i -U "$MIR" "$TGT" > "$M10" 2>/dev/null || { echo "❌ ssearch36 失败（确认已安装）"; exit 1; }
    # Step 2: TargetSoEngine 打分
    javac -cp "$JAR" "$TBCLI_DIR/TargetScoreCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" TargetScoreCli "$M10" "$OUT" --scoreCutOff "$SCORE" --maxMismatch "$MISMATCH" 2>/dev/null
    rm -f "$M10"
    echo "[tbplot] miRNA 靶标预测完成: $OUT"
    ;;
  conflictpaf)
    # 用法: conflictpaf <in.paf> <out.tsv> [binSize]
    #   in.paf: 基因组比对 PAF（minimap2/minigraph）
    #   out.tsv: contig 对冲突计数（query target bin冲突数）——组装冲突检测（第53引擎）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh conflictpaf <in.paf> <out.tsv> [binSize]"; exit 1; fi
    INPAF="$1"; OUTC="$2"; BIN="10000"; shift 2
    [ $# -ge 1 ] && BIN="$1"
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.GenomeAssembly.CalculateConflictByRefAlignPAF --inPAF "$INPAF" --outFile "$OUTC" --binSize "$BIN"
    ;;
  findblockmultiple)
    # 用法: findblockmultiple <queryGenome.fa> <query.gff> <queryId> <out.txt> <sub1Genome.fa> <sub1.gff> [<sub2Genome.fa> <sub2.gff> ...] [--leftEdge N --rightEdge N --expand N --threads N]
    #   多基因组伪共线性区块（第52引擎）：1 query + N subject
    #   ⚠️ 大数据引擎：必须 -Djava.io.tmpdir=<磁盘>（/tmp tmpfs 16G 会被 3GB 基因组撑爆）
    shift
    if [ $# -lt 7 ]; then echo "用法: tbplot.sh findblockmultiple <qGenome.fa> <q.gff> <qId> <out> <s1Genome.fa> <s1.gff> [更多subject对] [options]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/FindBlockMultipleCli.java" 2>/dev/null
    xvfb-run -a java -Djava.io.tmpdir="${TMPDIR_DISK:-/home/elysia/tmp_tb}" -Xmx6g -cp "$TBCLI_DIR:$JAR" FindBlockMultipleCli "$@"
    ;;
  findblockdual)
    # 用法: findblockdual <queryGenome.fa> <query.gff> <subjectGenome.fa> <subject.gff> <queryId> <out.txt> [--leftEdge N --rightEdge N --expand N --threads N --evalue X --minIdentity X --bestHit N]
    #   ⚠️ 内部 blastp 找同源，需真实双基因组数据验证（第50引擎）
    shift
    if [ $# -lt 6 ]; then echo "用法: tbplot.sh findblockdual <queryGenome.fa> <query.gff> <subjectGenome.fa> <subject.gff> <queryId> <out.txt> [options]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/FindBlockDualCli.java" 2>/dev/null
    xvfb-run -a java -Djava.io.tmpdir="${TMPDIR_DISK:-/home/elysia/tmp_tb}" -Xmx3g -cp "$TBCLI_DIR:$JAR" FindBlockDualCli "$@"
    ;;
  visualizeblock)
    # 用法: visualizeblock <inBlockOut> <out.pdf> [--labels "Genome1,Genome2"]
    #   inBlockOut: FindBlockDual 输出（findblockdual 命令产物）
    #   out.pdf: 输出 PDF（引擎只支持 PDF）
    #   --labels: 每行基因组标签（默认 Genome1/Genome2/...）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh visualizeblock <inBlockOut> <out.pdf> [--labels \"G1,G2\"]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/VisualizeCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" VisualizeCli "$@"
    ;;
  treeRooting)
    # 用法: treeRooting <in.nwk> <out.nwk>
    #   in.nwk: 未定根 NEWICK 树（单树）
    #   out.nwk: MAD 定根后的 NEWICK 树（Tria et al. 2017, MAD rooting）
    #   ⚠️ MAD.main() 硬编码输入路径，改调公开静态入口 quickMadRoot()
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh treeRooting <in.nwk> <out.nwk>"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/TreeRootingCli.java" 2>/dev/null
    xvfb-run -a java -Xmx1g -cp "$TBCLI_DIR:$JAR" TreeRootingCli "$@"
    ;;
  marker)
    # 用法: marker <MarkerDist|MarkerFilter|SampleDist|BigMarkerRandomDesign> <inMarker> <out> [args...]
    #   inMarker: 标记 0-1 矩阵（行=locus，列=样本，tab 分隔，首行列名/首列 locus 名）
    #   MarkerDist   : 找最大判别力 marker 组合 [--maxPoint N]
    #   MarkerFilter : 每样本 marker 计数（结果写 out）
    #   SampleDist   : marker 间成对距离（结果写 out）
    #   BigMarkerRandomDesign: 随机抽样找标记组合（无 out，直接打印到 stdout）
    #     [--targetMarkerNum N --numberOfTest N --batchSize N --numberOfThreads N]
    shift
    ENG="$1"; INM="$2"; shift 2
    if [ "$ENG" = "BigMarkerRandomDesign" ]; then
        [ -z "$INM" ] && { echo "用法: tbplot.sh marker BigMarkerRandomDesign <inMarker> [--targetMarkerNum N ...]"; exit 1; }
        xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.markerDesign.BigMarkerRandomDesign --inMakerStatus "$INM" "$@"
    else
        if [ $# -lt 1 ]; then echo "用法: tbplot.sh marker <MarkerDist|MarkerFilter|SampleDist> <inMarker> <out> [args...]"; exit 1; fi
        OUTM="$1"; shift
        javac -cp "$JAR" "$TBCLI_DIR/MarkerDesignCli.java" 2>/dev/null
        xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" MarkerDesignCli "$ENG" "$INM" "$OUTM" "$@"
    fi
    ;;
  dehist)
    # 用法: dehist <deg.txt> <out> [width] [height]
    #   deg.txt: 每行至少 3 列（tab）：任意ID\t值1\t值2（值1/值2 两样本数值，比较大小分左右直方图）
    #   # 开头行跳过
    #   引擎: DiffExpDualHistPlot.process(File) 返回 JIGSubPanel[]（差异表达双直方图）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh dehist <deg.txt> <out> [w] [h]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/DiffExpCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" DiffExpCli "$@"
    ;;
  msy)
    # 用法: msy <simplifiedGff.pos> <links.txt> <chrLayout.txt> <out> [width] [height]
    #   simplifiedGff.pos: Chr\tGeneName\tStart\tEnd\t[displayChr]\t[displayName]（多物种共线性区域/基因）
    #   links.txt: GeneA\tGeneB\t[r,g,b]（跨物种同源基因对）
    #   chrLayout.txt: 基因组名:\s*染色体列表（如 GenomeA: A_Chr1 A_Chr2）；#DISPLAY_ORIG_CHR: 前缀行定义显示名
    #   引擎: MultipleSpeciesSyteny.plot() 返回 JIGSubPanel（多物种微共线性图）
    shift
    if [ $# -lt 4 ]; then echo "用法: tbplot.sh msy <simplifiedGff.pos> <links.txt> <chrLayout.txt> <out> [w] [h]"; exit 1; fi
    POS="$1"; LINKS="$2"; LAYOUT="$3"; OUT="$4"; shift 4
    W="1000"; H="800"; [ $# -ge 1 ] && W="$1" && shift; [ $# -ge 1 ] && H="$1" && shift
    javac -cp "$JAR" "$TBCLI_DIR/GenericCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" GenericCli biocjava.bioDoer.JIGplotToolkit.Synteny.MultipleSpeciesSyteny plot "$OUT" --set inSimplifiedGff "$POS" --set genePairInfoFile "$LINKS" --set chrLayoutFile "$LAYOUT" --width "$W" --height "$H"
    ;;
  venn5)
    # 用法: venn5 <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> [labelA-E]
    #   每个 setN.txt: 每行一个成员 ID
    #   引擎: Venn5（setInArrA~E + setOutGraph + getVennGraph）
    shift
    if [ $# -lt 6 ]; then echo "用法: tbplot.sh venn5 <out> <setA> <setB> <setC> <setD> <setE> [labels]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/Venn5Cli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" Venn5Cli "$@"
    ;;
  venn6)
    # 用法: venn6 <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> <setF.txt> [labelA-F]
    #   引擎: Venn6（setInArrA~F + setOutGraph + getVennGraph）
    shift
    if [ $# -lt 7 ]; then echo "用法: tbplot.sh venn6 <out> <setA> <setB> <setC> <setD> <setE> <setF> [labels]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/Venn6Cli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" Venn6Cli "$@"
    ;;
  microsyn)
    # 用法: microsyn <gxf1> <gxf2> <collinearity> <out> [--chr1 C --start1 S --end1 E] [--chr2 C --start2 S --end2 E] [--highlight1 c:s:e] [--highlight2 c:s:e]
    #   gxf1/gxf2: 两物种 GFF/GXF 注释
    #   collinearity: MCScanX 输出（*.collinearity）
    #   引擎: MicroSyntenicAdvance（窗口遍历方案）双基因组微共线性图
    shift
    if [ $# -lt 4 ]; then echo "用法: tbplot.sh microsyn <gxf1> <gxf2> <collinearity> <out> [--chr1 .. --start1 ..]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/MicroSynCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" MicroSynCli "$@"
    ;;
  multisyn)
    # 用法: multisyn <gxf.lst> <collinear.lst> <out> [--genes idlist.txt]
    #   gxf.lst: 每行一个 GXF/GFF 注释（染色体名须数字）
    #   collinear.lst: 每行一个 MCScanX collinearity（与 GXF 配对）
    #   --genes: 高亮基因 ID 列表（可选，缺省自动从第一个 GXF 提取）
    #   引擎: SeveralSpeciesMicroSyntenicAnalysisAdvance（多物种微共线性，需真实数据验证输出）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh multisyn <gxf.lst> <collinear.lst> <out> [--genes f]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/SeveralSpeciesCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" SeveralSpeciesCli "$@"
    ;;
  *)
    echo "用法:"
    echo "  tbplot.sh genestructure <gff> <ids(mRNA)> <out> [genome.fa] [w] [h]  # 基因结构图"
    echo "  tbplot.sh motif <meme.xml> <ids> <out> [w] [h]                       # Motif分布图"
    echo "  tbplot.sh volcano <deg.txt> <out> [pvalCut] [fcCut] [w] [h]         # 火山图"
    echo "  tbplot.sh genelocation --ChrLen <len> --FeaturePos <pos> --OutGraph <out>  # 基因定位图(自带CLI)"
    echo "  tbplot.sh circos <chrLen> <links> <genePos> <out> [w] [h]                  # Circos共线性环形图"
    echo "  tbplot.sh dotplot --inGff --genePair --chrLayout --outGraph               # 共线性点图(自带CLI)"
  echo "  tbplot.sh upset <sets.txt> <out> [w] [h]                                 # UpSet交集图"
  echo "  tbplot.sh msa <aligned.fasta> <out> [padding]                            # MSA序列比对图"
  echo "  tbplot.sh genelocgff <gff3> <ids> <out> [--chrLen l] [--pairs p] [--color c]  # 基因定位图(GFF+ID输入)"
  echo "  tbplot.sh tree <treeMeta.cfg> <out> [pad]                                    # 树+注释图(TextAnno/HeatMap等9类轨道)"
  echo "  tbplot.sh heatmap2 <expr.matrix> <out> [--log2 --rowScale --clusterRow --colGroup...]  # 热图(引擎级)"
  echo "  tbplot.sh supercircos <config.cfg> <out> [w] [h]                              # SuperCircos多轨道环形图(HeatMap/Bar/Line/Tile等7类轨道)"
  echo "  tbplot.sh barplot <enrichment.tsv> <out> <termCol> <pvalCol> [classCol] [maxTerms] [xlab] [ylab] [mode]  # 富集柱状图(-log10 P-value)"
  echo "  tbplot.sh pafviz <in.paf> <out> [graphSize] [colorMode] [switchQT] [minAlnLen] [rcColor]  # PAF比对Dot-plot"
  echo "  tbplot.sh admixture <qFiles.lst> <out> [sampleIDFile] [groupFile] [sortMode] [w] [h] [interval]  # ADMIXTURE Q矩阵图"
  echo "  tbplot.sh groupedbar <data.tsv> <out> [BAR_ERROR|BOXPLOT|VIOLIN|SWARM] [SEM|SD|CI95] [hasHeader] [title] [--options]  # 分组柱图+显著性"
  echo "  tbplot.sh layoutheatmap <layout.tsv> <expr.tsv> <out> [--log2 --rowScale --minColor --midColor --maxColor ...]  # 布局热图"
  echo "  tbplot.sh cubeheatmap <expr.tsv> <group.tsv> <out> [--log10 --minColor r,g,b ...]  # 3D立方体热图"
  echo "  tbplot.sh circlegene <gff> <geneID.txt> <out> [--link f --rankedChr f --graphSize N ...]  # 环形基因位置图"
  echo "  tbplot.sh seqlogo <seq.fa> <out> [--scaleIC true --showPos --startPos N...]  # 序列LOGO图(开箱即用)"
  echo "  tbplot.sh peaktss <gxf> <macs2_peak.xls> <out> [--dist N]                     # Peak-TSS热图(ChIP-seq,开箱即用)"
  echo "  tbplot.sh peakdist <chrLen.tsv> <macs2_peak.xls> <out> [--width W --height H] # Peak染色体分布图(ChIP-seq)"
  echo "  tbplot.sh dehist <deg.txt> <out> [w] [h]                                     # 差异表达双直方图"
  echo "  tbplot.sh marker <MarkerDist|MarkerFilter|SampleDist|BigMarkerRandomDesign> <inMarker> <out> [args]  # 标记设计(0-1矩阵)"
  echo "  tbplot.sh treeRooting <in.nwk> <out.nwk>                                  # MAD系统发育定根"
  echo "  tbplot.sh findblockdual <qGenome.fa> <q.gff> <sGenome.fa> <s.gff> <qId> <out> [opts]  # 伪共线性区块(需真实数据)"
  echo "  tbplot.sh visualizeblock <inBlockOut> <out.pdf> [--labels \"G1,G2\"]               # 区块可视化PDF"
  echo "  tbplot.sh findblockmultiple <qGenome.fa> <q.gff> <qId> <out> <s1Genome.fa> <s1.gff> [more pairs]  # 多基因组伪共线性区块"
  echo "  tbplot.sh conflictpaf <in.paf> <out.tsv> [binSize]                           # PAF冲突检测(组装冲突)"
  echo "  tbplot.sh partitionconflict <inConflict.tsv> <polyPoid> <outCluster>           # 冲突分区(多倍体同源群)"
  echo "  tbplot.sh mirnatarget <mirna.fa> <target.fa> <out.tsv>                         # miRNA靶标预测(ssearch36→TargetSo)"
  echo "  tbplot.sh preparespecies <prefix> <inGenome.fa> <inGFF> <outGenome.fa> <outGFF> # 多物种数据准备(ID加前缀)"
  echo "  tbplot.sh bamstate <out.tsv> <gff3> <bam1> [bam2...]                         # BAM覆盖状态评估"
  echo "  tbplot.sh qpcrExp <in.qpcr.tab> <out.xls>                                      # qPCR相对定量(ΔΔCt)"
  echo "  tbplot.sh tauIndex <inExpTab> <outTAU>                                          # 组织特异性τ指数"
  echo "  tbplot.sh exprCorr <inFPKM> <outCorrMat>                                        # 表达相关矩阵(Pearson)"
  echo "  tbplot.sh msy <simplifiedGff.pos> <links.txt> <chrLayout.txt> <out> [w] [h]  # 多物种微共线性图"
  echo "  tbplot.sh microsyn <gxf1> <gxf2> <collinearity> <out> [--chr1 .. --start1 ..] # 双基因组微共线性图"
  echo "  tbplot.sh venn5 <out> <5 sets> [labels]                                      # 五集合韦恩图"
  echo "  tbplot.sh venn6 <out> <6 sets> [labels]                                      # 六集合韦恩图"
  echo "  tbplot.sh generic <engineClass> <method> <out> [--set f v ...]                 # 通用反射桥(任意TBtools引擎)"
    ;;
esac
