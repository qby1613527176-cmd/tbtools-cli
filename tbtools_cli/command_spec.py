"""command_spec.py — 统一命令模型(CommandSpec, 第八轮评审核心建议骨架)。

目标: 所有命令产物(metadata/docs/help/search/统计)从单一 CommandSpec 模型派生,
不再各自从 ENGINE_REGISTRY / CLI_TOOLS / cli.py / CATEGORY_MAP 分散读取。

当前为兼容层骨架: 从现有注册源构建统一 specs(不改运行时行为),
gen_metadata 与后续工具以 specs 为唯一输入。
"""
import os
from dataclasses import dataclass, field

from tbtools_cli import auto_commands as _ac
from tbtools_cli.cli_tools_registry import CLI_TOOLS
from tbtools_cli.cli_load import CATEGORY_MAP


@dataclass
class ParamSpec:
    """命令参数定义(评审 #31 Tool Contract: 类型/默认值/是否必填)"""
    name: str
    type: str = "string"        # string|int|float|bool
    default: object = None
    required: bool = False
    note: str = ""
    cli_name: str = ""          # CLI 实际 flag(如 --pval-cutoff;评审 #56 P0-2 name↔CLI 分离)


@dataclass
class InputSpec:
    """命令输入定义(二期 schema: 类型/格式/必填)"""
    name: str
    role: str = "file"           # file | param
    format: str = ""             # gff3 | fasta | tsv | newick | ...
    required: bool = True
    note: str = ""
    columns: list[str] | None = None  # 列名契约(评审 #31: Agent 语义校验)
    # 生物学语义类型(biological semantic type;防 protein 进 dna 工具)
    content_type: str = "generic"  # dna | protein | alignment | table | annotation | tree | generic
    # 引擎真实 flag(评审 #110 建议④): ArgsParser 工具的 inputs 与引擎参数名可能不同
    # (tpmCalc: spec counts → 引擎 --countsTable); build_argv 据此拼 --flag value
    cli_name: str = ""




@dataclass
class InvocationSpec:
    """调用契约(评审 #70 P0-1 Contract Compiler):
    把 CommandSpec 的 inputs/outputs/parameters 编译成精确 argv 布局——
    消灭 {input}/$step.output/args[-1] 的三层猜测。

    布局约定(与现有引擎一致): [flag 参数对...] [输入(按声明序)] [输出路径]
    """
    inputs: list = field(default_factory=list)
    parameters: list = field(default_factory=list)
    outputs: list = field(default_factory=list)
    # grammar 扩展(评审 #72 P0-1): named-flag 布局(venn2: --List1 a --List2 b --graph out.svg)
    # None=positional 布局(默认); {"inputs": {name: flag}, "output": flag} = named-flag 布局
    named_flags: dict | None = None
    # token layout(评审 #74 P0-3): 精确 argv token 序列,元素:
    #   {"input": <idx>}          第 idx 个输入
    #   {"output": true}          输出路径
    #   {"flag": "--x", "param": "name"}  参数 flag(值来自 parameters)
    #   {"literal": "..."}        字面量
    # 声明则优先于 named_flags/positional 默认布局
    layout: list | None = None

    def build_argv(self, inputs: list, parameters: dict, output: str) -> list:
        """编译精确 argv:
        inputs: 按 InputSpec 声明序的路径列表
        parameters: {contract 名: 值}(自动翻译 cli_name + 类型验证 + bool flag 形式)
        output: 输出路径(末位)
        """
        argv: list = []
        # 1. flag 参数(先放,引擎 ArgsParser 任意位置可识别;layout 模式只验证不发射)
        _layout_mode = bool(self.layout)
        for k, v in parameters.items():
            ps = next((p for p in self.parameters if p.name == k), None)
            if ps is None:
                raise ValueError(f"UNKNOWN_PARAMETER: {k}")
            if ps.type == "int":
                try:
                    int(v)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"INVALID_PARAMETER_TYPE: {k} expected int, got {v!r}") from e
            elif ps.type == "float":
                try:
                    float(v)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"INVALID_PARAMETER_TYPE: {k} expected float, got {v!r}") from e
            if _layout_mode:
                continue  # layout 模式: flag 由 layout token 发射
            flag = ps.cli_name or ("--" + k.replace("_", "-"))
            if ps.type == "bool":
                if str(v).lower() in ("true", "1", "yes"):
                    argv.append(flag)
                continue
            argv += [flag, str(v)]
        # 2. 必填检查
        for ps in self.parameters:
            if ps.required and ps.name not in parameters:
                raise ValueError(f"MISSING_REQUIRED_PARAMETER: {ps.name}")
        # 3. 输入+输出(按 grammar 布局)
        req_inputs = [i for i in self.inputs if i.required]
        if len(inputs) < len(req_inputs):
            raise ValueError(f"MISSING_REQUIRED_INPUT: 需要 {len(req_inputs)} 个必填输入, 收到 {len(inputs)}")
        if self.layout:
            # token layout(评审 #74 P0-3 + #76 P0-1 严格检查):
            # 契约声明什么,编译就必须满足什么——禁止 silent skip(silently degrade 破坏可验证性)
            for tok in self.layout:
                if not isinstance(tok, dict) or len(tok) == 0:
                    raise ValueError(f"INVALID_LAYOUT_TOKEN: {tok!r}")
                if "input" in tok:
                    idx = int(tok["input"])
                    if idx < 0:
                        raise ValueError(f"INVALID_LAYOUT_INPUT: layout input index 为负: {idx}")
                    if idx >= len(inputs):
                        raise ValueError(
                            f"INVALID_LAYOUT_INPUT: layout 引用 input[{idx}], 但只提供 {len(inputs)} 个输入")
                    argv.append(str(inputs[idx]))
                elif "output" in tok:
                    if not output:
                        raise ValueError("MISSING_LAYOUT_OUTPUT: layout 要求 output token, 但 binding 未提供 output")
                    argv.append(str(output))
                elif "flag" in tok:
                    pname = tok.get("param", "")
                    if not pname:
                        raise ValueError(f"INVALID_LAYOUT_TOKEN: flag token 缺 param 字段: {tok!r}")
                    if pname not in [p.name for p in self.parameters]:
                        raise ValueError(f"UNKNOWN_LAYOUT_PARAMETER: layout 引用未声明参数: {pname}")
                    if pname not in parameters:
                        raise ValueError(f"MISSING_LAYOUT_PARAMETER: layout 要求参数 {pname}, 但 binding 未提供")
                    # bool 语义(评审 #80): true→flag 无值,false→跳过(不发 flag)
                    _ps = next((p for p in self.parameters if p.name == pname), None)
                    if _ps and _ps.type == "bool":
                        if str(parameters[pname]).lower() in ("true", "1", "yes"):
                            argv.append(tok["flag"])
                        continue
                    argv += [tok["flag"], str(parameters[pname])]
                elif "literal" in tok:
                    argv.append(str(tok["literal"]))
                else:
                    raise ValueError(f"INVALID_LAYOUT_TOKEN: 未知 token 类型: {tok!r}")
            # required input 覆盖检查(评审 #80): layout 必须消费所有必填输入
            used = {int(t["input"]) for t in self.layout if "input" in t}
            for idx, inp in enumerate(self.inputs):
                if inp.required and idx not in used:
                    raise ValueError(
                        f"INVALID_LAYOUT: layout 遗漏必填输入槽位 {inp.name}(input[{idx}])")
            return argv
        if self.named_flags:
            # named-flag 布局(评审 #72 P0-1): 输入/输出都走 flag(venn2: --List1/--List2/--graph)
            in_flags = self.named_flags.get("inputs", {})
            for idx, path in enumerate(inputs):
                slot = self.inputs[idx].name if idx < len(self.inputs) else f"in{idx}"
                argv += [in_flags.get(slot, f"--{slot}"), str(path)]
            if output:
                argv += [self.named_flags.get("output", "--output"), str(output)]
        else:
            # positional/flag 布局(默认): 任一 input 声明了 cli_name → 引擎是 ArgsParser 风格,
            # 按 --flag value 拼(评审 #110 建议④: tpmCalc spec counts → 引擎 --countsTable);
            # 否则纯位置参数 [输入(按声明序)] [输出路径]
            _any_flag = any(getattr(i, "cli_name", "") for i in self.inputs)
            if _any_flag:
                for idx, path in enumerate(inputs):
                    _cn = getattr(self.inputs[idx], "cli_name", "") if idx < len(self.inputs) else ""
                    argv += [_cn or f"--{self.inputs[idx].name if idx < len(self.inputs) else 'in' + str(idx)}",
                             str(path)]
                if output:
                    _out_cn = self.named_flags.get("output", "--output") if self.named_flags else "--output"
                    argv += [_out_cn, str(output)]
            else:
                argv += [str(i) for i in inputs]
                if output:
                    argv.append(str(output))
        return argv


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
    aliases: list[str] = field(default_factory=list)  # 反向: canonical → 别名们
    alias_of: str = ""           # 本命令是某 canonical 的兼容别名(如 treeRooting→rooting)
    inputs: list[InputSpec] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)  # 输出类型(如 svg/png/tsv)
    capabilities: list[str] = field(default_factory=list)  # 能力标签(能力图搜索)
    dependencies: list[str] = field(default_factory=list)  # 外部依赖(环境解析, GLM #22)
    relations: dict = field(default_factory=dict)          # 语义关系(能力图衔接, GLM #24)
    parameters: list = field(default_factory=list)         # ParamSpec 参数契约(Tool Contract)
    output_slots: list = field(default_factory=list)       # OutputSpec 输出槽位(评审 #86 P1-5)

    @property
    def output_formats(self) -> list:
        """唯一 output truth 访问口(评审 #94 P0-1): output_slots 优先,outputs 兜底。"""
        if self.output_slots:
            return [o.format for o in self.output_slots]
        return list(self.outputs)

    @property
    def invocation(self) -> "InvocationSpec":
        """调用契约投影(评审 #70): inputs+parameters → 可编译 argv 的 InvocationSpec。"""
        inv = InvocationSpec()
        inv.inputs = self.inputs
        inv.parameters = self.parameters
        inv.outputs = self.outputs
        if self.name in KNOWN_NAMED_FLAGS:
            inv.named_flags = KNOWN_NAMED_FLAGS[self.name]
        # Contract YAML 布局优先(评审 #80 P1-6)
        if self.__dict__.get("_contract_named_flags"):
            inv.named_flags = self.__dict__["_contract_named_flags"]
        if self.__dict__.get("_contract_layout"):
            inv.layout = self.__dict__["_contract_layout"]
        return inv


