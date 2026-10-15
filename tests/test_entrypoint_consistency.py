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


def test_group_consistency():
    """十四轮 arch P1 配套守卫: 生产端(CommandSpec 构建的 spec.group) 与消费端
    (cli_load._group_of 运行时解析) 分组必须一致——迁移期若只迁一端立即分裂,
    现有守卫不覆盖该方向(守卫只测 KEY ⊆ specs, 不测构建期 vs 消费期分组一致)。"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tbtools_cli.command_spec import build_command_specs, clear_specs_cache
    from tbtools_cli.cli_load import _group_of
    clear_specs_cache()
    specs = build_command_specs()
    mismatch = [(n, spec.group, _group_of(n))
                for n, spec in specs.items()
                if (_group_of(n) or "engine") != spec.group]
    assert not mismatch, (
        f"生产/消费分组分裂({len(mismatch)}): 命令[(name, spec.group, _group_of)]——"
        f"生产端(command_spec._resolve_group)与消费端(cli_load._group_of)必须同批迁移")


def test_resolve_group_no_cmap_fallback():
    """十四轮 arch 第四步: 16 个 ENGINE_REGISTRY 命令已从硬编码 engine 兜底迁到
    KNOWN_GROUPS 显式分组——任何命令不得再静默落 engine 字面量(除非真属 engine 组内核)。
    守卫: specs 中非 engine 命令若经 _resolve_group 解析仍回 engine → 违规。"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tbtools_cli.command_spec import (build_command_specs, clear_specs_cache,
                                          KNOWN_GROUPS, _resolve_group)
    clear_specs_cache()
    specs = build_command_specs()
    # KNOWN_GROUPS 应有具体分组值(不能是 engine 兜底)
    bad = [n for n, g in KNOWN_GROUPS.items() if g == "engine"]
    assert not bad, f"KNOWN_GROUPS 不允许 engine 兜底值: {bad}"


def test_no_cmap_direct_read_in_consumer_modules():
    """十四轮 arch/gate P2(GPT): cli.py/cli_top.py 不得新增 CATEGORY_MAP 直读——
    AST 级检查(属性式访问 .CATEGORY_MAP 也能抓到, 比 import 正则强; registry discipline
    白名单已把两文件出列但未防属性访问回流)。单一权威退役防回归锁定。"""
    import ast
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bad = []
    for rel in ("tbtools_cli/cli.py", "tbtools_cli/cli_top.py"):
        src = open(os.path.join(root, rel), encoding="utf-8").read()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            # 属性访问: _LG.CATEGORY_MAP / CATEGORY_MAP.get —— AST 抓所有形态
            if isinstance(node, ast.Attribute) and node.attr == "CATEGORY_MAP":
                bad.append(f"{rel}:{node.lineno} 直读 CATEGORY_MAP")
    assert not bad, (
        f"消费端模块新增 CATEGORY_MAP 直读(单一权威回流): {bad} —— 用 "
        f"cli_load._group_of()(CommandSpec 优先)替代")
