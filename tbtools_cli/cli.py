"""tbtools-cli 主入口 — Python click 重构版"""
import os
import sys

import click

# ---- 配置 ----
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tbtools_cli.auto_commands as _ac
from tbtools_cli.cli_tools_registry import CLI_TOOLS
from tbtools_cli.core import (
    JAR,
    ROOT,
    cp,
    ensure_bridge,
    get_pitfall_hint,
    pre_flight,
    resolve_output,
    run_java,
    run_plot,
    stdout_path,
)
from tbtools_cli.presets import apply_preset
from tbtools_cli.cli_rpc import build_rpc_group
import tbtools_cli.cli_load as cli_load
from tbtools_cli.cli_top import register_top  # 批次 B: 顶层命令拆分
from tbtools_cli.cli_load import (  # 批次 B: 动态注册拆分
    CATEGORY_MAP,
    _groups,
    _load_auto_commands,
    _load_dynamic_commands,
    build_and_load,
)



# ---- 通用选项 ----
def common_options(f):
    """通用选项装饰器：--verbose, --quiet, --format, --preset, --width, --height, --threads"""
    f = click.option("--verbose", "-V", is_flag=True, default=False, help="显示完整堆栈（debug 模式）")(f)
    f = click.option("--quiet", "-q", is_flag=True, default=False, help="静默模式（只显示错误）")(f)
    f = click.option("--format", "-f", "fmt", default=None, help="输出格式: svg|png|pdf")(f)
    f = click.option("--preset", default=None, help="出版预设: nature|cell|plant_journal|wide|poster")(f)
    f = click.option("--height", "-H", type=int, default=None, help="画布高度")(f)
    f = click.option("--width", "-W", type=int, default=None, help="画布宽度")(f)
    f = click.option("--threads", "-t", type=int, default=None, help="线程数")(f)
    return f



def _plot_prelude(cmd, in_file, out_file, preset, width, height, fmt, bridge):
    """绘图命令公共前奏: pre_flight → preset → resolve_output → ensure_bridge。
    （第三轮审查:消除 volcano/heatmap 等命令前缀的逐字复制）返回 (out_file, width, height)。"""
    pre_flight(cmd, in_file)
    if preset:
        p = apply_preset(preset, width=width, height=height)
        if not p:
            print(f"❌ 未知预设: {preset}", file=sys.stderr)
            sys.exit(1)
        if 'width' in p and not width:
            width = p['width']
        if 'height' in p and not height:
            height = p['height']
    out_file = resolve_output(out_file, fmt)
    if bridge:
        ensure_bridge(bridge)
    return out_file, width, height


def _append_size(args, width, height):
    """公共尾部: width/height 拼装(--width/--height 风格)"""
    if width:
        args += ["--width", str(width)]
    if height:
        args += ["--height", str(height)]
    return args
# ---- 主命令组 ----
class RootGroup(click.Group):
    """顶层：未知命令时给分组建议 + 拼写纠错"""
    def resolve_command(self, ctx, args):
        try:
            return super().resolve_command(ctx, args)
        except click.UsageError:
            if not args:
                raise
            name = args[0]
            # 兼容旧写法/README：顶层裸命令自动转发到分组（如 tbtools seqlogo → tbtools seq logo）
            for gname, g in _groups.items():
                if name in g.commands:
                    return gname, g.commands[name], args[1:]  # F841 修复: 删未用 sub 变量
            # 拼写纠错（对分组名+顶层命令；前缀匹配优先——venn2 案例：n=3 截断挤掉正确建议）
            import difflib
            candidates = sorted(set(list(_groups.keys()) + [c for c in cli.commands.keys()]))
            prefix_hits = [c for c in candidates if c.startswith(name)]
            close = prefix_hits[:5] or difflib.get_close_matches(name, candidates, n=3, cutoff=0.6)
            if close:
                click.echo(f"❌ 未知命令: {name}", err=True)
                click.echo(f"   你是不是想用: {' / '.join(close)}?", err=True)
            else:
                click.echo(f"❌ 未知命令: {name}", err=True)
                click.echo("   查看: tbtools list", err=True)
            ctx.exit(2)

