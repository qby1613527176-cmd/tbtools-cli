import sys
#!/usr/bin/env python
"""Phase7: 中文/特殊字符路径 + 零散未测项，逐条原样记录"""
import io, os, re, subprocess, sys, time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
LOG = io.open("P7_LOG.md", "w", encoding="utf-8", newline="\n")

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

def block(out, err, ec, dt, limit=4000):
    p = []
    if out.strip():
        p.append("```\n" + (out if len(out) <= limit else out[:limit] + "…[截断]").rstrip() + "\n```")
    if err.strip():
        e = err if len(err) <= limit else err[:limit] + "…[截断]"
        p.append("**stderr:**\n```\n" + e.rstrip() + "\n```")
    if not p: p.append("```\n(无输出)\n```")
    p.append(f"退出码 `{ec}` · {dt:.1f}s")
    return "\n\n".join(p)

PYEXE = r"C:\Users\16135\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
CLI = f'"{PYEXE}" -m tbtools_cli.cli'
TBCLI_PY = "C:/Users/16135/WorkBuddy/2026-09-20-10-24-01/tbtools-cli/bin/tbcli.py"

def T(title, cmdline, tmo=240):
    w(f"\n### {title}")
    w("```bash\n" + cmdline + "\n```")
    out, err, ec, dt = run(cmdline, timeout=tmo)
    w(block(out, err, ec, dt))
    print("OK", title)

w("# Phase 7：中文/特殊路径 + 零散未测项\n")

# ---- 7.1 中文路径 ----
w("\n## 7.1 中文与空格路径\n")
os.makedirs("out/中文目录 子测试", exist_ok=True)
import shutil
shutil.copy("out/pin10.fa", "out/中文目录 子测试/序列一.fa")
shutil.copy("out/pin_deg.tsv", "out/中文目录 子测试/差异基因.tsv")
CN = "out/中文目录 子测试"
T("中文目录+中文文件名：tool statFasta", f'{CLI} tool statFasta --inFasta "{CN}/序列一.fa" --outPutFile "{CN}/统计结果.xls"')
T("中文目录：expr volcano", f'{CLI} expr volcano "{CN}/差异基因.tsv" "{CN}/火山图.svg"')
T("中文目录：tool extractFasta", f'{CLI} tool extractFasta --inFa "{CN}/序列一.fa" --inIDList out/chloro_ids.txt --outFa "{CN}/提取.fa"')
os.makedirs("out/space dir", exist_ok=True)
shutil.copy("out/pin10.fa", "out/space dir/seq one.fa")
T("空格路径：tool statFasta", f'{CLI} tool statFasta --inFasta "out/space dir/seq one.fa" --outPutFile "out/space dir/stat out.xls"')

# ---- 7.2 零散未测项 ----
w("\n## 7.2 零散未测项\n")
T("new --list（场景向导清单）", f'{CLI} new --list')
T("presets nature（单预设详情）", f'{CLI} presets nature')
T("examples volcano（单命令示例）", f'{CLI} examples volcano')
T("examples 不存在的命令", f'{CLI} examples nosuchcmd')
T("check VCF", f'{CLI} check out/p2_fake.vcf')
T("check XML", f'{CLI} check out/t2b5.xml')
T("check EMBL", f'{CLI} check data/monarda_chloro.embl')
T("check 不存在文件", f'{CLI} check data/no_such.fa')
T("rpc list（方法清单）", f'{CLI} rpc list')
T("rpc --help", f'{CLI} rpc --help')
T("setup --help", f'{CLI} setup --help')
T("fetch-jar --help", f'{CLI} fetch-jar --help')
T("engine --help", f'{CLI} engine --help')
T("list plots（绘图清单）", f'{CLI} list plots')

# ---- 7.3 旧入口零散子命令 ----
w("\n## 7.3 旧入口 tbcli.py 零散子命令\n")
T("旧入口 list plots", f'"{PYEXE}" "{TBCLI_PY}" list plots')
T("旧入口 list rpc", f'"{PYEXE}" "{TBCLI_PY}" list rpc')
T("旧入口 doctor", f'"{PYEXE}" "{TBCLI_PY}" doctor')
T("旧入口 plot 无参", f'"{PYEXE}" "{TBCLI_PY}" plot')
LOG.close()
print("PHASE7 DONE")

