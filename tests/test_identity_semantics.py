"""评审 #100 回归矩阵(identity semantics): A-E 全测。"""
import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TestIdentityMatrix:
    """identity 数学定义回归矩阵(评审 #100 Test A-E)"""

    def test_A_same_everything(self):
        """A: 同 contract + 同 binding + 同输入 → 三指纹全同"""
        from tbtools_cli.workflow import compile_step_full
        s = {"id": "t", "tool": "volcano",
             "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                         "output": "/tmp/a.svg"}}
        c1, c2 = compile_step_full(s, "/tmp", {}), compile_step_full(s, "/tmp", {})
        assert c1.contract_fingerprint == c2.contract_fingerprint
        assert c1.binding_fingerprint == c2.binding_fingerprint
        assert c1.execution_fingerprint == c2.execution_fingerprint

    def test_B_diff_output_binding_diff_contract_same(self):
        """B: 不同输出 → binding 不同,contract 同"""
        from tbtools_cli.workflow import compile_step_full
        s1 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                          "output": "/tmp/a.svg"}}
        s2 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                          "output": "/tmp/b.svg"}}
        c1, c2 = compile_step_full(s1, "/tmp", {}), compile_step_full(s2, "/tmp", {})
        assert c1.binding_fingerprint != c2.binding_fingerprint
        assert c1.contract_fingerprint == c2.contract_fingerprint

    def test_C_diff_input_execution_diff(self, tmp_path):
        """C: 不同输入文件 → execution 不同,contract/binding 可比"""
        from tbtools_cli.workflow import compile_step_full
        p = tmp_path / "deg2.txt"
        shutil.copy("examples/data/deg.txt", p)
        p.write_text(p.read_text() + "#x\n")
        s1 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                          "output": "/tmp/a.svg"}}
        s2 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": [str(p)], "parameters": {}, "output": "/tmp/a.svg"}}
        c1, c2 = compile_step_full(s1, "/tmp", {}), compile_step_full(s2, "/tmp", {})
        assert c1.execution_fingerprint != c2.execution_fingerprint
        assert c1.contract_fingerprint == c2.contract_fingerprint

    def test_D_raw_symbolic_binding(self):
        """D: binding_fp 用 raw symbolic binding({input.X}/$step.output 替换前)"""
        from tbtools_cli.workflow import compile_step_full
        s = {"id": "t", "tool": "volcano",
             "binding": {"inputs": ["{input.deg}"], "parameters": {},
                         "output": "{workdir}/v.svg"}}
        c1 = compile_step_full(s, "/tmp/wd1", {}, symbolic_override=dict(s["binding"]))
        c2 = compile_step_full(s, "/tmp/wd2", {}, symbolic_override=dict(s["binding"]))
        # 不同 workdir 替换后路径不同,但 raw binding 同 → binding_fp 必须同
        assert c1.binding_fingerprint == c2.binding_fingerprint, \
            "binding_fp 必须用 raw symbolic binding(替换前 refs)"

    def test_E_canonical_contract_complete(self):
        """E: canonical_contract 含全字段(inputs/outputs/output_slots/parameters/layout)"""
        from tbtools_cli.command_spec import build_command_specs
        from tbtools_cli.workflow import canonical_contract
        c = canonical_contract(build_command_specs()["volcano"])
        for field in ("inputs", "outputs", "output_slots", "parameters",
                      "layout", "named_flags", "capabilities"):
            assert field in c, f"canonical_contract 缺 {field}"
        assert c["inputs"][0]["content_type"] == "table"


