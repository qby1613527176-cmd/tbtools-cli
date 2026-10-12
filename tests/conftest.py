"""pytest 插件级 fixture/hook(2026-10-12 修复 + 七轮 P1-B 扩展):

红队 P1-3(763e55c)把 pytest_runtest_makereport 写在测试模块内——pytest 只注册
conftest.py 与插件的 hookimpl, 测试模块里的 @pytest.hookimpl **不生效**(pytest 9
实测), 导致 _TIER2_RESULTS 恒为空 → 写盘永远走继承路径 → last_passed_at 从未
刷新为 now, "每晚 pass 保鲜" 语义从未真正工作。hook 移到这里后由 pytest 自动注册。
"""
import pytest

# 与 test_conformance_verified 共享的 Tier2 执行结果容器(pytest hook 写入,
# 测试模块 from conftest import 同名引用, monkeypatch 仍按模块属性覆盖)。
TIER2_RESULTS: dict = {}

# 七轮 verified/arch/product P1-B: 金链 conformance 结果容器(与 Tier2 同构)。
# key = 工具名(从测试方法名 test_<tool>_golden_chain 解析), value = pass/skip/fail。
# 报告写入器 conformance 升级必须引用它——结束"静态名单 CONFORMANCE_VERIFIED
# 不依赖金链观测"的架构不对称。金链测试无参数化(callspec 无 tool), 故按类名+方法名识别。
CONFORMANCE_RESULTS: dict = {}

# 六轮 verified P2-1: 按 item 累积三阶段结果, teardown 报告处终判——防止
# "call 通过但 setup/teardown 失败"时残留 call-pass 错误刷新验证证据。
# 值: "pass"|"skip"|"fail"|None(未报告)。skip 在真实 pytest 中发生在 setup 阶段
# (call 不执行), 故三阶段各自记录, 终判合并。
_TIER2_STAGES: dict = {}  # item.nodeid → {"setup":.., "call":.., "teardown":..}
_CONFORMANCE_STAGES: dict = {}


def _record_stage(container: dict, item, rep) -> None:
    """三阶段累积 + teardown 终判, 写入指定容器(key 由调用方给定)。"""
    _node = item.nodeid
    _st = _node_key_stages(container, _node)
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
        if all(_st.get(w) == "pass" for w in ("setup", "call", "teardown")):
            _r = "pass"
        elif any(_st.get(w) == "fail" for w in ("setup", "call", "teardown")):
            _r = "fail"
        else:
            _r = "skip"
        # 七轮 arch P2-2: 终判后弹键——防 repeat(rerun) 场景下同一 nodeid 残留上轮
        # 状态污染下一轮判断(残留旧 pass + setup 新 skip 会错误终判为 skip 而非 pass)
        _holder = _TIER2_STAGES if container is TIER2_RESULTS else _CONFORMANCE_STAGES
        _holder.pop(_node, None)
        return _r
    return None


def _node_key_stages(container: dict, node: str) -> dict:
    _stages = None
    # 找该 nodeid 对应的累积 dict(容器存于 _TIER2_STAGES/_CONFORMANCE_STAGES)
    _holder = _TIER2_STAGES if container is TIER2_RESULTS else _CONFORMANCE_STAGES
    if node not in _holder:
        _holder[node] = {}
    return _holder[node]


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """收集 Tier2(TestTier2ExecutionVerified)与金链(TestExecutableConformance)结果。

    verified N7 ① 时序修复的配套: 报告构建发生在全部 Tier2 之后。
    六轮 verified P2-1: 仅 setup+call+teardown 三阶段全部通过才记 pass(完整测试项
    成功); 任一阶段 fail 记 fail, 任一阶段 skip 记 skip——均不刷新成功证据。
    七轮 P1-B: 金链测试按方法名 test_<tool>_golden_chain 解析工具名, 终判写入
    CONFORMANCE_RESULTS——conformance 证据获得独立观测来源。
    """
    outcome = yield
    rep = outcome.get_result()
    if item.cls is None:
        return
    _cls = item.cls.__name__
    if _cls == "TestTier2ExecutionVerified":
        _tool = getattr(item, "callspec", None) and "tool" in item.callspec.params \
            and item.callspec.params["tool"] or None
        if _tool is None:
            return
        _r = _record_stage(TIER2_RESULTS, item, rep)
        if _r is not None:
            TIER2_RESULTS[_tool] = _r
    elif _cls == "TestExecutableConformance":
        # 金链方法名 test_<tool>_golden_chain → tool
        import re as _re
        _m = _re.match(r"test_(\w+)_golden_chain", item.name)
        if not _m:
            return
        _tool = _m.group(1)
        _r = _record_stage(CONFORMANCE_RESULTS, item, rep)
        if _r is not None:
            CONFORMANCE_RESULTS[_tool] = _r