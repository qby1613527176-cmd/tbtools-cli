import sys
# -*- coding: utf-8 -*-
"""Phase 10b：长路径(\\?\前缀) + 只读目录 + FastaSsrMiner/GxfGenomeMatch 参数反查重试"""
import io, os, json, time, stat, shutil, urllib.request, subprocess

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
PUB = T + r"\data\public"
OUT = T + r"\out\p10"
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
LOG = io.open(T + r"\P10B_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s):
    LOG.write(s + "\n"); LOG.flush()
def rpc(method, params, timeout=900):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1})
    req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=body.encode(),
                                 headers={"Content-Type":"application/json"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8","replace")
def rec(name, ok, detail):
    w(f"- **{name}**: {'✅' if ok else '❌'} — {detail}")
    print(("OK  " if ok else "FAIL"), name, "|", detail[:110], flush=True)

w("# Phase 10b：长路径 / 只读目录 / 参数反查重试")

# E. 长路径（\\?\ 扩展前缀构造）
w("\n## 10.E 长路径（>260 字符，\\?\\ 前缀构造）")
deep = OUT + r"\p10_deep"
leaf = deep
while len(leaf) < 270:
    leaf = os.path.join(leaf, "级别" + "x" * 30)
leaf_w = "\\\\?\\" + leaf
try:
    os.makedirs(leaf_w, exist_ok=True)
    src = OUT + r"\p10_中文ID.fa"
    lp = os.path.join(leaf_w, "seq.fa")
    shutil.copy("\\\\?\\" + src, lp)
    out_lp = os.path.join(leaf_w, "stat.xls")
    t0 = time.time()
    r = subprocess.run(CLI + ["tool", "statFasta", "--inFasta", lp, "--outPutFile", out_lp],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    ok = r.returncode == 0 and os.path.exists("\\\\?\\" + out_lp)
    rec("statFasta 长路径(%d 字符)" % len(leaf), ok,
        f"ec={r.returncode}, {time.time()-t0:.1f}s, 输出={'有' if os.path.exists('\\\\\\\\?\\\\'+out_lp) else '无'}"
        + (("" if ok else " | " + (r.stdout + r.stderr).strip()[:120])))
except Exception as ex:
    rec("statFasta 长路径", False, f"构造/执行异常: {str(ex)[:120]}")

# F. 只读目录
w("\n## 10.F 只读目录")
ro = OUT + r"\p10_readonly"
os.makedirs(ro, exist_ok=True)
rofile = os.path.join(ro, "in.fa")
shutil.copy(OUT + r"\p10_中文ID.fa", rofile)
os.chmod(ro, stat.S_IREAD | stat.S_IEXEC)
try:
    t0 = time.time()
    r = subprocess.run(CLI + ["tool", "statFasta", "--inFasta", rofile, "--outPutFile", os.path.join(ro, "out.xls")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    out_exists = os.path.exists(os.path.join(ro, "out.xls"))
    blob = r.stdout + r.stderr
    err_mentioned = any(k in blob for k in ("拒绝", "denied", "Permission", "失败", "Error", "❌", "error", "错"))
    rec("只读目录输出", (r.returncode != 0) and not out_exists and err_mentioned,
        f"ec={r.returncode}, 产物={'意外存在!' if out_exists else '未创建(正确)'}, 错误提示={'有' if err_mentioned else '无(静默)'}")
finally:
    os.chmod(ro, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)

# 反查参数名重试
w("\n## 10.G' FastaSsrMiner / GxfGenomeMatch describeMethod 反查")
genome = PUB + r"\grch38_head60m.fa"
gtf = PUB + r"\gencode_head50k.gtf"
for m in ["FastaSsrMiner.process", "GxfGenomeMatch.process"]:
    try:
        d = json.loads(rpc("system.describeMethod", {"method": m})).get("result", {})
        w(f"- `{m}`: {json.dumps(d.get('description',{}), ensure_ascii=False)[:340]}")
        print("DESC", m, flush=True)
    except Exception as ex:
        w(f"- `{m}`: describe 异常 {str(ex)[:80]}")

# 用反查结果重试（合理猜测：SsrMiner 可能要 minLength 等 options；GxfGenomeMatch 参数名对齐）
for name, method, params in [
    ("FastaSsrMiner ← 240MB（inputPath/outputPath）", "FastaSsrMiner.process",
     {"inputPath": genome, "outputPath": OUT + r"\p10_ssr.xls"}),
    ("GxfGenomeMatch（gxfPath/genomePath）", "GxfGenomeMatch.process",
     {"gxfPath": gtf, "genomePath": genome, "outputPath": OUT + r"\p10_gmatch.gff3"}),
]:
    t0 = time.time()
    try:
        resp = rpc(method, params)
        ok = '"error"' not in resp
        msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "") if not ok else "成功"
        rec(name, ok, f"{time.time()-t0:.1f}s {msg[:120]}")
    except Exception as ex:
        rec(name, False, f"EXC {str(ex)[:100]}")

w("\n## Phase 10b 完")
LOG.close()
print("P10b done", flush=True)

