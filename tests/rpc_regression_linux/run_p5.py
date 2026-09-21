import sys
#!/usr/bin/env python
"""Phase5: CLI 表面/未测工具/输出格式矩阵/边界输入 逐条原样记录"""
import io, os, re, subprocess, sys, time

os.environ.setdefault("TBTOOLS_JAR", "C:/Program Files/TBtools/TBtools_JRE1.6.jar")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
LOG = io.open("P5_LOG.md", "w", encoding="utf-8", newline="\n")

def w(s=""):
    LOG.write(s + "\n"); LOG.flush()

def run(cmd, timeout=240):
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL, shell=True)
    try:
        out, err = p.communicate(timeout=timeout)
        return (out.decode("utf-8", "replace"), err.decode("utf-8", "replace"),
                p.returncode, time.time() - t0)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
        try: out, err = p.communicate(timeout=5)
        except Exception: out, err = b"", b""
        return (out.decode("utf-8", "replace"), err.decode("utf-8", "replace"),
                -99, time.time() - t0)

def block(out, err, ec, dt, limit=5000):
    p = []
    if out.strip():
        o = out if len(out) <= limit else out[:limit] + f"\n…[截断, 共{len(out)}字符]"
        p.append("```\n" + o.rstrip() + "\n```")
    if err.strip():
        e = err if len(err) <= limit else err[:limit] + f"\n…[截断, 共{len(err)}字符]"
        p.append("**stderr:**\n```\n" + e.rstrip() + "\n```")
    if not p: p.append("```\n(无输出)\n```")
    p.append(f"退出码 `{ec}` · {dt:.1f}s")
    return "\n\n".join(p)

PYEXE = r"C:\Users\16135\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
CLI = f'"{PYEXE}" -m tbtools_cli.cli'
def T(title, cmdline, tmo=240):
    w(f"\n### {title}")
    w("```bash\n" + cmdline + "\n```")
    out, err, ec, dt = run(cmdline, timeout=tmo)
    w(block(out, err, ec, dt))
    print("OK", title)

w("# Phase 5：CLI 表面 / 未测工具 / 输出格式矩阵 / 边界输入\n")

# ============ 5.1 全局 CLI 表面 ============
w("\n## 5.1 全局 CLI 表面（帮助/清单/纠错/未知命令）\n")
T("全局 --help", f"{CLI} --help")
T("全局无参", "{CLI}")
T("全局 --version", f"{CLI} --version")
T("list（分组清单）", f"{CLI} list")
T("list tools（工具清单）", f"{CLI} list tools")
T("help blast", f"{CLI} help blast")
T("help tree", f"{CLI} help tree")
T("未知分组 tbtools nosuch", f"{CLI} nosuch")
T("未知命令 tbtools blast nosuch", f"{CLI} blast nosuch")
T("拼写纠错 blast twoSeqBlsat", f"{CLI} blast twoSeqBlsat")
T("拼写纠错 sets ven", f"{CLI} sets ven")
T("tool 未知工具", f"{CLI} tool NoSuchTool123")
T("tool help", f"{CLI} tool help")
T("-q 静默模式（expr volcano）", f"{CLI} expr volcano out/pin_deg.tsv out/quiet_volcano.svg -q")
T("--verbose 正常命令", f"{CLI} expr volcano out/pin_deg.tsv out/vb_volcano.svg --verbose")
T("groups 参数枚举 blast（空参数触发用法）", f"{CLI} blast")

# ============ 5.2 registry 独有未测工具（6 个） ============
w("\n## 5.2 registry 独有、前两轮未实跑的工具\n")
T("pairWiseKaKsCalculator", f'{CLI} tool pairWiseKaKsCalculator --inCdsFasta data/monarda_chloro_cds.fa --inProteinAln out/pin_msa3.fa --outFile out/p5_kaks.tsv')
T("sRNAseqAdaperRemover", f'{CLI} tool sRNAseqAdaperRemover --inFastq out/sim_reads.fq --outFastq out/p5_adapt.fq --adapter GTGCTTCTCTCTCTTCTGTCA')
T("prepareFileFromMCScanXtoTBtools", f'{CLI} tool prepareFileFromMCScanXtoTBtools --inCollinearity out/fake_collinearity.tsv --inSimplifiedGff out/chloro_simpl_mc.gff --outFile out/p5_mcx2tb.txt')
T("findBestHomologyBatch", f'{CLI} tool findBestHomologyBatch --queryFasta out/pin10.fa --subjectFasta data/monarda_chloro_pep.fa --outTable out/p5_besthom.tsv')
T("mirIdentifierBasedOnTargetSo", f'{CLI} tool mirIdentifierBasedOnTargetSo --inGenomeFa data/monarda_chloro.clean.fa --inTargetSo out/targetso.tsv --outFile out/p5_mirid.txt')
T("findBestForkerRootTree", f'{CLI} tool findBestForkerRootTree --inTree out/pin8_genetree.treefile --outFile out/p5_forker.txt')

