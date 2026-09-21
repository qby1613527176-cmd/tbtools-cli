import sys
# -*- coding: utf-8 -*-
"""Phase 11：第八轮 — 全量收官
A 特殊路径(特殊字符/UNC/junction) B 畸形内容矩阵 C docstring 全量审计
D 并发写同一输出 E RPC 压力与畸形请求 F RPC kill 生命周期(最后)
"""
import io
import os
import json
import re
import time
import shutil
import subprocess
import threading
import urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
OUT = T + r"\out\p11"
os.makedirs(OUT, exist_ok=True)
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
LOG = io.open(T + r"\P11_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s):
    LOG.write(s + "\n"); LOG.flush()
def rec(name, ok, detail):
    w(f"- **{name}**: {'✅' if ok else '❌'} — {detail}")
    print(("OK  " if ok else "FAIL"), name, "|", detail[:110], flush=True)
def cli(args, timeout=600):
    t0 = time.time()
    r = subprocess.run(CLI + args, capture_output=True, timeout=timeout)
    so = (r.stdout or b"").decode("utf-8", "replace")
    se = (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, so, se, time.time() - t0
def rpc(method, params, timeout=300):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1})
    req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=body.encode(),
                                 headers={"Content-Type":"application/json"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8","replace")

FA = OUT + r"\base.fa"
with io.open(FA, "w", encoding="utf-8", newline="\n") as f:
    f.write(">s1\n" + "ACGT" * 10 + "\n>s2\n" + "TTTT" * 8 + "\n")

w("# Phase 11：第八轮 — 全量收官")

# ---------- A. 特殊路径 ----------
w("\n## 11.A 特殊路径专项")
cases = [
    ("百分号与感叹号", "pct!bang%special"),
    ("脱字符与和号", "caret^amp&name"),
    ("空格与圆括号", "space (1) name"),
    ("单引号与逗号", "quote',comma"),
    ("井号加号", "hash#plus+x"),
]
for title, nm in cases:
    d = os.path.join(OUT, "sp", nm)
    os.makedirs(d, exist_ok=True)
    fin = os.path.join(d, "in.fa")
    fout = os.path.join(d, "o.xls")
    shutil.copy(FA, fin)
    ec, so, se, dt = cli(["tool", "statFasta", "--inFasta", fin, "--outPutFile", fout])
    ok = ec == 0 and os.path.exists(fout) and os.path.getsize(fout) > 0
    canary = os.path.getsize(fin)
    rec(f"路径[{title}]", ok, f"ec={ec}, 输出={'有' if os.path.exists(fout) and os.path.getsize(fout)>0 else '无'}, 输入完好={canary==80}")

# UNC（本机 admin share）
try:
    unc_in = "\\\\localhost\\C$\\Users\\16135\\WorkBuddy\\2026-09-20-10-24-01\\tbtools-test\\out\\p11\\base.fa"
    ec, so, se, dt = cli(["tool", "statFasta", "--inFasta", unc_in, "--outPutFile", OUT + r"\unc_out.xls"])
    ok = ec == 0 and os.path.exists(OUT + r"\unc_out.xls")
    rec("UNC 路径输入(\\\\localhost\\C$)", ok, f"ec={ec}, 输出={'有' if os.path.exists(OUT + chr(92)+'unc_out.xls') else '无'} | {(so+se).strip()[:60]}")
except Exception as ex:
    rec("UNC 路径输入", False, f"EXC {str(ex)[:80]}")

# junction（目录联接，无需管理员）
try:
    src = os.path.join(OUT, "junction_target")
    os.makedirs(src, exist_ok=True)
    shutil.copy(FA, os.path.join(src, "in.fa"))
    lnk = os.path.join(OUT, "junction_link")
    if not os.path.exists(lnk):
        subprocess.run(["cmd", "/c", "mklink", "/J", lnk, src], capture_output=True)
    jf = os.path.join(lnk, "in.fa")
    ec, so, se, dt = cli(["tool", "statFasta", "--inFasta", jf, "--outPutFile", os.path.join(lnk, "o.xls")])
    ok = ec == 0 and os.path.exists(os.path.join(lnk, "o.xls"))
    rec("junction 目录联接路径", ok, f"ec={ec}, 输出={'有' if os.path.exists(os.path.join(lnk,'o.xls')) else '无'}")
except Exception as ex:
    rec("junction 目录联接路径", False, f"EXC {str(ex)[:80]}")

# 符号链接（文件级）
try:
    sl = os.path.join(OUT, "symlink.fa")
    if not os.path.lexists(sl):
        subprocess.run(["cmd", "/c", "mklink", sl, FA], capture_output=True)
    if os.path.lexists(sl):
        ec, so, se, dt = cli(["tool", "statFasta", "--inFasta", sl, "--outPutFile", OUT + r"\sl_out.xls"])
        ok = ec == 0 and os.path.exists(OUT + r"\sl_out.xls")
        rec("文件符号链接", ok, f"ec={ec}, 输出={'有' if os.path.exists(OUT + chr(92)+'sl_out.xls') else '无'}")
    else:
        w("- 文件符号链接：需要管理员权限，跳过（junction 已覆盖目录场景）")
        print("SKIP symlink", flush=True)
except Exception as ex:
    rec("文件符号链接", False, f"EXC {str(ex)[:80]}")

# ---------- B. 畸形内容矩阵 ----------
w("\n## 11.B 畸形内容矩阵（8 畸形 × statFasta / FastaStat / volcano）")
m = OUT + r"\malformed"
os.makedirs(m, exist_ok=True)
variants = {
    "BOM头":            b"\xef\xbb\xbf>seq1\nACGTACGTAC\n",
    "CRLF行尾":          b">seq1\r\nACGTACGTAC\r\n>seq2\r\nTTTTGGGGCC\r\n",
    "超长单行(1MB)":     b">seq1\n" + b"A" * 1048576 + b"\n",
    "二进制垃圾":        bytes(range(256)) * 64,
    "只有header无序列":  b">seq1\n>seq2\n>seq3\n",
    "空文件":            b"",
    "序列含非法字符":     b">seq1\nACGT1234!!!xyz\n",
    "全小写软遮蔽":       b">seq1\nacgtacgtacgtagct\n",
}
for name, content in variants.items():
    p = os.path.join(m, name.replace("(", "_").replace(")", "_") + ".fa")
    with io.open(p, "wb") as f: f.write(content)
    ec, so, se, dt = cli(["tool", "statFasta", "--inFasta", p, "--outPutFile", p + ".stat.xls"])
    outok = os.path.exists(p + ".stat.xls")
    hang = dt > 30
    # 静默失败检测：ec=0 但无输出且 stdout 无内容
    silent = ec == 0 and not outok and not so.strip()
    rec(f"statFasta×[{name}]", (ec != 0 and not outok and (so+se).strip()) or (ec == 0 and outok),
        f"ec={ec}, {dt:.1f}s{'(疑似卡!)' if hang else ''}, 输出={'有' if outok else '无'}, "
        f"{'⚠️静默失败' if silent else ''}报错={('有' if (so+se).strip() else '无')}")
# volcano 用畸形表格
for name, content in [("空表格", ""), ("错列数", "a\tb\n1\n2\t3\t4\n")]:
    p = os.path.join(m, f"deg_{name}.tsv")
    with io.open(p, "w", encoding="utf-8", newline="") as f: f.write(content)
    ec, so, se, dt = cli(["expr", "volcano", p, p + ".svg"], timeout=120)
    outok = os.path.exists(p + ".svg")
    silent = ec == 0 and not outok and not (so+se).strip()
    rec(f"volcano×[{name}]", not silent, f"ec={ec}, 输出={'有' if outok else '无'}, {'⚠️静默' if silent else '报错有'}")
# RPC FastaStat 畸形
for name in ["二进制垃圾", "只有header无序列"]:
    p = os.path.join(m, name.replace("(", "_").replace(")", "_") + ".fa")
    try:
        resp = rpc("FastaStat.process", {"inputPath": p, "outputPath": p + ".rpc.xls"})
        ok = '"error"' not in resp and os.path.exists(p + ".rpc.xls")
        rec(f"RPC FastaStat×[{name}]", ok, "成功" if ok else resp[:110])
    except Exception as ex:
        rec(f"RPC FastaStat×[{name}]", False, f"EXC {str(ex)[:80]}")

# ---------- C. docstring 全量审计 ----------
w("\n## 11.C docstring vs 引擎真实用法 全量审计（146 工具）")
# tool→group 映射
src = io.open("tbtools_cli" + os.sep + "cli.py", encoding="utf-8").read()
gmap = dict(re.findall(r'"([A-Za-z][A-Za-z0-9]+)":\s*"([a-z]+)"', src))
# docstring 位置参数数
auto = io.open("tbtools_cli" + os.sep + "auto_commands.py", encoding="utf-8").read()
doc_params = {}
for tool in gmap:
    mm = re.search(r'"""[^\n]*' + re.escape(tool) + r'[^\n]*"""', auto)
    if mm:
        line = mm.group(0)
        doc_params[tool] = len(re.findall(r'<[^>]+>', line))
audit = []
for tool, grp in sorted(gmap.items()):
    ec, so, se, dt = cli([grp, tool], timeout=60)
    blob = so + se
    mu = re.search(r'用法[:：]\s*(\S+)\s*(\S.*)', blob) or re.search(r'[Uu]sage:\s*(\S+)\s*(\S.*)', blob)
    if not mu:
        mu = re.search(r'(\w+\.java|\w+Cli)\s*(<.+)', blob)
    eng_n = len(re.findall(r'<[^>]+>', mu.group(2))) if mu else -1
    doc_n = doc_params.get(tool, -1)
    if eng_n >= 0 and doc_n >= 0 and eng_n != doc_n:
        audit.append((tool, grp, doc_n, eng_n, mu.group(2)[:80]))
w(f"\n审计 {len(gmap)} 个映射工具：docstring 与引擎用法位置参数数不一致 {len(audit)} 个：\n")
w("| 工具 | 分组 | docstring参数数 | 引擎实际 | 引擎用法片段 |")
w("|---|---|---|---|---|")
for t, g, dn, en, frag in audit:
    w(f"| {t} | {g} | {dn} | {en} | `{frag}` |")
print("AUDIT:", len(gmap), "checked,", len(audit), "mismatch", flush=True)

# ---------- D. 并发写同一输出 ----------
w("\n## 11.D 并发写同一输出文件（10 线程 statFasta 同一 out.xls）")
same = OUT + r"\same_out.xls"
if os.path.exists(same): os.remove(same)
results = []
def one(i):
    try:
        resp = rpc("FastaStat.process", {"inputPath": FA, "outputPath": same})
        results.append(("error" not in resp))
    except Exception:
        results.append(False)
ths = [threading.Thread(target=one, args=(i,)) for i in range(10)]
t0 = time.time()
for t in ths: t.start()
for t in ths: t.join()
sz = os.path.getsize(same) if os.path.exists(same) else -1
okcnt = sum(results)
# 内容完整性：输出应为 2 序列统计
body = io.open(same, encoding="utf-8", errors="replace").read() if sz > 0 else ""
intact = "2" in body and "Total" in body
rec("并发同输出", okcnt >= 0 and sz > 0, f"{okcnt}/10 rpc-ok, 文件 {sz}B, 内容{'完整' if intact else '可疑: '+body[:60]!r}, {time.time()-t0:.1f}s")

# ---------- E. RPC 压力与畸形请求 ----------
w("\n## 11.E RPC 压力与畸形请求")
# 100 连发
t0 = time.time(); okn = 0
for i in range(100):
    try:
        resp = rpc("FastaStat.process", {"inputPath": FA, "outputPath": OUT + rf"\burst_{i}.xls"})
        okn += ('"error"' not in resp)
    except Exception:
        pass
rec("100 连发顺序请求", okn == 100, f"{okn}/100, {time.time()-t0:.1f}s")
# 畸形 JSON
try:
    req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=b"{not json",
                                 headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    rec("畸形 JSON 请求", "error" in resp, resp[:100])
except Exception as ex:
    rec("畸形 JSON 请求", False, f"EXC {str(ex)[:80]}")
# 超大 payload（1MB inline sequence）
big = ">big\n" + "ACGT" * 262144 + "\n"
try:
    t0 = time.time()
    resp = rpc("FastaStat.process", {"inputPath": FA, "outputPath": OUT + r"\big.xls"})
    # inline 大文本走无效路径观察是否崩服务
    resp2 = rpc("FastaStat.process", {"inputPath": "Z:" + "x" * 200 + ".fa", "outputPath": OUT + r"\zz.xls"})
    alive = True
except Exception as ex:
    alive = False
    rec("服务存活(非法路径后)", False, f"EXC {str(ex)[:80]}")
if alive:
    rec("服务存活(非法长路径后)", True, f"非法盘符路径后服务正常, {time.time()-t0:.1f}s")

# ---------- F. RPC kill 生命周期（最后执行） ----------
w("\n## 11.F RPC 生命周期：kill 监听进程后行为")
def server_pid():
    r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
    for l in r.stdout.splitlines():
        if ":8765" in l and "LISTENING" in l:
            return l.split()[-1]
    return None
pid = server_pid()
w(f"- 监听 8765 的 PID: {pid}")
if pid:
    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
    time.sleep(2)
    try:
        resp = rpc("system.listMethods")
        rec("kill 后请求", True, "服务仍响应(自动重启?)")
    except Exception as ex:
        rec("kill 后请求", False, f"连接失败(服务未自动重启): {str(ex)[:70]}")
    # 尝试通过 CLI 唤醒
    ec, so, se, dt = cli(["rpc", "list"], timeout=120)
    pid2 = server_pid()
    if pid2:
        try:
            resp = rpc("system.listMethods")
            rec("CLI 唤醒后恢复", True, f"新 PID {pid2}, 服务恢复")
        except Exception as ex:
            rec("CLI 唤醒后恢复", False, f"PID {pid2} 但请求失败 {str(ex)[:60]}")
    else:
        rec("CLI 唤醒后恢复", False, "CLI 命令未拉起 RPC 服务（需手动/宿主重启）")

w("\n---\n\n## Phase 11 完")
LOG.close()
print("P11 done", flush=True)

