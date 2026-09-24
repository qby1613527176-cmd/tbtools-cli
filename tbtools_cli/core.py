"""tbtools-cli 核心引擎：通用选项 + _run_java wrapper + 统一输出格式 + 输入校验"""
import os
import shutil
import subprocess
import sys
import tempfile


from tbtools_cli.config import get_default  # heap 可配置(第六轮评审)
from tbtools_cli.errors import ERROR_CODES, classify_error  # noqa: F401  # 错误契约(拆分第一步)
# core.py 拆分(2026-09-24): i18n/env/validation 迁至 runtime/{i18n,env,validation}.py(重导出保兼容)
from tbtools_cli.runtime.i18n import _, _lang_cache_clear, _use_en  # noqa: F401
from tbtools_cli.runtime.env import (  # noqa: F401
    BRIDGES_DIR,
    BUILD_DIR,
    CP_SEP,
    JAR,
    ROOT,
    cp,
    find_jar_deep,
    get_jar,
    get_java,
    safe_temp,
    stdout_path,
)
from tbtools_cli.runtime.validation import (  # noqa: F401
    EXPECTED_INPUT_FORMATS,
    check_input_format,
    detect_format,
    validate_file,
    validate_format_cols,
)

PITFALL_HINTS = {
    "onesteptree": "--bb-time 必须 ≥1000（IQ-TREE UFBoot 下限），小于 1000 会静默不产树；序列须 ≥4 条唯一（太相似会被合并报错）；outFilePrefix 若是目录，产物命名为 目录/TBtools.*",
    "draw": "输入必须是 TreeTab 配置（[TYPE]:Tree + [NEWICK]: 行），直接喂 .nwk 曾导致引擎从 stdin 读入而挂起（G2 已修复为快速报错）；只画树用 tbtools tree phylotree",
    "hmmsearch": "调系统 hmmsearch 二进制（Linux: apt install hmmer；Windows: TBtools-II/bin 需加入 PATH）；idList 是 Pfam ID 每行一个（如 GRAS），不是基因 ID",
    "simplehmmscan": "调系统 hmmsearch 二进制（Linux: apt install hmmer；Windows: TBtools-II/bin 需加入 PATH）；需 Pfam-A.hmm 数据库文件，idList 每行一个 Pfam",
    "hclust": "输入必须是三列距离文件 GeneA\\tGeneB\\tdist（不是表达矩阵！）",
    "barplot": "termCol/pvalCol 用列名（如 Term/Pvalue），不是列索引数字",
    "cubeheatmap": "group 文件第一行会被当数据——喂前先去表头",
    "admixture": "第一个参数是 qFiles.lst（每行一个 Q 矩阵文件路径），不是 Q 矩阵内容",
    "dotplot": "--chrLayout 传文件路径（内容: Genome: Chr1 Chr2...），不是内联字符串",
    "microsyn": "必须指定 --chr1/--start1/--end1 和 --chr2/--start2/--end2；染色体名须数字；简化 GFF=数字染色体名\tGene\tStart\tEnd；输出父目录须存在",
    "dualsyn": "简化 GFF 染色体名必须数字（parseInt）；需显式 --chr1/--chr2",
    "msy": "简化 GFF 染色体名必须数字；基因名在第 2 列；坐标列不连 -",
    "multisyn": "染色体名必须数字；gxf.lst 路径不能硬编码",
    "pafviz": "PAF 文件必须 13 列（不足会 [12] 越界）",
    "pafref": "PAF 必须含 cg:Z: CIGAR 标签（minimap2 -c --cs 输出自带）",
    "peaktss": "签名 <gxf> <macs2_peak.xls> <out>——gxf 是必给第 1 参",
    "peakanno": "peak 用 MACS2 格式；坐标须百万级 bp（小坐标触发 bin 边界 bug）",
    "supercircos": "配置文件 [chrLen] 后跟文件路径，非内联数据；[link]/[gene]/[track] 同理",
    "gel": "LaneLabels 逗号分隔（第一个给 marker）；MarkerRange 降序；FragmentRangeArr 分号泳道/逗号片段",
    "motif": "需真 meme.xml + 序列 ID 匹配的 ID 列表（grep -oP 'name=\"[^\"]+\"' meme.xml 提取）",
    "colorscheme": "refColIndex 是 1-based（传 0 会 IndexOutOfBounds）",
    "plotrna": "必须带 --directPDF 否则弹窗；只支持 PDF",
    "pep2codon": "参数顺序 <cds.fa> <pep.aln.fa> <out>（先 CDS 后蛋白比对）",
    "goParse": "产物写到输入文件同目录（<输入名>.TBtools.Parsed.*），无独立输出参数",
    "mcscanx": "gff 简化格式 chr\\tgene\\tstart\\tend；blast 用 tab6；classify 须同时给 collinearityFile+geneTypeFile",
    "efpHeat": "TGA 底图必须 TrueColor(type2)；需 fake DatatypeConverter",
    "multiEfp": "TGA 底图必须 TrueColor(type2)；需 fake DatatypeConverter",
    "layoutheatmap": "layout.tsv 样本名须与 expr.tsv 表头一致（官方 examples 两文件样本名不匹配会 ArrayIndexOutOfBounds，属数据问题非命令缺陷）",
    "annocompare": "输入两个 GFF3 + 输出目录；生成 change_summary.csv + figures/*；before/after 须有共同 seqid（无共同序列报 IOException）",
    "nwAlign": "输入文件每行一条序列，无 FASTA 头（传 FASTA 会把 >s1 当序列）",
    "treeRooting": "Newick 树必须带枝长（裸 Newick 报 Corrupt NEWICK format）",
    "distance": "方法名小写 euclidean/pearson/pearsonDist；结果输出到 stdout（非文件）；col1/col2 是列索引(从 0 起)非列名（喂列名报 NumberFormatException）",
    "markertools": "首参是子命令 filter|dist|sampledist（非文件）；结果输出到 stderr（非 stdout！）；$(...) 需 2>&1 捕获",
    "barplotter": "选项式引擎: -g <gff> -s <synteny> -c <ctl> -o <out>（非位置参数；宽高须 >0）",
    "qpcrproc": "输入 qpcr 表列格式须规范（列数不足 ArrayIndexOutOfBounds）",
    "qdot": "GFF 用 4 列简化格式 Chr\tGene\tStart\tEnd（全 GFF 带特征列会被引擎当数字解析报 NumberFormatException）",
    "findblockmultiple": "需真实跨物种共线数据（合成数据无共线块→空输出）",
    "cddmotif": "cdd.hitdata 须 CDD 标准 8 列（qstart/qend/…）；列数不足越界",
    "seqlentrack": "序列 ID/树 taxon 须与 motif 域信息匹配（不匹配报 IOException）",
    "pfammotif": "输入 newick 树 taxon 须与 motif 信息匹配",
    "calcRepeat": "需要 jellyfish 在 PATH（Windows 默认缺失；apt install jellyfish）",
    "rnaplot": "需要 RNAfold/RNAplot 在 PATH（Windows 默认缺失；Linux apt install rna-folding）",
    "preparespecies": "首参是 ID 前缀字符串（非文件）",
    "marker": "首参是子命令 MarkerDist|MarkerFilter|SampleDist|BigMarkerRandomDesign（非文件）",
    "venn5": "首参是输出文件（非输入）；setA..E.txt 才是输入",
    "venn6": "首参是输出文件（非输入）；setA..F.txt 才是输入",
}


