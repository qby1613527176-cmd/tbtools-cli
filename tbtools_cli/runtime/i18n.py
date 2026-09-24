"""i18n(core.py 拆分): 轻量双语(--lang en / LC_ALL / config lang)。"""
import os

from tbtools_cli.config import get_default
# ── 轻量 i18n(--lang en / LC_ALL / config [defaults] lang)──
_LANG_EN = None

def _use_en() -> bool:
    """是否英文输出: config [defaults] lang=en 或 LC_ALL/LANG 含 en|c。中文默认。"""
    global _LANG_EN
    if _LANG_EN is None:
        cfg = get_default("lang", "")
        env = (os.environ.get("LC_ALL", "") + " " + os.environ.get("LANG", "")).lower()
        lang_code = env.split()[0].split(".")[0] if env.split() else ""
        # en 开头 → 英文; C/POSIX locale(如 C.UTF-8)也是英文环境
        _LANG_EN = bool(cfg and str(cfg).lower().startswith("en")) or "en" in env or lang_code in ("c", "posix")
    return _LANG_EN


def _lang_cache_clear():
    global _LANG_EN
    _LANG_EN = None


def _(zh: str, en: str) -> str:
    """双语消息选择(中文默认;英文开关)"""
    return en if _use_en() else zh

# ---- 平台常量（Windows 主战场：classpath 分隔符；Linux/WSL 用 :）----
