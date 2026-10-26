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


# 十二轮 product P2(GPT): 嵌入模式进程级状态(chdir/stdout 重定向)并发互扰——
# 默认子进程模式隔离安全; 嵌入模式用模块级锁串行化(多线程 MCP 请求并发时
# 防止工作目录/标准输出交叉污染 JSON 协议体)。
_EMBEDDED_LOCK = __import__("threading").Lock()


def _cli(*args: str, timeout: int = 300) -> str:
    """调 CLI, 返回 stdout(纯 JSON 协议)。

    双模式(ADR-0003, 评审 #52 P0-7):
    - subprocess(默认, 隔离): 进程级隔离, 稳定
    - embedded(TBTOOLS_MCP_EMBEDDED=1): 进程内直接调用, 无启动开销(十二轮 P2: 模块级锁串行化, 防并发 chdir/stdout 互扰)
    """
    import os as _os
    if _os.environ.get("TBTOOLS_MCP_EMBEDDED") == "1":
        import contextlib
        import io
        with _EMBEDDED_LOCK:  # 十二轮 P2: 串行化嵌入调用(chdir/stdout 是进程级状态)
            cwd = _os.getcwd()
            try:
                _os.chdir(_root())
                import tbtools_cli.cli as _c
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    _exit_code = 0
                    try:
                        _c.cli.main(list(args), standalone_mode=False)
                    except SystemExit as _se:
                        _exit_code = _se.code if isinstance(_se.code, int) else 1
                _out = buf.getvalue().strip()
                # envelope 统一(评审 #72 P1-5): embedded 非 0 也返回结构化,与 subprocess 对齐
                if _exit_code != 0 and not _out.startswith("{"):
                    return json.dumps({"schema_version": "1.0", "status": "failed",
                                       "error": {"code": "CLI_ERROR", "exit_code": _exit_code,
                                                 "message": _out[-500:], "retryable": False}},
                                      ensure_ascii=False, indent=1)
                return _out
            finally:
                _os.chdir(cwd)
    # 错误 envelope 统一(评审 #70 P1-6): timeout/非 0 返回结构化 JSON,不抛异常/裸文本
    try:
        r = subprocess.run(
            [sys.executable, "-m", "tbtools_cli.cli", *args],
            capture_output=True, text=True, timeout=timeout, cwd=_root(),
        )
    except subprocess.TimeoutExpired:
        return json.dumps({"schema_version": "1.0", "status": "failed",
                           "error": {"code": "TIMEOUT", "message": f"CLI timeout after {timeout}s",
                                     "retryable": True}}, ensure_ascii=False, indent=1)
    if r.returncode != 0 and not r.stdout.strip().startswith("{"):
        return json.dumps({"schema_version": "1.0", "status": "failed",
                           "error": {"code": "CLI_ERROR", "exit_code": r.returncode,
                                     "message": (r.stderr or r.stdout).strip()[-500:],
                                     "retryable": False}}, ensure_ascii=False, indent=1)
    return r.stdout.strip()


