"""tbtools-cli 主入口 — Python click 重构版"""
import os
import shutil
import subprocess
import sys

import click

# ---- 配置 ----
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tbtools_cli.auto_commands as _ac
from tbtools_cli.cli_tools_registry import CLI_TOOLS
from tbtools_cli.core import (
    JAR,
    ROOT,
    c,
    check_input_format,
    cp,
    detect_format,
    ensure_bridge,
    get_pitfall_hint,
    pre_flight,
    resolve_output,
    run_java,
    run_plot,
    stdout_path,
    validate_file,
)
from tbtools_cli.presets import PRESETS, apply_preset, list_presets


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
                    sub = click.Context(g, info_name=gname, parent=ctx)
                    return gname, g.commands[name], args[1:]
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

@click.group(cls=RootGroup, invoke_without_command=True)
@click.version_option("1.0.0", prog_name="tbtools-cli")
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
    pre_flight("logo", input_file)
    output_file = resolve_output(output_file, fmt)
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
    pre_flight("msa", aligned_fasta)
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("MSACli")
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
    pre_flight("structure", gff_file)
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("GeneStructureCli")
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
    pre_flight("motif", meme_xml)
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("MotifCli")
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
    pre_flight("volcano", deg_file)
    if preset:
        p = apply_preset(preset, width=width, height=height)
        if not p: print(f"❌ 未知预设: {preset}", file=sys.stderr); sys.exit(1)
        if 'width' in p and not width: width = p['width']
        if 'height' in p and not height: height = p['height']
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("GenericCli")
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
    pre_flight("heatmap", matrix_file)
    """热图（表达矩阵）"""
    # N12: heatmap 应用 --preset（同 volcano 通用选项一致性）
    if preset:
        p = apply_preset(preset, width=width, height=height)
        if not p:
            print(f"❌ 未知预设: {preset}", file=sys.stderr); sys.exit(1)
        if 'width' in p and not width: width = p['width']
        if 'height' in p and not height: height = p['height']
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("HeatmapCli")
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
    pre_flight("pca", matrix_file)
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("GenericCli")
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
    pre_flight("hclust", distance_file)
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("HclustCli")
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
    pre_flight("draw", config_file)  # draw 输入是 TreeTab 配置文件，不适用格式表
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("TreeCli")
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
    pre_flight("unrooted", newick_file)
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("UnrootedTreeCli")
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
    # FIX(G5): 原注册类 Phylogenetics.OneStepTree 在 2.475/2.535 jar 均不存在（WorkBuddy P1-1
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
                    # （WorkBuddy 2026-09-19 三轮实测报告 §3.1，Windows 已验证）
                    @click.pass_context
                    def _fwd(sctx, _impl=impl):
                        sys.exit(_impl(list(sctx.args)))
                    cmd = click.Command(name=name,
                        callback=_fwd,
                        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
                        help=help_text)
                    return name, cmd, args[1:]
                # FIX(P0-3): 回退到共享注册表（82 个 CLI 工具，原仅旧入口 tbcli.py 可达，
                # WorkBuddy 报告 §3.3：rpkmCal/statFasta/tpmCalc 等在新入口全部未找到）
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
    """按 ID 列表提取 FASTA 序列"""
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

# ---- 通用命令 ----
@cli.command()
def version():
    """显示版本信息"""
    # 动态统计
    plot_count = sum(len(g.commands) for g in _groups.values())
    auto_count = sum(1 for n in dir(_ac) if n.startswith('_') and n.endswith('_impl') and not n.startswith('__'))
    from tbtools_cli.core import BRIDGES_DIR, PITFALL_HINTS
    bridge_count = len([f for f in os.listdir(BRIDGES_DIR) if f.endswith('.java')]) if os.path.isdir(BRIDGES_DIR) else 80
    click.echo("tbtools-cli v1.0.0")
    click.echo(f"  {plot_count} 绘图/分析命令 + {auto_count} auto_commands + 188 RPC 方法")
    click.echo(f"  bridges: {bridge_count} | pitfall hints: {len(PITFALL_HINTS)}")
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
        ("xvfb-run", "xvfb-run（Linux 绘图必需）", os.name != "nt"),  # N14: Windows 无 xvfb 且不需要
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
        # G5: 死命令探测（jar 版本与 CLI 注册类不匹配预警，WorkBuddy P1-1）
        from tbtools_cli.core import probe_dead_engines
        dead = probe_dead_engines()
        if dead:
            click.echo(f"  ⚠️ 死命令探测: {len(dead)} 个注册引擎类在当前 jar 中不存在（版本不匹配）:")
            for cls, src in dead[:5]:
                click.echo(f"      - {cls}  （注册于 {src}）")
            if len(dead) > 5:
                click.echo(f"      ... 及其他 {len(dead)-5} 个")
            click.echo("      💡 这些命令会 ClassNotFound；升级 jar 到 2.535+ 或忽略对应命令")
            warn += 1
        else:
            click.echo("  ✅ 引擎类完整性: 注册类全部存在于 jar")
            ok += 1
    else:
        click.echo("  ❌ JAR: 未找到")
        err += 1
        click.echo("")
        click.echo("  ── 解决方法（AI 可直接执行）──")
        click.echo("  ① 本机已有 TBtools jar？自动搜索并配置：")
        click.echo("       tbtools setup --auto")
        click.echo("  ② 知道 jar 路径，直接指定：")
        click.echo("       tbtools setup /path/to/TBtools_JRE1.6.jar")
        click.echo("  ③ 还没有 jar，自动下载+提取+配置（官方只发 portable zip）：")
        click.echo("       tbtools fetch-jar")
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
@click.argument('jar_path', required=False)
@click.option('--auto', is_flag=True, help="自动搜索本机 TBtools jar 并配置")
def setup(jar_path, auto):
    """配置 TBtools jar 路径（AI 友好：一条命令接入本机 TBtools）"""
    import glob as _glob
    found = None
    if jar_path:
        if not os.path.isfile(jar_path):
            click.echo(f"❌ 文件不存在: {jar_path}", err=True)
            sys.exit(1)
        found = jar_path
    elif auto:
        click.echo("🔍 自动搜索 TBtools jar ...")
        # 复用 core 的搜索逻辑 + glob 深层搜索
        candidates = []
        for pat in [
            os.path.expanduser("~/TBtools*/**/TBtools_JRE1.6.jar"),
            os.path.expanduser("~/Downloads/TBtools*.jar"),
            os.path.expanduser("~/下载/TBtools*.jar"),
            os.path.expanduser("~/Desktop/TBtools*.jar"),
            "/opt/TBtools*/**/TBtools_JRE1.6.jar",
            "/mnt/*/TBtools*/**/TBtools_JRE1.6.jar",
            "/mnt/*/Users/*/Downloads/TBtools*.jar",
            "/mnt/*/Users/*/Desktop/TBtools*.jar",
            "/Applications/TBtools*/**/TBtools_JRE1.6.jar",
        ]:
            try:
                candidates.extend(_glob.glob(pat, recursive=True))
            except Exception:
                pass
        candidates = sorted(set(c for c in candidates if os.path.isfile(c)))
        if candidates:
            found = candidates[0]
            click.echo(f"✅ 找到: {found}")
            if len(candidates) > 1:
                click.echo(f"   （还有 {len(candidates)-1} 个候选，用 tbtools setup <路径> 指定其他）")
        else:
            click.echo("❌ 未找到。请先下载 TBtools_JRE1.6.jar：")
            click.echo("   https://github.com/CJ-Chen/TBtools/releases")
            click.echo("   下载后运行: tbtools setup /path/to/TBtools_JRE1.6.jar")
            sys.exit(1)
    else:
        click.echo("用法:")
        click.echo("  tbtools setup --auto                    # 自动搜索本机 jar")
        click.echo("  tbtools setup /path/to/TBtools.jar     # 指定路径")
        sys.exit(0)
    # 写入配置
    cfg_dir = os.path.expanduser("~/.config/tbtools-cli")
    os.makedirs(cfg_dir, exist_ok=True)
    with open(os.path.join(cfg_dir, "config.sh"), "w") as f:
        f.write(f'export TBTOOLS_JAR="{found}"\n')
    with open(os.path.join(cfg_dir, "config.toml"), "w") as f:
        f.write(f'jar = "{found}"\n\n[defaults]\nthreads = 4\nformat = "svg"\n')
    click.echo(f"✅ 已配置: {found}")
    click.echo("   写入 ~/.config/tbtools-cli/{config.sh,config.toml}")
    click.echo("   运行 tbtools doctor 验证")

