"""tbtools-cli 测试套件 — 验证 click 框架 + 命令注册 + help 质量"""
import pytest
import subprocess
import sys
import os

# 确保 tbtools_cli 可导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tbtools_cli.cli import cli, _groups, GROUPS, CATEGORY_MAP
from tbtools_cli.core import PITFALL_HINTS, validate_file, detect_format
from tbtools_cli.presets import PRESETS, apply_preset
import tbtools_cli.auto_commands as auto_commands

JAR = os.environ.get("TBTOOLS_JAR", "")
HAS_JAR = bool(JAR and os.path.isfile(JAR))

def run_cli(*args):
    """运行 tbtools CLI 命令，返回 (exit_code, stdout, stderr)"""
    result = subprocess.run(
        [sys.executable, "-m", "tbtools_cli.cli"] + list(args),
        capture_output=True, text=True, timeout=30
    )
    return result.returncode, result.stdout, result.stderr


# ============ 1. 框架加载 ============

class TestFrameworkLoad:
    def test_cli_group_exists(self):
        assert cli is not None

    def test_groups_registered(self):
        expected = {"seq", "expr", "tree", "syn", "sets", "chipseq",
                    "asm", "gxf", "mirna", "table", "blast", "fastq",
                    "hmm", "gwas", "engine"}
        for g in expected:
            assert g in _groups, f"Group '{g}' not registered"

    def test_auto_commands_loaded(self):
        impls = [n for n in dir(auto_commands)
                 if n.startswith('_') and n.endswith('_impl') and not n.startswith('__')]
        assert len(impls) >= 127, f"Expected >=127 auto_commands, got {len(impls)}"

    def test_pitfall_hints_count(self):
        assert len(PITFALL_HINTS) == 30, f"Expected 30 pitfall hints, got {len(PITFALL_HINTS)}"

    def test_pitfall_hints_no_double_emoji(self):
        for k, v in PITFALL_HINTS.items():
            assert not v.startswith('⚠️'), f"Pitfall '{k}' starts with ⚠️ (causes double emoji)"

    def test_presets_count(self):
        assert len(PRESETS) >= 7, f"Expected >=7 presets, got {len(PRESETS)}"


# ============ 2. 顶层命令 ============

class TestTopLevelCommands:
    def test_help_no_args(self):
        ec, out, err = run_cli()
        assert ec == 0
        assert "绘图" in out or "143" in out

    def test_version(self):
        ec, out, err = run_cli("version")
        assert ec == 0
        assert "tbtools-cli" in out
        assert "绘图" in out

    def test_doctor(self):
        ec, out, err = run_cli("doctor")
        # doctor 可能因 JAR 未配置返回 1，但应输出检查结果
        assert "✅" in out or "❌" in out

    def test_presets_list(self):
        ec, out, err = run_cli("presets")
        assert ec == 0
        assert "nature" in out
        assert "cell" in out

    def test_presets_detail(self):
        ec, out, err = run_cli("presets", "nature")
        assert ec == 0
        assert "nature" in out
        assert "89" in out  # width

    def test_presets_unknown(self):
        ec, out, err = run_cli("presets", "nonexistent")
        assert ec == 1
        assert "❌" in out


# ============ 3. list 命令 ============

class TestListCommand:
    def test_list_plots(self):
        ec, out, err = run_cli("list", "plots")
        assert ec == 0
        assert "seq" in out
        assert "expr" in out

    def test_list_tools(self):
        ec, out, err = run_cli("list", "tools")
        assert ec == 0
        # 不应包含绘图命令
        assert "volcano" not in out
        assert "heatmap" not in out

    def test_list_rpc(self):
        ec, out, err = run_cli("list", "rpc")
        assert ec == 0
        assert "188" in out

    def test_list_no_arg(self):
        ec, out, err = run_cli("list")
        assert ec == 0
        assert "绘图" in out


# ============ 4. venn2/3/4 ============

class TestVennCommands:
    def test_venn2_in_sets(self):
        ec, out, err = run_cli("sets", "--help")
        assert "venn2" in out
        assert "venn3" in out
        assert "venn4" in out

    def test_venn2_help(self):
        ec, out, err = run_cli("sets", "venn2", "--help")
        assert ec == 0
        assert "List1" in out

    def test_venn3_help(self):
        ec, out, err = run_cli("sets", "venn3", "--help")
        assert ec == 0
        assert "List1" in out

    def test_venn4_help(self):
        ec, out, err = run_cli("sets", "venn4", "--help")
        assert ec == 0
        assert "List1" in out


# ============ 5. 拼写纠错 ============

class TestSpellingSuggestions:
    def test_typo_circcos(self):
        ec, out, err = run_cli("syn", "circcos")
        assert "circos" in err

    def test_typo_exp(self):
        ec, out, err = run_cli("exp", "volcano")
        assert "expr" in err


# ============ 6. tool 分组 fallback ============

class TestToolFallback:
    def test_unknown_tool_lists_all(self):
        ec, out, err = run_cli("tool", "nonexistent_xyz")
        assert "未知工具" in err
        assert "gfa2fa" in err  # 列出了可用工具

    def test_known_auto_tool(self):
        ec, out, err = run_cli("tool", "gfa2fa")
        # gfa2fa 可能因 JAR 不兼容报错，但应触发了引擎（非 click 层面错误）
        assert ec != 0  # 没参数应该失败
        assert "inGFA" in out or "tbtools_err" in err or "执行失败" in err

    def test_exit_code_unknown_tool(self):
        ec, out, err = run_cli("tool", "nonexistent_xyz")
        assert ec == 2


