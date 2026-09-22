#!/usr/bin/env python3
"""同步 docs/commands.md(自动生成清单 → mkdocs 页面)。

由 .github/workflows/docs.yml 构建时调用,防 metadata 更新后快照漂移。
来源: docs/_generated/commands.md(gen_metadata.py --render 生成)。
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "docs", "_generated", "commands.md")
DST = os.path.join(ROOT, "docs", "commands.md")

gen = open(GEN, encoding="utf-8").read()
header = "# 命令清单(自动生成)\n\n> 由 `scripts/gen_metadata.py --render` 生成,构建时刷新,勿手改。\n\n"
open(DST, "w", encoding="utf-8").write(header + gen)
print(f"✅ docs/commands.md 已同步({len(gen.splitlines())} 行)")
