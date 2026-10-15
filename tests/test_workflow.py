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


class TestPathInterpolation:
    """十四轮 product P1(GPT): workflow plan() 路径插值不得走 JSON 序列化往返——
    Windows 反斜杠(C:\tmp\new.fa) 的 \t \n 在 dumps→replace→loads 链被吃成转义/
    崩溃/静默损坏(provenance 记假路径)。已改递归 str 叶子替换。"""

    def _plan(self, inputs, binding, workdir="C:/work"):
        import tbtools_cli.workflow as wf
        return wf.plan({"id": "t", "inputs": inputs,
                        "steps": [{"id": "s1", "tool": "muscle", "binding": binding}]},
                       workdir=workdir)

    def test_windows_backslash_path(self):
        """C:\tmp\new.fa——\t 转义地狱核心场景(此前崩溃/静默损坏)"""
        steps = self._plan({"fa": r"C:\tmp\new.fa"},
                           {"inputs": ["{input.fa}"], "parameters": {}, "output": "{workdir}/o.aln"})
        argstr = " ".join(str(x) for x in steps[0]["args"])
        assert r"C:\tmp\new.fa" in argstr, f"反斜杠路径损坏: {argstr!r}"

    def test_linux_path(self):
        steps = self._plan({"fa": "/data/sample.fa"},
                           {"inputs": ["{input.fa}"], "parameters": {}, "output": "{workdir}/o.aln"})
        assert "/data/sample.fa" in " ".join(str(x) for x in steps[0]["args"])

    def test_path_with_spaces_cjk(self):
        """含空格+中文字符路径"""
        steps = self._plan({"fa": "D:/data dir/样本.fa"},
                           {"inputs": ["{input.fa}"], "parameters": {}, "output": "{workdir}/o.aln"})
        assert "D:/data dir/样本.fa" in " ".join(str(x) for x in steps[0]["args"])

    def test_path_with_double_quote_backslash(self):
        """含双引号反斜杠——JSON 转义最坏场景"""
        steps = self._plan({"fa": r'C:\q"dir\x.fa'},
                           {"inputs": ["{input.fa}"], "parameters": {}, "output": "{workdir}/o.aln"})
        assert r'C:\q"dir\x.fa' in " ".join(str(x) for x in steps[0]["args"])

    def test_multiple_input_placeholders(self):
        """多输入占位符 + workdir"""
        steps = self._plan({"a": r"C:\a.fa", "b": r"D:\b.fa"},
                           {"inputs": ["{input.a}", "{input.b}"],
                            "parameters": {}, "output": "{workdir}/o.aln"})
        argstr = " ".join(str(x) for x in steps[0]["args"])
        assert r"C:\a.fa" in argstr and r"D:\b.fa" in argstr

    def test_undefined_placeholder_kept_raw(self):
        """未定义占位符保持原样(不崩不吞)"""
        steps = self._plan({"fa": "x.fa"},
                           {"inputs": ["{input.fa}", "{input.missing}"],
                            "parameters": {}, "output": "{workdir}/o.aln"})
        argstr = " ".join(str(x) for x in steps[0]["args"])
        assert "{input.missing}" in argstr, "未定义占位符应保留原样"

    def test_input_bare_placeholder(self):
        """{input} 裸占位 → 首个/唯一 input"""
        steps = self._plan({"fa": r"C:\bare.fa"},
                           {"inputs": ["{input}"], "parameters": {}, "output": "{workdir}/o.aln"})
        assert r"C:\bare.fa" in " ".join(str(x) for x in steps[0]["args"])
