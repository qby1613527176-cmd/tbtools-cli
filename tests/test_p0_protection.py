# -*- coding: utf-8 -*-
"""P0 输入保护测试（N19/N23/N25/N37 家族）：引擎在用户输入上建库/清洗/写穿的系统性防御。

覆盖:
1. snapshot_inputs 只快照输入、排除输出参数/jar/-cp
2. verify_and_restore 检测并恢复被引擎改写的输入
3. cleanup_side_effects 只删本次调用新增的 TBtools 副作用残留
4. findBestHomologyBatch impl 参数归一（N19：真实参数名 + 旧名兼容）
5. gffCdsPhaseCorrector impl 拒绝 in==out（N25：防覆盖输入）
6. mirnatarget impl 拒绝输出与输入同名（N23：防清零输入）
"""
import os
import shutil
import tempfile
import time


from tbtools_cli import core


def _mkfa(path, n=50, seq="ACGT"):
    with open(path, "w") as f:
        for i in range(n):
            f.write(f">seq{i}\n{seq * 20}\n")


class TestSnapshotInputs:
    def test_excludes_outputs_and_cp(self):
        td = tempfile.mkdtemp()
        try:
            inp = os.path.join(td, "in.fa")
            out = os.path.join(td, "out.xls")
            _mkfa(inp)
            open(out, "w").write("old")
            args = ["java", "-Xmx2g", "-cp", core.JAR, "Eng", "--inFa", inp, "--outPutFile", out]
            snaps = core.snapshot_inputs(args)
            assert len(snaps) == 1
            assert snaps[0][0] == inp
            assert snaps[0][1] is not None  # 有备份
        finally:
            shutil.rmtree(td, ignore_errors=True)

    def test_skips_missing_and_jar(self):
        td = tempfile.mkdtemp()
        try:
            args = ["java", "-cp", "/nonexistent.jar", "Eng", "/no/such.fa"]
            assert core.snapshot_inputs(args) == []
        finally:
            shutil.rmtree(td, ignore_errors=True)


class TestVerifyRestore:
    def test_restores_modified_input(self):
        td = tempfile.mkdtemp()
        try:
            inp = os.path.join(td, "in.fa")
            _mkfa(inp)
            before = open(inp, "rb").read()
            snaps = core.snapshot_inputs(["java", "-cp", core.JAR, "E", inp])
            with open(inp, "ab") as f:
                f.write(b">hacked\n" * 5)
            probs = core.verify_and_restore(snaps)
            assert probs and probs[0][1] == "modified-restored"
            assert open(inp, "rb").read() == before
        finally:
            shutil.rmtree(td, ignore_errors=True)

    def test_reports_missing(self):
        td = tempfile.mkdtemp()
        try:
            inp = os.path.join(td, "in.fa")
            _mkfa(inp)
            snaps = core.snapshot_inputs(["java", "-cp", core.JAR, "E", inp])
            os.unlink(inp)
            probs = core.verify_and_restore(snaps)
            assert probs and probs[0][1] == "missing"
        finally:
            shutil.rmtree(td, ignore_errors=True)


class TestCleanupSideEffects:
    def test_only_new_files(self):
        td = tempfile.mkdtemp()
        old = os.getcwd()
        os.chdir(td)
        try:
            t0 = time.time()
            open("new.TBtools.fa", "w").write("x")
            open("db.TBtoolsDB.nhr", "w").write("y")
            oldfile = "old.TBtools.fa"
            open(oldfile, "w").write("z")
            os.utime(oldfile, (1000000000, 1000000000))
            n = core.cleanup_side_effects(t0)
            assert n == 2
            assert not os.path.exists("new.TBtools.fa")
            assert not os.path.exists("db.TBtoolsDB.nhr")
            assert os.path.exists(oldfile)
        finally:
            os.chdir(old)
            shutil.rmtree(td, ignore_errors=True)


class TestImplSafety:
    """三个修复 impl 的防覆盖/参数归一（不启动 JVM，纯 Python 层）。"""

    def test_findBestHomologyBatch_requires_three_pos(self, capsys):
        from tbtools_cli import auto_commands
        ec = auto_commands._findBestHomologyBatch_impl([])
        assert ec == 1
        assert "用法" in capsys.readouterr().err

    def test_findBestHomologyBatch_missing_input(self, capsys):
        from tbtools_cli import auto_commands
        ec = auto_commands._findBestHomologyBatch_impl(
            ["/no/such.fa", "/no/such2.fa", "/tmp/outdir"])
        assert ec == 2

    def test_gffCdsPhaseCorrector_rejects_in_equal_out(self, capsys):
        from tbtools_cli import auto_commands
        td = tempfile.mkdtemp()
        try:
            f = os.path.join(td, "x.gff3")
            _mkfa(f, n=1, seq="ACGT")
            ec = auto_commands._gffCdsPhaseCorrector_impl(
                ["--inGff", f, "--outGff", f])
            assert ec == 2
            assert "不能相同" in capsys.readouterr().err
        finally:
            shutil.rmtree(td, ignore_errors=True)

    def test_mirnatarget_rejects_out_equal_input(self, capsys):
        from tbtools_cli import auto_commands
        td = tempfile.mkdtemp()
        try:
            f = os.path.join(td, "x.fa")
            g = os.path.join(td, "y.fa")
            _mkfa(f, n=1)
            _mkfa(g, n=1)
            ec = auto_commands._mirnatarget_impl([f, g, f])  # out == mirna
            assert ec == 2
            assert "覆盖输入" in capsys.readouterr().err
        finally:
            shutil.rmtree(td, ignore_errors=True)

    def test_mirnatarget_needs_three_pos(self, capsys):
        from tbtools_cli import auto_commands
        assert auto_commands._mirnatarget_impl(["a.fa", "b.fa"]) == 1

    def test_mirnatarget_missing_ssearch(self, capsys, monkeypatch):
        from tbtools_cli import auto_commands
        td = tempfile.mkdtemp()
        try:
            a = os.path.join(td, "m.fa")
            b = os.path.join(td, "t.fa")
            _mkfa(a, n=1)
            _mkfa(b, n=1)
            monkeypatch.setattr(auto_commands.shutil, "which", lambda x: None)
            ec = auto_commands._mirnatarget_impl([a, b, os.path.join(td, "o.tsv")])
            assert ec == 4
            assert "ssearch36" in capsys.readouterr().err
        finally:
            shutil.rmtree(td, ignore_errors=True)