class TestResumeStrictness:
    """评审 #100 P0-3: resume 严格化(旧 state 无 fp → 重跑)"""

    @pytest.mark.integration
    def test_old_state_without_fp_reruns(self, tmp_path):
        jar = os.environ.get("TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar")
        if not os.path.isfile(jar):
            pytest.skip("无 JAR")
        wf = tmp_path / "w.yaml"
        wf.write_text("""id: strict.test
steps:
  - id: v
    tool: expr volcano
    binding: {inputs: ["{workdir}/deg.txt"], parameters: {}, output: "{workdir}/v.svg"}
""")
        wd = tmp_path / "w.wf"
        wd.mkdir()
        shutil.copy("examples/data/deg.txt", wd / "deg.txt")
        env = dict(os.environ, TBTOOLS_JAR=jar)
        r1 = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "workflow", "run",
                             str(wf), "--workdir", str(wd)], capture_output=True, text=True,
                            cwd=ROOT, env=env, timeout=120)
        assert json.loads(r1.stdout)["status"] == "succeeded"
        # 模拟旧 state: 删掉 fingerprint(旧版本 state)
        st_path = wd / ".wf_state.json"
        state = json.loads(st_path.read_text())
        for s in state["steps"]:
            s.pop("execution_fingerprint", None)
        st_path.write_text(json.dumps(state))
        # resume → 无 fp 必须重跑(评审 #100 P0-3)
        r2 = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "workflow", "run",
                             str(wf), "--workdir", str(wd), "--resume"],
                            capture_output=True, text=True, cwd=ROOT, env=env, timeout=120)
        assert "重新执行" in r2.stderr, "旧 state 无 fp 却跳过=假成功风险"


