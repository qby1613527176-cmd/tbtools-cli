import sys
#!/usr/bin/env python
"""Phase3: RPC 188 方法全量盘点 + 可映射方法实跑（原样 JSON 响应）"""
import io, json, os, subprocess, sys, time, urllib.request

os.environ.setdefault("TBTOOLS_JAR", "C:/Program Files/TBtools/TBtools_JRE1.6.jar")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
LOG = io.open("P3_LOG.md", "w", encoding="utf-8", newline="\n")
D = os.getcwd().replace("\\", "/")
RPC = "http://127.0.0.1:8765/rpc"
SHELL = os.environ.get("SHELL", "bash")
RPCSH = os.path.join(os.environ["TBROOT"], "bin", "tbtools_rpc.sh")

def w(s=""):
    LOG.write(s + "\n"); LOG.flush()

def rpc(method, params, timeout=300):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params})
    t0 = time.time()
    try:
        req = urllib.request.Request(RPC, data=body.encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            txt = r.read().decode("utf-8", "replace")
        return txt, 0, time.time() - t0
    except Exception as e:
        return json.dumps({"error": str(e)}), 1, time.time() - t0

def block(txt, ec, dt, limit=6000):
    t = txt if len(txt) <= limit else txt[:limit] + f"\n…[截断, 共{len(txt)}字符]"
    return f"```\n{t.rstrip()}\n```\n\n退出码 `{ec}` · {dt:.1f}s"

# 确保 RPC 服务器活着
subprocess.run(["bash", RPCSH, "start"], capture_output=True, timeout=60)

w("# Phase 3：RPC 数据服务全量测试\n")
w("## 一、system.listMethods（188 方法全名单）\n")
w("```bash\ntbtools_rpc.sh methods\n```")
txt, ec, dt = rpc("system.listMethods", {})
w(block(txt, ec, dt))
try:
    methods = json.loads(txt)["result"]
except Exception:
    methods = []
if isinstance(methods, dict):
    methods = methods.get("methods", list(methods.keys()))
w(f"\n方法总数: **{len(methods)}**\n")

w("\n## 二、逐方法实测（可映射子集，全量 JSON 响应）\n")
P = lambda p: f"{D}/{p}"
CALLS = [
 ("FastaStat.process", {"inputPath": P("out/pin_family_full.fa"), "outputPath": P("out/r3_fastastat.xls")}),
 ("FastaExtract.process", {"inputPath": P("data/monarda_chloro_pep.fa"), "idListPath": P("out/chloro_ids.txt"), "outputPath": P("out/r3_extract.fa")}),
 ("CdsToProtein.process", {"inputPath": P("data/monarda_chloro_cds.fa"), "outputPath": P("out/r3_cds2pep.fa")}),
 ("FastaSsrMiner.process", {"inputPath": P("data/monarda_chloro.clean.fa"), "outputPath": P("out/r3_ssr.xls")}),
 ("AmazingHeatMap.process", {"matrixPath": P("out/atpin_sipin_matrix.tsv"), "outputPath": P("out/r3_heatmap.png"), "options": {"showWindow": False}}),
 ("ExpressionCorrMatrix.process", {"inputPath": P("out/pin_expr.tsv"), "outputPath": P("out/r3_exprcorr.tsv")}),
 ("GxfToGenePos.process", {"inputPath": P("data/monarda_chloro.gff3"), "chrLenPath": P("data/chloro_chrlen.tsv"), "outputPath": P("out/r3_genepos.tsv")}),
 ("QuickGeneFamilyIdentification.process", {"QueryPepSet": P("out/pin10.fa"), "ReferencePepSet": P("out/pin_family_full.fa"), "ReferenceFamilyId": P("out/pin10_ids.txt"), "OutFilePrefix": P("out/r3_qf"), "NumOfThreads": 4}),
 ("TableTools.tableTranspose", {"inputPath": P("out/pin_expr.tsv"), "outputPath": P("out/r3_transpose.tsv")}),
 ("TableTools.tableUniq", {"inputPath": P("out/pin_expr.tsv"), "colIndex": 0, "outputPath": P("out/r3_uniq.txt")}),
 ("CheckPrimer.process", {"genomeFile": P("data/monarda_chloro.clean.fa"), "primerFile": P("out/p2_primer.tsv"), "outputPath": P("out/r3_primer.xls")}),
]
for m, params in CALLS:
    w(f"\n### rpc {m}")
    w("```json\n" + json.dumps({"method": m, "params": params}, ensure_ascii=False) + "\n```")
    txt, ec, dt = rpc(m, params)
    w(block(txt, ec, dt))
    print("RPC", m)

# 其余方法逐个用空参数调用，记录真实错误响应（参数校验回显也是行为证据）
rest = [m for m in methods if m not in {c[0] for c in CALLS} and m not in ("system.listMethods",)]
w(f"\n## 三、其余 {len(rest)} 个方法空参调用（记录引擎真实参数校验响应）\n")
for i, m in enumerate(rest, 1):
    txt, ec, dt = rpc(m, {}, timeout=60)
    short = txt if len(txt) <= 900 else txt[:900] + " …"
    w(f"\n### {m}\n```json\n{short.rstrip()}\n```\n*（空参调用 · {dt:.1f}s）*")
    if i % 20 == 0: print(f"rest {i}/{len(rest)}")
LOG.close()
print("PHASE3 DONE", len(methods))

