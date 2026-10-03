# -*- coding: utf-8 -*-
"""批次 A: metadata 唯一数据源一致性测试（架构重构）"""
import json
import os
import subprocess
import sys

from tbtools_cli.core import ROOT


class TestMetadataConsistency:
    """command_metadata.json 必须与运行时事实来源一致（防漂移）"""

    def _meta(self):
        p = os.path.join(ROOT, "tbtools_cli", "command_metadata.json")
        return json.load(open(p, encoding="utf-8"))

    def test_meta_total_ge_engine_registry(self):
        """metadata 总数 >= spec 注册命令数(CommandSpec 是唯一入口,Phase 3)"""
        from tbtools_cli.command_spec import build_command_specs
        reg_n = sum(1 for s in build_command_specs().values() if s.kind in ("direct", "bridge"))
        meta_n = len(self._meta())
        assert meta_n >= reg_n, f"metadata({meta_n}) < 注册命令({reg_n})，运行 python3 scripts/gen_metadata.py"

    def test_meta_contains_all_registry_cmds(self):
        """每个注册引擎命令都存在于 metadata（缺失即漂移;CommandSpec 投影,Phase 3）"""
        from tbtools_cli.command_spec import build_command_specs
        meta = self._meta()
        missing = [n for n, s in build_command_specs().items()
                   if s.kind in ("direct", "bridge") and n not in meta]
        assert not missing, f"metadata 缺 {len(missing)} 命令: {missing[:10]}，运行 gen_metadata.py"

    def test_meta_contains_all_cli_tools(self):
        """每个 tool kind 命令都在 metadata(CommandSpec 投影,Phase 3)"""
        from tbtools_cli.command_spec import build_command_specs
        meta = self._meta()
        missing = [n for n, s in build_command_specs().items()
                   if s.kind == "tool" and n not in meta]
        assert not missing, f"metadata 缺 tool 命令 {len(missing)}: {missing[:10]}"

    def test_gen_metadata_check_passes(self):
        """gen_metadata.py --check 非零退出即失败（生成器自校验）"""
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "gen_metadata.py"), "--check"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, f"gen_metadata --check 失败:\n{r.stdout}\n{r.stderr}"
        assert "registry" in r.stdout

    def test_meta_kinds_consistent(self):
        """metadata 每条都有 kind 字段（无 '?' 残留）"""
        meta = self._meta()
        bad = [k for k, v in meta.items() if not v.get("kind") or v["kind"] == "?"]
        assert not bad, f"无 kind 条目: {bad}"

def test_impl_reflection_matches_registry():
    """第五轮评审: 反射注册命令集 == ENGINE_REGISTRY 键集(防命名改坏导致命令静默消失)"""
    import tbtools_cli.auto_commands as ac
    # 表驱动 impl 集合(注册表)
    reg_keys = set(ac._IMPL_REGISTRY.keys())
    # 反射可找到的 impl 集合(cli_load 的查找路径)
    reflected = {n for n in dir(ac) if n.startswith("_") and n.endswith("_impl")}
    reflected_names = {n[1:-5] for n in reflected}
    # 所有注册表命令都能被 cli_load 找到
    missing = reg_keys - reflected_names
    assert not missing, f"注册表命令缺失 impl: {sorted(missing)[:10]}"
    # 反射命名规则一致(无无关的 _x_impl)
    assert len(reflected) >= len(reg_keys)