# ── named-flag 布局注册表(评审 #72 P0-1): 输入/输出全走 flag 的工具 ──
KNOWN_NAMED_FLAGS = {
    "venn2": {"inputs": {"list1": "--List1", "list2": "--List2"}, "output": "--graph"},
    "venn3": {"inputs": {"list1": "--List1", "list2": "--List2", "list3": "--List3"}, "output": "--graph"},
    "recipBlast": {"inputs": {"query": "--querySeqFile", "subject": "--subjectSeqFile"},
                   "output": "--outDirAndPrefix"},
    "tpmCalc": {"inputs": {"counts": "--countsTable", "lenInfo": "--lenInfo"},
                 "output": "--outTable"},
    "autoMakeBlastDb": {"inputs": {"fasta": "--inFasta"}, "output": "--outBase"},
}


# ── Contract Loader(评审 #80 P1-5): contracts/tools/*.yaml 正式声明层 ──
_CONTRACTS_CACHE: dict = {}
_CONTRACTS_MTIME: tuple = ()  # 文件指纹(mtime+size tuple;评审 #92)


def load_contracts() -> dict:
    """加载 contracts/tools/*.yaml(评审: CommandSpec 从聚合器变成 contract loader;
    YAML 声明优先于 KNOWN_* 内存表)。返回 {name: {inputs/outputs/parameters/capabilities/layout/...}}。"""
    import glob as _g

    import yaml as _y
    global _CONTRACTS_CACHE, _CONTRACTS_MTIME
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = sorted(_g.glob(os.path.join(root, "contracts", "tools", "*.yaml")))
    if not files:
        return {}
    # P0-2(评审 #92): 文件指纹(mtime+size 每文件 tuple)——max(mtime) 会漏"同秒改写/新增文件"
    _fp = tuple(sorted((f, os.path.getmtime(f), os.path.getsize(f)) for f in files))
    if _CONTRACTS_CACHE and _fp == _CONTRACTS_MTIME:
        return _CONTRACTS_CACHE
    out = {}
    global _CONTRACTS_ERRORS
    _CONTRACTS_ERRORS = []
    for f in files:
        try:
            d = _y.safe_load(open(f, encoding="utf-8"))
            if isinstance(d, dict) and d.get("name"):
                # P1-3(评审 #92): 重名契约记录(不再静默覆盖)
                if d["name"] in out:
                    _CONTRACTS_ERRORS.append({"code": "CONTRACT_DUPLICATE_NAME",
                                              "file": f, "name": d["name"]})
                out[d["name"]] = d
        except Exception as e:
            # P1-1(评审 #90): YAML 加载失败不再静默——收集供 doctor/validate 报告
            _CONTRACTS_ERRORS.append({"code": "CONTRACT_LOAD_ERROR", "file": f, "error": str(e)})
    _CONTRACTS_CACHE, _CONTRACTS_MTIME = out, _fp
    return out


_CONTRACTS_ERRORS: list = []


def contract_load_errors() -> list:
    """YAML 契约加载错误(评审 #90 P1-1): doctor/validate 可报告。"""
    load_contracts()  # 确保已加载
    return list(_CONTRACTS_ERRORS)


def _apply_contract_overlay(spec) -> None:
    """YAML 契约覆盖到 spec(YAML 胜出:inputs/outputs/parameters/capabilities/layout)。"""
    c = load_contracts().get(spec.name)
    if not c:
        return
    if "inputs" in c:  # 评审 #94: presence semantics(显式 []=清空)
        # merge by slot name(评审: YAML 未声明 content_type 时保留内存标注,不冲掉 slot 语义)
        _old_ct = {i.name: i.content_type for i in spec.inputs if i.content_type != "generic"}
        spec.inputs = [InputSpec(name=i.get("name", ""), role=i.get("role", "file"),
                                 format=i.get("format", ""), required=i.get("required", True),
                                 note=i.get("note", ""), columns=i.get("columns"),
                                 content_type=i.get("content_type")
                                 or _old_ct.get(i.get("name", ""), "generic"))
                       for i in c["inputs"]]
    # 🔴 P0(评审 #96): output_slots 优先读 YAML 声明(slots 是唯一真相,outputs 为投影);
    # 仅无 output_slots 时才从 outputs 重建(generic)——不再"用 outputs 覆盖掉 YAML 的 content_type"
    if "output_slots" in c:
        spec.output_slots = [OutputSpec(name=o.get("name", ""), format=o.get("format", ""),
                                        content_type=o.get("content_type", "generic"))
                             for o in c["output_slots"]]
        # outputs 从 slots 投影(一致性)
        spec.outputs = [o.format for o in spec.output_slots if o.format]
    elif "outputs" in c:  # P0-3(评审 #92): presence 检查——显式 [] 是有意清空
        spec.outputs = list(c["outputs"])
        # P0-1(评审 #94): outputs 覆盖时同步重建 output_slots——消灭 outputs/output_slots 漂移
        spec.output_slots = [OutputSpec(name=o, format=o) for o in c["outputs"]]
    if "parameters" in c:  # P0-3(评审 #92): presence 检查——显式 [] 是有意清空
        spec.parameters = [ParamSpec(name=p.get("name", ""), type=p.get("type", "string"),
                                     default=p.get("default"), required=p.get("required", False),
                                     note=p.get("note", ""), cli_name=p.get("cli_name", ""))
                           for p in c["parameters"]]
    if "capabilities" in c:  # P0-3(评审 #92): presence 检查——显式 [] 是有意清空
        # 评审 #109: YAML 仅兜底, 不覆盖代码真源(KNOWN_CAPABILITIES 已设的语义更准)——
        # 旧 YAML 快照(如 mastExtract: ['sequence'])曾覆盖新标注(如 ['motif','sequence_extraction']),
        # 造成 planner 语义丢失; 代码真源 > 生成产物(YAML 是 gen_metadata 导出物, 循环覆盖让旧值持久化)
        if not spec.capabilities:
            spec.capabilities = list(c["capabilities"])
    if "layout" in c:  # 评审 #94: presence semantics
        # layout 经 invocation 投影(named_flags 或 token layout)
        lay = c["layout"]
        if isinstance(lay, dict) and ("inputs" in lay or "output" in lay):
            spec.__dict__["_contract_named_flags"] = lay
        elif isinstance(lay, list):
            spec.__dict__["_contract_layout"] = lay


