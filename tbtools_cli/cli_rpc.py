"""cli_rpc.py — RPC 服务器管理（架构重构批次 B：从 cli.py 拆分）

rpc 分组 + N34/N35 自愈基础设施（pid 文件/健康探针/自动拉起）+ N38 错误兜底。
由 cli.py 以 `cli_rpc.build_rpc_group()` 注册。
"""
import json
import os
import subprocess
import sys
import time as _t
import urllib.request

import click

from tbtools_cli.core import JAR
from tbtools_cli.core import _ as _tr

@click.group('rpc')
def rpc_group():
    """RPC 服务器管理（188 方法）"""

# ---------- RPC 自愈基础设施（N34/N35 批次 2）----------
# 症状：引擎进程内存/空闲期自发死亡；代理层把死亡伪装成 502；CLI 无感知、无自愈。
# 方案：pid 文件 + 健康探针（system.listMethods）+ call/methods 前 ensure 自动拉起。
# 注意：urllib 必须绕过代理（N41：HTTP_PROXY 注入会让 127.0.0.1 请求走代理转发失败）。

def _rpc_state_dir():
    d = os.environ.get(
        "TBTOOLS_RPC_DIR",
        os.path.join(os.path.expanduser("~"), ".config", "tbtools-cli"),
    )
    os.makedirs(d, exist_ok=True)
    return d

def _rpc_pid_file(port):
    return os.path.join(_rpc_state_dir(), f"rpc-{port}.pid")

def _rpc_log_file(port):
    return os.path.join(_rpc_state_dir(), f"rpc-{port}.log")

def _rpc_ping(port, timeout=5):
    """健康探针：POST system.listMethods。绕过代理。返回 True/False"""
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/rpc",
            data=json.dumps({"jsonrpc": "2.0", "method": "system.listMethods",
                             "params": {}, "id": 1}).encode(),
            headers={"Content-Type": "application/json"})
        resp = opener.open(req, timeout=timeout)
        result = json.loads(resp.read())
        return "result" in result
    except Exception:
        return False

def _rpc_read_pid(port):
    """读 pid 文件；进程不存在或与 RPC 无关则清理并返回 None"""
    pid_file = _rpc_pid_file(port)
    try:
        with open(pid_file) as f:
            pid = int(f.read().strip())
    except Exception:
        return None
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError, OverflowError, ValueError):
        _rpc_remove_pid(port)
        return None
    # Linux 下确认 cmdline 是 RPC server（防 pid 复用误杀）
    cmdline = f"/proc/{pid}/cmdline"
    if os.path.isfile(cmdline):
        try:
            with open(cmdline, "rb") as f:
                if b"biocjava.rpc.RpcServer" not in f.read():
                    _rpc_remove_pid(port)
                    return None
        except Exception:
            pass
    return pid

def _rpc_write_pid(port, pid):
    with open(_rpc_pid_file(port), "w") as f:
        f.write(str(pid))

def _rpc_remove_pid(port):
    try:
        os.remove(_rpc_pid_file(port))
    except OSError:
        pass

def _rpc_launch(port, mem):
    """拉起 RPC 服务器（detached，OOM 崩溃转储，日志落盘）。返回 Popen"""
    if not JAR or not os.path.isfile(JAR):
        raise FileNotFoundError(
            "TBtools jar 未找到。请设置 TBTOOLS_JAR 环境变量或放入常见位置")
    log_path = _rpc_log_file(port)
    log_fh = open(log_path, "ab", buffering=0)
    args = [
        "java", f"-Xmx{mem}",
        # N35: OOM 时宁可崩溃（可自愈拉起）也不要僵尸悬挂；同时留堆转储供排查
        "-XX:+CrashOnOutOfMemoryError",
        "-XX:+HeapDumpOnOutOfMemoryError",
        f"-XX:HeapDumpPath={_rpc_state_dir()}",
        "-cp", JAR, "biocjava.rpc.RpcServer",
    ]
    proc = subprocess.Popen(
        args, stdout=log_fh, stderr=log_fh, start_new_session=True)
    _rpc_write_pid(port, proc.pid)
    return proc

