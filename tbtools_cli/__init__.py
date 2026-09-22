"""tbtools-cli — TBtools-II 全功能 CLI（Python click 重构版）"""
try:
    from importlib.metadata import version as _v
    __version__ = _v("tbtools-cli")
    del _v
except Exception:
    __version__ = "1.1.0"
