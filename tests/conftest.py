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

# 六轮 verified P2-1: 按 item 累积三阶段结果, teardown 报告处终判——防止
# "call 通过但 setup/teardown 失败"时残留 call-pass 错误刷新验证证据。
# 值: "pass"|"skip"|"fail"|None(未报告)。skip 在真实 pytest 中发生在 setup 阶段
# (call 不执行), 故三阶段各自记录, 终判合并。
_TIER2_STAGES: dict = {}  # item.nodeid → {"setup":.., "call":.., "teardown":..}


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """收集 TestTier2ExecutionVerified 每工具真实执行结果(pass/skip/fail)。

    verified N7 ① 时序修复的配套: 报告构建发生在全部 Tier2 之后。
    六轮 verified P2-1: 仅 setup+call+teardown 三阶段全部通过才记 pass(完整测试项
    成功); 任一阶段 fail 记 fail, 任一阶段 skip 记 skip——均不刷新成功证据。
    """
    outcome = yield
    rep = outcome.get_result()
    if (item.cls is not None and item.cls.__name__ == "TestTier2ExecutionVerified"
            and getattr(item, "callspec", None) and "tool" in item.callspec.params):
        _tool = item.callspec.params["tool"]
        _node = item.nodeid
        _st = _TIER2_STAGES.setdefault(_node, {})
        if rep.when in ("setup", "call", "teardown"):
            if rep.skipped:
                _st[rep.when] = "skip"
            elif rep.failed:
                _st[rep.when] = "fail"
            elif rep.passed:
                _st[rep.when] = "pass"
            else:
                _st[rep.when] = "fail"
        if rep.when == "teardown":
            # 终判: 三阶段全 pass → pass; 任一 fail → fail; 否则(含任一 skip) → skip
            if all(_st.get(w) == "pass" for w in ("setup", "call", "teardown")):
                TIER2_RESULTS[_tool] = "pass"
            elif any(_st.get(w) == "fail" for w in ("setup", "call", "teardown")):
                TIER2_RESULTS[_tool] = "fail"
            else:
                TIER2_RESULTS[_tool] = "skip"