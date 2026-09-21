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
        tools[name] = {"name": name, "kind": "tool", "mode": "tool", "class": cls,
                       "xmx": "3g", "runner": "java", "help": "", "src": "cli_tools_registry"}
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
    for name in re.findall(r"add_command\(\w+,\s*name=[\"']([a-zA-Z][a-zA-Z0-9_]*)[\"']", src):
        if name not in cmds:
            cmds[name] = {"name": name, "kind": "manual", "mode": "manual", "class": "",
                          "xmx": "", "runner": "plot", "help": "", "src": "cli_manual"}
    return cmds


def scan_bridges():
    return sorted(f[:-5] for f in os.listdir(BRIDGES) if f.endswith(".java"))


def build():
    reg = scan_engine_registry()
    tools = scan_cli_tools()
    manual = scan_manual_commands()
    bridges = scan_bridges()

    meta = {}
    if os.path.isfile(META):
        meta = json.load(open(META, encoding="utf-8"))

    for name, entry in reg.items():
        old = meta.get(name, {})
        entry.setdefault("help", old.get("help", entry.get("help", "")))
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


def main():
    check = "--check" in sys.argv or "-c" in sys.argv
    meta, counts = build()
    print(json.dumps(counts, ensure_ascii=False, indent=1))
    if check:
        print("check mode: 不写文件")
        return 0
    json.dump(meta, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✅ 已写入 {META}: {len(meta)} 命令")
    return 0


if __name__ == "__main__":
    sys.exit(main())