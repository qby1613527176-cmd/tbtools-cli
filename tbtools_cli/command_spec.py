"""command_spec.py — 统一命令模型(CommandSpec, 第八轮评审核心建议骨架)。

目标: 所有命令产物(metadata/docs/help/search/统计)从单一 CommandSpec 模型派生,
不再各自从 ENGINE_REGISTRY / CLI_TOOLS / cli.py / CATEGORY_MAP 分散读取。

当前为兼容层骨架: 从现有注册源构建统一 specs(不改运行时行为),
gen_metadata 与后续工具以 specs 为唯一输入。
"""
from dataclasses import dataclass, field

from tbtools_cli import auto_commands as _ac
from tbtools_cli.cli_tools_registry import CLI_TOOLS
from tbtools_cli.cli_load import CATEGORY_MAP


@dataclass
class InputSpec:
    """命令输入定义(二期 schema: 类型/格式/必填)"""
    name: str
    role: str = "file"           # file | param
    format: str = ""             # gff3 | fasta | tsv | newick | ...
    required: bool = True
    note: str = ""


@dataclass
class CommandSpec:
    """单一命令定义(第八轮评审 CommandSpec 模型)"""
    name: str
    group: str
    kind: str                    # bridge | direct | tool | manual
    class_name: str = ""
    runner: str = ""             # plot | java | ""
    xmx: str = "2g"
    doc: str = ""
    status: str = "stable"       # stable|beta|legacy|platform-limited|network-required
    aliases: list[str] = field(default_factory=list)
    inputs: list[InputSpec] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)  # 输出类型(如 svg/png/tsv)


# 核心命令输入输出 schema 样例(证明模型模式; 全量标注为二期)
KNOWN_SCHEMAS = {
    "volcano": ([InputSpec("deg", format="tsv", note="GeneID\tLog2FC\tpvalue")], ["svg"]),
    "heatmap": ([InputSpec("matrix", format="tsv", note="表达矩阵 gene×sample")], ["svg"]),
    "hclust": ([InputSpec("distance", format="tsv", note="三列: GeneA\tGeneB\tdist")], ["svg"]),
    "venn2": ([InputSpec("list1", format="txt"), InputSpec("list2", format="txt")], ["svg"]),
    "msy": ([InputSpec("pos", format="tsv", note="Chr\tGene\tStart\tEnd"),
             InputSpec("links", format="tsv"), InputSpec("layout", format="txt")], ["svg"]),
    "genestructure": ([InputSpec("gff", format="gff3"), InputSpec("ids", format="txt")], ["svg"]),
    "motif": ([InputSpec("meme_xml", format="xml"), InputSpec("ids", format="txt")], ["svg"]),
    "peaktss": ([InputSpec("gxf", format="gff3"), InputSpec("peaks", format="tsv", note="MACS2")], ["svg"]),
    "tableMerge": ([InputSpec("tables", format="tsv", note="多个输入表")], ["tsv"]),
    "qdot": ([InputSpec("gff", format="tsv", note="4 列简化: Chr\tGene\tStart\tEnd")], ["svg"]),
    # 二期扩展批(高频绘图/工具)
    "dehist": ([InputSpec("deg", format="tsv", note="DEG 表")], ["svg"]),
    "pca": ([InputSpec("matrix", format="tsv", note="表达矩阵")], ["svg"]),
    "barplot": ([InputSpec("enrichment", format="tsv", note="富集表: 列名 Term/Pvalue")], ["svg"]),
    "circos": ([InputSpec("chrLen", format="tsv"), InputSpec("link", format="tsv"),
                InputSpec("genePos", format="tsv")], ["svg"]),
    "dotplot": ([InputSpec("gff", format="tsv", note="4 列简化"), InputSpec("pairs", format="tsv")], ["svg"]),
    "dualsyn": ([InputSpec("gff", format="tsv", note="简化 GFF"), InputSpec("pairs", format="tsv")], ["svg"]),
    "mcscanx": ([InputSpec("gff", format="tsv", note="chr\tgene\tstart\tend"),
                 InputSpec("blast", format="tsv", note="tab6")], ["tsv"]),
    "iqtree": ([InputSpec("aln", format="fasta")], ["nwk", "treefile"]),
    "muscle": ([InputSpec("fasta", format="fasta")], ["aln"]),
    "trimal": ([InputSpec("aln", format="fasta")], ["aln"]),
    "blastp": ([InputSpec("query", format="fasta"), InputSpec("db", format="fasta")], ["out"]),
    "sixframe": ([InputSpec("pep", format="fasta", note="蛋白(输出核酸)")], ["fa"]),
    "longestorf": ([InputSpec("seq", format="fasta", note="核酸输入")], ["fa"]),
    "seqlogo": ([InputSpec("seqs", format="fasta")], ["svg"]),
    "stat-fasta": ([InputSpec("fasta", format="fasta")], ["xls"]),
}


# 已知别名(兼容层命名; canonical → 命令)
KNOWN_ALIASES = {
    "treeRooting": "rooting",
    "TableCast": "tableCast",
    "gbar": "groupedbar",
    "gdensity": "genedensity",
    "getLongestCompleteORF": "longestorf",
    "one-step": "onesteptree",
    "genestructure": "structure",  # 旧名 → seq structure? 保留注释: genestructure 是独立命令
}

