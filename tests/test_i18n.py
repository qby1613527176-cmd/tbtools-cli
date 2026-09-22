"""i18n 语言开关测试(_use_en/_,第十四轮审计: 边界变体无覆盖盲区)。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import tbtools_cli.core as core


@pytest.fixture(autouse=True)
def _clean_lang():
    """每个测试前清缓存并记录原 env"""
    saved = {k: os.environ.get(k) for k in ("LC_ALL", "LANG", "TBTOOLS_CONFIG")}
    core._lang_cache_clear()
    yield
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    core._lang_cache_clear()


class TestLangDetection:
    """LC_ALL/LANG/config 的语言判定边界"""

    @pytest.mark.parametrize("locale", ["en_US.UTF-8", "en_US", "C.UTF-8", "C", "POSIX"])
    def test_en_locales(self, locale):
        os.environ["LC_ALL"] = locale
        assert core._use_en() is True, f"{locale} 应为英文"

    @pytest.mark.parametrize("locale", ["zh_CN.UTF-8", "ja_JP.UTF-8", "de_DE.UTF-8"])
    def test_non_en_locales(self, locale):
        os.environ["LC_ALL"] = locale
        assert core._use_en() is False, f"{locale} 应为中文默认"

    def test_empty_inherits_lang(self):
        """LC_ALL 空时继承 LANG"""
        os.environ.pop("LC_ALL", None)
        os.environ["LANG"] = "en_US.UTF-8"
        assert core._use_en() is True
        os.environ["LANG"] = "zh_CN.UTF-8"
        core._lang_cache_clear()
        assert core._use_en() is False

    def test_config_lang_en(self, tmp_path):
        """config [defaults] lang=en 强制英文"""
        cfg = tmp_path / "cfg.toml"
        cfg.write_text('[defaults]\nlang = "en"\n', encoding="utf-8")
        os.environ["TBTOOLS_CONFIG"] = str(cfg)
        os.environ["LC_ALL"] = "zh_CN.UTF-8"  # 与 config 冲突时 config 优先
        assert core._use_en() is True

    def test_msg_selection(self):
        """_() 中文默认/英文切换"""
        os.environ["LC_ALL"] = "zh_CN.UTF-8"
        core._lang_cache_clear()
        assert core._("中文", "English") == "中文"
        os.environ["LC_ALL"] = "en_US.UTF-8"
        core._lang_cache_clear()
        assert core._("中文", "English") == "English"
