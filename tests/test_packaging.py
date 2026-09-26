"""WOX 实跑 P06 打包回归测试(2026-09-25 WOX 问题单):
P06-A【严重】: wheel 缺 tbtools_cli.runtime 子包(pip install 后 ModuleNotFoundError)
P06-B: editable/namespace 场景 __version__ 导入防御回退
"""
import glob
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestWheelContents:
    """P06-A: wheel 必须包含全部子包(runtime/ 等)"""

    def test_pyproject_uses_find(self):
        """pyproject 必须用 packages.find(显式 ['tbtools_cli'] 只打顶层=P06-A 根因)"""
        pp = open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8").read()
        assert "[tool.setuptools.packages.find]" in pp, \
            "P06-A 回归: pyproject 应使用 packages.find auto-discovery"
        assert 'include = ["tbtools_cli*"]' in pp
        # 显式单包声明不得回归
        assert 'packages = ["tbtools_cli"]' not in pp

    def test_wheel_has_runtime(self):
        """构建的 wheel 必须含 runtime/ 子包(慢速集成, 无 dist 时跳过)"""
        import pytest
        wheels = sorted(glob.glob(os.path.join(ROOT, "dist", "*.whl")))
        if not wheels:
            pytest.skip("无 dist/(仅发布流程构建)")
        names = zipfile.ZipFile(wheels[-1]).namelist()
        assert any("tbtools_cli/runtime/__init__.py" in n for n in names), \
            "P06-A: wheel 缺 runtime/__init__.py"
        assert any("tbtools_cli/runtime/java.py" in n for n in names), \
            "P06-A: wheel 缺 runtime/java.py"
        assert any("tbtools_cli/runtime/env.py" in n for n in names)

    def test_source_subpackages_importable(self):
        """源码树内子包可导入(与 pip 安装后行为对齐)。

        注: runtime.java 与 core 存在设计内循环引用(core 文件尾 re-export),
        真实路径先加载 core——测试按真实导入序(与 cli.py 一致)。"""
        import importlib
        import tbtools_cli.core  # noqa: F401  # 先 core(与生产导入序一致)
        for mod in ("tbtools_cli.runtime", "tbtools_cli.runtime.env",
                    "tbtools_cli.runtime.i18n", "tbtools_cli.runtime.validation"):
            importlib.import_module(mod)
        import tbtools_cli.runtime.java  # noqa: F401  # core 已加载后 java 可导入


class TestVersionFallback:
    """P06-B: __version__ 导入防御(cli.py 有 ImportError 回退)"""

    def test_cli_version_fallback_exists(self):
        import inspect

        from tbtools_cli import cli
        src = inspect.getsource(cli)
        assert "except ImportError" in src and "importlib.metadata" in src, \
            "P06-B: cli.py 应有 __version__ ImportError 防御回退"

    def test_version_resolves(self):
        from tbtools_cli import cli
        assert cli._CLI_VERSION and cli._CLI_VERSION != ""


class TestDoctorUx:
    """P07: doctor jar 版本显示 + 平台感知 Java 提示"""

    def test_doctor_shows_jar_version_line(self):
        env = dict(os.environ, TBTOOLS_JAR=os.environ.get(
            "TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar"))
        if not os.path.isfile(env["TBTOOLS_JAR"]):
            import pytest
            pytest.skip("无 JAR")
        r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "doctor"],
                           capture_output=True, text=True, cwd=ROOT, env=env, timeout=60)
        assert "📦 JAR 版本" in r.stdout, "doctor 应显示 jar 版本行(P07)"

    def test_java_hint_platform_aware(self):
        import inspect

        from tbtools_cli import cli_top
        src = inspect.getsource(cli_top)
        assert "winget" in src or "Temurin" in src, \
            "P07: Java 安装提示应含 Windows/macOS 方案(不只 apt)"