# ============ 5.3 输出格式/预设矩阵 ============
w("\n## 5.3 出图命令 --format × --preset 矩阵（volcano/heatmap/phylotree 抽样）\n")
for fmt in ("png", "pdf", "svg"):
    for preset in ("nature", "cell", "wide"):
        T(f"volcano fmt={fmt} preset={preset}",
          f"{CLI} expr volcano out/pin_deg.tsv out/p5_volc_{fmt}_{preset}.{fmt} -f {fmt} --preset {preset}")
T("heatmap fmt=png（无 --preset，验证默认）", f"{CLI} expr heatmap out/pin_expr.tsv out/p5_heat_poster.png -f png")
T("phylotree fmt=pdf preset=nature", f"{CLI} tree phylotree out/pin_tree2/TBtools.IQtree.treefile out/p5_tree_nature.pdf -f pdf -p nature")
T("无效格式 fmt=webp（预期友好报错）", f"{CLI} expr volcano out/pin_deg.tsv out/p5_volc.webp -f webp")
T("无效预设 preset=science（观察行为）", f"{CLI} expr volcano out/pin_deg.tsv out/p5_volc_sci.svg --preset science")

# ============ 5.4 边界输入 ============
w("\n## 5.4 边界与非法输入\n")
io.open("out/empty.fa", "w", newline="\n").write("")
io.open("out/empty.tsv", "w", newline="\n").write("")
io.open("out/one.fa", "w", newline="\n").write(">only\nMKTAYIAKQRQISFVKSHFSRQLEALPL\n")
io.open("out/badchar.fa", "w", newline="\n").write(">bad\nMKTA@#$_123!!\n")
io.open("out/noeol.tsv", "w", newline="\n").write("Gene\tV1\nA\t1")  # 无换行结尾
with open("out/crlf.tsv", "w", newline="\r\n") as f:
    f.write("Gene\tV1\nA\t1\nB\t2\n")
T("空 FASTA → statFasta", f"{CLI} tool statFasta --inFasta out/empty.fa --outPutFile out/p5_stat_empty.xls")
T("单序列 FASTA → quickSplitFasta（每文件20）", f"{CLI} tool quickSplitFasta --inFasta out/one.fa --outDir out/p5_split1 --seqsPerFile 20")
T("非法字符 FASTA → translater", f"{CLI} tool translater --inFasta out/badchar.fa --outFasta out/p5_bad_trans.pep")
T("空 TSV → expr heatmap", f"{CLI} expr heatmap out/empty.tsv out/p5_heat_empty.svg")
T("无换行结尾 TSV → tableTranspose", f"{CLI} table tableTranspose out/noeol.tsv out/p5_noeol_t.tsv")
T("CRLF 换行 TSV → tableMelt", f"{CLI} table tableMelt out/crlf.tsv out/p5_crlf_melt.tsv")
T("输入文件不存在 → extractFasta", f"{CLI} tool extractFasta --inFa data/no_such_file.fa --inIDList out/chloro_ids.txt --outFa out/p5_x.fa")
T("输入目录当文件 → statFasta", f"{CLI} tool statFasta --inFasta data --outPutFile out/p5_dir.xls")
T("输出路径非法（指向不存在目录）→ rpkmCal", f"{CLI} tool rpkmCal --countsTable out/counts.tsv --lenInfo out/genelen.tsv --outTable Z:/no_such_dir/p5_x.tsv")
T("同名读写（输入=输出）→ tableTranspose", f"{CLI} table tableTranspose out/pin_expr.tsv out/pin_expr.tsv")

# ============ 5.5 旧入口 bin/tbcli.py 抽样 ============
w("\n## 5.5 旧入口 bin/tbcli.py（与 python -m 对比抽样）\n")
T("旧入口无参", '"%s" "C:/Users/16135/WorkBuddy/2026-09-20-10-24-01/tbtools-cli/bin/tbcli.py"' % PYEXE)
T("旧入口 statFasta 带参", f'"{PYEXE}" "C:/Users/16135/WorkBuddy/2026-09-20-10-24-01/tbtools-cli/bin/tbcli.py" statFasta --inFasta out/pin_family_full.fa --outPutFile out/p5_old_stat.xls')
T("旧入口未知工具", f'"{PYEXE}" "C:/Users/16135/WorkBuddy/2026-09-20-10-24-01/tbtools-cli/bin/tbcli.py" NoSuchTool')
LOG.close()
print("PHASE5 DONE")

