"""结构化错误契约(GLM 评审): 错误码注册表 + 异常分类。

独立模块(零依赖), 供 core/运行时/CLI 复用。
"""
from __future__ import annotations

# ── Error Code Registry(GLM 评审: 结构化错误契约, AI 可编程处理)──
ERROR_CODES: dict[str, dict[str, object]] = {
    "TB001_INVALID_ARGUMENT":   {"exit": 1, "retryable": False, "action": "check argument names/values, see --help"},
    "TB002_FILE_NOT_FOUND":     {"exit": 2, "retryable": False, "action": "check the input file path exists"},
    "TB003_INPUT_FORMAT_ERROR": {"exit": 3, "retryable": False, "action": "check input format/columns/separator"},
    "TB004_INPUT_SCHEMA_ERROR": {"exit": 3, "retryable": False, "action": "input does not match required schema"},
    "TB005_DEPENDENCY_MISSING": {"exit": 1, "retryable": False, "action": "install missing dependency (see doctor)"},
    "TB007_TOOL_TIMEOUT":       {"exit": 1, "retryable": True,  "action": "retry with more time or smaller input"},
    "TB008_OUT_OF_MEMORY":      {"exit": 4, "retryable": True,  "action": "increase memory in config.toml [defaults]"},
    "TB009_ENGINE_CRASH":       {"exit": 1, "retryable": False, "action": "engine-level defect; see PITFALL/docs"},
    "TB010_OUTPUT_MISSING":     {"exit": 1, "retryable": False, "action": "output not produced; check engine"},
    "TB012_INTERNAL_ERROR":     {"exit": 1, "retryable": False, "action": "wrapper bug; report with --verbose"},
}


def classify_error(err_text: str) -> tuple[str, int, str]:
    """异常文本 → (错误码, 退出码, hint)。退出码与现分类一致(0/2/3/4... 语义化)。"""
    if "FileNotFoundException" in err_text:
        return "TB002_FILE_NOT_FOUND", 2, "文件不存在或路径错误，检查输入文件路径"
    if "ClassNotFoundException" in err_text:
        return "TB009_ENGINE_CRASH", 1, "引擎类不存在(版本不匹配或死命令)"
    if "NumberFormatException" in err_text:
        return "TB003_INPUT_FORMAT_ERROR", 3, "数据格式不匹配，检查列数/类型/分隔符"
    if "ArrayIndexOutOfBoundsException" in err_text:
        return "TB003_INPUT_FORMAT_ERROR", 3, "行列数不足或参数缺省"
    if "OutOfMemoryError" in err_text:
        return "TB008_OUT_OF_MEMORY", 4, "内存不足: config.toml [defaults] memory 调大"
    if "NullPointerException" in err_text:
        return "TB001_INVALID_ARGUMENT", 1, "可能缺少必需参数或格式不匹配"
    if "NoClassDefFoundError|DatatypeConverter" in err_text:
        return "TB005_DEPENDENCY_MISSING", 1, "缺 javax.xml 类(ensure_bridge 应已编译 fake DatatypeConverter)"
    return "TB001_INVALID_ARGUMENT", 1, "参数缺失/格式不对/路径错误/数据不匹配"
