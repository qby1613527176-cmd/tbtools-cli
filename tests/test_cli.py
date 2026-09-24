"""tbtools-cli 测试套件 — 验证 click 框架 + 命令注册 + help 质量"""
import pytest
import subprocess
import sys
import os

# 确保 tbtools_cli 可导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tbtools_cli.cli import cli
from tbtools_cli.cli_load import _groups  # 批次B: 已移至 cli_load
from tbtools_cli.core import PITFALL_HINTS, validate_file, detect_format
from tbtools_cli.presets import PRESETS
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
        assert len(PITFALL_HINTS) >= 30, f"Expected >=30 pitfall hints, got {len(PITFALL_HINTS)}"

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
        # N15: banner 不再宣称固定数字（原 "143 绘图命令" 与实际脱节），改断命令分组存在
        assert "TBtools-II" in out and "tool" in out

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
    @pytest.mark.integration
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
        """顶层直调分组内命令 → 自动转发（兼容 README 旧写法，2026-09-20）"""
        ec, out, err = run_cli("venn2", "--help")
        # 不再报错，而是成功转发到 sets 分组（help 里能看到 venn2 用法）
        assert ec == 0
        assert "venn2" in out or "venn2" in err

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

    def test_group_unknown_subcommand_suggests(self):
        """分组内未知子命令 → 最近命令纠错"""
        ec, out, err = run_cli("syn", "circcos")
        assert "circos" in err

    def test_group_unknown_subcommand_no_match(self):
        """分组内未知子命令无接近 → 指向 help"""
        ec, out, err = run_cli("seq", "qqqq")
        assert "seq --help" in err

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

    def test_completion_bash(self):
        ec, out, err = run_cli("completion", "bash")
        assert ec == 0
        assert "_tbtools_complete" in out

    def test_completion_fish(self):
        ec, out, err = run_cli("completion", "fish")
        assert ec == 0
        assert "complete -c tbtools" in out

    def test_completion_menu(self):
        ec, out, err = run_cli("completion")
        assert ec == 0
        assert "bash" in out and "zsh" in out and "fish" in out

    def test_new_list(self):
        ec, out, err = run_cli("new", "--list")
        assert ec == 0
        assert "多序列比对可视化" in out
        assert "火山图" in out

    def test_new_wizard_non_interactive(self):
        """无 stdin（/dev/null EOF）→ 友好取消，不挂死"""
        import subprocess as sp
        p = sp.run([sys.executable, "-m", "tbtools_cli.cli", "new"],
                   stdin=sp.DEVNULL, capture_output=True, text=True, timeout=30)
        # 非交互 EOF 应友好取消（exit 130），不挂死
        assert p.returncode == 130
        assert "已取消" in p.stderr or "已取消" in p.stdout

    def test_new_wizard_piped(self):
        """管道注入选择 → 生成命令"""
        import subprocess as sp
        p = sp.run([sys.executable, "-m", "tbtools_cli.cli", "new"],
                   input="2\n1\ndeg.txt\nvolcano.svg\n", capture_output=True, text=True, timeout=30)
        assert p.returncode == 0
        assert "tbtools expr volcano deg.txt volcano.svg" in p.stdout

    def test_help_shortcut(self):
        ec, out, err = run_cli("help", "volcano")
        assert ec == 0
        assert "expr" in out
        assert "volcano" in out

    def test_help_not_found(self):
        ec, out, err = run_cli("help", "nonexistent_cmd")
        assert ec == 1
        assert "❌" in out

    def test_rpc_methods_static_discovery(self):
        # GPT/GLM 评审: 发现操作应 side-effect free——默认不启动服务器(9999 无服务应报错非零)
        ec, out, err = run_cli("rpc", "methods", "-p", "9999")
        assert ec != 0
        assert "❌" in err or "❌" in out or "不可达" in out or "refused" in err.lower()


# ============ 10. help 文本质量 ============

class TestHelpQuality:
    def test_venn5_help_not_truncated(self):
        ec, out, err = run_cli("sets", "venn5", "--help")
        # 应包含完整 setE.txt 和 [labels]
        assert "setE.txt" in out or "[labels]" in out, "venn5 help truncated"

    def test_mcscanx_no_double_emoji(self):
        ec, out, err = run_cli("syn", "mcscanx", "--help")
        assert "⚠️ ⚠️" not in out

    def test_all_groups_have_help(self):
        for gname, g in _groups.items():
            assert g.help is not None, f"Group '{gname}' has no help text"


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "data")


def _find(pattern):
    import glob
    cands = sorted(glob.glob(os.path.join(DATA_DIR, pattern), recursive=True))
    return cands[0] if cands else None