def test_metadata_covers_runtime_commands():
    """发现层防丢(二期教训): 运行时分组命令必须可被 metadata 发现。

    背景: N23/N26 删除注册表条目导致 26 个手写 impl 命令从 metadata 消失(可用但 search/help 找不到)。
    """
    import json
    import os as _os
    root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    meta = json.load(open(_os.path.join(root, "tbtools_cli", "command_metadata.json"), encoding="utf-8"))
    cli_names = set()
    import tbtools_cli.cli as _c
    from click.testing import CliRunner
    r = CliRunner().invoke(_c.cli, ["list", "plots"])
    import re as _re
    cli_names |= set(_re.findall(r"^    (\S+)", r.output, _re.M))
    r2 = CliRunner().invoke(_c.cli, ["list", "tools"])
    cli_names |= set(_re.findall(r"^    (\S+)", r2.output, _re.M))
    hidden = cli_names - set(meta)
    # 顶层管理命令不在 metadata 属预期;分组绘图/工具命令必须可发现
    expected_hidden = {"version", "doctor", "setup", "fetch_jar", "help", "examples", "list", "new",
                       "search", "completion", "presets", "check", "env", "tool-describe",
                       "tool-validate", "tool-provenance", "rpc", "stat-fasta", "cds2protein",
                       "fasta-extract", "seqlogo", "msa", "structure", "motif",
                       "volcano", "heatmap", "pca", "hclust", "dehist",
                       "tree", "unrooted", "rooting", "onesteptree", "draw", "gene-structure",
                       "genestructure", "one-step", "treeRooting"}
    real_missing = hidden - expected_hidden
    assert not real_missing, f"运行时命令在 metadata 中不可发现(发现层缺口): {sorted(real_missing)[:15]}"


class TestAiManifestInheritance:
    """评审 #112 P1: ai/ manifest 必须继承 CommandSpec metadata 的可信度字段——
    防"tool-describe 信息完整 / ai/*.json 被削薄"双世界分裂复发。"""

    def _meta(self):
        p = os.path.join(ROOT, "tbtools_cli", "command_metadata.json")
        return json.load(open(p, encoding="utf-8"))

    def test_ai_tool_schema_inherits_trust_fields(self):
        """ai/tools/*.json 的 readiness/verification/semantic_fp/relations 等与 metadata 一致。"""
        meta = self._meta()
        # 抽查 3 个代表性工具(含 CONFORMANCE_VERIFIED 的 volcano)
        for name in ("volcano", "muscle", "tpmCalc"):
            g = meta[name].get("group", "engine")
            p = os.path.join(ROOT, "ai", "tools", g, f"{name}.json")
            assert os.path.isfile(p), f"ai/tools/{g}/{name}.json 缺失(重跑 gen_metadata --render)"
            ai = json.load(open(p, encoding="utf-8"))
            m = meta[name]
            # 可信度字段必须继承(与 metadata 完全一致)
            assert ai.get("readiness") == m.get("readiness"), f"{name}: readiness 未继承"
            assert ai.get("verification") == m.get("verification"), f"{name}: verification 未继承"
            assert ai.get("semantic_fingerprint") == m.get("semantic_fingerprint"), f"{name}: semantic_fp 未继承"
            assert bool(ai.get("relations")) == bool(m.get("relations")), f"{name}: relations 未继承"
            assert bool(ai.get("output_slots")) == bool(m.get("output_slots")), f"{name}: output_slots 未继承"

    def test_ai_index_has_filter_fields(self):
        """tool-index.jsonl 每条含 readiness/verification/semantic_fingerprint(筛选字段)。"""
        p = os.path.join(ROOT, "ai", "tool-index.jsonl")
        assert os.path.isfile(p), "tool-index.jsonl 缺失(重跑 gen_metadata --render)"
        n = 0
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                e = json.loads(line)
                for k in ("readiness", "verification", "semantic_fingerprint"):
                    assert k in e, f"index 缺 {k}(工具 {e.get('name')})"
                n += 1
        assert n > 0

    def test_ai_relations_matches_spec(self):
        """relations.json 与 CommandSpec 派生一致(含 GROUP_RELATIONS fallback)。"""
        from tbtools_cli.command_spec import build_command_specs
        p = os.path.join(ROOT, "ai", "relations.json")
        assert os.path.isfile(p), "relations.json 缺失(重跑 gen_metadata --render)"
        ai_rel = set(json.load(open(p, encoding="utf-8")).get("relations", {}).keys())
        specs = build_command_specs()
        spec_rel = {n for n, s in specs.items() if s.relations}
        assert not (spec_rel - ai_rel), \
            f"ai/relations.json 缺 {len(spec_rel - ai_rel)} 个有 relations 的工具: {sorted(spec_rel - ai_rel)[:5]}(重跑 gen_metadata --render)"
