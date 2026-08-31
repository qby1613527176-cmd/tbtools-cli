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
  batchReplace)
    # 用法: batchReplace <inFile> <outFile> <patternMap.tsv> [--partial]
    #   patternMap.tsv: 模式\t替换（tab 分隔）；默认全词匹配，--partial 则子串替换
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh batchReplace <inFile> <outFile> <patternMap.tsv> [--partial]"; exit 1; fi
    INBR="$1"; OUTBR="$2"; MAPBR="$3"; FULL="true"; shift 3
    [ "$1" = "--partial" ] && FULL="false"
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Table.BatchStringReplace --inFile "$INBR" --outFile "$OUTBR" --patternMap "$MAPBR" --fullWordMatch "$FULL"
    ;;
  levelGo)
    # 用法: levelGo <gene2Go.txt> <outTable> <oboFile> [--level N]
    #   gene2Go.txt: 第1列基因ID(逗号分隔)\t第2列GO ID(逗号分隔)；oboFile: go-basic.obo 或 goslim_plant.obo
    #   outTable: GO slim 图层级统计表（第85引擎，LevelDoer 表格模式）
    #   ⚠️ --doGraph 1（SVG 图）模式不稳定（LevelGrapher 布局 GUI 依赖），默认表格模式
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh levelGo <gene2Go.txt> <outTable> <oboFile> [--level N]"; exit 1; fi
    INLG="$1"; OUTLG="$2"; OBOFILE="$3"; LEVEL="2"; shift 3
    [ $# -ge 2 ] && [ "$1" = "--level" ] && LEVEL="$2"
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.GeneOntology.Grapher.LevelDoer --oboFile "$OBOFILE" --gene2GoFile "$INLG" --outTable "$OUTLG" --level "$LEVEL" --doGraph 0
    ;;
  goParse)
    # 用法: goParse <gene2Go.txt> <oboFile> [--level N]   # GO 词典解析（第103引擎，GOtermParser）
    #   gene2Go.txt: 第1列基因ID(逗号分隔)\t第2列GO ID(逗号分隔)；oboFile: go-basic.obo 或 goslim_plant.obo
    #   自动生成 3 个文件（当前目录）: <input>.TBtools.Parsed.Gene2Go.xls / Go2Gene.xls / Go2Gene.Level<N>.xls
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh goParse <gene2Go.txt> <oboFile> [--level N]"; exit 1; fi
    INGP="$1"; OBOGP="$2"; LEVELGP="2"; shift 2
    [ $# -ge 2 ] && [ "$1" = "--level" ] && LEVELGP="$2"
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.GeneOntology.littleTools.GOtermParser --oboFile "$OBOGP" --gene2Go "$INGP" --level "$LEVELGP"
    echo "[tbplot] GO 词典解析完成: ${INGP}.TBtools.Parsed.*"
    ;;
  tableCollapse)
    # 用法: tableCollapse <inTable> <keyColIndex> <outTable> [hasHeader true|false]
    #   按键折叠（同键行合并，值用 ; 连接）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh tableCollapse <inTable> <keyColIndex> <outTable> [hasHeader]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/TableCollapseCli.java" 2>/dev/null
    xvfb-run -a java -Xmx1g -cp "$TBCLI_DIR:$JAR" TableCollapseCli "$@"
    ;;
  tableColSelect)
    # 用法: tableColSelect <inTable> <outTable> <colName1> [colName2...] [--sep tab|comma|space] [--header true|false] [--caseSensitive true|false]
    #   按列名选择列输出（第84引擎，TableColManipulator）——注意输出不含行标识列（除非也选上）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh tableColSelect <inTable> <outTable> <colName1> [colName2...]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/TableColManipCli.java" 2>/dev/null
    xvfb-run -a java -Xmx1g -cp "$TBCLI_DIR:$JAR" TableColManipCli "$@"
    ;;
  tableAppend)
    # 用法: tableAppend <inTab1> <inTab2> <outTab> [--c1 N] [--c2 N]   # 按指定列合并两表（第87引擎）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh tableAppend <inTab1> <inTab2> <outTab> [--c1 N] [--c2 N]"; exit 1; fi
    C1="0"; C2="0"; ARGS=("$@")
    for i in $(seq 0 $((${#ARGS[@]}-1))); do
      [ "${ARGS[$i]}" = "--c1" ] && C1="${ARGS[$((i+1))]}"
      [ "${ARGS[$i]}" = "--c2" ] && C2="${ARGS[$((i+1))]}"
    done
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Table.TableAppend --inTab1 "$1" --inTab2 "$2" --inColIndex1 "$C1" --inColIndex2 "$C2" --outTab "$3"
    ;;
  tableMelt)
    # 用法: tableMelt <inTable> <outTable>   # 宽表转长表（第88引擎，TableMelt）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh tableMelt <inTable> <outTable>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Table.TableMelt --inFile "$1" --outFile "$2"
    ;;
  tableColSel)
    # 用法: tableColSel <inTable> <outTable> <idList.txt> [--mode Match|Contain] [--caseSensitive true|false] [--sortByIDList true|false]
    #   按 idList 正则选列（第89引擎，TableColSelector）；idList 每行一个模式；Match=精确,Contain=正则包含
    #   表头匹配列；--sortByIDList true 按 idList 顺序排序输出列
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh tableColSel <inTable> <outTable> <idList.txt> [--mode Match|Contain]"; exit 1; fi
    MODE="Match"; CS="true"; SORT="true"; ARGS=("$@")
    for i in $(seq 0 $((${#ARGS[@]}-1))); do
      [ "${ARGS[$i]}" = "--mode" ] && MODE="${ARGS[$((i+1))]}"
      [ "${ARGS[$i]}" = "--caseSensitive" ] && CS="${ARGS[$((i+1))]}"
      [ "${ARGS[$i]}" = "--sortByIDList" ] && SORT="${ARGS[$((i+1))]}"
    done
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Table.TableColSelector --inTable "$1" --outTable "$2" --idList "$3" --selectionMode "$MODE" --caseSensitive "$CS" --sortByIDList "$SORT"
    ;;
  tableCast)
    # 用法: tableCast <inLong.txt> <outMatrix>
    #   长表转宽矩阵（第90引擎）；输入 3 列: 行名\t列名\t值；与 tableMelt 互逆
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh tableCast <inLong.txt> <outMatrix>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Table.TableCast --inFile "$1" --outFile "$2"
    ;;
  tableUniq)
    # 用法: tableUniq <inTab> <outFile> [--colIndex N] [--showFreq true|false] [--sortByFreq true|false]
    #   按列去重（第94引擎，TableUniq）；--showFreq 输出频率
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh tableUniq <inTab> <outFile> [--colIndex N] [--showFreq]"; exit 1; fi
    COL="0"; FREQ="false"; SORTF="false"; ARGS=("$@")
    for i in $(seq 0 $((${#ARGS[@]}-1))); do
      [ "${ARGS[$i]}" = "--colIndex" ] && COL="${ARGS[$((i+1))]}"
      [ "${ARGS[$i]}" = "--showFreq" ] && FREQ="true"
      [ "${ARGS[$i]}" = "--sortByFreq" ] && SORTF="true"
    done
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Table.TableUniq --inTab "$1" --outFile "$2" --colIndex "$COL" --showFreq "$FREQ" --sortByFreq "$SORTF"
    ;;
  tableTranspose)
    # 用法: tableTranspose <inTable> <outTable>   # 表格转置（第95引擎，TableTransposer）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh tableTranspose <inTable> <outTable>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Table.TableTransposer --inTable "$1" --outTable "$2"
    ;;
  tableSplit)
    # 用法: tableSplit <inTab> <outDir> [--colIndex N] [--suffix .txt]
    #   按列值拆分为多个文件（第96引擎，TableSplitByCol）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh tableSplit <inTab> <outDir> [--colIndex N] [--suffix .txt]"; exit 1; fi
    COL="0"; SUF=".txt"; ARGS=("$@")
    for i in $(seq 0 $((${#ARGS[@]}-1))); do
      [ "${ARGS[$i]}" = "--colIndex" ] && COL="${ARGS[$((i+1))]}"
      [ "${ARGS[$i]}" = "--suffix" ] && SUF="${ARGS[$((i+1))]}"
    done
    mkdir -p "$2"
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Table.TableSplitByCol --inTab "$1" --outDir "$2" --colIndex "$COL" --suffix "$SUF"
    ;;
  tableMerge)
    # 用法: tableMerge <outTable> <inFile1> [<inFile2>...] [--keyCols 0,0...] [--appendOnly true|false] [--rmKey]
    #   多表按关键列合并（第97引擎，TableMerger）；--appendOnly 不合并纯追加；--rmKey 去掉关键列
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh tableMerge <outTable> <inFile1> [<inFile2>...] [--keyCols 0,0]"; exit 1; fi
    OUTM="$1"; shift
    FILES=""; KEYS=""; APPEND="false"; RMKEY="false"
    ARGS=("$@")
    for i in $(seq 0 $((${#ARGS[@]}-1))); do
      [ "${ARGS[$i]}" = "--keyCols" ] && KEYS="${ARGS[$((i+1))]}"
      [ "${ARGS[$i]}" = "--appendOnly" ] && APPEND="${ARGS[$((i+1))]}"
      [ "${ARGS[$i]}" = "--rmKey" ] && RMKEY="true"
    done
    # 收集 inFileArr（非 -- 开头的参数）
    for a in "$@"; do
      case "$a" in
        --*) continue;;
        *) [ -z "$FILES" ] && FILES="$a" || FILES="$FILES,$a";;
      esac
    done
    N=$(echo "$FILES" | tr ',' '\n' | wc -l)
    [ -z "$KEYS" ] && KEYS=$(yes 0 | head -n $N | tr '\n' ',' | sed 's/,$//')
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Table.TableMerger --inFileArr "$FILES" --outTable "$OUTM" --inColIndexArr "$KEYS" --appendOnly "$APPEND" --rmKeyColumns "$RMKEY"
    ;;
  fqTrim)
    # 用法: fqTrim <in.fq> <out.fq> [--b5 N] [--b3 N] [--threads N]
    #   5'/3' 端固定长度修剪（默认 5'剪6 3'剪6；--b3 0 不剪）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh fqTrim <in.fq> <out.fq> [--b5 N] [--b3 N] [--threads N]"; exit 1; fi
    INFQ="$1"; OUTFQ="$2"; B5="6"; B3="6"; TH="2"; shift 2
    while [ $# -ge 2 ]; do
      case "$1" in
        --b5) B5="$2";; --b3) B3="$2";; --threads) TH="$2";;
        *) echo "未知选项: $1"; exit 1;;
      esac
      shift 2
    done
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Fastq.FastqParallelTrimmer --inFq "$INFQ" --outFq "$OUTFQ" --NumOfThread "$TH" --NumOfBases5 "$B5" --NumOfBases3 "$B3"
    ;;
  gfa2fa)
    # 用法: gfa2fa <in.gfa> <out.fa>   # GFA 组装图 → FASTA（第91引擎，GFAtoFasta）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh gfa2fa <in.gfa> <out.fa>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Fasta.Tools.GFAtoFasta --inGFA "$1" --outFa "$2"
    ;;
  fastaSubseq)
    # 用法: fastaSubseq <in.fa> <pos.txt> <out.fa>   # 按坐标提子序列（第92引擎，ExtractFastaSubseq）
    #   pos.txt: GeneId\tChrId\tStart\tEnd（4列 BED 风格，ChrId 须匹配 fasta 头）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh fastaSubseq <in.fa> <pos.txt> <out.fa>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Fasta.ExtractFastaSubseq --inFastaFile "$1" --inIDs "$2" --outFastaFile "$3"
    ;;
  fastaExtract)
    # 用法: fastaExtract <in.fa> <idList.txt> <out.fa> [--mode Match|Contain] [--process Extract|Filter]
    #   按 ID 列表提取/过滤整条序列（第93引擎，ExtractFasta）
    #   Extract=保留列表中的；Filter=排除列表中的；Match=全等 ID，Contain=子串匹配
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh fastaExtract <in.fa> <idList.txt> <out.fa> [--mode Match|Contain] [--process Extract|Filter]"; exit 1; fi
    MODE="Match"; PROC="Extract"; ARGS=("$@")
    for i in $(seq 0 $((${#ARGS[@]}-1))); do
      [ "${ARGS[$i]}" = "--mode" ] && MODE="${ARGS[$((i+1))]}"
      [ "${ARGS[$i]}" = "--process" ] && PROC="${ARGS[$((i+1))]}"
    done
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Fasta.ExtractFasta --inFa "$1" --inIDList "$2" --outFa "$3" --matchMode "$MODE" --processMode "$PROC" --caseInSensitive false
    ;;
  fqfaConv)
    # 用法: fqfaConv <input> <output> <fq2fa|fa2fq>   # FASTQ/FASTA 互转（第98引擎，FastqAndFasta）
    #   fq2fa 去质量行；fa2fq 生成假质量（IIIIIII）——兼容其他工具的占位质量
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh fqfaConv <input> <output> <fq2fa|fa2fq>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.LinuxPipe.FastqAndFasta --input "$1" --output "$2" --mode "$3"
    ;;
  hmmExtract)
    # 用法: hmmExtract <in.hmm> <idList.txt> <out.hmm>   # 从 HMM 文件按 NAME 提取（第99引擎，hmmInfoExtracter）
    #   idList.txt 每行一个 NAME；只保留匹配的 HMM 模型
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh hmmExtract <in.hmm> <idList.txt> <out.hmm>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.LinuxPipe.hmmInfoExtracter --inHmmFile "$1" --idListFile "$2" --outHmmFile "$3"
    ;;
  mastExtract)
    # 用法: mastExtract <in.fa> <mast.xml> <out.txt>   # 从 MAST XML 提取命中序列（第102引擎，ExtractSeqFromMastXML）
    #   mast.xml: MEME 套件 MAST 输出（root→sequences→sequence(name length)→seg→hit(pos idx match rc)）
    #   out.txt: 序列名\t全序列\t命中子序列\t正/反链
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh mastExtract <in.fa> <mast.xml> <out.txt>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.MEME.ExtractSeq.ExtractSeqFromMastXML --inFastaFile "$1" --inMastXML "$2" --outTable "$3"
    ;;
  nwAlign)
    # 用法: nwAlign <inSeq1.txt> <inSeq2.txt> <out>   # Needleman-Wunsch 全局比对（EMBOSS 格式）
    #   inSeqN.txt: 每行一条序列；全对全两两比对（纯 Java，无外部依赖）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh nwAlign <inSeq1.txt> <inSeq2.txt> <out>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Aligner.NeedleMan.SimpleBatchProcess --inFile_1 "$1" --inFile_2 "$2" --outFile "$3"
    ;;
  twoSeqBlast)
    # 用法: twoSeqBlast <query.fa> <subject.fa> <out.txt> [--prog blastp|blastn|tblastn] [--thread N] [--fmt 6|XML]
    #   双序列集 BLAST 比对（第105引擎，CompareTwoSeqSet）——封装 makeblastdb+blast
    #   需要 blast+ 在 PATH（makeblastdb/blastp）；输出标准 BLAST tabular (fmt 6)
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh twoSeqBlast <query.fa> <subject.fa> <out.txt> [--prog blastp]"; exit 1; fi
    Q="$1"; S="$2"; O="$3"; PROG="blastp"; TH="2"; FMT="6"; shift 3
    while [ $# -ge 2 ]; do
      case "$1" in
        --prog) PROG="$2";;
        --thread) TH="$2";;
        --fmt) FMT="$2";;
      esac
      shift 2
    done
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.BLAST.CompareTwoSeqSet --query "$Q" --subject "$S" --specifiedBlastProg "$PROG" --outBlastResult "$O" --outFmt "$FMT" --thread "$TH"
    ;;
  recipBlast)
    # 用法: recipBlast <query.fa> <subject.fa> <outPrefix> [--queryIds idlist] [--prog blastp|blastn|tblastn] [--evalue 1e-5] [--minId 0.3] [--thread N]
    #   双向 BLAST 基因家族鉴定（第106引擎，ReciprocalBlast）——封装 makeblastdb+blast 双方向
    #   输出: <outPrefix>_<query>_and_<subject>.ID.Mapping.Result.xls（双向最佳命中表）+ 正反向 TBtools.table.xls + xml
    #   ⚠️ 坑: FASTA ID 超 50 字符会被 makeblastdb 拒绝（GRAS 59 字符 ID 需先短 ID 重写）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh recipBlast <query.fa> <subject.fa> <outPrefix> [--queryIds idlist] [--prog blastp] [--evalue 1e-5] [--minId 0.3] [--thread 2]"; exit 1; fi
    Q="$1"; S="$2"; O="$3"; PROG="blastp"; EVAL="1e-5"; MINID="0.3"; TH="2"; QID=""; shift 3
    while [ $# -ge 2 ]; do
      case "$1" in
        --queryIds) QID="$2";;
        --prog) PROG="$2";;
        --evalue) EVAL="$2";;
        --minId) MINID="$2";;
        --thread) TH="$2";;
      esac
      shift 2
    done
    if [ -n "$QID" ]; then QID_ARG="--queryIdListFile $QID"; else QID_ARG=""; fi
    xvfb-run -a java -Xmx3g -cp "$JAR" biocjava.bioDoer.BLAST.ReciprocalBlast.ReciprocalBlast --querySeqFile "$Q" --subjectSeqFile "$S" $QID_ARG --outDirAndPrefix "$O" --NumOfthreads "$TH" --evalue "$EVAL" --minIdentityPercent "$MINID" --forseQueryBlastType "$PROG" --forseSubjectBlastType "$PROG"
    echo "[tbplot] 双向 BLAST 完成，见 ${O}_*"
    ;;
  filterCScore)
    # 用法: filterCScore <in.blast.tab6> <out.tab6> [--cscore 0.5]
    #   BLAST tab6 按 C-score 过滤（第107引擎，FilterBlastResultByCScore）——区分直系/旁系同源候选
    #   C-score 过滤低 identity 旁系同源（paralog），保留高 confidence 直系同源（ortholog）候选
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh filterCScore <in.blast.tab6> <out.tab6> [--cscore 0.5]"; exit 1; fi
    IN="$1"; OUT="$2"; CSCORE="0.5"; shift 2
    while [ $# -ge 2 ]; do
      case "$1" in
        --cscore) CSCORE="$2";;
      esac
      shift 2
    done
    java -Xmx1g -cp "$JAR" biocjava.bioDoer.BLAST.FilterBlastResultByCScore --inBlastTab6 "$IN" --outBlastTab "$OUT" --cscore "$CSCORE"
    echo "[tbplot] C-score 过滤完成: $(wc -l < "$IN") 行 → $(wc -l < "$OUT") 行"
    ;;
  quickFamily)
    # 用法: quickFamily <refPep.fa> <familyIds.txt> <queryPep.fa> <outPrefix> [--autoFill N] [--thread N] [--diamond true|false]
    #   快速基因家族鉴定（第108引擎，QuickGeneFamilyIdentification）——用参考家族成员从查询蛋白组找同源成员
    #   流程: 家族ID提取→参考蛋白集自比对(可选AutoFill迭代扩展)→query BLAST→输出家族成员
    #   输出: <outPrefix>.final.IDset.txt（成员ID）+ <outPrefix>.final.Seq.fasta（成员序列）
    #   ⚠️ AutoFill(默认2) 需要完整蛋白组(>20000)作参考集；小参考集测试用 --autoFill 0
    shift
    if [ $# -lt 4 ]; then echo "用法: tbplot.sh quickFamily <refPep.fa> <familyIds.txt> <queryPep.fa> <outPrefix> [--autoFill N] [--thread N] [--diamond true|false]"; exit 1; fi
    REF="$1"; FID="$2"; Q="$3"; O="$4"; AF="2"; TH="2"; DM="true"; shift 4
    while [ $# -ge 2 ]; do
      case "$1" in
        --autoFill) AF="$2";;
        --thread) TH="$2";;
        --diamond) DM="$2";;
      esac
      shift 2
    done
    java -Xmx3g -cp "$JAR" biocjava.bioDoer.BLAST.ReciprocalBlast.QuickGeneFamilyIdentification --ReferencePepSet "$REF" --ReferenceFamilyId "$FID" --QueryPepSet "$Q" --OutFilePrefix "$O" --NumOfThreads "$TH" --UseDiamond "$DM" --AutoCompleteRefSet "$AF"
    echo "[tbplot] 基因家族鉴定完成: $(wc -l < ${O}.final.IDset.txt 2>/dev/null || echo 0) 个成员 → ${O}.final.IDset.txt + ${O}.final.Seq.fasta"
    ;;
  ctgGroup)
    # 用法: ctgGroup <in.miniprot.gff> <polyPoid> <outContigGrpMap>
    #   in.miniprot.gff: miniprot --gff 输出（蛋白→contigs 比对）；组装辅助链第一环（第72引擎）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh ctgGroup <in.miniprot.gff> <polyPoid> <outContigGrpMap>"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/CtgGroupCli.java" 2>/dev/null
    xvfb-run -a java -Xmx1g -cp "$TBCLI_DIR:$JAR" CtgGroupCli "$@"
    ;;
  homoPhase)
    # 用法: homoPhase <inContigGrpMap> <outPhasedMap>
    #   同源冲突分区（多倍体相位分离）——组装辅助链第二环（第73引擎）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh homoPhase <inContigGrpMap> <outPhasedMap>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.GenomeAssembly.HomoConflictBasedPartition --inContigGrpMap "$1" --outPhasedMap "$2"
    ;;
  sepChr)
    # 用法: sepChr <gene2chr.tsv> <in.miniprot.gff> <outMap>
    #   gene2chr.tsv: 蛋白名\t染色体（注意：用蛋白名不是 mRNA ID！引擎读 ##PAF 行 info[1]=蛋白名）
    #   等位 contig → 染色体分配——组装辅助链第三环（第74引擎）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh sepChr <gene2chr.tsv> <in.miniprot.gff> <outMap>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.GenomeAssembly.SeperateChrByAlleles --inGene2ChrMap "$1" --inMiniprotGff "$2" --outMap "$3"
    ;;
  bamMerge)
    # 用法: bamMerge <gtf> <bamDir> <outDir>   # 按区域覆盖合并 BAM（多样本择优）
    #   输出: merged.bam + merged_sorted.bam(.bai) + merged_region.txt（第75引擎）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh bamMerge <gtf> <bamDir> <outDir>"; exit 1; fi
    xvfb-run -a java -Xmx4g -cp "$JAR" biocjava.bioDoer.GenomeAnnotation.BAMMergeByRegionCoverage "$1" "$2" "$3"
    ;;
  hicEnzyme)
    # 用法: hicEnzyme <inHiC.fastq>   # HiC 限制酶预测（第76引擎）
    #   从 HiC FastQ 预测酶切类型（MboI/DpnII|MseI|HindIII|NcoI|Arima）；引擎内部抽样 1000 条
    shift
    if [ $# -lt 1 ]; then echo "用法: tbplot.sh hicEnzyme <inHiC.fastq>"; exit 1; fi
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.GenomeAssembly.HiCRestrictionEnzymePrediction --inFq "$1"
    ;;
  virusRecomb)
    # 用法: virusRecomb <inDB.fa> <inContig.fa> <outDir>   # 病毒重组分析（第77引擎）
    #   inDB.fa: 病毒参考库；inContig.fa: 待查 contig；输出 Top hit 重组 PDF
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh virusRecomb <inDB.fa> <inContig.fa> <outDir>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.VirusDetect.RecombinationAnalysis --inDB "$1" --inContig "$2" --outDir "$3"
    ;;
  gxfRename)
    # 用法: gxfRename <in.gff3> <out.gff3> <renameMap.tsv>
    #   renameMap.tsv: 旧ID\t新ID（gene/mRNA/transcript）；Parent/ID 关系同步更新
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh gxfRename <in.gff3> <out.gff3> <renameMap.tsv>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.GXFUtils.GXFRenamer --inGXF "$1" --outGXF "$2" --renameMap "$3"
    ;;
  gxfStat)
    # 用法: gxfStat <in.gff3> <outStat.xls>   # GFF 统计（基因/mRNA/外显子/内含子/CDS/UTR 明细）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh gxfStat <in.gff3> <outStat.xls>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.GXFUtils.GXFfixer.GXFstat --inGXF "$1" --outStat "$2"
    ;;
  gxfAppend)
    # 用法: gxfAppend <in.gff3> <out.gff3> <prefix>   # GFF seqid+ID 加前缀
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh gxfAppend <in.gff3> <out.gff3> <prefix>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.GXFUtils.GxfIDAppender --inGff "$1" --outGff "$2" --prefix "$3"
    ;;
  gxfGenepos)
    # 用法: gxfGenepos <in.gff3> <outGenepos> <outChrLen> [feature]  # GFF→基因位置+染色体长度（喂 genelocation）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh gxfGenepos <in.gff3> <outGenepos> <outChrLen> [feature]"; exit 1; fi
    FEAT="exon"; [ $# -ge 4 ] && FEAT="$4"
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.GXFUtils.GXFToGenePosFile --inGXF "$1" --outGenePos "$2" --outChrLen "$3" --feature "$FEAT"
    ;;
  gxfRegion)
    # 用法: gxfRegion <in.gff3> <region.txt> <out.gff3> [--ignoreStrand] [--extendLen N]
    #   region.txt: chr\tstrand\tstart\tend\tinfo；按区域保留 GFF
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh gxfRegion <in.gff3> <region.txt> <out.gff3> [--ignoreStrand] [--extendLen N]"; exit 1; fi
    IGNS="false"; EXTL="0"; ARGS=("$@")
    for a in "${ARGS[@]}"; do [ "$a" = "--ignoreStrand" ] && IGNS="true"; done
    for i in $(seq 0 $((${#ARGS[@]}-1))); do
      [ "${ARGS[$i]}" = "--extendLen" ] && EXTL="${ARGS[$((i+1))]}"
    done
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.GXFUtils.GXFRegionSummary --inGxf "$1" --regionFile "$2" --outGxf "$3" --ignoreStrand "$IGNS" --extendLen "$EXTL"
    ;;
  gxfOverlap)
    # 用法: gxfOverlap <in.gff3> <region.txt> <out.gff3> [--ignoreStrand] [--extendLen N]
    #   region.txt: chr\tstrand\tstart\tend （strand 敏感！第2列是链 +/-）
    #   区域重叠过滤（第79引擎，GXFOverlaper）——与 gxfRegion 区别：这里 region 必带 strand
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh gxfOverlap <in.gff3> <region.txt> <out.gff3> [--ignoreStrand] [--extendLen N]"; exit 1; fi
    IGNS="false"; EXTL="2000"; ARGS=("$@")
    for a in "${ARGS[@]}"; do [ "$a" = "--ignoreStrand" ] && IGNS="true"; done
    for i in $(seq 0 $((${#ARGS[@]}-1))); do
      [ "${ARGS[$i]}" = "--extendLen" ] && EXTL="${ARGS[$((i+1))]}"
    done
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.GXFUtils.GXFOverlaper --inGxf "$1" --regionFile "$2" --outGxf "$3" --ignoreStrand "$IGNS" --extendLen "$EXTL"
    ;;
  gxfRepIDs)
    # 用法: gxfRepIDs <in.gff3> <out.txt>
    #   代表转录本映射：mRNA ID → gene ID + 长度（第80引擎，GXFToRepresentativeIDs）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh gxfRepIDs <in.gff3> <out.txt>"; exit 1; fi
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.GXFUtils.GXFToRepresentativeIDs --inGXF "$1" --outRepresentative "$2"
    ;;
  gxfRepGXF)
    # 用法: gxfRepGXF <in.gff3> <out.gff3> [--featureID CDS] [--attachID 'pattern']
    #   代表转录本提取（第86引擎，GXFToRepresentativeGXF）：每 gene 保留最长转录本，去冗余 isoform
    #   ⚠️ 命名要求：mRNA ID 须以 gene ID 开头（如 TGY000001.t1 Parent=TGY000001）；EVM 命名（evm.model ≠ evm.TU 前缀）不兼容
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh gxfRepGXF <in.gff3> <out.gff3> [--featureID CDS]"; exit 1; fi
    FEAT="CDS"; ATTACH="(.*exon.*)|(.*UTR.*)"
    ARGS=("$@")
    for i in $(seq 0 $((${#ARGS[@]}-1))); do
      [ "${ARGS[$i]}" = "--featureID" ] && FEAT="${ARGS[$((i+1))]}"
      [ "${ARGS[$i]}" = "--attachID" ] && ATTACH="${ARGS[$((i+1))]}"
    done
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.GXFUtils.GXFToRepresentativeGXF --inGXF "$1" --outRepresentativeGff3 "$2" --featureID "$FEAT" --attachID "$ATTACH"
    ;;
  gxfMatch)
    # 用法: gxfMatch <in.gff3> <inGenome.fa>
    #   GFF 与基因组 seqid 匹配检查（第81引擎，GxfGenomeMatch）→ Yes/No + Intersection Size
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh gxfMatch <in.gff3> <inGenome.fa>"; exit 1; fi
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.GXFUtils.GxfGenomeMatch --inGXF "$1" --inGenome "$2"
    ;;
  gxfRecall)
    # 用法: gxfRecall <in.gff3> <out.gff3>   # 从 gene 行恢复 mRNA 特征（第82引擎，RecallmRNAFeature）
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh gxfRecall <in.gff3> <out.gff3>"; exit 1; fi
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.GXFUtils.RecallmRNAFeature --in "$1" --out "$2"
    ;;
  regionAnno)
    # 用法: regionAnno <in.gff3> <region.txt> <outTab> [--flankLen N] [--targetFeaturePattern P]
    #   region.txt: id\tchr\tstart\tend （任意第1列！chr 在第2列 index1）
    #   区域重叠注释：输出 Genic/Intergenic + 重叠基因（第83引擎，RegionGXFOverlapAnnotation）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh regionAnno <in.gff3> <region.txt> <outTab> [--flankLen N]"; exit 1; fi
    FLANK="10000"; PAT="gene"
    ARGS=("$@")
    for i in $(seq 0 $((${#ARGS[@]}-1))); do
      [ "${ARGS[$i]}" = "--flankLen" ] && FLANK="${ARGS[$((i+1))]}"
      [ "${ARGS[$i]}" = "--targetFeaturePattern" ] && PAT="${ARGS[$((i+1))]}"
    done
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.GXFUtils.RegionGXFOverlapAnnotation --inGxf "$1" --region "$2" --outTab "$3" --flankLen "$FLANK" --targetFeaturePattern "$PAT"
    ;;
  gxfFix)
    # 用法: gxfFix <in.gff3> <out.gff3>   # GFF 修复（重复ID前缀/CDS phase/dangling mRNA/排序）
    #   修复 CDS phase 记录分离到 <out>_phase_corrected/problematic.gff3
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh gxfFix <in.gff3> <out.gff3>"; exit 1; fi
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.GXFUtils.GXFfixer.GXFFix --inGXF "$1" --outGff3 "$2"
    ;;
  groupCol)
    # 用法: groupCol <inTable.tsv> <inGrpInfo.tsv> <outTable> [Sum|Mean|Max|Min|Var|Std]
    #   inTable: 表达矩阵（首列基因名+样本列）；inGrpInfo: Sample\tGroup（无表头）
    #   outTable: 样本按组折叠后的矩阵（默认 Mean）——表达分组分析（第61引擎）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh groupCol <inTable> <inGrpInfo> <outTable> [Sum|Mean|Max|Min|Var|Std]"; exit 1; fi
    INTAB="$1"; INGRP="$2"; OUTTAB="$3"; COLTYPE="Mean"; shift 3
    [ $# -ge 1 ] && COLTYPE="$1"
    xvfb-run -a java -Xmx1g -cp "$JAR" biocjava.bioDoer.Table.TableColCollaspe --inTable "$INTAB" --inGrpInfo "$INGRP" --outTable "$OUTTAB" --ColType "$COLTYPE"
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
  phylotree)
    # 用法: phylotree <in.nwk> <out> [vertical] [width] [height]
    #   PhyloTreeView 系统发育树视图（08/31 攻下，纠正「需 TreeTab」误判）
    #   build() 直接吃 newick，内部自动算坐标；支持枝长/Cladogram 自动降级/坐标轴
    shift
    javac -cp "$JAR" "$TBCLI_DIR/PhyloTreeCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" PhyloTreeCli "$@"
    ;;
  unrooted)
    # 用法: unrooted <in.nwk> <out> [layout] [width] [height] [iterations]
    #   无根树可视化（引擎 115，unrootedtree 独立引擎，非 UnrootedTreeViz）
    #   layout: Circular|Radial|Force-Directed|Equal Angle|N-Body|Equal-Daylight（默认 Circular）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/UnrootedTreeCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" UnrootedTreeCli "$@"
    ;;
  violin)
    # 用法: violin <in.tsv> <out> [width] [height]
    #   独立小提琴图（引擎 116，ViolinPlot.generate()；仅 SVG/PDF）
    #   in.tsv: 组别\t值（每行一个观测）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/ViolinCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" ViolinCli "$@"
    ;;
  barplotter)
    # 用法: barplotter -g <gff> -s <synteny> -c <ctl> -o <out.png>
    #   合成共线性柱状图（引擎 117，bar_plotter.main1——main 是死代码）
    #   gff: chr\tgene\tend；synteny: MCScanX 式 collinearity；ctl: 4 行 xdim/ydim/xchr/ychr
    shift
    javac -cp "$JAR" "$TBCLI_DIR/BarPlotterCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" BarPlotterCli "$@"
    ;;
  findpath)
    # 用法: findpath --inGffArr <gff1,gff2,...> --inGenePairs <pairs> --inRegion <geneID> [--flankGeneNum N] [--highlightGene ID] --outGraph <out>
    #   共线性基因块进化路径（引擎 118，FindPathBySynteny.main1；main 硬编码演示）
    #   gff 需简化格式 chr\tgene\tstart\tend\tstrand；genepairs 每行 geneA\tgeneB
    shift
    javac -cp "$JAR" "$TBCLI_DIR/FindPathCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" FindPathCli "$@"
    ;;
  mcscanx)
    # 用法: mcscanx <gff> <blast> <outPrefix> [--html]   # 共线性检测
    #        mcscanx classify <gff> <blast> <outPrefix>  # 重复基因分类（WGD/tandem/proximal/dispersed/singleton）
    #   纯 Java MCScanX（工具 72，org.mcscanx.api.MCScanXAPI）——无需外部 MCScanX 二进制
    #   ⚠️ 与外部 MCScanX 输出 100% 一致验证（GRAS Co_wgd：334 blocks cmp 全同）；
    #      classify 的 String API 有 bug（validate 需 collinearityFile）→ 桥用完整 InputFiles/OutputOptions API
    shift
    javac -cp "$JAR" "$TBCLI_DIR/MCScanXCli.java" 2>/dev/null
    xvfb-run -a java -Xmx6g -cp "$TBCLI_DIR:$JAR" MCScanXCli "$@"
    ;;
  degramdom)
    # 用法: degramdom <in.tsv> [out.nwk]
    #   亲子表构建 Newick 树（工具 73，BuildDegramdomFromTable.process；main 硬编码演示）
    #   in.tsv: 子节点\t父节点\t枝长（每行一个关系）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/DegramdomCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" DegramdomCli "$@"
    ;;
  sambamcov)
    # 用法: sambamcov <in.bam> <out.tsv> [binSize] [countMode]
    #   BAM bin 覆盖统计（工具 74，SamBamBINCov.process——main 硬编码演示）
    #   binSize: 窗口 bp（默认 1000）；countMode: Overlap|StartPos|EndPos（默认 Overlap）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/SamBamCovCli.java" 2>/dev/null
    xvfb-run -a java -Xmx4g -cp "$TBCLI_DIR:$JAR" SamBamCovCli "$@"
    ;;
  bamindex)
    # 用法: bamindex <in.sorted.bam> [out.bai]
    #   BAM 索引创建（工具 75，BAMIndexCreater.process——main 硬编码演示）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/BamIndexCli.java" 2>/dev/null
    xvfb-run -a java -Xmx4g -cp "$TBCLI_DIR:$JAR" BamIndexCli "$@"
    ;;
  bamsort)
    # 用法: bamsort <in.bam> <out.bam> [sortOrder] [tmpDir]
    #   BAM 排序（工具 76，SAMBAMSorter.process——main 硬编码演示）
    #   sortOrder: coordinate|queryname|unsorted|duplicate（默认 coordinate）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/BamSortCli.java" 2>/dev/null
    xvfb-run -a java -Xmx4g -cp "$TBCLI_DIR:$JAR" BamSortCli "$@"
    ;;
  onesteptree)
    # 用法: onesteptree --inPepFie <in.pep> --outFilePrefix <outDir> [--bbTime N] [--clean true|false]
    #   一步法 ML 系统发育树（引擎 119，OneStepMLTree——pep→muscle→trimal→IQ-TREE MFP+UFboot）
    #   需系统 muscle+iqtree；⚠️ --bbTime ≥1000（iqtree 限制）；序列需 ≥4 条唯一
    shift
    xvfb-run -a java -Xmx4g -cp "$JAR" biocjava.bioIO.BioSoftPipeServer.OneStepMLTree "$@"
    ;;
  simplehmmscan)
    # 用法: simplehmmscan <pfamA.hmm> <target.pep> <idList.txt> <out.txt>
    #   Pfam 域快速扫描（工具 83，simpleHmmscan——main 硬编码演示 → setter+process，调系统 hmmsearch）
    #   ⚠️ 需 Pfam-A.hmm 数据库（本地 ~/.eggnog-mapper/data/pfam/）；idList 每行一个 Pfam NAME（如 GRAS）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/SimpleHmmscanCli.java" 2>/dev/null
    xvfb-run -a java -Xmx4g -cp "$TBCLI_DIR:$JAR" SimpleHmmscanCli "$@"
    ;;
  colorscheme)
    # 用法: colorscheme <in.tab> <out.tab> <refColIndex(1-based)>
    #   表格分组着色（工具 86，ColorSchemeGenerator.process——main 硬编码演示）
    #   输出 = 原表 + RGB 颜色列（分组键相同者同色组标记）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/ColorSchemeCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" ColorSchemeCli "$@"
    ;;
  regiondepth)
    # 用法: regiondepth <in.sam> <region> <out.depth> [scaleFactor]
    #   SAM 区域覆盖深度（工具 88，CalcRegionDepth.init+processRegion——main 硬编码演示）
    #   region: ChrID:Start-End；输出每碱基覆盖深度
    shift
    javac -cp "$JAR" "$TBCLI_DIR/RegionDepthCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" RegionDepthCli "$@"
    ;;
  markertools)
    # 用法: markertools <filter|dist|sampledist> <in.marker.tab> [maxPoint]
    #   分子标记分析组（工具 89：MarkerFilter minor allele / MarkerDist / SampleDist——main 均硬编码）
    #   in.marker.tab: 0/1 标记矩阵（行=样本，列=标记，首行列名+首列行名）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/MarkerToolsCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" MarkerToolsCli "$@"
    ;;
  annocompare)
    # 用法: annocompare <before.gff3> <after.gff3> <outDir> [runName] [reciprocalOverlap] [boundaryTol] [cdsChangePct] [utrChangePct] [geneScope] [overlapMode]
    #   注释版本对比管线：对比同一基因组前后两版注释，产 change_summary.csv/change_log.csv/BED +
    #   Curation 图 + ABCD 四图（PNG/PDF/SVG）+ 单物种 ABCD 表（08/31 攻下）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/StructAnnoCompareCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" StructAnnoCompareCli "$@"
    ;;
  genedensity)
    # 用法: genedensity <in.gff3> <out.tsv> [binSize]
    #   基因密度谱：按窗口统计每染色体/contig 基因数（基因组轨道/密度分析）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/GeneDensityCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" GeneDensityCli "$@"
    ;;
  seqconvert)
    # 用法: seqconvert -i <in> -o <out> -iF <fmt> -oF <fmt>
    #   序列格式转换（main1 入口；fmt: fasta|clustal|MEGA|nexus|PAML|phylip）
    shift
    javac -cp "$JAR" "$TBCLI_DIR/SeqConverterCli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" SeqConverterCli "$@"
    ;;
  trimmsa)
    # 用法: trimmsa <in.aln.fa> <out.aln.fa> [ratio]
    #   MSA 修剪（按列保留率），main 硬编码 → 桥 setter+process
    shift
    javac -cp "$JAR" "$TBCLI_DIR/TrimMSACli.java" 2>/dev/null
    xvfb-run -a java -Xmx2g -cp "$TBCLI_DIR:$JAR" TrimMSACli "$@"
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
  efpHeat)
    # 用法: efpHeat <inTGA> <sample2cc.txt> <expMat.tsv> <geneId> <out.svg> [--imageWidth N] [--imageHeight N]
    #   eFP 浏览器风格组织表达热图（第100引擎，generateSuperHeatMap）——TGA 植物示意图上叠加表达
    #   inTGA: 底图（植物/组织示意图，必须 TrueColor RGB 非灰度）；sample2cc: SampleName\tRGB 映射
    #   expMat: 首列基因名 + 样本列；geneId: 要可视化的基因；out: .svg/.pdf/.png
    #   ⚠️ 需 fake DatatypeConverter（build/javax/xml/bind/，JDK9+ 移除 jaxb 的兼容 hack）
    shift
    if [ $# -lt 5 ]; then echo "用法: tbplot.sh efpHeat <inTGA> <sample2cc.txt> <expMat.tsv> <geneId> <out.svg>"; exit 1; fi
    W="0"; H="0"; ARGS=("$@")
    for i in $(seq 0 $((${#ARGS[@]}-1))); do
      [ "${ARGS[$i]}" = "--imageWidth" ] && W="${ARGS[$((i+1))]}"
      [ "${ARGS[$i]}" = "--imageHeight" ] && H="${ARGS[$((i+1))]}"
    done
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" biocjava.bioDoer.SimpleEfpBrowser.generateSuperHeatMap --inTGA "$1" --inSample2CC "$2" --expMat "$3" --geneId "$4" --outImg "$5" --imageWidth "$W" --imageHeight "$H"
    ;;
  rnaplot)
    # 用法: rnaplot <seq.fa|rawSeq> <out> [--colorMap "seq1=R,G,B;seq2=R,G,B"] [--interactive false]
    #   RNA 二级结构图（第111引擎，RNAplotAdvance，需 RNAfold/RNAplot 可执行）
    #   ⚠️ 本机 RNAplot 2.7 不读 stdin 管道（generatePlotPsFile 失败）→ 桥自己 RNAplot -i 生成 EPS + transformat 解析
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh rnaplot <seq> <out> [--colorMap ..]"; exit 1; fi
    javac -cp "build:$JAR" "$TBCLI_DIR/RNAplotCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:build:$JAR" RNAplotCli "$@"
    ;;
  calcRepeat)
    # 用法: calcRepeat <genome.fa> <outRepeat.txt> [--kmerSize N] [--minFreq N] [--threads N]
    #   重复序列得分计算（工具39，calcRepeatScore，需 jellyfish）
    #   ⚠️ 内部默认 60 线程 jellyfish count 易挂 → 桥预生成 .jf（合理线程数）+ process() 复用
    shift
    if [ $# -lt 2 ]; then echo "用法: tbplot.sh calcRepeat <genome.fa> <out> [--kmerSize N]"; exit 1; fi
    javac -cp "build:$JAR" "$TBCLI_DIR/CalcRepeatCli.java" 2>/dev/null
    java -Xmx2g -cp "$TBCLI_DIR:build:$JAR" CalcRepeatCli "$@"
    ;;
  multiEfp)
    # 用法: multiEfp <inTGA> <sample2cc> <expMat1[,expMat2,...]> <geneId> <out> [--imageWidth N] [--imageHeight N]
    #   多矩阵组织表达热图（第110引擎，generateMultipleSuperHeatMap）——TGA 底图 + 多表达矩阵叠加
    #   ⚠️ main 硬编码第二矩阵路径 → 走桥（setter+反射 initExp+showHeatMapOf→JIGBasePanel）；需 fake DatatypeConverter
    shift
    if [ $# -lt 5 ]; then echo "用法: tbplot.sh multiEfp <inTGA> <sample2cc> <expMat> <geneId> <out> [--imageWidth N]"; exit 1; fi
    javac -cp "build:$JAR" "$TBCLI_DIR/MultiSuperHeatCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:build:$JAR" MultiSuperHeatCli "$@"
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
  mirnaTarget2)
    # 用法: mirnaTarget2 <mirna.fa> <target.fa> <out.txt> [--revCom true|false] [--fragment true|false] [--threads N]
    #   Target2TablePipe 完整管线：miRNA + 基因组/转录本 → 全量靶标表（含比对行，未过滤低分）
    #   与 mirnatarget 区别：直接用官方完整封装（ssearch36 内置），输出含全部命中+比对列
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh mirnaTarget2 <mirna.fa> <target.fa> <out.txt> [--revCom true|false]"; exit 1; fi
    MIRA="$1"; TGTA="$2"; OUTA="$3"; REV="true"; FRAG="false"; TH="4"; shift 3
    while [ $# -ge 2 ]; do
      case "$1" in
        --revCom) REV="$2";;
        --fragment) FRAG="$2";;
        --threads) TH="$2";;
      esac
      shift 2
    done
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.miRNA.Target2TablePipe --inMIRfa "$MIRA" --inGenomeFa "$TGTA" --outTable "$OUTA" --searchRevCom "$REV" --isFragment "$FRAG" --maxThreadNum "$TH" 2>/dev/null
    echo "[tbplot] miRNA 靶标管线完成: $OUTA"
    ;;
  mirnaIdentify)
    # 用法: mirnaIdentify <genome.fa> <targetSo.tsv> <outPredict.txt> [outChecklog.txt] [--checkARM BOTH|FIVE|THREE] [--maxAsy N] [--maxMatureAsy N] [--maxStarAsy N] [--maxBulge N]
    #   genome.fa: 基因组（FAindex 索引，染色体名须与靶标表第2列一致）
    #   targetSo.tsv: TargetSo 输出（第2列=染色体名，第4/5列=基因组坐标）——mirnatarget 输出后用 positionRecover 转换坐标
    #   outPredict.txt: 预测前体表；outChecklog.txt: 结构检查日志（maxBulge/ARM 过滤原因）
    #   ⚠️ MIRidentifier 第78引擎：miRNA 前体鉴定（RNAfold 结构检查 + ARM 判定）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh mirnaIdentify <genome.fa> <targetSo.tsv> <outPredict.txt> [outChecklog.txt] [--checkARM BOTH|FIVE|THREE]"; exit 1; fi
    GENOME="$1"; INTSV="$2"; OUTP="$3"; shift 3
    OUTL="${OUTP%.txt}.checklog.txt"
    CHECKARM="BOTH"; MAXASY="1"; MAXMAT="1"; MAXSTAR="0"; MAXBULGE="2"
    while [ $# -ge 2 ]; do
      case "$1" in
        --checkARM) CHECKARM="$2";;
        --maxAsy) MAXASY="$2";;
        --maxMatureAsy) MAXMAT="$2";;
        --maxStarAsy) MAXSTAR="$2";;
        --maxBulge) MAXBULGE="$2";;
        *) OUTL="$1";;
      esac
      shift 2
    done
    javac -cp "$JAR" "$TBCLI_DIR/MirIdentifyCli.java" 2>/dev/null
    xvfb-run -a java -Djava.io.tmpdir="${TMPDIR_TB:-/tmp}" -Xmx8g -cp "$TBCLI_DIR:$JAR" MirIdentifyCli "$GENOME" "$INTSV" "$OUTP" "$OUTL" --checkARM "$CHECKARM" --maxAsy "$MAXASY" --maxMatureAsy "$MAXMAT" --maxStarAsy "$MAXSTAR" --maxBulge "$MAXBULGE"
    echo "[tbplot] miRNA 前体鉴定完成: $OUTP"
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
  collinearRegion)
    # 用法: collinearRegion <in.collinearity> <simGff> <out.txt>
    #   MCScanX 共线性→区域文件（第104引擎，CollinearityToRegion）
    #   输出: chr1 start1 end1 chr2 start2 end2 genePairInfo——供共线性区块分析/可视化
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh collinearRegion <in.collinearity> <simGff> <out.txt>"; exit 1; fi
    xvfb-run -a java -Xmx2g -cp "$JAR" biocjava.bioDoer.ComparativeGenomics.MCScanX.CollinearityToRegion --inCollinearity "$1" --inSimGff "$2" --outTab "$3"
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
  dualsyn)
    # 用法: dualsyn <simplifiedGff> <collinearity> <out> [--chr1 "1,2"] [--chr2 "3,4"] [--rows N] [--gap N]
    #   simplifiedGff: Chr\tGeneName\tStart\tEnd（染色体名必须数字）
    #   collinearity: MCScanX 输出（*.collinearity）
    #   引擎: DualSyntenyPlotterAdvance（旧 JJplot2 框架，反射扫描窗口树提取 GUI 实例保存）
    shift
    if [ $# -lt 3 ]; then echo "用法: tbplot.sh dualsyn <simplifiedGff> <collinearity> <out> [--chr1 ..] [--chr2 ..]"; exit 1; fi
    javac -cp "$JAR" "$TBCLI_DIR/DualSynCli.java" 2>/dev/null
    xvfb-run -a java -Xmx3g -cp "$TBCLI_DIR:$JAR" DualSynCli "$@"
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
  echo "  tbplot.sh groupCol <inTable> <inGrpInfo> <outTable> [Sum|Mean|Max|Min|Var|Std]   # 表达样本按组折叠"
  echo "  tbplot.sh batchReplace <inFile> <outFile> <patternMap.tsv> [--partial]          # 批量ID替换"
  echo "  tbplot.sh tableCollapse <inTable> <keyColIndex> <outTable> [hasHeader]           # 表格按键折叠"
  echo "  tbplot.sh fqTrim <in.fq> <out.fq> [--b5 N] [--b3 N] [--threads N]                 # FASTQ固定长度修剪"
  echo "  tbplot.sh gxfRename <in.gff3> <out.gff3> <renameMap.tsv>                          # GFF ID重命名(Parent同步)"
  echo "  tbplot.sh nwAlign <inSeq1.txt> <inSeq2.txt> <out>                                  # Needleman-Wunsch全局比对"
  echo "  tbplot.sh ctgGroup <in.miniprot.gff> <polyPoid> <outGrpMap>                        # contig等位分组(miniprot)"
  echo "  tbplot.sh homoPhase <inContigGrpMap> <outPhasedMap>                                # 同源冲突分区(多倍体相位)"
  echo "  tbplot.sh sepChr <gene2chr.tsv> <in.miniprot.gff> <outMap>                          # 等位contig→染色体分配"
  echo "  tbplot.sh bamMerge <gtf> <bamDir> <outDir>                                          # 按区域合并BAM(覆盖择优)"
  echo "  tbplot.sh hicEnzyme <inHiC.fastq> [--numOfRecords N]                                 # HiC限制酶预测"
  echo "  tbplot.sh virusRecomb <inDB.fa> <inContig.fa> <outDir>                              # 病毒重组分析"
  echo "  tbplot.sh gxfStat <in.gff3> <outStat.xls>                                             # GFF统计"
  echo "  tbplot.sh gxfAppend <in.gff3> <out.gff3> <prefix>                                     # GFF ID加前缀"
  echo "  tbplot.sh gxfGenepos <in.gff3> <outGenepos> <outChrLen> [feature]                     # GFF→基因位置(喂genelocation)"
  echo "  tbplot.sh gxfRegion <in.gff3> <region.txt> <out.gff3> [--ignoreStrand] [--extendLen N] # 区域筛选GFF"
  echo "  tbplot.sh exprCorr <inFPKM> <outCorrMat>                                        # 表达相关矩阵(Pearson)"
  echo "  tbplot.sh msy <simplifiedGff.pos> <links.txt> <chrLayout.txt> <out> [w] [h]  # 多物种微共线性图"
  echo "  tbplot.sh microsyn <gxf1> <gxf2> <collinearity> <out> [--chr1 .. --start1 ..] # 双基因组微共线性图"
  echo "  tbplot.sh venn5 <out> <5 sets> [labels]                                      # 五集合韦恩图"
  echo "  tbplot.sh venn6 <out> <6 sets> [labels]                                      # 六集合韦恩图"
  echo "  tbplot.sh generic <engineClass> <method> <out> [--set f v ...]                 # 通用反射桥(任意TBtools引擎)"
    ;;
esac