def _rpc_start_lock(port, timeout_s=20):
    """启动互斥锁(评审 #17/#52-P0-8: Agent 并发 ensure 竞争, 跨平台)。

    POSIX: fcntl.flock;Windows: msvcrt.locking;不可用: 降级无锁(仅警告)。
    返回锁 fd(成功)或 None(已有人持有/平台不支持, 等待后 double-check)。
    """
    import time as _t
    lock = os.path.expanduser(f"~/.config/tbtools-cli/rpc-{port}.lock")
    fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o644)
    _locker = None
    try:
        import fcntl as _f
        def _try():
            _f.flock(fd, _f.LOCK_EX | _f.LOCK_NB)
        _locker = _try
    except ImportError:
        try:
            import msvcrt as _m  # type: ignore[attr-defined]  # Windows-only 模块
            def _try():
                _m.locking(fd, _m.LK_NBLCK, 1)  # type: ignore[attr-defined]
            _locker = _try
        except ImportError:
            _locker = None
    if _locker is None:
        click.echo("⚠️ 平台无文件锁(fcntl/msvcrt 均不可用), RPC 启动无互斥保护", err=True)
        return fd  # 降级: 仍返回 fd(调用方 double-check ping 兜底)
    t0 = _t.time()
    while True:
        try:
            _locker()
            return fd
        except (BlockingIOError, OSError):
            if _t.time() - t0 > timeout_s:
                os.close(fd)
                return None
            _t.sleep(0.3)


_RPC_CRASHES: dict = {}  # port -> [崩溃时间戳...](P1-20 crash-loop breaker)


def _rpc_breaker_open(port) -> bool:
    """60s 内 ≥3 次启动崩溃 → breaker OPEN(停止自动重启)"""
    import time as _t
    now = _t.time()
    hist = [t for t in _RPC_CRASHES.get(port, []) if now - t < 60]
    _RPC_CRASHES[port] = hist
    return len(hist) >= 3


def _rpc_record_crash(port):
    import time as _t
    _RPC_CRASHES.setdefault(port, []).append(_t.time())


def _ensure_rpc(port, mem="4g", wait_s=30, quiet=False):
    """ensure 逻辑（同交付包 run_p*.py 的 ensure_srv）：
    健康 → True；不健康/死亡 → 清 stale pid → 拉起 → 轮询健康。"""
    if _rpc_ping(port):
        return True
    # 启动互斥(评审 #17: 两个进程同时 ensure → 竞争; 锁内 double-check)
    _lock_fd = _rpc_start_lock(port)
    if _lock_fd is None:
        # 未获锁(他人启动中)→ 等待其完成, 再 ping
        import time as _t
        for _ in range(40):
            _t.sleep(0.5)
            if _rpc_ping(port):
                return True
        return _rpc_ping(port)
    try:
        if _rpc_ping(port):  # double-check(锁内)
            return True
    finally:
        pass
    old_pid = _rpc_read_pid(port)
    if old_pid:
        if not quiet:
            click.echo(f"⚠️ 检测到旧 RPC 进程 (PID {old_pid}) 无响应，终止后拉起新实例...", err=True)
        try:
            os.kill(old_pid, 15)
        except OSError:
            pass
        _rpc_remove_pid(port)
        _t.sleep(1)
    elif not quiet:
        click.echo(_tr("⚠️ RPC 服务器不可达（端口 {p}），自动拉起...", "⚠️ RPC server unreachable (port {p}) — auto-restarting...").format(p=port), err=True)
    try:
        # P1-20: crash-loop breaker(反复崩溃不再自动重启)
        if _rpc_breaker_open(port):
            click.echo(f"🛑 RPC crash-loop breaker: 60s 内 ≥3 次启动失败, 停止自动重启。"
                       f"诊断: tbtools rpc logs -p {port};手动恢复: tbtools rpc start -p {port} --force", err=True)
            _rpc_record_crash(port)
            return False
        _rpc_launch(port, mem)
    except FileNotFoundError as e:
        click.echo(f"❌ {e}", err=True)
        return False
    for _ in range(wait_s):
        _t.sleep(1)
        if _rpc_ping(port):
            return True
    click.echo(_tr("❌ RPC 服务器 {s}s 内未就绪，日志: {log}", "❌ RPC server not ready within {s}s, log: {log}").format(s=wait_s, log=_rpc_log_file(port)), err=True)
    return False

