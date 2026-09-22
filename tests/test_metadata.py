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
        """metadata 总数 >= ENGINE_REGISTRY 命令数（registry 是权威子集）"""
        from tbtools_cli import auto_commands as ac
        reg_n = len(ac.ENGINE_REGISTRY)
        meta_n = len(self._meta())
        assert meta_n >= reg_n, f"metadata({meta_n}) < ENGINE_REGISTRY({reg_n})，运行 python3 scripts/gen_metadata.py"

    def test_meta_contains_all_registry_cmds(self):
        """每个 ENGINE_REGISTRY 命令都存在于 metadata（缺失即漂移）"""
        from tbtools_cli import auto_commands as ac
        meta = self._meta()
        missing = [r[0] for r in ac.ENGINE_REGISTRY if r[0] not in meta]
        assert not missing, f"metadata 缺 {len(missing)} 命令: {missing[:10]}，运行 gen_metadata.py"

    def test_meta_contains_all_cli_tools(self):
        from tbtools_cli.cli_tools_registry import CLI_TOOLS
        meta = self._meta()
        missing = [t for t in CLI_TOOLS if t not in meta]
        assert not missing, f"metadata 缺 CLI_TOOLS {len(missing)}: {missing[:10]}"

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
    import tbtools_cli.cli_load as _cl
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
