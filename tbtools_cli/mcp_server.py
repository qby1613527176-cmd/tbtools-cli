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

    timeout 与 CLI --timeout 对齐(评审 #6: 唯一 timeout authority):
    tool-run --timeout N 时 MCP 外层 subprocess timeout = N + 30s 缓冲(不抢先杀)。
    """
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
        for k, v in arguments.get("parameters", {}).items():
            parts += [f"--{k}", str(v)]
        parts += list(arguments.get("outputs", []))
    else:
        parts = args if isinstance(args, list) else [p.strip() for p in args.split() if p.strip()]
    # command 含空格(如 "expr volcano")拆分为分组+命令(评审: CLI 需要独立 token)
    cmd_parts = command.split() if " " in command else [command]
    return _cli("tool-run", *cmd_parts, *parts, "--json", "--timeout", str(timeout_s), timeout=timeout_s + 30)


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
