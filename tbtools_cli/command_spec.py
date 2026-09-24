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


# 核心命令输入输出 schema 样例(证明模型模式; 全量标注为二期)
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
    "sixframe": ([InputSpec("pep", format="fasta", note="蛋白(输出核酸)")], ["fa"]),
    "longestorf": ([InputSpec("seq", format="fasta", note="核酸输入")], ["fa"]),
    "seqlogo": ([InputSpec("seqs", format="fasta")], ["svg"]),
    "stat-fasta": ([InputSpec("fasta", format="fasta")], ["xls"]),
    # 三期批次(schema 标注继续)
    "venn3": ([InputSpec("list1", format="txt"), InputSpec("list2", format="txt"),
               InputSpec("list3", format="txt")], ["svg"]),
    "venn4": ([InputSpec("list1", format="txt"), InputSpec("list2", format="txt"),
               InputSpec("list3", format="txt"), InputSpec("list4", format="txt")], ["svg"]),
    "upset": ([InputSpec("sets", format="txt", note="多个集合文件, 末参为输出")], ["svg"]),
    "tpmCalc": ([InputSpec("counts", format="tsv", note="counts 表"), InputSpec("lenInfo", format="tsv", columns=["GeneID", "Length"])], ["tsv"]),
    "gxfSplit": ([InputSpec("gff", format="gff3")], ["tsv"]),
    "gxfAttr": ([InputSpec("gff", format="gff3")], ["tsv"]),
    "gxfIdAppender": ([InputSpec("gff", format="gff3")], ["gff3"]),
    "recipBlast": ([InputSpec("db", format="fasta"), InputSpec("query", format="fasta")], ["tsv"]),
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
    "hmmsearch": [{"name": "hmmer", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "simplehmmscan": [{"name": "hmmer", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "calcRepeat": [{"name": "jellyfish", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "rnaplot": [{"name": "rnafold", "type": "binary", "required": True, "platforms": ["linux"]}],
    "plotrna": [{"name": "rnafold", "type": "binary", "required": True, "platforms": ["linux"]}],
    "kallisto": [{"name": "kallisto", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "diamond": [{"name": "diamond", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "mcscanxd": [{"name": "mcscanx", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "blastp": [{"name": "blast+", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "blastn": [{"name": "blast+", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "muscle": [{"name": "muscle", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "mafft": [{"name": "mafft", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "iqtree": [{"name": "iqtree2", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "onesteptree": [{"name": "iqtree2", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "trimal": [{"name": "trimal", "type": "binary", "required": True, "platforms": ["linux", "macos"]}],
    "taxparse": [{"name": "internet", "type": "capability", "required": True, "platforms": ["linux", "macos", "windows"]}],
    "sraxml2tab": [{"name": "internet", "type": "capability", "required": False, "platforms": ["linux", "macos", "windows"]}],
}


# 兼容层(评审 #52 P1-3 合并): 简单 list 由 STRUCT 派生, 单一事实源
KNOWN_DEPENDENCIES: dict = {cmd: [str(d["name"]) for d in deps] for cmd, deps in KNOWN_DEPENDENCIES_STRUCT.items()}


# 能力 ontology(评审 #52 P1-7): 分层标签 domain.subdomain
# 平标签 → 分层父链(Agent 可用 "phylogeny.tree-building" 或 "phylogeny" 查询)
ONTOLOGY = {
    "alignment": "sequence.alignment",
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
    "recipBlast": ["homology", "reciprocal_best_hit"],
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
    "treeRooting": "rooting",
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
        spec.capabilities = KNOWN_CAPABILITIES.get(name, []) or GROUP_CAPABILITIES.get(spec.group, [])
        spec.dependencies = KNOWN_DEPENDENCIES.get(name, [])
        spec.relations = KNOWN_RELATIONS.get(name, {}) or GROUP_RELATIONS.get(spec.group, {})
        spec.parameters = KNOWN_PARAMS.get(name, [])
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
        s.alias_of = KNOWN_ALIASES.get(name, "")
        s.status = KNOWN_STATUS.get(name, "stable")
        if name in KNOWN_SCHEMAS:
            s.inputs, s.outputs = KNOWN_SCHEMAS[name]
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
    if spec.alias_of:
        e["alias_of"] = spec.alias_of
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
        e["inputs"] = [{"name": i.name, "role": i.role, "format": i.format,
                        "required": i.required, "note": i.note,
                        **({"columns": i.columns} if i.columns else {})} for i in spec.inputs]
    if spec.outputs:
        e["outputs"] = spec.outputs
    if spec.status != "stable":
        e["status"] = spec.status
    if spec.aliases:
        e["aliases"] = spec.aliases
    return e

# ── Agent-ready 分级(评审 #60-8): FULL/PARTIAL/LEGACY 正式定义 ──
def agent_readiness(spec) -> str:
    """工具 Agent-ready 分级:
    FULL = 契约完整(inputs+outputs+parameters+capabilities 均有标注, 且 status=stable)
    PARTIAL = 部分契约(capabilities 有但 schema 不全, 或 status 非 stable)
    LEGACY = 基础(仅注册;或无 capability 标注)
    """
    has_caps = bool(spec.capabilities)
    has_schema = bool(spec.inputs)
    has_params = bool(spec.parameters)
    if has_caps and has_schema and has_params and spec.status == "stable":
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