@dataclass
class OutputSpec:
    """输出槽位定义(评审 #86 P1-5): semantic matching 需要 output-slot → input-slot。"""
    name: str
    format: str = ""
    content_type: str = "generic"  # dna | protein | alignment | table | annotation | tree | generic


# 关键工具输出槽位(output slot 级语义;KNOWN_OUTPUT_CONTENT_TYPES 的槽位化)
KNOWN_OUTPUT_SLOTS = {
    "muscle": [OutputSpec("aln", format="fasta", content_type="alignment")],
    "trimal": [OutputSpec("aln", format="fasta", content_type="alignment")],
    "sixframe": [OutputSpec("pep", format="fasta", content_type="protein")],
    "pep2codon": [OutputSpec("cds", format="fasta", content_type="dna")],
    "iqtree": [OutputSpec("tree", format="nwk", content_type="tree")],
    "mcscanx": [OutputSpec("collinearity", format="tsv", content_type="table")],
    "recipBlast": [OutputSpec("result", format="tsv", content_type="table")],
    "volcano": [OutputSpec("plot", format="svg", content_type="plot")],  # 评审 #98: 输出是 plot 不是 table
}


# 核心命令输入输出 schema 样例(证明模型模式; 全量标注为二期)
# slot 级 content_type(评审 #80 P0-4): 按"输入槽位"标注,优先于工具级
KNOWN_INPUT_CONTENT_TYPES = {
    "pep2codon": {"cds": "dna", "pep_aln": "protein"},
    "sixframe": {"inFa": "dna", "dna": "dna", "pep": "dna"},  # 评审 #98: 输入是 DNA(pep 槽命名误导,兼容保留)
    "recipBlast": {"query": "protein", "subject": "protein"},
    "autoMakeBlastDb": {"fasta": "protein"},
    "dualsyn": {"gff": "annotation", "collinearity": "table"},
    "mcscanx": {"gff": "annotation", "blast": "table"},
}

# 输出 slot 级 content_type(评审 #84 P1-7): A.output-slot 语义(content_compat A 侧)
KNOWN_OUTPUT_CONTENT_TYPES = {
    "muscle": "alignment", "trimal": "alignment", "sixframe": "protein",
    "pep2codon": "dna", "blastp": "table", "blastn": "table", "diamond": "table",
    "recipBlast": "table", "mcscanx": "table", "hmmsearch": "table",
    "iqtree": "tree", "phylotree": "tree", "fasttree": "tree",
}

# content_type 标注表(biological semantic type;按工具名挂语义——slot 级无标注时兜底)
KNOWN_CONTENT_TYPES = {
    "muscle": "sequence", "trimal": "alignment", "iqtree": "alignment", "phylotree": "alignment",  # 评审 #98: muscle DNA+蛋白双兼容
    "blastp": "protein", "blastn": "dna", "diamond": "protein", "recipBlast": "protein",
    "hmmsearch": "protein", "simpleHmmscan": "protein", "pep2codon": "protein",
    "sixframe": "dna", "longestorf": "dna", "cpg": "dna", "seqlogo": "alignment",
    "msa": "alignment", "genestructure": "annotation", "gxfSplit": "annotation",
    "volcano": "table", "dehist": "table", "hclust": "table", "barplot": "table",
    "heatmap": "table", "goEnrich": "table", "keggEnrich": "table", "gsea": "table",
    "mcscanx": "table", "dualsyn": "table", "fasta2phy": "dna",
}

KNOWN_SCHEMAS = {
    "volcano": ([InputSpec("deg", format="tsv", note="GeneID\tLog2FC\tpvalue", columns=["GeneID", "Log2FC", "pvalue"])], ["svg"]),
    "heatmap": ([InputSpec("matrix", format="tsv", note="首列 gene ID", columns=["gene_id"])], ["svg"]),
    "hclust": ([InputSpec("distance", format="tsv", note="三列距离", columns=["GeneA", "GeneB", "distance"])], ["svg"]),
    "venn2": ([InputSpec("list1", format="txt"), InputSpec("list2", format="txt")], ["svg"]),
    "msy": ([InputSpec("pos", format="tsv", note="Chr\tGene\tStart\tEnd"),
             InputSpec("links", format="tsv"), InputSpec("layout", format="txt")], ["svg"]),
    "genestructure": ([InputSpec("gff", format="gff3"), InputSpec("ids", format="txt")], ["svg"]),
    "motif": ([InputSpec("meme_xml", format="xml"), InputSpec("ids", format="txt")], ["svg"]),
    "peaktss": ([InputSpec("gxf", format="gff3"), InputSpec("peaks", format="tsv", note="MACS2")], ["svg"]),
    "tableMerge": ([InputSpec("tables", format="tsv", note="多个输入表")], ["tsv"]),
    "qdot": ([InputSpec("gff", format="tsv", note="4 列简化: Chr\tGene\tStart\tEnd")], ["svg"]),
    # 二期扩展批(高频绘图/工具)
    "dehist": ([InputSpec("deg", format="tsv", note="DEG 表", columns=["GeneID", "Log2FC", "pvalue"])], ["svg"]),
    "pca": ([InputSpec("matrix", format="tsv", note="首列 gene ID", columns=["gene_id"])], ["svg"]),
    "barplot": ([InputSpec("enrichment", format="tsv", note="富集表", columns=["Term", "Pvalue"])], ["svg"]),
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
    "sixframe": ([InputSpec("dna", format="fasta", note="DNA 序列输入(6-frame 翻译为蛋白)")], ["fasta"]),  # 评审 #100: 命名+note 语义修正(输入 DNA 输出蛋白,原"蛋白(输出核酸)"完全写反)
    "longestorf": ([InputSpec("seq", format="fasta", note="核酸输入")], ["fa"]),
    "seqlogo": ([InputSpec("seqs", format="fasta")], ["svg"]),
    "stat-fasta": ([InputSpec("fasta", format="fasta")], ["xls"]),
    # 三期批次(schema 标注继续)
    "venn3": ([InputSpec("list1", format="txt"), InputSpec("list2", format="txt"),
               InputSpec("list3", format="txt")], ["svg"]),
    "venn4": ([InputSpec("list1", format="txt"), InputSpec("list2", format="txt"),
               InputSpec("list3", format="txt"), InputSpec("list4", format="txt")], ["svg"]),
    "upset": ([InputSpec("sets", format="txt", note="多个集合文件, 末参为输出")], ["svg"]),
    "tpmCalc": ([InputSpec("counts", format="tsv", note="counts 表", cli_name="--countsTable"),
                   InputSpec("lenInfo", format="tsv", columns=["GeneID", "Length"], cli_name="--lenInfo")], ["tsv"]),
    "gxfSplit": ([InputSpec("gff", format="gff3")], ["tsv"]),
    "gxfAttr": ([InputSpec("gff", format="gff3")], ["tsv"]),
    "gxfIdAppender": ([InputSpec("gff", format="gff3")], ["gff3"]),
    "recipBlast": ([InputSpec("query", format="fasta"), InputSpec("subject", format="fasta")], ["tsv"]),
    "autoMakeBlastDb": ([InputSpec("fasta", format="fasta")], ["db"]),
    "genelocgff": ([InputSpec("gff", format="gff3"), InputSpec("ids", format="txt")], ["svg"]),
    "treeRooting": ([InputSpec("nwk", format="newick", note="需枝长")], ["nwk"]),
    "memerun": ([InputSpec("fasta", format="fasta")], ["meme"]),
    "mastrun": ([InputSpec("meme", format="meme")], ["xml"]),
    "goEnrich": ([InputSpec("background", format="tsv"), InputSpec("target", format="tsv")], ["tsv"]),
    "keggEnrich": ([InputSpec("background", format="tsv"), InputSpec("target", format="tsv")], ["tsv"]),
    "gsea": ([InputSpec("expr", format="tsv"), InputSpec("cls", format="txt")], ["xls"]),
    "efpHeat": ([InputSpec("tga", format="tga", note="TrueColor type2"), InputSpec("expMat", format="tsv")], ["svg"]),
    "multiEfp": ([InputSpec("tga", format="tga"), InputSpec("expMat", format="tsv")], ["svg"]),
    "layoutheatmap": ([InputSpec("expr", format="tsv"), InputSpec("layout", format="tsv")], ["svg"]),
    # 第三批(常用绘图/工具)
    "microsyn": ([InputSpec("gff", format="tsv", note="简化 GFF"),
                  InputSpec("links", format="tsv")], ["svg"]),
    "multisyn": ([InputSpec("gff", format="tsv"), InputSpec("gxf_lst", format="txt")], ["svg"]),
    "pafviz": ([InputSpec("paf", format="tsv", note="13 列 PAF")], ["svg"]),
    "pafref": ([InputSpec("paf", format="tsv", note="含 cg:Z CIGAR")], ["svg"]),
    "peakanno": ([InputSpec("peaks", format="tsv", note="MACS2, 百万级坐标")], ["tsv"]),
    "supercircos": ([InputSpec("config", format="txt", note="[chrLen] 等节")], ["svg"]),
    "gel": ([InputSpec("lanes", format="tsv", note="LaneLabels 逗号分隔")], ["svg"]),
    "plotrna": ([InputSpec("seq", format="fasta")], ["pdf"]),
    "pep2codon": ([InputSpec("cds", format="fasta"), InputSpec("pep_aln", format="fasta")], ["fa"]),
    "mcscanxd": ([InputSpec("gff", format="tsv"), InputSpec("blast", format="tsv")], ["collinearity"]),
    "notung": ([InputSpec("tree", format="newick"), InputSpec("gene_tree", format="newick")], ["nwk"]),
    "newickRename": ([InputSpec("nwk", format="newick")], ["nwk"]),
    "hmmerSearch": ([InputSpec("hmm", format="hmm"), InputSpec("seq", format="fasta")], ["tsv"]),
    "memeViz": ([InputSpec("meme", format="meme")], ["svg"]),
    "kallisto": ([InputSpec("fastq", format="fastq", note="RNA-seq")], ["tsv"]),
    "tfbsShift": ([InputSpec("motif", format="meme")], ["tsv"]),
    "smart": ([InputSpec("seq", format="fasta")], ["tsv"]),
    "barplotter": ([InputSpec("gff", format="gff3"), InputSpec("synteny", format="tsv")], ["svg"]),
    "calcRepeat": ([InputSpec("fasta", format="fasta")], ["tsv"]),
    "rnaplot": ([InputSpec("seq", format="fasta")], ["svg"]),
    "preparespecies": ([InputSpec("genome", format="fasta"), InputSpec("gff", format="gff3")], ["fasta"]),
}


