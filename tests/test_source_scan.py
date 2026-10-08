"""source_scan / meta_guard 直接单测(arch N5 中期产物 + arch N8 守卫).

source_scan: 用**合成源码**独立验证 AST 扫描器——不依赖真实仓库文件,
直接覆盖 N5 报告的脆弱点场景(无 docstring 不错配下一条 / 引号不截断 /
顶层命令可见 / add_command 别名可发现)。
meta_guard: 临时目录构造源码树, 验证指纹确定性 + staleness 检出。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tbtools_cli.source_scan import ast_scan_commands  # noqa: E402

# ---- 合成源码: 覆盖装饰器/顶层/add_command/无 docstring/含引号 doc ----
CLI_SRC = '''"""fake cli.py"""

@cli.group()
def expr_group():
    pass

@expr_group.command("volcano")
def volcano_cmd():
    """volcano: 火山图(DEG: GeneID Log2FC pvalue)"""
    pass

@cli.command(name="topcmd")
def topcmd():
    """topcmd: 顶层管理命令"""
    pass

@expr_group.command("nodoc")
def nodoc_cmd():
    pass  # 无 docstring——旧正则脆弱点 4: 会越过它把下一条 doc 错配给它

@expr_group.command("after")
def after_cmd():
    """after: 有 doc 的命令"""
    pass

@expr_group.add_command(seqlogo_fn, name="seqlogo")
def seqlogo_fn():
    pass

@expr_group.command("tableMerge")
def tablemerge_cmd():
    """tableMerge: 含"引号'的 doc——旧正则 [^"] 会在此截断"""
    pass
'''

AC_SRC = '''"""fake auto_commands.py"""

def _mirnatarget_impl(args, verbose=False, quiet=False):
    """mirnatarget: miRNA 靶标预测"""
    return 0

def _msy_impl(args, verbose=False, quiet=False):
    """msy: 多物种微共线性图"""
    return 0
'''


class TestAstScanCommands:
    def test_decorator_command_group_and_doc(self):
        out = ast_scan_commands(CLI_SRC, AC_SRC)
        assert out["volcano"]["group"] == "expr"
        assert "火山图" in out["volcano"]["doc"]
        assert out["volcano"]["src"] == "cli_manual"

    def test_top_level_command_visible_group_none(self):
        # N5 脆弱点 2: 顶层 @cli.command 不再单侧漂移(消费侧 KNOWN_TOP_MANUAL 过滤)
        out = ast_scan_commands(CLI_SRC, AC_SRC)
        assert out["topcmd"]["group"] is None
        assert "顶层" in out["topcmd"]["doc"]

    def test_no_docstring_no_mismatch(self):
        # N5 脆弱点 4: 无 docstring 命令不再被正则把下一条的 doc 错配给它
        out = ast_scan_commands(CLI_SRC, AC_SRC)
        assert out["nodoc"]["doc"] == ""          # 自身 doc 空
        assert "after" in out["after"]["doc"]     # 下一条 doc 完好

    def test_quote_in_docstring_not_truncated(self):
        # N5 脆弱点 5: docstring 内双引号不再提前截断
        out = ast_scan_commands(CLI_SRC, AC_SRC)
        assert "引号" in out["tableMerge"]["doc"]

    def test_add_command_alias_discovered(self):
        out = ast_scan_commands(CLI_SRC, AC_SRC)
        assert out["seqlogo"]["src"] == "cli_manual"
        assert out["seqlogo"]["fn"] == "seqlogo_fn"  # 供 help 借用

    def test_manual_impl_scanned(self):
        out = ast_scan_commands(CLI_SRC, AC_SRC)
        assert out["mirnatarget"]["src"] == "auto_manual"
        assert "miRNA" in out["mirnatarget"]["doc"]
        assert out["msy"]["src"] == "auto_manual"
        assert out["msy"]["doc"].startswith("msy")


class TestMetaGuard:
    def test_fingerprint_deterministic(self, tmp_path):
        from tbtools_cli.meta_guard import sources_mtime_fingerprint
        root = tmp_path / "root"
        (root / "tbtools_cli").mkdir(parents=True)
        (root / "bridges").mkdir()
        (root / "tbtools_cli" / "a.py").write_text("x = 1")
        (root / "tbtools_cli" / "b.py").write_text("y = 2")
        (root / "bridges" / "C.java").write_text("class C {}")
        fp1 = sources_mtime_fingerprint(str(root))
        fp2 = sources_mtime_fingerprint(str(root))
        assert fp1 == fp2  # 同输入同输出(确定性, 非随机)

    def test_content_change_changes_fingerprint(self, tmp_path):
        from tbtools_cli.meta_guard import sources_mtime_fingerprint
        root = tmp_path / "root"
        (root / "tbtools_cli").mkdir(parents=True)
        f = root / "tbtools_cli" / "a.py"
        f.write_text("x = 1")
        fp1 = sources_mtime_fingerprint(str(root))
        import time
        time.sleep(0.01)
        f.write_text("x = 2")  # mtime + 内容都变
        fp2 = sources_mtime_fingerprint(str(root))
        assert fp1 != fp2

    def test_staleness_detection(self, tmp_path, monkeypatch):
        # sidecar 最新 → fresh; touch 源码后 → stale(arch N8 守卫生效)
        import json
        import time
        from tbtools_cli import meta_guard
        root = tmp_path / "root"
        (root / "tbtools_cli").mkdir(parents=True)
        (root / "bridges").mkdir()  # 仓库布局(有 bridges)——安装态跳过(P1-7)不触发
        f = root / "tbtools_cli" / "a.py"
        f.write_text("x = 1")
        # 写 sidecar(指纹 = 当前源码)
        side = tmp_path / "side" / meta_guard._SIDE
        side.parent.mkdir(parents=True)
        with open(side, "w", encoding="utf-8") as fh:
            json.dump({"sources_content": meta_guard.sources_content_fingerprint(str(root))}, fh)
        # monkeypatch ROOT 到临时树 + sidecar 路径
        monkeypatch.setattr(meta_guard, "ROOT", str(root))
        monkeypatch.setattr(meta_guard, "_SIDE_REPO", str(side))
        assert meta_guard.staleness_ok() is True
        time.sleep(0.01)
        f.write_text("x = 2")  # 改源码不重跑 render
        assert meta_guard.staleness_ok() is False