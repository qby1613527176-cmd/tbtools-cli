"""tbtools-cli 核心引擎：通用选项 + _run_java wrapper + 统一输出格式"""
import subprocess, tempfile, os, sys, re, shutil

# ---- 配置 ----
def get_jar():
    jar = os.environ.get("TBTOOLS_JAR", "")
    if jar and os.path.isfile(jar):
        return jar
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

# ---- 统一输出格式处理 ----
def resolve_output(output, fmt="svg", width=None, height=None):
    """处理输出文件路径 + 格式推断/覆盖"""
    if not output:
        # 无输出文件 → 生成默认文件名
        output = f"output.{fmt}"
    # 格式覆盖：如果指定了 --format，覆盖文件扩展名
    if fmt and fmt != "auto":
        base = os.path.splitext(output)[0]
        output = f"{base}.{fmt}"
    return output

# ---- _run_java wrapper（友好错误处理 + 智能异常分类 + 退出码规范）----
def run_java(java_args, verbose=False, quiet=False):
    """执行 Java 命令，失败时输出友好提示
    
    退出码: 0=成功, 1=参数错误, 2=文件不存在, 3=格式错误
    """
    err_file = tempfile.mktemp(prefix="tbtools_err.")
    
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
        
        print("", file=sys.stderr)
        print(f"   💡 {hint}", file=sys.stderr)
        print(f"   📖 查看帮助: tbtools help <命令>", file=sys.stderr)
        
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
def run_plot(java_args, verbose=False, quiet=False, use_xvfb=True):
    """执行绘图引擎（需要 xvfb-run）"""
    if use_xvfb and shutil.which("xvfb-run"):
        full_args = ["xvfb-run", "-a"] + java_args
    else:
        full_args = java_args
    return run_java(full_args, verbose=verbose, quiet=quiet)