# 命令参数契约(评审 #31: Agent 知道参数类型/默认值)
KNOWN_PARAMS = {
    "volcano": [ParamSpec("pval_cutoff", "float", 0.05, cli_name="--pval-cutoff"), ParamSpec("fc_cutoff", "float", 1.0, cli_name="--fc-cutoff"),
                ParamSpec("w", "int", 1000), ParamSpec("h", "int", 800)],
    "heatmap": [ParamSpec("w", "int", 1000), ParamSpec("h", "int", 800),
                ParamSpec("log2", "bool", False), ParamSpec("row_scale", "bool", False)],
    "hclust": [ParamSpec("w", "int", 1000), ParamSpec("h", "int", 800),
               ParamSpec("t", "int", 4, note="线程")],
    "genestructure": [ParamSpec("w", "int", 1000), ParamSpec("h", "int", 800),
                      ParamSpec("genome", "string", None, note="可选基因组 FASTA")],
    "dehist": [ParamSpec("w", "int", 1000), ParamSpec("h", "int", 800)],
    "mcscanx": [ParamSpec("t", "int", 4), ParamSpec("w", "int", 1000), ParamSpec("h", "int", 800)],
    "dualsyn": [ParamSpec("chr1", "string", None, note="逗号分隔染色体"), ParamSpec("chr2", "string", None)],
    "iqtree": [ParamSpec("bb", "int", 1000, note="UFBoot ≥1000"), ParamSpec("t", "int", 4)],
}


# 命令外部依赖结构化(评审 #29: 类型/必需性/平台; env 工具级解析)
# 格式: command -> [{"name": str, "type": binary|capability, "required": bool, "platforms": [str]}]
KNOWN_DEPENDENCIES_STRUCT = {
    "hmmsearch": [{"name": "hmmer", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                    "executable": "hmmsearch", "version_args": ["-h"]}],
    "simplehmmscan": [{"name": "hmmer", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                       "executable": "hmmscan", "version_args": ["-h"]}],
    "calcRepeat": [{"name": "jellyfish", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                    "executable": "jellyfish", "version_args": ["--version"]}],
    "rnaplot": [{"name": "rnafold", "type": "binary", "required": True, "platforms": ["linux"],
                 "executable": "RNAfold", "version_args": ["--version"]}],
    "plotrna": [{"name": "rnafold", "type": "binary", "required": True, "platforms": ["linux"],
                 "executable": "RNAfold", "version_args": ["--version"]}],
    "kallisto": [{"name": "kallisto", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                  "executable": "kallisto", "version_args": ["version"]}],
    "diamond": [{"name": "diamond", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                 "executable": "diamond", "version_args": ["--version"]}],
    "mcscanxd": [{"name": "mcscanx", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                  "executable": "MCScanX", "version_args": []}],
    "blastp": [{"name": "blast+", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                "executable": "blastp", "version_args": ["-version"]}],
    "blastn": [{"name": "blast+", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                "executable": "blastn", "version_args": ["-version"]}],
    "muscle": [{"name": "muscle", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                 "executable": "muscle", "version_args": ["-version"]}],
    "mafft": [{"name": "mafft", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                "executable": "mafft", "version_args": ["--version"]}],
    "iqtree": [{"name": "iqtree2", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                 "executable": "iqtree2", "version_args": ["--version"]}],
    "onesteptree": [{"name": "iqtree2", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                    "executable": "iqtree2", "version_args": ["--version"]}],
    "trimal": [{"name": "trimal", "type": "binary", "required": True, "platforms": ["linux", "macos"],
                "executable": "trimal", "version_args": ["-version"]}],
    "taxparse": [{"name": "internet", "type": "capability", "required": True, "platforms": ["linux", "macos", "windows"]}],
    "sraxml2tab": [{"name": "internet", "type": "capability", "required": False, "platforms": ["linux", "macos", "windows"]}],
}


# 兼容层(评审 #52 P1-3 合并): 简单 list 由 STRUCT 派生, 单一事实源
KNOWN_DEPENDENCIES: dict = {cmd: [str(d["name"]) for d in deps] for cmd, deps in KNOWN_DEPENDENCIES_STRUCT.items()}


