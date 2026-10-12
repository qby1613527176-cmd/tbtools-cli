"""pytest 插件级 fixture/hook(2026-10-12 修复):

红队 P1-3(763e55c)把 pytest_runtest_makereport 写在测试模块内——pytest 只注册
conftest.py 与插件的 hookimpl, 测试模块里的 @pytest.hookimpl **不生效**(pytest 9
实测), 导致 _TIER2_RESULTS 恒为空 → 写盘永远走继承路径 → last_passed_at 从未
刷新为 now, "每晚 pass 保鲜" 语义从未真正工作。hook 移到这里后由 pytest 自动注册。
"""
import pytest

# 与 test_conformance_verified 共享的 Tier2 执行结果容器(pytest hook 写入,
# 测试模块 from conftest import 同名引用, monkeypatch 仍按模块属性覆盖)。
TIER2_RESULTS: dict = {}


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """收集 TestTier2ExecutionVerified 每工具真实执行结果(pass/skip/fail)。

    verified N7 ① 时序修复的配套: 报告构建发生在全部 Tier2 之后, 这里在
    "call" 阶段逐用例记录; skip(无 JAR/RPC)≠fail, 均不刷新证据(没真跑过)。
    """
    outcome = yield
    rep = outcome.get_result()
    if (rep.when == "call" and item.cls is not None
            and item.cls.__name__ == "TestTier2ExecutionVerified"):
        _tool = getattr(item, "callspec", None)
        if _tool and "tool" in _tool.params:
            TIER2_RESULTS[_tool.params["tool"]] = ("pass" if rep.passed
                                                   else ("skip" if rep.skipped else "fail"))