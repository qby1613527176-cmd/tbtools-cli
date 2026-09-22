"""cli_load.py — 动态命令注册（架构重构批次 B：从 cli.py 拆分）

CATEGORY_MAP/GROUPS 分组映射 + _load_auto_commands/_load_dynamic_commands +
_make_passthrough（metadata 驱动）+ ToolGroup 兜底注册。
由 cli.py 在 cli 定义后调用 build_and_load(cli) 完成装配。
"""
import difflib
import os
import re
import shutil
import subprocess
import sys

import click

from tbtools_cli import auto_commands as _ac
from tbtools_cli.core import ROOT, check_input_format, get_pitfall_hint, validate_file
from tbtools_cli.presets import PRESETS, apply_preset


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
    "gxfSplit": "gxf", "gxfIdAppender": "gxf",
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

# 全局分组表（build_and_load → _ensure_groups(cli) 填充；cli.py/list 等 import 使用）
_groups: dict[str, click.Group] = {}
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
    impl = _ac._IMPL_REGISTRY.get(name) or getattr(_ac, f'_{name}_impl', None)  # 显式注册表优先(第四轮评审)
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
    
    _target = group  # 调用方总传 group
    
    def _cmd_impl(ctx, verbose, quiet, fmt, preset, height, width, threads):
        args = list(ctx.args)
        
        # 输入校验：第一个非选项参数通常是输入文件（mcscanxd/kallisto 首参为工作目录/自定义路径，跳过校验）
        if args and not args[0].startswith('-') and name not in ("mcscanxd", "kallisto", "famerge", "getseqdb", "seqrecommend", "pubmed", "tableMerge", "generic", "preparespecies", "marker", "markertools", "venn5", "venn6"):
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


def build_and_load(cli):
    """组装: 建 groups → 动态注册 auto_commands + tbplot.sh 遗留 → 返回 groups dict"""
    _ensure_groups(cli)
    _load_auto_commands()
    _load_dynamic_commands()
    return _groups


def _ensure_groups(cli):
    """按 GROUPS 定义补齐分组（复用装饰器已创建的；原地填充保持 _groups 引用不变）"""
    global _groups
    _groups.clear()
    for key, desc in GROUPS.items():
        if key in cli.commands:
            _groups[key] = cli.commands[key]
        else:
            g = click.Group(name=key, help=desc)
            cli.add_command(g, name=key)
            _groups[key] = g
    # 子命令纠错绑定在 _load_dynamic_commands 尾部完成（_smart_resolve）
