"""meta_guard.py — command_metadata.json 投影 staleness 守卫(自审 arch N8).

背景: P1-1 之后架构宣称 "specs 是唯一真源, command_metadata.json 是投影",
但 Agent 面(tool-describe/tool-run/list 等)直接读投影文件且无任何 staleness 检查
——开发者改 KNOWN_*/cli.py 未重跑 gen_metadata → Agent 看到旧数据且无提示。
yaml_to_snapshot 那套快照比对没有延伸到 JSON 投影(评审 #115 arch N8 P2)。

机制: 生成端(--render)写 sidecar 指纹文件, 消费端读投影前比对——
源码文件(tbtools_cli/*.py + bridges/*.java)的 mtime+size 聚合哈希。
任一源码编辑而未重跑 render → 指纹变 → 消费端 stderr warn(不阻断, 数据仍可用)。

生成端与消费端必须共用本模块的同一指纹算法(禁止两侧复制逻辑漂移)。
"""

import hashlib
import json
import os

from tbtools_cli.core import ROOT

_SIDE = "command_metadata.fingerprint.json"
_SIDE_REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), _SIDE)


def sources_mtime_fingerprint(root: str | None = None) -> str:
    """扫描源文件 mtime 聚合(tbtools_cli/*.py + bridges/*.java)。

    - 只取 .py/.java: 投影由这些源码扫描生成; sidecar/command_metadata.json 自身
      (.json) 不参与——防止"render 一次就自脏"。
    - mtime_ns + size: 内容变更必改 mtime(或至少 size), touch 不改内容也触发
      误报 warn(可容忍: warn 不阻断, 重跑 render 即消)。
    """
    r = root or ROOT
    _srcs: list[str] = []
    _tbt = os.path.join(r, "tbtools_cli")
    if os.path.isdir(_tbt):
        _srcs += [os.path.join(_tbt, f) for f in sorted(os.listdir(_tbt)) if f.endswith(".py")]
    _br = os.path.join(r, "bridges")
    if os.path.isdir(_br):
        _srcs += [os.path.join(_br, f) for f in sorted(os.listdir(_br)) if f.endswith(".java")]
    _h = hashlib.sha256()
    for _f in _srcs:
        try:
            _st = os.stat(_f)
            _h.update(f"{os.path.basename(_f)}:{_st.st_mtime_ns}:{_st.st_size}".encode())
        except OSError:
            pass
    return _h.hexdigest()


def sidecar_path(out_root: str | None = None) -> str:
    """sidecar 路径: out_root 下(临时渲染)或仓库 tbtools_cli/ 下。"""
    if out_root is not None:
        return os.path.join(out_root, "tbtools_cli", _SIDE)
    return _SIDE_REPO


def write_fingerprint(out_root: str | None = None) -> None:
    """生成端调用(gen_metadata _json_dump 同步写): 写 sidecar。
    指纹**始终基于仓库源码**(ROOT)——out_root 仅决定 sidecar 写盘位置(临时渲染时
    不算临时目录的源码, 否则 --check 的 tmp 渲染会算出空指纹致恒漂移)。"""
    _p = sidecar_path(out_root)
    _d = os.path.dirname(_p)
    if not os.path.isdir(_d):
        os.makedirs(_d, exist_ok=True)
    with open(_p, "w", encoding="utf-8") as _f:
        json.dump({"spec": "command_metadata",
                   "sources_mtime": sources_mtime_fingerprint(None)},
                  _f, ensure_ascii=False, indent=1)


def staleness_ok() -> bool:
    """消费端调用: 仓库 sidecar 指纹 vs 当前源码——一致=True(新鲜)。
    sidecar 缺失(老仓库/首跑) → True(无对比基准不打扰)。"""
    try:
        if not os.path.isfile(_SIDE_REPO):
            return True
        with open(_SIDE_REPO, encoding="utf-8") as _f:
            _stored = json.load(_f).get("sources_mtime")
        return bool(_stored) and _stored == sources_mtime_fingerprint()
    except Exception:
        return True  # 守卫自身故障不阻断(保守静默, 数据仍可读)
