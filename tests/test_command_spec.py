"""CommandSpec 统一命令模型测试(第八轮评审核心建议骨架)。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tbtools_cli.command_spec import CommandSpec, build_command_specs


def _meta():
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "tbtools_cli", "command_metadata.json")
    return json.load(open(p, encoding="utf-8"))


class TestCommandSpec:
    def test_specs_match_metadata(self):
        """CommandSpec 集合 == metadata 集合(单一模型对齐, 防漂移)"""
        specs = build_command_specs()
        meta = _meta()
        assert set(specs) == set(meta), \
            f"specs/metadata 不一致: 缺 {set(meta) - set(specs)}, 多 {set(specs) - set(meta)}"
        assert len(specs) >= 250

    def test_spec_dataclass(self):
        s = CommandSpec(name="x", group="expr", kind="direct")
        assert s.name == "x" and s.status == "stable" and s.aliases == []

    def test_core_specs_exist(self):
        specs = build_command_specs()
        for cmd, group in [("volcano", "expr"), ("venn2", "sets"), ("heatmap", "expr")]:
            assert cmd in specs, f"缺 {cmd}"
            s = specs[cmd]
            assert s.kind in ("bridge", "direct", "tool", "manual")

    def test_kinds_distribution(self):
        specs = build_command_specs()
        kinds = {}
        for s in specs.values():
            kinds[s.kind] = kinds.get(s.kind, 0) + 1
        assert kinds.get("bridge", 0) >= 90
        assert kinds.get("direct", 0) >= 60
        assert kinds.get("tool", 0) >= 70
        assert kinds.get("manual", 0) >= 10

    def test_schemas_for_core(self):
        """核心命令有 inputs/outputs schema(二期样例)"""
        specs = build_command_specs()
        for cmd in ("volcano", "venn2", "msy", "genestructure", "tableMerge"):
            assert specs[cmd].inputs, f"{cmd} 缺 inputs schema"
            assert specs[cmd].outputs, f"{cmd} 缺 outputs schema"
