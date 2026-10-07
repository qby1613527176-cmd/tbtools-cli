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
        # 评审 #114: v2 --check 输出为 Generated Surface 一致性(旧 "registry" 字样已随
        # renderer 自报 surface 改造消失)
        assert "Generated Surface 一致性" in r.stdout

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


class TestVerificationDetailsProjection:
    """评审 #112 P1: verification 证据对象投影——ai/tools/*.json 不只 level,
    还有绑定证据(verified_at/corpus/contract_fingerprint), Agent 可判断证据新旧。"""

    def _meta(self):
        p = os.path.join(ROOT, "tbtools_cli", "command_metadata.json")
        return json.load(open(p, encoding="utf-8"))

    def test_executed_tools_have_verification_details(self):
        """EXECUTION/CONFORMANCE_VERIFIED 工具必须带 verification_details(证据对象)。"""
        meta = self._meta()
        _n = 0
        for name, m in meta.items():
            if m.get("verification") not in ("EXECUTION_VERIFIED", "CONFORMANCE_VERIFIED"):
                continue
            g = m.get("group", "engine")
            p = os.path.join(ROOT, "ai", "tools", g, f"{name}.json")
            assert os.path.isfile(p), f"{name}: ai schema 缺失"
            ai = json.load(open(p, encoding="utf-8"))
            det = ai.get("verification_details")
            assert det, f"{name}: 执行验证工具缺 verification_details(证据对象未投影)"
            for k in ("contract_fingerprint", "verified_at", "corpus"):
                assert k in det, f"{name}: details 缺 {k}"
            _n += 1
        assert _n >= 5, f"应至少 5 个执行验证工具, 实际 {_n}(重跑 gen_metadata --render)"


class TestGeneratedSurfaceFreshness:
    """评审 #113 P1-3: Generated Surface freshness——所有 Agent-facing 视图必须共享
    同一份最新 verification 事实(防 44/33/26 漂移复发)。"""

    def _meta(self):
        p = os.path.join(ROOT, "tbtools_cli", "command_metadata.json")
        return json.load(open(p, encoding="utf-8"))

    def test_verification_consistent_across_surfaces(self):
        """抽查 5 个执行验证工具: runtime(CommandSpec) == metadata == ai == yaml verification。"""
        import yaml
        from tbtools_cli.command_spec import build_command_specs, verification_level
        specs = build_command_specs(force=True, _skip_overlay=True)
        meta = self._meta()
        samples = ["volcano", "pca", "pafviz", "gel", "memeViz"]
        for name in samples:
            rv = verification_level(specs[name])
            mv = meta[name].get("verification")
            assert rv == mv, f"{name}: runtime={rv} != metadata={mv}(重跑 gen_metadata --render)"
            g = meta[name].get("group", "engine")
            ai = json.load(open(os.path.join(ROOT, "ai", "tools", g, f"{name}.json"), encoding="utf-8"))
            assert ai.get("verification") == mv, f"{name}: ai={ai.get('verification')} != metadata={mv}"
            yp = os.path.join(ROOT, "contracts", "tools", f"{name}.yaml")
            if os.path.isfile(yp):
                yc = yaml.safe_load(open(yp, encoding="utf-8"))
                assert yc.get("verification") == mv, f"{name}: yaml={yc.get('verification')} != metadata={mv}"

    def test_counts_equals_live_census(self):
        """counts.md 的 execution_verified == 运行时 census(EXECUTION_VERIFIED + CONFORMANCE_VERIFIED)。"""
        from tbtools_cli.command_spec import verification_census
        c = verification_census()
        live = c.get("EXECUTION_VERIFIED", 0) + c.get("CONFORMANCE_VERIFIED", 0)
        counts = {}
        with open(os.path.join(ROOT, "docs", "_generated", "counts.md"), encoding="utf-8") as f:
            for line in f:
                if line.startswith("- "):
                    k, _, v = line[2:].strip().partition(": ")
                    counts[k] = int(v)
        assert counts.get("execution_verified") == live, \
            f"counts.md={counts.get('execution_verified')} != live census={live}(重跑 gen_metadata --render)"

    def test_verified_tools_single_layer(self):
        """report 的 verified_tools 单层 evidence map 完整(防 list/details 两段式不一致)。"""
        p = os.path.join(ROOT, "tests", "verification_report.json")
        rep = json.load(open(p, encoding="utf-8"))
        vt = rep.get("verified_tools") or {}
        exec_list = set(rep.get("execution_verified", []))
        # verified_tools 必须覆盖全部 execution_verified
        missing = exec_list - set(vt.keys())
        assert not missing, f"verified_tools 缺 {sorted(missing)[:5]}(单层 map 不完整)"
        # 每个都有 contract_fingerprint
        for t, ev in vt.items():
            assert ev.get("contract_fingerprint"), f"{t}: verified_tools 缺 contract_fingerprint"
            assert ev.get("level") in ("EXECUTION_VERIFIED", "CONFORMANCE_VERIFIED")


def test_dry_run_flag_aware_precheck():
    """product P1-1(v1.4.91 五视角): dry-run 预检必须 flag-aware——
    带 --pval-cutoff 0.01 的 volcano 不再误报 flag/flag 值缺失; barplot 列名
    (Term/Pvalue)不误伤(v1.4.87 三度误伤教训); 真缺路径仍拦。"""
    import subprocess
    import json

    def _dry(*args, expect_exit=0):
        r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "tool-run",
                            "--dry-run", "--json", *args],
                           capture_output=True, text=True, timeout=60, cwd=ROOT)
        assert r.returncode == expect_exit, f"exit {r.returncode} != {expect_exit}: {r.stderr}"
        return json.loads(r.stdout)

    # 带可选 flag: 不误报(--pval-cutoff 是 flag, 0.01 是它的值)
    d = _dry("expr", "volcano", "--pval-cutoff", "0.01",
             "examples/data/deg.txt", "/tmp/v.svg")
    assert d["inputs_valid"] is True, f"flag 值被误报: {d.get('problems')}"
    # barplot 列名参数: 不误伤
    d2 = _dry("expr", "barplot", "examples/data/misc/enrich.tsv",
              "/tmp/b.svg", "Term", "Pvalue")
    assert d2["inputs_valid"] is True, f"列名被误报: {d2.get('problems')}"
    # 真缺路径: 仍拦(dry-run 缺输入 exit 3, JSON 仍在 stdout)
    d3 = _dry("expr", "volcano", "--inFile", "/no/way.tsv", expect_exit=3)
    assert d3["inputs_valid"] is False and d3.get("problems")
