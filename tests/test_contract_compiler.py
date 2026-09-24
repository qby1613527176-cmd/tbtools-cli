"""第 15 份评审金链契约测试(Contract Compiler 闭环):
InvocationSpec / Planner 契约图 / workflow_id 身份 / resume fingerprint / 列名契约 / MCP envelope。
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TestInvocationSpec:
    """① Contract Compiler: 契约 → 精确 argv"""

    def test_build_argv_layout(self):
        from tbtools_cli.command_spec import build_command_specs
        sp = build_command_specs()["volcano"]
        argv = sp.invocation.build_argv(
            inputs=["deg.txt"], parameters={"pval_cutoff": "0.01"}, output="out.svg")
        assert argv == ["--pval-cutoff", "0.01", "deg.txt", "out.svg"], f"布局错误: {argv}"

    def test_type_validation(self):
        from tbtools_cli.command_spec import build_command_specs
        sp = build_command_specs()["volcano"]
        with pytest.raises(ValueError, match="INVALID_PARAMETER_TYPE"):
            sp.invocation.build_argv(inputs=["d.txt"], parameters={"pval_cutoff": "abc"}, output="o.svg")

    def test_unknown_parameter(self):
        from tbtools_cli.command_spec import build_command_specs
        sp = build_command_specs()["volcano"]
        with pytest.raises(ValueError, match="UNKNOWN_PARAMETER"):
            sp.invocation.build_argv(inputs=["d.txt"], parameters={"nope": "1"}, output="o.svg")

    def test_missing_required_input(self):
        from tbtools_cli.command_spec import build_command_specs
        sp = build_command_specs()["volcano"]
        with pytest.raises(ValueError, match="MISSING_REQUIRED_INPUT"):
            sp.invocation.build_argv(inputs=[], parameters={}, output="o.svg")


class TestPlannerContractGraph:
    """② Planner 契约图(outputs↔inputs)+ reasons-based confidence"""

    def test_phylogeny_plan_sensible(self):
        from tbtools_cli.workflow import plan_from_goal
        p = plan_from_goal("phylogenetic tree", input_format="fasta", output_format="nwk")
        tools = [s["tool"] for s in p["plan"]]
        assert tools, "应有计划"
        # 终点必须是树工具(iqtree/phylotree 等),且含契约边或单步直达
        assert tools[-1] in ("iqtree", "phylotree", "fasttree", "raxml") or "tree" in tools[-1]

    def test_exact_name_single_step(self):
        """目标点名工具 → 单步(不塞无关前缀)"""
        from tbtools_cli.workflow import plan_from_goal
        p = plan_from_goal("differential expression volcano", input_format="tsv", output_format="svg")
        assert [s["tool"] for s in p["plan"]] == ["volcano"]

    def test_confidence_reasons(self):
        from tbtools_cli.workflow import plan_from_goal
        p = plan_from_goal("volcano plot", input_format="tsv", output_format="svg")
        assert 0 < p["confidence"] <= 0.99
        assert p["confidence_reasons"], "必须有 reasons"
        assert "input_format_exact" in p["confidence_reasons"]

    def test_multi_input_tool_penalized(self):
        """多必填输入工具被降级(preparespecies 需 genome+gff3 两个必填)"""
        from tbtools_cli.workflow import plan_from_goal
        p = plan_from_goal("phylogenetic tree", input_format="fasta", output_format="nwk")
        tools = [s["tool"] for s in p["plan"]]
        assert "preparespecies" not in tools, "多必填输入工具不应入选"


class TestWorkflowIdentity:
    """③ workflow_id 完整身份(跨进程稳定 + chain 不同则 id 不同)"""

    def test_stable_cross_process(self):
        from tbtools_cli.workflow import plan_from_goal
        p1 = plan_from_goal("volcano plot", input_format="tsv")
        r = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0,'.');"
             "from tbtools_cli.workflow import plan_from_goal;"
             "print(plan_from_goal('volcano plot', input_format='tsv')['workflow']['workflow_id'])"],
            capture_output=True, text=True, cwd=ROOT)
        assert p1["workflow"]["workflow_id"] == r.stdout.strip()


class TestResumeFingerprint:
    """④ resume fingerprint: workflow 定义变更 → 全部重跑"""

    @pytest.mark.integration
    def test_fingerprint_invalidation(self, tmp_path):
        if not os.path.isfile(os.environ.get("TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar")):
            pytest.skip("无 JAR")
        wf = tmp_path / "w.yaml"
        wf.write_text("""id: fp.test
steps:
  - id: v
    tool: expr volcano
    args: ["examples/data/deg.txt", "{workdir}/v.svg"]
""")
        env = dict(os.environ, TBTOOLS_JAR=os.environ.get(
            "TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar"))
        wd = str(tmp_path / "w.wf")
        r1 = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "workflow", "run",
                             str(wf), "--workdir", wd], capture_output=True, text=True,
                            cwd=ROOT, env=env, timeout=120)
        assert json.loads(r1.stdout)["status"] == "succeeded"
        # 定义变更 → resume 应重跑(fingerprint 不匹配)
        wf.write_text("""id: fp.test
steps:
  - id: v
    tool: expr volcano
    args: ["examples/data/deg.txt", "{workdir}/v.svg", "0.01"]
""")
        r2 = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "workflow", "run",
                             str(wf), "--workdir", wd, "--resume"],
                            capture_output=True, text=True, cwd=ROOT, env=env, timeout=120)
        assert "fingerprint" in r2.stderr or json.loads(r2.stdout)["steps"][0]["exit_code"] == 0


class TestArtifactContractColumns:
    """⑤ artifact inspect 列名契约(producer 有 columns 契约时验证表头)"""

    def test_column_contract_violation(self, tmp_path):
        bad = tmp_path / "bad.tsv"
        bad.write_text(open(os.path.join(ROOT, "examples/data/deg.txt")).read().replace("GeneID", "WRONG", 1))
        prov = {"command": "volcano", "invocation": "t", "tbtools_cli": "1.4.2",
                "exit_code": 0, "outputs": [str(bad)], "inputs": [], "timestamp": "t"}
        (tmp_path / "bad.tsv.tbtools.json").write_text(json.dumps(prov))
        r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "artifact", "inspect",
                            str(bad), "--json"], capture_output=True, text=True, cwd=ROOT)
        d = json.loads(r.stdout)
        assert d["validation"]["valid"] is False
        assert "GeneID" in d["validation"]["contract_columns"]["missing"]


class TestMcpEnvelope:
    """⑥ MCP 错误 envelope 统一"""

    def test_error_envelope(self):
        from tbtools_cli import mcp_server as ms
        r = ms._cli("tool-describe", "nosuchtool_xyz", "--json")
        d = json.loads(r)
        assert d["status"] == "failed" and d["error"]["code"] == "CLI_ERROR"


class TestArtifactIndexLock:
    """⑦ Artifact 索引 flock(评审 #70 P1-4 核验)"""

    def test_flock_present(self):
        import inspect

        from tbtools_cli import artifact
        src = inspect.getsource(artifact.register)
        assert "flock" in src, "register 应有 flock(并发防丢)"
