"""环境发现(core.py 拆分): JAR/ROOT/BRIDGES/CLASSPATH/get_java/工具函数。"""
import os
import shutil
import sys
import tempfile


CP_SEP = ";" if os.name == "nt" else ":"


def safe_temp(prefix="tmp.", suffix="", dir=None, text=True):
    """mkstemp 封装(替代有竞态的 tempfile.mktemp, 第六轮评审): 返回已关 fd 的路径"""
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=dir, text=text)
    os.close(fd)
    return path
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
# runtime/env.py 在 tbtools_cli/runtime/ 下, 项目根需上三级(core.py 拆分修正)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SRC_BRIDGES = os.path.join(ROOT, "bridges")
if os.path.isdir(_SRC_BRIDGES):
    BRIDGES_DIR: str = _SRC_BRIDGES
elif os.path.isdir(os.path.join(os.path.dirname(__file__), "bridges")):
    BRIDGES_DIR = os.path.join(os.path.dirname(__file__), "bridges")
elif os.path.isdir(os.path.join(sys.prefix, "tbtools_cli", "bridges")):
    BRIDGES_DIR = os.path.join(sys.prefix, "tbtools_cli", "bridges")
else:
    BRIDGES_DIR = ""  # 空串约定(同 JAR): 桥命令会报未配置
# bridges 位置: 源码环境 ROOT/bridges;pip data-files 装到 sys.prefix/tbtools_cli/bridges(实测);包内路径兜底
_SRC_BUILD = os.path.join(ROOT, "build")
BUILD_DIR = _SRC_BUILD if (os.path.isdir(_SRC_BUILD) or os.access(ROOT, os.W_OK)) else     os.path.join(os.path.expanduser("~/.cache/tbtools-cli/build"))

# ---- 输入校验 ----

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