# PITFALL 英文版(Top10 高频命令;其余 en 模式回退中文——完整翻译见 backlog)
PITFALL_HINTS_EN = {
    "hclust": "hclust requires a THREE-column distance file: GeneA\tGeneB\tdistance (not an expression matrix!)",
    "msy": "Microsynteny: simplified GFF must use NUMERIC chromosome names; gene name in column 2; coordinates in one column",
    "venn2": "venn2 uses flag style: --List1 a.txt --List2 b.txt --label1 A --label2 B --graph out.svg --prefix <prefix>",
    "venn5": "venn5: first arg is the OUTPUT file (not input); pass setA..E.txt as inputs",
    "venn6": "venn6: first arg is the OUTPUT file (not input); pass setA..F.txt as inputs",
    "peaktss": "peaktss: input GXF + MACS2 peak table; --dist sets the window around TSS",
    "onesteptree": "--bb-time must be >= 1000 (IQ-TREE UFBoot minimum); smaller values are rejected",
    "motif": "motif requires a REAL MEME XML (with motif definitions) + an ID list matching the sequences",
    "tableMerge": "tableMerge: engine takes --inFileArr/--inColIndexArr/--outTable (hidden --config supported); first positional arg treated as output",
    "barplot": "barplot uses COLUMN NAMES (e.g. Term/Pvalue), not column indices",
    "draw": "Input must be a TreeTab config ([TYPE]:Tree + [NEWICK]: lines); feeding a raw .nwk used to crash",
    "hmmsearch": "Calls the system hmmsearch binary (Linux: apt install hmmer; Windows: bundled in TBtools)",
    "simplehmmscan": "Calls the system hmmsearch binary (Linux: apt install hmmer; Windows: bundled in TBtools)",
    "cubeheatmap": "The first row of the group file is treated as data — strip the header before feeding",
    "admixture": "First arg is qFiles.lst (one Q-matrix file path per line), not the Q matrix content",
    "dotplot": "--chrLayout takes a FILE PATH (content: Genome: Chr1 Chr2...), not an inline string",
    "microsyn": "Must specify --chr1/--start1/--end1 and --chr2/--start2/--end2; chromosome names must be numeric",
    "dualsyn": "Simplified GFF chromosome names must be numeric (parseInt); explicit --chr1/--chr2 required",
    "multisyn": "Chromosome names must be numeric; the gxf.lst path cannot be hardcoded",
    "pafviz": "PAF file must have 13 columns (fewer causes index [12] out-of-bounds)",
    "pafref": "PAF must include cg:Z: CIGAR tags (minimap2 -c --cs output has them)",
    "peakanno": "Peaks use MACS2 format; coordinates must be in megabases (small coordinates trigger a bin-boundary bug)",
    "supercircos": "Config [chrLen] takes a file path, not inline data; same for [link]/[gene]/[track]",
    "gel": "LaneLabels comma-separated (the first one is the marker); MarkerRange descending; FragmentRange within bounds",
    "colorscheme": "refColIndex is 1-based (passing 0 causes IndexOutOfBounds)",
    "plotrna": "Must use --directPDF or it pops a dialog; PDF output only",
    "pep2codon": "Argument order is <cds.fa> <pep.aln.fa> <out> (CDS first, then the protein alignment)",
    "goParse": "Outputs are written next to the input file (<input>.TBtools.Parsed.*); no separate output argument",
    "mcscanx": "gff simplified format chr\tgene\tstart\tend; blast uses tab6; classify requires the same prefix",
    "efpHeat": "TGA base image must be TrueColor (type 2); needs the fake DatatypeConverter",
    "multiEfp": "TGA base image must be TrueColor (type 2); needs the fake DatatypeConverter",
    "layoutheatmap": "layout.tsv sample names must match expr.tsv headers (official examples mismatch → ArrayIndexOutOfBounds)",
    "annocompare": "Inputs are two GFF3 + an output dir; generates change_summary.csv + figures/*; annotate before compare",
    "nwAlign": "Each line of input is one sequence without FASTA headers (FASTA input treats >s1 as a sequence)",
    "treeRooting": "Newick tree must have branch lengths (bare Newick → Corrupt NEWICK format)",
    "distance": "Method names lowercase: euclidean/pearson/pearsonDist; results go to stdout (not a file)",
    "markertools": "First arg is a subcommand filter|dist|sampledist (not a file); results go to stderr",
    "barplotter": "Flag-style engine: -g <gff> -s <synteny> -c <ctl> -o <out> (not positional; width/height as flags)",
    "qpcrproc": "Input qpcr table columns must be well-formed (too few columns → ArrayIndexOutOfBounds)",
    "qdot": "GFF uses the 4-column simplified format Chr\tGene\tStart\tEnd (full GFF → NumberFormatException)",
    "findblockmultiple": "Needs real cross-species collinearity data (synthetic data has no blocks → empty output)",
    "cddmotif": "cdd.hitdata must be standard CDD 8 columns (qstart/qend/...); too few columns → out-of-bounds",
    "seqlentrack": "Sequence IDs / tree taxa must match the motif domain info (mismatch → IOException)",
    "pfammotif": "Input newick tree taxa must match the motif info",
    "calcRepeat": "Needs jellyfish in PATH (missing on Windows by default; apt install jellyfish)",
    "rnaplot": "Needs RNAfold/RNAplot in PATH (missing on Windows by default; Linux: apt install ...)",
    "preparespecies": "First arg is an ID prefix string (not a file)",
    "marker": "First arg is a subcommand MarkerDist|MarkerFilter|SampleDist|BigMarkerRandomDesign (not a file)",
}


