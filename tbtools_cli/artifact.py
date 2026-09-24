"""Artifact 一等公民(ADR-0007): 数据载体模型——运行产物不再是裸路径,而是带类型/格式/溯源的结构化对象。

Artifact = Tool 之间传递的数据单元;workflow 的边。
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field

# 扩展名 → (artifact type, format) 语义映射(Agent 理解"这是什么",不只是"这是个文件")
TYPE_BY_EXT = {
    ".svg": ("plot", "svg"), ".png": ("plot", "png"), ".pdf": ("report", "pdf"),
    ".tsv": ("table", "tsv"), ".csv": ("table", "csv"), ".xls": ("table", "xls"),
    ".txt": ("table", "txt"), ".json": ("data", "json"),
    ".fa": ("sequence", "fasta"), ".fasta": ("sequence", "fasta"),
    ".fq": ("sequence", "fastq"), ".fastq": ("sequence", "fastq"),
    ".gff": ("annotation", "gff"), ".gff3": ("annotation", "gff3"), ".gtf": ("annotation", "gtf"),
    ".nwk": ("phylogenetic_tree", "newick"), ".tree": ("phylogenetic_tree", "newick"),
    ".aln": ("alignment", "fasta"), ".meme": ("motif", "meme"),
    ".collinearity": ("synteny", "tsv"), ".log": ("log", "txt"),
    ".gz": ("archive", "gzip"), ".out": ("report", "txt"),
}


@dataclass
class Artifact:
    """运行产物结构化对象(ADR-0007)。"""
    id: str
    type: str                    # plot|table|sequence|annotation|phylogenetic_tree|alignment|report|log|data
    format: str                  # svg|tsv|fasta|newick|...
    path: str
    uri: str = ""
    size: int = 0
    sha256: str = ""
    producer: str = ""           # 产生它的 tool(canonical name)
    created_at: str = ""
    schema_version: str = "1.0"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def classify(path: str) -> tuple[str, str]:
    """路径 → (type, format)。"""
    ext = os.path.splitext(path)[1].lower()
    return TYPE_BY_EXT.get(ext, ("file", ext.lstrip(".") or "unknown"))


def _sha256_file(path: str, _max: int = 256 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        read = 0
        while chunk := f.read(1 << 20):
            h.update(chunk)
            read += len(chunk)
            if read > _max:
                break
    return h.hexdigest()


def from_provenance(artifact_path: str) -> Artifact | None:
    """从 <artifact>.tbtools.json 构建 Artifact(溯源完整)。"""
    prov_path = artifact_path + ".tbtools.json"
    if not os.path.isfile(artifact_path) or not os.path.isfile(prov_path):
        return None
    prov = json.load(open(prov_path, encoding="utf-8"))
    _art = build(
        artifact_path,
        producer=prov.get("command", ""),
        metadata={"invocation": prov.get("invocation", ""),
                  "tbtools_cli": prov.get("tbtools_cli", ""),
                  "exit_code": prov.get("exit_code"),
                  "timestamp": prov.get("timestamp", "")},
    )
    register(_art)
    return _art


def build(path: str, producer: str = "", metadata: dict | None = None) -> Artifact:
    """从路径构建 Artifact(计算 type/format/size/sha256)。"""
    t, fmt = classify(path)
    size = os.path.getsize(path) if os.path.isfile(path) else 0
    return Artifact(
        id=f"art_{int(time.time()*1000)%10**10}_{os.path.basename(path)[:20]}",
        type=t, format=fmt, path=os.path.abspath(path),
        uri=f"file://{os.path.abspath(path)}",
        size=size,
        sha256=_sha256_file(path)[:16] if os.path.isfile(path) else "",
        producer=producer,
        created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
        metadata=metadata or {},
    )

# ── Artifact 索引(评审 #62 P0-6): art_id → path 登记与解析(去路径化基础)──
def _index_path() -> str:
    d = os.path.join(os.path.expanduser("~"), ".config", "tbtools-cli")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "artifacts.json")


def register(art: "Artifact"):
    """登记 Artifact 到索引(art_id → path)。"""
    try:
        idx = {}
        p = _index_path()
        if os.path.isfile(p):
            idx = json.load(open(p, encoding="utf-8"))
        idx[art.id] = {"path": art.path, "type": art.type, "format": art.format,
                       "producer": art.producer, "created_at": art.created_at}
        json.dump(idx, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    except Exception:
        pass


def resolve(ref: str) -> str | None:
    """art_id 或 path → path(索引解析;去路径化: workflow 可引用 art_id)。"""
    if os.path.isfile(ref):
        return ref
    p = _index_path()
    if os.path.isfile(p):
        try:
            idx = json.load(open(p, encoding="utf-8"))
            if ref in idx:
                return idx[ref]["path"]
        except Exception:
            pass
    return None
