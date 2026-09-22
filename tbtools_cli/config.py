"""配置文件加载 — ~/.config/tbtools-cli/config.toml"""
import os

try:
    import tomllib
except ImportError:
    tomllib = None  # type: ignore[assignment]

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.config/tbtools-cli/config.toml")

_config_cache: dict | None = None

def load_config():
    """加载配置文件。返回 dict（可能为空）。

    _config_cache 缓存 (路径, 数据)——TBTOOLS_CONFIG env 变化时自动重读
    (第十四轮审计: 原缓存不感知 env 变化,测试/库场景拿旧配置)。
    """
    global _config_cache
    path = os.environ.get("TBTOOLS_CONFIG", DEFAULT_CONFIG_PATH)
    if _config_cache is not None and _config_cache[0] == path:
        return _config_cache[1]
    if not tomllib:
        return {}
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "rb") as f:
            _config_cache = (path, tomllib.load(f))
    except Exception:
        _config_cache = (path, {})
    return _config_cache[1]

def get_default(key, fallback=None):
    """获取默认值（配置文件 < 环境变量 < 命令行）"""
    cfg = load_config()
    defaults = cfg.get("defaults", {})
    return defaults.get(key, fallback)

def get_jar():
    """获取 JAR 路径（配置文件优先）"""
    cfg = load_config()
    return cfg.get("jar", "")
