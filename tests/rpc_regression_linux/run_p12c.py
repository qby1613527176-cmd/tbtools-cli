import sys
# -*- coding: utf-8 -*-
"""P12c：RPC 残余自动救援（带重试与存活检查）"""
import io
import os
import json
import re
import time
import subprocess
import urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
PUB = T + r"\data\public"
OUT = T + r"\out\p12"
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
E = "examples/data"
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P12C_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s):
    LOG.write(s + "\n"); LOG.flush()

def restart_rpc():
    subprocess.Popen(CLI + ["rpc", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(15):
        time.sleep(2)
        try:
            rpc("system.listMethods", {}, timeout=10)
            return True
        except Exception:
            pass
    return False

def rpc(method, params=None, timeout=240, retry=2):
    for attempt in range(retry + 1):
        try:
            body = json.dumps({"jsonrpc":"2.0","method":method,"params":params or {},"id":1})
            req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=body.encode(),
                                         headers={"Content-Type":"application/json"})
            return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8","replace")
        except Exception:
            if attempt >= retry:
                raise
            if not restart_rpc():
                raise

SKIP = re.compile(r"ncbi|timetree|sra|geo|fastqblast|blastzone|download|remote|email|todo", re.I)
POOL = {"gtf": [PUB + r"\gencode_head50k.gtf"], "gff": [os.path.abspath(f"{E}/gxf/input.gff3")],
        "gff3": [os.path.abspath(f"{E}/gxf/input.gff3")], "bed": [OUT + r"\p12_gencode.bed"],
        "fa": [os.path.abspath(f"{E}/blast/query.fa")], "fasta": [os.path.abspath(f"{E}/blast/query.fa")],
        "tsv": [os.path.abspath(f"{E}/deg.txt")], "table": [os.path.abspath(f"{E}/deg.txt")],
        "xls": [os.path.abspath(f"{E}/chipseq/peak_std.xls")], "txt": [os.path.abspath(f"{E}/deg.txt")],
        "xml": [OUT + r"\p12_blast_f5.txt"], "tga": [os.path.abspath(f"{E}/efp/plant_bg.tga")],
        "img": [os.path.abspath(f"{E}/efp/plant_bg.tga")], "png": [os.path.abspath(f"{E}/efp/plant_bg.tga")]}
report = io.open(T + r"\FINAL_TEST_REPORT_V3.md", encoding="utf-8", errors="replace").read()
report_pass = set(re.findall(r'\b([A-Za-z]+)\.process\b', report)) | set(re.findall(r'### ([A-Za-z]+) [—→]', report))
names = json.loads(rpc("system.listMethods")).get("result")
names = names.get("methods") if isinstance(names, dict) else names
procs = [m for m in names if isinstance(m, str) and m.endswith(".process") and not SKIP.search(m)]
w(f"# P12c：RPC 残余自动救援\n\n候选 {len(procs)} 个\n")
print(f"候选 {len(procs)} 个", flush=True)
new_pass, fails, server_died = [], [], 0
for m in procs:
    base = m.split(".")[0]
    try:
        d = json.loads(rpc("system.describeMethod", {"method": m})).get("result", {})
        desc = json.dumps(d.get("description", {}), ensure_ascii=False)
        dlow = desc.lower()
        try:
            vres = json.loads(rpc(m.replace(".process", ".validateParams"), {}, timeout=30))
            verr = json.dumps(vres.get("error", vres.get("result", {})), ensure_ascii=False)
        except Exception:
            verr = ""
        need = list(dict.fromkeys(re.findall(r'([A-Za-z][A-Za-z0-9]+)[ _]is required', verr)))
        if not need:
            need = list(dict.fromkeys(re.findall(r'"([A-Za-z][A-Za-z0-9]+)":\s*"[^"]*required', desc)))
        params = {}
        for p in need:
            pl = p.lower()
            if "output" in pl or pl.startswith("out"):
                params[p] = OUT + rf"\p12c_{base}_{p}.out"
            else:
                match = None
                for k, v in POOL.items():
                    if k in pl: match = v[0]; break
                if not match:
                    for k, v in POOL.items():
                        if k in dlow: match = v[0]; break
                params[p] = match if match else os.path.abspath(f"{E}/deg.txt")
        t0 = time.time()
        resp = rpc(m, params)
        ok = '"error"' not in resp
        if ok and base not in report_pass:
            new_pass.append(base)
        print(("NEWPASS " if ok and base not in report_pass else ("pass    " if ok else "fail    ")) + base,
              f"need={','.join(need)[:36]}", f"{time.time()-t0:.1f}s", flush=True)
        if not ok:
            msg = json.loads(resp).get("error", {}).get("data", {}).get("message", "")
            fails.append((base, ",".join(need), msg[:70]))
    except Exception as ex:
        if "10054" in str(ex) or "502" in str(ex) or "Connection" in str(ex):
            server_died += 1
            restart_rpc()
        fails.append((base, "-", "EXC " + str(ex)[:70]))
        print("err     ", base, flush=True)

w("\n## 本轮新通过\n\n" + (", ".join(sorted(set(new_pass))) if new_pass else "（无新增）"))
w(f"\n## 仍失败 {len(fails)}（含服务死亡 {server_died} 次）\n")
w("| 方法 | 需填参数 | 错误 |")
w("|---|---|---|")
for b, need, msg in fails:
    w(f"| {b} | {need} | {msg} |")
print("\nNEW PASS:", ", ".join(sorted(set(new_pass))) if new_pass else "(无)", flush=True)
print("FAILS:", len(fails), "server_died:", server_died, flush=True)
w("\n\n## Phase 12c 完")
LOG.close()
print("P12c done", flush=True)

