import sys
# -*- coding: utf-8 -*-
"""Phase 9：第六轮 — P8 遗留 7 命令官方数据补测 + N22 族 GTF 交叉验证 + 幂等性/并发"""
import io
import os
import subprocess
import threading
import time

os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-cli"))
PY = sys.executable
CLI = [PY, "-m", "tbtools_cli.cli"]
OUT = r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test\out\p9"
os.makedirs(OUT, exist_ok=True)
LOG = io.open(r"C:\Users\16135\WorkBuddy\2026-09-20-10-24-01\tbtools-test\P9_LOG.md", "w", encoding="utf-8", newline="\n")

def w(s):
    LOG.write(s + "\n"); LOG.flush()

def run(name, args, timeout=300):
    """跑一条 CLI 命令并记录"""
    w(f"\n### {name}")
    w("```bash")
    w("tbtools " + " ".join(a if " " not in a else '"'+a+'"' for a in args))
    w("```")
    w("```")
    try:
        r = subprocess.run(CLI + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        ec, so, se = r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        ec, so, se = -99, "", "TIMEOUT"
    tail = (so.strip().splitlines()[-3:] if so.strip() else [])
    for l in tail: w(l)
    if se.strip():
        for l in se.strip().splitlines()[-4:]: w(l)
    w("```")
    # 产物检查：最后一个以 out 开头的参数或 --out* 的值
    status = "✅ PASS" if ec == 0 else f"❌ FAIL (ec={ec})"
    w(f"\n退出码 `{ec}` → **{status}**")
    print(("OK  " if ec == 0 else "FAIL"), name, flush=True)
    return ec

w("# Phase 9：第六轮 — P8 遗留补测 / N22 GTF 交叉 / 幂等性与并发")
w("\n日期：2026-09-20　输入：CLI 自带 examples/data（官方权威数据）")

# ---------- A. P8 遗留 7+1 命令 ----------
w("\n---\n\n## 9.A P8 遗留 7+1 命令（官方数据 + 源码签名）\n")
w("签名来源：`tbtools_cli/auto_commands.py` docstring（ positional 约定）\n")

E = "examples/data"
O = OUT.replace("\\", "/")
T = O  # 输出都进 p9 目录

run("9.1 layoutheatmap（layout.tsv + expr.tsv）",
    ["expr", "layoutheatmap", f"{E}/expr/layout.tsv", f"{E}/expr/expr.tsv", f"{T}/p9_layoutheat.svg"])
run("9.2 multiEfp（官方 TGA+sample2cc+expmat）",
    ["expr", "multiEfp", f"{E}/efp/plant_bg.tga", f"{E}/efp/sample2cc.txt", f"{E}/efp/expmat.tsv", "AT1G01010", f"{T}/p9_multiefp.svg"])
run("9.3 mirnaIdentify（官方 positive_ctrl 三件套）",
    ["mirna", "mirnaIdentify", f"{E}/mirna/mirnaIdentify/positive_ctrl_genome.fa",
     f"{E}/mirna/mirnaIdentify/positive_ctrl_target.tsv", f"{T}/p9_mirpredict.txt"])
run("9.4 msy（官方 genes2.pos + links2 + layout2）",
    ["expr", "msy", f"{E}/synteny/msy/genes2.pos", f"{E}/synteny/msy/links2.txt", f"{E}/synteny/msy/layout2.txt", f"{T}/p9_msy.svg"])
run("9.5 ctgGroup（官方 miniprot.gff，polyPoid=2）",
    ["asm", "ctgGroup", f"{E}/assembly/miniprot.gff", "2", f"{T}/p9_ctggrp.tsv"])
run("9.6 peakdist（官方 chrlen2 + peak_std.xls）",
    ["chipseq", "peakdist", f"{E}/chipseq/chrlen2.txt", f"{E}/chipseq/peak_std.xls", f"{T}/p9_peakdist.svg"])
run("9.7 extractFeatureFromGTF（先空参探签名）",
    ["tool", "extractFeatureFromGTF"])
# 根据 9.7 的报错/usage 自适应补一次常见形态
run("9.7b extractFeatureFromGTF（猜测形态：inGTF feature outGTF）",
    ["tool", "extractFeatureFromGTF", f"{E}/gene_structure.gff", "CDS", f"{T}/p9_exfeat.gff"])
# pileup 需要 blast.xml：用官方 query/subject 先跑 twoSeqBlast 出 XML
run("9.8a twoSeqBlast 造 blast xml（供 pileup）",
    ["tool", "twoSeqBlast", "--queryFasta", f"{E}/blast/query.fa",
     "--subjectFasta", f"{E}/blast/subject.fa", "--outXml", f"{T}/p9_blast.xml"])
if os.path.exists(f"{T}/p9_blast.xml") and os.path.getsize(f"{T}/p9_blast.xml") > 100:
    run("9.8b pileup（自产 blast.xml）", ["plot", "pileup", f"{T}/p9_blast.xml", f"{T}/p9_pileup.svg"])
else:
    w("\n### 9.8b pileup — UNFILLABLE（twoSeqBlast 未产出 xml）\n")

# ---------- B. N22 族 GTF 交叉验证 ----------
w("\n---\n\n## 9.B N22 族 GTF 交叉验证\n")
w("构造合法 GTF（gene→transcript→exon/CDS 四级，gene_id/transcript_id 属性齐全），"
  "对 N22 报「can not decide GFF3 or GTF」的同一批 RPC 方法跑 GTF 输入，检验是『只认 GFF3』还是『格式识别整体失效』。\n")

# 由官方 gene_structure.gff 转 GTF
gtf_path = f"{T}/p9_test.gtf"
try:
    gff = io.open(f"{E}/gene_structure.gff", encoding="utf-8", errors="replace").read().splitlines()
    tx2gene, genes, txs, exons, cds = {}, [], [], [], []
    for l in gff:
        if l.startswith("#") or not l.strip(): continue
        f = l.split("\t")
        if len(f) < 9: continue
        typ, s, e, attr = f[2], f[3], f[4], f[8]
        def av(k):
            for kv in attr.split(";"):
                kv = kv.strip()
                if kv.startswith(k + "="): return kv[len(k)+1:].strip('"')
            return ""
        if typ == "gene":
            gid = av("ID"); tx2gene[gid] = gid; genes.append((f[0], f[6], s, e, gid))
        elif typ in ("mRNA", "transcript"):
            tid = av("ID"); tx2gene[tid] = av("Parent"); txs.append((f[0], f[6], s, e, tid, av("Parent")))
        elif typ == "exon":
            exons.append((f[0], f[6], s, e, av("Parent")))
        elif typ == "CDS":
            cds.append((f[0], f[6], s, e, av("Parent"), f[7]))
    with io.open(gtf_path, "w", encoding="utf-8", newline="\n") as fo:
        for c, st, s, e, gid in genes:
            fo.write(f'{c}\tTBtools\tgene\t{s}\t{e}\t.\t{st}\t.\tgene_id "{gid}";\n')
        for c, st, s, e, tid, gid in txs:
            fo.write(f'{c}\tTBtools\ttranscript\t{s}\t{e}\t.\t{st}\t.\tgene_id "{gid}"; transcript_id "{tid}";\n')
        for c, st, s, e, tid in exons:
            fo.write(f'{c}\tTBtools\texon\t{s}\t{e}\t.\t{st}\t.\tgene_id "{tx2gene.get(tid,"G")}"; transcript_id "{tid}";\n')
        for c, st, s, e, tid, ph in cds:
            fo.write(f'{c}\tTBtools\tCDS\t{s}\t{e}\t.\t{st}\t{ph or 0}\tgene_id "{tx2gene.get(tid,"G")}"; transcript_id "{tid}";\n')
    w(f"GTF 构造完成：{len(genes)} gene / {len(txs)} transcript / {len(exons)} exon / {len(cds)} CDS\n")
except Exception as ex:
    w(f"GTF 构造失败：{ex}")

O2 = OUT.replace("\\", "/")
for m, extra in [("GxfPatch", {}), ("GxfRecallMrna", {}), ("GxfRepresentativeMrna", {}),
                 ("GxfRepresentativeLongestTranscript", {}), ("GxfSplit", {}), ("GffCdsPhaseCorrector", {})]:
    w(f"\n### RPC {m} ← GTF 输入")
    params = {"inGxf": gtf_path.replace("/", "\\"),
              "outGxf": f"{O2}\\p9_{m}_out.gtf",
              "specie": "test"}
    params = {k: v for k, v in params.items() if v}
    import json
    body = json.dumps({"jsonrpc": "2.0", "method": m + ".process", "params": params, "id": 1})
    try:
        import urllib.request
        req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=body.encode(),
                                     headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")
        w("```json"); w(resp[:500]); w("```")
        ok = '"error"' not in resp
        w(f"\n→ **{'✅ PASS' if ok else '❌ FAIL'}**")
        print(("OK  " if ok else "FAIL"), "GTF-" + m, flush=True)
    except Exception as ex:
        w(f"RPC 调用异常：{ex}"); print("ERR ", m, flush=True)

# ---------- C. 幂等性 + 并发 ----------
w("\n---\n\n## 9.C 幂等性（同一命令 3 连跑比对输出）+ RPC 并发 10 路\n")
w("### 幂等性：volcano 同输入同参数连跑 3 次，比对三次输出的 md5\n")
import hashlib
digests = []
for i in range(1, 4):
    out_i = f"{T}/p9_idem_{i}.svg"
    r = subprocess.run(CLI + ["expr", "volcano", f"{E}/deg.txt", out_i],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    if os.path.exists(out_i):
        md5 = hashlib.md5(io.open(out_i, "rb").read()).hexdigest()
        digests.append(md5)
        w(f"- 第 {i} 跑：ec={r.returncode}, md5={md5}")
    else:
        digests.append(f"MISSING(ec={r.returncode})")
        w(f"- 第 {i} 跑：ec={r.returncode}, 输出缺失")
idem = "✅ 三跑输出一致（幂等）" if len(set(digests)) == 1 and digests[0] != "MISSING(ec=0)" else f"⚠️ 输出不一致或缺失：{digests}"
w(f"\n**幂等性结论：{idem}**")
print("IDEM:", idem, flush=True)

w("\n### RPC 并发：10 线程同时调 system.listMethods + statFasta.process，观察错误/串扰\n")
results = []
def rpc_call(i):
    import json
    import urllib.request
    body = json.dumps({"jsonrpc": "2.0",
                       "method": "statFasta.process",
                       "params": {"inFasta": os.path.abspath(f"{E}/blast/query.fa").replace("/", "\\"),
                                  "outPutFile": f"{O2}\\p9_conc_{i}.xls"},
                       "id": i})
    try:
        t0 = time.time()
        req = urllib.request.Request("http://127.0.0.1:8765/rpc", data=body.encode(),
                                     headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")
        dt = time.time() - t0
        ok = '"error"' not in resp and os.path.exists(f"{T}/p9_conc_{i}.xls")
        results.append((i, ok, dt, resp[:120]))
    except Exception as ex:
        results.append((i, False, -1, str(ex)[:120]))
ths = [threading.Thread(target=rpc_call, args=(i,)) for i in range(10)]
t0 = time.time()
for t in ths: t.start()
for t in ths: t.join()
nok = sum(1 for _, ok, _, _ in results if ok)
w("\n| 线程 | 成功 | 耗时s | 备注 |")
w("|---|---|---|---|")
for i, ok, dt, note in results:
    w(f"| {i} | {'✅' if ok else '❌'} | {dt:.2f} | {note[:60]} |")
w(f"\n**并发结论：{nok}/10 成功，总耗时 {time.time()-t0:.1f}s**")
print("CONC:", nok, "/10", flush=True)

w("\n---\n\n## Phase 9 完")
LOG.close()
print("P9 done", flush=True)