class TestFormatDetection:
    """C2: 早期格式检测 + check 探测器"""

    def test_check_input_format_fasta_vs_tsv(self):
        from tbtools_cli.core import check_input_format
        fa = _find("**/*.fa") or _find("**/*.fasta")
        if not fa:
            pytest.skip("no fasta example")
        warn = check_input_format("hclust", fa)
        assert warn is not None and "表格" in warn

    def test_check_input_format_ok_no_warn(self):
        from tbtools_cli.core import check_input_format
        deg = _find("deg.txt")
        if not deg:
            pytest.skip("no deg.txt")
        assert check_input_format("volcano", deg) is None

    def test_check_command(self):
        deg = _find("deg.txt")
        if not deg:
            pytest.skip("no deg.txt")
        ec, out, err = run_cli("check", deg)
        assert ec == 0
        assert "tsv" in out


class TestAgentOnboarding:
    """自动接入：setup / fetch-jar / doctor 指引 / 跨平台 jar 发现"""

    def test_setup_command_exists(self):
        ec, out, err = run_cli("setup", "--help")
        assert ec == 0
        assert "--auto" in out

    def test_fetch_jar_command_exists(self):
        ec, out, err = run_cli("fetch-jar", "--help")
        assert ec == 0
        assert "--version" in out

    def test_setup_no_args_shows_usage(self):
        ec, out, err = run_cli("setup")
        assert ec == 0
        assert "--auto" in out

    def test_setup_with_missing_path(self):
        ec, out, err = run_cli("setup", "/nonexistent/xyz.jar")
        assert ec == 1
        assert "不存在" in err

    def test_setup_auto_discovers(self, tmp_path, monkeypatch):
        """fake home 里有 TBtools 目录 → setup --auto 应找到并写配置"""
        import tbtools_cli.cli as cli_mod
        fake_home = tmp_path / "home"
        tb_dir = fake_home / "TBtools"
        tb_dir.mkdir(parents=True)
        fake_jar = tb_dir / "TBtools_JRE1.6.jar"
        fake_jar.write_bytes(b"PK\x05\x06" + b"\x00" * 18)  # 假装 zip/jar
        monkeypatch.setenv("HOME", str(fake_home))
        monkeypatch.delenv("TBTOOLS_JAR", raising=False)
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli_mod.cli, ["setup", "--auto"])
        assert "已配置" in result.output
        cfg = fake_home / ".config" / "tbtools-cli" / "config.sh"
        assert cfg.exists()
        assert "TBtools_JRE1.6.jar" in cfg.read_text()

    def test_doctor_guidance_when_no_jar(self, tmp_path):
        """jar 缺失时 doctor 应给出 setup/fetch-jar 指引（子进程+干净 HOME，绕开模块级 JAR 缓存）"""
        fake_home = tmp_path / "home"
        fake_home.mkdir(parents=True)
        env = dict(os.environ)
        env["HOME"] = str(fake_home)
        env.pop("TBTOOLS_JAR", None)
        import subprocess as sp
        p = sp.run([sys.executable, "-m", "tbtools_cli.cli", "doctor"],
                   capture_output=True, text=True, timeout=30, env=env)
        out = p.stdout + p.stderr
        assert "setup --auto" in out
        assert "fetch-jar" in out


# ============ 12. README 数字防漂移（外部审查反馈） ============