def get_pitfall_hint(command_name: str) -> str | None:
    """获取已知坑位提示;en 模式优先英文版(未翻译回退中文)"""
    if _use_en():
        return PITFALL_HINTS_EN.get(command_name) or PITFALL_HINTS.get(command_name, "")
    return PITFALL_HINTS.get(command_name, "")

# ---- 统一输出格式处理 ----

def ensure_bridge(bridge_name: str) -> None:
    """确保桥 Java 文件已编译到 build/ 目录"""
    src = os.path.join(BRIDGES_DIR, f"{bridge_name}.java")
    dst = os.path.join(BUILD_DIR, f"{bridge_name}.java")

    # 同步源码到 build/
    if os.path.isfile(src):
        need_copy = (not os.path.isfile(dst)
                     or os.path.getmtime(src) > os.path.getmtime(dst))
        if need_copy:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    # 编译（如果 .class 不存在或源码更新）
    cls_file = os.path.join(BUILD_DIR, f"{bridge_name}.class")
    if not os.path.isfile(cls_file) or (
        os.path.isfile(dst) and os.path.getmtime(dst) > os.path.getmtime(cls_file)
    ):
        _r = subprocess.run(
            ["javac", "-cp", JAR, dst],
            capture_output=True, cwd=BUILD_DIR
        )
        # 桥编译失败即中断(评审 #15): 不继续启动 Java(否则 ClassNotFound 掩盖真实错误归因)
        if _r.returncode != 0:
            _err = _r.stderr.decode("utf-8", "replace") if _r.stderr else ""
            print(f"❌ 桥编译失败 {bridge_name}(TB_BRIDGE_COMPILE_FAILED):\n{_err[-800:]}", file=sys.stderr)
            sys.exit(6)  # TB_BRIDGE_COMPILE_FAILED(统一所有调用点: 表驱动/手动 impl 均受益)

    # N27: fake jaxb DatatypeConverter（JDK9+ 无 javax.xml.bind）随仓库分发源码，
    # 有需要即编译到 build/javax/xml/bind/（全新 checkout 也能重建，修复 NoClassDefFoundError）
    fake_src = os.path.join(BRIDGES_DIR, "javax", "xml", "bind", "DatatypeConverter.java")
    if os.path.isfile(fake_src):
        fake_cls = os.path.join(BUILD_DIR, "javax", "xml", "bind", "DatatypeConverter.class")
        if (not os.path.isfile(fake_cls)
                or os.path.getmtime(fake_src) > os.path.getmtime(fake_cls)):
            os.makedirs(os.path.dirname(fake_cls), exist_ok=True)
            subprocess.run(["javac", "-d", BUILD_DIR, fake_src], capture_output=True)

