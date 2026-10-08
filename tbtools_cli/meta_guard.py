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


def sources_content_fingerprint(root: str | None = None) -> str:
    """扫描源文件**内容** sha256 聚合(tbtools_cli/*.py + bridges/*.java).

    arch N8 修正(gate P0-2, v1.4.91 五视角): 原 mtime 指纹**不可提交**——fresh clone 后
    所有文件 mtime 相同, sidecar(提交时 mtime)与源码对比恒漂移, --check 在干净
    checkout 上确定性红; 内容 sha256 才是内容寻址: 源码不变则指纹稳定(可提交),
    源码变更(改代码未重跑 render)则指纹变 → 消费端告警。
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
            with open(_f, "rb") as _fh:
                _h.update(os.path.basename(_f).encode())
                _h.update(_fh.read())
        except OSError:
            pass
    return _h.hexdigest()


# 兼容别名(mtime 版退役, 防外部引用断裂)
sources_mtime_fingerprint = sources_content_fingerprint


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
                   "sources_content": sources_content_fingerprint(None)},
                  _f, ensure_ascii=False, indent=1)


def staleness_ok() -> bool:
    """消费端调用: 仓库 sidecar 指纹 vs 当前源码——一致=True(新鲜)。
    sidecar 缺失(老仓库/首跑) → True(无对比基准不打扰)。
    安装态(PyPI wheel, product P1-7 五视角自审): ROOT 无 bridges/ 目录时跳过比对——
    sidecar 是构建期固化的源码快照, 运行时(用户 site-packages)无需也不该再比
    (wheel 重设 mtime/路径布局与仓库不同, 比对必然假告警——警告疲劳比没有更糟)。"""
    try:
        if not os.path.isdir(os.path.join(ROOT, "bridges")):
            return True  # 安装态: 构建期快照, 不做运行时比对
        if not os.path.isfile(_SIDE_REPO):
            return True
        with open(_SIDE_REPO, encoding="utf-8") as _f:
            _stored = json.load(_f).get("sources_content")
        return bool(_stored) and _stored == sources_content_fingerprint()
    except Exception:
        return True  # 守卫自身故障不阻断(保守静默, 数据仍可读)
