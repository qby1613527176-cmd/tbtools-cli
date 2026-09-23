"""tbtools-cli — TBtools-II 全功能 CLI（Python click 重构版）"""
try:
    from importlib.metadata import version as _v
    __version__ = _v("tbtools-cli")
    del _v
except Exception:
    # 源码运行(未安装): 从 pyproject.toml 解析(单一源; 不再硬编码)
    import os as _os
    import re as _re
    _pp = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "pyproject.toml")
    _m = _re.search(r'^version = "([^"]+)"', open(_pp, encoding="utf-8").read(), _re.M) if _os.path.isfile(_pp) else None
    __version__ = _m.group(1) if _m else "0.0.0.dev"
