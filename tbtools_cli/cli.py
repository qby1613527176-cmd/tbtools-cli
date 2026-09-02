"""tbtools-cli 主入口 — Python click 重构版"""
import click
import os, sys, subprocess

# ---- 配置 ----
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tbtools_cli.core import JAR, run_java, run_plot, ensure_bridge, resolve_output, ROOT

# ---- 通用选项 ----
def common_options(f):
    """通用选项装饰器：--verbose, --quiet, --format, --width, --height"""
    f = click.option("--verbose", "-V", is_flag=True, default=False, help="显示完整堆栈（debug 模式）")(f)
    f = click.option("--quiet", "-q", is_flag=True, default=False, help="静默模式（只显示错误）")(f)
    f = click.option("--format", "-f", "fmt", default=None, help="输出格式: svg|png|pdf")(f)
    f = click.option("--height", "-H", type=int, default=None, help="画布高度")(f)
    f = click.option("--width", "-W", type=int, default=None, help="画布宽度")(f)
    f = click.option("--threads", "-t", type=int, default=None, help="线程数")(f)
    return f

# ---- 主命令组 ----
@click.group(invoke_without_command=True)
@click.version_option("1.0.0", prog_name="tbtools-cli")
@click.pass_context
def cli(ctx):
    """TBtools-II 全功能 CLI — 140 绘图命令 + 82 工具 + 188 RPC"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

# ---- 命令组：序列/结构 ----
@cli.group("seq")
def seq_group():
    """序列/结构域命令"""
    pass

@seq_group.command("logo")
@click.argument("input_file")
@click.argument("output_file")
@click.option("--scale-ic/--no-scale-ic", default=True, help="按信息含量缩放")
@click.option("--show-pos/--no-show-pos", default=False, help="显示位置编号")
@common_options
def seqlogo(input_file, output_file, scale_ic, show_pos, verbose, quiet, fmt, height, width, threads):
    """序列 LOGO 图"""
    output_file = resolve_output(output_file, fmt)
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioDoer.seqLogo.makeSeqLogo",
            "--inFile", input_file, "--OutGraph", output_file]
    if not scale_ic:
        args += ["--scaleIC=false"]
    if show_pos:
        args += ["--showPos=true"]
    ec = run_plot(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

@seq_group.command("msa")
@click.argument("aligned_fasta")
@click.argument("output_file")
@click.option("--padding", type=int, default=0, help="序列间填充")
@common_options
def seq_msa(aligned_fasta, output_file, padding, verbose, quiet, fmt, height, width, threads):
    """多序列比对可视化"""
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("MSACli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "MSACli", aligned_fasta, output_file]
    if padding:
        args += ["--padding", str(padding)]
    ec = run_plot(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

@seq_group.command("structure")
@click.argument("gff_file")
@click.argument("id_list")
@click.argument("output_file")
@click.option("--genome", "-g", default=None, help="基因组 FASTA（可选）")
@common_options
def seq_structure(gff_file, id_list, output_file, genome, verbose, quiet, fmt, height, width, threads):
    """基因结构图（外显子/UTR 从 GFF）"""
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("GeneStructureCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "GeneStructureCli", gff_file, id_list, output_file]
    if genome:
        args += [genome]
    if width: args += [str(width)]
    if height: args += [str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

@seq_group.command("motif")
@click.argument("meme_xml")
@click.argument("id_list")
@click.argument("output_file")
@common_options
def seq_motif(meme_xml, id_list, output_file, verbose, quiet, fmt, height, width, threads):
    """Motif 分布图（MEME XML）"""
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("MotifCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "MotifCli", meme_xml, id_list, output_file]
    if width: args += [str(width)]
    if height: args += [str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

# ---- 命令组：表达/统计 ----
@cli.group("expr")
def expr_group():
    """表达/统计命令"""
    pass

@expr_group.command("volcano")
@click.argument("deg_file")
@click.argument("output_file")
@click.option("--pval-cutoff", "-p", type=float, default=0.05, help="P值阈值")
@click.option("--fc-cutoff", "-c", type=float, default=1.0, help="Log2FC 阈值")
@common_options
def volcano(deg_file, output_file, pval_cutoff, fc_cutoff, verbose, quiet, fmt, height, width, threads):
    """火山图（DEG: GeneID Log2FC pvalue）"""
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("GenericCli")
    args = ["java", "-Xmx2g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "GenericCli", "biocjava.bioDoer.JIGplotToolkit.VocanoPlot.vocanoPlot", "show",
            output_file, "--set", "inData", deg_file]
    args += ["--set", "log2FoldChange", "true", "--set", "negLogPvalue", "true"]
    args += ["--set", "pvalueCutOff", str(pval_cutoff), "--set", "foldChangeCutOff", str(fc_cutoff)]
    args += ["--set", "normPointSize", "5.0", "--set", "showTopChangeNum", "5"]
    if width:
        args += ["--width", str(width)]
    if height:
        args += ["--height", str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

@expr_group.command("heatmap")
@click.argument("matrix_file")
@click.argument("output_file")
@click.option("--log2/--no-log2", default=False, help="log2 转换")
@click.option("--row-scale/--no-row-scale", default=False, help="行标准化")
@click.option("--cluster-row/--no-cluster-row", default=False, help="行聚类")
@click.option("--cluster-col/--no-cluster-col", default=False, help="列聚类")
@common_options
def heatmap(matrix_file, output_file, log2, row_scale, cluster_row, cluster_col, verbose, quiet, fmt, height, width, threads):
    """热图（表达矩阵）"""
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("HeatmapCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "HeatmapCli", matrix_file, output_file]
    if log2:
        args += ["--log2"]
    if row_scale:
        args += ["--rowScale"]
    if cluster_row:
        args += ["--clusterRow"]
    if cluster_col:
        args += ["--clusterCol"]
    if width:
        args += ["--width", str(width)]
    if height:
        args += ["--height", str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

@expr_group.command("pca")
@click.argument("matrix_file")
@click.argument("output_file")
@click.argument("direction", type=click.Choice(["row", "col"]), default="row")
@click.option("--scale/--no-scale", default=False, help="标准化")
@common_options
def expr_pca(matrix_file, output_file, direction, scale, verbose, quiet, fmt, height, width, threads):
    """PCA 图"""
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("GenericCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "GenericCli", "biocjava.bioDoer.JIGplotToolkit.PCAanalysis.PCAanalysis",
            "doPCA+postGraph", output_file,
            "--set", "inTabFile", matrix_file,
            "--set", "rowName", "true", "--set", "colName", "true",
            "--set", "processDirect", direction]
    if scale: args += ["--set", "scale", "true"]
    args += ["--set", "pointSize", "8.0", "--set", "showLabel", "true"]
    if width: args += ["--width", str(width)]
    if height: args += ["--height", str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

@expr_group.command("hclust")
@click.argument("distance_file")
@click.argument("output_file")
@common_options
def expr_hclust(distance_file, output_file, verbose, quiet, fmt, height, width, threads):
    """层次聚类树（三列距离文件 GeneA\tGeneB\tdist）"""
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("HclustCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "HclustCli", distance_file, output_file]
    ec = run_plot(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

@expr_group.command("dehist")
@click.argument("deg_file")
@click.argument("output_file")
@common_options
def expr_dehist(deg_file, output_file, verbose, quiet, fmt, height, width, threads):
    """差异表达双直方图"""
    output_file = resolve_output(output_file, fmt)
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioDoer.JIGplotToolkit.DiffExp.DualHistPlot.DiffExpDualHistPlot",
            deg_file, output_file]
    if width: args += [str(width)]
    if height: args += [str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

# ---- 命令组：树/进化 ----
@cli.group("tree")
def tree_group():
    """树/进化命令"""
    pass

@tree_group.command("draw")
@click.argument("config_file")
@click.argument("output_file")
@common_options
def tree_draw(config_file, output_file, verbose, quiet, fmt, height, width, threads):
    """树+注释图（TreeTreeTree 多轨道）"""
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("TreeCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "TreeCli", config_file, output_file]
    ec = run_plot(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

@tree_group.command("unrooted")
@click.argument("newick_file")
@click.argument("output_file")
@common_options
def tree_unrooted(newick_file, output_file, verbose, quiet, fmt, height, width, threads):
    """无根树可视化"""
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("UnrootedTreeCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "UnrootedTreeCli", newick_file, output_file]
    if width: args += ["--width", str(width)]
    if height: args += ["--height", str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

@tree_group.command("rooting")
@click.argument("input_nwk")
@click.argument("output_nwk")
@common_options
def tree_rooting(input_nwk, output_nwk, verbose, quiet, fmt, height, width, threads):
    """MAD 系统发育定根"""
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioDoer.JIGplotToolkit.newickParser.TreeTreeTree.TreeRootingByMAD",
            input_nwk, output_nwk]
    ec = run_java(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

@tree_group.command("one-step")
@click.argument("pep_fasta")
@click.argument("output_prefix")
@click.option("--bb-time", "-b", type=int, default=1000, help="IQ-TREE bootstrap iterations")
@common_options
def tree_onesteptree(pep_fasta, output_prefix, bb_time, verbose, quiet, fmt, height, width, threads):
    """一步法 ML 树（muscle → trimal → IQ-TREE）"""
    t = threads or 4
    args = ["java", "-Xmx4g", "-cp", JAR,
            "biocjava.bioDoer.JIGplotToolkit.Phylogenetics.OneStepTree",
            "--inPepFie", pep_fasta, "--outFilePrefix", output_prefix,
            "--bbTime", str(bb_time), "--threads", str(t)]
    ec = run_java(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

# ---- 命令组：工具 ----
@cli.group("tool")
def tool_group():
    """命令行工具（82 个）"""
    pass

@tool_group.command("stat-fasta")
@click.argument("input_file")
@click.argument("output_file")
@common_options
def tool_stat_fasta(input_file, output_file, verbose, quiet, fmt, height, width, threads):
    """FASTA 序列统计"""
    # stdin 管道支持
    if input_file == "-":
        import tempfile
        tmp = tempfile.mktemp(suffix=".fa")
        with open(tmp, "wb") as f:
            f.write(sys.stdin.buffer.read())
        input_file = tmp
    if output_file == "-":
        output_file = "/dev/stdout"
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioIO.FastX.FastaIndex.QuickStatFasta",
            "--inFasta", input_file, "--outPutFile", output_file]
    ec = run_java(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

@tool_group.command("cds2protein")
@click.argument("cds_fasta")
@click.argument("output_file")
@common_options
def tool_cds2protein(cds_fasta, output_file, verbose, quiet, fmt, height, width, threads):
    """CDS → 蛋白质翻译"""
    if output_file == "-": output_file = "/dev/stdout"
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioDoer.JIGplotToolkit.Protein.CdsToProtein",
            cds_fasta, output_file]
    ec = run_java(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

@tool_group.command("fasta-extract")
@click.argument("input_fasta")
@click.argument("id_list")
@click.argument("output_file")
@common_options
def tool_fasta_extract(input_fasta, id_list, output_file, verbose, quiet, fmt, height, width, threads):
    """按 ID 列表提取 FASTA 序列"""
    if input_fasta == "-":
        import tempfile; tmp = tempfile.mktemp(suffix=".fa")
        with open(tmp, "wb") as f: f.write(sys.stdin.buffer.read())
        input_fasta = tmp
    if output_file == "-": output_file = "/dev/stdout"
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioIO.FastX.FastaIndex.ExtractFasta",
            input_fasta, id_list, output_file]
    ec = run_java(args, verbose=verbose, quiet=quiet)
    sys.exit(ec)

# ---- 通用命令 ----
@cli.command()
def version():
    """显示版本信息"""
    click.echo(f"tbtools-cli v1.0.0")
    click.echo(f"  140 绘图命令 + 82 CLI 工具 + 188 RPC 方法")
    click.echo(f"  bridges: 80 | engines: 123 | 坑位: 35")
    r = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=5)
    java_ver = r.stderr.splitlines()[0] if r.stderr else "unknown"
    click.echo(f"  Java: {java_ver}")
    click.echo(f"  JAR: {JAR}" if JAR else "  JAR: ⚠️ 未配置")

@cli.command()
def doctor():
    """环境诊断"""
    import shutil
    ok = warn = err = 0
    checks = [
        ("java", "Java", True),
        ("javac", "javac", False),
        ("xvfb-run", "xvfb-run（绘图必需）", True),
    ]
    for cmd_name, desc, required in checks:
        if shutil.which(cmd_name):
            click.echo(f"  ✅ {desc}: 可用")
            ok += 1
        elif required:
            click.echo(f"  ❌ {desc}: 未安装")
            err += 1
        else:
            click.echo(f"  ⚠️ {desc}: 未安装")
            warn += 1
    if JAR and os.path.isfile(JAR):
        size_mb = os.path.getsize(JAR) / 1024 / 1024
        click.echo(f"  ✅ JAR: {JAR} ({size_mb:.0f}MB)")
        ok += 1
    else:
        click.echo("  ❌ JAR: 未找到")
        err += 1
    optional = {"samtools": "SAM/BAM", "blastp": "BLAST", "muscle": "MSA",
                "iqtree2": "建树", "meme": "Motif", "RNAfold": "RNA"}
    avail = [f"{d}({v})" for d, v in optional.items() if shutil.which(d)]
    if avail:
        click.echo(f"  ✅ 可选依赖: {', '.join(avail[:5])}")
        ok += 1
    click.echo(f"\n  汇总: ✅ {ok}  ⚠️ {warn}  ❌ {err}")
    if err:
        sys.exit(1)

@cli.command()
@click.argument("command", required=False)
def examples(command):
    """显示命令示例"""
    EX = {
        "seqlogo": ("序列 LOGO", "tbtools seq logo examples/data/phylogeny/msa.fa logo.svg"),
        "volcano": ("火山图", "tbtools expr volcano examples/data/deg.txt volcano.svg"),
        "heatmap": ("热图", "tbtools expr heatmap examples/data/expr/expr.tsv heatmap.svg --log2 --cluster-row"),
        "tree": ("系统发育树", "tbtools tree draw test_reports/data_b5/tree.config tree.svg"),
        "stat-fasta": ("FASTA 统计", "tbtools tool stat-fasta examples/data/rpc/gras6_pep.fa stat.xls"),
    }
    if command and command in EX:
        click.echo(f"\n{command} 示例:")
        click.echo(f"  {EX[command][0]}:")
        click.echo(f"    {EX[command][1]}")
    elif command:
        click.echo(f"暂无 {command} 的示例。查看帮助: tbtools {command} --help")
    else:
        click.echo("tbtools-cli 命令示例")
        for name, (desc, cmd) in EX.items():
            click.echo(f"  {name}: {desc}")
            click.echo(f"    {cmd}")
        click.echo("\n用法: tbtools examples <命令>")

# ---- 动态加载剩余命令 ----
# ---- 命令分类映射 ----
CATEGORY_MAP = {
    # 序列/结构/域
    "genestructure": "seq", "motif": "seq", "msa": "seq", "seqlentrack": "seq",
    "amazingmeta": "seq", "cddmotif": "seq", "pfammotif": "seq", "memerun": "seq",
    "mastrun": "seq", "mastExtract": "seq", "mast2tab": "seq", "pep2codon": "seq",
    "simplehmmscan": "seq", "gel": "seq", "gfa": "seq", "gfa2fa": "seq",
    # 表达/统计
    "pca": "expr", "hclust": "expr", "qpcr": "expr", "qpcrExp": "expr",
    "groupedbar": "expr", "dehist": "expr", "barplot": "expr", "barplotter": "expr",
    "layoutheatmap": "expr", "cubeheatmap": "expr", "violin": "expr",
    "colorscheme": "expr", "distance": "expr", "mountain": "expr",
    "tauIndex": "expr", "exprCorr": "expr", "groupCol": "expr",
    # 树/进化
    "phylotree": "tree", "unrooted": "tree", "treeRooting": "tree",
    "onesteptree": "tree", "degramdom": "tree", "findpath": "tree",
    "nwAlign": "tree",
    # 共线性/基因组
    "circos": "syn", "supercircos": "syn", "circlegene": "syn", "dotplot": "syn",
    "microsyn": "syn", "msy": "syn", "multisyn": "syn", "dualsyn": "syn",
    "pafviz": "syn", "pafcomp": "syn", "pafref": "syn",
    "mcscanx": "syn", "collinearRegion": "syn",
    "findblockdual": "syn", "findblockmultiple": "syn", "visualizeblock": "syn",
    "conflictpaf": "syn", "partitionconflict": "syn",
    "microgenome": "syn",
    # 集合/ChIP
    "venn5": "sets", "venn6": "sets", "upset": "sets",
    "peaktss": "chipseq", "peakdist": "chipseq", "peakanno": "chipseq",
    "pileup": "chipseq",
    # 组装/注释
    "ctgGroup": "asm", "homoPhase": "asm", "sepChr": "asm",
    "bamMerge": "asm", "bamindex": "asm", "bamsort": "asm", "bamstate": "asm",
    "hicEnzyme": "asm", "virusRecomb": "asm", "preparespecies": "asm",
    "gxfRename": "gxf", "gxfStat": "gxf", "gxfAppend": "gxf", "gxfGenepos": "gxf",
    "gxfRegion": "gxf", "gxfFix": "gxf", "gxfOverlap": "gxf", "gxfRepIDs": "gxf",
    "gxfRepGXF": "gxf", "gxfMatch": "gxf", "gxfRecall": "gxf",
    "regionAnno": "gxf", "annocompare": "gxf", "genedensity": "gxf",
    "genelocation": "gxf", "genelocgff": "gxf", "gxfSort": "gxf",
    # miRNA
    "mirnatarget": "mirna", "mirnaTarget2": "mirna", "mirnaIdentify": "mirna",
    # GO/表格
    "levelGo": "table", "goParse": "table", "batchReplace": "table",
    "tableCollapse": "table", "tableColSelect": "table", "tableAppend": "table",
    "tableMelt": "table", "tableColSel": "table", "tableCast": "table",
    "tableUniq": "table", "tableTranspose": "table", "tableSplit": "table",
    "tableMerge": "table",
    # BLAST/比对
    "recipBlast": "blast", "filterCScore": "blast", "quickFamily": "blast",
    "twoSeqBlast": "blast",
    # FASTQ
    "fqTrim": "fastq", "fqfaConv": "fastq", "fastaSubseq": "fastq",
    "fastaExtract": "fastq",
    # HMM
    "hmmExtract": "hmm",
    # GWAS
    "mimicVqsr": "gwas",
    # 通用
    "generic": "engine", "efpHeat": "expr", "multiEfp": "expr",
    "plotrna": "seq", "rnaplot": "seq",
}

# 分组定义
GROUPS = {
    "seq": "序列/结构/域",
    "expr": "表达/统计",
    "tree": "树/进化",
    "syn": "共线性/基因组",
    "sets": "集合/韦恩",
    "chipseq": "ChIP-seq",
    "asm": "组装/注释",
    "gxf": "GXF/表格",
    "mirna": "miRNA",
    "table": "GO/表格",
    "blast": "BLAST/比对",
    "fastq": "FASTQ/FASTA",
    "hmm": "HMM",
    "gwas": "GWAS",
    "engine": "通用",
}

# 获取已注册的 group 对象（与装饰器创建的是同一个）
_groups = {}
for key, desc in GROUPS.items():
    if key in cli.commands:
        _groups[key] = cli.commands[key]  # 复用装饰器创建的 group
    else:
        # 不存在则创建
        g = click.Group(name=key, help=desc)
        cli.add_command(g, name=key)
        _groups[key] = g

def _load_dynamic_commands():
    """从 tbplot.sh 动态生成 click 命令，按分类注册到 group"""
    import re
    tbplot_sh = os.path.join(ROOT, "bin", "tbplot.sh")
    if not os.path.isfile(tbplot_sh):
        return
    with open(tbplot_sh) as f:
        content = f.read()
    cmds = set(re.findall(r'^  ([a-zA-Z][a-zA-Z0-9]+)\)$', content, re.M))
    # 已迁移命令的原始名（不动态转发）——用 tbplot.sh 里的原始命令名
    registered = {"seqlogo", "msa", "motif", "genestructure",  # seq
                  "volcano", "heatmap2", "pca", "hclust", "dehist",  # expr
                  "tree", "unrooted", "treeRooting", "onesteptree",  # tree
                  "circos", "dotplot", "pafviz",  # syn
                  "upset",  # sets
                  "peaktss", "peakdist",  # chipseq
                  "version", "doctor", "examples", "seq", "expr", "tree", "tool",
                  "chipseq", "sets", "syn", "asm", "gxf", "mirna", "table",
                  "blast", "fastq", "hmm", "gwas", "engine"}
    for cmd_name in sorted(cmds - registered):
        cat = CATEGORY_MAP.get(cmd_name, "engine")
        _make_passthrough(cmd_name, _groups[cat])

def _make_passthrough(name, group=None):
    """生成一个转发到 tbplot.sh 的命令"""
    _target = group or cli
    @_target.command(name=name, context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
    @click.pass_context
    def _cmd(ctx, **kw):
        args = ["bash", os.path.join(ROOT, "bin", "tbplot.sh"), name] + ctx.args
        ec = subprocess.run(args).returncode
        sys.exit(ec)
    _cmd.__doc__ = f"转发到 tbplot.sh {name}"

_load_dynamic_commands()

if __name__ == "__main__":
    cli()
