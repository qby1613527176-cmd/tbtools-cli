"""输入校验(core.py 拆分): 文件检查/格式探测/列数校验。"""
import os


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
    if lines[0].lstrip().startswith('<?xml'):  # 收紧: 仅真 XML 声明(评审: 含<和?的任何文本误判)
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

def check_input_format(cmd_name: str, path: str) -> str | None:
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