@rpc_group.command('start')
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
@click.option('--mem', '-m', default='4g', help='Java 堆内存')
@click.option('--force', '-f', is_flag=True, help='强制重启（杀掉已有实例）')
def rpc_start(port, mem, force):
    """启动 RPC 服务器（pid 文件 + 健康检查；已在跑则幂等返回）"""
    if _rpc_ping(port):
        if not force:
            pid = _rpc_read_pid(port)
            click.echo(_tr("✅ RPC 服务器已在运行（端口 {p}, PID {pid}）", "✅ RPC server already running (port {p}, PID {pid})").format(p=port, pid=pid or '?'))
            return
        old = _rpc_read_pid(port)
        click.echo(f"🔄 --force：终止旧实例 (PID {old or '?'})...")
        if old:
            try:
                os.kill(old, 15)
            except OSError:
                pass
        _rpc_remove_pid(port)
        _t.sleep(1)
    else:
        # 清 stale（引擎自发死亡残留）
        old = _rpc_read_pid(port)
        if old:
            click.echo(f"⚠️ 旧 RPC 进程 (PID {old}) 无响应，终止...")
            try:
                os.kill(old, 15)
            except OSError:
                pass
            _rpc_remove_pid(port)
        _t.sleep(1)
    click.echo(_tr("🚀 启动 RPC 服务器（端口 {p}，堆 {m}）...", "🚀 Starting RPC server (port {p}, heap {m})...").format(p=port, m=mem))
    try:
        proc = _rpc_launch(port, mem)
    except FileNotFoundError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)
    for _ in range(30):
        _t.sleep(1)
        if _rpc_ping(port):
            click.echo(f"✅ RPC 服务器就绪 (PID {proc.pid})")
            click.echo(f"   pid 文件: {_rpc_pid_file(port)}")
            click.echo(f"   日志: {_rpc_log_file(port)}")
            click.echo(f"   测试: curl -X POST http://127.0.0.1:{port}/rpc -H 'Content-Type: application/json' -d '{{\"method\":\"system.listMethods\",\"params\":{{}},\"id\":1}}'")
            return
    click.echo(f"❌ 启动超时（30s），日志: {_rpc_log_file(port)}", err=True)
    sys.exit(1)


@rpc_group.command('logs')
@click.option('--tail', 'n', type=int, default=50, help='显示末尾 N 行(0=全部)')
@click.option('--port', default=8765, help='RPC 端口')
def logs(n, port):
    """查看 RPC 服务器日志(尾部 N 行;0=全部)"""
    import os as _os
    log = _rpc_log_file(port)
    if not _os.path.isfile(log):
        click.echo(f"❌ 无日志文件(服务器未启动过?): {log}", err=True)
        sys.exit(1)
    if n <= 0:
        click.echo(open(log, encoding="utf-8", errors="replace").read())
    else:
        lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
        click.echo("\n".join(lines[-n:]))

@rpc_group.command('stop')
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
def rpc_stop(port):
    """停止 RPC 服务器"""
    pid = _rpc_read_pid(port)
    if not pid:
        click.echo(f"RPC 服务器未在运行（端口 {port}）")
        _rpc_remove_pid(port)
        return
    try:
        os.kill(pid, 15)
        click.echo(_tr("✅ 已发送 SIGTERM (PID {p})", "✅ SIGTERM sent (PID {p})").format(p=pid))
    except OSError as e:
        click.echo(f"❌ 终止失败: {e}", err=True)
        sys.exit(1)
    _rpc_remove_pid(port)

