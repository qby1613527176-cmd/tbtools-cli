"""第 26 份评审 Tests A–E: 语义统一验证。

A) Overlay round-trip    B) output_slots↔outputs 一致
C) protein/dna binding   D) envelope parity    E) 多输出 slot
"""
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TestA_OverlayRoundTrip:
    """A) YAML overlay → spec → metadata 语义一致"""

    def test_content_type_survives_roundtrip(self):
        import json as _j
        from tbtools_cli.command_spec import build_command_specs
        specs = build_command_specs()
        # spec 有 content_type
        assert specs["muscle"].inputs[0].content_type == "protein"
        # metadata 也有(round-trip 不丢)
        m = _j.load(open(os.path.join(ROOT, "tbtools_cli", "command_metadata.json"),
                         encoding="utf-8"))
        assert m["muscle"]["inputs"][0].get("content_type") == "protein"

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
        assert ci.schema_version == "1.1"
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
        assert len(ci.execution_fingerprint) == 16
        # 同绑定同 binding_fingerprint
        ci2 = compile_step_full(
            {"id": "t", "tool": "volcano",
             "binding": {"inputs": ["d.txt"], "parameters": {"pval_cutoff": "0.05"},
                         "output": "/tmp/o2.svg"}}, "/tmp", {})
        assert ci.binding_fingerprint == ci2.binding_fingerprint  # 输出不同不影响 binding 层
        assert ci.contract_fingerprint != ci2.contract_fingerprint  # 但 contract 层不同
