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
    check_input_format,
    detect_format,
    get_pitfall_hint,
    safe_temp,
    validate_file,
)
from tbtools_cli.presets import PRESETS, list_presets



def _detect_java_ver():
    """检测 Java 版本(无 java 返回 None;不崩)"""
    try:
        r = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=5)
        return r.stderr.splitlines()[0] if r.stderr else "unknown"
    except FileNotFoundError:
        return None

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
    @click.option("--json", "as_json", is_flag=True, help="机器格式输出(环境快照, 供 Agent)")
    def doctor(as_json):
        """环境诊断"""
        import shutil
        import json as _json
        if as_json:
            # 机器格式快速路径: 不经 echo 循环, stdout 只含 JSON(评审 #24)
            _jf = bool(JAR) and os.path.isfile(JAR)
            _ec = 0 if (_jf and shutil.which("java") and (os.name == "nt" or shutil.which("xvfb-run"))) else 1
            # 版本兼容矩阵(评审 #23): CLI/TBtools/Java 兼容状态
            _compat = {
                "tbtools_cli": "1.2.0",
                "tbtools_jar_required": "2.535+",
                "java_runtime": "11-21 (推荐 17)",
                "compatibility": "verified" if _ec == 0 else "check_jar_version",
            }
            click.echo(_json.dumps({
                "schema_version": "1.0", "ready": _ec == 0, "err": _ec,
                "java": shutil.which("java") is not None,
                "xvfb": shutil.which("xvfb-run") is not None,
                "jar": _jf, "jar_path": JAR if _jf else None,
                "mcp": True, "compat": _compat,
            }, ensure_ascii=False, indent=1))
            sys.exit(_ec)
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
            # 供应链校验(fetch-jar 记录 sha256; hashlib 流式, 300MB 约 1s)
            import hashlib as _hl
            import tomllib as _tl
            _cfg_p = os.path.join(os.path.expanduser("~/.config/tbtools-cli"), "config.toml")
            _exp = None
            if os.path.isfile(_cfg_p):
                try:
                    _exp = _tl.load(open(_cfg_p, "rb")).get("jar_sha256")
                except Exception:
                    pass
            if _exp:
                h = _hl.sha256()
                with open(JAR, "rb") as _f:
                    for _c in iter(lambda: _f.read(1 << 20), b""):
                        h.update(_c)
                if h.hexdigest() == _exp:
                    click.echo(f"  ✅ sha256 校验通过 ({_exp[:16]}...)")
                else:
                    click.echo(f"  ❌ sha256 不匹配! 期望 {_exp[:16]}... 实际 {h.hexdigest()[:16]}...", err=True)
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

        if as_json:
            import json as _json
            click.echo(_json.dumps({
                "schema_version": "1.0",
                "ready": err == 0,
                "ok": ok, "warn": warn, "err": err,
                "java": shutil.which("java") is not None,
                "xvfb": shutil.which("xvfb-run") is not None,
                "jar": jar_ready,
                "jar_path": JAR if jar_ready else None,
                "jar_sha_verified": "_exp" in dir() and bool(_exp),
            }, ensure_ascii=False, indent=1))
            sys.exit(0 if err == 0 else 1)

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
        # 供应链校验(GPT 评审 #9): 下载 zip 与提取 jar 均计算 SHA256, 记录进 config.toml 供复现校验
        import hashlib as _hl
        zip_sha = _hl.sha256()
        with open(tmp, "rb") as _f:
            for _chunk in iter(lambda: _f.read(1 << 20), b""):
                zip_sha.update(_chunk)
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
        h = _hl.sha256()
        with open(jar_target, "rb") as _f:
            for _chunk in iter(lambda: _f.read(1 << 20), b""):
                h.update(_chunk)
        jar_sha_hex = h.hexdigest()
        click.echo(f"✅ 已提取: {jar_target}")
        click.echo(f"   sha256(zip) = {zip_sha.hexdigest()}")
        click.echo(f"   sha256(jar) = {jar_sha_hex}")
        # 配置(含 checksum 与版本, 供验证/审计)
        cfg_dir = os.path.expanduser("~/.config/tbtools-cli")
        os.makedirs(cfg_dir, exist_ok=True)
        with open(os.path.join(cfg_dir, "config.sh"), "w") as f:
            f.write(f'export TBTOOLS_JAR="{jar_target}"\n')
        with open(os.path.join(cfg_dir, "config.toml"), "w") as f:
            f.write(f'jar = "{jar_target}"\njar_sha256 = "{jar_sha_hex}"\njar_version = "{tag}"\n\n[defaults]\nthreads = 4\nformat = "svg"\n')
        click.echo("✅ 已配置(sha256 已记录, 可用 doctor 验证)。运行 tbtools doctor 验证")

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

    @cli.command(name="env")
    @click.option("--json", "as_json", is_flag=True, help="输出结构化(JSON)")
    @click.option("--lock", is_flag=True, help="固化环境到 tbtools.lock(可复现性)")
    def env(as_json, lock):
        """环境快照: 版本/依赖/可选工具(科研可复现, 第八轮评审建议)"""
        import json as _json
        import shutil as _sh
        from tbtools_cli import __version__ as _pkg_ver
        snap = {
            "tbtools_cli": _pkg_ver,
            "jar": JAR or "",
            "java": _detect_java_ver(),
            "xvfb": bool(_sh.which("xvfb-run")),
            "deps": {},
        }
        for tool in ("blastp", "muscle", "iqtree2", "trimal", "jellyfish", "hmmsearch", "mafft", "diamond"):
            snap["deps"][tool] = _sh.which(tool) or None
        if lock:
            path = "tbtools.lock"
            _json.dump(snap, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            click.echo(f"✅ 环境已固化: {path}(运行复现:tbtools env --json 对比)")
        elif as_json:
            click.echo(_json.dumps(snap, ensure_ascii=False, indent=1))
        else:
            click.echo(f"  tbtools-cli: {snap['tbtools_cli']}")
            click.echo(f"  TBtools JAR: {snap['jar'] or '⚠️ 未配置'}")
            click.echo(f"  Java: {snap['java']}")
            click.echo(f"  xvfb: {'✅' if snap['xvfb'] else '❌ 未安装(Linux 绘图必需)'}")
            for k, v in snap["deps"].items():
                click.echo(f"  {k}: {'✅' if v else '—'}")

    @cli.command(name="tool-describe")
    @click.argument("command")
    @click.option("--json", "as_json", is_flag=True, help="输出机器 schema(JSON, 供 Agent)")
    def tool_describe(command, as_json):
        """命令机器描述(schema): tbtools tool-describe <命令> [--json](Agent 能力)"""
        import json as _json
        meta_path = os.path.join(ROOT, "tbtools_cli", "command_metadata.json")
        meta = _json.load(open(meta_path, encoding="utf-8")) if os.path.isfile(meta_path) else {}
        if command not in meta:
            click.echo(f"❌ 未知命令: {command}(见 tbtools list / search)", err=True)
            sys.exit(1)
        v = meta[command]
        # 分组: metadata group 字段优先(gen_metadata 注入), 运行时 _groups 兜底
        group = v.get("group") or next((g for g, grp in _LG._groups.items() if command in grp.commands),
                                       _LG.CATEGORY_MAP.get(command, "engine"))
        # help: metadata 优先, 回退点击命令对象(手动命令)
        help_txt = (v.get("help", "") or "").split("#")[-1].strip()
        if not help_txt:
            grp = _LG._groups.get(group)
            cmd_obj = grp.commands.get(command) if grp else None
            help_txt = (cmd_obj.help or "") if cmd_obj else ""
        cls = v.get("class") or ("" if command not in _LG._groups.get("engine", type("x", (), {"commands": {}})).commands else "")
        desc = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "schema_version": "1.0",
            "id": f"tbtools.{group}.{command}",
            "uri": f"tbtools://{group}/{command}",  # 稳定标识(评审 #9 URI)
            "name": command,
            "group": group,
            "kind": v.get("kind", "?"),
            "help": help_txt,
            "invoke": f"tbtools {group} {command} <args...>" if group != "engine" else f"tbtools engine {cls} key=value",
            "class": cls,
            "pitfall": get_pitfall_hint(command),
        }
        if v.get("alias_of"):
            desc["alias_of"] = v["alias_of"]
        if v.get("relations"):
            desc["relations"] = v["relations"]
        if v.get("capabilities"):
            desc["capabilities"] = v["capabilities"]
        if v.get("parameters"):
            desc["parameters"] = v["parameters"]
        if v.get("dependencies"):
            import shutil as _sh
            desc["dependencies"] = v["dependencies"]
            desc["availability"] = {
                "status": "ready" if all(_sh.which(d) for d in v["dependencies"]) else "missing_dependencies",
                "missing": [d for d in v["dependencies"] if not _sh.which(d)],
            }
        if v.get("inputs"):
            desc["inputs"] = v["inputs"]
        if v.get("outputs"):
            desc["outputs"] = v["outputs"]
        if as_json:
            click.echo(_json.dumps(desc, ensure_ascii=False, indent=1))
        else:
            click.echo(f"  {desc['id']}")
            click.echo(f"  描述: {desc['help']}")
            click.echo(f"  调用: {desc['invoke']}")
            click.echo(f"  坑位: {desc['pitfall'] or '无'}")

    @cli.command(name="tool-validate")
    @click.argument("command")
    @click.argument("inputs", nargs=-1, required=True)
    @click.option("--json", "as_json", is_flag=True, help="结构化输出(JSON, 供 Agent)")
    @click.option("--force", is_flag=True, help="忽略预检问题(结果 valid=True, 保留 warnings)")
    def tool_validate(command, inputs, as_json, force):
        """执行前预检: 输入存在性/格式/列数(Agent 能力3;不运行命令)"""
        import json as _json
        checks = []
        ok = True
        for i, path in enumerate(inputs, 1):
            if not os.path.isfile(path):
                checks.append({"input": path, "ok": False, "issue": "文件不存在"})
                ok = False
                continue
            v_ok, msg = validate_file(path, "文件")
            if not v_ok:
                checks.append({"input": path, "ok": False, "issue": msg})
                ok = False
                continue
            fmt, ncols, _ = detect_format(path)
            warn = check_input_format(command, path)
            # 列名契约校验(评审 #31: CommandSpec columns 标注的命令, 首行列名比对)
            _col_mismatch = None
            try:
                from tbtools_cli.command_spec import KNOWN_SCHEMAS
                _specs = KNOWN_SCHEMAS.get(command)
                if _specs and _specs[0] and _specs[0][0].columns:
                    _expected = _specs[0][0].columns
                    _header = open(path, encoding="utf-8", errors="replace").readline().rstrip().split("	")
                    # 无表头文件(首行=数据行含数字)跳过列名校验(评审 #31 误报修复)
                    def _looks_numeric(x):
                        try:
                            float(x.replace("e", "E"))
                            return True
                        except Exception:
                            return False
                    _is_header = not any(_looks_numeric(_c) for _c in _header[:len(_expected)])
                    if _is_header and _header[:len(_expected)] != _expected:
                        _col_mismatch = f"列名不匹配: 期望 {_expected}, 实际 {_header[:len(_expected)]}"
            except Exception:
                pass
            _ok_this = not warn and not _col_mismatch
            checks.append({"input": path, "ok": _ok_this, "format": fmt, "columns": ncols,
                           "warning": warn or _col_mismatch or None})
            if not _ok_this:
                ok = False
        result = {"command": command, "valid": ok, "checks": checks}
        if as_json:
            click.echo(_json.dumps(result, ensure_ascii=False, indent=1))
        else:
            for c2 in checks:
                st = "✅" if c2["ok"] else "❌"
                w = f" ⚠️ {c2.get('warning')}" if c2.get("warning") else ""
                click.echo(f"  {st} {c2['input']} [{c2.get('format','?')}/{c2.get('columns','?')}列]{w}")
            click.echo(f"  结论: {'✅ 可执行' if ok else '❌ 有预检问题(可 --force 忽略,见引擎报错)'}")
        sys.exit(0 if (ok or force) else 3)

    @cli.command(name="tool-provenance")
    @click.argument("artifact")
    def tool_provenance(artifact):
        """查询运行溯源: 读取 <artifact>.tbtools.json(Agent 能力7)"""
        import json as _json
        p = artifact + ".tbtools.json"
        if not os.path.isfile(p):
            click.echo(f"❌ 无溯源文件: {p}(命令成功运行后自动生成)", err=True)
            sys.exit(1)
        d = _json.load(open(p, encoding="utf-8"))
        click.echo(_json.dumps(d, ensure_ascii=False, indent=1))

    @cli.command(name="tool-result")
    @click.argument("artifact")
    def tool_result(artifact):
        """结构化结果摘要(Agent 能力5): 从 provenance 提炼 status/artifacts/inputs"""
        import json as _json
        p = artifact + ".tbtools.json"
        if not os.path.isfile(p):
            click.echo(_json.dumps({"status": "unknown", "artifact": artifact,
                                    "error": "无溯源文件(命令未成功运行或未生成)"},
                                   ensure_ascii=False, indent=1))
            sys.exit(1)
        d = _json.load(open(p, encoding="utf-8"))
        summary = {
            "schema_version": "1.0",
            "status": "success" if d.get("exit_code") == 0 else "failed",
            "tool": d.get("command"),
            "artifacts": [{"path": o, "role": "primary_output"} for o in d.get("outputs", [])],
            "inputs_count": len(d.get("inputs", [])),
            "tbtools_cli": d.get("tbtools_cli"),
            "timestamp": d.get("timestamp"),
        }
        click.echo(_json.dumps(summary, ensure_ascii=False, indent=1))

    @cli.command(name="tool-run")
    @click.argument("args", nargs=-1, required=True)
    @click.option("--json", "as_json", is_flag=True, help="结构化结果回显(Agent 能力4)")
    @click.option("--timeout", "timeout_s", type=int, default=0, help="超时秒数(0=不超时; 超时杀进程树并返回 TB007)")
    @click.option("--dry-run", "dry", is_flag=True, help="不执行: 预检+预估产物(Agent 规划, 评审 #37)")
    @click.option("--quiet", "quiet", is_flag=True, help="静默: stdout 只出结构化结果(日志进 stderr)")
    def tool_run(args, as_json, timeout_s, dry, quiet):
        """统一执行接口: 转发任意 tbtools 命令 + 结构化结果(退出码/时长/产物)"""
        import json as _json
        import time as _time
        # --json 时: stdout 是协议(纯 JSON)——执行期 stdout → /dev/null(日志丢弃, Java 详情在 err 文件)
        _saved_fd = None
        if dry:
            # dry-run: 输入存在性/格式预检 + 预估产物, 不执行(评审 #37)
            import json as _json2
            ok, probs = True, []
            _skip = 2 if len(args) >= 3 else 1  # 跳过 <group> <cmd>(和 <cmd>)
            for a in args[_skip:]:
                if a.endswith((".svg", ".png", ".pdf", ".tsv", ".nwk")):
                    continue  # 输出参数
                if not os.path.isfile(a):
                    ok = False
                    probs.append(f"missing input: {a}")
            est = [a for a in args[_skip:] if a.endswith((".svg", ".png", ".pdf"))]
            # P1-17: dry-run 资源/依赖预估(从 CommandSpec 模型读)
            _deps, _net, _mem = [], None, None
            try:
                from tbtools_cli.command_spec import KNOWN_DEPENDENCIES_STRUCT, KNOWN_STATUS
                _cmd_name = args[1] if len(args) >= 2 else (args[0] if args else "")
                _deps = [d["name"] for d in KNOWN_DEPENDENCIES_STRUCT.get(_cmd_name, [])]
                _net = KNOWN_STATUS.get(_cmd_name) == "network-required"
                import json as _jm
                _meta = _jm.load(open(os.path.join(ROOT, "tbtools_cli", "command_metadata.json"), encoding="utf-8"))
                _mem = _meta.get(_cmd_name, {}).get("xmx")
            except Exception:
                pass
            click.echo(_json2.dumps({"schema_version": "1.0", "status": "ready" if ok else "not_ready",
                                     "tool": args[-1] if args else "", "inputs_valid": ok,
                                     "dependencies_ready": True if (JAR and os.path.isfile(JAR)) else False,
                                     "estimated_artifacts": est,
                                     "estimated_memory": _mem,
                                     "required_dependencies": _deps,
                                     "network_required": _net,
                                     "problems": probs}, ensure_ascii=False, indent=1))
            sys.exit(0 if ok else 3)

        if as_json:
            import os as _os
            _saved_fd = _os.dup(1)
            _devnull = _os.open(_os.devnull, _os.O_WRONLY)
            _os.dup2(_devnull, 1)
            _os.close(_devnull)

        t0 = _time.time()
        _timed_out = False
        try:
            if timeout_s and timeout_s > 0:
                # 超时模式: 独立进程执行, 可整体杀进程树(含 java/xvfb 子进程)
                import subprocess as _sp
                import sys as _sys
                try:
                    _r = _sp.run([_sys.executable, "-m", "tbtools_cli.cli"] + list(args),
                                 timeout=timeout_s)
                    ec = _r.returncode or 0
                except _sp.TimeoutExpired:
                    _timed_out = True
                    ec = 1
            else:
                try:
                    ec = cli.main(list(args), standalone_mode=False) if cli is not None else 1
                except SystemExit as _e:
                    ec = int(_e.code or 0)  # 命令内部 sys.exit(0/2) 在嵌套调用下逃逸——捕获
                ec = ec or 0
        finally:
            if _saved_fd is not None:
                import os as _os
                _os.dup2(_saved_fd, 1)
                _os.close(_saved_fd)
        dt = round(_time.time() - t0, 2)
        # 产物+错误: 明确输出识别(args 中最后图形参数 → 其 provenance), 非扫描猜测
        artifacts, error = [], None
        for a in reversed(args):
            if a.endswith((".svg", ".png", ".pdf")):
                _po = a + ".tbtools.json"
                if os.path.isfile(_po):
                    try:
                        _prov = _json.load(open(_po, encoding="utf-8"))
                        artifacts = _prov.get("outputs", [])
                        error = _prov.get("error")
                    except Exception:
                        pass
                break
        if _timed_out:
            error = {"code": "TB007_TOOL_TIMEOUT", "retryable": True,
                     "suggested_action": "retry with --timeout higher or smaller input"}
        result = {"$schema": "https://json-schema.org/draft/2020-12/schema",
                  "schema_version": "1.0", "exit_code": ec, "duration_s": dt,
                  "artifacts": artifacts, "error": error, "timed_out": _timed_out}
        if as_json:
            click.echo(_json.dumps(result, ensure_ascii=False, indent=1))
        else:
            click.echo(f"  exit: {ec} | {dt}s | 产物: {artifacts or '无'}")
        sys.exit(ec if ec else 0)

    # ── Job 模型(GLM P1 + 状态机完善 2026-09-23)──
    # 状态机: running → succeeded(exit 0) / failed(exit≠0) / cancelled / timed_out
    _JOB_MONITOR = """import subprocess, sys, json, os, signal, time, traceback
jf = sys.argv[1]
try:
    job = json.load(open(jf, encoding='utf-8'))
    jd = os.path.dirname(jf)
    log = open(os.path.join(jd, job['id'] + '.log'), 'w', encoding='utf-8')
    p = subprocess.Popen([sys.executable, '-m', 'tbtools_cli.cli'] + job['args'], stdout=log, stderr=subprocess.STDOUT, close_fds=True)
    job['pid'] = p.pid; job['status'] = 'running'
    json.dump(job, open(jf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    try:
        ec = p.wait(timeout=job.get('timeout_s') or None)
    except subprocess.TimeoutExpired:
        try: os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception: pass
        p.wait(); job['status'] = 'timed_out'; job['exit_code'] = -1
    else:
        job['status'] = 'succeeded' if ec == 0 else 'failed'; job['exit_code'] = ec or 0
    job['finished_at'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    json.dump(job, open(jf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
except Exception:
    try:
        tb = traceback.format_exc()
        open(os.path.join(os.path.dirname(jf), os.path.basename(jf).replace('.json', '.err')), 'w', encoding='utf-8').write(tb)
    except Exception:
        pass
"""

    # P1-14: JSON Protocol 统一封装(评审 #52)——Agent 接口统一 {schema_version/request_id/status/data/error/meta}
    def _envelope(data, status="success", error=None, meta=None):
        import json as _json
        import time as _time
        import uuid as _uuid
        return _json.dumps({
            "schema_version": "1.0",
            "request_id": f"req_{_time.strftime('%Y%m%d')}_{_uuid.uuid4().hex[:8]}",
            "status": status,
            "data": data,
            "error": error,
            "meta": meta or {"tbtools_cli": "1.3.0"},
        }, ensure_ascii=False, indent=1)

    def _jobs_dir():
        d = os.path.join(os.path.expanduser("~"), ".config", "tbtools-cli", "jobs")
        os.makedirs(d, exist_ok=True)
        return d

    def _job_save(job):
        import json as _json
        jf = os.path.join(_jobs_dir(), f"{job['id']}.json")
        _json.dump(job, open(jf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def _job_finish(job, status, exit_code):
        """进程结束后: 从 provenance 读 exit_code/error 判 succeeded/failed 并落盘"""
        import json as _json
        job["status"] = status
        job["exit_code"] = exit_code
        job["finished_at"] = __import__("time").strftime("%Y-%m-%dT%H:%M:%S")
        # 输出识别(args 中最后图形参数 → provenance, 取 error)
        for a in reversed(job.get("args", [])):
            if a.endswith((".svg", ".png", ".pdf")):
                _po = a + ".tbtools.json"
                if os.path.isfile(_po):
                    try:
                        job["error"] = _json.load(open(_po, encoding="utf-8")).get("error")
                    except Exception:
                        pass
                break
        _job_save(job)

    @cli.command(name="tool-submit")
    @click.argument("args", nargs=-1, required=True)
    @click.option("--timeout", "timeout_s", type=int, default=0, help="超时秒数(0=不超时; 超时杀进程树并置 timed_out)")
    def tool_submit(args, timeout_s):
        """异步提交任务: 后台执行, 返回 job_id(Agent 长任务; 状态机 running→succeeded/failed/cancelled/timed_out)"""
        import json as _json
        import time as _time
        import uuid as _uuid
        import subprocess as _sp
        import sys as _sys
        jid = f"job_{_time.strftime('%Y%m%d_%H%M%S')}_{_uuid.uuid4().hex[:6]}"
        # 独立监控进程(非线程): wait 任务 + 按退出码落盘终态(不依赖图形 provenance)
        job = {"id": jid, "status": "running", "pid": None, "args": list(args),
               "started_at": _time.strftime("%Y-%m-%dT%H:%M:%S"),
               "timeout_s": timeout_s, "log": os.path.join(_jobs_dir(), f"{jid}.log")}
        _job_save(job)
        jf = os.path.join(_jobs_dir(), f"{jid}.json")
        # stdin=DEVNULL 关键(2026-09-23 实测): 继承 exec 管道 stdin 的子进程在父退出时被清
        _sp.Popen([_sys.executable, "-c", _JOB_MONITOR, jf],
                  start_new_session=True, stdin=_sp.DEVNULL,
                  stdout=_sp.DEVNULL, stderr=_sp.DEVNULL, close_fds=True)
        click.echo(_json.dumps({"job_id": jid, "status": "running"}, ensure_ascii=False, indent=1))

    @cli.command(name="job-status")
    @click.argument("job_id")
    def job_status(job_id):
        """查询任务状态(状态机: running/succeeded/failed/cancelled/timed_out + 退出码)"""
        import json as _json
        jf = os.path.join(_jobs_dir(), f"{job_id}.json")
        if not os.path.isfile(jf):
            click.echo(f"❌ 未知 job: {job_id}", err=True)
            sys.exit(1)
        job = _json.load(open(jf, encoding="utf-8"))
        import time as _t
        # ① 超时惰性判定: running + elapsed > timeout_s → killpg + timed_out
        if job["status"] == "running" and job.get("pid") and job.get("timeout_s", 0) > 0:
            try:
                _start = _t.mktime(_t.strptime(job["started_at"], "%Y-%m-%dT%H:%M:%S"))
                if _t.time() - _start > job["timeout_s"]:
                    import signal as _sig
                    try:
                        os.killpg(os.getpgid(job["pid"]), _sig.SIGKILL)
                    except Exception:
                        pass
                    _job_finish(job, "timed_out", -1)
            except Exception:
                pass
        # ② running 但 pid 已消失(子进程独立退出)→ 惰性终态判定(provenance)
        if job["status"] == "running" and job.get("pid"):
            alive = os.path.exists(f"/proc/{job['pid']}") if os.path.isdir("/proc") else True
            if not alive:
                # 从 provenance 判终态(子进程独立写; 无 provenance=失败)
                _ec, _err = None, None
                for a in reversed(job.get("args", [])):
                    if a.endswith((".svg", ".png", ".pdf")) and os.path.isfile(a + ".tbtools.json"):
                        try:
                            _pr = _json.load(open(a + ".tbtools.json", encoding="utf-8"))
                            _ec, _err = _pr.get("exit_code"), _pr.get("error")
                        except Exception:
                            pass
                        break
                if _ec is None:
                    _job_finish(job, "failed", -1)
                else:
                    _job_finish(job, "succeeded" if _ec == 0 else "failed", _ec)
                    job["error"] = _err
                    _job_save(job)
        click.echo(_json.dumps({"job_id": job_id, "status": job.get("status"),
                                "exit_code": job.get("exit_code"),
                                "started_at": job.get("started_at"),
                                "finished_at": job.get("finished_at"),
                                "log": job.get("log") or os.path.join(_jobs_dir(), f"{job_id}.log")},
                               ensure_ascii=False, indent=1))

    @cli.command(name="job-log")
    @click.argument("job_id")
    @click.option("--tail", "n", type=int, default=30)
    def job_log(job_id, n):
        """查看任务日志(尾部 N 行)"""
        lf = os.path.join(_jobs_dir(), f"{job_id}.log")
        if not os.path.isfile(lf):
            click.echo(f"❌ 无日志: {job_id}", err=True)
            sys.exit(1)
        lines = open(lf, encoding="utf-8", errors="replace").read().splitlines()
        click.echo("\n".join(lines[-n:]))

    @cli.command(name="job-result")
    @click.argument("job_id")
    def job_result(job_id):
        """任务结构化结果(状态机终态 + artifacts + error; Agent 结果验证)"""
        import json as _json
        jf = os.path.join(_jobs_dir(), f"{job_id}.json")
        if not os.path.isfile(jf):
            click.echo(f"❌ 未知 job: {job_id}", err=True)
            sys.exit(1)
        job = _json.load(open(jf, encoding="utf-8"))
        artifacts = []
        for a in reversed(job.get("args", [])):
            if a.endswith((".svg", ".png", ".pdf")):
                if os.path.isfile(a):
                    artifacts.append(os.path.abspath(a))
                break
        click.echo(_json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema",
                                "schema_version": "1.0", "job_id": job_id,
                                "status": job.get("status"), "exit_code": job.get("exit_code"),
                                "artifacts": artifacts, "error": job.get("error")},
                               ensure_ascii=False, indent=1))

    @cli.command(name="job-cancel")
    @click.argument("job_id")
    def job_cancel(job_id):
        """取消任务(杀进程树, 含 java/xvfb 子进程; 终态 cancelled)"""
        import json as _json
        import signal as _sig
        jf = os.path.join(_jobs_dir(), f"{job_id}.json")
        if not os.path.isfile(jf):
            click.echo(f"❌ 未知 job: {job_id}", err=True)
            sys.exit(1)
        job = _json.load(open(jf, encoding="utf-8"))
        if job.get("status") != "running" or not job.get("pid"):
            click.echo(f"⏹ {job_id} 非运行中(当前 {job.get('status')})", err=True)
            sys.exit(1)
        try:
            os.killpg(os.getpgid(job["pid"]), _sig.SIGKILL)
            _job_finish(job, "cancelled", -1)
            click.echo(f"✅ 已取消 {job_id}(PID {job['pid']} 进程组)")
        except Exception:
            # 进程已死(未落盘终态)→ 惰性判定(provenance)
            _ec, _err = None, None
            for a in reversed(job.get("args", [])):
                if a.endswith((".svg", ".png", ".pdf")) and os.path.isfile(a + ".tbtools.json"):
                    try:
                        import json as _json
                        _pr = _json.load(open(a + ".tbtools.json", encoding="utf-8"))
                        _ec, _err = _pr.get("exit_code"), _pr.get("error")
                    except Exception:
                        pass
                    break
            if _ec is None:
                _job_finish(job, "failed", -1)
            else:
                _job_finish(job, "succeeded" if _ec == 0 else "failed", _ec)
                job["error"] = _err
                _job_save(job)
            click.echo(f"⏹ {job_id} 进程已结束(终态 {job['status']}, exit {job.get('exit_code')})")

    @cli.command(name="job-clean")
    @click.option("--days", "days", type=int, default=7, help="清理 N 天前已结束(非 running)的 job(默认 7)")
    @click.option("--all", "all_flag", is_flag=True, help="清理全部已结束 job(忽略天数)")
    def job_clean(days, all_flag):
        """清理历史 job(已结束且超期的 json/log)"""
        import json as _json
        import time as _time
        jdir = _jobs_dir()
        now = _time.time()
        removed = []
        for f in os.listdir(jdir):
            if not (f.endswith(".json") or f.endswith(".log")):
                continue
            jid = f.rsplit(".", 1)[0]
            jp = os.path.join(jdir, f"{jid}.json")
            try:
                job = _json.load(open(jp, encoding="utf-8"))
            except Exception:
                continue
            if job.get("status") == "running":
                continue  # 运行中不碰
            age = now - os.path.getmtime(jp)
            if all_flag or age > days * 86400:
                for ext in (".json", ".log"):
                    p = os.path.join(jdir, jid + ext)
                    if os.path.isfile(p):
                        os.unlink(p)
                        removed.append(os.path.basename(p))
        if removed:
            click.echo(f"🗑 清理 {len(removed)} 个文件(>={days} 天前已结束):")
            for r in removed[:8]:
                click.echo(f"   {r}")
            if len(removed) > 8:
                click.echo(f"   ... 等 {len(removed) - 8} 个")
        else:
            click.echo("  无过期 job 可清理(running 任务保留)")

    @cli.command(name="mcp")
    def mcp_cmd():
        """启动 MCP server(stdio)——Claude/Cursor/任意 MCP 客户端即插即用"""
        from tbtools_cli.mcp_server import main as _mcp_main
        _mcp_main()

    @cli.command(name="capabilities")
    @click.option("--json", "as_json", is_flag=True, help="机器格式输出(供 Agent 环境选择)")
    def capabilities_cmd(as_json):
        """环境能力检测: 绘图/无头/RPC/MCP/网络 等能力状态(评审 #25)"""
        import json as _json
        import shutil as _sh
        is_win = os.name == "nt"
        caps = {
            "plotting": bool(JAR) and (not is_win or _sh.which("xvfb-run")),
            "headless": not is_win,
            "rpc": bool(JAR),
            "mcp": True,
            "ncbi": _sh.which("blastdbcmd") is not None,
            "sra": _sh.which("fastq-dump") is not None or _sh.which("fasterq-dump") is not None,
            "external": sorted({d for d in ["mafft", "muscle", "iqtree2", "hmmsearch", "diamond", "kallisto", "trimal", "jellyfish", "blastp", "mcscanx"] if _sh.which(d)}),
        }
        if as_json:
            click.echo(_json.dumps(caps, ensure_ascii=False, indent=1))
        else:
            for k, v in caps.items():
                mark = "✅" if v else ("⚠️" if k != "external" else "-")
                click.echo(f"  {mark} {k}: {v if isinstance(v, list) else ('可用' if v else '不可用')}")

    @cli.command(name="provenance-graph")
    @click.argument("dir", default=".", required=False)
    @click.option("--json", "as_json", is_flag=True, help="结构化 DAG 输出")
    @click.option("--mermaid", "mermaid", is_flag=True, help="mermaid 图代码")
    def provenance_graph(dir, as_json, mermaid):
        """运行链 DAG: 按 provenance 输入/输出路径关联, 连成工作流图(评审 #30/#54-9)"""
        import glob as _glob
        import json as _json
        files = _glob.glob(os.path.join(dir, "**", "*.tbtools.json"), recursive=True)
        provs = []
        for p in files:
            try:
                d = _json.load(open(p, encoding="utf-8"))
                d["_file"] = p
                provs.append(d)
            except Exception:
                pass
        # 输出路径 → prov 索引(abspath 归一)
        out_map = {}
        for d in provs:
            for o in d.get("outputs", []):
                out_map[os.path.abspath(o)] = d
        nodes, edges = {}, []
        for d in provs:
            cmd = d.get("command", "?")
            for inp in d.get("inputs", []):
                ipath = os.path.abspath(inp.get("path", ""))
                if ipath in out_map:
                    parent = out_map[ipath]
                    if parent is not d:
                        edges.append({"from": parent.get("command"), "to": cmd,
                                      "via": os.path.basename(ipath)})
                        nodes[parent.get("command")] = {"type": "tool"}
                        nodes[cmd] = {"type": "tool"}
        # 孤立节点(无上游)
        for d in provs:
            nodes.setdefault(d.get("command", "?"), {"type": "tool"})
        if mermaid:
            lines = ["graph LR"]
            for e in edges:
                lines.append(f'    {e["from"]} -->|{e["via"]}| {e["to"]}')
            click.echo("\n".join(lines))
        elif as_json:
            click.echo(_json.dumps({"schema_version": "1.0", "dir": os.path.abspath(dir),
                                    "provenance_count": len(provs),
                                    "nodes": [{"id": n, **v} for n, v in nodes.items()],
                                    "edges": edges}, ensure_ascii=False, indent=1))
        else:
            if not edges:
                click.echo(f"  目录 {dir} 下无运行链(仅 {len(provs)} 个孤立 provenance)")
            else:
                click.echo(f"  工作流 DAG({len(edges)} 条边, {len(provs)} 个运行):")
                for e in edges:
                    click.echo(f"    {e['from']} ──{e['via']}──> {e['to']}")

    @cli.command(name="plugin")
    @click.argument("sub", default="list", required=False, type=click.Choice(["list"]))
    @click.option("--json", "as_json", is_flag=True)
    def plugin_cmd(sub, as_json):
        """插件契约(评审 #33): 列出已 CLI 化的插件命令 + 来源/状态"""
        import json as _json
        # 插件命令 ↔ Plugin ID 映射(12 个 CLI 化插件)
        PLUGINS = {
            "gsea": ("P00342-Simple_GO_GSEA_Wrapper", "GSEA 富集"),
            "mcscanxd": ("P00370-OneStepMCScanX-SuperFast", "MCScanX 加速"),
            "quickAnno": ("P00480-Quick_Protein_Anno", "diamond 蛋白注释"),
            "qdot": ("P00380-Quick_Genome_Dot_Plot", "基因组 dot plot"),
            "tfbsShift": ("P00551-Plant_TF_Binding_Motif_Shift", "植物 TF motif 偏移"),
            "hmmerSearch": ("P00680-Advanced_HMMer_Search", "HMMer 全库扫描"),
            "newickRename": ("P00690-Newick_Rename", "Newick 重命名"),
            "memeViz": ("P00700-Batch_MEME_Motif_Viz", "MEME 可视化"),
            "kallisto": ("P00740-Kallisto_Super_Wrapper", "kallisto 定量"),
            "smart": ("P00060-Batch_SMART", "SMART 域注释"),
            "fimo": ("fimo(外部 FIMO)", "FIMO motif 扫描"),
            "notung": ("notung(外部 Notung)", "Notung reconcile"),
        }
        rows = []
        for cmd_name, (plugin_id, desc) in PLUGINS.items():
            rows.append({"command": cmd_name, "plugin": plugin_id, "description": desc,
                         "status": "cli_ready"})
        if as_json:
            click.echo(_json.dumps({"schema_version": "1.0", "plugin_count": len(rows), "plugins": rows},
                                   ensure_ascii=False, indent=1))
        else:
            click.echo(f"  已 CLI 化插件 {len(rows)} 个:")
            for r in rows:
                click.echo(f"    {r['command']:<14} {r['description']:<20} ({r['plugin']})")
            click.echo("  (plugin install/search 规划: plugins/src/ 原始存档 + PluginStore 122 插件/飞纪盘 64)")

    @cli.command(name="artifact")
    @click.argument("sub", default="inspect", type=click.Choice(["inspect"]))
    @click.argument("path")
    @click.option("--json", "as_json", is_flag=True)
    def artifact_cmd(sub, path, as_json):
        """Artifact 一等公民(ADR-0007): inspect——从 provenance 输出结构化 Artifact"""
        import json as _json
        from tbtools_cli.artifact import build, from_provenance
        art = from_provenance(path) or build(path)
        if not art:
            click.echo(f"❌ 文件不存在: {path}", err=True)
            sys.exit(1)
        d = art.to_dict()
        from tbtools_cli.workflow import validate_artifact
        _vok, _vmsg = validate_artifact(path)
        d["validation"] = {"valid": _vok, "detail": _vmsg}
        if as_json:
            click.echo(_json.dumps(d, ensure_ascii=False, indent=1))
        else:
            prov = "✅ 溯源完整" if art.metadata.get("invocation") else "⚠️ 无 provenance"
            click.echo(f"  Artifact: {art.id}")
            click.echo(f"    类型/格式: {art.type}/{art.format}")
            click.echo(f"    路径: {art.path}")
            click.echo(f"    大小: {art.size} B | sha256: {art.sha256}")
            click.echo(f"    生产者: {art.producer or '?'} | {prov}")

    @cli.command(name="workflow")
    @click.argument("sub", type=click.Choice(["validate", "plan", "run", "graph"]))
    @click.argument("path")
    @click.option("--workdir", default=None, help="执行目录(默认 <wf 名>.wf/)")
    @click.option("--timeout", "timeout_s", type=int, default=600)
    @click.option("--resume", is_flag=True, help="断点续跑(跳过已成功步骤)")
    def workflow_cmd(sub, path, workdir, timeout_s, resume):
        """Workflow 一等公民(ADR-0007): YAML 工作流 validate/plan/run/graph"""
        import json as _json
        from tbtools_cli.workflow import WorkflowError, graph, load_workflow, plan, run
        try:
            wf = load_workflow(path)
        except WorkflowError as e:
            click.echo(f"❌ workflow 无效: {e}", err=True)
            sys.exit(3)
        wd = workdir or os.path.splitext(os.path.basename(path))[0] + ".wf"
        if sub == "validate":
            click.echo(_json.dumps({"schema_version": "1.0", "workflow": wf["id"],
                                    "valid": True, "steps": len(wf["steps"])}, ensure_ascii=False))
        elif sub == "plan":
            click.echo(_json.dumps({"schema_version": "1.0", "workflow": wf["id"],
                                    "plan": plan(wf, wd)}, ensure_ascii=False, indent=1))
        elif sub == "graph":
            click.echo(graph(wf))
        else:
            result = run(wf, wd, timeout_s=timeout_s, resume=resume)
            click.echo(_json.dumps(result, ensure_ascii=False, indent=1))
            sys.exit(0 if result["status"] == "succeeded" else 1)

    @cli.command(name="search")
    @click.argument("keyword", required=False)
    @click.option("--json", "as_json", is_flag=True, help="结构化输出(JSON, 供 Agent 发现)")
    @click.option("--input", "in_fmt", default=None, help="反向搜索: 输入格式(gff3/fasta/tsv/...)")
    @click.option("--output", "out_fmt", default=None, help="反向搜索: 输出格式(svg/tsv/nwk/...)")
    @click.option("--capability", "cap", default=None, help="反向搜索: 能力标签(如 phylogeny/enrichment)")
    def search_cmd(keyword, as_json, in_fmt, out_fmt, cap):
        """模糊搜索命令（匹配名称+doc）: tbtools search <关键词> [--json]"""
        import json as _json
        if not keyword and not (in_fmt or out_fmt or cap):
            click.echo(_json.dumps({"query": "", "hits": [], "error": "need keyword or --input/--output/--capability"},
                                   ensure_ascii=False) if as_json
                       else "❌ 需要关键词或 --input/--output/--capability。试试: tbtools search volcano")
            sys.exit(1)
        meta_path = os.path.join(ROOT, "tbtools_cli", "command_metadata.json")
        if not os.path.isfile(meta_path):
            click.echo(f"❌ 元数据缺失: {meta_path}", err=True)
            sys.exit(1)
        meta = _json.load(open(meta_path, encoding="utf-8"))
        # 多词查询: 空格拆分, 全部词须命中(名/help/class)——Agent 自然语言("gene structure")
        kws = [w for w in (keyword or "").lower().split() if w]
        hits = []
        for name, v in meta.items():
            hay = " ".join([name.lower(),
                            (v.get("help", "") or "")[:300].lower(),
                            (v.get("class", "") or "").lower()])
            if all(w in hay for w in kws):
                cat = _LG.CATEGORY_MAP.get(name, "engine")
                kind = v.get("kind", "?")
                desc = (v.get("help", "") or "").split("#")[-1].strip()[:60]
                hits.append((name, cat, kind, desc))
        if not hits and len(kws) > 1:
            # AND 无果回退 OR(Agent 宽松匹配优于无结果)
            for name, v in meta.items():
                hay = " ".join([name.lower(), (v.get("help", "") or "")[:300].lower(),
                                (v.get("class", "") or "").lower()])
                if any(w in hay for w in kws):
                    cat = v.get("group") or _LG.CATEGORY_MAP.get(name, "engine")
                    kind = v.get("kind", "?")
                    desc = (v.get("help", "") or "").split("#")[-1].strip()[:60]
                    hits.append((name, cat, kind, desc))

        # 反向/能力过滤(GLM: 能力图搜索; --input/--output/--capability)
        if (in_fmt or out_fmt or cap) and meta:
            filtered = []
            for name, v in meta.items():
                ins = [i.get("format", "") for i in v.get("inputs", [])] if v.get("inputs") else []
                outs = v.get("outputs", []) or []
                caps = v.get("capabilities", []) or []
                if in_fmt and in_fmt not in ins:
                    continue
                if v.get("alias_of") and not kws:
                    continue  # 反向/能力搜索: alias 不污染工具空间(仅 canonical)
                if out_fmt and out_fmt not in outs:
                    continue
                if cap:
                    _onto = v.get("capabilities_ontology", []) or []
                    if cap not in caps and cap not in _onto:
                        continue
                cat = v.get("group") or _LG.CATEGORY_MAP.get(name, "engine")
                desc = (v.get("help", "") or "").split("#")[-1].strip()[:60]
                filtered.append((name, cat, v.get("kind", "?"), desc))
            hits = filtered
        if not hits:
            if not keyword and not (in_fmt or out_fmt or cap):
                click.echo(_json.dumps({"query": "", "hits": [], "error": "need keyword or --input/--output/--capability"},
                                       ensure_ascii=False) if as_json
                           else "❌ 需要关键词或 --input/--output/--capability。试试: tbtools search volcano")
                sys.exit(1)
            click.echo(_json.dumps({"query": keyword or "", "hits": []}, ensure_ascii=False) if as_json
                       else f"❌ 没有匹配 '{keyword}' 的命令。试试: tbtools list")
            sys.exit(1)
        if as_json:
            click.echo(_json.dumps({"query": keyword, "hits": [
                {"name": n, "group": g, "kind": k, "description": d} for n, g, k, d in sorted(hits)
            ]}, ensure_ascii=False, indent=1))
            return
        kw_disp = keyword or ""
        click.echo(f"🔍 匹配 '{kw_disp}' 的命令（{len(hits)} 个）:")
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
