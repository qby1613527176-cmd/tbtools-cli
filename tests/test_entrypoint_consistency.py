"""入口一致性守卫(十三轮 docs P2): CommandSpec 是唯一正式契约入口——
所有命令来源(tbplot.sh 兼容层 / CATEGORY_MAP 分组)必须 ⊆ specs, 防幽灵工具
(gxfSort 教训: 只在 CATEGORY_MAP、其余 5 源零命中, 现存守卫无一能发现)。"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _specs_set():
    from tbtools_cli.command_spec import build_command_specs
    return set(build_command_specs().keys())


def test_cmap_keys_subset_of_specs():
    """CATEGORY_MAP 每个键都应有 CommandSpec(十三轮 docs P2-1: gxfSort 曾只在此源)"""
    from tbtools_cli.cli_load import CATEGORY_MAP
    specs = _specs_set()
    missing = sorted(set(CATEGORY_MAP) - specs)
    assert not missing, (
        f"CATEGORY_MAP 幽灵工具(无 CommandSpec): {missing} —— 新增工具必须走 CommandSpec,"
        f" 或从 CATEGORY_MAP 移除(gxfSort 先例)")


def test_tbplot_sh_cmds_subset_of_specs():
    """tbplot.sh 兼容层命令 ⊆ specs(动态加载来源; 防只存在脚本无契约)"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    content = open(os.path.join(root, "bin", "tbplot.sh"), encoding="utf-8").read()
    cmds = set(re.findall(r"^  ([a-zA-Z][a-zA-Z0-9]+)\)$", content, re.MULTILINE))
    specs = _specs_set()
    missing = sorted(cmds - specs)
    assert not missing, (
        f"tbplot.sh 命令无 CommandSpec: {missing} —— 兼容层命令也应有契约(单一权威)")


def test_specs_census_stable():
    """specs 总量稳定在权威计数(298)附近——防幽灵工具加入后 silently 膨胀。
    反方向(来源覆盖 specs)不适用: specs 含 engine/tool registry + manual scans +
    别名等多来源(92 个 tool/bridge/manual 命令不经 tbplot.sh/CATEGORY_MAP, 是合法
    的 registry/manual 来源)——正向守卫(来源 ⊆ specs)才是防幽灵的正确方向。"""
    specs = _specs_set()
    assert 280 <= len(specs) <= 320, f"specs 总量异常: {len(specs)}(权威 298±22)"
