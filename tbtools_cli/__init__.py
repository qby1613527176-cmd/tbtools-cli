"""tbtools-cli — TBtools-II 全功能 CLI（Python click 重构版）"""
import os as _os
import re as _re

_pp = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "pyproject.toml")
if _os.path.isfile(_pp):
    # 源码树内: pyproject.toml 是唯一版本源(2026-09-23: 避免旧安装 metadata 幽灵版本误导)
    _m = _re.search(r'^version = "([^"]+)"', open(_pp, encoding="utf-8").read(), _re.M)
    __version__ = _m.group(1) if _m else "0.0.0.dev"
    del _m
else:
    # 安装分发: importlib.metadata
    try:
        from importlib.metadata import version as _v
        __version__ = _v("tbtools-cli")
        del _v
    except Exception:
        __version__ = "0.0.0.dev"
