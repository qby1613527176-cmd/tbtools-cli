import sys
# -*- coding: utf-8 -*-
"""P14b：A 段 6 方法迭代收敛（错误回显驱动，8 轮上限）"""
import io, os, json, re, time, subprocess, urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
# 本会话注入了 HTTP_PROXY → 会劫持对 127.0.0.1:8765 的请求，必须禁用
for _k in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy",
           "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)
os.environ["NO_PROXY"] = "127.0.0.1,localhost"
os.environ["no_proxy"] = "127.0.0.1,localhost"
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
OUT = T + r"\out\p14"
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
E = "examples/data"
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P14B_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s):
    LOG.write(s + "\n"); LOG.flush()
def rpc(method, params=None, timeout=240):
    body = json.dumps({"jsonrpc":"2.0","method":method,"params":params or {},"id":1})
    req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=body.encode(),
                                 headers={"Content-Type":"application/json"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8","replace")
def alive():
    try:
        rpc("system.listMethods", {}, timeout=8); return True
    except Exception:
        return False
def ensure():
    if alive(): return True
    subprocess.Popen(CLI + ["rpc", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(20):
        time.sleep(2)
        if alive(): return True
    return False
def call(m, p):
    for _ in range(3):
        if not ensure(): return None, "SERVER_DOWN"
        try: return rpc(m, p, timeout=300), "ok"
        except Exception as ex:
            last = str(ex); time.sleep(1)
    return None, last

FA = os.path.abspath(f"{E}/blast/query.fa"); FA2 = os.path.abspath(f"{E}/blast/subject.fa")
GFF3 = os.path.abspath(f"{E}/gxf/input.gff3"); GFF3b = os.path.abspath(f"{E}/gene_structure.gff")
DEG = os.path.abspath(f"{E}/deg.txt"); CHRL = os.path.abspath(f"{E}/synteny/chrlen.txt")
IDLIST = os.path.abspath(f"{E}/fasta/extract.idlist.txt")
genome_small = T + r"\out\p13\genome2m.fa"; msa = T + r"\out\p13\msa.fa"
def O(n): return OUT + "\\" + n

SEED = {
    "FastaWindowStat": {"inputPath": genome_small, "windowSize": 1000, "windowOverlap": 50, "outputPath": O("p14b_fws.xls")},
    "GxfGeneDensityProfiler": {"inputPath": GFF3, "binSize": 100, "featurePattern": "gene", "outputPath": O("p14b_gdp.xls")},
    "OneStepBuildATree": {"inputPath": msa, "outputPath": O("p14b_tree.nwk")},
    "GffExtractRegion": {"gxfPath": GFF3b, "regionListPath": T + r"\out\p10\p10_regions.tsv", "outputPath": O("p14b_ger.gff3")},
    "GxfToGenePos": {"inputPath": GFF3, "chrLenPath": CHRL, "outputPath": O("p14b_gtp.pos")},
    "TableRowManipulator": {"inputPath": DEG, "selectedColumn": 1, "idListPath": IDLIST, "outputPath": O("p14b_trm.tsv")},
}
POOL = [  # (名/描述关键词, 值)
    (r"chrlen|len", CHRL), (r"idlist|ids", IDLIST), (r"region", T + r"\out\p10\p10_regions.tsv"),
    (r"msa|align", msa), (r"genome|window", genome_small), (r"gtf", T + r"\out\p9\p9_test.gtf"),
    (r"gff", GFF3b), (r"gxf", GFF3), (r"pep|protein|fa\b|fasta|seq", FA),
    (r"expr|deg|table|tsv|xls|txt", DEG), (r"tree", os.path.abspath(f"{E}/phylogeny/phylo.nwk")),
]
def fill(pname, desc):
    pl = pname.lower()
    if "output" in pl or pl.startswith("out") or "prefix" in pl:
        return OUT + rf"\p14b_{pname}.out"
    for pat, v in POOL:
        if re.search(pat, pl): return v
    for pat, v in POOL:
        if re.search(pat, desc.lower()): return v
    return DEG

w("# P14b：6 方法迭代收敛（8 轮上限）\n")
final_pass, final_fail = [], []
for base, seed in SEED.items():
    try:
        d = json.loads(rpc("system.describeMethod", {"method": base + ".process"})).get("result", {})
        desc = json.dumps(d.get("description", {}), ensure_ascii=False)
    except Exception:
        desc = ""
    params = dict(seed)
    ok = False; msg = ""; rounds = 0
    for round_i in range(8):
        rounds = round_i + 1
        resp, err = call(base + ".process", params)
        if resp is None:
            msg = "SERVER: " + err; break
        if '"error"' not in resp:
            ok = True; msg = f"第 {rounds} 轮收敛"; break
        try:
            e = json.loads(resp).get("error", {})
            msg = (e.get("data", {}).get("message") if isinstance(e.get("data"), dict) else e.get("data")) or e.get("message") or ""
            msg = str(msg)
        except Exception:
            msg = resp[:120]
        need = re.findall(r'([A-Za-z][A-Za-z0-9]+) is required', msg)
        nm = re.search(r'([A-Za-z][A-Za-z0-9]+) is not a readable file', msg)
        if nm and nm.group(1) in params:
            # 文件不可读 → 换个类型化文件
            params[nm.group(1)] = fill(nm.group(1), desc); continue
        filled = False
        for p in need:
            if p not in params:
                params[p] = fill(p, desc); filled = True
        if not filled and not need:
            break
    if ok:
        final_pass.append((base, rounds)); print(f"PASS  {base} rounds={rounds}", flush=True)
    else:
        final_fail.append((base, msg[:110])); print(f"fail  {base}: {msg[:90]}", flush=True)

w(f"\n## 收敛通过 {len(final_pass)}\n")
w("| 方法 | 轮数 |")
w("|---|---|")
for b, r in final_pass: w(f"| {b} | {r} |")
w(f"\n## 终局失败 {len(final_fail)}\n")
w("| 方法 | 错误 |")
w("|---|---|")
for b, msg in final_fail: w(f"| {b} | {msg} |")
print(f"\nP14B: pass={len(final_pass)} fail={len(final_fail)}", flush=True)
w("\n\n## Phase 14b 完")
LOG.close()
print("P14b done", flush=True)