@cli.command()
@click.option('--version', 'ver', default=None, help="TBtools 版本 tag（默认最新含 portable 的 release）")
@click.option('--yes', is_flag=True, help="跳过确认")
def fetch_jar(ver, yes):
    """自动下载并提取 TBtools_JRE1.6.jar（官方只发 portable zip，需解包）"""
    import tempfile
    import urllib.request
    import zipfile
    # 确定版本
    tag = ver
    if not tag:
        click.echo("🔍 查询最新 portable release ...")
        try:
            req = urllib.request.Request("https://api.github.com/repos/CJ-Chen/TBtools-II/releases",
                headers={"Accept": "application/vnd.github+json", "User-Agent": "tbtools-cli"})
            import json
            rels = json.loads(urllib.request.urlopen(req, timeout=30).read())
            tag = next((r["tag_name"] for r in rels
                        if any("portable" in a["name"] for a in r.get("assets", []))), None)
            if not tag:
                click.echo("❌ 未找到含 portable 的 release", err=True)
                sys.exit(1)
            click.echo(f"   最新: {tag}")
        except Exception as e:
            click.echo(f"❌ 查询失败: {e}", err=True)
            click.echo("   手动: tbtools fetch-jar --version 2.475", err=True)
            sys.exit(1)
    # 找资产
    zip_name = None
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/CJ-Chen/TBtools-II/releases/tags/{tag}",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "tbtools-cli"})
        import json
        rel = json.loads(urllib.request.urlopen(req, timeout=30).read())
        zip_name = next((a["name"] for a in rel.get("assets", []) if "portable" in a["name"] and a["name"].endswith(".zip")), None)
    except Exception as e:
        click.echo(f"❌ 查询资产失败: {e}", err=True)
        sys.exit(1)
    if not zip_name:
        click.echo(f"❌ {tag} 无 portable zip 资产", err=True)
        sys.exit(1)
    url = f"https://github.com/CJ-Chen/TBtools-II/releases/download/{tag}/{zip_name}"
    size_mb = None
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "tbtools-cli"})
        resp = urllib.request.urlopen(req, timeout=30)
        size_mb = int(resp.headers.get("Content-Length", 0)) / 1024 / 1024
    except Exception:
        pass
    click.echo(f"📦 下载 {zip_name}" + (f"（~{size_mb:.0f}MB）" if size_mb else ""))
    if not yes:
        if not click.confirm("  继续下载?"):
            click.echo("已取消")
            sys.exit(0)
    # 下载
    tmp = tempfile.mktemp(suffix=".zip")
    click.echo("  ⏳ 下载中（约 300MB，请稍候）...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "tbtools-cli"})
        with urllib.request.urlopen(req, timeout=600) as r, open(tmp, "wb") as f:
            import shutil as _sh
            _sh.copyfileobj(r, f)
    except Exception as e:
        click.echo(f"❌ 下载失败: {e}", err=True)
        sys.exit(1)
    # 提取 jar
    jar_target = os.path.expanduser("~/tbtools-cli/lib/TBtools_JRE1.6.jar")
    os.makedirs(os.path.dirname(jar_target), exist_ok=True)
    found = False
    try:
        with zipfile.ZipFile(tmp) as z:
            for n in z.namelist():
                if n.endswith("TBtools_JRE1.6.jar"):
                    click.echo(f"  📂 提取 {n}")
                    with z.open(n) as src, open(jar_target, "wb") as dst:
                        _sh = __import__("shutil")
                        _sh.copyfileobj(src, dst)
                    found = True
                    break
    except Exception as e:
        click.echo(f"❌ 解压失败: {e}", err=True)
        sys.exit(1)
    finally:
        os.unlink(tmp)
    if not found:
        click.echo("❌ zip 中未找到 TBtools_JRE1.6.jar", err=True)
        sys.exit(1)
    click.echo(f"✅ 已提取: {jar_target}")
    # 配置
    cfg_dir = os.path.expanduser("~/.config/tbtools-cli")
    os.makedirs(cfg_dir, exist_ok=True)
    with open(os.path.join(cfg_dir, "config.sh"), "w") as f:
        f.write(f'export TBTOOLS_JAR="{jar_target}"\n')
    with open(os.path.join(cfg_dir, "config.toml"), "w") as f:
        f.write(f'jar = "{jar_target}"\n\n[defaults]\nthreads = 4\nformat = "svg"\n')
    click.echo("✅ 已配置。运行 tbtools doctor 验证")

@cli.command()
@click.argument('name')
def help(name):
    """快捷帮助: tbtools help <命令名> 自动定位 + 坑位提示"""
    # 尝试在所有分组中查找
    for gname, g in _groups.items():
        if name in g.commands:
            cmd = g.commands[name]
            click.echo(f"\n  命令: {gname} {name}  （分组 {gname}）")
            if cmd.help:
                click.echo(f"\n{cmd.help}")
            # 坑位提示
            pit = get_pitfall_hint(name)
            if pit:
                click.echo(f"\n  ⚠️ 坑位: {pit}")
            # 示例（若存在）
            try:
                from tbtools_cli.auto_commands import EXAMPLES
                ex = EXAMPLES.get(name)
                if ex:
                    click.echo(f"\n  示例: {ex}")
            except Exception:
                pass
            click.echo(f"\n  完整帮助: tbtools {gname} {name} --help")
            return
    # 顶层命令
    if name in cli.commands:
        cmd = cli.commands[name]
        if cmd.help:
            click.echo(f"\n{cmd.help}")
        return
    # 共享注册表工具（P0-3：tbtools tool <name> 动态解析，不在静态 commands 里）
    if name in CLI_TOOLS:
        click.echo(f"\n  命令: tool {name}  （分组 tool · 注册表工具）")
        click.echo(f"\n  {name} [引擎命名参数...]")
        click.echo(f"  引擎类: {CLI_TOOLS[name]}")
        click.echo("\n  ⚠️ ArgsParser 系引擎一律 --key value 空格分隔，--key=value 会被拒绝")
        click.echo(f"  💡 查看引擎真实参数: java -cp $TBTOOLS_JAR {CLI_TOOLS[name]} --bogus x（逼出 Usage）")
        click.echo(f"\n  完整帮助: tbtools tool {name} --help")
        return
    click.echo(f"❌ 未找到命令: {name}")
    click.echo("   查看: tbtools list")
    sys.exit(1)

@cli.group('rpc')
def rpc_group():
    """RPC 服务器管理（188 方法）"""

# ---------- RPC 自愈基础设施（N34/N35 批次 2）----------
# 症状：引擎进程内存/空闲期自发死亡；代理层把死亡伪装成 502；CLI 无感知、无自愈。
# 方案：pid 文件 + 健康探针（system.listMethods）+ call/methods 前 ensure 自动拉起。
# 注意：urllib 必须绕过代理（N41：HTTP_PROXY 注入会让 127.0.0.1 请求走代理转发失败）。

def _rpc_state_dir():
    d = os.environ.get(
        "TBTOOLS_RPC_DIR",
        os.path.join(os.path.expanduser("~"), ".config", "tbtools-cli"),
    )
    os.makedirs(d, exist_ok=True)
    return d

def _rpc_pid_file(port):
    return os.path.join(_rpc_state_dir(), f"rpc-{port}.pid")

def _rpc_log_file(port):
    return os.path.join(_rpc_state_dir(), f"rpc-{port}.log")

def _rpc_ping(port, timeout=5):
    """健康探针：POST system.listMethods。绕过代理。返回 True/False"""
    import json
    import urllib.request
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/rpc",
            data=json.dumps({"jsonrpc": "2.0", "method": "system.listMethods",
                             "params": {}, "id": 1}).encode(),
            headers={"Content-Type": "application/json"})
        resp = opener.open(req, timeout=timeout)
        result = json.loads(resp.read())
        return "result" in result
    except Exception:
        return False

