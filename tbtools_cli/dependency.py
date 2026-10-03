"""Dependency identity 解析层(评审 #112 P2 拆分): workflow.py 中依赖版本探测逻辑独立成模块。

定位: CommandSpec.dependencies 声明 → 三级优先解析外部工具版本(execution_fp 的一部分):
  1. dependency_manifest(KNOWN_DEPENDENCIES_STRUCT 的 executable/version_args, contract-driven)
  2. DEP_VERSION_ARGS 表(identity.py 常量)
  3. heuristic(--version/-version/-v, timeout=5, 截 40 字符, 缺失回退 "missing")

缓存: 模块级 _DEP_VERSION_CACHE(评审 #100 + #102 P1-2)——同一进程内外部依赖版本只探测一次,
防 flaky(每次 fork 查版本会因超时/失败随机漂移 execution_fp); 缓存 key 带可执行文件身份
(评审 #107 P1⑥: name+path+mtime+size, 防长期 Agent 进程缓存过期版本)。
"""
from __future__ import annotations

import os
import shutil
import subprocess

# 评审 #100 + #102 P1-2: 模块级缓存声明(原 workflow._DEP_VERSION_CACHE 迁移至此;
# workflow.py re-export 保持向后兼容)
_DEP_VERSION_CACHE: dict = {}


def resolve_dependencies(spec, cache: dict | None = None) -> dict:
    """按 spec.dependencies 解析外部工具版本(contract-driven)。

    spec: CommandSpec(需 .dependencies / .name)
    cache: 版本缓存 dict(默认用模块级 _DEP_VERSION_CACHE;测试可注入空 dict 隔离)
    返回 {dep_name: version_str|"missing"}——不探测 fork(调用方按 runtime_resolve 决定)。
    """
    _cache = cache if cache is not None else _DEP_VERSION_CACHE
    deps: dict = {}
    dep_names = list(getattr(spec, "dependencies", None) or [])
    if not dep_names:
        return deps
    try:
        from tbtools_cli.command_spec import KNOWN_DEPENDENCIES_STRUCT as _dep_struct
        from tbtools_cli.identity import DEP_VERSION_ARGS as _dva
    except Exception:
        _dep_struct, _dva = {}, {}
    for _dn in dep_names:
        # manifest → DEP_VERSION_ARGS 表 → heuristic 三级优先(评审 #108 P1-3 终态)
        _manifest_entry = None
        try:
            if spec.name in _dep_struct:
                for _e in _dep_struct[spec.name]:
                    if str(_e.get("name")) == _dn:
                        _manifest_entry = _e
                        break
        except Exception:
            pass
        _exe: str = _dn
        _exe_m = _manifest_entry.get("executable") if _manifest_entry else None
        if isinstance(_exe_m, str) and _exe_m:
            _exe = _exe_m
        # 缓存 key 带可执行文件身份(评审 #107 P1⑥: name + path + mtime + size)
        _dnorm = _exe.lower().replace("+", "").replace("-", "")
        _bin = shutil.which(_exe) or shutil.which(_dnorm)
        _resolved = "missing"
        _cache_key = _dn
        if _bin and os.path.isfile(_bin):
            try:
                _st = os.stat(_bin)
                _cache_key = f"{_dn}|{_bin}|{int(_st.st_mtime)}|{_st.st_size}"
            except OSError:
                pass
        if _cache_key in _cache:
            deps[_dn] = _cache[_cache_key]
            continue
        if _bin:
            _args: tuple[str, ...] | None = None
            _va = _manifest_entry.get("version_args") if _manifest_entry else None
            if isinstance(_va, (list, tuple)) and _va:
                _args = tuple(str(x) for x in _va)
            if not _args:
                _args = _dva.get(_dn, ("--version", "-version", "-v"))
            for _flag in _args or ("--version", "-version", "-v"):
                try:
                    _rv = subprocess.run([_bin, _flag], capture_output=True, text=True, timeout=5)
                    _ver = (_rv.stdout or _rv.stderr).strip().splitlines()
                    if _ver:
                        _resolved = _ver[0][:40]
                        break
                except Exception:
                    continue
        deps[_dn] = _resolved
        _cache[_cache_key] = _resolved
    return deps


def clear_dep_cache() -> None:
    """清空版本缓存(测试/热更新用)。"""
    _DEP_VERSION_CACHE.clear()
