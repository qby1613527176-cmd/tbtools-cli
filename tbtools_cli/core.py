"""tbtools-cli 核心引擎：通用选项 + _run_java wrapper + 统一输出格式 + 输入校验"""
import subprocess, tempfile, os, sys, re, shutil
import click

# ---- 配置 ----
def get_jar():
    jar = os.environ.get("TBTOOLS_JAR", "")
    if jar and os.path.isfile(jar):
        return jar
    # 配置文件
    try:
        from tbtools_cli.config import get_jar as cfg_jar
        cj = cfg_jar()
        if cj and os.path.isfile(cj):
            return cj
    except Exception:
        pass
    for cand in [
        os.path.expanduser("~/tbtools-cli/lib/TBtools_JRE1.6.jar"),
        os.path.expanduser("~/TBtools/TBtools_JRE1.6.jar"),
        os.path.expanduser("~/Downloads/TBtools_JRE1.6.jar"),
        "/opt/TBtools/TBtools_JRE1.6.jar",
    ]:
        if os.path.isfile(cand):
            return cand
    return jar  # 返回空或原始值（让下游报错）

JAR = get_jar()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGES_DIR = os.path.join(ROOT, "bridges")
BUILD_DIR = os.path.join(ROOT, "build")

# ---- 输入校验 ----
def validate_file(path, desc="输入文件", check_readable=True):
    """校验文件存在性 + 可读性。返回 (ok, msg)"""
    if not path:
        return False, f"❌ {desc}: 路径为空"
    if path in ("-", "/dev/stdin", "/dev/stdout"):
        return True, ""  # 管道跳过校验
    if not os.path.exists(path):
        return False, f"❌ {desc}: 文件不存在 → {path}"
    if os.path.isdir(path):
        return False, f"❌ {desc}: 是目录不是文件 → {path}"
    if check_readable and not os.access(path, os.R_OK):
        return False, f"❌ {desc}: 无读取权限 → {path}"
    size = os.path.getsize(path)
    if size == 0:
        return False, f"❌ {desc}: 文件为空（0 字节）→ {path}"
    return True, ""

def detect_format(path, max_lines=3):
    """探测文件格式（peek 前 N 行）。返回 (format_hint, ncols, sample_lines)"""
    if path in ("-", "/dev/stdin"):
        return ("stdin", 0, [])
    try:
        with open(path, 'r', errors='replace') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                lines.append(line.rstrip('\n'))
    except Exception:
        return ("unknown", 0, [])
    if not lines:
        return ("empty", 0, [])
    # FASTA
    if lines[0].startswith('>'):
        return ("fasta", 0, lines)
    # GFF3
    if '\tgff3' in lines[0].lower() or '\tgff' in lines[0].lower():
        return ("gff3", len(lines[0].split('\t')), lines)
    # Newick
    if lines[0].startswith('(') or lines[0].endswith(';'):
        return ("newick", 0, lines)
    # MEME XML
    if '<' in lines[0] and '?' in lines[0]:
        return ("xml", 0, lines)
    # TSV/CSV
    delim = '\t' if '\t' in lines[0] else (',' if ',' in lines[0] else None)
    if delim:
        ncols = len(lines[0].split(delim))
        return ("tsv" if delim == '\t' else "csv", ncols, lines)
    return ("text", 0, lines)

def validate_format_cols(path, expected_cols, desc="输入文件"):
    """校验文件列数是否符合预期"""
    fmt, ncols, _ = detect_format(path)
    if ncols > 0 and expected_cols and ncols < expected_cols:
        return False, f"❌ {desc}: 需要 ≥{expected_cols} 列，实际 {ncols} 列（{fmt} 格式）→ {path}"
    return True, ""

# ---- 已知坑位提示 ----
PITFALL_HINTS = {
    "hclust": "输入必须是三列距离文件 GeneA\\tGeneB\\tdist（不是表达矩阵！）",
    "barplot": "termCol/pvalCol 用列名（如 Term/Pvalue），不是列索引数字",
    "cubeheatmap": "group 文件第一行会被当数据——喂前先去表头",
    "admixture": "第一个参数是 qFiles.lst（每行一个 Q 矩阵文件路径），不是 Q 矩阵内容",
    "dotplot": "--chrLayout 传文件路径（内容: Genome: Chr1 Chr2...），不是内联字符串",
    "microsyn": "必须指定 --chr1/--start1/--end1 和 --chr2/--start2/--end2；染色体名须数字",
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
    "annocompare": "输入两个 GFF3 + 输出目录；生成 change_summary.csv + figures/*",
    "onesteptree": "--bbTime ≥1000；序列须 ≥4 条唯一（太相似会被合并报错）",
    "nwAlign": "输入文件每行一条序列，无 FASTA 头（传 FASTA 会把 >s1 当序列）",
    "treeRooting": "Newick 树必须带枝长（裸 Newick 报 Corrupt NEWICK format）",
    "distance": "方法名小写 euclidean/pearson/pearsonDist；结果输出到 stdout（非文件）",
    "markertools": "结果输出到 stderr（非 stdout！）；$(...) 需 2>&1 捕获",
    "simplehmmscan": "需 Pfam-A.hmm 数据库；idList 每行一个 Pfam NAME（如 GRAS）",
}

def get_pitfall_hint(command_name):
    """获取已知坑位提示"""
    return PITFALL_HINTS.get(command_name, "")