@mcp.tool()
def search(query: str = "") -> str:
    """发现工具: 关键词/自然语言; 支持 --input/--output/--capability 反向搜索。返回 JSON hits。"""
    q = query.strip()
    if not q:
        # 评审 #109(DX): 空查询返回用法引导而非裸 {}——Agent 首次调用即知可用姿势
        # 十七轮 product P1-1(GPT): 空查询返回缺 schema_version/status, 违反 agent-protocol
        # §L14 统一响应结构——补齐协议字段(Agent 首撞路径, 不能是例外)
        return json.dumps({
            "schema_version": "1.0", "status": "failed",
            "query": "", "hits": [], "error": "query 为空",
            "usage": {"examples": ["search(query='volcano')", "search(query='phylogenetic tree')",
                                       "search(query='') 配合 input_format/output_format 反向搜索"],
                       "note": "可搭配 tool_describe(command) 看参数契约"},
        }, ensure_ascii=False)
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
    # 二十轮 arch P0(GPT): _unknown_params_warnings 必须在 if arguments: 分支前初始化——
    # 此前 init 在分支内(v1.5.7 起带菌发布: args=list/str/空/arguments={} falsy 全炸
    # UnboundLocalError, 底层 _cli 已执行完才抛异常→文件落盘+Agent 收异常→重试重复计算)
    _unknown_params_warnings: list = []
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
        # 十八轮 product P2(GPT): 未知参数边界不拒绝——有契约工具传未声明参数(evil_param)
        # 被静默拼成 --evil-param 直透 CLI, 错误在下游才暴露(实证 dualsyn)。修复: 有契约
        # 工具默认严格拒绝(UNKNOWN_PARAMETER + valid_parameters + retryable); 无契约工具
        # 保留逃生舱(kebab-case 回退)但响应加 warnings 字段。
        # 二十轮 arch P2(GPT): arguments 结构未校验——inputs 传字符串时
        # list("input.fa") 逐字符展开成垃圾路径(实证); parameters 传列表时
        # .items() 裸抛 AttributeError(违统一错误信封)。展开前结构校验:
        if not isinstance(arguments.get("inputs", []), (list, tuple)):
            return json.dumps({
                "schema_version": "1.0", "status": "failed",
                "error": {"code": "INVALID_ARGUMENTS_STRUCTURE",
                          "field": "inputs", "expected": "list",
                          "received": type(arguments.get("inputs")).__name__,
                          "retryable": True}}, ensure_ascii=False, indent=1)
        if not isinstance(arguments.get("parameters", {}), dict):
            return json.dumps({
                "schema_version": "1.0", "status": "failed",
                "error": {"code": "INVALID_ARGUMENTS_STRUCTURE",
                          "field": "parameters", "expected": "dict",
                          "received": type(arguments.get("parameters")).__name__,
                          "retryable": True}}, ensure_ascii=False, indent=1)
        for k, v in arguments.get("parameters", {}).items():
            _ps = _spec_map.get(k)
            if _spec_map and _ps is None and k not in _cli_map:
                return json.dumps({
                    "schema_version": "1.0", "status": "failed",
                    "error": {"code": "UNKNOWN_PARAMETER",
                              "parameter": k, "tool": _cmd_name,
                              "valid_parameters": sorted(_spec_map.keys()),
                              "retryable": True}}, ensure_ascii=False, indent=1)
            if not _spec_map and _ps is None and k not in _cli_map:
                _unknown_params_warnings.append(
                    f"参数 {k} 不在已知契约中, 按 kebab-case 直透(--{k.replace('_', '-')}), 引擎将自行判定")
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
                    # 十七轮 product P1-1(GPT): 参数类型错误返回缺 schema_version/status——
                    # 补齐协议字段(Agent 首次传错参即撞此分支)
                    return json.dumps({
                        "schema_version": "1.0", "status": "failed",
                        "error": {"code": "INVALID_PARAMETER_TYPE",
                                  "parameter": k, "expected": _t, "received": str(v),
                                  "retryable": True}}, ensure_ascii=False, indent=1)
            flag = (_ps.cli_name if _ps and _ps.cli_name else None) or _cli_map.get(k) or ("--" + k.replace("_", "-"))
            # bool 参数: true→flag 无值, false→省略(评审 #68 P1-6)
            if _t == "bool":
                if str(v).lower() in ("true", "1", "yes"):
                    parts.append(flag)
                continue
            parts += [flag, str(v)]
        # 二十一轮(GPT 审查一 P2-3): outputs 缺结构校验——list("path.svg") 会逐字符
        # 展开成垃圾参数(与 inputs 同型漏洞)。补校验:
        _outputs = arguments.get("outputs", [])
        if not isinstance(_outputs, (list, tuple)):
            return json.dumps({
                "schema_version": "1.0", "status": "failed",
                "error": {"code": "INVALID_ARGUMENTS_STRUCTURE",
                          "field": "outputs", "expected": "list[str]",
                          "received": type(_outputs).__name__,
                          "retryable": True}}, ensure_ascii=False, indent=1)
        if not all(isinstance(x, str) for x in _outputs):
            return json.dumps({
                "schema_version": "1.0", "status": "failed",
                "error": {"code": "INVALID_ARGUMENTS_STRUCTURE",
                          "field": "outputs", "expected": "list[str](元素均为字符串)",
                          "retryable": True}}, ensure_ascii=False, indent=1)
        parts += list(_outputs)
    else:
        if isinstance(args, str) and args.strip():
            import warnings as _w
            _w.warn("MCP args string 形式已弃用(空格路径拆错风险)——请用 args: list[str] 或 arguments: dict",
                    DeprecationWarning, stacklevel=2)
        parts = args if isinstance(args, list) else [p.strip() for p in args.split() if p.strip()]
    # 二十一轮 GPT P2-1: 移除二次初始化残留——它清空 for 循环收集的 warnings,
    # 无契约工具的未知参数警告丢失(入口 init 已在 L129 完成, 此处不得再清)
    # command 含空格(如 "expr volcano")拆分为分组+命令(评审: CLI 需要独立 token)
    cmd_parts = command.split() if " " in command else [command]
    out = _cli("tool-run", *cmd_parts, *parts, "--json", "--timeout", str(timeout_s), timeout=timeout_s + 30)
    # 十八轮 product P2: 无契约工具的未知参数逃生舱——warnings 显式注入响应(非静默直透)
    if _unknown_params_warnings:
        try:
            _d = json.loads(out)
            _d.setdefault("warnings", []).extend(_unknown_params_warnings)
            out = json.dumps(_d, ensure_ascii=False, indent=1)
        except Exception:
            pass
    return out


@mcp.tool()
def workflow_plan(goal: str, input_format: str = "", output_format: str = "") -> str:
    """目标 → 自动推导工具链计划(Workflow Planner; relations/capability 链推导)。
    响应包装: plan 为领域文档(协议 §3 显式例外——goal/plan/workflow/confidence 顶层字段
    保持原样, 向后兼容), 但十八轮 arch P2 起增量补顶层 status 字段, 通用解析器可先判
    status 再读领域字段。"""
    import json as _json
    from tbtools_cli.workflow import plan_from_goal
    _plan = plan_from_goal(goal, input_format=input_format, output_format=output_format)
    # 十八轮 arch P2(GPT): 裸出违反协议 §3 统一包装, 但全包装是破坏性变更——
    # 走 1.x 兼容路径: 增量加 status 顶层字段(不移动现有字段)
    # 二十一轮(GPT 审查二 P2-3): setdefault("status","success") 让空 plan 也报成功——
    # 违协议语义(成功=找到可执行计划, 不是规划函数没抛异常)。空 plan → NO_PLAN_FOUND。
    if not _plan.get("plan"):
        _plan["status"] = "failed"
        _plan.setdefault("error", {"code": "NO_PLAN_FOUND",
                                   "message": "未找到可执行工具链(契约图无匹配路径)",
                                   "retryable": True})
    else:
        _plan.setdefault("status", "success")
    _plan.setdefault("schema_version", "1.0")
    return _json.dumps(_plan, ensure_ascii=False, indent=1)


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