# 能力 ontology(评审 #52 P1-7): 分层标签 domain.subdomain
# 平标签 → 分层父链(Agent 可用 "phylogeny.tree-building" 或 "phylogeny" 查询)
ONTOLOGY = {
    "alignment": "sequence.alignment",
    "expression_matrix": "expression.matrix",
    "gene_structure": "annotation.gene_structure",
    "translation": "sequence.translation",
    "extraction": "sequence.extraction",
    "conversion": "sequence.conversion",
    "sequence": "sequence",
    "homology": "sequence.homology",
    "hmm_scan": "sequence.homology.hmm_scan",
    "filtering": "sequence.homology.filtering",
    "reciprocal_best_hit": "sequence.homology.reciprocal_best_hit",
    "phylogeny": "phylogeny",
    "rooting": "phylogeny.rooting",
    "reconciliation": "phylogeny.reconciliation",
    "tree_building": "phylogeny.tree-building",
    "tree_editing": "phylogeny.editing",
    "synteny": "genomics.synteny",
    "collinearity": "genomics.synteny",
    "collinearity_detection": "genomics.synteny.detection",
    "microsynteny": "genomics.synteny.microsynteny",
    "annotation": "genomics.annotation",
    "gff_fixing": "genomics.annotation.fixing",
    "gff_ops": "genomics.annotation.ops",
    "genome_analysis": "genomics",
    "genome_circos": "genomics.circos",
    "expression": "expression",
    "differential_expression": "expression.differential",
    "normalization": "expression.normalization",
    "rna_seq": "expression.rna-seq",
    "quantification": "expression.rna-seq.quantification",
    "enrichment": "expression.enrichment",
    "gene_ontology": "expression.enrichment.go",
    "pathway": "expression.enrichment.pathway",
    "clustering": "expression.clustering",
    "distance": "expression.clustering.distance",
    "dimension_reduction": "expression.dimension-reduction",
    "statistics": "expression.statistics",
    "visualization": "visualization",
    "motif": "sequence.motif",
    "scanning": "sequence.motif.scanning",
    "discovery": "sequence.motif.discovery",
    "genome_scan": "sequence.motif.genome-scan",
    "domain": "sequence.domain",
    "orf_prediction": "sequence.orf-prediction",
    "chip_seq": "chip-seq",
    "peak_calling": "chip-seq.peak-calling",
    "peak_annotation": "chip-seq.peak-annotation",
    "assembly": "genomics.assembly",
    "ngs": "sequence.ngs",
    "preprocessing": "sequence.ngs.preprocessing",
    "set_operations": "sets",
    "table_operations": "table",
    "viral_analysis": "virus",
}


def expand_ontology(tags: list[str]) -> list[str]:
    """平标签 → 含分层父链的全集(如 alignment → [sequence.alignment, sequence])。

    Agent 用 'phylogeny' 查询时, 'phylogeny.tree-building' 也命中(父链展开)。
    """
    out = set()
    for t in tags:
        out.add(t)
        full = ONTOLOGY.get(t, t)
        parts = full.split(".")
        for i in range(1, len(parts) + 1):
            out.add(".".join(parts[:i]))
    return sorted(out)


# 组级能力兜底(无精确标注的命令按组归能力域; 优先精确标注, 后兜底)
GROUP_CAPABILITIES = {
    "expr": ["expression"], "syn": ["synteny"], "gxf": ["annotation"],
    "table": ["table_operations"], "fastq": ["ngs", "sequence"],
    "blast": ["homology"], "asm": ["assembly"], "chipseq": ["chip_seq"],
    "tree": ["phylogeny"], "seq": ["sequence"], "efp": ["expression"],
    "sets": ["set_operations"], "enrich": ["enrichment"], "virus": ["viral_analysis"],
    "genome": ["genome_analysis"], "assembly": ["assembly"],
}


# 工具语义关系(能力图: 输入输出衔接; GLM #24)——核心命令标注
KNOWN_RELATIONS = {
    "volcano":  {"accepts": ["DEG_TABLE"], "produces": ["VOLCANO_PLOT"],
                 "next_step": ["goEnrich", "keggEnrich"], "related_to": ["dehist", "heatmap"]},
    "dehist":   {"accepts": ["DEG_TABLE"], "produces": ["DEG_HISTOGRAM"],
                 "related_to": ["volcano"]},
    "heatmap":  {"accepts": ["EXPRESSION_MATRIX"], "produces": ["HEATMAP"],
                 "next_step": ["hclust"], "related_to": ["pca"]},
    "pca":      {"accepts": ["EXPRESSION_MATRIX"], "produces": ["PCA_PLOT"]},
    "hclust":   {"accepts": ["DISTANCE_TABLE"], "produces": ["DENDROGRAM"],
                 "related_to": ["heatmap"]},
    "mcscanx":  {"accepts": ["GFF", "BLAST_TAB6"], "produces": ["COLLINEARITY"],
                 "next_step": ["dualsyn", "dotplot"]},
    "dualsyn":  {"accepts": ["SIMPLIFIED_GFF", "COLLINEARITY"], "produces": ["SYNTENY_PLOT"]},
    "dotplot":  {"accepts": ["SIMPLIFIED_GFF", "COLLINEARITY"], "produces": ["DOTPLOT"]},
    "muscle":   {"accepts": ["FASTA"], "produces": ["ALIGNMENT"], "next_step": ["trimal", "iqtree"]},
    "trimal":   {"accepts": ["ALIGNMENT"], "produces": ["TRIMMED_ALIGNMENT"], "next_step": ["iqtree"]},
    "iqtree":   {"accepts": ["ALIGNMENT"], "produces": ["PHYLOGENY_NWK"], "next_step": ["tree"]},
    "tpmCalc":  {"accepts": ["COUNTS_TABLE", "GENE_LENGTH"], "produces": ["TPM_TABLE"],
                 "next_step": ["pca", "heatmap", "volcano"]},
    "gsea":     {"accepts": ["EXPRESSION_TABLE", "PHENOTYPE_CLS"], "produces": ["GSEA_REPORT"]},
    "genestructure": {"accepts": ["GFF3", "GENE_ID_LIST"], "produces": ["GENE_STRUCTURE_PLOT"]},
    "kallisto": {"accepts": ["FASTQ"], "produces": ["QUANT_TABLE"], "next_step": ["tpmCalc"]},
    # 评审 #109(Planner 决策质量): 精确 relations 覆盖教程实证场景——
    # 组级兜底会污染同组工具(seq 组全部变 SEQUENCE_ARTIFACT 万能中介), 关键工具必须精确标注
    "recipBlast": {"accepts": ["FASTA"], "produces": ["BLAST_HITS", "RBH_TABLE"],
                   "next_step": ["filterCScore"], "related_to": ["twoSeqBlast"]},
    "twoSeqBlast": {"accepts": ["FASTA"], "produces": ["BLAST_HITS"], "related_to": ["recipBlast"]},
    "extractFasta": {"accepts": ["FASTA", "GENE_ID_LIST"], "produces": ["SEQUENCE_SUBSET", "FASTA"],
                      "related_to": ["extractFastaSub"]},
    "statFasta": {"accepts": ["FASTA"], "produces": ["FASTA_STATS", "TSV"], "related_to": ["fastaExtract"]},
    "dnDsCalculate": {"accepts": ["ALIGNMENT"], "produces": ["KAKS_TABLE"], "related_to": ["muscle"]},
    "hmmsearch": {"accepts": ["FASTA", "HMM_PROFILE"], "produces": ["HMM_HITS", "TSV"]},
    "sixframe": {"accepts": ["DNA_FASTA"], "produces": ["PROTEIN_FASTA"], "related_to": ["longestorf"]},
    "longestorf": {"accepts": ["DNA_FASTA"], "produces": ["PROTEIN_FASTA"], "related_to": ["sixframe"]},
    "memerun": {"accepts": ["PROTEIN_FASTA"], "produces": ["MEME_XML"], "next_step": ["motif"]},
    "tfbsShift": {"accepts": ["MEME_XML"], "produces": ["TFBS_TABLE"], "related_to": ["motif"]},
    # 评审 #109: 清理 seq 组万能中介——组兜底把 pep2codon/structure/mastExtract 全变成
    # FASTA→SEQUENCE_ARTIFACT 等价工具, planner 无法区分真实语义, 大量错误规划源于此
    "pep2codon": {"accepts": ["PROTEIN_ALIGNMENT"], "produces": ["CODON_ALIGNMENT"], "related_to": ["muscle"]},
    "structure": {"accepts": ["GFF3"], "produces": ["GENE_STRUCTURE_PLOT"], "related_to": ["genestructure"]},
    "mastExtract": {"accepts": ["MEME_XML", "HMM_HITS"], "produces": ["SEQUENCE_SUBSET"], "related_to": ["memerun"]},
    # 评审 #109: 空壳 spec 抢占——hmmerSearch(无 relations/caps 的空壳) 曾靠 name 命中 goal 抢走
    # hmmsearch(真工具) 的规划; 空壳补精确关系让其可识别但语义明确
    "hmmerSearch": {"accepts": ["FASTA", "HMM_PROFILE"], "produces": ["HMM_HITS"], "related_to": ["hmmsearch"]},
    "calcRepeat": {"accepts": ["DNA_FASTA"], "produces": ["REPEAT_SCAN"], "related_to": ["careclassify"]},
    "smart": {"accepts": ["PROTEIN_FASTA"], "produces": ["DOMAIN_ANNOTATION"], "related_to": ["cddmotif"]},
    "memeViz": {"accepts": ["MEME_XML"], "produces": ["MOTIF_PLOT"], "related_to": ["memerun"]},
}


