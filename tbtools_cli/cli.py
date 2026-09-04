"""tbtools-cli 主入口 — Python click 重构版"""
import click
import os, sys, subprocess

# ---- 配置 ----
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tbtools_cli.core import (JAR, run_java, run_plot, ensure_bridge,
    resolve_output, ROOT, validate_file, detect_format, get_pitfall_hint)
from tbtools_cli.presets import apply_preset, list_presets, PRESETS
import tbtools_cli.auto_commands as _ac

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
            # 检查是否是某个分组内的子命令
            for gname, g in _groups.items():
                if name in g.commands:
                    click.echo(f"❌ '{name}' 不是顶层命令，它在 '{gname}' 分组内", err=True)
                    click.echo(f"   正确用法: tbtools {gname} {name} ...", err=True)
                    doc = g.commands[name].help or ''
                    if doc:
                        first = doc.strip().split('\n')[0]
                        click.echo(f"   说明: {first}", err=True)
                    ctx.exit(2)
            # 拼写纠错（对分组名+顶层命令）
            import difflib
            candidates = sorted(set(list(_groups.keys()) + [c for c in cli.commands.keys()]))
            close = difflib.get_close_matches(name, candidates, n=3, cutoff=0.6)
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
    """TBtools-II 全功能 CLI — 143 绘图命令 + 130 工具 + 188 RPC"""
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
def seqlogo(input_file, output_file, scale_ic, show_pos, verbose, quiet, fmt, preset, height, width, threads):
    """序列 LOGO 图"""
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
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("MSACli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
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
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("GeneStructureCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "GeneStructureCli", gff_file, id_list, output_file]
    if genome:
        args += [genome]
    if width: args += [str(width)]
    if height: args += [str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="structure")
    sys.exit(ec)

@seq_group.command("motif")
@click.argument("meme_xml")
@click.argument("id_list")
@click.argument("output_file")
@common_options
def seq_motif(meme_xml, id_list, output_file, verbose, quiet, fmt, preset, height, width, threads):
    """Motif 分布图（MEME XML）"""
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("MotifCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "MotifCli", meme_xml, id_list, output_file]
    if width: args += [str(width)]
    if height: args += [str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="motif")
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
def volcano(deg_file, output_file, pval_cutoff, fc_cutoff, verbose, quiet, fmt, preset, height, width, threads):
    """火山图（DEG: GeneID Log2FC pvalue）"""
    if preset:
        p = apply_preset(preset, width=width, height=height)
        if not p: print(f"❌ 未知预设: {preset}", file=sys.stderr); sys.exit(1)
        if 'width' in p and not width: width = p['width']
        if 'height' in p and not height: height = p['height']
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
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("GenericCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
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
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("HclustCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "HclustCli", distance_file, output_file]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="hclust")
    sys.exit(ec)

@expr_group.command("dehist")
@click.argument("deg_file")
@click.argument("output_file")
@common_options
def expr_dehist(deg_file, output_file, verbose, quiet, fmt, preset, height, width, threads):
    """差异表达双直方图"""
    output_file = resolve_output(output_file, fmt)
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioDoer.JIGplotToolkit.DiffExp.DualHistPlot.DiffExpDualHistPlot",
            deg_file, output_file]
    if width: args += [str(width)]
    if height: args += [str(height)]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="dehist")
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
def tree_draw(config_file, output_file, verbose, quiet, fmt, preset, height, width, threads):
    """树+注释图（TreeTreeTree 多轨道）"""
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("TreeCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
            "TreeCli", config_file, output_file]
    ec = run_plot(args, verbose=verbose, quiet=quiet, command_name="draw")
    sys.exit(ec)

@tree_group.command("unrooted")
@click.argument("newick_file")
@click.argument("output_file")
@common_options
def tree_unrooted(newick_file, output_file, verbose, quiet, fmt, preset, height, width, threads):
    """无根树可视化"""
    output_file = resolve_output(output_file, fmt)
    ensure_bridge("UnrootedTreeCli")
    args = ["java", "-Xmx3g", "-cp", f"{os.path.join(ROOT, 'build')}:{JAR}",
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
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioDoer.JIGplotToolkit.newickParser.TreeTreeTree.TreeRootingByMAD",
            input_nwk, output_nwk]
    ec = run_java(args, verbose=verbose, quiet=quiet, command_name="rooting")
    sys.exit(ec)

@tree_group.command("one-step")
@click.argument("pep_fasta")
@click.argument("output_prefix")
@click.option("--bb-time", "-b", type=int, default=1000, help="IQ-TREE bootstrap iterations")
@common_options
def tree_onesteptree(pep_fasta, output_prefix, bb_time, verbose, quiet, fmt, preset, height, width, threads):
    """一步法 ML 树（muscle → trimal → IQ-TREE）"""
    t = threads or 4
    args = ["java", "-Xmx4g", "-cp", JAR,
            "biocjava.bioDoer.JIGplotToolkit.Phylogenetics.OneStepTree",
            "--inPepFie", pep_fasta, "--outFilePrefix", output_prefix,
            "--bbTime", str(bb_time), "--threads", str(t)]
    ec = run_java(args, verbose=verbose, quiet=quiet, command_name="onesteptree")
    sys.exit(ec)

# ---- 命令组：工具 ----
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
                    cmd = click.Command(name=name,
                        callback=lambda: sys.exit(impl(list(ctx.args))),
                        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
                        help=help_text)
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
    pass

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
        output_file = "/dev/stdout"
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
    if output_file == "-": output_file = "/dev/stdout"
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioDoer.JIGplotToolkit.Protein.CdsToProtein",
            cds_fasta, output_file]
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
    if output_file == "-": output_file = "/dev/stdout"
    args = ["java", "-Xmx2g", "-cp", JAR,
            "biocjava.bioIO.FastX.FastaIndex.ExtractFasta",
            input_fasta, id_list, output_file]
    ec = run_java(args, verbose=verbose, quiet=quiet, command_name="fasta_extract")
    sys.exit(ec)

# ---- 通用命令 ----
@cli.command()
def version():
    """显示版本信息"""
    # 动态统计
    plot_count = sum(len(g.commands) for g in _groups.values())
    auto_count = sum(1 for n in dir(_ac) if n.startswith('_') and n.endswith('_impl') and not n.startswith('__'))
    from tbtools_cli.core import PITFALL_HINTS, BRIDGES_DIR
    bridge_count = len([f for f in os.listdir(BRIDGES_DIR) if f.endswith('.java')]) if os.path.isdir(BRIDGES_DIR) else 80
    click.echo(f"tbtools-cli v1.0.0")
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
@click.argument('name')
def help(name):
    """快捷帮助: tbtools help <命令名> 自动定位"""
    # 尝试在所有分组中查找
    for gname, g in _groups.items():
        if name in g.commands:
            cmd = g.commands[name]
            click.echo(f"\n  命令: {gname} {name}")
            click.echo(f"  分组: {gname}")
            if cmd.help:
                click.echo(f"\n{cmd.help}")
            return
    # 顶层命令
    if name in cli.commands:
        cmd = cli.commands[name]
        if cmd.help:
            click.echo(f"\n{cmd.help}")
        return
    click.echo(f"❌ 未找到命令: {name}")
    click.echo(f"   查看: tbtools list")
    sys.exit(1)

@cli.group('rpc')
def rpc_group():
    """RPC 服务器管理（188 方法）"""
    pass

@rpc_group.command('start')
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
@click.option('--mem', '-m', default='4g', help='Java 堆内存')
def rpc_start(port, mem):
    """启动 RPC 服务器"""
    import subprocess
    args = ["java", f"-Xmx{mem}", "-cp", JAR, "biocjava.rpc.RpcServer"]
    click.echo(f"启动 RPC 服务器（端口 {port}）...")
    try:
        proc = subprocess.Popen(args, stdout=sys.stdout, stderr=sys.stderr)
        click.echo(f"RPC PID: {proc.pid}")
        click.echo(f"测试: curl -X POST http://127.0.0.1:{port}/rpc -H 'Content-Type: application/json' -d '{{\"method\":\"system.listMethods\",\"params\":[],\"id\":1}}'")
    except FileNotFoundError:
        click.echo("❌ Java 未安装", err=True)
        sys.exit(1)

@rpc_group.command('methods')
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
def rpc_methods(port):
    """列出全部 188 RPC 方法"""
    import json, urllib.request
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/rpc",
            data=json.dumps({"method": "system.listMethods", "params": [], "id": 1}).encode(),
            headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=5)
        result = json.loads(resp.read())
        methods = result.get('result', [])
        click.echo(f"RPC 方法（{len(methods)} 个）：")
        for m in methods:
            click.echo(f"  {m}")
    except Exception as e:
        click.echo(f"❌ RPC 服务器未启动或连接失败: {e}", err=True)
        click.echo("   启动: tbtools rpc start")
        sys.exit(1)

@rpc_group.command('call')
@click.argument('method')
@click.argument('params', required=False)
@click.option('--port', '-p', type=int, default=8765, help='RPC 端口')
def rpc_call(method, params, port):
    """调用 RPC 方法"""
    import json, urllib.request
    params_list = json.loads(params) if params else []
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/rpc",
            data=json.dumps({"method": method, "params": params_list, "id": 1}).encode(),
            headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        if 'error' in result and result['error']:
            click.echo(f"❌ RPC 错误: {result['error']}", err=True)
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

@cli.command()
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

def _load_auto_commands():
    """从 auto_commands.py 加载所有命令到对应分组（弥补 tbplot.sh 遗漏的命令）"""
    skip = {"seqlogo", "msa", "motif", "genestructure",  # seq manual
            "volcano", "heatmap2", "pca", "hclust", "dehist",  # expr manual
            "tree", "unrooted", "treeRooting", "onesteptree",  # tree manual
            "version", "doctor", "examples", "list", "presets",  # top commands
            "seq", "expr", "tree", "tool",  # group names
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
    import re, difflib
    tbplot_sh = os.path.join(ROOT, "bin", "tbplot.sh")
    if not os.path.isfile(tbplot_sh):
        return
    with open(tbplot_sh) as f:
        content = f.read()
    cmds = set(re.findall(r'^  ([a-zA-Z][a-zA-Z0-9]+)\)$', content, re.M))
    # 已迁移命令的原始名（不动态转发）——用 tbplot.sh 里的原始命令名
    # 只排除真正有 @xxx.command 手动注册的命令 + group 名
    registered = {"seqlogo", "msa", "motif", "genestructure",  # seq
                  "volcano", "heatmap2", "pca", "hclust", "dehist",  # expr
                  "tree", "unrooted", "treeRooting", "onesteptree",  # tree
                  "version", "doctor", "examples", "seq", "expr", "tree", "tool",
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
            close = difflib.get_close_matches(name, list(self.commands.keys()), n=3, cutoff=0.6)
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

def _parse_auto_metadata(name):
    """从 auto_commands.py 解析命令元数据（docstring + 坑位）"""
    impl = getattr(_ac, f'_{name}_impl', None)
    doc = (impl.__doc__ or "").strip() if impl else ""
    usage = doc.split(':', 1)[1].strip() if ':' in doc else f"{name} [参数...]"
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
        
        # 输入校验：第一个非选项参数通常是输入文件
        if args and not args[0].startswith('-'):
            ok, msg = validate_file(args[0], f"{name} 输入文件")
            if not ok:
                print(msg, file=sys.stderr)
                sys.exit(2)
        
        # 应用预设
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
            bash_args = ["bash", os.path.join(ROOT, "bin", "tbplot.sh"), name] + list(ctx.args)
            ec = subprocess.run(bash_args).returncode
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
    """列出可用命令（plots/tools/rpc）"""
    if not category or category == 'plots':
        click.echo("绘图/分析命令：")
        for gname in sorted(GROUPS.keys()):
            g = _groups.get(gname)
            if g and g.commands:
                click.echo(f"\n  {gname} — {GROUPS[gname]}")
                for cname, cmd in sorted(g.commands.items()):
                    short = (cmd.help or '').split('\n')[0][:60]
                    click.echo(f"    {cname:20s} {short}")
        if not category:
            click.echo("\n用法: tbtools list tools|rpc")
    elif category == 'tools':
        click.echo("命令行工具：")
        # 排除绘图类命令（属于 seq/expr/tree/syn/sets/chipseq 分组的）
        plot_groups = {'seq', 'expr', 'tree', 'syn', 'sets', 'chipseq'}
        count = 0
        for n in sorted(dir(_ac)):
            if n.startswith('_') and n.endswith('_impl') and not n.startswith('__'):
                cmd = n[1:-5]
                cat = CATEGORY_MAP.get(cmd, 'engine')
                if cat in plot_groups:
                    continue  # 跳过绘图类
                doc = getattr(_ac, n).__doc__ or ''
                short = doc.split(':',1)[1].strip()[:60] if ':' in doc else ''
                click.echo(f"  {cmd:20s} {short}")
                count += 1
        # 加上手动注册的 3 个
        click.echo(f"\n共 {count + 3} 个工具（含 3 个手动迁移）")
    elif category == 'rpc':
        click.echo("RPC 方法（188 个），启动 RPC 服务器后可用：")
        click.echo("  tbtools_rpc.sh start    # 启动")
        click.echo("  tbtools_rpc.sh methods   # 列出全部 188 方法")
        click.echo("  tbtools_rpc.sh call <method> '<json>'")
    else:
        click.echo(f"未知类别: {category}。可用: plots|tools|rpc")
        sys.exit(1)

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

_load_dynamic_commands()
_load_auto_commands()

if __name__ == "__main__":
    cli()