def _rpc_read_pid(port):
    """读 pid 文件；进程不存在或与 RPC 无关则清理并返回 None"""
    pid_file = _rpc_pid_file(port)
    try:
        with open(pid_file) as f:
            pid = int(f.read().strip())
    except Exception:
        return None
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError, OverflowError, ValueError):
        _rpc_remove_pid(port)
        return None
    # Linux 下确认 cmdline 是 RPC server（防 pid 复用误杀）
    cmdline = f"/proc/{pid}/cmdline"
    if os.path.isfile(cmdline):
        try:
            with open(cmdline, "rb") as f:
                if b"biocjava.rpc.RpcServer" not in f.read():
                    _rpc_remove_pid(port)
                    return None
        except Exception:
            pass
    return pid

def _rpc_write_pid(port, pid):
    with open(_rpc_pid_file(port), "w") as f:
        f.write(str(pid))

def _rpc_remove_pid(port):
    try:
        os.remove(_rpc_pid_file(port))
    except OSError:
        pass

def _rpc_launch(port, mem):
    """拉起 RPC 服务器（detached，OOM 崩溃转储，日志落盘）。返回 Popen"""
    if not JAR or not os.path.isfile(JAR):
        raise FileNotFoundError(
            "TBtools jar 未找到。请设置 TBTOOLS_JAR 环境变量或放入常见位置")
    log_path = _rpc_log_file(port)
    log_fh = open(log_path, "ab", buffering=0)
    args = [
        "java", f"-Xmx{mem}",
        # N35: OOM 时宁可崩溃（可自愈拉起）也不要僵尸悬挂；同时留堆转储供排查
        "-XX:+CrashOnOutOfMemoryError",
        "-XX:+HeapDumpOnOutOfMemoryError",
        f"-XX:HeapDumpPath={_rpc_state_dir()}",
        "-cp", JAR, "biocjava.rpc.RpcServer",
    ]
    proc = subprocess.Popen(
        args, stdout=log_fh, stderr=log_fh, start_new_session=True)
    _rpc_write_pid(port, proc.pid)
    return proc

