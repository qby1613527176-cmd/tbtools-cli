import sys
# -*- coding: utf-8 -*-
"""P14c：定向收敛 GxfGeneDensityProfiler 与 OneStepBuildATree"""
import io
import os
import json
import time
import subprocess
import urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
for k in ("HTTP_PROXY","http_proxy","HTTPS_PROXY","https_proxy","ALL_PROXY","all_proxy"):
    os.environ.pop(k, None)
os.environ["NO_PROXY"] = "127.0.0.1,localhost"
os.environ["no_proxy"] = "127.0.0.1,localhost"
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P14C_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s): LOG.write(s + "\n"); LOG.flush()
def rpc(m, p=None, timeout=60):
    b = json.dumps({"jsonrpc":"2.0","method":m,"params":p or {},"id":1}).encode()
    return urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:8765/rpc", data=b,
        headers={"Content-Type":"application/json"}), timeout=timeout).read().decode("utf-8","replace")
def alive():
    try: rpc("system.listMethods", {}, 8); return True
    except Exception: return False
if not alive():
    subprocess.Popen(CLI + ["rpc", "start"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        time.sleep(2)
        if alive(): break
w("# P14c 定向收敛\n")

GFF3 = os.path.abspath("examples/data/gxf/input.gff3")
GFF3b = os.path.abspath("examples/data/gene_structure.gff")
msa = T + r"\out\p13\msa.fa"
OUT = T + r"\out\p14"

# ---- 1) GxfGeneDensityProfiler：先看 describe，再试参数名变体 ----
d = json.loads(rpc("system.describeMethod", {"method":"GxfGeneDensityProfiler.process"}))
w("## GxfGeneDensityProfiler describe\n```json\n" +
  json.dumps(d, ensure_ascii=False, indent=1)[:2500] + "\n```\n")
base = {"inputPath": GFF3, "binSize": 100, "outputPath": OUT + r"\p14c_gdp.xls"}
variants = [
    ("seed原名", dict(base, featurePattern="gene")),
    ("featurePatterns复数", dict(base, featurePatterns="gene")),
    ("feature单数", dict(base, feature="gene")),
    ("featureType", dict(base, featureType="gene")),
    ("features", dict(base, features="gene")),
]
gdp_ok = None
for name, params in variants:
    try:
        r = rpc("GxfGeneDensityProfiler.process", params, 240)
        if '"error"' not in r:
            gdp_ok = name; w(f"- PASS `{name}`"); print("PASS", name, flush=True); break
        e = json.loads(r).get("error", {})
        msg = (e.get("data", {}).get("message") if isinstance(e.get("data"), dict) else e.get("data")) or e.get("message") or ""
        w(f"- FAIL `{name}`: {str(msg)[:150]}")
        print("fail", name, str(msg)[:100], flush=True)
    except Exception as ex:
        w(f"- ERR `{name}`: {ex}"); print("err", name, str(ex)[:100], flush=True)

# ---- 2) OneStepBuildATree：900s 长超时重试 ----
d2 = json.loads(rpc("system.describeMethod", {"method":"OneStepBuildATree.process"}))
w("\n## OneStepBuildATree describe\n```json\n" +
  json.dumps(d2, ensure_ascii=False, indent=1)[:2500] + "\n```\n")
try:
    r = rpc("OneStepBuildATree.process",
            {"inputPath": msa, "outputPath": OUT + r"\p14c_tree.nwk"}, 900)
    if '"error"' not in r:
        w("- PASS 900s 长超时"); print("PASS tree", flush=True)
    else:
        e = json.loads(r).get("error", {})
        msg = (e.get("data", {}).get("message") if isinstance(e.get("data"), dict) else e.get("data")) or e.get("message") or ""
        w(f"- FAIL: {str(msg)[:200]}"); print("fail tree", str(msg)[:120], flush=True)
except Exception as ex:
    w(f"- ERR 900s 仍超时: {ex}"); print("err tree", str(ex)[:120], flush=True)

w("\n## Phase 14c 完")
LOG.close()
print("P14c done", flush=True)

