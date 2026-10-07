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
        """CommandSpec 集合 == metadata 集合(单一模型对齐, 防漂移) + 字段级比对
        (自审 arch N5 短期: 名字集合相同只是"巧合"——装饰器正则单侧漏检/错配时
        set 可能仍相等; 字段级比对把"两侧投影一致"变成保证)。"""
        specs = build_command_specs()
        meta = _meta()
        assert set(specs) == set(meta), \
            f"specs/metadata 不一致: 缺 {set(meta) - set(specs)}, 多 {set(specs) - set(meta)}"
        assert len(specs) >= 250
        # N5 短期: 字段级比对(kind/group/runner/help 投影全等)——
        # 任一命令单侧字段漂移(正则断链/无 docstring 错配下一条)即红
        _field_diffs = []
        for _n in sorted(specs):
            _s, _m = specs[_n], meta[_n]
            for _f, _sv, _mv in (("kind", _s.kind, _m.get("kind")),
                                 ("group", _s.group, _m.get("group")),
                                 ("runner", _s.runner, _m.get("runner")),
                                 ("help", _s.doc, _m.get("help"))):
                if _sv != _mv:
                    _field_diffs.append(f"{_n}.{_f}: specs={_sv!r} meta={_mv!r}")
        assert not _field_diffs, "specs/metadata 字段漂移(重跑 gen_metadata --render):\n" + "\n".join(_field_diffs[:10])
        # N5 发现 4: 无 docstring 命令被正则错配下一条 doc——非 tool 命令 doc 必须非空
        _empty_doc = [n for n, s in specs.items()
                      if s.kind != "tool" and not (s.doc or "").strip()]
        assert not _empty_doc, f"非 tool 命令 doc 空(可能被正则错配/漏扫): {_empty_doc[:10]}"

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
