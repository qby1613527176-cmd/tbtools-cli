"""tbtools MCP server(GLM #40: MCP 是 transport, 核心是 CommandSpec 模型)。

让 Claude/Cursor/任意 MCP 客户端把 tbtools 当原生工具用:
自动发现(search/describe) → 预检(validate) → 执行(run/result) → 溯源(provenance)。
实现方式: 子进程调 CLI(稳定隔离, 复用全部 Agent 能力与 JSON 协议)。
启动: tbtools mcp (stdio) 或 python -m tbtools_cli.mcp_server
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tbtools")


def _root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _cli(*args: str, timeout: int = 300) -> str:
    """调 CLI, 返回 stdout(纯 JSON 协议)。

    双模式(ADR-0003, 评审 #52 P0-7):
    - subprocess(默认, 隔离): 进程级隔离, 稳定
    - embedded(TBTOOLS_MCP_EMBEDDED=1): 进程内直接调用, 无启动开销
    """
    import os as _os
    if _os.environ.get("TBTOOLS_MCP_EMBEDDED") == "1":
        import contextlib
        import io
        cwd = _os.getcwd()
        try:
            _os.chdir(_root())
            import tbtools_cli.cli as _c
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    _c.cli.main(list(args), standalone_mode=False)
                except SystemExit:
                    pass
            return buf.getvalue().strip()
        finally:
            _os.chdir(cwd)
    r = subprocess.run(
        [sys.executable, "-m", "tbtools_cli.cli", *args],
        capture_output=True, text=True, timeout=timeout, cwd=_root(),
    )
    return r.stdout.strip()


@mcp.tool()
def search(query: str = "") -> str:
    """发现工具: 关键词/自然语言; 支持 --input/--output/--capability 反向搜索。返回 JSON hits。"""
    q = query.strip()
    out = _cli("search", q, "--json") if q else "{}"
    try:
        return json.dumps(json.loads(out), ensure_ascii=False)
    except Exception:
        return out


@mcp.tool()
def tool_describe(command: str) -> str:
    """理解工具: 完整 schema(id/help/inputs/outputs/capabilities/dependencies/relations)。"""
    return _cli("tool-describe", command, "--json")


@mcp.tool()
def tool_validate(command: str, inputs: list[str] | str = "") -> str:
    """执行前预检: 文件存在/格式/列数。inputs 为输入路径 list 或兼容旧逗号串。"""
    parts = inputs if isinstance(inputs, list) else [p.strip() for p in inputs.split(",") if p.strip()]
    _cp = command.split() if " " in command else [command]
    return _cli("tool-validate", *_cp, *parts, "--json")


@mcp.tool()
def tool_run(command: str, args: list[str] | str = "", arguments: dict | None = None, timeout_s: int = 600) -> str:
    """执行工具(同步)。

    参数优先级: arguments(dict, Agent 结构化) > args(list 或 string 兼容)。
    arguments 形式: {"inputs": [...], "outputs": [...], "parameters": {k: v}}
    —— dict 会展开为 CLI 参数(空格路径安全; 评审 #21 Agent-native 结构化)。
    返回纯 JSON(exit_code/artifacts/error)。
    """
    if arguments:
        parts = list(arguments.get("inputs", []))
        # 参数 Schema-bound 翻译(评审 #56 P0-2): ParamSpec.name → cli_name(如 pval_cutoff→--pval-cutoff)
        # Agent 只传 contract 名;无 cli_name 标注的参数按 kebab-case 兜底
        _cmd_name = command.split()[-1] if command else ""
        _cli_map = {}
        try:
            from tbtools_cli.command_spec import KNOWN_PARAMS
            _cli_map = {p.name: p.cli_name for p in KNOWN_PARAMS.get(_cmd_name, []) if p.cli_name}
        except Exception:
            pass
        # 参数类型验证(评审 #64 P1-1: ParamSpec.type 强类型;错误→INVALID_PARAMETER_TYPE)
        # P1(评审 #68): 从 spec 读参数契约,不再 KNOWN_PARAMS 旁路;bool→flag 形式(--flag 无值)
        _spec_map = {}
        try:
            from tbtools_cli.command_spec import build_command_specs
            _sp = build_command_specs().get(_cmd_name)
            if _sp:
                _spec_map = {p.name: p for p in _sp.parameters}
        except Exception:
            pass
        for k, v in arguments.get("parameters", {}).items():
            _ps = _spec_map.get(k)
            _t = _ps.type if _ps else None
            if _t:
                _ok = True
                try:
                    if _t == "int":
                        int(v)
                    elif _t == "float":
                        float(v)
                    elif _t == "bool":
                        if str(v).lower() not in ("true", "false", "1", "0", "yes", "no"):
                            _ok = False
                except (ValueError, TypeError):
                    _ok = False
                if not _ok:
                    return json.dumps({
                        "error": {"code": "INVALID_PARAMETER_TYPE",
                                  "parameter": k, "expected": _t, "received": str(v),
                                  "retryable": False}}, ensure_ascii=False, indent=1)
            flag = (_ps.cli_name if _ps and _ps.cli_name else None) or _cli_map.get(k) or ("--" + k.replace("_", "-"))
            # bool 参数: true→flag 无值, false→省略(评审 #68 P1-6)
            if _t == "bool":
                if str(v).lower() in ("true", "1", "yes"):
                    parts.append(flag)
                continue
            parts += [flag, str(v)]
        parts += list(arguments.get("outputs", []))
    else:
        if isinstance(args, str) and args.strip():
            import warnings as _w
            _w.warn("MCP args string 形式已弃用(空格路径拆错风险)——请用 args: list[str] 或 arguments: dict",
                    DeprecationWarning, stacklevel=2)
        parts = args if isinstance(args, list) else [p.strip() for p in args.split() if p.strip()]
    # command 含空格(如 "expr volcano")拆分为分组+命令(评审: CLI 需要独立 token)
    cmd_parts = command.split() if " " in command else [command]
    return _cli("tool-run", *cmd_parts, *parts, "--json", "--timeout", str(timeout_s), timeout=timeout_s + 30)


@mcp.tool()
def workflow_plan(goal: str, input_format: str = "", output_format: str = "") -> str:
    """目标 → 自动推导工具链计划(Workflow Planner; relations/capability 链推导)。"""
    import json as _json
    from tbtools_cli.workflow import plan_from_goal
    return _json.dumps(plan_from_goal(goal, input_format=input_format,
                                      output_format=output_format), ensure_ascii=False, indent=1)


@mcp.tool()
def job_submit(command: str, args: list[str] | str = "", timeout_s: int = 0) -> str:
    """异步提交长任务: 返回 job_id(状态机 running→succeeded/failed/cancelled/timed_out)。"""
    parts = args if isinstance(args, list) else [p.strip() for p in args.split() if p.strip()]
    t = [f"--timeout={timeout_s}"] if timeout_s > 0 else []
    _cp = command.split() if " " in command else [command]
    return _cli("tool-submit", *_cp, *parts, *t)


@mcp.tool()
def job_status(job_id: str) -> str:
    """查询任务状态(含 exit_code)。"""
    return _cli("job-status", job_id)


@mcp.tool()
def job_result(job_id: str) -> str:
    """任务结构化结果(artifacts/error)。"""
    return _cli("job-result", job_id)


@mcp.tool()
def tool_provenance(output: str) -> str:
    """运行溯源: 读 <output>.tbtools.json(命令/版本/输入 sha/时间戳/错误)。"""
    return _cli("tool-provenance", output)


def main() -> None:
    # P1-22: MCP 默认 agent 安全模式(engine reflection 关闭, 除非 config [agent.policy] 显式开启)
    import os as _os
    _os.environ.setdefault("TBTOOLS_AGENT_MODE", "1")
    mcp.run()


if __name__ == "__main__":
    main()
