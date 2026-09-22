"""cli_top.py — 顶层命令（架构重构批次 B：从 cli.py 拆分）

version/doctor/setup/fetch_jar/help/examples/completion/list/presets/new/check。
由 cli.py 以 register_top(cli, cli_load) 注册。
"""
import os
import subprocess
import sys

import click

from tbtools_cli import auto_commands as _ac
from tbtools_cli.cli_tools_registry import CLI_TOOLS
from tbtools_cli.core import (
    JAR,
    ROOT,
    c,
    detect_format,
    get_pitfall_hint,
    safe_temp,
    validate_file,
)
from tbtools_cli.presets import PRESETS, list_presets


def register_top(cli, _LG):
    """注册顶层命令。cli=主 CLI group；_LG=cli_load 模块（提供 _groups/GROUPS/CATEGORY_MAP）。"""
    # ---- 通用命令 ----
    @cli.command()
    @click.option("--json", "as_json", is_flag=True, help="输出结构化统计(JSON, 供脚本/Agent 使用)")
    def version(as_json):
        """显示版本与命令统计(权威数字; --json 输出结构化)"""
        import json as _json
        # 动态统计(数量哲学统一: 唯一统计 API, README/badge/文档口径均以此为准)
        plot_count = sum(len(g.commands) for g in _LG._groups.values())
        auto_count = sum(1 for n in dir(_ac) if n.startswith('_') and n.endswith('_impl') and not n.startswith('__'))
        from tbtools_cli.core import BRIDGES_DIR, PITFALL_HINTS
        bridge_count = len([f for f in os.listdir(BRIDGES_DIR) if f.endswith('.java')]) if os.path.isdir(BRIDGES_DIR) else 80
        from tbtools_cli import __version__ as _pkg_ver
        if as_json:
            click.echo(_json.dumps({
                "version": _pkg_ver,
                "cli_commands": plot_count,
                "auto_commands": auto_count,
                "rpc_methods": 188,
                "tools": len(CLI_TOOLS),
                "bridges": bridge_count,
                "pitfall_hints": len(PITFALL_HINTS),
                "metadata_commands": len(_json.load(open(os.path.join(ROOT, "tbtools_cli", "command_metadata.json"), encoding="utf-8"))) if os.path.isfile(os.path.join(ROOT, "tbtools_cli", "command_metadata.json")) else 0,
            }, ensure_ascii=False, indent=1))
            return
        click.echo(f"tbtools-cli v{_pkg_ver}")
        click.echo(f"  {plot_count} 绘图/分析命令 + {auto_count} auto_commands + 188 RPC 方法")
        click.echo(f"  bridges: {bridge_count} | pitfall hints: {len(PITFALL_HINTS)}")
        # P0(第七轮评审实测): 无 Java 环境不能崩——version 是新人第一条命令
        try:
            r = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=5)
            java_ver = r.stderr.splitlines()[0] if r.stderr else "unknown"
        except FileNotFoundError:
            java_ver = "❌ 未安装(apt install openjdk-17-jre-headless)"
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
        fix_cmds = {
            "java": "sudo apt install -y openjdk-17-jre-headless",
            "javac": "sudo apt install -y openjdk-17-jdk-headless",
            "xvfb-run": "sudo apt install -y xvfb",
        }
        for cmd_name, desc, required in checks:
            if shutil.which(cmd_name):
                click.echo(f"  ✅ {desc}: 可用")
                ok += 1
            elif required:
                click.echo(f"  ❌ {desc}: 未安装")
                if cmd_name in fix_cmds:
                    click.echo(f"      📋 复制即用: {fix_cmds[cmd_name]}")
                err += 1
            else:
                click.echo(f"  ⚠️ {desc}: 未安装")
                warn += 1
        if JAR and os.path.isfile(JAR):
            size_mb = os.path.getsize(JAR) / 1024 / 1024
            click.echo(f"  ✅ JAR: {JAR} ({size_mb:.0f}MB)")
            ok += 1
            # G5: 死命令探测（jar 版本与 CLI 注册类不匹配预警,外部测试 P1-1）
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

        # 平台能力矩阵（第三轮审查：让用户第一分钟知道能力边界）
        click.echo("\n  ── 平台能力矩阵 ──")
        is_win = sys.platform.startswith("win")
        have_xvfb = shutil.which("xvfb-run") is not None
        jar_ready = bool(JAR) and os.path.isfile(JAR)
        click.echo(f"  工具类命令        {'✅' if jar_ready else '❌'}")
        click.echo(f"  RPC 数据工具      {'✅' if jar_ready else '❌'}")
        click.echo(f"  绘图（SVG）       {'✅' if (not is_win or have_xvfb) and jar_ready else '⚠️ Windows 无 xvfb 部分受限 / JAR 缺失'}")
        click.echo(f"  管道 stdin/stdout {'⚠️ 仅部分 tool 层'}")
        click.echo("  （Linux 绘图需 xvfb;Windows 限制见 README Known Limitations）")

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
        tmp = safe_temp(suffix=".zip")
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
        for gname, g in _LG._groups.items():
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
                    from tbtools_cli.auto_commands import EXAMPLES  # type: ignore[attr-defined]  # 可选属性,hasattr 兜底
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
                for gname in _LG._groups:
                    for cname in _LG._groups[gname].commands:
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

    @cli.command(name="search")
    @click.argument("keyword", required=True)
    def search_cmd(keyword):
        """模糊搜索命令（匹配名称+doc，276 命令可发现性）: tbtools search <关键词>"""
        import json as _json
        meta_path = os.path.join(ROOT, "tbtools_cli", "command_metadata.json")
        if not os.path.isfile(meta_path):
            click.echo(f"❌ 元数据缺失: {meta_path}", err=True)
            sys.exit(1)
        meta = _json.load(open(meta_path, encoding="utf-8"))
        kw = keyword.lower()
        hits = []
        for name, v in meta.items():
            help_txt = (v.get("help", "") or "")[:200].lower()
            if kw in name.lower() or kw in help_txt:
                cat = _LG.CATEGORY_MAP.get(name, "engine")
                kind = v.get("kind", "?")
                desc = (v.get("help", "") or "").split("#")[-1].strip()[:60]
                hits.append((name, cat, kind, desc))
        if not hits:
            click.echo(f"❌ 没有匹配 '{keyword}' 的命令。试试: tbtools list")
            sys.exit(1)
        click.echo(f"🔍 匹配 '{keyword}' 的命令（{len(hits)} 个）:")
        for name, cat, kind, desc in sorted(hits):
            click.echo(f"  {name:24s} [{cat}/{kind}] {desc}")
        click.echo("\n查看详情: tbtools help <命令> | 全量: tbtools list")

    @cli.command(name='list')
    @click.argument('category', required=False)
    def listing(category):
        """列出可用命令（plots/tools/rpc）——TTY 下自动分页"""
        lines = []
        if not category or category == 'plots':
            lines.append(c("绘图/分析命令：", "bold"))
            for gname in sorted(_LG.GROUPS.keys()):
                g = _LG._groups.get(gname)
                if g and g.commands:
                    lines.append(f"\n  {c(gname, 'cyan', bold=True)} — {_LG.GROUPS[gname]}")
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
                    cat = _LG.CATEGORY_MAP.get(cmd, 'engine')
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