@rpc_group.command('status')
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
def rpc_status(port):
    """查看 RPC 服务器状态"""
    pid = _rpc_read_pid(port)
    healthy = _rpc_ping(port)
    if healthy:
        click.echo(f"✅ 运行中（端口 {port}, PID {pid or '?'}）")
    elif pid:
        click.echo(f"⚠️ 进程存在 (PID {pid}) 但健康检查失败（可能正在启动或假死）")
        sys.exit(2)
    else:
        click.echo(f"❌ 未运行（端口 {port}）。启动: tbtools rpc start")
        sys.exit(1)

@rpc_group.command('methods')
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
@click.option('--mem', '-m', default='4g', help='--autostart 时的 Java 堆内存')
@click.option('--autostart', is_flag=True, help='服务不可达时自动拉起(默认不启动进程——发现操作应 side-effect free)')
def rpc_methods(port, mem, autostart):
    """列出全部 188 RPC 方法（默认静态发现, 不启动服务器; --autostart 时自动拉起）"""
    if autostart and not _ensure_rpc(port, mem):
        click.echo("   手动启动: tbtools rpc start", err=True)
        sys.exit(1)
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/rpc",
            data=json.dumps({"jsonrpc": "2.0", "method": "system.listMethods", "params": {}, "id": 1}).encode(),
            headers={"Content-Type": "application/json"})
        resp = opener.open(req, timeout=15)
        result = json.loads(resp.read())
        res = result.get('result', [])
        methods = res.get('methods', res) if isinstance(res, dict) else res
        click.echo(f"RPC 方法（{len(methods)} 个）：")
        for m in methods:
            click.echo(f"  {m}")
    except Exception as e:
        click.echo(f"❌ RPC 调用失败: {e}", err=True)
        click.echo("   引擎可能已死，尝试: tbtools rpc start --force", err=True)
        sys.exit(1)

@rpc_group.command('call')
@click.argument('method')
@click.argument('params', required=False)
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
@click.option('--mem', '-m', default='4g', help='自动拉起时的 Java 堆内存')
@click.option('--timeout', '-t', type=int, default=300, help='调用超时（秒）')
@click.option('--no-autostart', is_flag=True, help='禁用在不可达时自动拉起')
def rpc_call(method, params, port, mem, timeout, no_autostart):
    """调用 RPC 方法（服务不可达时自动拉起）"""
    params_obj = json.loads(params) if params else {}
    if not no_autostart and not _ensure_rpc(port, mem):
        click.echo("   手动启动: tbtools rpc start", err=True)
        sys.exit(1)
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/rpc",
            data=json.dumps({"jsonrpc": "2.0", "method": method, "params": params_obj, "id": 1}).encode(),
            headers={"Content-Type": "application/json"})
        resp = opener.open(req, timeout=timeout)
        result = json.loads(resp.read())
        if result.get('error'):
            # N38: 引擎错误 message 空/占位符时补友好提示（GffReconstructorBatch 等家族）
            err = result['error']
            msg = str(err.get('data', {}).get('message') if isinstance(err.get('data'), dict) else err.get('data') or err.get('message') or '')
            if not msg.strip() or msg.strip() == '===== See Following Info =====' or msg.startswith('Something Error'):
                msg = '引擎内部错误且未提供消息（N38 家族，GffReconstructorBatch/BestIdConverter/ReciprocalBlast 已知）'
                click.echo(f"❌ RPC 错误 [{err.get('code')}]: {msg}（原始: {json.dumps(err, ensure_ascii=False)[:200]}）", err=True)
            else:
                click.echo(f"❌ RPC 错误 [{err.get('code')}]: {msg}", err=True)
            sys.exit(1)
        click.echo(json.dumps(result.get('result', ''), indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"❌ RPC 调用失败: {e}", err=True)
        sys.exit(1)


def build_rpc_group():
    """构建 rpc 分组（由主 CLI 注册）"""
    return rpc_group