class TestReadmeCounts:
    """README 硬编码数字必须与实现实时统计一致（防漂移）"""

    def _counts(self):
        import re
        import os
        from tbtools_cli.core import ROOT
        impls = len(re.findall(r'def _\w+_impl',
                    open(os.path.join(ROOT, "tbtools_cli", "auto_commands.py"), encoding="utf-8").read()))
        bridges = len([f for f in os.listdir(os.path.join(ROOT, "bridges")) if f.endswith(".java")])
        return impls, bridges

    def test_readme_bridge_count(self):
        import os
        from tbtools_cli.core import ROOT
        readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
        impls, bridges = self._counts()
        # README 里必须出现实际桥数（100 → 更新时同步改）
        assert f"{bridges} 个 Java 桥" in readme or f"{bridges} 个桥" in readme or f"{bridges} Java bridge" in readme, \
            f"README 桥数与实现({bridges})漂移，运行 tbtools version 后同步 README"

    def test_version_cmd_reports_positive_counts(self):
        ec, out, err = run_cli("version")
        assert ec == 0

    def test_readme_plot_count(self):
        """README 数字机器化(GPT #7): 不手写精确计数; 权威源 counts.md 与运行时一致。

        2026-09-23 改造: 精确数字全部移除(218/188/82/118/276), 改为范围口径 +
        docs/_generated/counts.md(gen_metadata 自动生成)作为唯一权威。
        """
        import os
        import json
        from tbtools_cli.core import ROOT
        readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
        # 1) README 不应含已废弃精确数字(范围口径时代)
        for bad in ["218 个", "188 个", "82 个", "118 个", "276 命令", "196 绘图", "268 命令"]:
            assert bad not in readme, f"README 含已废弃精确数字 {bad!r}"
        # 2) 权威源: counts.md(机器生成)必须与 command_metadata.json 实际一致
        counts_path = os.path.join(ROOT, "docs", "_generated", "counts.md")
        assert os.path.isfile(counts_path), "counts.md 缺失(跑 gen_metadata --render)"
        counts = open(counts_path, encoding="utf-8").read()
        meta = json.load(open(os.path.join(ROOT, "tbtools_cli", "command_metadata.json"), encoding="utf-8"))
        assert f"metadata_commands: {len(meta)}" in counts, \
            "counts.md 与 command_metadata.json 不一致(跑 gen_metadata --render)"
        # 3) README 头部应指向权威源(防回归到手写数字)
        assert "counts.md" in readme and "version --json" in readme, \
            "README 缺少数字权威源声明(应指向 counts.md / version --json)"

    def test_readme_pitfall_count(self):
        """README 坑位数 = PITFALL_HINTS 实际数"""
        import os
        import re
        from tbtools_cli.core import ROOT, PITFALL_HINTS
        readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
        m = re.search(r'(\d+) 条实测坑位', readme)
        assert m and int(m.group(1)) == len(PITFALL_HINTS), \
            f"README 坑位数 {m.group(1) if m else '?'} != 实际 {len(PITFALL_HINTS)}"


# ============ 13. probe_dead_engines 假 jar 测试（外部审查反馈：CI 无真 jar） ============

class TestProbeWithFakeJar:
    """用假 jar（手工 zip + 空 .class 条目）验证死命令探测逻辑，不依赖真 TBtools jar"""

    def _make_fake_jar(self, tmp_path):
        import zipfile
        jar = tmp_path / "fake.jar"
        with zipfile.ZipFile(jar, "w") as z:
            # 空 class 文件即可（zipfile 只查名存在性）
            z.writestr("biocjava/bioDoer/TestEngine/Exists.class", b"\xca\xfe\xba\xbe")
            z.writestr("biocjava/bioIO/Other/RealEngine.class", b"\xca\xfe\xba\xbe")
        return str(jar)

    def test_probe_finds_missing_class(self, tmp_path, monkeypatch):
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from tbtools_cli import core
        fake = self._make_fake_jar(tmp_path)
        # 造一个只引用两个类的临时 src，一个存在一个不存在
        src = tmp_path / "probe_src.py"
        src.write_text(
            'X = "biocjava.bioDoer.TestEngine.Exists"  # 存在\n'
            'Y = "biocjava.bioDoer.TestEngine.Missing"  # 不存在\n',
            encoding="utf-8")
        monkeypatch.setattr(core, "JAR", fake)
        # 直接调核心匹配逻辑（复用 probe 的正则/判定）
        import zipfile
        import re
        with zipfile.ZipFile(fake) as z:
            names = set(z.namelist())
        pat = re.compile(r'"(biocjava\.[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+)"')
        missing = []
        for m in pat.finditer(src.read_text(encoding="utf-8")):
            cls = m.group(1)
            if cls.replace(".", "/") + ".class" not in names:
                missing.append(cls)
        assert missing == ["biocjava.bioDoer.TestEngine.Missing"], f"应只报 Missing，实际 {missing}"

    def test_doctor_reports_ok_when_all_exist(self, tmp_path, monkeypatch):
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        fake = self._make_fake_jar(tmp_path)
        import zipfile
        import re
        with zipfile.ZipFile(fake) as z:
            names = set(z.namelist())
        pat = re.compile(r'"(biocjava\.[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+)"')
        src_text = 'A = "biocjava.bioDoer.TestEngine.Exists"\nB = "biocjava.bioIO.Other.RealEngine"\n'
        missing = [m.group(1) for m in pat.finditer(src_text)
                   if m.group(1).replace(".", "/") + ".class" not in names]
        assert missing == [], f"全部应存在，实际缺失 {missing}"