# 组级关系兜底(无精确关系命令按组给默认衔接; 优先 KNOWN_RELATIONS)
GROUP_RELATIONS = {
    "syn":   {"accepts": ["SIMPLIFIED_GFF", "COLLINEARITY"], "produces": ["SYNTENY_PLOT"],
              "next_step": ["dualsyn", "dotplot"], "related_to": ["mcscanx"]},
    "expr":  {"accepts": ["EXPRESSION_TABLE"], "produces": ["PLOT"],
              "related_to": ["volcano", "heatmap"]},
    "tree":  {"accepts": ["ALIGNMENT", "NEWICK"], "produces": ["PHYLOGENY_NWK"],
              "next_step": ["tree"]},
    "seq":   {"accepts": ["FASTA", "GFF3"], "produces": ["SEQUENCE_ARTIFACT"],
              "related_to": ["muscle", "trimal"]},
    "gxf":   {"accepts": ["GFF3"], "produces": ["ANNOTATION_OUT"]},
    "table": {"accepts": ["TABLE"], "produces": ["TABLE_OUT"]},
    "blast": {"accepts": ["FASTA"], "produces": ["BLAST_HITS"],
              "next_step": ["filterCScore"]},
    "chipseq": {"accepts": ["ALIGNMENT", "PEAKS"], "produces": ["PEAK_ANNOTATION"]},
    "fastq": {"accepts": ["FASTQ"], "produces": ["SEQUENCE_ARTIFACT"],
              "next_step": ["kallisto", "tpmCalc"]},
    "asm":     {"accepts": ["GENOME", "GFF"], "produces": ["ASSEMBLY_OUT"]},
    "virus":   {"accepts": ["FASTA", "REF_DB"], "produces": ["VIRUS_ANNOTATION"]},
    "efp":     {"accepts": ["TGA", "EXP_MATRIX"], "produces": ["EFP_HEATMAP"]},
    "sets":    {"accepts": ["GENE_LISTS"], "produces": ["SET_DIAGRAM"],
                "related_to": ["venn2", "venn3", "upset"]},
    "enrich":  {"accepts": ["GENE_LISTS"], "produces": ["ENRICHMENT_REPORT"],
                "next_step": ["barplot"]},
    "genome":  {"accepts": ["GENOME"], "produces": ["GENOME_OUT"]},
}


# 已知别名(兼容层命名; canonical → 命令)
KNOWN_CAPABILITIES = {
    "volcano": ["differential_expression", "visualization"],
    "heatmap": ["expression_matrix", "clustering", "visualization"],
    "dehist": ["differential_expression", "visualization"],
    "pca": ["dimension_reduction", "expression_matrix"],
    "hclust": ["clustering", "distance"],
    "genestructure": ["gene_structure", "annotation", "visualization"],
    "seqlogo": ["motif", "visualization"],
    "msa": ["alignment", "visualization"],
    "motif": ["motif", "visualization"],
    "sixframe": ["translation", "sequence"],
    "longestorf": ["orf_prediction", "sequence"],
    "blastp": ["homology", "alignment"],
    "mcscanx": ["synteny", "collinearity"],
    "dualsyn": ["synteny", "visualization"],
    "dotplot": ["synteny", "visualization"],
    "msy": ["microsynteny", "visualization"],
    "iqtree": ["phylogeny"],
    "muscle": ["alignment"],
    "trimal": ["alignment", "filtering"],
    "kallisto": ["rna_seq", "quantification"],
    "gsea": ["enrichment"],
    "goEnrich": ["enrichment"],
    "keggEnrich": ["enrichment"],
    "tpmCalc": ["rna_seq", "normalization"],
    "peaktss": ["chip_seq"],
    # 评审 #109(Planner 决策质量): kind=tool/manual 工具缺能力标注 → goal 语义匹配永远选不到
    "dnDsCalculate": ["ka_ks", "evolutionary_analysis"],
    "extractFasta": ["sequence", "extraction"],
    "statFasta": ["sequence", "statistics"],
    "hmmerSearch": ["homology", "hmm_scan"],
    "pep2codon": ["translation", "codon"],
    "mastExtract": ["motif", "sequence_extraction"],
    "preparespecies": ["genome_preparation", "annotation"],
    "fastaExtract": ["sequence", "extraction"],
    "mastrun": ["motif", "scanning"],
    # structure 是空壳 manual(无 class/inputs)占位, 不授予真工具语义——
    # 曾因 name 'structure' 精确命中 goal 词赢过 genestructure(评审 #109)
    "structure": ["sequence"],
}
# 精确标注补充(2026-09-23): 覆盖组级兜底的粗标签, 核心命令细化
KNOWN_CAPABILITIES.update({
    "mcscanx": ["synteny", "collinearity_detection"],
    "dualsyn": ["synteny", "visualization"],
    "dotplot": ["synteny", "visualization"],
    "circos": ["visualization", "genome_circos"],
    "collinearRegion": ["synteny", "visualization"],
    "pafviz": ["synteny", "visualization"],
    "pafref": ["synteny", "visualization"],
    "microsyn": ["synteny", "visualization"],
    "multisyn": ["synteny", "visualization"],
    "qdot": ["synteny", "visualization"],
    "fimo": ["motif", "scanning"],
    "mastrun": ["motif", "scanning"],
    "memerun": ["motif", "discovery"],
    "memeViz": ["motif", "visualization"],
    "seqlogo": ["motif", "visualization"],
    "tfbsShift": ["motif", "genome_scan"],
    "smart": ["domain", "annotation"],
    "hmmsearch": ["homology", "hmm_scan"],
    "diamond": ["homology", "alignment"],
    "blastp": ["homology", "alignment"],
    "blastn": ["homology", "alignment"],
    "recipBlast": ["homology", "reciprocal_best_hit", "blast"],
    "filterCScore": ["homology", "filtering"],
    "kallisto": ["rna_seq", "quantification"],
    "fqTrim": ["ngs", "preprocessing"],
    "fqfaConv": ["sequence", "conversion"],
    "fastaExtract": ["sequence", "extraction"],
    "fastaSubseq": ["sequence", "extraction"],
    "gffFix": ["annotation", "gff_fixing"],
    "gxfAppend": ["annotation", "gff_ops"],
    "genelocation": ["annotation", "visualization"],
    "peaktss": ["chip_seq", "peak_calling"],
    "peakanno": ["chip_seq", "peak_annotation"],
    "tpmCalc": ["rna_seq", "normalization"],
    "efpHeat": ["expression", "visualization"],
    "layoutheatmap": ["expression", "visualization"],
    "gsea": ["enrichment"],
    "goEnrich": ["enrichment", "gene_ontology"],
    "keggEnrich": ["enrichment", "pathway"],
    "multiEfp": ["expression", "visualization"],
    "treeRooting": ["phylogeny", "rooting"],
    "onesteptree": ["phylogeny", "tree_building"],
    "notung": ["phylogeny", "reconciliation"],
    "newickRename": ["phylogeny", "tree_editing"],
})



