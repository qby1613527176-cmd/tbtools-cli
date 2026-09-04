"""配置文件加载 — ~/.config/tbtools-cli/config.toml"""
import os

try:
    import tomllib
except ImportError:
    tomllib = None

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.config/tbtools-cli/config.toml")

_config_cache = None

def load_config():
    """加载配置文件。返回 dict（可能为空）"""
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    
    _config_cache = {}
    if not tomllib:
        return _config_cache
    
    path = os.environ.get("TBTOOLS_CONFIG", DEFAULT_CONFIG_PATH)
    if not os.path.isfile(path):
        return _config_cache
    
    try:
        with open(path, "rb") as f:
            _config_cache = tomllib.load(f)
    except Exception:
        pass
    return _config_cache

def get_default(key, fallback=None):
    """获取默认值（配置文件 < 环境变量 < 命令行）"""
    cfg = load_config()
    defaults = cfg.get("defaults", {})
    return defaults.get(key, fallback)

def get_jar():
    """获取 JAR 路径（配置文件优先）"""
    cfg = load_config()
    return cfg.get("jar", "")