# ---- 统一输出格式处理 ----
def resolve_output(output, fmt="svg", width=None, height=None):
    """处理输出文件路径 + 格式推断/覆盖 + 父目录提前校验"""
    if not output:
        # 无输出文件 → 生成默认文件名
        output = f"output.{fmt}"
    # 格式覆盖：如果指定了 --format，覆盖文件扩展名
    if fmt and fmt != "auto":
        base = os.path.splitext(output)[0]
        ext = os.path.splitext(output)[1].lstrip('.')
        # 只在用户显式指定 -f 时覆盖
        if fmt and fmt != ext:
            output = f"{base}.{fmt}"
    # 父目录提前校验（避免 Java 引擎里静默挂死/异常堆栈）
    out_dir = os.path.dirname(os.path.abspath(output))
    if not os.path.isdir(out_dir):
        click.echo(f"❌ 输出目录不存在: {out_dir}", err=True)
        click.echo(f"   创建: mkdir -p {out_dir}", err=True)
        sys.exit(1)
    # 已存在警告（不阻断，仅提示防覆盖）
    if os.path.isfile(output):
        import click as _click
        _click.echo(f"⚠️ 输出文件已存在将被覆盖: {output}", err=True)
    return output

# ---- _run_java wrapper（友好错误处理 + 智能异常分类 + 退出码规范 + 坑位提示）----
def run_java(java_args, verbose=False, quiet=False, command_name=None):
    """执行 Java 命令，失败时输出友好提示
    
    退出码: 0=成功, 1=参数错误, 2=文件不存在, 3=格式错误
    """
    err_file = tempfile.mktemp(prefix="tbtools_err.")
    import time as _time
    _t0 = _time.perf_counter()
    
    # 确保桥编译产物存在
    os.makedirs(BUILD_DIR, exist_ok=True)
    
    try:
        result = subprocess.run(
            java_args, stderr=open(err_file, "w"),
            stdout=None,  # stdout 直通
        )
        ec = result.returncode
    except FileNotFoundError:
        print("❌ Java 未安装或路径错误", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ 启动失败: {e}", file=sys.stderr)
        return 1
    
    if ec != 0:
        ec_out = ec
        # 错误处理
        err_text = open(err_file).read() if os.path.isfile(err_file) else ""
        print("", file=sys.stderr)
        print(f"❌ 执行失败（退出码 {ec}）", file=sys.stderr)
        
        # 提取异常关键行
        exc_lines = [l for l in err_text.splitlines() 
                     if re.match(r'^(Exception in thread|Caused by:|Error:|\[Error\])', l)]
        for line in exc_lines[:3]:
            print(f"   {line}", file=sys.stderr)
        
        if not exc_lines:
            nonblank = [l for l in err_text.splitlines() if l.strip()]
            for line in nonblank[-3:]:
                print(f"   {line}", file=sys.stderr)
        
        # 智能异常分类 + 退出码
        hint = "参数缺失/格式不对/文件路径错误/数据不匹配"
        ec_out = 1
        if "FileNotFoundException" in err_text:
            hint = "文件不存在或路径错误，检查输入文件路径"
            ec_out = 2
        elif "NullPointerException" in err_text:
            hint = "可能缺少必需参数或数据格式不匹配"
            ec_out = 1
        elif "NumberFormatException" in err_text:
            hint = "数据格式不匹配，检查输入文件列数/类型/分隔符"
            ec_out = 3
        elif "ArrayIndexOutOfBoundsException" in err_text:
            hint = "可能缺少必需参数或输入数据行列数不足"
            ec_out = 3
        elif "OutOfMemoryError" in err_text:
            hint = "内存不足，尝试 -Xmx4g 或更大堆内存"
            ec_out = 4
        
        print("", file=sys.stderr)
        print(f"   💡 {hint}", file=sys.stderr)
        
        # 坑位提示
        if command_name:
            pitfall = get_pitfall_hint(command_name)
            if pitfall:
                print(f"   ⚠️ 已知坑位: {pitfall}", file=sys.stderr)
        
        print(f"   📖 查看帮助: tbtools {command_name} --help" if command_name else "   📖 查看帮助: tbtools --help", file=sys.stderr)
        
        if verbose:
            print("   🔍 完整堆栈:", file=sys.stderr)
            print(err_text, file=sys.stderr)
        else:
            print(f"   🔍 完整堆栈: {err_file}（--verbose 显示，重启后清除）", file=sys.stderr)
        
        print("", file=sys.stderr)
    else:
        # 成功时输出进度信息（quiet 模式跳过）
        if not quiet and os.path.isfile(err_file):
            sys.stderr.write(open(err_file).read())
        # 耗时统计（quiet 模式跳过）
        if not quiet:
            _dt = _time.perf_counter() - _t0
            sys.stderr.write(f"⏱ 耗时 {_dt:.1f}s ({command_name})\n")
    
    try:
        os.unlink(err_file)
    except:
        pass
    
    # 成功时 ec_out = 0
    if ec == 0:
        ec_out = 0
    return ec_out

# ---- 桥编译 ----
def ensure_bridge(bridge_name):
    """确保桥 Java 文件已编译到 build/ 目录"""
    src = os.path.join(BRIDGES_DIR, f"{bridge_name}.java")
    dst = os.path.join(BUILD_DIR, f"{bridge_name}.java")
    
    # 同步源码到 build/
    if os.path.isfile(src):
        need_copy = (not os.path.isfile(dst) 
                     or os.path.getmtime(src) > os.path.getmtime(dst))
        if need_copy:
            shutil.copy2(src, dst)
    
    # 编译（如果 .class 不存在或源码更新）
    cls_file = os.path.join(BUILD_DIR, f"{bridge_name}.class")
    if not os.path.isfile(cls_file) or (
        os.path.isfile(dst) and os.path.getmtime(dst) > os.path.getmtime(cls_file)
    ):
        subprocess.run(
            ["javac", "-cp", JAR, dst],
            capture_output=True, cwd=BUILD_DIR
        )

# ---- xvfb-run 包装 ----
def run_plot(java_args, verbose=False, quiet=False, use_xvfb=True, command_name=None):
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
