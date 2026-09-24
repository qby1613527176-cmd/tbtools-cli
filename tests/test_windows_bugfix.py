"""WorkBuddy ARR-B Windows 实跑 Bug 回归测试(2026-09-24 实跑报告 §5)。

Bug 1【P0】: javac 缺 -encoding UTF-8 → 中文 Windows 桥编译全灭(GBK 读 UTF-8 源码)
Bug 2【P1】: err_file 未指定编码 → Windows GBK stderr 触发 UnicodeDecodeError 自崩
Bug 3【P1】: recipBlast doc 位置参数风格错误(引擎实为 ArgsParser)→ 静默 ec=0 零输出
Bug 4【契约】: autoMakeBlastDb 同模式(位置参数静默零输出)
"""
import inspect
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestBug1JavacEncoding:
    """Bug 1: 桥编译必须显式 -encoding UTF-8"""

    def test_bridge_compile_has_utf8(self):
        from tbtools_cli import core
        src = inspect.getsource(core.ensure_bridge)
        assert '"-encoding", "UTF-8"' in src, "ensure_bridge javac 缺 -encoding UTF-8(中文 Windows 全灭)"

    def test_fake_jaxb_compile_has_utf8(self):
        from tbtools_cli import core
        src = inspect.getsource(core)
        assert src.count('"-encoding", "UTF-8"') >= 2, "fake jaxb 编译也应带 UTF-8"


class TestBug2ErrFileEncoding:
    """Bug 2: err_file 读写必须 encoding=utf-8 + errors=replace(Windows GBK 不自崩)"""

    def test_err_file_encoding(self):
        from tbtools_cli.runtime import java as _j
        src = inspect.getsource(_j)
        assert 'open(err_file, "w", encoding="utf-8", errors="replace")' in src
        assert src.count('open(err_file, encoding="utf-8", errors="replace")') >= 2

    def test_gbk_bytes_no_crash(self, tmp_path):
        """GBK 字节写入 err_file 场景: open 不应 UnicodeDecodeError"""
        p = tmp_path / "err.txt"
        p.write_bytes("错误: 编码问题 ".encode("gbk") + b"\xca\xfe")  # GBK 字节
        # errors=replace 读取不崩
        txt = open(p, encoding="utf-8", errors="replace").read()
        assert txt  # 不崩即可


class TestBug3SilentFailureDetection:
    """Bug 3/4: ArgsParser 引擎位置参数静默失败 → 应检测并 ec=1"""

    def test_recipblast_doc_is_argsparser(self):
        from tbtools_cli import auto_commands as _ac
        entry = next(e for e in _ac.ENGINE_REGISTRY if e[0] == "recipBlast")
        doc = entry[5]
        assert "--querySeqFile" in doc, "recipBlast doc 应是 ArgsParser 风格(Bug3)"
        assert "<query.fa>" not in doc, "recipBlast doc 不应再写位置参数风格"

    def test_silent_failure_guard_present(self):
        from tbtools_cli.runtime import java as _j
        src = inspect.getsource(_j)
        assert '"[Usage]:" in _err0' in src, "缺 [Usage]: 静默失败检测"
        assert '"Should be Setted" in _err0' in src

    def test_positional_args_now_fail(self):
        """集成: recipBlast 位置参数应 ec=1(不再静默 ec=0)"""
        if not os.path.isfile(os.environ.get("TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar")):
            import pytest
            pytest.skip("无 JAR")
        env = dict(os.environ, TBTOOLS_JAR=os.environ.get(
            "TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar"))
        r = subprocess.run(
            [sys.executable, "-m", "tbtools_cli.cli", "blast", "recipBlast",
             "examples/data/blast/query.fa", "examples/data/blast/subject.fa", "/tmp/rb_reg"],
            capture_output=True, text=True, cwd=ROOT, env=env, timeout=60)
        assert r.returncode != 0, "位置参数应失败(Bug3 修复前静默 ec=0)"
        assert "Invalid arguments" in r.stderr or "参数错误" in r.stderr