try:
    from importlib.metadata import version as _pkg_version
    _CLI_VERSION = _pkg_version("tbtools-cli")  # pyproject 单一来源
    del _pkg_version
except Exception:
    _CLI_VERSION = "1.1.0"

@click.group(cls=RootGroup, invoke_without_command=True)
@click.version_option(_CLI_VERSION, prog_name="tbtools-cli")
@click.pass_context
def cli(ctx):
    """TBtools-II 全功能 CLI（命令/工具/RPC 数字见 tbtools list）"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

# ---- 命令组：序列/结构 ----
@cli.group("seq")
def seq_group():
    """序列/结构域命令"""

@seq_group.command("logo")
@click.argument("input_file")
@click.argument("output_file")
@click.option("--scale-ic/--no-scale-ic", default=True, help="按信息含量缩放")
@click.option("--show-pos/--no-show-pos", default=False, help="显示位置编号")
@common_options
def seqlogo(input_file, output_file, scale_ic, show_pos, verbose, quiet, fmt, preset, height, width, threads):
    """序列 LOGO 图"""
    output_file, width, height = _plot_prelude("logo", input_file, output_file, preset, width, height, fmt, None)
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioDoer.seqLogo.makeSeqLogo",
            "--inFile", input_file, "--OutGraph", output_file]
    if not scale_ic:
        args += ["--scaleIC=false"]
    if show_pos:
        args += ["--showPos=true"]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="seqlogo")
    sys.exit(ec)

@seq_group.command("msa")
@click.argument("aligned_fasta")
@click.argument("output_file")
@click.option("--padding", type=int, default=0, help="序列间填充")
@common_options
def seq_msa(aligned_fasta, output_file, padding, verbose, quiet, fmt, preset, height, width, threads):
    """多序列比对可视化"""
    output_file, width, height = _plot_prelude("msa", aligned_fasta, output_file, preset, width, height, fmt, "MSACli")
    args = ["java", "-Xmx3g", "-cp", cp(os.path.join(ROOT, "build"), JAR),
            "MSACli", aligned_fasta, output_file]
    if padding:
        args += ["--padding", str(padding)]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="msa")
    sys.exit(ec)

@seq_group.command("structure")
@click.argument("gff_file")
@click.argument("id_list")
@click.argument("output_file")
@click.option("--genome", "-g", default=None, help="基因组 FASTA（可选）")
@common_options
def seq_structure(gff_file, id_list, output_file, genome, verbose, quiet, fmt, preset, height, width, threads):
    """基因结构图（外显子/UTR 从 GFF）"""
    output_file, width, height = _plot_prelude("structure", gff_file, output_file, preset, width, height, fmt, "GeneStructureCli")
    args = ["java", "-Xmx3g", "-cp", cp(os.path.join(ROOT, "build"), JAR),
            "GeneStructureCli", gff_file, id_list, output_file]
    if genome:
        args += [genome]
    if width: args += [str(width)]
    if height: args += [str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="structure")
    sys.exit(ec)


# 旧名别名（README/老用户兼容）：genestructure == structure
seq_group.add_command(seq_structure, name="genestructure")

@seq_group.command("motif")
@click.argument("meme_xml")
@click.argument("id_list")
@click.argument("output_file")
@common_options
def seq_motif(meme_xml, id_list, output_file, verbose, quiet, fmt, preset, height, width, threads):
    """Motif 分布图（MEME XML）"""
    output_file, width, height = _plot_prelude("motif", meme_xml, output_file, preset, width, height, fmt, "MotifCli")
    args = ["java", "-Xmx3g", "-cp", cp(os.path.join(ROOT, "build"), JAR),
            "MotifCli", meme_xml, id_list, output_file]
    if width: args += [str(width)]
    if height: args += [str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="motif")
    sys.exit(ec)

# ---- 命令组：表达/统计 ----
@cli.group("expr")
def expr_group():
    """表达/统计命令"""

@expr_group.command("volcano")
@click.argument("deg_file")
@click.argument("output_file")
@click.option("--pval-cutoff", "-p", type=float, default=0.05, help="P值阈值")
@click.option("--fc-cutoff", "-c", type=float, default=1.0, help="Log2FC 阈值")
@common_options
def volcano(deg_file, output_file, pval_cutoff, fc_cutoff, verbose, quiet, fmt, preset, height, width, threads):
    """火山图（DEG: GeneID Log2FC pvalue）"""
    output_file, width, height = _plot_prelude("volcano", deg_file, output_file, preset, width, height, fmt, "GenericCli")
    args = ["java", "-Xmx2g", "-cp", cp(os.path.join(ROOT, "build"), JAR),
            "GenericCli", "biocjava.bioDoer.JIGplotToolkit.VocanoPlot.vocanoPlot", "show",
            output_file, "--set", "inData", deg_file]
    args += ["--set", "log2FoldChange", "true", "--set", "negLogPvalue", "true"]
    args += ["--set", "pvalueCutOff", str(pval_cutoff), "--set", "foldChangeCutOff", str(fc_cutoff)]
    args += ["--set", "normPointSize", "5.0", "--set", "showTopChangeNum", "5"]
    if width:
        args += ["--width", str(width)]
    if height:
        args += ["--height", str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="volcano")
    sys.exit(ec)

@expr_group.command("heatmap")
@click.argument("matrix_file")
@click.argument("output_file")
@click.option("--log2/--no-log2", default=False, help="log2 转换")
@click.option("--row-scale/--no-row-scale", default=False, help="行标准化")
@click.option("--cluster-row/--no-cluster-row", default=False, help="行聚类")
@click.option("--cluster-col/--no-cluster-col", default=False, help="列聚类")
@common_options
def heatmap(matrix_file, output_file, log2, row_scale, cluster_row, cluster_col, verbose, quiet, fmt, preset, height, width, threads):
    """热图（表达矩阵）"""
    output_file, width, height = _plot_prelude("heatmap", matrix_file, output_file, preset, width, height, fmt, "HeatmapCli")
    args = ["java", "-Xmx3g", "-cp", cp(os.path.join(ROOT, "build"), JAR),
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
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="heatmap")
    sys.exit(ec)

@expr_group.command("pca")
@click.argument("matrix_file")
@click.argument("output_file")
@click.argument("direction", type=click.Choice(["row", "col"]), default="row")
@click.option("--scale/--no-scale", default=False, help="标准化")
@common_options
def expr_pca(matrix_file, output_file, direction, scale, verbose, quiet, fmt, preset, height, width, threads):
    """PCA 图"""
    output_file, width, height = _plot_prelude("pca", matrix_file, output_file, preset, width, height, fmt, "GenericCli")
    args = ["java", "-Xmx3g", "-cp", cp(os.path.join(ROOT, "build"), JAR),
            "GenericCli", "biocjava.bioDoer.JIGplotToolkit.PCAanalysis.PCAanalysis",
            "doPCA+postGraph", output_file,
            "--set", "inTabFile", matrix_file,
            "--set", "rowName", "true", "--set", "colName", "true",
            "--set", "processDirect", "Rows" if direction == "row" else "Columns"]
    if scale: args += ["--set", "scale", "true"]
    args += ["--set", "pointSize", "8.0", "--set", "showLabel", "true"]
    if width: args += ["--width", str(width)]
    if height: args += ["--height", str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="pca")
    sys.exit(ec)

@expr_group.command("hclust")
@click.argument("distance_file")
@click.argument("output_file")
@common_options
def expr_hclust(distance_file, output_file, verbose, quiet, fmt, preset, height, width, threads):
    """层次聚类树（三列距离文件 GeneA\tGeneB\tdist）"""
    output_file, width, height = _plot_prelude("hclust", distance_file, output_file, preset, width, height, fmt, "HclustCli")
    args = ["java", "-Xmx3g", "-cp", cp(os.path.join(ROOT, "build"), JAR),
            "HclustCli", distance_file, output_file]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="hclust")
    sys.exit(ec)

@expr_group.command("dehist")
@click.argument("deg_file")
@click.argument("output_file")
@common_options
def expr_dehist(deg_file, output_file, verbose, quiet, fmt, preset, height, width, threads):
    """差异表达双直方图"""
    pre_flight("dehist", deg_file)
    output_file = resolve_output(output_file, fmt)
    # FIX(G5): 原注册类 DiffExp.DualHistPlot.DiffExpDualHistPlot 在 2.535 jar 不存在，
    # 真实类 RNAseqViz.DiffExpDualHistPlot main 硬编码 → DeHistCli 桥（doctor 死命令探测发现）
    ensure_bridge("DeHistCli")
    args = ["java", "-Xmx2g", "-cp", cp(os.path.join(ROOT, "build"), JAR),
            "DeHistCli", deg_file, output_file]
    if width: args += [str(width)]
    if height: args += [str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="dehist")
    sys.exit(ec)

# ---- 命令组：树/进化 ----
@cli.group("tree")
def tree_group():
    """树/进化命令"""

@tree_group.command("draw")
@click.argument("config_file")
@click.argument("output_file")
@common_options
def tree_draw(config_file, output_file, verbose, quiet, fmt, preset, height, width, threads):
    """树+注释图（TreeTreeTree 多轨道）"""
    output_file, width, height = _plot_prelude("draw", config_file, output_file, preset, width, height, fmt, "TreeCli")
    args = ["java", "-Xmx3g", "-cp", cp(os.path.join(ROOT, "build"), JAR),
            "TreeCli", config_file, output_file]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="draw")
    sys.exit(ec)

@tree_group.command("unrooted")
@click.argument("newick_file")
@click.argument("output_file")
@common_options
def tree_unrooted(newick_file, output_file, verbose, quiet, fmt, preset, height, width, threads):
    """无根树可视化"""
    output_file, width, height = _plot_prelude("unrooted", newick_file, output_file, preset, width, height, fmt, "UnrootedTreeCli")
    args = ["java", "-Xmx3g", "-cp", cp(os.path.join(ROOT, "build"), JAR),
            "UnrootedTreeCli", newick_file, output_file]
    if width: args += ["--width", str(width)]
    if height: args += ["--height", str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="unrooted")
    sys.exit(ec)

@tree_group.command("rooting")
@click.argument("input_nwk")
@click.argument("output_nwk")
@common_options
def tree_rooting(input_nwk, output_nwk, verbose, quiet, fmt, preset, height, width, threads):
    """MAD 系统发育定根"""
    # FIX(G5): 原注册类 newickParser.TreeTreeTree.TreeRootingByMAD 在 2.535 jar 不存在，
    # 改走既有 TreeRootingCli 桥（quickMadRoot，08/29 已验证）
    ensure_bridge("TreeRootingCli")
    args = ["java", "-Xmx2g", "-cp", cp(os.path.join(ROOT, "build"), JAR),
            "TreeRootingCli", input_nwk, output_nwk]
    ec = run_java(args, verbose=verbose, quiet=quiet, command_name="rooting")
    sys.exit(ec)


# 旧名别名（README/老用户兼容）：treeRooting == rooting
tree_group.add_command(tree_rooting, name="treeRooting")

@tree_group.command("one-step")
@click.argument("pep_fasta")
@click.argument("output_prefix")
@click.option("--bb-time", "-b", type=int, default=1000, help="IQ-TREE bootstrap iterations")
@common_options
def tree_onesteptree(pep_fasta, output_prefix, bb_time, verbose, quiet, fmt, preset, height, width, threads):
    """一步法 ML 树（muscle → trimal → IQ-TREE）"""
    # FIX(G5): 原注册类 Phylogenetics.OneStepTree 在 2.475/2.535 jar 均不存在（外部测试 P1-1
    # + 本地 doctor 探测复核）；真实引擎为 BioSoftPipeServer.OneStepMLTree。
    # ⚠️ 该引擎 ArgsParser 只认 --inPepFie/--outFilePrefix/--clean/--bbTime，没有 --threads！
    args = ["java", "-Xmx4g", "-cp", JAR,
            "biocjava.bioIO.BioSoftPipeServer.OneStepMLTree",
            "--inPepFie", pep_fasta, "--outFilePrefix", output_prefix,
            "--bbTime", str(bb_time)]
    ec = run_java(args, verbose=verbose, quiet=quiet, command_name="onesteptree")
    sys.exit(ec)

# ---- 命令组：工具 ----
# N2: GUI 面板类工具黑名单（headless 无参直通会弹 Swing 窗口悬挂）
_GUI_TOOLS = {"RNAplotAdvance", "PlotRNAfold", "AmazingGeneView", "BlastZone", "SequenceZone"}

class ToolGroup(click.Group):
    """tool 分组：未知子命令自动转发 auto_commands + --help 列出全部"""
    def resolve_command(self, ctx, args):
        try:
            return super().resolve_command(ctx, args)
        except click.UsageError:
            if args:
                name = args[0]
                impl = getattr(_ac, f'_{name}_impl', None)
                if impl:
                    doc = (impl.__doc__ or '').split(':',1)[1].strip() if ':' in (impl.__doc__ or '') else f'{name} [参数...]'
                    pitfall = get_pitfall_hint(name)
                    help_text = doc + (f'\n\n⚠️ {pitfall}' if pitfall else '')
                    # FIX(P0-1): 旧写法闭包捕获 tool 分组自身 Context（ctx.args 恒空），
                    # 所有参数被丢弃。改用 pass_context 拿子命令自己的 Context。
                    # （外部测试 2026-09-19 实测,Windows 已验证）
                    @click.pass_context
                    def _fwd(sctx, _impl=impl):
                        sys.exit(_impl(list(sctx.args)))
                    cmd = click.Command(name=name,
                        callback=_fwd,
                        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
                        help=help_text)
                    return name, cmd, args[1:]
                # FIX(P0-3): 回退到共享注册表（82 个 CLI 工具，原仅旧入口 tbcli.py 可达，
                # 外部测试 §3.3：rpkmCal/statFasta/tpmCalc 等在新入口全部未找到）
                cls = CLI_TOOLS.get(name)
                if cls:
                    @click.pass_context
                    def _fwd_reg(sctx, _cls=cls, _name=name):
                        # N2: GUI 类工具无参直通会弹 Swing 窗口悬挂——黑名单无参时打印用法即退出
                        if _name in _GUI_TOOLS and not sctx.args:
                            click.echo(f"❌ {_name} 是 GUI 面板类工具，headless 下不可用；请提供参数直接调用引擎[Usage]查看签名", file=sys.stderr)
                            click.echo(f"   💡 查看引擎真实参数: java -cp $TBTOOLS_JAR {_cls} --bogus x（逼出 Usage）", file=sys.stderr)
                            sys.exit(1)
                        java_args = ["java", "-Xmx4g", "-cp", JAR, _cls] + list(sctx.args)
                        sys.exit(run_java(java_args, command_name=_name))
                    cmd = click.Command(name=name,
                        callback=_fwd_reg,
                        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
                        help=f"{name} [引擎命名参数...]\n\n⚠️ ArgsParser 系引擎一律 --key value 空格分隔，--key=value 会被拒绝")
                    return name, cmd, args[1:]
                click.echo(f"❌ 未知工具: {name}", file=sys.stderr)
                count = 0
                for n in sorted(dir(_ac)):
                    if n.startswith('_') and n.endswith('_impl') and not n.startswith('__'):
                        cmd = n[1:-5]
                        doc = getattr(_ac, n).__doc__ or ''
                        short = doc.split(':',1)[1].strip()[:50] if ':' in doc else ''
                        click.echo(f"  {cmd:20s} {short}", file=sys.stderr)
                        count += 1
                for tname in sorted(CLI_TOOLS):
                    if getattr(_ac, f'_{tname}_impl', None):
                        continue
                    click.echo(f"  {tname:20s} {CLI_TOOLS[tname].split('.')[-1]}", file=sys.stderr)
                    count += 1
                click.echo(f"\n共 {count} 个工具，查看: tbtools list tools", file=sys.stderr)
                ctx.exit(2)
            raise
    
    def format_options(self, ctx, formatter):
        """重写 --help：手动命令 + auto_command 工具全列出"""
        super().format_options(ctx, formatter)
        plot_groups = {'seq', 'expr', 'tree', 'syn', 'sets', 'chipseq'}
        entries = []
        for n in sorted(dir(_ac)):
            if n.startswith('_') and n.endswith('_impl') and not n.startswith('__'):
                cmd = n[1:-5]
                cat = CATEGORY_MAP.get(cmd, 'engine')
                if cat in plot_groups:
                    continue
                doc = getattr(_ac, n).__doc__ or ''
                short = doc.split(':',1)[1].strip()[:50] if ':' in doc else ''
                entries.append(f"{cmd:20s} {short}")
        if entries:
            with formatter.section(f'可用工具（共 {len(entries)} 个，完整列表: tbtools list tools）'):
                for e in entries[:20]:
                    formatter.write_text(e)
                if len(entries) > 20:
                    formatter.write_text(f"... 及其他 {len(entries)-20} 个")

@cli.group("tool", cls=ToolGroup)
def tool_group():
    """命令行工具（82 个）"""

@tool_group.command("stat-fasta")
@click.argument("input_file")
@click.argument("output_file")
@common_options
def tool_stat_fasta(input_file, output_file, verbose, quiet, fmt, preset, height, width, threads):
    """FASTA 序列统计"""
    # stdin 管道支持
    if input_file == "-":
        import tempfile
        tmp = tempfile.mktemp(suffix=".fa")
        with open(tmp, "wb") as f:
            f.write(sys.stdin.buffer.read())
        input_file = tmp
    if output_file == "-":
        output_file = stdout_path()
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioIO.FastX.FastaIndex.QuickStatFasta",
            "--inFasta", input_file, "--outPutFile", output_file]
    ec = run_java(args, verbose=verbose, quiet=quiet, command_name="stat_fasta")
    sys.exit(ec)

@tool_group.command("cds2protein")
@click.argument("cds_fasta")
@click.argument("output_file")
@common_options
def tool_cds2protein(cds_fasta, output_file, verbose, quiet, fmt, preset, height, width, threads):
    """CDS → 蛋白质翻译"""
    if output_file == "-": output_file = stdout_path()
    # FIX(G5): 原注册类 JIGplotToolkit.Protein.CdsToProtein 在 2.535 jar 不存在，
    # 真实引擎 bioIO.ORF.Translater（ArgsParser: --inFa/--outFa）
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioIO.ORF.Translater",
            "--inFa", cds_fasta, "--outFa", output_file]
    ec = run_java(args, verbose=verbose, quiet=quiet, command_name="cds2protein")
    sys.exit(ec)

@tool_group.command("fasta-extract")
@click.argument("input_fasta")
@click.argument("id_list")
@click.argument("output_file")
@common_options
def tool_fasta_extract(input_fasta, id_list, output_file, verbose, quiet, fmt, preset, height, width, threads):
    """按 ID 列表提取 FASTA 序列（idList: 一行一个 ID,不带 > 号;与原始 header 精确匹配）"""
    if input_fasta == "-":
        import tempfile; tmp = tempfile.mktemp(suffix=".fa")
        with open(tmp, "wb") as f: f.write(sys.stdin.buffer.read())
        input_fasta = tmp
    if output_file == "-": output_file = stdout_path()
    # FIX(G5): 原注册类 bioIO.FastX.FastaIndex.ExtractFasta 路径错误，
    # 真实类 bioDoer.Fasta.ExtractFasta（ArgsParser: --inFa/--inIDList/--outFa）
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioDoer.Fasta.ExtractFasta",
            "--inFa", input_fasta, "--inIDList", id_list, "--outFa", output_file]
    ec = run_java(args, verbose=verbose, quiet=quiet, command_name="fasta_extract")
    sys.exit(ec)

# ---- 动态装配(批次 B: cli_load)----
build_and_load(cli)
register_top(cli, cli_load)

_load_dynamic_commands()
_load_auto_commands()


# 旧名别名（README/老用户兼容，顶层/分组均可用）——须在 cli() 前注册
seq_group.add_command(seqlogo, name="seqlogo")
expr_group.add_command(heatmap, name="heatmap2")
# ---- RPC 分组注册（批次 B: 从 cli_rpc 模块组装）----
cli.add_command(build_rpc_group())


if __name__ == "__main__":
    cli()
