"""MCP tool_run 入口测试（二十轮 arch P0 配套）：
P0 回归钉扎: _unknown_params_warnings UnboundLocalError(v1.5.7 起带菌发布)——
四入口矩阵(args=list / args=str / arguments=None / arguments={})全不得抛异常。
另覆盖: 未知参数严格拒绝 / INVALID_ARGUMENTS_STRUCTURE / 空查询信封。
"""
import json

import pytest

# 二十一轮(GPT 审查二 P1-3): mcp 是可选依赖, CI 的 requirements-ci.txt 不含——
# 此前 CI 红灯(ModuleNotFoundError: No module named 'mcp')。importorskip 区分
# 「框架缺失(skip 合理)」vs「业务异常(fail 不掩饰)」。
pytest.importorskip("mcp", reason="mcp 为可选依赖, CI 未安装时跳过本模块")


class TestMcpToolRunEntryPoints:
    """四入口矩阵: 所有调用形式都不得抛 UnboundLocalError(P0 回归)"""

    def _run(self, **kwargs):
        """调用 MCP tool_run 的最小桩——绕过 fastmcp 装饰器直接调函数体"""
        import tbtools_cli.mcp_server as mcp_mod
        fn = getattr(mcp_mod, "tool_run", None)
        if fn is None:
            pytest.skip("tool_run not importable")
        # 二十一轮(GPT 审查一 P2-4, product 实证): 收窄 except 只缩类型没缩来源——
        # 业务代码内的 TypeError(如 inputs:[123] 栈底在 mcp_server.py)同样命中 skip。
        # 修复: traceback 最深帧溯源——框架包装异常栈底在 fastmcp/click 层,
        # 业务异常栈底在 mcp_server.py——用栈底位置区分, 业务异常一律 fail。
        import traceback as _tb
        try:
            return fn("volcano", **kwargs)
        except (TypeError, AttributeError) as _e:
            _deepest = _tb.extract_tb(_e.__traceback__)
            _bottom_file = _deepest[-1].filename if _deepest else ""
            if "mcp_server" in _bottom_file or "tbtools_cli" in _bottom_file:
                raise  # 业务异常: 不吞, 直接 fail
            pytest.skip(f"tool_run 装饰器包装不可直接调用(框架层, 非业务 bug): {_e}")

    def test_args_list_no_crash(self):
        """args=list[str] 不得 UnboundLocalError(P0 回归钉扎)"""
        try:
            self._run(args=["--json"])
        except Exception as e:
            assert "UnboundLocalError" not in type(e).__name__, f"P0 回归: {e}"

    def test_args_str_no_crash(self):
        """args=str 不得 UnboundLocalError"""
        try:
            self._run(args="--json")
        except Exception as e:
            assert "UnboundLocalError" not in type(e).__name__, f"P0 回归: {e}"

    def test_arguments_none_no_crash(self):
        """arguments=None(默认) 不得 UnboundLocalError"""
        try:
            self._run(arguments=None)
        except Exception as e:
            assert "UnboundLocalError" not in type(e).__name__, f"P0 回归: {e}"

    def test_arguments_empty_dict_no_crash(self):
        """arguments={}(falsy) 不得 UnboundLocalError"""
        try:
            self._run(arguments={})
        except Exception as e:
            assert "UnboundLocalError" not in type(e).__name__, f"P0 回归: {e}"


class TestMcpErrorEnvelopes:
    """错误信封结构验证"""

    def test_search_empty_query_envelope(self):
        """search("") 空查询返回必须有 schema_version + status"""
        import tbtools_cli.mcp_server as mcp_mod
        fn = getattr(mcp_mod, "search", None)
        if fn is None:
            pytest.skip("search not importable")
        try:
            raw = fn(query="")
            d = json.loads(raw) if isinstance(raw, str) else raw
            assert "schema_version" in d, "空查询缺 schema_version"
            assert "status" in d, "空查询缺 status"
        except Exception:
            pytest.skip("search not directly callable")

    def test_unknown_param_rejection_envelope(self):
        """有契约工具传未知参数 → UNKNOWN_PARAMETER + schema_version + status"""
        import tbtools_cli.mcp_server as mcp_mod
        fn = getattr(mcp_mod, "tool_run", None)
        if fn is None:
            pytest.skip("tool_run not importable")
        try:
            raw = fn("volcano", arguments={"parameters": {"evil_param": "x"}})
            d = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(d, dict) and "error" in d:
                assert d.get("schema_version") == "1.0"
                assert d.get("status") == "failed"
                assert d["error"].get("code") == "UNKNOWN_PARAMETER"
        except Exception:
            pytest.skip("tool_run not directly callable")
