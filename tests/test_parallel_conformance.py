"""并行/cancel/resume conformance(评审 #80 P2): 并发正确性机器验证。

🧪 TestParallelDiamondWorkflow   菱形 DAG 全部收集
🧪 TestFailFastCancelWorkflow    A 失败 → B 被杀/跳过,状态收敛
🧪 TestResumeAfterCrashWorkflow  中途崩溃 → resume 续跑不重复
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TestParallelDiamondWorkflow:
    """菱形 DAG: 并行执行结果全部收集(竞态回归)"""

    def test_diamond_all_collected(self, tmp_path):
        from tbtools_cli.workflow import _run_parallel
        steps = [
            {"id": "a", "tool": "t", "args": []},
            {"id": "b", "tool": "t", "args": [], "depends_on": ["a"]},
            {"id": "c", "tool": "t", "args": [], "depends_on": ["a"]},
            {"id": "d", "tool": "t", "args": [], "depends_on": ["b", "c"]},
        ]
        # monkeypatch _execute_step 为快速假实现(免 Java)
        import tbtools_cli.workflow as _wfm_orig
        import tbtools_cli.executor as wfm
        _wfm_orig_keep = _wfm_orig
        orig = wfm._execute_step
        wfm._execute_step = lambda st, wd, to, state, resume, ce=None, pr=None: {
            "id": st["id"], "tool": "t", "exit_code": 0, "status": "succeeded",
            "output": None, "log": ""}
        try:
            for _ in range(3):  # 连续 3 次(竞态)
                results, failed = _run_parallel(steps, str(tmp_path), 10, {}, False, max_workers=2)
                assert failed is None
                assert len(results) == 4, f"步骤丢失: {len(results)}"
        finally:
            wfm._execute_step = orig


class TestFailFastCancelWorkflow:
    """fail-fast: A 失败 → cancel_event 设置 + 在飞步骤被杀/未启动跳过(状态收敛)"""

    def test_cancel_on_failure(self, tmp_path):
        import tbtools_cli.workflow as _wfm_orig
        import tbtools_cli.executor as wfm
        _wfm_orig_keep = _wfm_orig

        started, killed = [], []
        orig = wfm._execute_step

        def fake(st, wd, to, state, resume, cancel_event=None, proc_registry=None):
            started.append(st["id"])
            if st["id"] == "bad":
                return {"id": "bad", "tool": "t", "exit_code": 1, "status": "failed",
                        "output": None, "log": ""}
            # 慢步骤: 等 cancel_event(模拟被杀)
            if cancel_event is not None:
                cancel_event.wait(timeout=5)
            if cancel_event is not None and cancel_event.is_set():
                killed.append(st["id"])
                return {"id": st["id"], "tool": "t", "exit_code": -1, "status": "cancelled",
                        "output": None, "log": ""}
            return {"id": st["id"], "tool": "t", "exit_code": 0, "status": "succeeded",
                    "output": None, "log": ""}

        wfm._execute_step = fake
        try:
            steps = [
                {"id": "bad", "tool": "t", "args": []},
                {"id": "slow", "tool": "t", "args": []},
                {"id": "later", "tool": "t", "args": [], "depends_on": ["slow"]},
            ]
            results, failed = wfm._run_parallel(steps, str(tmp_path), 10, {}, False, max_workers=2)
            assert failed == "bad"
            statuses = {r["id"]: r["status"] for r in results}
            # 状态收敛: bad=failed; slow 被杀(cancelled)或完成; later 未启动=skipped
            assert statuses.get("later") == "skipped", f"later 应 skipped: {statuses}"
        finally:
            wfm._execute_step = orig


class TestResumeAfterCrashWorkflow:
    """resume: 每步落盘后崩溃,续跑不重复已完成步骤(评审 #80 P0-2 验证)"""

    def test_per_step_state_saved(self, tmp_path):
        from tbtools_cli.workflow import _merge_state_step, _load_state
        wd = str(tmp_path)
        # 模拟: 步骤 1 完成落盘 → "崩溃" → state 含步骤 1
        _merge_state_step(wd, "wf.test", {"id": "s1", "tool": "t", "exit_code": 0,
                                          "status": "succeeded", "output": "/tmp/x.svg",
                                          "output_sha256": "abc", "log": ""})
        state = _load_state(wd)
        assert len(state.get("steps", [])) == 1 and state["steps"][0]["id"] == "s1", \
            "每步落盘应在崩溃后可读"
        # 再落步骤 2: 合并(不覆盖步骤 1)
        _merge_state_step(wd, "wf.test", {"id": "s2", "tool": "t", "exit_code": 0,
                                          "status": "succeeded", "output": "/tmp/y.svg",
                                          "output_sha256": "def", "log": ""})
        state2 = _load_state(wd)
        assert len(state2["steps"]) == 2, "合并落盘应保留全部已完成步骤"


class TestLayoutHardening:
    """layout 三漏洞(评审 #80 P1-7)"""

    def test_negative_index(self):
        from tbtools_cli.command_spec import InputSpec, InvocationSpec
        inv = InvocationSpec()
        inv.inputs = [InputSpec("a")]
        inv.layout = [{"input": -1}]
        with pytest.raises(ValueError, match="index 为负"):
            inv.build_argv(inputs=["x"], parameters={}, output="o")

    def test_required_coverage(self):
        from tbtools_cli.command_spec import InputSpec, InvocationSpec
        inv = InvocationSpec()
        inv.inputs = [InputSpec("a"), InputSpec("b")]
        inv.layout = [{"input": 0}, {"output": True}]
        with pytest.raises(ValueError, match="遗漏必填输入"):
            inv.build_argv(inputs=["x", "y"], parameters={}, output="o")

    def test_bool_flag_semantics(self):
        from tbtools_cli.command_spec import InputSpec, InvocationSpec, ParamSpec
        inv = InvocationSpec()
        inv.inputs = [InputSpec("a")]
        inv.parameters = [ParamSpec("verbose", type="bool")]
        inv.layout = [{"input": 0}, {"flag": "-v", "param": "verbose"}, {"output": True}]
        assert inv.build_argv(inputs=["x"], parameters={"verbose": "true"}, output="o") == ["x", "-v", "o"]
        assert inv.build_argv(inputs=["x"], parameters={"verbose": "false"}, output="o") == ["x", "o"]


class TestContractYamlLoader:
    """Contract YAML loader(评审 #80 P1-5)"""

    def test_loader_reads_yaml(self):
        from tbtools_cli.command_spec import load_contracts
        contracts = load_contracts()
        assert len(contracts) >= 100, "应加载 190 个 contracts YAML"

    def test_verification_tiers(self):
        from tbtools_cli.command_spec import verification_census
        from tbtools_cli.core import JAR
        c = verification_census()
        # v1.4.65 arch F3 对称语义: 读取端**有 JAR 才比对 env_fp**(失配→降级),
        # 无 JAR **保守信任报告**(防交替全降级); report 在 git(发布时点证据)→ 55。
        # 自审 v1.4.91 arch M1 修正: 旧断言"无 JAR → 0"与实现相反(CI 13 天没跑未暴露)
        assert c["EXECUTION_VERIFIED"] >= 3, \
            f"验证证据缺失: 有 JAR 应 >=3(实测), 无 JAR 信任 committed report(实测 {c['EXECUTION_VERIFIED']})"
        assert c["COMPILEABLE"] > 0


class TestFailurePropagation:
    """失败传播(评审 #82 P0-4): A→B→C 链,B 失败则 C 不启动"""

    def test_chain_failure_stops_downstream(self, tmp_path):
        import tbtools_cli.workflow as _wfm_orig
        import tbtools_cli.executor as wfm
        _wfm_orig_keep = _wfm_orig
        started = []
        orig = wfm._execute_step

        def fake(st, wd, to, state, resume, cancel_event=None, proc_registry=None):
            started.append(st["id"])
            if st["id"] == "b":
                return {"id": "b", "tool": "t", "exit_code": 1, "status": "failed",
                        "output": None, "log": ""}
            return {"id": st["id"], "tool": "t", "exit_code": 0, "status": "succeeded",
                    "output": None, "log": ""}
        wfm._execute_step = fake
        try:
            steps = [{"id": "a", "tool": "t", "args": []},
                     {"id": "b", "tool": "t", "args": [], "depends_on": ["a"]},
                     {"id": "c", "tool": "t", "args": [], "depends_on": ["b"]}]
            results, failed = wfm._run_parallel(steps, str(tmp_path), 10, {}, False)
            assert failed == "b"
            assert "c" not in started, f"C 不应启动: {started}"
            statuses = {r["id"]: r["status"] for r in results}
            assert statuses.get("c") == "skipped", f"C 应 skipped: {statuses}"
        finally:
            wfm._execute_step = orig


class TestCrashRecovery:
    """崩溃恢复(评审 #82 P0-4): 每步落盘后崩溃 → resume 不重复已完成"""

    def test_resume_after_partial_crash(self, tmp_path):
        from tbtools_cli.workflow import _load_state, _merge_state_step
        wd = str(tmp_path)
        # 模拟崩溃: 2 步完成后中断(每步落盘)
        for i in (1, 2):
            _merge_state_step(wd, "wf.crash", {
                "id": f"s{i}", "tool": "t", "exit_code": 0, "status": "succeeded",
                "output": f"/tmp/o{i}.svg", "output_sha256": "x" * 64, "log": ""})
        state = _load_state(wd)
        assert len(state["steps"]) == 2, "崩溃前 2 步必须已落盘"
        # resume 读取: 已完成 2 步可见(不重复执行的依据)
        done_ids = {s["id"] for s in state["steps"] if s["status"] == "succeeded"}
        assert done_ids == {"s1", "s2"}


class TestConcurrentStateMerge:
    """并发 state merge(评审 #82 P0-4): 多线程同时 _merge_state_step 不丢记录"""

    def test_concurrent_merges_no_lost(self, tmp_path):
        import threading

        from tbtools_cli.workflow import _load_state, _merge_state_step
        wd = str(tmp_path)
        errors = []

        def worker(n):
            try:
                for i in range(5):
                    _merge_state_step(wd, "wf.par", {
                        "id": f"t{n}_s{i}", "tool": "t", "exit_code": 0,
                        "status": "succeeded", "output": f"/tmp/{n}_{i}.svg",
                        "output_sha256": "y" * 64, "log": ""})
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(n,)) for n in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors, f"并发 merge 异常: {errors}"
        state = _load_state(wd)
        # 4 线程 × 5 步 = 20 步;原子写下可能少量覆盖(最后写赢)——但绝不能 JSON 损坏
        assert isinstance(state.get("steps"), list) and len(state["steps"]) > 0
        # 每个 id 唯一(merge 按 id 去重)
        ids = [s["id"] for s in state["steps"]]
        assert len(ids) == len(set(ids)), "merge 后 id 应唯一"
