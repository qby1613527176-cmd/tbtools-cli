import sys
# -*- coding: utf-8 -*-
"""Phase 9b：并发重测（真方法名）+ N22 GTF 交叉重测（真参数名）+ 9.1/9.2/9.3 verbose 堆栈"""
import io, os, subprocess, threading, time, json, urllib.request

os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
PY = sys.executable
CLI = [PY, "-m", "tbtools_cli.cli"]
OUT = r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test\out\p9"
O = OUT.replace("\\", "/")
E = "examples/data"
LOG = io.open(r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test\P9B_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s):
    LOG.write(s + "\n"); LOG.flush()

def rpc(method, params, timeout=180):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1})
    req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=body.encode(),
                                 headers={"Content-Type":"application/json"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8","replace")

w("# Phase 9b：并发重测 + N22 GTF 交叉重测 + 遗留堆栈")

# ---------- C'. 并发 10 路（FastaStat.process，真参数名） ----------
w("\n## 9.C' RPC 并发 10 路（FastaStat.process，inputPath/outputPath）\n")
results = []
def rpc_call(i):
    try:
        t0 = time.time()
        resp = rpc("FastaStat.process", {
            "inputPath": os.path.abspath(f"{E}/blast/query.fa"),
            "outputPath": f"{O}\\p9_conc_{i}.xls"})
        dt = time.time() - t0
        ok = '"error"' not in resp and os.path.exists(f"{O}/p9_conc_{i}.xls")
        results.append((i, ok, dt, resp[:100]))
    except Exception as ex:
        results.append((i, False, -1, str(ex)[:100]))
ths = [threading.Thread(target=rpc_call, args=(i,)) for i in range(10)]
t0 = time.time()
for t in ths: t.start()
for t in ths: t.join()
nok = sum(1 for _, ok, _, _ in results if ok)
w("| 线程 | 成功 | 耗时s | 备注 |")
w("|---|---|---|---|")
for i, ok, dt, note in sorted(results):
    w(f"| {i} | {'✅' if ok else '❌'} | {dt:.2f} | {note[:70]} |")
w(f"\n**并发结论：{nok}/10 成功，总耗时 {time.time()-t0:.1f}s**")
print("CONC:", nok, "/10", flush=True)

# ---------- B'. N22 GTF 交叉（真参数名） ----------
w("\n## 9.B' N22 族 GTF 交叉重测（describeMethod 真参数名）\n")
gtf = os.path.abspath(r"..\tbtools-test\out\p9\p9_test.gtf")
gff3 = os.path.abspath(f"{E}/gxf/input.gff3")
for name, method, params in [
    ("GxfRecallMrna ← GTF", "GxfRecallMrna.process", {"inputPath": gtf, "outputPath": f"{O}\\p9_recall_out.gff3"}),
    ("GxfRecallMrna ← GFF3(对照)", "GxfRecallMrna.process", {"inputPath": gff3, "outputPath": f"{O}\\p9_recall_ctl.gff3"}),
    ("GxfPatch ← GTF+GFF3", "GxfPatch.process", {"refGxfPath": gtf, "patchGxfPath": gff3, "outputPath": f"{O}\\p9_patch_out.gff3"}),
    ("GxfSplit ← GTF", "GxfSplit.process", {"inputPath": gtf, "outputPrefix": f"{O}\\p9_split", "numOfFile": 2}),
]:
    try:
        t0 = time.time()
        resp = rpc(method, params)
        dt = time.time() - t0
        ok = '"error"' not in resp
        w(f"\n### {name}")
        w("```json"); w(resp[:400]); w("```")
        w(f"\n→ **{'✅ PASS' if ok else '❌ FAIL'}**（{dt:.1f}s）")
        print(("OK  " if ok else "FAIL"), name, flush=True)
    except Exception as ex:
        w(f"\n### {name}\nRPC 异常：{ex}")
        print("ERR ", name, flush=True)

# ---------- verbose 堆栈 ----------
w("\n## 9.D 9.1/9.2/9.3 verbose 完整堆栈\n")
for name, args in [
    ("layoutheatmap", ["expr", "layoutheatmap", f"{E}/expr/layout.tsv", f"{E}/expr/expr.tsv", f"{O}/p9_layoutheat.svg", "--verbose"]),
    ("multiEfp", ["expr", "multiEfp", f"{E}/efp/plant_bg.tga", f"{E}/efp/sample2cc.txt", f"{E}/efp/expmat.tsv", "AT1G01010", f"{O}/p9_multiefp.svg", "--verbose"]),
    ("mirnaIdentify", ["mirna", "mirnaIdentify", f"{E}/mirna/mirnaIdentify/positive_ctrl_genome.fa",
                       f"{E}/mirna/mirnaIdentify/positive_ctrl_target.tsv", f"{O}/p9_mirpredict.txt", "--verbose"]),
]:
    r = subprocess.run(CLI + args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    w(f"\n### {name} (ec={r.returncode})")
    w("```")
    txt = (r.stdout or "") + (r.stderr or "")
    keep = [l for l in txt.splitlines() if any(k in l for k in ("Exception", "Error", "at bio", "at tb", "at Layout", "at Multi", "at Mir", "Caused"))]
    for l in keep[:12]: w(l)
    if not keep: w(txt.strip()[:400])
    w("```")
    print("STACK", name, flush=True)

w("\n## Phase 9b 完")
LOG.close()
print("P9b done", flush=True)

