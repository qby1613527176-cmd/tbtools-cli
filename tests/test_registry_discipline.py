"""CommandSpec 唯一读取入口纪律(评审 #64 P0-4):
新模块/新功能禁止直接 import legacy registry(ENGINE_REGISTRY/CLI_TOOLS/CATEGORY_MAP)。
白名单: command_spec(构建源)/cli_load(分组兼容)/gen_metadata(扫描)/auto_commands(注册本体)。
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

WHITELIST = {
    "tbtools_cli/command_spec.py",      # 构建源(从 legacy 读取以投影)
    "tbtools_cli/cli_load.py",          # CATEGORY_MAP 定义+_group_of 兼容层
    "tbtools_cli/auto_commands.py",     # ENGINE_REGISTRY 本体
    "tbtools_cli/cli_tools_registry.py",  # CLI_TOOLS 本体
    "scripts/gen_metadata.py",          # 扫描器
    "tests/test_registry_discipline.py",
    "tests/test_cli.py",
    "tests/test_contract.py",
    "tests/test_command_spec.py",
    # Phase 2 过渡期存量(评审 #64; 目标: Phase 3 全部迁移到 CommandSpec 后从此清单删除)
    "tbtools_cli/cli.py",               # 存量: CLI_TOOLS 引用
    "tbtools_cli/cli_top.py",           # 存量: ENGINE_REGISTRY/CLI_TOOLS 引用
    "tests/test_metadata.py",           # 存量: CLI_TOOLS 断言
}

LEGACY_PATTERNS = [
    (re.compile(r"from tbtools_cli\.auto_commands import (?!_make_impl)"), "ENGINE_REGISTRY/auto_commands"),
    (re.compile(r"from tbtools_cli\.cli_tools_registry import"), "CLI_TOOLS"),
    (re.compile(r"from tbtools_cli\.cli_load import CATEGORY_MAP"), "CATEGORY_MAP"),
]


class TestRegistryDiscipline:
    def test_no_new_legacy_imports(self):
        violations = []
        for py in list(ROOT.glob("tbtools_cli/**/*.py")) + list(ROOT.glob("scripts/*.py")) + list(ROOT.glob("tests/*.py")):
            rel = str(py.relative_to(ROOT))
            if rel in WHITELIST:
                continue
            src = py.read_text(encoding="utf-8")
            for pat, what in LEGACY_PATTERNS:
                if pat.search(src):
                    violations.append(f"{rel}: import {what}")
        assert not violations, "新模块直接 import legacy registry(应用 CommandSpec):\n" + "\n".join(violations)