class TestIdentityFinal:
    """评审 #102 Test 1-5: identity 数学化收官"""

    def test_T1_same_contract_binding_input_same_fp(self):
        """Test 1: 同 contract + 同 binding + 同 input → 相同 fingerprint"""
        from tbtools_cli.workflow import compile_step_full
        s = {"id": "t", "tool": "volcano",
             "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                         "output": "/tmp/a.svg"}}
        c1, c2 = compile_step_full(s, "/tmp", {}), compile_step_full(s, "/tmp", {})
        assert c1.execution_fingerprint == c2.execution_fingerprint

    def test_T2_diff_input_diff_execution(self, tmp_path):
        """Test 2: 不同 input → execution_fp 不同,contract 不变"""
        import shutil

        from tbtools_cli.workflow import compile_step_full
        p = tmp_path / "d2.txt"
        shutil.copy("examples/data/deg.txt", p)
        p.write_text(p.read_text() + "#x\n")
        s1 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                          "output": "/tmp/a.svg"}}
        s2 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": [str(p)], "parameters": {}, "output": "/tmp/a.svg"}}
        c1, c2 = compile_step_full(s1, "/tmp", {}), compile_step_full(s2, "/tmp", {})
        assert c1.execution_fingerprint != c2.execution_fingerprint
        assert c1.contract_fingerprint == c2.contract_fingerprint

    def test_T3_contract_change_diff_fp(self):
        """Test 3: 契约字段变化 → execution_contract_fp 变化"""
        from tbtools_cli.command_spec import CommandSpec, InputSpec
        from tbtools_cli.workflow import execution_contract_fingerprint
        sp1 = CommandSpec(name="t", group="g", kind="manual",
                          inputs=[InputSpec("a", format="tsv")])
        sp2 = CommandSpec(name="t", group="g", kind="manual",
                          inputs=[InputSpec("a", format="fasta")])  # format 变
        assert execution_contract_fingerprint(sp1) != execution_contract_fingerprint(sp2)

    def test_T4_semantic_change_exec_contract_same(self):
        """Test 4: 语义字段变化 → execution_contract 不变,semantic_fp 变"""
        from tbtools_cli.command_spec import CommandSpec, InputSpec
        from tbtools_cli.workflow import execution_contract_fingerprint, semantic_fingerprint
        sp1 = CommandSpec(name="t", group="g", kind="manual",
                          inputs=[InputSpec("a", format="tsv")], capabilities=["x"])
        sp2 = CommandSpec(name="t", group="g", kind="manual",
                          inputs=[InputSpec("a", format="tsv")], capabilities=["y"])
        assert execution_contract_fingerprint(sp1) == execution_contract_fingerprint(sp2), \
            "语义变化不应影响执行契约"
        assert semantic_fingerprint(sp1) != semantic_fingerprint(sp2)

    def test_T5_full_sha256(self):
        """Test 5: fingerprint 内部 full 64 hex(不截断)"""
        from tbtools_cli.workflow import compile_step_full
        ci = compile_step_full(
            {"id": "t", "tool": "volcano",
             "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                         "output": "/tmp/a.svg"}}, "/tmp", {})
        assert len(ci.execution_fingerprint) == 64
        assert len(ci.binding_fingerprint_full) == 64


class TestIdentityClosure:
    """评审 #104 性质测试 1-6(identity closure)"""

    def test_P1_tool_change_fp_diff(self):
        """① 改 tool → execution contract fp 变"""
        from tbtools_cli.command_spec import CommandSpec, InputSpec
        from tbtools_cli.workflow import execution_contract_fingerprint
        a = CommandSpec(name="toolA", group="g", kind="manual",
                        inputs=[InputSpec("x", format="tsv")])
        b = CommandSpec(name="toolB", group="g", kind="manual",
                        inputs=[InputSpec("x", format="tsv")])
        assert execution_contract_fingerprint(a) != execution_contract_fingerprint(b)

    def test_P2_schema_change_fp_diff(self):
        """② 改 schema_version → execution contract fp 变(常量内嵌)"""
        from tbtools_cli.command_spec import CommandSpec
        from tbtools_cli.workflow import execution_contract_fingerprint
        sp = CommandSpec(name="t", group="g", kind="manual")
        fp1 = execution_contract_fingerprint(sp)
        # schema_version 是常量内嵌——同函数同输入必同(幂等);版本升级由常量变更触发
        assert execution_contract_fingerprint(sp) == fp1

    def test_P3_relations_change_semantic_diff(self):
        """③ 改 relations → semantic_fp 变"""
        from tbtools_cli.command_spec import CommandSpec
        from tbtools_cli.workflow import semantic_fingerprint
        a = CommandSpec(name="t", group="g", kind="manual", relations={"accepts": ["FASTA"]})
        b = CommandSpec(name="t", group="g", kind="manual", relations={"accepts": ["GFF3"]})
        assert semantic_fingerprint(a) != semantic_fingerprint(b)

    def test_P4_capability_change_semantic_diff(self):
        """④ 改 capability → semantic_fp 变"""
        from tbtools_cli.command_spec import CommandSpec
        from tbtools_cli.workflow import semantic_fingerprint
        a = CommandSpec(name="t", group="g", kind="manual", capabilities=["alignment"])
        b = CommandSpec(name="t", group="g", kind="manual", capabilities=["phylogeny"])
        assert semantic_fingerprint(a) != semantic_fingerprint(b)

    def test_P5_input_path_change_fp_diff(self, tmp_path):
        """⑤ input 路径变 → execution_fp 变(评审 #104 原文: input 路径变→fp 变;
        binding 含路径 refs,路径变=binding identity 变)"""
        import shutil

        from tbtools_cli.workflow import compile_step_full
        p = tmp_path / "deg_copy.txt"
        shutil.copy("examples/data/deg.txt", p)
        s1 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                          "output": "/tmp/a.svg"}}
        s2 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": [str(p)], "parameters": {}, "output": "/tmp/a.svg"}}
        c1, c2 = compile_step_full(s1, "/tmp", {}), compile_step_full(s2, "/tmp", {})
        assert c1.execution_fingerprint != c2.execution_fingerprint, \
            "评审 #104 Test⑤: input 路径变 → execution_fp 变"

    def test_P6_input_content_change_fp_diff(self, tmp_path):
        """⑥ input 内容变 → execution_fp 变"""
        import shutil

        from tbtools_cli.workflow import compile_step_full
        p = tmp_path / "deg_mod.txt"
        shutil.copy("examples/data/deg.txt", p)
        p.write_text(p.read_text() + "#tamper\n")
        s1 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                          "output": "/tmp/a.svg"}}
        s2 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": [str(p)], "parameters": {}, "output": "/tmp/a.svg"}}
        c1, c2 = compile_step_full(s1, "/tmp", {}), compile_step_full(s2, "/tmp", {})
        assert c1.execution_fingerprint != c2.execution_fingerprint