def _ensure_rpc(port, mem="4g", wait_s=30, quiet=False):
    """ensure 逻辑（同交付包 run_p*.py 的 ensure_srv）：
    健康 → True；不健康/死亡 → 清 stale pid → 拉起 → 轮询健康。"""
    if _rpc_ping(port):
        return True
    old_pid = _rpc_read_pid(port)
    if old_pid:
        if not quiet:
            click.echo(f"⚠️ 检测到旧 RPC 进程 (PID {old_pid}) 无响应，终止后拉起新实例...", err=True)
        try:
            os.kill(old_pid, 15)
        except OSError:
            pass
        _rpc_remove_pid(port)
        import time as _t
        _t.sleep(1)
    elif not quiet:
        click.echo(f"⚠️ RPC 服务器不可达（端口 {port}），自动拉起...", err=True)
    try:
        _rpc_launch(port, mem)
    except FileNotFoundError as e:
        click.echo(f"❌ {e}", err=True)
        return False
    import time as _t
    for _ in range(wait_s):
        _t.sleep(1)
        if _rpc_ping(port):
            return True
    click.echo(f"❌ RPC 服务器 {wait_s}s 内未就绪，日志: {_rpc_log_file(port)}", err=True)
    return False

@rpc_group.command('start')
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
@click.option('--mem', '-m', default='4g', help='Java 堆内存')
@click.option('--force', '-f', is_flag=True, help='强制重启（杀掉已有实例）')
def rpc_start(port, mem, force):
    """启动 RPC 服务器（pid 文件 + 健康检查；已在跑则幂等返回）"""
    import time as _t
    if _rpc_ping(port):
        if not force:
            pid = _rpc_read_pid(port)
            click.echo(f"✅ RPC 服务器已在运行（端口 {port}, PID {pid or '?'}）")
            return
        old = _rpc_read_pid(port)
        click.echo(f"🔄 --force：终止旧实例 (PID {old or '?'})...")
        if old:
            try:
                os.kill(old, 15)
            except OSError:
                pass
        _rpc_remove_pid(port)
        _t.sleep(1)
    else:
        # 清 stale（引擎自发死亡残留）
        old = _rpc_read_pid(port)
        if old:
            click.echo(f"⚠️ 旧 RPC 进程 (PID {old}) 无响应，终止...")
            try:
                os.kill(old, 15)
            except OSError:
                pass
            _rpc_remove_pid(port)
            _t.sleep(1)
    click.echo(f"🚀 启动 RPC 服务器（端口 {port}，堆 {mem}）...")
    try:
        proc = _rpc_launch(port, mem)
    except FileNotFoundError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)
    for _ in range(30):
        _t.sleep(1)
        if _rpc_ping(port):
            click.echo(f"✅ RPC 服务器就绪 (PID {proc.pid})")
            click.echo(f"   pid 文件: {_rpc_pid_file(port)}")
            click.echo(f"   日志: {_rpc_log_file(port)}")
            click.echo(f"   测试: curl -X POST http://127.0.0.1:{port}/rpc -H 'Content-Type: application/json' -d '{{\"method\":\"system.listMethods\",\"params\":{{}},\"id\":1}}'")
            return
    click.echo(f"❌ 启动超时（30s），日志: {_rpc_log_file(port)}", err=True)
    sys.exit(1)

@rpc_group.command('stop')
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
def rpc_stop(port):
    """停止 RPC 服务器"""
    pid = _rpc_read_pid(port)
    if not pid:
        click.echo(f"RPC 服务器未在运行（端口 {port}）")
        _rpc_remove_pid(port)
        return
    try:
        os.kill(pid, 15)
        click.echo(f"✅ 已发送 SIGTERM (PID {pid})")
    except OSError as e:
        click.echo(f"❌ 终止失败: {e}", err=True)
        sys.exit(1)
    _rpc_remove_pid(port)

@rpc_group.command('status')
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
def rpc_status(port):
    """查看 RPC 服务器状态"""
    pid = _rpc_read_pid(port)
    healthy = _rpc_ping(port)
    if healthy:
        click.echo(f"✅ 运行中（端口 {port}, PID {pid or '?'}）")
    elif pid:
        click.echo(f"⚠️ 进程存在 (PID {pid}) 但健康检查失败（可能正在启动或假死）")
        sys.exit(2)
    else:
        click.echo(f"❌ 未运行（端口 {port}）。启动: tbtools rpc start")
        sys.exit(1)

@rpc_group.command('methods')
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
@click.option('--mem', '-m', default='4g', help='自动拉起时的 Java 堆内存')
@click.option('--no-autostart', is_flag=True, help='禁用在不可达时自动拉起')
def rpc_methods(port, mem, no_autostart):
    """列出全部 188 RPC 方法（服务不可达时自动拉起）"""
    import json
    import urllib.request
    if not no_autostart and not _ensure_rpc(port, mem):
        click.echo("   手动启动: tbtools rpc start", err=True)
        sys.exit(1)
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/rpc",
            data=json.dumps({"jsonrpc": "2.0", "method": "system.listMethods", "params": {}, "id": 1}).encode(),
            headers={"Content-Type": "application/json"})
        resp = opener.open(req, timeout=15)
        result = json.loads(resp.read())
        res = result.get('result', [])
        methods = res.get('methods', res) if isinstance(res, dict) else res
        click.echo(f"RPC 方法（{len(methods)} 个）：")
        for m in methods:
            click.echo(f"  {m}")
    except Exception as e:
        click.echo(f"❌ RPC 调用失败: {e}", err=True)
        click.echo("   引擎可能已死，尝试: tbtools rpc start --force", err=True)
        sys.exit(1)