KNOWN_ALIASES = {
    "treeRooting": "rooting",
    "TableCast": "tableCast",
    "gbar": "groupedbar",
    "gdensity": "genedensity",
    "getLongestCompleteORF": "longestorf",
    "one-step": "onesteptree",
    "genestructure": "structure",  # 旧名 → seq structure? 保留注释: genestructure 是独立命令
    # 显示别名(与 gen_metadata 特判一致, 评审 #56 两路径统一): draw→tree, one-step→onesteptree, rooting→treeRooting
    "tree": "draw",
    "onesteptree": "one-step",
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


# SpecRegistry(评审 #110 P1): 一次性构建缓存——Agent 高频链 search/describe/plan/validate/run
# 每次都重建 294 spec(~105ms)纯浪费; KNOWN_* 一旦变更调 _clear_specs_cache()
_SPECS_CACHE: dict | None = None


def build_command_specs(force: bool = False) -> dict[str, CommandSpec]:
    """构建统一命令模型(单一源, 兼容层: 不改变现运行行为)。

    force=True 强制重建(测试/热更新用); 否则命中 SpecRegistry 缓存(评审 #110 P1,
    294 spec 一次性构建, Agent 高频链不再重复重建)。

    来源:
      1. ENGINE_REGISTRY 表驱动(组 CATEGORY_MAP 归属)
      2. CLI_TOOLS 工具注册表
      3. 手动命令(经 cli_load 分组注册的 manual 命令, 从分组命令集补)
    """
    global _SPECS_CACHE
    if not force and _SPECS_CACHE is not None:
        return _SPECS_CACHE
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
                        runner="plot",  # 与 specs_from_scans 一致(评审 #56 两路径统一)
                        doc=v.get("help", ""),
                    )
    except Exception:
        pass

    # 别名/状态/schema 标注(统一模型增强; 在所有来源构建完成后)
    for name, spec in specs.items():
        spec.aliases = [a for a, target in KNOWN_ALIASES.items() if target == name]
        spec.alias_of = KNOWN_ALIASES.get(name, "")
        spec.status = KNOWN_STATUS.get(name, "stable")
        if name in KNOWN_SCHEMAS:
            ins, outs = KNOWN_SCHEMAS[name]
            spec.inputs, spec.outputs = ins, outs
            # output_slots 挂接(评审 #86 P1-5)
            if name in KNOWN_OUTPUT_SLOTS:
                spec.output_slots = KNOWN_OUTPUT_SLOTS[name]
            # content_type 挂接: slot 级优先,工具级兜底(评审 #80 P0-4)
            _slot_ct = KNOWN_INPUT_CONTENT_TYPES.get(name, {})
            for _inp in spec.inputs:
                if _inp.content_type == "generic":
                    _inp.content_type = _slot_ct.get(_inp.name) or KNOWN_CONTENT_TYPES.get(name, "generic")
        spec.capabilities = KNOWN_CAPABILITIES.get(name, []) or GROUP_CAPABILITIES.get(spec.group, [])
        spec.dependencies = KNOWN_DEPENDENCIES.get(name, [])
        spec.relations = KNOWN_RELATIONS.get(name, {}) or GROUP_RELATIONS.get(spec.group, {})
        spec.parameters = KNOWN_PARAMS.get(name, [])
    # Contract Loader: YAML 覆盖层(评审 #80;YAML 胜出)
    for _sp in specs.values():
        _apply_contract_overlay(_sp)
    _SPECS_CACHE = specs  # SpecRegistry 缓存(模块级写入; 调用方只读约定)
    return specs


def clear_specs_cache() -> None:
    """SpecRegistry 失效(评审 #110 P1): KNOWN_* / 注册表变更后强制下次重建。"""
    global _SPECS_CACHE
    _SPECS_CACHE = None


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
        s.alias_of = KNOWN_ALIASES.get(name, "")
        s.status = KNOWN_STATUS.get(name, "stable")
        if name in KNOWN_SCHEMAS:
            s.inputs, s.outputs = KNOWN_SCHEMAS[name]
        # output_slots 挂接(specs_from_scans 路径;评审 #88 P1-2)
        if name in KNOWN_OUTPUT_SLOTS:
            s.output_slots = KNOWN_OUTPUT_SLOTS[name]
        # content_type 挂接: slot 级优先,工具级兜底(评审 #80 P0-4)
        # ⚠️ 必须在 KNOWN_OUTPUT_SLOTS 之外(缩进 bug: 否则只 8 个工具有 content_type)
        _slot_ct = KNOWN_INPUT_CONTENT_TYPES.get(name, {})
        for _inp in s.inputs:
            if _inp.content_type == "generic":
                _inp.content_type = _slot_ct.get(_inp.name) or KNOWN_CONTENT_TYPES.get(name, "generic")
        s.capabilities = KNOWN_CAPABILITIES.get(name, []) or GROUP_CAPABILITIES.get(s.group, [])
        s.dependencies = KNOWN_DEPENDENCIES.get(name, [])
        s.relations = KNOWN_RELATIONS.get(name, {}) or GROUP_RELATIONS.get(s.group, {})
        s.parameters = KNOWN_PARAMS.get(name, [])
    return {n: to_metadata_entry(s) for n, s in specs.items()}


def to_metadata_entry(spec: CommandSpec) -> dict:
    """CommandSpec → metadata 条目(与现有 command_metadata.json 结构兼容)"""
    e: dict[str, object] = {"name": spec.name, "kind": spec.kind, "mode": spec.kind,
                            "class": spec.class_name, "xmx": spec.xmx, "runner": spec.runner,
                            "group": spec.group, "help": spec.doc}
    # P1-4(评审 #104 + #107 P1④ + #108 P1-4): semantic_fp 进入 metadata full 64 hex(Agent 搜索/规划可读;
    # execution 侧不进)——full 用于 identity 比较/cache/metadata 版本检查, short 仅展示
    # 从 identity.py 取(评审 #108: 解 command_spec↔workflow 双向依赖——workflow 拆出 identity 后单向依赖)
    try:
        from tbtools_cli.identity import semantic_fingerprint as _sfp
        _sfp_full = _sfp(spec)
        e["semantic_fingerprint"] = _sfp_full
        e["semantic_fingerprint_short"] = _sfp_full[:16]
    except Exception:
        pass
    if spec.alias_of:
        e["alias_of"] = spec.alias_of
    # 评审 #110 建议①: readiness 与 verification 两维正交注入 metadata——
    # Agent 直接可见"契约写得完整(FULL)" vs "真的跑过(EXECUTION/CONFORMANCE_VERIFIED)", 防混淆
    e["readiness"] = agent_readiness(spec)
    e["verification"] = verification_level(spec)
    if spec.capabilities:
        e["capabilities"] = spec.capabilities
        e["capabilities_ontology"] = expand_ontology(spec.capabilities)
    if spec.dependencies:
        e["dependencies"] = spec.dependencies
    if spec.name in KNOWN_DEPENDENCIES_STRUCT:
        e["dependency_manifest"] = KNOWN_DEPENDENCIES_STRUCT[spec.name]
    if spec.relations:
        e["relations"] = spec.relations
    if spec.parameters:
        e["parameters"] = [{"name": p.name, "type": p.type, "default": p.default,
                            "required": p.required, "note": p.note,
                            **({"cli_name": p.cli_name} if p.cli_name else {})} for p in spec.parameters]
    if spec.inputs:
        # 评审 #88 P1-1: content_type 必须导出(否则 metadata 丢语义,spec 升级降级不一致)
        e["inputs"] = [{"name": i.name, "role": i.role, "format": i.format,
                        "required": i.required, "note": i.note,
                        **({"columns": i.columns} if i.columns else {}),
                        **({"content_type": i.content_type} if i.content_type != "generic" else {})}
                       for i in spec.inputs]
    # outputs 从 output_slots 投影(评审 #96 P0: slots 为真相——specs_from_scans 无 overlay 也一致)
    _outs = [o.format for o in spec.output_slots if o.format] if spec.output_slots else spec.outputs
    if _outs:
        e["outputs"] = _outs
    # 评审 #88 P1-2: layout/named_flags/output_slots 导出(metadata 丢布局=第二轮 metadata bug)
    # output_slots 为空时从 outputs 派生(评审 #94 P0-1: 唯一 output truth 的一致性)
    _slots = spec.output_slots or [OutputSpec(name=o, format=o) for o in spec.outputs]
    if _slots:
        e["output_slots"] = [{"name": o.name, "format": o.format,
                              **({"content_type": o.content_type} if o.content_type != "generic" else {})}
                             for o in _slots]
    if spec.name in KNOWN_NAMED_FLAGS:
        e["named_flags"] = KNOWN_NAMED_FLAGS[spec.name]
    # YAML contract 布局投影(评审 #90 P1-2): contract loader 声明的布局也进 metadata
    if spec.__dict__.get("_contract_named_flags"):
        e["named_flags"] = spec.__dict__["_contract_named_flags"]
    if spec.__dict__.get("_contract_layout"):
        e["layout"] = spec.__dict__["_contract_layout"]
    if spec.status != "stable":
        e["status"] = spec.status
    if spec.aliases:
        e["aliases"] = spec.aliases
    return e