# ---- xvfb-run 包装 ----
def run_plot(java_args: list, verbose: bool = False, quiet: bool = False, use_xvfb: bool = True, command_name: str | None = None) -> int:
    """执行绘图引擎（需要 xvfb-run）"""
    if use_xvfb and shutil.which("xvfb-run"):
        full_args = ["xvfb-run", "-a"] + java_args
    else:
        full_args = java_args
    return run_java(full_args, verbose=verbose, quiet=quiet, command_name=command_name)


# ---- ANSI 彩色（仅 TTY 时启用）----
def _tty() -> bool:
    try:
        return bool(sys.stdout.isatty())
    except Exception:
        return False

def c(text, color=None, bold=False):
    """条件 ANSI 着色：非 TTY 返回原样"""
    if not _tty():
        return text
    codes = {"red": "31", "green": "32", "yellow": "33", "blue": "34",
             "magenta": "35", "cyan": "36", "dim": "2", "bold": "1"}
    out = []
    if bold:
        out.append("1")
    if color in codes:
        out.append(codes[color])
    if not out:
        return text
    return f"\033[{';'.join(out)}m{text}\033[0m"

def pre_flight(cmd_name: str, first_file: str) -> None:
    """手动注册命令的早期格式检查（打印警告，不阻断）"""
    if not first_file or str(first_file).startswith('-'):
        return
    ok, _ = validate_file(str(first_file))
    if not ok:
        return
    warn = check_input_format(cmd_name, str(first_file))
    if warn:
        print(f"⚠️ 格式提醒: {warn}", file=sys.stderr)
        print("   （继续执行；如确认无误可忽略）", file=sys.stderr)


