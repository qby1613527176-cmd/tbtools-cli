"""tbtools-cli 核心引擎：通用选项 + _run_java wrapper + 统一输出格式 + 输入校验"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

import click

# ---- 平台常量（Windows 主战场：classpath 分隔符；Linux/WSL 用 :）----
CP_SEP = ";" if os.name == "nt" else ":"
def cp(*parts):
    """平台安全的 classpath 拼接（Windows ; / POSIX :）"""
    return CP_SEP.join(p for p in parts if p)

def stdout_path():
    """标准输出占位路径：POSIX /dev/stdout；Windows 用 CON（模式受限时回退临时文件）"""
    return "/dev/stdout" if os.name != "nt" else "CON"

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
    # 常见路径 + Windows/WSL/macOS 路径
    for cand in [
        os.path.expanduser("~/tbtools-cli/lib/TBtools_JRE1.6.jar"),
        os.path.expanduser("~/TBtools/TBtools_JRE1.6.jar"),
        os.path.expanduser("~/Downloads/TBtools_JRE1.6.jar"),
        os.path.expanduser("~/下载/TBtools_JRE1.6.jar"),
        os.path.expanduser("~/Desktop/TBtools_JRE1.6.jar"),
        os.path.expanduser("~/桌面/TBtools_JRE1.6.jar"),
        "/opt/TBtools/TBtools_JRE1.6.jar",
        "/usr/local/lib/TBtools_JRE1.6.jar",
        # Windows 原生路径（git-bash / cmd 环境）
        "C:/TBtools/TBtools_JRE1.6.jar",
        "C:/Program Files/TBtools/TBtools_JRE1.6.jar",
        "C:/Users/%s/Downloads/TBtools_JRE1.6.jar" % os.environ.get("USERNAME", ""),
        # WSL 挂载 Win 盘
        "/mnt/c/TBtools/TBtools_JRE1.6.jar",
        "/mnt/c/Program Files/TBtools/TBtools_JRE1.6.jar",
        "/mnt/d/TBtools/TBtools_JRE1.6.jar",
        "/mnt/c/Users/*/Downloads/TBtools_JRE1.6.jar",
        "/mnt/c/Users/*/Desktop/TBtools_JRE1.6.jar",
        # macOS
        "/Applications/TBtools/TBtools_JRE1.6.jar",
        os.path.expanduser("~/Applications/TBtools/TBtools_JRE1.6.jar"),
    ]:
        if os.path.isfile(cand):
            return cand
    return jar  # 返回空或原始值（让下游报错）


def find_jar_deep():
    """全盘深搜 TBtools jar（限定常见挂载点 + 递归 glob）。

    外部审查反馈（2026-09-20）：原 get_jar 在模块导入期执行递归全盘
    glob（/mnt/*/TBtools*/**/...），无 jar 机器每次起 CLI 都白扫一遍。
    现改为独立函数，仅 doctor / setup --auto 显式调用。
    """
    import glob
    for pat in [
        "/mnt/*/TBtools*/**/TBtools_JRE1.6.jar",
        "/mnt/*/Users/*/Downloads/TBtools*.jar",
        "/mnt/*/Users/*/Desktop/TBtools*.jar",
        "/mnt/c/Users/*/Downloads/TBtools*.jar",
        "/mnt/c/Users/*/Desktop/TBtools*.jar",
    ]:
        try:
            hits = sorted(glob.glob(pat, recursive=True))
        except Exception:
            continue
        if hits and os.path.isfile(hits[0]):
            return hits[0]
    return ""

JAR = get_jar()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGES_DIR = os.path.join(ROOT, "bridges")
BUILD_DIR = os.path.join(ROOT, "build")

# ---- 输入校验 ----
def validate_file(path: str, desc: str = "输入文件", check_readable: bool = True) -> tuple[bool, str]:
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

def detect_format(path: str, max_lines: int = 3) -> tuple[str, int, list[str]]:
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
    except Exception as e:
        import logging; logging.getLogger(__name__).debug("detect_format %s: %s", path, e)
        return ("unknown", 0, [])
    if not lines:
        return ("empty", 0, [])
    # FASTA
    if lines[0].startswith('>'):
        return ("fasta", 0, lines)
    # GFF3（N16: 含 ##gff-version 头或特征列 gene/mRNA 的均判 GFF3，此前误判 text）
    if lines[0].startswith('##gff-version') or '\tgene\t' in lines[0] or '\tmRNA\t' in lines[0]:
        return ("gff3", len(lines[0].split('\t')), lines)
    # GFF3（旧判定保留）
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

# ---- C2: 早期格式不匹配警告 ----
# 命令 → (期望格式, 最少列数, 人类描述)。仅高置信场景，警告不阻断。
EXPECTED_INPUT_FORMATS = {
    "hclust":    ("tsv", 3, "三列距离文件 GeneA\tGeneB\tdist"),
    "volcano":   ("tsv", 3, "DEG 表（ID\tlog2FC\tP值...）"),
    "heatmap":   ("tsv", 2, "表达矩阵（基因×样本）"),
    "pca":       ("tsv", 2, "表达矩阵（基因×样本，行=观测）"),
    "msa":       ("fasta", 0, "多序列比对 FASTA"),
    "logo":      ("fasta", 0, "比对 FASTA"),
    "motif":     ("xml", 0, "MEME XML"),
    "structure": ("gff3", 9, "GFF3 注释"),
    "tree":      ("newick", 0, "Newick 树文件"),
    "barplot":   ("tsv", 2, "富集表（term\tP值...）"),
}

def check_input_format(cmd_name: str, path: str) -> None:
    """早期格式检测：期望格式与实际不符时返回警告文本（不阻断）"""
    exp = EXPECTED_INPUT_FORMATS.get(cmd_name)
    if not exp:
        return None
    exp_fmt, min_cols, desc = exp
    fmt, ncols, _ = detect_format(path)
    if fmt in ("unknown", "empty", "stdin"):
        return None
    if exp_fmt == "fasta" and fmt != "fasta":
        return f"输入文件看起来是 {fmt}，但 {cmd_name} 通常需要 FASTA（{desc}）"
    if exp_fmt == "newick" and fmt != "newick":
        return f"输入文件看起来是 {fmt}，但 {cmd_name} 需要 Newick 树文件（{desc}）"
    if exp_fmt == "xml" and fmt != "xml":
        return f"输入文件看起来是 {fmt}，但 {cmd_name} 需要 XML（{desc}）"
    if exp_fmt == "gff3" and fmt != "gff3":
        return f"输入文件看起来是 {fmt}，但 {cmd_name} 需要 GFF3（{desc}）"
    if exp_fmt == "tsv" and fmt not in ("tsv", "csv"):
        return f"输入文件看起来是 {fmt}，但 {cmd_name} 需要表格（{desc}）"
    if exp_fmt == "tsv" and min_cols and ncols and ncols < min_cols:
        return f"输入文件只有 {ncols} 列，{cmd_name} 通常需要 ≥{min_cols} 列（{desc}）"
    return None

# ---- 已知坑位提示 ----
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

def get_pitfall_hint(command_name: str) -> str | None:
    """获取已知坑位提示"""
    return PITFALL_HINTS.get(command_name, "")

# ---- 统一输出格式处理 ----
def resolve_output(output: str, fmt: str = "svg", width: int | None = None, height: int | None = None) -> tuple[str, str]:
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

# ---- P0 输入保护（N19/N23/N25/N37：引擎在用户输入上建库/清洗/写穿，系统性防御）----
# 副作用文件模式（引擎在输入旁落 *.TBtools.fa* 索引 / *.TBtoolsDB.* BLAST 库 / 清洗中间文件）
_SIDE_EFFECT_RE = re.compile(
    r'(\.TBtools\.(fa|fai|gp|highGC)$|\.TBtoolsDB\.|\.tmpClean$|\.sortedGXF$|'
    r'\.subjectSubset$|\.subJog\.|\.splitLines\.txt$|\.link\.dmnd$|\.s2s(\.finished)?$)',
    re.IGNORECASE)
# 参数名含 out/output/prefix/graph/dir/report → 值是输出路径，不纳入输入快照
_OUT_FLAG_RE = re.compile(
    r'^(--?)?(out|output|prefix|graph|dir|report)(file|path|fa|fq|tab|table|gff|gff3|gtf|txt|xml|xls|svg|png|pdf|nwk|pre|dir|put)*$',
    re.IGNORECASE)
_MAX_SNAPSHOT_COPY = 50 * 1024 * 1024  # >50MB 只记 (size, mtime)，不复制（无法恢复，只报警）

def _sha1_file(f):
    h = hashlib.sha1()
    with open(f, "rb") as fh:
        for _chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(_chunk)
    return h.hexdigest()

def snapshot_inputs(java_args: list) -> list:
    """识别 java_args 中的输入文件并快照。

    返回 [(path, backup|None, size, mtime)]；
    规则：跳过执行器/-cp/-D/-X/-jar 值、跳过输出型参数名（_OUT_FLAG_RE）、
    跳过 .jar/.class 与空文件。
    """
    snaps = []
    tmpdir = None
    prev = None
    for _i, _a in enumerate(java_args):
        if _i == 0 or not isinstance(_a, str):
            continue
        if _a in ("-cp", "-classpath", "-jar") or _a.startswith(("-D", "-X", "-J", "--module-path")):
            prev = _a if not _a.startswith("-") else None
            continue
        if _a.startswith("-"):
            prev = _a
            continue
        # _a 是参数值
        flag = prev
        prev = None
        if flag and (_OUT_FLAG_RE.search(flag) or flag in ("-cp", "-classpath", "-jar", "-o")):
            continue
        if not os.path.isfile(_a):
            continue
        if _a.endswith((".jar", ".class")):
            continue
        try:
            size = os.path.getsize(_a)
            mtime = os.path.getmtime(_a)
        except OSError:
            continue
        if size == 0:
            continue
        backup = None
        if size <= _MAX_SNAPSHOT_COPY:
            if tmpdir is None:
                tmpdir = tempfile.mkdtemp(prefix="tbtools_inp.")
            backup = os.path.join(tmpdir, f"inp_{len(snaps)}_{os.path.basename(_a)}")
            try:
                shutil.copy2(_a, backup)
            except Exception:
                backup = None
        snaps.append([_a, backup, size, mtime])
    return snaps

def verify_and_restore(snaps: list) -> list:
    """调用后比对快照；被引擎改写的输入自动恢复。返回问题清单 [(path, 状态)]。"""
    problems = []
    for path, backup, size, mtime in snaps:
        if not os.path.isfile(path):
            problems.append((path, "missing"))
            continue
        if backup and os.path.isfile(backup):
            try:
                if _sha1_file(path) != _sha1_file(backup):
                    shutil.copy2(backup, path)
                    problems.append((path, "modified-restored"))
            except Exception:
                problems.append((path, "verify-error"))
        else:
            try:
                if (os.path.getsize(path), os.path.getmtime(path)) != (size, mtime):
                    problems.append((path, "modified-no-backup"))
            except OSError:
                problems.append((path, "verify-error"))
    return problems

def cleanup_side_effects(t0: float) -> list:
    """删除 CWD 下本次调用新产生的 TBtools 副作用文件（N37 族），返回删除数。"""
    try:
        cwd = os.getcwd()
        names = os.listdir(cwd)
    except Exception:
        return 0
    n = 0
    for fn in names:
        if not _SIDE_EFFECT_RE.search(fn):
            continue
        fp = os.path.join(cwd, fn)
        try:
            if os.path.isfile(fp) and os.path.getmtime(fp) >= t0 - 2:
                os.unlink(fp)
                n += 1
        except Exception:
            pass
    return n

# 强输出参数名：调用成功后对应文件必须存在（N30：长路径/引擎静默跳过兜底）
_STRONG_OUT_RE = re.compile(
    r'^(--)?(outPutFile|outFile|outTable|outTab|outFa|outFq|outGff|outGff3|outGtf|'
    r'outTxt|outXml|outXls|outSvg|outPng|outPdf|outNwk|outGraph|outORFs|outImg)$',
    re.IGNORECASE)

def check_missing_outputs(java_args: list) -> list:
    """调用成功后检查强输出参数对应文件是否生成。返回缺失列表。"""
    missing = []
    prev = None
    for _i, _a in enumerate(java_args):
        if _a.startswith("--") or (prev is None and _i > 0):
            if _a.startswith("--"):
                prev = _a
            continue
        # _a 是值
        if prev and _STRONG_OUT_RE.match(prev):
            if _a and not _a.startswith("-") and _a not in ("/dev/stdout", "CON", "stdout"):
                if not os.path.isfile(_a):
                    missing.append(_a)
        prev = None
    return missing

def find_empty_inputs(java_args):
    """N10/N11: 识别 java_args 中的空输入文件（非输出参数值、存在但 0 字节）。"""
    empties = []
    prev = None
    for _i, _a in enumerate(java_args):
        if _i == 0 or not isinstance(_a, str):
            continue
        if _a in ("-cp", "-classpath", "-jar") or _a.startswith(("-D", "-X", "-J")):
            prev = None
            continue
        if _a.startswith("-"):
            prev = _a
            continue
        flag = prev
        prev = None
        if flag and (_OUT_FLAG_RE.search(flag) or flag in ("-cp", "-classpath", "-jar", "-o")):
            continue
        if os.path.isfile(_a) and os.path.getsize(_a) == 0:
            empties.append(_a)
    return empties

# ---- _run_java wrapper（友好错误处理 + 智能异常分类 + 退出码规范 + 坑位提示）----
def run_java(java_args: list, verbose: bool = False, quiet: bool = False, command_name: str | None = None) -> int:
    """执行 Java 命令，失败时输出友好提示
    
    退出码: 0=成功, 1=参数错误, 2=文件不存在, 3=格式错误
    P0 保护：调用前快照输入，调用后恢复被改写输入 + 清理副作用文件。
    """
    err_file = tempfile.mktemp(prefix="tbtools_err.")
    import time as _time
    _t0 = _time.perf_counter()
    
    # 确保桥编译产物存在
    os.makedirs(BUILD_DIR, exist_ok=True)
    
    # ── N1: 解析 java 绝对路径（不依赖 PATH；找不到时给可操作指引）──
    if java_args and java_args[0] in ("java", "java.exe"):
        _java_bin = get_java()
        if not _java_bin:
            print("❌ 未找到 java 可执行文件。可操作指引：", file=sys.stderr)
            print("   ① 安装 JDK/JRE（如 apt install default-jdk）", file=sys.stderr)
            print("   ② 或 export PATH 使其包含 java", file=sys.stderr)
            print("   ③ 或设置 TBTOOLS_JAVA 环境变量指向 java 可执行文件", file=sys.stderr)
            return 1
        java_args = list(java_args)
        java_args[0] = _java_bin
    
    # ── N19 特判：FindBestHomologyBatch 引擎把结果写进 queryFasta 而非 outTable ──
    # 包装：query 重定向到临时副本（引擎写穿副本），调用后仅当副本被引擎改写（sha1 变）
    # 才把副本搬到 --outTable 目标；未改写=引擎未产出（参数拒认），不搬并报错。
    n19_tmp = n19_out = n19_orig_sha = None
    if command_name == "findBestHomologyBatch":
        qidx = oidx = None
        for _i, _a in enumerate(java_args):
            if _a == "--queryFasta":
                qidx = _i
            elif _a == "--outTable":
                oidx = _i
        if qidx is not None and qidx + 1 < len(java_args) and os.path.isfile(java_args[qidx + 1]):
            n19_tmp = tempfile.mktemp(prefix="tbq.", suffix=".fa", dir=os.path.dirname(os.path.abspath(java_args[qidx + 1])) or None)
            try:
                shutil.copy2(java_args[qidx + 1], n19_tmp)
                n19_orig_sha = _sha1_file(n19_tmp)
                java_args = list(java_args)
                java_args[qidx + 1] = n19_tmp
                n19_out = java_args[oidx + 1] if (oidx is not None and oidx + 1 < len(java_args)) else None
            except Exception:
                n19_tmp = None
    
    # ── P0：输入快照（在原 java_args 上做，含 query 原文件，兜底验证）──
    snaps = snapshot_inputs(java_args)
    _wall_t0 = _time.time()
    # N10/N11: 空输入文件友好报错（引擎对 0 字节文件裸崩：statFasta/heatmap 等）
    _empties = find_empty_inputs(java_args)
    if _empties:
        for _e in _empties:
            print(f"❌ 输入文件为空（0 字节）: {_e}", file=sys.stderr)
        print("   💡 数据可能未生成或路径指向了空文件", file=sys.stderr)
        return 3
    
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
    
    # ── P0：输入保护（无论成败都执行）──
    _problems = verify_and_restore(snaps)
    _clean_n = cleanup_side_effects(_wall_t0)
    if _problems:
        print(file=sys.stderr)
        print("⚠️ 输入保护：检测到引擎修改/删除了输入文件，已自动恢复：", file=sys.stderr)
        for _p, _st in _problems:
            print(f"   {_p} [{_st}]", file=sys.stderr)
    if _clean_n:
        print(f"⚠️ 已清理引擎副作用文件 {_clean_n} 个（临时索引/建库残留）", file=sys.stderr)
    
    # ── N19：仅当引擎改写了临时副本时才把结果搬到 outTable ──
    if n19_tmp:
        try:
            _modified = (os.path.isfile(n19_tmp) and os.path.getsize(n19_tmp) > 0
                         and _sha1_file(n19_tmp) != n19_orig_sha)
            if _modified:
                if n19_out:
                    _od = os.path.dirname(os.path.abspath(n19_out))
                    if _od:
                        os.makedirs(_od, exist_ok=True)
                    shutil.copy2(n19_tmp, n19_out)
                    print(f"✅ findBestHomologyBatch 结果已写入: {n19_out}", file=sys.stderr)
                else:
                    print(f"⚠️ findBestHomologyBatch 未指定 --outTable，结果留在: {n19_tmp}", file=sys.stderr)
            os.unlink(n19_tmp)
        except Exception as _e:
            print(f"⚠️ findBestHomologyBatch 结果搬移失败: {_e}", file=sys.stderr)
    
    if ec != 0:
        ec_out = ec
        # 错误处理
        err_text = open(err_file).read() if os.path.isfile(err_file) else ""
        print(file=sys.stderr)
        print(f"❌ 执行失败（退出码 {ec}）", file=sys.stderr)
        
        # 提取异常关键行
        exc_lines = [ln for ln in err_text.splitlines()
                     if re.match(r'^(Exception in thread|Caused by:|Error:|\[Error\])', ln)]
        for line in exc_lines[:3]:
            print(f"   {line}", file=sys.stderr)
        
        if not exc_lines:
            nonblank = [ln for ln in err_text.splitlines() if ln.strip()]
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
        
        print(file=sys.stderr)
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
        
        print(file=sys.stderr)
    else:
        # 成功时输出进度信息（quiet 模式跳过）
        if not quiet and os.path.isfile(err_file):
            sys.stderr.write(open(err_file).read())
        # N30: 输出存在性校验（声明了强输出但未生成 → 报错，避免长路径/静默失败）
        _missing_out = check_missing_outputs(java_args)
        if _missing_out:
            print("⚠️ 声明了输出但未检测到生成文件（路径过长或引擎静默跳过）:", file=sys.stderr)
            for _o in _missing_out:
                print(f"   {_o}", file=sys.stderr)
            if ec_out == 0:
                ec_out = 1
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

def get_java() -> str | None:
    """定位 java 可执行文件（N1：tool 层 PATH 依赖误导报错）。

    优先级: TBTOOLS_JAVA 环境变量 > PATH 搜索 > 常见位置。
    Windows 下 Python 运行时注入 PATH 对 CreateProcess 无效（交付包实测），
    所以调用前必须解析出绝对路径而非依赖 PATH。
    """
    j = os.environ.get("TBTOOLS_JAVA", "")
    if j and os.path.isfile(j):
        return j
    w = shutil.which("java")
    if w:
        return w
    for cand in (
        "/usr/bin/java", "/usr/local/bin/java", "/opt/java/bin/java",
        os.path.expanduser("~/jdk*/bin/java"),
        "C:/Program Files/TBtools/jre/bin/java.exe",
        "C:/Program Files/Java/*/bin/java.exe",
        "/mnt/c/Program Files/TBtools/jre/bin/java.exe",
        "/mnt/c/Program Files/Java/*/bin/java.exe",
        "/Applications/TBtools/jre/bin/java",
    ):
        import glob as _glob
        hits = _glob.glob(cand)
        for h in hits:
            if os.path.isfile(h):
                return h
    return ""


# ---- 桥编译 ----
def ensure_bridge(bridge_name: str) -> str | None:
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
        # 外部审查反馈: javac 编译错误不再静默吞掉（此前 capture_output 丢 stderr）
        if _r.returncode != 0:
            _err = _r.stderr.decode("utf-8", "replace") if _r.stderr else ""
            print(f"⚠️ 桥编译失败 {bridge_name}:\n{_err[-800:]}", file=sys.stderr)

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
    dead = {}
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