# ── Agent-ready 分级(评审 #60-8): FULL/PARTIAL/LEGACY 正式定义 ──
def agent_readiness(spec) -> str:
    """工具 Agent-ready 分级(评审 #66 P1-5 修正):
    FULL = inputs+outputs+capabilities 有标注 + status=stable(parameters 声明存在即可,
           无参数工具不扣分——区分"声明无参数"和"未定义参数")
    PARTIAL = 部分契约(capabilities 有但 schema 不全, 或 status 非 stable)
    LEGACY = 基础(仅注册;或无 capability 标注)
    """
    has_caps = bool(spec.capabilities)
    has_schema = bool(spec.inputs)
    has_outputs = bool(spec.outputs)
    # parameters 用"声明存在"判定(dataclass 字段总是存在;无参数工具声明空列表=合法)
    params_declared = True  # CommandSpec.parameters 总是声明(空=无可选参数, 仍算契约完整)
    if has_caps and has_schema and has_outputs and params_declared and spec.status == "stable":
        return "FULL"
    if has_caps or spec.status != "stable":
        return "PARTIAL"
    return "LEGACY"


def readiness_census() -> dict:
    """全量工具 Agent-ready 统计(readiness matrix 的数值口径)。"""
    out = {"FULL": 0, "PARTIAL": 0, "LEGACY": 0}
    for s in build_command_specs().values():
        out[agent_readiness(s)] += 1
    return out

def contract_coverage() -> dict:
    """契约覆盖三层(评审 #82 P1-7): declared(声明)/compileable(可编译)/verified(执行验证)。
    保留六维明细(向后兼容)。"""
    specs = build_command_specs()
    tiers = {"DECLARED": 0, "COMPILEABLE": 0, "EXECUTION_VERIFIED": 0, "CONFORMANCE_VERIFIED": 0}  # #110 建议①: 金链级
    for s in specs.values():
        tiers[verification_level(s)] += 1
    # 评审 #96 P1-3: COMPILE_VERIFIED(测试产物名单)单独统计——与 COMPILEABLE(声明可编译)区分
    _cv = sum(1 for s in specs.values() if s.name in _COMPILE_VERIFIED)
    tiers["COMPILE_VERIFIED"] = _cv
    return {
        "total": len(specs),
        "tiers": tiers,  # 三层(评审 #82)
        "input_contract": sum(1 for s in specs.values() if s.inputs),
        "output_contract": sum(1 for s in specs.values() if s.outputs),
        "parameter_contract": sum(1 for s in specs.values() if s.parameters),
        "invocation_contract": sum(1 for s in specs.values()
                                   if s.inputs or s.name in KNOWN_NAMED_FLAGS),
        "capability_contract": sum(1 for s in specs.values() if s.capabilities),
        "dependency_contract": sum(1 for s in specs.values() if s.dependencies),
    }

# ── Execution Verification 分级(评审 #80 P1-8 + #82 P1-6): 与 Agent-ready 正交 ──
def _load_verification_report() -> tuple[set, set, set]:
    """从测试产物读 verification 名单(评审 #82 P1-6 + #86 P1-6 + #90 P0-2:
    名单由测试生成;报告不存在时**不回退过时内置名单**——假的 EXECUTION_VERIFIED 比 DECLARED 更危险)。
    返回 (conformance_verified, execution_verified, compile_verified)。"""
    import json as _j
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(root, "tests", "verification_report.json")
    if os.path.isfile(p):
        try:
            d = _j.load(open(p, encoding="utf-8"))
            _exec = set(d.get("execution_verified", []))
            _conf = set(d.get("conformance_verified", []))
            # 评审 #110 P1: execution_verified 绑定 contract_fingerprint——
            # 入场合同变了(fp 不匹配)旧验证自动失效, 降级为未验证(防"contract 改但仍标已验")
            _details = d.get("execution_verified_details") or {}
            if _details:
                from tbtools_cli.identity import execution_contract_fingerprint as _fpfn
                try:
                    _specs_now = _bcs_for_verify()
                except Exception:
                    _specs_now = {}
                for _t in (list(_exec) + list(_conf)):
                    _entry = _details.get(_t) or {}
                    _old_fp = _entry.get("contract_fingerprint")
                    _sp = _specs_now.get(_t)
                    if _old_fp and _sp:
                        try:
                            if _fpfn(_sp) != _old_fp:
                                _exec.discard(_t)
                                _conf.discard(_t)  # 评审 #110 建议①: contract 变 → 连 conformance 一并失效
                        except Exception:
                            pass
                    elif not _old_fp:
                        _exec.discard(_t)
                        _conf.discard(_t)
            return _conf, _exec, set(d.get("compile_verified", []))
        except Exception:
            pass
    return set(), set(), set()


def _bcs_for_verify():
    """verification 加载时构建 spec(模块内直接调用, 避免自 import 循环)。"""
    return build_command_specs()


_CONFORMANCE_VERIFIED, _EXEC_VERIFIED, _COMPILE_VERIFIED = _load_verification_report()
CONFORMANCE_VERIFIED_TOOLS = _CONFORMANCE_VERIFIED
EXECUTION_VERIFIED_TOOLS = _EXEC_VERIFIED


def verification_level(spec) -> str:
    """执行验证分级(评审 #80 + #110 建议① 再分层):
    CONFORMANCE_VERIFIED = 金链 conformance 全断言通过(Tier2+; 评审 #110: 真跑+expected argv+产物语义+provenance)
    EXECUTION_VERIFIED = 真实执行通过(Tier2; 产物非空+sha256 完整)
    COMPILEABLE = InvocationSpec 可编译(有 inputs 契约)
    DECLARED = 仅注册声明
    """
    if spec.name in CONFORMANCE_VERIFIED_TOOLS:
        return "CONFORMANCE_VERIFIED"
    if spec.name in EXECUTION_VERIFIED_TOOLS:
        return "EXECUTION_VERIFIED"
    if spec.name in _COMPILE_VERIFIED:
        return "COMPILEABLE"  # 评审 #86: 测试产物名单优先
    if spec.inputs or spec.name in KNOWN_NAMED_FLAGS:
        return "COMPILEABLE"  # 无报告时回退: 有 inputs 契约(COMPILEABLE 属声明级,非假验证)
    return "DECLARED"


def verification_census() -> dict:
    """评审 #98 P1-3: COMPILE_VERIFIED(测试产物名单)入 census——
    与 COMPILEABLE(声明可编译)区分,API 统一(不再只在 coverage 里有)。"""
    out = {"CONFORMANCE_VERIFIED": 0, "EXECUTION_VERIFIED": 0,
           "COMPILEABLE": 0, "DECLARED": 0, "COMPILE_VERIFIED": 0}
    for s in build_command_specs().values():
        out[verification_level(s)] += 1
    for s in build_command_specs().values():
        if s.name in _COMPILE_VERIFIED:
            out["COMPILE_VERIFIED"] += 1
    return out
