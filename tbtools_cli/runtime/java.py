"""Java 执行运行时(core.py 拆分, GPT 评审 #8): run_java + 输入保护 + provenance + 输出解析。

自 2026-09 重构: 从 core.py 迁出。依赖 core 的 i18n(_)/环境(JAR/BUILD_DIR)/工具函数——
core 在文件末尾重导出本模块, 因此本模块可安全 `from tbtools_cli.core import ...`(core 已加载完)。
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

import click

from tbtools_cli.core import (
    BUILD_DIR,
    _,
    get_default,   # heap 可配置
    get_java,
    get_pitfall_hint,
    safe_temp,
)
from tbtools_cli.errors import ERROR_CODES, classify_error

def resolve_output(output: str, fmt: str = "svg", width: int | None = None, height: int | None = None) -> str:
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
    snaps: list = []
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

def verify_and_restore(snaps: list) -> list[tuple[str, str]]:
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

def cleanup_side_effects(t0: float) -> int:
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

# ── Error Code Registry(GLM 评审: 结构化错误契约, AI 可编程处理)──
def _n19_move_result(n19_tmp, n19_out, n19_orig_sha):
    """N19: findBestHomologyBatch 引擎改写了临时副本时才搬结果到 outTable。
    独立函数(第六轮评审: 引擎特判不寄生在 run_java 主干,便于单独测试)。"""
    if not n19_tmp:
        return
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


def _security_check_generic(java_args: list, command_name: str | None = None) -> str | None:
    """execution policy(评审 #34/#35): engine reflection(GenericCli 任意类)安全门。

    config.toml [security] allow_engine_reflection = false 时拒绝**裸反射命令**(generic——
    用户直接传任意类名)。普通命令(volcano 等 bridge 固定类名)不受影响。
    返回 None=放行; 返回错误消息=拒绝。
    """
    if command_name != "generic":
        return None
    try:
        from tbtools_cli.config import load_config
        sec = load_config().get("security", {})
        allow = sec.get("allow_engine_reflection", True)
    except Exception:
        allow = True
    if allow is False or str(allow).lower() in ("false", "0", "no"):
        cls = java_args[java_args.index("GenericCli") + 1] if "GenericCli" in java_args and java_args.index("GenericCli") + 1 < len(java_args) else "?"
        return f"🚫 engine reflection 被 config.toml [security] allow_engine_reflection=false 拒绝(类: {cls})"
    return None


def run_java(java_args: list, verbose: bool = False, quiet: bool = False, command_name: str | None = None) -> int:
    _sec = _security_check_generic(java_args, command_name)
    if _sec:
        click.echo(_sec, err=True)
        return 5  # POLICY_ERROR(engine reflection 被 config.toml [security] 拒绝)
    ec_out = 0
    # 堆内存可配置(第六轮评审: 注册表 -Xmx 硬编码,低配机器直接 OOM):
    # config.toml [defaults] memory = "2g" 全局覆盖;未配置保持注册表值
    _mem = get_default("memory")
    if _mem and any(a.startswith("-Xmx") for a in java_args):
        java_args = [f"-Xmx{_mem}" if a.startswith("-Xmx") else a for a in java_args]
    """执行 Java 命令，失败时输出友好提示
    
    退出码: 0=成功, 1=参数错误, 2=文件不存在, 3=格式错误
    P0 保护：调用前快照输入，调用后恢复被改写输入 + 清理副作用文件。
    """
    err_file = safe_temp(prefix="tbtools_err.")
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
            n19_tmp = safe_temp(prefix="tbq.", suffix=".fa", dir=os.path.dirname(os.path.abspath(java_args[qidx + 1])) or None)
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
            print(_("❌ 输入文件为空（0 字节）: {e}", "❌ Input file is empty (0 bytes): {e}").format(e=_e), file=sys.stderr)
        print(_("   💡 数据可能未生成或路径指向了空文件",
                "   💡 Data may not have been generated, or the path points to an empty file"), file=sys.stderr)
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
        print(_("⚠️ 输入保护：检测到引擎修改/删除了输入文件，已自动恢复：",
                 "⚠️ Input protection: engine modified/deleted input files — auto-restored:"), file=sys.stderr)
        for _p, _st in _problems:
            print(f"   {_p} [{_st}]", file=sys.stderr)
    if _clean_n:
        print(_("⚠️ 已清理引擎副作用文件 {n} 个（临时索引/建库残留）",
                 "⚠️ Cleaned up {n} engine side-effect files (temp index/db residue)").format(n=_clean_n), file=sys.stderr)
    
    # ── N19：仅当引擎改写了临时副本时才把结果搬到 outTable（独立 hook 函数）──
    _n19_move_result(n19_tmp, n19_out, n19_orig_sha)
    
    if ec != 0:
        ec_out = ec
        # 错误处理
        err_text = open(err_file).read() if os.path.isfile(err_file) else ""
        print(file=sys.stderr)
        print(_("❌ 执行失败（退出码 {ec}）", "❌ Execution failed (exit code {ec})").format(ec=ec), file=sys.stderr)
        
        # 提取异常关键行
        exc_lines = [ln for ln in err_text.splitlines()
                     if re.match(r'^(Exception in thread|Caused by:|Error:|\[Error\])', ln)]
        for line in exc_lines[:3]:
            print(f"   {line}", file=sys.stderr)
        
        if not exc_lines:
            nonblank = [ln for ln in err_text.splitlines() if ln.strip()]
            for line in nonblank[-3:]:
                print(f"   {line}", file=sys.stderr)
        
        # 智能异常分类 + 错误码(结构化错误契约: code/exit/retryable 供 AI 处理)
        _code, ec_out_from_code, _hint_zh = classify_error(err_text)
        _err_meta = ERROR_CODES.get(_code, ERROR_CODES["TB001_INVALID_ARGUMENT"])
        ec_out = ec_out_from_code
        hint = _(_hint_zh, str(_err_meta["action"]))
        
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
    # 运行 provenance: 识别输出文件, 旁写 <out>.tbtools.json(成功/失败都写, 含结构化 error)
    _write_provenance(java_args, command_name, ec_out, err_text if ec_out != 0 else "")
    return ec_out


def _write_provenance(java_args, command_name, ec, err_text=""):
    """运行记录旁文件: <输出>.tbtools.json(命令/版本/参数/输入 sha/时间/错误)。

    成功(ec==0)与失败(ec!=0, 含结构化 error)都写;失败不影响主流程。
    """
    if command_name is None:
        return
    # 输出识别: 反向第一个图形参数即视为输出(重跑时文件已存在也当输出), 排除选项
    out = None
    for a in reversed(java_args):
        if a.endswith((".svg", ".png", ".pdf")) and not a.startswith("-"):
            out = a
            break
    if not out or not os.path.isdir(os.path.dirname(os.path.abspath(out))):
        return
    try:
        import json as _json
        import hashlib as _hl
        import time as _tm
        from tbtools_cli import __version__ as _pkg_ver
        inputs = [a for a in java_args
                  if os.path.isfile(a) and not a.startswith("-")
                  and a != out and not a.endswith((".jar", ".class", ".svg", ".png", ".pdf"))]
        _code, _ec, _hint = classify_error(err_text) if ec != 0 else ("TB000_OK", 0, "")
        prov = {
            "command": command_name,
            "invocation": " ".join(java_args[:8]) + (" ..." if len(java_args) > 8 else ""),
            "tbtools_cli": _pkg_ver,
            "exit_code": ec,
            "error": None if ec == 0 else {
                "code": _code,
                "retryable": ERROR_CODES.get(_code, {}).get("retryable", False),
                "suggested_action": ERROR_CODES.get(_code, {}).get("action", ""),
            },
            "outputs": [out],
            "inputs": [{"path": i, "sha256": _hl.sha256(open(i, "rb").read()).hexdigest()[:16]} for i in inputs[:10]],
            "timestamp": _tm.strftime("%Y-%m-%dT%H:%M:%S"),
            "java_args_count": len(java_args),
        }
        with open(out + ".tbtools.json", "w", encoding="utf-8") as f:
            _json.dump(prov, f, ensure_ascii=False, indent=1)
    except Exception:
        pass  # provenance 是附加信息, 失败不影响命令

