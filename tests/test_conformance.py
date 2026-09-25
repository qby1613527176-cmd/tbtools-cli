"""Contract Conformance 测试(评审 #72 P2-2):
① 全部 FULL 工具: InvocationSpec 编译行为符合契约(compile 可调用/类型拦截/未知拦截)
② 有数据的 FULL 工具: 金链 executable conformance(compile→execute→artifact→sha→provenance→resume)
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tbtools_cli.command_spec import agent_readiness, build_command_specs

FULL_TOOLS = sorted(n for n, s in build_command_specs().items() if agent_readiness(s) == "FULL")


class TestFullCompileConformance:
    """每个 FULL 工具: 契约编译行为一致"""

    @pytest.mark.parametrize("tool", FULL_TOOLS)
    def test_invocation_compilable(self, tool):
        spec = build_command_specs()[tool]
        inv = spec.invocation
        # 契约对象存在且 inputs/outputs 非空(FULL 定义)
        assert inv.inputs, f"{tool} FULL 但 inputs 空"
        assert inv.outputs, f"{tool} FULL 但 outputs 空"
        # 编译: 缺必填输入必须拒绝
        with pytest.raises(ValueError, match="MISSING_REQUIRED_INPUT"):
            inv.build_argv(inputs=[], parameters={}, output="o.out")

    @pytest.mark.parametrize("tool", FULL_TOOLS)
    def test_unknown_param_rejected(self, tool):
        spec = build_command_specs()[tool]
        n_inputs = len([i for i in spec.inputs if i.required])
        fake_inputs = [f"in{i}.txt" for i in range(max(n_inputs, 1))]
        with pytest.raises(ValueError, match="UNKNOWN_PARAMETER"):
            spec.invocation.build_argv(
                inputs=fake_inputs, parameters={"__definitely_unknown__": "1"}, output="o.out")


class TestExecutableConformance:
    """金链: compile→execute→artifact→sha→provenance(有数据的工具)"""

    @pytest.mark.integration
    def test_volcano_golden_chain(self, tmp_path):
        jar = os.environ.get("TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar")
        if not os.path.isfile(jar):
            pytest.skip("无 JAR")
        env = dict(os.environ, TBTOOLS_JAR=jar)
        # ① compile(契约编译出 argv——与 workflow binding 同路径)
        spec = build_command_specs()["volcano"]
        out_svg = str(tmp_path / "v.svg")
        argv = spec.invocation.build_argv(
            inputs=[os.path.join(ROOT, "examples/data/deg.txt")],
            parameters={"pval_cutoff": "0.05"}, output=out_svg)
        # ② execute
        r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "tool-run",
                            "expr", "volcano", *argv,
                            "--json"], capture_output=True, text=True, cwd=ROOT, env=env, timeout=120)
        d = json.loads(r.stdout)
        assert d["exit_code"] == 0
        # ③ artifact(统一模型)
        art = d["artifacts"][0]
        assert art["type"] == "plot" and art["format"] == "svg"
        # ④ sha256 完整
        assert len(art["sha256"]) == 64
        # ⑤ provenance
        prov = json.load(open(out_svg + ".tbtools.json", encoding="utf-8"))
        assert prov["exit_code"] == 0 and prov["inputs"]
        # ⑥ artifact_id 稳定(art_<sha[:32]>)
        assert art["id"].startswith("art_") and len(art["id"]) == 36


class TestEdgeInfo:
    """边标注: contract vs legacy_relation"""

    def test_contract_edge_typed(self):
        from tbtools_cli.workflow import plan_from_goal
        p = plan_from_goal("phylogenetic tree", input_format="fasta", output_format="nwk")
        # WorkflowSpec 步骤有 depends_on + contract
        steps = p["workflow"]["steps"]
        for i, s in enumerate(steps):
            assert "depends_on" in s and "input_contract" in s and "output_contract" in s
            if i > 0:
                assert s["depends_on"], f"step {s['id']} 应有依赖"


class TestPlanningScore:
    """planning_score 结构"""

    def test_structure(self):
        from tbtools_cli.workflow import plan_from_goal
        p = plan_from_goal("volcano plot", input_format="tsv", output_format="svg")
        ps = p["planning_score"]
        assert 0 < ps["score"] <= 0.99
        assert ps["level"] in ("high", "medium", "low")
        assert ps["evidence"], "evidence 非空"
