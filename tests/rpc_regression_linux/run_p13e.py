import sys
# -*- coding: utf-8 -*-
"""P13e：终局定点修复——数组/整数/正则/单ID 等类型正确化"""
import io, os, json, re, time, subprocess, urllib.request

T = os.environ.get("TBREGRESSION_TEST", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test")
OUT = T + r"\out\p13"
os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
E = "examples/data"
CLI = [sys.executable, "-m", "tbtools_cli.cli"]
LOG = io.open(T + r"\P13E_LOG.md", "w", encoding="utf-8", newline="\n")
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
def call(method, params):
    for _ in range(3):
        if not ensure(): return None, "SERVER_UNRECOVERABLE"
        try:
            return rpc(method, params, timeout=240), "ok"
        except Exception as ex:
            last = str(ex); time.sleep(1)
    return None, last

FA = os.path.abspath(f"{E}/blast/query.fa"); FA2 = os.path.abspath(f"{E}/blast/subject.fa")
GFF3 = os.path.abspath(f"{E}/gxf/input.gff3"); GTF_SYN = T + r"\out\p9\p9_test.gtf"
DEG = os.path.abspath(f"{E}/deg.txt"); genome_small = OUT + r"\genome2m.fa"
msa = OUT + r"\msa.fa"; XMLE = OUT + r"\p12_blast_f5.txt"
IDLIST = os.path.abspath(f"{E}/fasta/extract.idlist.txt")
GFF3b = os.path.abspath(f"{E}/gene_structure.gff")
def O(n): return OUT + "\\" + n

# 首个 ID
first_id = None
for line in io.open(IDLIST, encoding="utf-8", errors="replace"):
    if line.strip():
        first_id = line.strip().split()[0]; break

FIX = {
    "FastaMerge": {"inputPaths": [FA, FA2], "outputPath": O("p13e_fmerge.fa")},
    "GxfCat": {"inputPaths": [GFF3, GFF3b], "outputPath": O("p13e_gcat.gff3")},
    "McScanXFileMerge": {"inputPaths": [os.path.abspath(f"{E}/synteny/test.collinearity"),
                                          os.path.abspath(f"{E}/synteny/dual.collinearity")],
                          "outputPath": O("p13e_msm.collinearity")},
    "FastaSplitByCount": {"inputPath": FA, "maxNumInOneFasta": 2, "outputDir": O("p13e_fbc")},
    "FastaWindowStat": {"inputPath": genome_small, "windowSize": 1000, "outputPath": O("p13e_fws.xls")},
    "GxfGeneDensityProfiler": {"inputPath": GFF3, "binSize": 100, "outputPath": O("p13e_gdp.xls")},
    "FastaPatternLocate": {"inputPath": FA, "pattern": "MSTN", "outputPath": O("p13e_fpl.xls")},
    "FastxExtract": {"inputPath": FA, "id": (first_id or "q1"), "outputPath": O("p13e_fx.fa")},
    "GxfFilter": {"inputPath": GFF3, "idList": [first_id or "gene1"], "outputPath": O("p13e_gfil.gff3")},
    "OneStepBuildATree": {"inputPath": msa, "outputDir": OUT + r"\p13e_tree_out"},
    "GffExtractRegion": {"inputPath": GFF3b, "region": "chr1:1-100000", "outputPath": O("p13e_ger.gff3")},
    "GxfToGenePos": {"inputPath": GFF3b, "outputPath": O("p13e_gtp.pos")},
    "TableRowManipulator": {"inputPath": DEG, "idListPath": IDLIST, "outputPath": O("p13e_trm.tsv")},
}

passed, failed = [], []
for base, params in FIX.items():
    resp, err = call(base + ".process", params)
    if resp is None:
        failed.append((base, "SERVER: " + err)); print("dead ", base, flush=True); continue
    ok = '"error"' not in resp
    if ok:
        passed.append(base); print("PASS ", base, flush=True)
    else:
        try:
            e = json.loads(resp).get("error", {})
            msg = (e.get("data", {}).get("message") if isinstance(e.get("data"), dict) else e.get("data")) or e.get("message") or ""
        except Exception:
            msg = resp[:90]
        # 再来一轮回显补参
        need = re.findall(r'([A-Za-z][A-Za-z0-9]+) is required', str(msg))
        if need:
            p2 = dict(params)
            for p in need:
                pl = p.lower()
                if "output" in pl or pl.startswith("out"): p2[p] = O(f"p13e_{base}_{p}.out")
                elif re.search(r"num|size|count|bin", pl): p2[p] = 2
                elif re.search(r"list|ids?$", pl): p2[p] = [first_id or "q1"]
                else: p2[p] = FA
            resp2, err2 = call(base + ".process", p2)
            if resp2 and '"error"' not in resp2:
                passed.append(base); print("PASS ", base, "(2nd)", flush=True); continue
            failed.append((base, str(msg)[:100]))
        else:
            failed.append((base, str(msg)[:100]))
        print("fail ", base, str(msg)[:70], flush=True)

w(f"# P13e：终局定点修复\n\n## 通过 {len(passed)}\n\n" + (", ".join(sorted(passed)) if passed else "（无）"))
w(f"\n## 终局仍失败 {len(failed)}\n")
w("| 方法 | 错误 |")
w("|---|---|")
for b, msg in failed:
    w(f"| {b} | {msg} |")
print(f"\nP13E: pass={len(passed)} fail={len(failed)}", flush=True)
w("\n\n## Phase 13e 完")
LOG.close()
print("P13e done", flush=True)