# ============ 7. --preset 一致性 ============

class TestPresetConsistency:
    def test_volcano_has_preset(self):
        ec, out, err = run_cli("expr", "volcano", "--help")
        assert "--preset" in out

    def test_heatmap_has_preset(self):
        ec, out, err = run_cli("expr", "heatmap", "--help")
        assert "--preset" in out

    def test_auto_command_has_preset(self):
        ec, out, err = run_cli("syn", "circos", "--help")
        assert "--preset" in out

    def test_venn2_has_preset(self):
        ec, out, err = run_cli("sets", "venn2", "--help")
        assert "--preset" in out


# ============ 8. 退出码 ============

class TestExitCodes:
    def test_success(self):
        if not HAS_JAR:
            pytest.skip("No TBtools JAR")
        ec, out, err = run_cli("expr", "volcano", "examples/data/deg.txt", "/tmp/test_ec.svg")
        assert ec == 0

    def test_missing_file(self):
        ec, out, err = run_cli("expr", "volcano", "/nonexistent", "/tmp/out.svg")
        # Java 引擎报 FileNotFoundException → 退出码 1 或 2
        assert ec in (1, 2)

    def test_missing_args(self):
        ec, out, err = run_cli("expr", "volcano")
        assert ec == 2

    def test_unknown_command(self):
        ec, out, err = run_cli("syn", "xxx")
        assert ec == 2


# ============ 9. 输入校验 ============

class TestInputValidation:
    def test_validate_file_exists(self):
        ok, msg = validate_file("/nonexistent/path.fa", "test")
        assert not ok
        assert "不存在" in msg

    def test_validate_file_empty(self, tmp_path):
        f = tmp_path / "empty.fa"
        f.write_text("")
        ok, msg = validate_file(str(f), "test")
        assert not ok
        assert "空" in msg

    def test_validate_file_stdin(self):
        ok, msg = validate_file("/dev/stdin", "test")
        assert ok

    def test_detect_format_fasta(self, tmp_path):
        f = tmp_path / "test.fa"
        f.write_text(">seq1\nACGT\n")
        fmt, ncols, lines = detect_format(str(f))
        assert fmt == "fasta"

    def test_detect_format_newick(self, tmp_path):
        f = tmp_path / "test.nwk"
        f.write_text("(A,B);\n")
        fmt, ncols, lines = detect_format(str(f))
        assert fmt == "newick"


# ============ 12. 顶层错误导航 + 输出目录校验 ============

class TestRootNavigation:
    def test_top_level_group_command_hint(self):
        """顶层直调分组内命令 → 提示正确分组"""
        ec, out, err = run_cli("venn2")
        assert "sets" in err
        assert "tbtools sets venn2" in err

    def test_top_level_typo_suggestion(self):
        """拼写错分组名 → 纠错建议"""
        ec, out, err = run_cli("exp")
        assert "expr" in err

    def test_top_level_unknown_no_match(self):
        """完全未知命令 → 指向 list"""
        ec, out, err = run_cli("zzzz")
        assert "list" in err

    def test_error_shows_command_name(self):
        """报错时帮助提示带命令名 + 坑位提示"""
        ec, out, err = run_cli("expr", "hclust", "/no_file.txt", "/tmp/tb_x.svg")
        assert "tbtools hclust --help" in err
        assert "已知坑位" in err  # hclust 有坑位提示

    def test_output_dir_not_exist(self):
        """输出目录不存在 → 立即报错（不挂 Java）"""
        ec, out, err = run_cli("expr", "volcano", "examples/data/deg.txt", "/nonexist_dir_xyz/o.svg")
        assert ec == 1
        assert "目录不存在" in err
        assert "mkdir -p" in err


# ============ 11. RPC + help 快捷入口 ============

class TestRpcAndHelp:
    def test_rpc_group_exists(self):
        ec, out, err = run_cli("rpc", "--help")
        assert ec == 0
        assert "start" in out
        assert "methods" in out
        assert "call" in out

    def test_help_shortcut(self):
        ec, out, err = run_cli("help", "volcano")
        assert ec == 0
        assert "expr" in out
        assert "volcano" in out

    def test_help_not_found(self):
        ec, out, err = run_cli("help", "nonexistent_cmd")
        assert ec == 1
        assert "❌" in out

    def test_rpc_methods_no_server(self):
        ec, out, err = run_cli("rpc", "methods")
        # 没启动 RPC 服务器应该报错
        assert ec == 1
        assert "❌" in err or "❌" in out or "启动" in out


# ============ 10. help 文本质量 ============

class TestHelpQuality:
    def test_venn5_help_not_truncated(self):
        ec, out, err = run_cli("sets", "venn5", "--help")
        # 应包含完整 setE.txt 和 [labels]
        assert "setE.txt" in out or "[labels]" in out, f"venn5 help truncated"

    def test_mcscanx_no_double_emoji(self):
        ec, out, err = run_cli("syn", "mcscanx", "--help")
        assert "⚠️ ⚠️" not in out

    def test_all_groups_have_help(self):
        for gname, g in _groups.items():
            assert g.help is not None, f"Group '{gname}' has no help text"