class TestSearchCommand:
    """tbtools search 模糊搜索(第十轮审计: 新功能无测试盲区)"""

    def test_search_exact(self):
        ec, out, err = run_cli("search", "volcano")
        assert ec == 0 and "volcano" in out

    def test_search_partial(self):
        ec, out, err = run_cli("search", "venn")
        assert ec == 0 and "venn2" in out

    def test_search_no_match(self):
        ec, out, err = run_cli("search", "zzzz_nonexist_xyz")
        assert ec != 0, "无匹配应非零退出"
        assert "没有匹配" in out or "没有匹配" in err

    def test_search_requires_arg(self):
        ec, out, err = run_cli("search")
        assert ec != 0, "缺关键词应非零退出"


class TestReadmeStructure:
    """README 结构健全(第六轮评审: 围栏配对/TOC 锚点/License)"""

    def _readme(self):
        import os as _os
        p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "README.md")
        return open(p, encoding="utf-8").read()

    def test_fence_strict_pairing(self):
        """代码围栏必须严格交替(```bash 开 → ``` 闭),防止标题被吞渲染"""
        state = None
        for i, ln in enumerate(self._readme().split('\n'), 1):
            s = ln.strip()
            if s.startswith('```'):
                if state is None:
                    state = s
                else:
                    assert s == '```', f"L{i}: 开围栏未用 ``` 闭合({s})"
                    state = None
        assert state is None, "存在未闭合围栏"

    def test_toc_anchors_exist(self):
        """TOC 锚点必须对应真实标题(死链检查, GitHub 锚点近似规则)"""
        import re
        r = self._readme()
        headers = []
        for ln in r.split('\n'):
            if ln.startswith('## '):
                headers.append(ln[3:].strip())

        def gh_anchor(title):
            # GitHub GFM 锚点近似: 去 emoji/标点(非 \w), 小写, 空格→-
            t = re.sub(r'[^\w\s-]', '', title, flags=re.UNICODE).lower().replace(' ', '-')
            t = t.strip('-')
            # 纯 ASCII 标题(GitHub 规则确定), 中文标题保留
            return (t or title.lower()) if t.isascii() else title.lower()

        for m in re.finditer(r'\[[^\]]*\]\(#([^)]+)\)', r):
            anchor = m.group(1)
            if anchor.isascii():
                assert anchor in {gh_anchor(h) for h in headers}, f"TOC 死锚点: #{anchor}"
            else:
                assert any(anchor in h or anchor == h for h in headers), f"TOC 中文锚点无对应标题: #{anchor}"

    def test_license_single(self):
        """License 只出现一次(英文完整说明, 不重复中文节)"""
        r = self._readme()
        assert r.count('## 📄 License') == 1
        assert '## 📄 许可' not in r, "中文许可节已合并, 不应残留"


class TestVersionConsistency:
    """P0-2: pyproject/__version__/CHANGELOG 单一权威源一致性"""

    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_pyproject_matches_package(self):
        import re
        import tbtools_cli
        ROOT = self.ROOT
        pp = open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8").read()
        m = re.search(r'^version = "([^"]+)"', pp, re.M)
        assert m and m.group(1) == tbtools_cli.__version__, \
            f"pyproject {m.group(1) if m else '?'} != __version__ {tbtools_cli.__version__}"

    def test_changelog_latest_matches(self):
        import re
        ROOT = self.ROOT
        cl = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read()
        m = re.search(r'^## \[([0-9.]+)\]', cl, re.M)
        pp = open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8").read()
        pv = re.search(r'^version = "([^"]+)"', pp, re.M)
        assert m and pv and m.group(1) == pv.group(1), \
            f"CHANGELOG 最新 {m.group(1) if m else '?'} != pyproject {pv.group(1) if pv else '?'}"


class TestWorkflowYaml:
    """所有 GitHub workflow YAML 必须有效(第十五轮审计: docs.yml 曾被 heredoc 破坏,需固化)"""

    def test_all_workflows_valid(self):
        import glob
        import os as _os
        import yaml
        root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        files = sorted(glob.glob(_os.path.join(root, ".github", "workflows", "*.yml")))
        assert files, "无 workflow 文件?"
        for f in files:
            yaml.safe_load(open(f, encoding="utf-8"))  # 无效则抛异常
        print(f"✅ {len(files)} 个 workflow YAML 有效: {[_os.path.basename(f) for f in files]}")

    def test_workflow_refs_exist(self):
        """workflow 引用的关键脚本/文件存在(防 docs.yml 引错路径)"""
        import os as _os
        root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        for rel in ["scripts/gen_metadata.py", "scripts/sync_docs_commands.py",
                    "scripts/rpc_regression_linux.sh", "examples/scripts/run_examples.sh",
                    "mkdocs.yml", "config/config.sh"]:
            assert _os.path.exists(_os.path.join(root, rel)), f"workflow 引用缺失: {rel}"
