import sys
# -*- coding: utf-8 -*-
"""Phase 11c：docstring 审计（防挂死版）+ D/E/F 补跑
教训：no-arg 调用某些工具会挂起且 Windows 下 subprocess 超时杀不净 java 子进程。
对策：timeout=20s + 超时后 taskkill /T /F 清树 + 每工具打印进度。
"""
import io, os, json, re, time, subprocess, threading, urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
OUT = T + r"\out\p11"
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
LOG = io.open(T + r"\P11C_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s):
    LOG.write(s + "\n"); LOG.flush()
def rec(name, ok, detail):
    w(f"- **{name}**: {'✅' if ok else '❌'} — {detail}")
    print(("OK  " if ok else "FAIL"), name, "|", detail[:110], flush=True)
def rpc(method, params, timeout=300):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1})
    req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=body.encode(),
                                 headers={"Content-Type":"application/json"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8","replace")

FA = OUT + r"\base.fa"

w("# Phase 11c：docstring 审计（防挂死）+ 并发同写 / RPC 压力 / kill 生命周期")

# ---------- C'. docstring 审计 ----------
w("\n## 11.C' docstring vs 引擎真实用法（146 工具，20s 超时+杀树）")
src = io.open("tbtools_cli" + os.sep + "cli.py", encoding="utf-8").read()
gmap = dict(re.findall(r'"([A-Za-z][A-Za-z0-9]+)":\s*"([a-z]+)"', src))
auto = io.open("tbtools_cli" + os.sep + "auto_commands.py", encoding="utf-8").read()
doc_params = {}
for tool in gmap:
    mm = re.search(r'"""[^\n]*' + re.escape(tool) + r'[^\n]*"""', auto)
    if mm:
        doc_params[tool] = len(re.findall(r'<[^>]+>', mm.group(0)))

def run_noarg(grp, tool, timeout=20):
    p = subprocess.Popen(CLI + [grp, tool], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        so, se = p.communicate(timeout=timeout)
        blob = so.decode("utf-8", "replace") + se.decode("utf-8", "replace")
        return blob, False
    except subprocess.TimeoutExpired:
        # 杀整棵树
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
        try:
            so, se = p.communicate(timeout=5)
            blob = (so or b"").decode("utf-8", "replace") + (se or b"").decode("utf-8", "replace")
        except Exception:
            blob = ""
        return blob, True

audit, hung_tools, nomsg = [], [], []
n = 0
for tool, grp in sorted(gmap.items()):
    n += 1
    blob, hung = run_noarg(grp, tool)
    if hung:
        hung_tools.append((tool, grp)); print(f"[{n}/{len(gmap)}] {grp} {tool} HUNG(20s)", flush=True)
        continue
    mu = re.search(r'用法[:：]\s*\S+\s*(\S.*)', blob) or re.search(r'[Uu]sage:\s*\S+\s*(\S.*)', blob)
    if not mu:
        nomsg.append((tool, grp)); print(f"[{n}/{len(gmap)}] {grp} {tool} no-usage-msg", flush=True)
        continue
    eng_n = len(re.findall(r'<[^>]+>', mu.group(1)))
    doc_n = doc_params.get(tool, -1)
    if doc_n >= 0 and eng_n != doc_n:
        audit.append((tool, grp, doc_n, eng_n, mu.group(1)[:90]))
        print(f"[{n}/{len(gmap)}] {grp} {tool} MISMATCH doc={doc_n} eng={eng_n}", flush=True)
    else:
        print(f"[{n}/{len(gmap)}] {grp} {tool} ok", flush=True)

w(f"\n审计 {len(gmap)} 个映射工具：参数数不一致 **{len(audit)}**、挂起(20s 无响应) **{len(hung_tools)}**、"
  f"无用法信息 **{len(nomsg)}**\n")
w("### 参数数不一致（N29 同族）\n")
w("| 工具 | 分组 | docstring | 引擎实际 | 引擎用法片段 |")
w("|---|---|---|---|---|")
for t, g, dn, en, frag in audit:
    w(f"| {t} | {g} | {dn} | {en} | `{frag}` |")
w("\n### no-arg 挂起清单（本身即可用性缺陷候选）\n")
if hung_tools:
    w("| 工具 | 分组 |\n|---|---|")
    for t, g in hung_tools: w(f"| {t} | {g} |")
else:
    w("（无）")
w("\n### 无用法信息清单\n")
if nomsg:
    w("| 工具 | 分组 |\n|---|---|")
    for t, g in nomsg: w(f"| {t} | {g} |")
else:
    w("（无）")

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
body = io.open(same, encoding="utf-8", errors="replace").read() if sz > 0 else ""
intact = "Total" in body and "2" in body
rec("并发同输出", sz > 0 and intact,
    f"{sum(results)}/10 rpc-ok, 文件 {sz}B, 内容{'完整' if intact else '可疑: ' + body[:50]!r}, {time.time()-t0:.1f}s")

# ---------- E. RPC 压力与畸形请求 ----------
w("\n## 11.E RPC 压力与畸形请求")
t0 = time.time(); okn = 0
for i in range(100):
    try:
        resp = rpc("FastaStat.process", {"inputPath": FA, "outputPath": OUT + rf"\burst_{i}.xls"})
        okn += ('"error"' not in resp)
    except Exception:
        pass
rec("100 连发顺序请求", okn == 100, f"{okn}/100, {time.time()-t0:.1f}s")
try:
    req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=b"{not json",
                                 headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    rec("畸形 JSON 请求", "error" in resp, resp[:100])
except Exception as ex:
    rec("畸形 JSON 请求", False, f"EXC {str(ex)[:80]}")
try:
    t0 = time.time()
    rpc("FastaStat.process", {"inputPath": "Z:" + "x" * 200 + ".fa", "outputPath": OUT + r"\zz.xls"})
    rec("服务存活(非法盘符路径后)", True, f"返回错误后服务正常, {time.time()-t0:.1f}s")
except Exception as ex:
    rec("服务存活(非法盘符路径后)", False, f"EXC {str(ex)[:80]}")

# ---------- F. RPC kill 生命周期 ----------
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
        rpc("system.listMethods")
        rec("kill 后请求", True, "服务仍响应(自动重启?)")
    except Exception as ex:
        rec("kill 后请求", False, f"连接失败(未自动重启): {str(ex)[:70]}")
    ec_r = subprocess.run(CLI + ["engine", "status"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=60)
    time.sleep(1)
    pid2 = server_pid()
    if pid2:
        try:
            rpc("system.listMethods")
            rec("CLI 交互后恢复", True, f"新 PID {pid2}, 服务恢复")
        except Exception as ex:
            rec("CLI 交互后恢复", False, f"PID {pid2} 但请求失败 {str(ex)[:60]}")
    else:
        rec("CLI 交互后恢复", False, "未自动拉起（RPC 需宿主重启，生命周期结论：服务不可自愈）")
else:
    rec("kill 生命周期", False, "未找到监听进程（服务可能已不在）")

w("\n---\n\n## Phase 11c 完")
LOG.close()
print("P11c done", flush=True)

