"""tbtools new 交互式向导 — 场景映射表
把用户「我想做什么」（中文场景）映射到具体命令 + 参数收集提示。
"""
from .core import get_pitfall_hint

# 场景表: 键 = 中文场景名, 值 = [分组, 命令名, 一句话说明, 参数收集器描述]
# 参数收集器: 每个元素 = (参数位置标签, 默认值或None, 可选标志help)
def _scen(name, group, cmd, desc, args):
    return {
        "scenario": name, "group": group, "cmd": cmd,
        "desc": desc, "args": args, "usage": _usage(group, cmd),
    }

def _usage(group, cmd):
    import tbtools_cli.auto_commands as _ac
    impl = getattr(_ac, f'_{cmd}_impl', None)
    if impl and (impl.__doc__ or ''):
        d = impl.__doc__.strip()
        if ':' in d:
            return d.split(':', 1)[1].strip()
    # 从已注册命令找
    from .cli import _groups
    g = _groups.get(group)
    if g and cmd in g.commands:
        h = g.commands[cmd].help or ''
        return h.split('\n')[0][:80]
    return f"{group} {cmd}"

# 常用场景（覆盖 80% 使用）——按用户「想做什么」组织
SCENARIOS = {
    # ---- 序列 ----
    "多序列比对可视化（MSA）": _scen("多序列比对可视化（MSA）", "seq", "msa",
        "把比对好的多序列（如蛋白/CDS）画成可视化图", [("输入比对文件 .fa", None)]),
    "蛋白序列 Logo（conserved motif）": _scen("蛋白序列 Logo", "seq", "logo",
        "把多序列比对的保守位点画成序列 Logo", [("输入比对文件 .fa", None), ("输出 Logo 图片", "logo.svg")]),
    "Motif 分布图（MEME 结果）": _scen("Motif 分布图", "seq", "motif",
        "把 MEME 发现的 motif 沿基因画分布图", [("MEME xml", None), ("输出图", "motif.svg")]),
    "基因结构图（外显子/UTR）": _scen("基因结构图", "seq", "structure",
        "从 GFF 画基因外显子/内含子/U TR 结构图", [("GFF 文件", None), ("输出图", "structure.svg")]),
    "序列统计（长度/GC/组成）": _scen("序列统计", "tool", "stat-fasta",
        "统计 FASTA 每条序列长度/GC 含量/组成", [("FASTA 文件", None), ("输出表", "stat.xls")]),

    # ---- 表达 ----
    "火山图（差异表达）": _scen("火山图", "expr", "volcano",
        "差异表达分析结果画火山图（log2FC vs -log10P）", [("DEG 表", None), ("输出图", "volcano.svg")]),
    "热图（表达矩阵）": _scen("热图", "expr", "heatmap",
        "基因×样本表达矩阵画热图（支持聚类）", [("表达矩阵 .tsv", None), ("输出图", "heatmap.svg")]),
    "PCA 聚类（样本分群）": _scen("PCA 聚类", "expr", "pca",
        "表达矩阵样本 PCA 降维分群", [("表达矩阵 .tsv", None), ("输出图", "pca.svg")]),
    "层次聚类树（距离矩阵）": _scen("层次聚类树", "expr", "hclust",
        "三列距离矩阵（GeneA GeneB dist）画聚类树", [("距离文件 GeneA GeneB dist", None), ("输出图", "hclust.svg")]),
    "差异表达双直方图": _scen("差异表达双直方图", "expr", "dehist",
        "上下调基因数画左右直方图", [("任意 ID\\t值 文件", None), ("输出图", "dehist.svg")]),

    # ---- 树 ----
    "系统发育树（ML 一步法）": _scen("系统发育树", "tree", "onesteptree",
        "蛋白序列快速建 ML 树（muscle→trimal→IQ-TREE）", [("蛋白多序列 .fa", None), ("输出前缀", "tree")]),
    "可视化已有树（Newick）": _scen("可视化树", "tree", "tree",
        "画 Newick 树的图", [("Newick 树文件", None), ("输出图", "tree.svg")]),
    "无根树可视化": _scen("无根树", "tree", "unrooted",
        "把树画成无根（放射状）风格", [("Newick 树文件", None), ("输出图", "unrooted.svg")]),

    # ---- 共线性/基因组 ----
    "共线性 Dot-plot": _scen("共线性 Dot-plot", "syn", "dotplot",
        "两基因组共线性点图", [("简化 GFF 1", None), ("简化 GFF 2", None), ("blast 结果", None), ("输出图", "dotplot.svg")]),
    "MCScanX 共线性分析": _scen("MCScanX 共线性", "syn", "mcscanx",
        "跑 MCScanX 找共线性区块", [("简化 GFF", None), ("blast 结果", None)]),
    "环形共线性图（Circos）": _scen("环形共线性图", "syn", "circos",
        "多染色体环形共线性图", [("chromLen", None), ("link 文件", None), ("genePos", None), ("输出图", "circos.svg")]),
    "染色体基因定位图": _scen("染色体定位图", "tool", "genelocation",
        "基因在染色体上的位置分布图", [("chromLen 文件", None), ("FeaturePos", None), ("输出图", "geneloc.svg")]),
    "基因密度分布（染色体）": _scen("基因密度", "tool", "genedensity",
        "染色体基因密度分布统计", [("GFF3", None), ("输出表", "density.tsv")]),

    # ---- 集合 ----
    "Venn 图（2-6 集合交集）": _scen("Venn 图", "sets", "venn",
        "多个基因集合交集 Venn 图（2/3/4/5/6 集）", [("集合数目 2-6", "3"), ("集合文件前缀", None), ("输出图", "venn.svg")]),
    "UpSet 图（交集可视化）": _scen("UpSet 图", "sets", "upset",
        "多个集合交集用 UpSet 图展示", [("集合文件", None), ("输出图", "upset.svg")]),

    # ---- 表操作 ----
    "表格行列转换/合并/拆分": _scen("表格操作", "table", "tableMerge",
        "表格合并/转置/筛选等（见 list tools）", []),
}

_categories = {
    "序列/结构": ["多序列比对可视化（MSA）", "蛋白序列 Logo（conserved motif）", "Motif 分布图（MEME 结果）", "基因结构图（外显子/UTR）", "序列统计（长度/GC/组成）"],
    "表达/统计": ["火山图（差异表达）", "热图（表达矩阵）", "PCA 聚类（样本分群）", "层次聚类树（距离矩阵）", "差异表达双直方图"],
    "系统发育": ["系统发育树（ML 一步法）", "可视化已有树（Newick）", "无根树可视化"],
    "共线性/基因组": ["共线性 Dot-plot", "MCScanX 共线性分析", "环形共线性图（Circos）", "染色体基因定位图", "基因密度分布（染色体）"],
    "集合分析": ["Venn 图（2-6 集合交集）", "UpSet 图（交集可视化）"],
    "表格处理": ["表格行列转换/合并/拆分"],
}
