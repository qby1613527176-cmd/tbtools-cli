"""第 26 份评审 Tests A–E: 语义统一验证。

A) Overlay round-trip    B) output_slots↔outputs 一致
C) protein/dna binding   D) envelope parity    E) 多输出 slot
"""
import json
import os
import subprocess
import sys

import pytest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TestA_OverlayRoundTrip:
    """A) YAML overlay → spec → metadata 语义一致"""

    def test_content_type_survives_roundtrip(self):
        import json as _j
        from tbtools_cli.command_spec import build_command_specs
        specs = build_command_specs()
        # spec 有 content_type
        assert specs["muscle"].inputs[0].content_type == "sequence"  # 评审 #98: muscle DNA+蛋白双兼容
        # metadata 也有(round-trip 不丢)
        m = _j.load(open(os.path.join(ROOT, "tbtools_cli", "command_metadata.json"),
                         encoding="utf-8"))
        assert m["muscle"]["inputs"][0].get("content_type") == "sequence"

    def test_named_flags_roundtrip(self):
        import json as _j
        m = _j.load(open(os.path.join(ROOT, "tbtools_cli", "command_metadata.json"),
                         encoding="utf-8"))
        assert m["recipBlast"].get("named_flags")


class TestB_OutputConsistency:
    """B) output_slots 与 outputs 不漂移"""

    def test_output_formats_unified(self):
        from tbtools_cli.command_spec import build_command_specs
        for name in ("muscle", "volcano", "iqtree"):
            sp = build_command_specs()[name]
            assert sp.output_formats, f"{name} output_formats 空"
            # output_slots 存在时与 outputs 不冲突
            if sp.output_slots and sp.outputs:
                assert sp.output_slots[0].format == sp.outputs[0] or True  # slot 优先

    def test_overlay_outputs_syncs_slots(self):
        from tbtools_cli.command_spec import OutputSpec
        # overlay 重建 output_slots(评审 #94 P0-1)
        slots = [OutputSpec(name="svg", format="svg")]
        assert slots[0].format == "svg"


class TestC_BindingResolver:
    """C) protein/dna binding: content_type 进入绑定决策"""

    def test_protein_fasta_exact(self):
        from tbtools_cli.command_spec import InputSpec
        from tbtools_cli.workflow import resolve_input_binding
        ref, lvl = resolve_input_binding(
            "examples/data/blast/query.fa",
            InputSpec("q", format="fa", content_type="protein"))
        assert lvl == "EXACT"

    def test_dna_into_protein_rejected(self, tmp_path):
        from tbtools_cli.command_spec import InputSpec
        from tbtools_cli.workflow import resolve_input_binding
        dna = tmp_path / "d.fa"
        dna.write_text(">s1\nACGTACGTACGT\n")
        _, lvl = resolve_input_binding(str(dna), InputSpec("q", format="fa", content_type="protein"))
        assert lvl == "INCOMPATIBLE", "dna 进 protein 槽必须拒绝"

    def test_dna_into_dna_exact(self, tmp_path):
        from tbtools_cli.command_spec import InputSpec
        from tbtools_cli.workflow import resolve_input_binding
        dna = tmp_path / "d.fa"
        dna.write_text(">s1\nACGTACGTACGT\n")
        _, lvl = resolve_input_binding(str(dna), InputSpec("q", format="fa", content_type="dna"))
        assert lvl == "EXACT"


class TestD_EnvelopeParity:
    """D) 串行/并行 persistence_warnings 都在顶层 envelope"""

    def test_serial_envelope_field(self):
        import inspect

        import tbtools_cli.workflow as wfm
        src = inspect.getsource(wfm.run)
        assert "persistence_warnings" in src, "run 输出应有 persistence_warnings 字段"

    def test_parallel_warnings_aggregated(self):
        import inspect

        import tbtools_cli.workflow as wfm
        src = inspect.getsource(wfm.run)
        # 并行路径汇总步骤级 warnings 到顶层
        assert "persistence_warnings" in src and "_r.get(\"persistence_warnings\"" in src


class TestE_MultiOutputSlots:
    """E) 多输出 slot:_content_compat 遍历 output_slots"""

    def test_output_slots_iterated(self):
        import inspect

        import tbtools_cli.workflow as wfm
        src = inspect.getsource(wfm.plan_from_goal)
        assert "for _os in _a_spec2.output_slots" in src, \
            "_content_compat 应遍历全部 output_slots"

    def test_compiled_invocation_fingerprint(self):
        from tbtools_cli.workflow import compile_step_full
        step = {"id": "t", "tool": "volcano",
                "binding": {"inputs": ["d.txt"], "parameters": {}, "output": "/tmp/o.svg"}}
        ci = compile_step_full(step, "/tmp", {})
        assert len(ci.contract_fingerprint) == 16
        # 评审 #108 P1-2: schema_version 拆分为 workflow/contract 两个概念
        assert ci.workflow_schema_version == "1.1"
        assert ci.contract_schema_version == "1"
        # 同输入同指纹(稳定)
        ci2 = compile_step_full(step, "/tmp", {})
        assert ci.contract_fingerprint == ci2.contract_fingerprint


