import sys
# -*- coding: utf-8 -*-
"""P15：最后 4 个残余方法收口（Diamond 族 2 + GxfCat + FastxExtract ID 匹配场景）"""
import io, os, json, re, time, subprocess, urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
for k in ("HTTP_PROXY","http_proxy","HTTPS_PROXY","https_proxy","ALL_PROXY","all_proxy"):
    os.environ.pop(k, None)
os.environ["NO_PROXY"] = "127.0.0.1,localhost"; os.environ["no_proxy"] = "127.0.0.1,localhost"
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P15_LOG.md", "w", encoding="utf-8", newline="\n")
def w(s): LOG.write(s + "\n"); LOG.flush()
def rpc(m, p=None, timeout=240):
    b = json.dumps({"jsonrpc":"2.0","method":m,"params":p or {},"id":1}).encode()
    return urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:8765/rpc", data=b,
        headers={"Content-Type":"application/json"}), timeout=timeout).read().decode("utf-8","replace")
def alive():
    try: rpc("system.listMethods", {}, 8); return True
    except Exception: return False
def ensure():
    if alive(): return True
    subprocess.Popen(CLI + ["rpc", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(25):
        time.sleep(2)
        if alive(): return True
    return False
def call(m, p, timeout=240):
    for _ in range(3):
        if not ensure(): return None, "SERVER_DOWN"
        try: return rpc(m, p, timeout), "ok"
        except Exception as ex:
            last = str(ex); time.sleep(1)
    return None, last

E = "examples/data"
FA  = os.path.abspath(f"{E}/blast/query.fa")        # 蛋白 query
FA2 = os.path.abspath(f"{E}/blast/subject.fa")      # 蛋白 subject
GFF3  = os.path.abspath(f"{E}/gxf/input.gff3")
GFF3b = os.path.abspath(f"{E}/gene_structure.gff")
DEG   = os.path.abspath(f"{E}/deg.txt")
OUT = T + r"\out\p15"; os.makedirs(OUT, exist_ok=True)
def O(n): return OUT + "\\" + n

# FastxExtract：从 query.fa 实际 header 生成匹配 ID 列表
ids = []
for line in io.open(FA, encoding="utf-8", errors="replace"):
    if line.startswith(">"):
        ids.append(line[1:].split()[0])
    if len(ids) >= 3: break
IDLIST = O("p15_ids.txt")
io.open(IDLIST, "w", encoding="utf-8", newline="\n").write("\n".join(ids) + "\n")

POOL = [(r"chrlen|len", os.path.abspath(f"{E}/synteny/chrlen.txt")),
        (r"idlist|ids", IDLIST), (r"query", FA), (r"subject|target|ref", FA2),
        (r"gtf", T + r"\out\p9\p9_test.gtf"), (r"gff3|gene_struct", GFF3b),
        (r"gxf|gff", GFF3), (r"fasta|fa\b|seq|pep|protein", FA),
        (r"expr|deg|table|tsv|xls|txt", DEG)]
def fill(pname, desc):
    pl = pname.lower()
    if "output" in pl or pl.startswith("out") or "prefix" in pl and "conflict" not in pl:
        return O("p15_" + pname + ".out")
    if "conflict" in pl:
        return O("p15_conflict_prefix.txt")
    for pat, v in POOL:
        if re.search(pat, pl): return v
    for pat, v in POOL:
        if re.search(pat, desc.lower()): return v
    return DEG

TARGETS = {
    "QuickGeneFamilyIdentification": {"queryFastaPath": FA, "subjectFastaPath": FA2,
                                      "outputPath": O("p15_qgfi")},
    "QuickProteinAnno": {"inputPath": FA, "outputPath": O("p15_qpa")},
    "GxfCat": {"inputPath": GFF3, "outputPath": O("p15_gxfcat.gff3")},
    "FastxExtract": {"inputPath": FA, "idListPath": IDLIST, "outputPath": O("p15_fastx.fa")},
}
w("# P15 最后 4 个残余收口\n")
res = {}
for base, seed in TARGETS.items():
    try:
        d = json.loads(rpc("system.describeMethod", {"method": base + ".process"})).get("result", {})
        desc = json.dumps(d.get("description", {}), ensure_ascii=False)
        w(f"\n## {base} describe\n```json\n" + json.dumps(d.get("description", {}), ensure_ascii=False, indent=1)[:1200] + "\n```")
    except Exception as ex:
        desc = ""; w(f"\n## {base} describe 失败: {ex}")
    params = dict(seed); ok = False; msg = ""
    for rnd in range(6):
        resp, err = call(base + ".process", params)
        if resp is None: msg = "SERVER: " + err; break
        if '"error"' not in resp:
            ok = True; msg = f"第 {rnd+1} 轮收敛"; break
        try:
            e = json.loads(resp).get("error", {})
            msg = (e.get("data", {}).get("message") if isinstance(e.get("data"), dict) else e.get("data")) or e.get("message") or ""
            msg = str(msg)
        except Exception: msg = resp[:150]
        w(f"- r{rnd+1} FAIL: {msg[:160]}")
        need = re.findall(r'([A-Za-z][A-Za-z0-9]+) is required', msg)
        nm = re.search(r'([A-Za-z][A-Za-z0-9]+) is not a readable file', msg)
        if nm and nm.group(1) in params:
            params[nm.group(1)] = fill(nm.group(1), desc); continue
        filled = False
        for p in need:
            if p not in params: params[p] = fill(p, desc); filled = True
        if not filled and not need: break
    res[base] = (ok, msg)
    print(("PASS  " if ok else "fail  ") + base + ": " + msg[:100], flush=True)

w("\n## 总结\n")
for b, (ok, msg) in res.items():
    w(f"- {'✅' if ok else '❌'} {b}: {msg[:120]}")
w("\n## Phase 15 完")
LOG.close()
print("P15 done", flush=True)

