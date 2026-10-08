"""Workflow 一等公民测试(ADR-0007)。"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_cli(*args, timeout=120):
    r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", *args],
                       capture_output=True, text=True, timeout=timeout, cwd=ROOT,
                       env=dict(os.environ, TBTOOLS_JAR=os.environ.get(
                           "TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar")))
    return r.returncode, r.stdout, r.stderr


class TestWorkflow:
    def test_validate(self):
        ec, out, _ = run_cli("workflow", "validate", "examples/workflows/deg-pipeline/workflow.yaml")
        assert ec == 0
        d = json.loads(out)
        assert d["valid"] is True and d["steps"] == 2

    def test_plan(self):
        ec, out, _ = run_cli("workflow", "plan", "examples/workflows/deg-pipeline/workflow.yaml")
        assert ec == 0
        d = json.loads(out)
        assert len(d["plan"]) == 2 and d["plan"][0]["tool"] == "expr volcano"

    def test_graph(self):
        ec, out, _ = run_cli("workflow", "graph", "examples/workflows/deg-pipeline/workflow.yaml")
        assert ec == 0 and "graph LR" in out

    def test_validate_rejects_bad(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("id: x\nsteps: [{tool: volcano}]\n")
        ec, _, err = run_cli("workflow", "validate", str(bad))
        assert ec == 3 and "无效" in err

    @pytest.mark.integration
    def test_run_chain(self):
        """链式 workflow: $s1.output 引用解析 + artifacts + provenance"""
        # tableCollapse 是 Java 引擎——无 JAR 环境跳过(五视角自审 CI 首跑暴露)
        jar = os.environ.get("TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar")
        if not os.path.isfile(jar):
            pytest.skip("无 JAR(tableCollapse Java 引擎)")
        import tempfile
        yaml_content = """id: chain.test
steps:
  - id: s1
    tool: table tableCollapse
    args: ["examples/data/table/tableCollapse.in.tsv", "0", "{wd}/s1.tsv"]
  - id: s2
    tool: table tableCollapse
    args: ["$s1.output", "0", "{wd}/s2.tsv"]
"""
        with tempfile.TemporaryDirectory() as td:
            yf = os.path.join(td, "wf.yaml")
            open(yf, "w").write(yaml_content.replace("{wd}", td))
            ec, out, err = run_cli("workflow", "run", yf)
            assert ec == 0, err
            d = json.loads(out)
            assert d["status"] == "succeeded"
            assert len(d.get("artifacts", [])) == 2
            assert os.path.isfile(d["artifacts"][1] + ".tbtools.json")


class TestDagParallel:
    """DAG 并行调度(depends_on;ready-queue;竞态回归: 在飞步骤结果不丢)"""

    @pytest.mark.integration
    def test_parallel_all_steps_collected(self, tmp_path):
        """4 步菱形 DAG 连续 2 次运行,结果必须全部收集(竞态回归)"""
        jar = os.environ.get("TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar")
        if not os.path.isfile(jar):
            pytest.skip("无 JAR")
        wf = tmp_path / "dag.yaml"
        wf.write_text("""id: dag.test
steps:
  - id: v1
    tool: expr volcano
    binding: {inputs: ["examples/data/deg.txt"], parameters: {}, output: "{workdir}/v1.svg"}
  - id: v2
    tool: expr dehist
    depends_on: ["v1"]
    binding: {inputs: ["examples/data/deg.txt"], parameters: {}, output: "{workdir}/v2.svg"}
  - id: v3
    tool: expr dehist
    depends_on: ["v1"]
    binding: {inputs: ["examples/data/deg.txt"], parameters: {}, output: "{workdir}/v3.svg"}
  - id: v4
    tool: expr volcano
    depends_on: ["v2", "v3"]
    binding: {inputs: ["examples/data/deg.txt"], parameters: {}, output: "{workdir}/v4.svg"}
""")
        env = dict(os.environ, TBTOOLS_JAR=jar)
        for run_n in range(2):
            wd = str(tmp_path / f"r{run_n}.wf")
            r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "workflow", "run",
                                str(wf), "--workdir", wd], capture_output=True, text=True,
                               cwd=ROOT, env=env, timeout=300)
            d = json.loads(r.stdout)
            assert d["status"] == "succeeded", f"run{run_n} 失败"
            assert len(d["steps"]) == 4, f"run{run_n} 步骤丢失(竞态): {len(d['steps'])}"
            assert all(s["status"] == "succeeded" for s in d["steps"])