@rpc_group.command('call')
@click.argument('method')
@click.argument('params', required=False)
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
@click.option('--mem', '-m', default='4g', help='自动拉起时的 Java 堆内存')
@click.option('--timeout', '-t', type=int, default=300, help='调用超时（秒）')
@click.option('--no-autostart', is_flag=True, help='禁用在不可达时自动拉起')
def rpc_call(method, params, port, mem, timeout, no_autostart):
    """调用 RPC 方法（服务不可达时自动拉起）"""
    import json
    import urllib.request
    params_obj = json.loads(params) if params else {}
    if not no_autostart and not _ensure_rpc(port, mem):
        click.echo("   手动启动: tbtools rpc start", err=True)
        sys.exit(1)
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/rpc",
            data=json.dumps({"jsonrpc": "2.0", "method": method, "params": params_obj, "id": 1}).encode(),
            headers={"Content-Type": "application/json"})
        resp = opener.open(req, timeout=timeout)
        result = json.loads(resp.read())
        if result.get('error'):
            # N38: 引擎错误 message 空/占位符时补友好提示（GffReconstructorBatch 等家族）
            err = result['error']
            msg = str(err.get('data', {}).get('message') if isinstance(err.get('data'), dict) else err.get('data') or err.get('message') or '')
            if not msg.strip() or msg.strip() == '===== See Following Info =====' or msg.startswith('Something Error'):
                msg = '引擎内部错误且未提供消息（N38 家族，GffReconstructorBatch/BestIdConverter/ReciprocalBlast 已知）'
                click.echo(f"❌ RPC 错误 [{err.get('code')}]: {msg}（原始: {json.dumps(err, ensure_ascii=False)[:200]}）", err=True)
            else:
                click.echo(f"❌ RPC 错误 [{err.get('code')}]: {msg}", err=True)
            sys.exit(1)
        click.echo(json.dumps(result.get('result', ''), indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"❌ RPC 调用失败: {e}", err=True)
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

@cli.command(name="completion")
@click.pass_context
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"]), required=False)
def completion_cmd(ctx, shell):
    """生成 shell 补全脚本（tbtools completion bash）"""
    comp_path = os.path.join(ROOT, "scripts", "tbtools-completion.bash")
    if not os.path.isfile(comp_path):
        click.echo(f"❌ 补全脚本不存在: {comp_path}", err=True)
        sys.exit(1)
    if shell == "bash":
        click.echo(open(comp_path, encoding="utf-8").read())
    elif shell == "zsh":
        click.echo("autoload -U +X bashcompinit && bashcompinit")
        click.echo(open(comp_path, encoding="utf-8").read())
    elif shell == "fish":
        try:
            lines = []
            for gname in _groups:
                for cname in _groups[gname].commands:
                    lines.append(f"complete -c tbtools -n '__fish_use_subcommand' -a '{cname}'")
            click.echo("# tbtools-cli fish 补全")
            click.echo("\n".join(sorted(set(lines))))
        except Exception as e:
            click.echo(f"❌ fish 补全生成失败: {e}", err=True)
            sys.exit(1)
    else:
        click.echo("生成 shell 补全脚本")
        click.echo("用法: tbtools completion bash|zsh|fish")
        for s, inst in {"bash": "source <(tbtools completion bash)",
                        "zsh": "tbtools completion zsh > ~/.zshrc",
                        "fish": "tbtools completion fish > ~/.config/fish/completions/tbtools.fish"}.items():
            click.echo(f"  {s:6s} {inst}")

# ---- 动态加载剩余命令 ----
# ---- 命令分类映射 ----
CATEGORY_MAP = {
    "sixframe": "seq",  # GUI 逆向：六框翻译
    "longestorf": "seq",  # GUI 逆向：最长 ORF 预测
    "protparam": "seq",  # GUI 逆向：蛋白理化性质
    "genomefilter": "seq",  # GUI 逆向：序列长度过滤
    "seqpattern": "seq",  # GUI 逆向：序列模式定位
    "bed2gff3": "gxf",  # GUI 逆向：BED→GFF3
    "careclassify": "seq",  # GUI 逆向：PlantCARE 元件分类
    "protsim": "seq",  # GUI 逆向：蛋白相似度矩阵
    "xml2blasttab": "blast", "xml2pairwise": "blast",  # GUI 逆向：BLAST XML 转换
    "fa2tab": "seq", "tab2fa": "seq",  # GUI 逆向：FASTA↔表
    "muscle": "seq",  # GUI 逆向：MUSCLE 比对（系统二进制）
    "trimal": "seq",  # GUI 逆向：trimAl 修剪
    "gblocks": "seq",  # GUI 逆向：Gblocks 修剪
    "bestid": "blast",  # GUI 逆向：最优 ID 转换
    "fasplit": "seq", "famerge": "seq",  # GUI 逆向：FASTA 拆/合
    "clearchar": "table",  # GUI 逆向：非法字符清理
    "getseqdb": "blast",  # GUI 逆向：BLAST 库提序列
    "gb2fa": "seq",  # GUI 逆向：GenBank→FASTA
    "findhomolog": "blast",  # GUI 逆向：最优同源
    "taxparse": "table",  # GUI 逆向：物种分类解析
    "srr2ena": "table",  # GUI 逆向：SRR→ENA 链接
    "sraxml2tab": "table",  # GUI 逆向：SRA XML→表
    "sranum2info": "table",  # GUI 逆向：SRR 信息表
    "blat": "blast",  # GUI 逆向：BLAT 比对
    "seqrecommend": "engine",  # GUI 逆向：测序量推荐
    "seqfetch": "seq",  # GUI 逆向：NCBI 序列下载
    "pubmed": "table",  # GUI 逆向：PubMed 检索
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
    "kaks": "tree",  # GUI 逆向：成对 Ka/Ks
    "subtree": "tree",  # GUI 逆向：子树提取
    "iqtree": "tree",  # GUI 逆向：IQ-TREE 建树
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
    "venn2": "sets", "venn3": "sets", "venn4": "sets",
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
    "goAnno": "table",  # GUI 逆向：GO 注释管道
    "goEnrich": "table", "keggEnrich": "table",
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
    "hmmExtract": "hmm", "hmmsearch": "hmm",
    "gxfAttr": "gxf", "gdensity": "gxf",
    "notung": "tree",
    "newickRename": "tree",
    "hmmerSearch": "hmm",
    "memeViz": "seq",
    "gsea": "table", "gbar": "expr", "golevel": "table", "sricher": "table",
    "tfbsShift": "seq",
    "kallisto": "expr",
    "mcscanxd": "syn",
    "qdot": "syn",
    "quickAnno": "blast",
    "smart": "seq",
    "fimo": "seq", "meme": "seq", "mast": "seq", "meme2tab": "seq", "makemotif": "seq", "mpattern": "seq",
    # GWAS
    "mimicVqsr": "gwas", "vcfAddID": "gwas",
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

def _load_auto_commands():
    """从 auto_commands.py 加载所有命令到对应分组（弥补 tbplot.sh 遗漏的命令）"""
    skip = {"seqlogo", "msa", "motif", "genestructure",  # seq manual
            "volcano", "heatmap2", "pca", "hclust", "dehist",  # expr manual
            "tree", "unrooted", "treeRooting", "onesteptree",  # tree manual
            "version", "doctor", "examples", "list", "presets",  # top commands
            "seq", "expr", "tool",  # group names
            "chipseq", "sets", "syn", "asm", "gxf", "mirna", "table",
            "blast", "fastq", "hmm", "gwas", "engine"}
    for name in sorted(dir(_ac)):
        if name.startswith('_') and name.endswith('_impl') and not name.startswith('__'):
            cmd = name[1:-5]
            if cmd in skip:
                continue
            cat = CATEGORY_MAP.get(cmd, "engine")
            target = _groups.get(cat)
            if target and cmd not in target.commands:
                _make_passthrough(cmd, target)

def _load_dynamic_commands():
    """从 tbplot.sh 动态生成 click 命令，按分类注册到 group"""
    import difflib
    import re
    tbplot_sh = os.path.join(ROOT, "bin", "tbplot.sh")
    if not os.path.isfile(tbplot_sh):
        return
    with open(tbplot_sh) as f:
        content = f.read()
    cmds = set(re.findall(r'^  ([a-zA-Z][a-zA-Z0-9]+)\)$', content, re.MULTILINE))
    # 已迁移命令的原始名（不动态转发）——用 tbplot.sh 里的原始命令名
    # 只排除真正有 @xxx.command 手动注册的命令 + group 名
    registered = {"seqlogo", "msa", "motif", "genestructure",  # seq
                  "volcano", "heatmap2", "pca", "hclust", "dehist",  # expr
                  "tree", "unrooted", "treeRooting", "onesteptree",  # tree
                  "version", "doctor", "examples", "seq", "expr", "tool",
                  "chipseq", "sets", "syn", "asm", "gxf", "mirna", "table",
                  "blast", "fastq", "hmm", "gwas", "engine"}
    for cmd_name in sorted(cmds - registered):
        cat = CATEGORY_MAP.get(cmd_name, "engine")
        _make_passthrough(cmd_name, _groups[cat])

    # 给所有分组加未知子命令纠错（ToolGroup/rpc 已有自己的 resolve_command）
    def _smart_resolve(self, ctx, args):
        try:
            return click.Group.resolve_command(self, ctx, args)
        except click.UsageError:
            if not args:
                raise
            name = args[0]
            cmds = list(self.commands.keys())
            # 前缀优先（venn2 案例：get_close_matches n=3 按相似度排序会挤掉正确建议）
            prefix_hits = [c for c in cmds if c.startswith(name)]
            close = prefix_hits[:5] or difflib.get_close_matches(name, cmds, n=3, cutoff=0.6)
            if close:
                click.echo(f"❌ '{name}' 不是 '{self.name}' 分组内的命令", err=True)
                click.echo(f"   你是不是想用: {' / '.join(close)}?", err=True)
            else:
                click.echo(f"❌ '{name}' 不是 '{self.name}' 分组内的命令", err=True)
                click.echo(f"   查看: tbtools {self.name} --help", err=True)
            ctx.exit(2)
    for gname, g in _groups.items():
        if gname in ("tool", "rpc"):
            continue
        if not hasattr(g, "resolve_command") or g.__class__.__name__ == "Group":
            g.resolve_command = _smart_resolve.__get__(g, type(g))

_META_JSON = None
def _load_meta_json():
    """懒加载 command_metadata.json（N33: 143 命令完整 help，含 150 可选位）"""
    global _META_JSON
    if _META_JSON is None:
        try:
            import json as _json
            _p = os.path.join(ROOT, "tbtools_cli", "command_metadata.json")
            _META_JSON = _json.load(open(_p, encoding="utf-8")) if os.path.isfile(_p) else {}
        except Exception:
            _META_JSON = {}
    return _META_JSON

def _parse_auto_metadata(name):
    """从 auto_commands.py 解析命令元数据（docstring + 坑位）"""
    impl = getattr(_ac, f'_{name}_impl', None)
    doc = (impl.__doc__ or "").strip() if impl else ""
    # N33: 优先 command_metadata.json 完整 help（含可选位；docstring 常被表驱动截断）
    _meta = _load_meta_json().get(name)
    if _meta and _meta.get("help"):
        usage = _meta["help"]
    elif ':' in doc:
        usage = doc.split(':', 1)[1].strip()
    else:
        usage = f"{name} [参数...]"
    pitfall = get_pitfall_hint(name)
    return {'impl': impl, 'usage': usage, 'pitfall': pitfall}

def _make_passthrough(name, group=None):
    """生成元数据驱动的 click 命令（help + 校验 + 预设 + 直调 Java）"""
    meta = _parse_auto_metadata(name)
    impl = meta['impl']
    usage = meta['usage']
    pitfall = meta['pitfall']
    
    help_text = usage
    if pitfall:
        help_text += f"\n\n⚠️ {pitfall}"
    
    _target = group or cli
    
    def _cmd_impl(ctx, verbose, quiet, fmt, preset, height, width, threads):
        args = list(ctx.args)
        
        # 输入校验：第一个非选项参数通常是输入文件（mcscanxd/kallisto 首参为工作目录/自定义路径，跳过校验）
        if args and not args[0].startswith('-') and name not in ("mcscanxd", "kallisto", "famerge", "getseqdb", "seqrecommend", "pubmed", "tableMerge", "generic"):
            ok, msg = validate_file(args[0], f"{name} 输入文件")
            if not ok:
                print(msg, file=sys.stderr)
                sys.exit(2)
            # C2: 早期格式不匹配警告（不阻断，仅提示）
            warn = check_input_format(name, args[0])
            if warn:
                print(f"⚠️ 格式提醒: {warn}", file=sys.stderr)
                print("   （继续执行；如确认无误可忽略）", file=sys.stderr)
        if preset:
            p = apply_preset(preset, width=width, height=height)
            if not p:
                print(f"❌ 未知预设: {preset}", file=sys.stderr)
                print(f"   可用: {', '.join(PRESETS.keys())}", file=sys.stderr)
                sys.exit(1)
            if 'width' in p and not width:
                width = p['width']
            if 'height' in p and not height:
                height = p['height']
        
        # 格式覆盖：替换输出文件扩展名
        if fmt:
            for i in range(len(args) - 1, -1, -1):
                if args[i].endswith(('.svg', '.png', '.pdf')):
                    base = os.path.splitext(args[i])[0]
                    args[i] = f"{base}.{fmt}"
                    break
        
        # 追加 width/height 到参数末尾（大多数命令接受 [w] [h] 位置参数）
        if width:
            args.append(str(width))
        if height:
            args.append(str(height))
        
        # 调用 impl 或回退到 bash tbplot.sh
        if impl:
            ec = impl(args, verbose=verbose, quiet=quiet)
        else:
            # 兜底走 bash tbplot.sh（Windows 需 Git Bash；无 bash 时报清晰错误）
            bash_bin = shutil.which("bash")
            if bash_bin:
                bash_args = [bash_bin, os.path.join(ROOT, "bin", "tbplot.sh"), name] + list(ctx.args)
                ec = subprocess.run(bash_args).returncode
            else:
                print(f"❌ {name} 需要 bash 兜底（tbplot.sh），但未找到 bash（Windows 请装 Git Bash）", file=sys.stderr)
                ec = 1
        sys.exit(ec)
    
    # 先设置 docstring，再装饰
    _cmd_impl.__doc__ = help_text
    _cmd_impl = click.pass_context(_cmd_impl)
    for opt_args, opt_kwargs in [
        (("--verbose", "-V"), {"is_flag": True, "default": False, "help": "显示完整堆栈"}),
        (("--quiet", "-q"), {"is_flag": True, "default": False, "help": "静默模式"}),
        (("--format", "-f", "fmt"), {"default": None, "help": "输出格式: svg|png|pdf"}),
        (("--preset", "-p"), {"default": None, "help": "出版预设: nature|cell|plant_journal|wide|poster"}),
        (("--height", "-H"), {"type": int, "default": None, "help": "画布高度"}),
        (("--width", "-W"), {"type": int, "default": None, "help": "画布宽度"}),
        (("--threads", "-t"), {"type": int, "default": None, "help": "线程数"}),
    ]:
        _cmd_impl = click.option(*opt_args, **opt_kwargs)(_cmd_impl)
    
    # 提取 click.option 装饰器注册的参数（__click_params__）
    params = getattr(_cmd_impl, '__click_params__', [])
    params = params[::-1]  # click 处理顺序是反的
    
    cmd = click.Command(name=name, callback=_cmd_impl, params=params,
        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
        help=help_text)
    _target.add_command(cmd)


@cli.command(name='list')
@click.argument('category', required=False)
def listing(category):
    """列出可用命令（plots/tools/rpc）——TTY 下自动分页"""
    lines = []
    if not category or category == 'plots':
        lines.append(c("绘图/分析命令：", "bold"))
        for gname in sorted(GROUPS.keys()):
            g = _groups.get(gname)
            if g and g.commands:
                lines.append(f"\n  {c(gname, 'cyan', bold=True)} — {GROUPS[gname]}")
                for cname, cmd in sorted(g.commands.items()):
                    short = (cmd.help or '').split('\n')[0][:60]
                    lines.append(f"    {c(f'{cname:20s}', 'green')} {short}")
        if not category:
            lines.append("\n用法: tbtools list tools|rpc")
    elif category == 'tools':
        lines.append("命令行工具：")
        # 排除绘图类命令（属于 seq/expr/tree/syn/sets/chipseq 分组的）
        plot_groups = {'seq', 'expr', 'tree', 'syn', 'sets', 'chipseq'}
        # V1 §3 P3-9: 插件工具在绘图分组但实为命令行工具，强制显示（kallisto/fimo 等）
        plugin_tools = {"kallisto", "memeViz", "qdot", "tfbsShift", "smart", "fimo",
                       "mcscanxd", "notung", "quickAnno", "hmmerSearch", "gsea", "meme", "mast"}
        count = 0
        for n in sorted(dir(_ac)):
            if n.startswith('_') and n.endswith('_impl') and not n.startswith('__'):
                cmd = n[1:-5]
                cat = CATEGORY_MAP.get(cmd, 'engine')
                if cat in plot_groups and cmd not in plugin_tools:
                    continue  # 跳过绘图类（插件工具除外）
                doc = getattr(_ac, n).__doc__ or ''
                short = doc.split(':',1)[1].strip()[:60] if ':' in doc else ''
                lines.append(f"  {cmd:20s} {short}")
                count += 1
        # 加上共享注册表（P0-3：82 个 CLI 工具，排除已被 _impl 覆盖的）
        reg_count = 0
        for tname in sorted(CLI_TOOLS):
            if getattr(_ac, f'_{tname}_impl', None):
                continue  # 已在上面列出
            lines.append(f"  {tname:20s} {CLI_TOOLS[tname].split('.')[-1]}")
            reg_count += 1
        # 加上手动注册的 3 个
        lines.append(f"\n共 {count + reg_count + 3} 个工具（含 {reg_count} 个注册表工具 + 3 个手动迁移）")
    elif category == 'rpc':
        lines.append("RPC 方法（188 个），启动 RPC 服务器后可用：")
        lines.append("  tbtools_rpc.sh start    # 启动")
        lines.append("  tbtools_rpc.sh methods   # 列出全部 188 方法")
        lines.append("  tbtools_rpc.sh call <method> '<json>'")
    else:
        click.echo(f"未知类别: {category}。可用: plots|tools|rpc", err=True)
        sys.exit(1)
    # 输出：TTY 且行数多 → pager；否则直接打印（管道/重定向可 grep）
    text = "\n".join(lines)
    is_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    if is_tty and len(lines) > 20:
        click.echo_via_pager(text)
    else:
        click.echo(text)

@cli.command()
@click.argument("name", required=False)
def presets(name):
    """列出或查看出版预设"""
    if name:
        p = PRESETS.get(name)
        if not p:
            click.echo(f"❌ 未知预设: {name}")
            click.echo(f"   可用: {', '.join(PRESETS.keys())}")
            sys.exit(1)
        click.echo(f"\n  预设: {name}")
        click.echo(f"  描述: {p['desc']}")
        for k, v in p.items():
            if k != 'desc':
                click.echo(f"  {k}: {v}")
    else:
        click.echo("出版级预设模板")
        click.echo("用法: tbtools <命令> ... --preset <名称>\n")
        for n, d in list_presets():
            click.echo(f"  {n:20s} {d}")

# ---- new 交互式向导 ----
@cli.command()
@click.option("--list", "list_only", is_flag=True, help="只列出场景，不交互")
@click.option("--run", "run_it", is_flag=True, help="生成后直接执行")
def new(list_only, run_it):
    """交互式向导：按「想做什么」生成命令"""
    from tbtools_cli.scenarios import SCENARIOS, _categories
    if list_only:
        click.echo("可用的场景（tbtools new 交互式选择）：")
        for cat, scens in _categories.items():
            click.echo(f"\n  [{cat}]")
            for s in scens:
                sc = SCENARIOS[s]
                click.echo(f"    {s:22s} → tbtools {sc['group']} {sc['cmd']}")
        return
    # 非 TTY 的 stdin：拒绝（引导 --list）——但允许显式测试/管道注入
    if not (hasattr(sys.stdin, "isatty") and sys.stdin.isatty()):
        # 检查 stdin 是否有数据（管道注入）
        try:
            import select
            if select.select([sys.stdin], [], [], 0)[0]:
                pass  # 有管道输入，允许
            else:
                raise Exception("no input")
        except Exception:
            click.echo("交互式向导需要终端。\n  tbtools new --list    # 查看全部场景\n  tbtools help <命令>   # 查看用法", err=True)
            sys.exit(1)
    _run_new_wizard(_categories, SCENARIOS, run_it)


def _wiz_prompt(text, *a, **kw):
    """click.prompt 封装，EOF/非交互时友好退出"""
    try:
        return click.prompt(text, *a, **kw)
    except (EOFError, KeyboardInterrupt, click.Abort):
        click.echo("（已取消，未生成命令）", err=True)
        sys.exit(130)


def _run_new_wizard(_categories, SCENARIOS, run_it=False):
    """执行向导：选类别 → 选场景 → 填参数 → 出命令"""
    # 1. 选类别
    cats = list(_categories.keys())
    click.echo("\n🧭 你想做什么？（选一个类型）")
    for i, cat in enumerate(cats, 1):
        click.echo(f"  {i}. {cat}")
    cat_idx = _wiz_prompt("\n选择 [1-%d]" % len(cats), type=click.IntRange(1, len(cats)), default=1)
    cat = cats[cat_idx - 1]

    # 2. 选场景
    scens = _categories[cat]
    click.echo(f"\n📂 [{cat}] 具体场景：")
    for i, s in enumerate(scens, 1):
        sc = SCENARIOS[s]
        click.echo(f"  {i}. {s}\n      {sc['desc']}")
    sc_idx = _wiz_prompt("\n选择 [1-%d]" % len(scens), type=click.IntRange(1, len(scens)), default=1)
    scen = SCENARIOS[scens[sc_idx - 1]]

    # 3. 填参数（交互）
    click.echo(f"\n🔧 命令: tbtools {scen['group']} {scen['cmd']}")
    click.echo(f"   用法: {scen['usage']}\n")
    parts = [scen['cmd']]
    if scen['args']:
        click.echo("填参数（直接回车用默认/跳过，可稍后改）:")
        for label, default in scen['args']:
            p = _wiz_prompt(f"  {label}", default=default if default else None, show_default=False)
            p = (p or "").strip()
            if p:
                parts.append(p)
    else:
        click.echo("（此命令无需位置参数，请用 --help 看选项）")

    # 4. 展示最终命令
    cmd_str = f"tbtools {scen['group']} " + " ".join(parts)
    click.echo("\n✅ 生成命令:")
    click.echo(f"  {cmd_str}")
    # 坑位
    pit = get_pitfall_hint(scen['cmd'])
    if pit:
        click.echo(f"\n  ⚠️ 坑位: {pit}")
    if run_it:
        click.echo("\n🚀 正在执行...")
        # 剥离前面的 'tbtools' 并调用相应分组命令
        argv = cmd_str.split()[1:]  # 去 tbtools，剩 [group, args...]
        sys.exit(cli.main(argv, standalone_mode=False) or 0)
    click.echo(f"\n  复制后运行，或：\n    直接运行: tbtools {scen['group']} {scen['cmd']} --help")


# ---- check 格式探测器 ----
@cli.command()
@click.argument('files', nargs=-1, required=True)
def check(files):
    """探测文件格式：tbtools check <文件...>（FASTA/GFF/Newick/XML/TSV）"""
    import json as _json
    bad = 0  # N20: check 对不存在的文件报错后应非零退出
    for path in files:
        ok, msg = validate_file(path, "文件")
        if not ok:
            click.echo(msg, err=True)
            bad += 1
            continue
        fmt, ncols, sample = detect_format(path)
        import os as _os
        size = _os.path.getsize(path)
        with open(path, 'rb') as fh:
            head = fh.read(4)
        gz = head[:2] == b'\x1f\x8b'
        lines = sum(1 for _ in open(path, 'r', errors='replace')) if size < 50_000_000 else None
        click.echo(f"\n📄 {path}")
        click.echo(f"   格式: {fmt}{'+gzip' if gz else ''}   大小: {size:,}B" + (f"   行数: {lines:,}" if lines is not None else ""))
        if ncols:
            click.echo(f"   列数: {ncols}")
        for s in sample[:2]:
            disp = s if len(s) <= 90 else s[:87] + "..."
            click.echo(f"   样例: {disp}")
        if _json.dumps(sample[:1], ensure_ascii=False) and fmt == "unknown":
            click.echo("   （无法识别格式；如是表格确认分隔符是 Tab 还是逗号）")
    if bad:
        sys.exit(1)

_load_dynamic_commands()
_load_auto_commands()


# 旧名别名（README/老用户兼容，顶层/分组均可用）——须在 cli() 前注册
seq_group.add_command(seqlogo, name="seqlogo")
expr_group.add_command(heatmap, name="heatmap2")
if __name__ == "__main__":
    cli()
