#!/usr/bin/env python3
"""gen_metadata.py — command_metadata.json 唯一数据源生成器（架构重构批次 A）

合并事实来源 → 单一 metadata：
  1. ENGINE_REGISTRY（auto_commands.py 表驱动，172 命令）— 运行时权威
  2. 手动注册命令（cli.py @group.command，13 个）
  3. CLI_TOOLS（cli_tools_registry.py，82 工具）— 工具层
  4. bridges/*.java（118）— 桥索引

用法:
  python3 scripts/gen_metadata.py            # 生成（写 command_metadata.json + 打印断言）
  python3 scripts/gen_metadata.py --check    # 只校验一致性（CI/防漂移，不写文件）
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = os.path.join(ROOT, "tbtools_cli", "command_metadata.json")
AUTO = os.path.join(ROOT, "tbtools_cli", "auto_commands.py")
CLI = os.path.join(ROOT, "tbtools_cli", "cli.py")
REG = os.path.join(ROOT, "tbtools_cli", "cli_tools_registry.py")
BRIDGES = os.path.join(ROOT, "bridges")


def scan_engine_registry():
    """运行时导入 ENGINE_REGISTRY（auto_commands 模块级列表，权威来源）"""
    sys.path.insert(0, ROOT)
    from tbtools_cli import auto_commands as ac
    cmds = {}
    for (name, kind, cls, xmx, runner, doc) in ac.ENGINE_REGISTRY:
        cmds[name] = {"name": name, "kind": kind, "mode": kind, "class": cls,
                      "xmx": xmx, "runner": runner, "help": doc[:400], "src": "engine_registry"}
    return cmds


def scan_cli_tools():
    sys.path.insert(0, ROOT)
    from tbtools_cli.cli_tools_registry import CLI_TOOLS
    tools = {}
    for name, cls in CLI_TOOLS.items():
        # 类名末段 → 人类可读标题(rpkmCal → "rpkmCal (RpkmCal)")
        short = cls.split(".")[-1] if isinstance(cls, str) else str(cls)
        pretty = re.sub(r"(?<!^)(?=[A-Z])", " ", short) if short else name
        tools[name] = {"name": name, "kind": "tool", "mode": "tool", "class": cls,
                       "xmx": "3g", "runner": "java",
                       "help": f"{name}: {name} (tool, {short}) — {pretty}", "src": "cli_tools_registry"}
    return tools


def scan_manual_commands():
    src = open(CLI, encoding="utf-8").read()
    # 匹配 @seq_group.command("seqlogo") / @expr_group.command("heatmap2") / @cli.command()(顶层, 跳过)
    manual = re.findall(r"@(?:\w+_group|\w+)\.command\(\s*['\"]([a-zA-Z][a-zA-Z0-9_]*)['\"]", src)
    cmds = {}
    for name in manual:
        if name in ("list", "check", "doctor", "version", "new", "completion", "examples", "presets", "help", "setup", "fetch-jar"):
            continue  # 顶层命令(非分组绘图)
        cmds[name] = {"name": name, "kind": "manual", "mode": "manual", "class": "",
                      "xmx": "", "runner": "plot", "help": "", "src": "cli_manual"}
    # add_command 别名方式: @group.add_command(fn, name="alias")
    # 格式: seq_group.add_command(seqlogo, name="seqlogo") → 目标 fn 的命令名可查
    alias_map = {}
    for m in re.finditer(r"(\w+_group)\.add_command\((\w+),\s*name=[\"']([a-zA-Z][a-zA-Z0-9_]*)[\"']\)", src):
        grp, fn, alias = m.group(1), m.group(2), m.group(3)
        alias_map[alias] = (grp, fn)
    for alias, (grp, fn) in alias_map.items():
        if alias not in cmds:
            cmds[alias] = {"name": alias, "kind": "manual", "mode": "manual", "class": "",
                           "xmx": "", "runner": "plot", "help": "", "src": "cli_manual"}
        # 别名 help: 从主命令 docstring 或 fn 名对应命令借用
        if not cmds[alias].get("help"):
            for other, oc in cmds.items():
                if oc.get("src") == "cli_manual" and oc.get("help") and fn in (other, f"_{other}"):
                    cmds[alias]["help"] = f"(alias of {other}) " + oc["help"]
                    break
    # cli.py 手动命令 docstring 首行(补 help 空洞): 装饰器+def+docstring 联合匹配
    for m in re.finditer(
        r'@(?:\w+_group|\w+)\.command\(\s*[\"\']([a-zA-Z][a-zA-Z0-9_]*)[\"\']\)'
        r'[\s\S]*?^def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*\):\s*\"\"\"([^\n\"]*)',
        src, re.M):
        cmd, d = m.group(1), m.group(2).strip()[:200]
        if cmd in cmds and d:
            cmds[cmd]["help"] = d
    # auto_commands 手写 impl(注册为命令但不在 ENGINE_REGISTRY——N23/N26 后 msy/mirnatarget 等)
    # 否则这些命令从 metadata/search/help 消失(2026-09-22 二期发现)
    try:
        ac_src = open(os.path.join(os.path.dirname(CLI), "auto_commands.py"), encoding="utf-8").read()
        for m in re.finditer(r"^def _([a-zA-Z0-9]+)_impl\([^)]*\):\s*\"\"\"([^\n\"]*)", ac_src, re.M):
            name, docfirst = m.group(1), m.group(2).strip()
            if name in cmds or name in ("simplehmmscan", "longestorf"):
                continue
            cmds[name] = {"name": name, "kind": "manual", "mode": "manual", "class": "",
                          "xmx": "", "runner": "plot", "help": docfirst[:200], "src": "auto_manual"}
    except Exception:
        pass
    return cmds


def scan_bridges():
    return sorted(f[:-5] for f in os.listdir(BRIDGES) if f.endswith(".java"))


def build():
    reg = scan_engine_registry()
    tools = scan_cli_tools()
    manual = scan_manual_commands()
    bridges = scan_bridges()

    # 完全重建(第八轮评审): 不读旧 metadata——消除已删除命令的残影条目(统计污染源)
    meta = {}

    for name, entry in reg.items():
        meta[name] = entry
    for name, entry in tools.items():
        if name not in meta:
            meta[name] = entry
    for name, entry in manual.items():
        old = meta.get(name, {})
        entry.setdefault("help", old.get("help", ""))
        meta[name] = entry  # 覆盖: 手动命令补 kind=manual（保留旧 help）
    # tree 分组别名（显示名 ≠ 函数名）: draw→tree, one-step→onesteptree, rooting→treeRooting
    for alias, disp in (("tree", "draw"), ("onesteptree", "one-step"), ("treeRooting", "rooting")):
        if alias not in meta and disp in meta:
            meta[alias] = {"name": alias, "kind": "manual", "mode": "manual", "class": "",
                           "xmx": "", "runner": "plot", "help": meta[disp].get("help", ""),
                           "alias_of": disp, "src": "cli_manual"}

    # 兜底: 旧 metadata 遗留条目统一补 kind（兼容历史数据）
    for _v in meta.values():
        _v.setdefault("kind", "manual")
        _v.setdefault("mode", "manual")
    counts = {"registry": len(reg), "tools": len(tools), "bridges": len(bridges),
              "meta_total": len(meta),
              "plot_ish": sum(1 for v in meta.values() if v.get("kind") in ("bridge", "direct", "manual"))}
    return meta, counts


def render_commands_md(meta):
    """按分组生成全量命令清单 docs/_generated/commands.md（metadata 驱动,防漂移）"""
    sys.path.insert(0, ROOT)
    from tbtools_cli.cli_load import CATEGORY_MAP, GROUPS
    out_dir = os.path.join(ROOT, "docs", "_generated")
    os.makedirs(out_dir, exist_ok=True)
    lines = ["# 命令全量清单（自动生成,勿手改）",
             "",
             "> 由 `python3 scripts/gen_metadata.py --render` 生成,来源 command_metadata.json。",
             "> 分组归类参考 cli_load.CATEGORY_MAP;数字防漂移由 gen_metadata.py --check 与 pytest 保证。",
             ""]
    # 分组 → 命令
    grouped = {}
    for name, v in meta.items():
        cat = CATEGORY_MAP.get(name, "engine")
        grouped.setdefault(cat, []).append((name, v))
    for cat in sorted(GROUPS.keys()):
        if cat not in grouped:
            continue
        cmds = grouped[cat]
        lines.append(f"## {cat} — {GROUPS.get(cat, cat)}（{len(cmds)} 个）")
        lines.append("")
        lines.append("| 命令 | 类型 | 说明 |")
        lines.append("|---|---|---|")
        for name, v in sorted(cmds):
            kind = v.get("kind", "?")
            icon = {"bridge": "桥", "direct": "直连", "tool": "工具", "manual": "手动"}.get(kind, kind)
            desc = (v.get("help", "") or "").split("#")[-1].strip() or (v.get("help", "") or "")[:40]
            if ":" in desc:
                desc = desc.split(":", 1)[-1].strip()
            lines.append(f"| `{name}` | {icon} | {desc[:60]} |")
        lines.append("")
    # 数字统计(权威口径)
    from collections import Counter
    kinds = Counter(v.get("kind", "?") for v in meta.values())
    lines.append("## 统计")
    lines.append("")
    lines.append(f"- 命令总数: {len(meta)}")
    for k, n in kinds.most_common():
        lines.append(f"- {k}: {n}")
    lines.append("")
    path = os.path.join(out_dir, "commands.md")
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    print(f"✅ 已生成 {path}（{len(meta)} 命令,{len(lines)} 行）")

    # 权威数字摘要(README/徽章/文档口径单一源)
    import tbtools_cli.auto_commands as _ac
    import tbtools_cli.cli_tools_registry as _reg
    import tbtools_cli.core as _core
    n_plot = sum(1 for v in meta.values() if v.get("kind") in ("bridge", "direct", "manual"))
    n_auto = sum(1 for n in dir(_ac) if n.startswith("_") and n.endswith("_impl") and not n.startswith("__"))
    counts = {
        "metadata_commands": len(meta),          # 276: 唯一数据源全量
        "plot_commands_meta": n_plot,            # 196: metadata 中非工具类(静态口径)
        "auto_commands": n_auto,                 # 201: 引擎注册表驱动的命令数
        "rpc_methods": 188,                      # RPC 方法(固定)
        "tools": len(_reg.CLI_TOOLS),            # 82: 工具注册表
        "bridges": len([f for f in os.listdir(os.path.join(ROOT, "bridges")) if f.endswith(".java")]),  # 118
        "pitfall_hints": len(_core.PITFALL_HINTS),  # 46
    }
    # 注: README/`tbtools version` 的 "218 绘图/分析命令" 是运行时全部分组命令数
    # (含 engine 分组等),与 plot_commands_meta(静态注册口径)不同——两个口径都合法,勿互改
    counts_path = os.path.join(out_dir, "counts.md")
    with open(counts_path, "w", encoding="utf-8") as f:
        f.write("# 权威数字(自动生成,勿手改)\n\n")
        for k, v in counts.items():
            f.write(f"- {k}: {v}\n")
    print(f"✅ 已生成 {counts_path}: {counts}")


def main():
    check = "--check" in sys.argv or "-c" in sys.argv
    render = "--render" in sys.argv or "-r" in sys.argv
    meta, counts = build()
    print(json.dumps(counts, ensure_ascii=False, indent=1))
    if check:
        # CommandSpec 模型一致性(第八轮评审: 单一模型接管的第一步校验)
        try:
            import sys as _sys
            _sys.path.insert(0, ROOT)
            from tbtools_cli.command_spec import build_command_specs
            specs = build_command_specs()
            spec_names = set(specs)
            meta_names = set(meta)
            if spec_names != meta_names:
                print(f"❌ CommandSpec 模型与 metadata 不一致: 模型多 {len(spec_names - meta_names)} 个, 缺 {len(meta_names - spec_names)} 个")
                return 1
            print(f"✅ CommandSpec 模型一致性: {len(spec_names)} 命令对齐")
        except ImportError:
            pass
        print("check mode: 不写文件")
        return 0
    json.dump(meta, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✅ 已写入 {META}: {len(meta)} 命令")
    if render:
        render_commands_md(meta)
    return 0


if __name__ == "__main__":
    sys.exit(main())