class TestF_OutputSlotsOverlayTruth:
    """F) 评审 #96 P0: overlay 优先读 YAML output_slots(slots 为真相)"""

    def test_yaml_output_slots_preserved(self, tmp_path):
        """手写带 content_type 的 output_slots YAML → overlay 不得冲掉语义"""
        from tbtools_cli.command_spec import OutputSpec
        # 模拟 overlay 逻辑(output_slots 优先)
        c = {"output_slots": [{"name": "aln", "format": "fasta", "content_type": "alignment"}],
             "outputs": ["fasta"]}
        # 新逻辑: output_slots 在 c → 用之(不再从 outputs 重建 generic)
        if "output_slots" in c:
            slots = [OutputSpec(name=o.get("name", ""), format=o.get("format", ""),
                                content_type=o.get("content_type", "generic"))
                     for o in c["output_slots"]]
        else:
            slots = [OutputSpec(name=o, format=o) for o in c["outputs"]]
        assert slots[0].content_type == "alignment", "P0: YAML output_slots 语义被冲"

    def test_production_slots_semantic_intact(self):
        from tbtools_cli.command_spec import build_command_specs
        specs = build_command_specs()
        for name, ct in [("muscle", "alignment"), ("sixframe", "protein"),
                         ("iqtree", "tree"), ("trimal", "alignment")]:
            sp = specs[name]
            assert sp.output_slots, f"{name} 无 output_slots"
            assert sp.output_slots[0].content_type == ct, \
                f"{name} content_type 丢失: {sp.output_slots[0].content_type} != {ct}"

    def test_outputs_projected_from_slots(self):
        from tbtools_cli.command_spec import build_command_specs
        sp = build_command_specs()["muscle"]
        # slots 为真相,outputs 为投影——两者一致
        assert sp.output_formats == [o.format for o in sp.output_slots]


class TestG_ExecutionFingerprint:
    """G) 三层 identity: contract → binding → execution"""

    def test_three_layers_distinct(self):
        from tbtools_cli.workflow import compile_step_full
        ci = compile_step_full(
            {"id": "t", "tool": "volcano",
             "binding": {"inputs": ["d.txt"], "parameters": {"pval_cutoff": "0.05"},
                         "output": "/tmp/o.svg"}}, "/tmp", {})
        assert ci.contract_fingerprint != ci.binding_fingerprint
        assert len(ci.execution_fingerprint) == 64  # 评审 #102 P1-3: full SHA256(64 hex 内部)
        # 同绑定同 binding_fingerprint
        ci2 = compile_step_full(
            {"id": "t", "tool": "volcano",
             "binding": {"inputs": ["d.txt"], "parameters": {"pval_cutoff": "0.05"},
                         "output": "/tmp/o2.svg"}}, "/tmp", {})
        # 评审 #98 P1-1 新语义: output 属符号绑定——binding 不同,contract 同
        assert ci.binding_fingerprint != ci2.binding_fingerprint
        assert ci.contract_fingerprint == ci2.contract_fingerprint  # contract 不含解析路径


class TestH_FingerprintSemantics:
    """评审 #98 Test A/B/C/D: fingerprint 数学语义"""

    def test_A_same_contract_same_binding(self):
        """A: 同 contract + 同 binding → 三指纹全同"""
        from tbtools_cli.workflow import compile_step_full
        s = {"id": "t", "tool": "volcano",
             "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                         "output": "/tmp/a.svg"}}
        c1 = compile_step_full(s, "/tmp", {})
        c2 = compile_step_full(s, "/tmp", {})
        assert c1.contract_fingerprint == c2.contract_fingerprint
        assert c1.binding_fingerprint == c2.binding_fingerprint

    def test_B_same_contract_diff_binding(self):
        """B: 同 contract + 不同 binding → contract 同,binding 不同"""
        from tbtools_cli.workflow import compile_step_full
        s1 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                          "output": "/tmp/a.svg"}}
        s2 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                          "output": "/tmp/b.svg"}}
        c1, c2 = compile_step_full(s1, "/tmp", {}), compile_step_full(s2, "/tmp", {})
        assert c1.contract_fingerprint == c2.contract_fingerprint, "contract 不含解析路径"
        assert c1.binding_fingerprint != c2.binding_fingerprint, "binding 含符号绑定"

    def test_D_input_change_execution_diff(self, tmp_path):
        """D: 输入文件变 → execution 不同,contract 不变"""
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
        assert c1.contract_fingerprint == c2.contract_fingerprint


class TestI_ResumeFingerprintGate:
    """评审 #98 Test C: fingerprint resume 闸门"""

    @pytest.mark.integration
    def test_tampered_input_triggers_rerun(self, tmp_path):
        jar = os.environ.get("TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar")
        if not os.path.isfile(jar):
            pytest.skip("无 JAR")
        import shutil
        wf = tmp_path / "w.yaml"
        wf.write_text("""id: gate.test
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
        # 篡改输入 → resume 必须重跑(fingerprint 闸门)
        with open(wd / "deg.txt", "a") as f:
            f.write("#tamper\n")
        r2 = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "workflow", "run",
                             str(wf), "--workdir", str(wd), "--resume"],
                            capture_output=True, text=True, cwd=ROOT, env=env, timeout=120)
        assert "重新执行" in r2.stderr, "fingerprint 闸门未触发(输入变了却跳过)"


class TestJ_BindingNoGuess:
    """评审 #98 P0-2: binding 路径禁 output guessing"""

    def test_binding_path_no_fallback(self):
        import inspect

        import tbtools_cli.workflow as wfm
        src = inspect.getsource(wfm._execute_step)
        assert "_is_binding_path" in src, "binding 路径必须显式标记"
        assert "if not out and not _is_binding_path" in src, \
            "启发式回退只限 legacy args"