# ---- G5: 注册引擎类完整性探测（不起 JVM，zip 中央目录秒查）----
def probe_dead_engines():
    """提取代码中硬编码的 biocjava.* 引擎类，检查 jar 内是否存在对应 .class。

    覆盖: auto_commands.py / cli.py / cli_tools_registry.py / bridges/*.java
    返回 [(className, 来源文件), ...]（缺失项）；jar 不可读时返回 []。
    用途: tbtools doctor 死命令预警（外部测试 P1-1：2.475 jar 无
    Phylogenetics.OneStepTree，tbtools tree one-step 直接 ClassNotFound）。
    """
    import re as _re
    import zipfile
    try:
        with zipfile.ZipFile(JAR) as z:
            names = set(z.namelist())
    except Exception:
        return []
    pat = _re.compile(r'"(biocjava\.[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+)"')
    dead: dict[str, str] = {}
    srcs = [os.path.join(ROOT, "tbtools_cli", "auto_commands.py"),
            os.path.join(ROOT, "tbtools_cli", "cli.py"),
            os.path.join(ROOT, "tbtools_cli", "cli_tools_registry.py")]
    bridges_dir = os.path.join(ROOT, "bridges")
    if os.path.isdir(bridges_dir):
        srcs += [os.path.join(bridges_dir, f) for f in os.listdir(bridges_dir) if f.endswith(".java")]
    for src in srcs:
        if not os.path.isfile(src):
            continue
        try:
            with open(src, encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue
        for m in pat.finditer(content):
            cls = m.group(1)
            path = cls.replace(".", "/") + ".class"
            if path not in names:
                dead.setdefault(cls, os.path.basename(src))
    return sorted(dead.items())

# ── core.py 拆分(GPT 评审 #8): Java 执行/输入保护/provenance 迁至 runtime/java.py, 此处重导出保持兼容 ──
from tbtools_cli.runtime.java import (  # noqa: E402  # 延迟到模块加载完(避免循环 import)
    _n19_move_result,
    _sha1_file,
    _write_provenance,
    check_missing_outputs,
    cleanup_side_effects,
    find_empty_inputs,
    resolve_output,
    run_java,
    snapshot_inputs,
    verify_and_restore,
)  # noqa: F401  # 重导出(拆分兼容)——配合 pyproject: 见 [tool.ruff.lint.per-file-ignores]
