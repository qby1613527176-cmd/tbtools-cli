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