# 已知状态(engine 级/环境限制; 未列默认为 stable)
KNOWN_STATUS = {
    "srr2ena": "network-required",
    "pubmed": "network-required",
    "seqfetch": "network-required",
    "rnaplot": "platform-limited",       # 需 RNAfold 在 PATH(Windows 默认缺)
    "calcRepeat": "platform-limited",    # 需 jellyfish(Windows 默认缺)
    "hmmsearch": "platform-limited",     # 需系统 hmmsearch
    "simplehmmscan": "platform-limited",
    "cubeheatmap": "beta",               # 引擎列数假设严格(官方数据仍 ArrayIndexOutOfBounds)
    "groupedbar": "beta",
    "nwAlign": "beta",                   # 输入格式易错(FASTA 头被当序列)
}


def build_command_specs() -> dict[str, CommandSpec]:
    """构建统一命令模型(单一源, 兼容层: 不改变现运行行为)。

    来源:
      1. ENGINE_REGISTRY 表驱动(组 CATEGORY_MAP 归属)
      2. CLI_TOOLS 工具注册表
      3. 手动命令(经 cli_load 分组注册的 manual 命令, 从分组命令集补)
    """
    specs: dict[str, CommandSpec] = {}

    # 1. 表驱动引擎命令
    for name, kind, cls, xmx, runner, doc in _ac.ENGINE_REGISTRY:
        specs[name] = CommandSpec(
            name=name, group=CATEGORY_MAP.get(name, "engine"),
            kind=kind, class_name=cls, runner=runner, xmx=xmx, doc=doc,
        )

    # 2. CLI 工具(runner/xmx 对齐现 metadata 条目: java/3g)
    for name, cls in CLI_TOOLS.items():
        specs.setdefault(name, CommandSpec(name=name, group="tool", kind="tool", class_name=cls,
                                           runner="java", xmx="3g"))


    # 3. 手动命令: 从现有 metadata 回退(kind=manual 且未被表驱动/工具覆盖)
    #    (完整版应遍历 cli 分组命令树; 骨架期以 metadata 为准, 单一模型逐步接管)
    try:
        import json as _json
        import os as _os
        meta_path = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                                  "tbtools_cli", "command_metadata.json")
        if _os.path.isfile(meta_path):
            meta = _json.load(open(meta_path, encoding="utf-8"))
            for name, v in meta.items():
                if v.get("kind") == "manual" and name not in specs:
                    specs[name] = CommandSpec(
                        name=name, group=v.get("group", "engine"), kind="manual",
                        doc=v.get("help", ""),
                    )
    except Exception:
        pass

    # 别名/状态/schema 标注(统一模型增强; 在所有来源构建完成后)
    for name, spec in specs.items():
        spec.aliases = [a for a, target in KNOWN_ALIASES.items() if target == name]
        spec.status = KNOWN_STATUS.get(name, "stable")
        if name in KNOWN_SCHEMAS:
            ins, outs = KNOWN_SCHEMAS[name]
            spec.inputs, spec.outputs = ins, outs
    return specs


def specs_from_scans(reg, tools, manual, infer_group=None) -> dict[str, dict]:
    """扫描结果 → CommandSpec → metadata 投影(单一组装逻辑, gen_metadata 与工具共用)。

    reg/tools/manual: scan_* 输出的条目 dict(含 name/kind/class/runner/xmx/help/group)。
    infer_group: 可选分组推断函数(name, kind, src) -> str(manual 命令分组)。
    """
    from tbtools_cli.cli_load import CATEGORY_MAP as _CM
    specs = {}
    for name, e in reg.items():
        specs[name] = CommandSpec(name, _CM.get(name, "engine"), e.get("kind", "direct"),
                                  e.get("class", ""), e.get("runner") or "plot",
                                  e.get("xmx") or "2g", e.get("help", ""))
    for name, e in tools.items():
        specs.setdefault(name, CommandSpec(name, "tool", "tool", e.get("class", ""),
                                           "java", "3g", e.get("help", "")))
    for name, e in manual.items():
        grp = e.get("group") or (infer_group(name, "manual", e.get("src", "")) if infer_group else _CM.get(name, "engine"))
        specs.setdefault(name, CommandSpec(name, grp, "manual", runner="plot", doc=e.get("help", "")))
    for name, s in specs.items():
        s.aliases = [a for a, t in KNOWN_ALIASES.items() if t == name]
        s.status = KNOWN_STATUS.get(name, "stable")
        if name in KNOWN_SCHEMAS:
            s.inputs, s.outputs = KNOWN_SCHEMAS[name]
    return {n: to_metadata_entry(s) for n, s in specs.items()}


def to_metadata_entry(spec: CommandSpec) -> dict:
    """CommandSpec → metadata 条目(与现有 command_metadata.json 结构兼容)"""
    e: dict[str, object] = {"name": spec.name, "kind": spec.kind, "mode": spec.kind,
                            "class": spec.class_name, "xmx": spec.xmx, "runner": spec.runner,
                            "group": spec.group, "help": spec.doc}
    if spec.inputs:
        e["inputs"] = [{"name": i.name, "role": i.role, "format": i.format,
                        "required": i.required, "note": i.note} for i in spec.inputs]
    if spec.outputs:
        e["outputs"] = spec.outputs
    if spec.status != "stable":
        e["status"] = spec.status
    if spec.aliases:
        e["aliases"] = spec.aliases
    return e
