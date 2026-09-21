#!/usr/bin/env python
"""Phase4b: PARAM-OTHER 68 方法定向救援（12 轮迭代 + 增强数据池 + 特殊流程）"""
import io
import json
import os
import re
import time
import urllib.request

os.chdir(os.path.dirname(os.path.abspath(__file__)))
LOG = io.open("P4B_LOG.md", "w", encoding="utf-8", newline="\n")
D = os.getcwd().replace("\\", "/")
RPC = "http://127.0.0.1:8765/rpc"

def w(s=""):
    LOG.write(s + "\n"); LOG.flush()

def rpc(method, params, timeout=240):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params})
    t0 = time.time()
    try:
        req = urllib.request.Request(RPC, data=body.encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace"), time.time() - t0
    except Exception as e:
        return json.dumps({"error": str(e)}), time.time() - t0

# ---- 预构造特殊输入 ----
io.open("out/p4b_acc.txt", "w", newline="\n").write("NC_035621.1\nNC_035622.1\n")
io.open("out/p4b_regex.txt", "w", newline="\n").write("^At_.*\n^Os_.*\n")
io.open("out/p4b_plantcare.tsv", "w", newline="\n").write(
    "At_PIN1_Q9C6B8\t1000\t1010\tTATA-box\t+\t1\t1\tpromoter\n"
    "At_PIN1_Q9C6B8\t2000\t2015\tCAAT-box\t-\t1\t1\tpromoter\n"
    "At_PIN2_Q9LU77\t500\t512\tGT1-motif\t+\t1\t1\tpromoter\n")
io.open("out/p4b_sra.xml", "w", newline="\n").write(
    '<?xml version="1.0"?>\n<EXPERIMENT_PACKAGE><EXPERIMENT><ID>1</ID>'
    '<TITLE>test</TITLE><STUDY_REF accession="SRP1"/><DESIGN><SAMPLE_DESCRIPTOR accession="SRS1"/>'
    '<LIBRARY_DESCRIPTOR><LIBRARY_STRATEGY>RNA-Seq</LIBRARY_STRATEGY></LIBRARY_DESCRIPTOR>'
    '</DESIGN></EXPERIMENT></EXPERIMENT_PACKAGE>\n')
io.open("out/p4b_species.txt", "w", newline="\n").write("Arabidopsis thaliana\nOryza sativa\n")
io.open("out/p4b_rename.tsv", "w", newline="\n").write("At_PIN1_Q9C6B8\tAtPIN1\nAt_PIN2_Q9LU77\tAtPIN2\n")
io.open("out/p4b_pattern.tsv", "w", newline="\n").write("At_PIN1\tATPIN1\nAt_PIN2\tATPIN2\n")
io.open("out/p4b_primer.tsv", "w", newline="\n").write("F1\tATGGCGAACGACGGGAATTG\tR1\tTTAGGCCTTAACATGCTCGG\n")

POOL = [
    (r"swissprot", f"{D}/data/si_proteome.fa"),
    (r"accession", f"{D}/out/p4b_acc.txt"),
    (r"regex", f"{D}/out/p4b_regex.txt"),
    (r"plantcare", f"{D}/out/p4b_plantcare.tsv"),
    (r"sra", f"{D}/out/p4b_sra.xml"),
    (r"species", f"{D}/out/p4b_species.txt"),
    (r"renamemap|renam", f"{D}/out/p4b_rename.tsv"),
    (r"patternmap|pattern", f"{D}/out/p4b_pattern.tsv"),
    (r"primer", f"{D}/out/p4b_primer.tsv"),
    (r"fpkm|tpm", f"{D}/out/p2_rpkm.tsv"),
    (r"count|table|tab\b", f"{D}/out/pin_expr.tsv"),
    (r"subject|ref|reference|db\b|database", f"{D}/data/monarda_chloro_pep.fa"),
    (r"pep|protein", f"{D}/data/monarda_chloro_pep.fa"),
    (r"cds|codon|nucl|orf", f"{D}/data/monarda_chloro_cds.fa"),
    (r"genome", f"{D}/data/monarda_chloro.clean.fa"),
    (r"mrna", f"{D}/data/monarda_chloro_pep.fa"),
    (r"chrlen|chrheight", f"{D}/data/chloro_chrlen.tsv"),
    (r"matrix", f"{D}/out/atpin_sipin_matrix.tsv"),
    (r"gtf", f"{D}/data/monarda_chloro.gff3"),
    (r"gff|gxf", f"{D}/data/monarda_chloro.gff3"),
    (r"tree|nwk|newick", f"{D}/out/pin8_genetree.treefile"),
    (r"expr", f"{D}/out/pin_expr.tsv"),
    (r"fastq|fq|read", f"{D}/out/sim_reads.fq"),
    (r"query", f"{D}/out/pin10.fa"),
    (r"idlist|ids|genelist|selectedrows", f"{D}/out/chloro_ids.txt"),
    (r"group", f"{D}/out/sample_group.tsv"),
    (r"vcf", f"{D}/out/p2_fake.vcf"),
    (r"xml", f"{D}/out/t2b5.xml"),
    (r"embl|genbank|gb", f"{D}/data/monarda_chloro.embl"),
    (r"region|bed|coord", f"{D}/out/coords.bed"),
    (r"obo|ontology", f"{D}/data/go.obo"),
]
IN_KW = r"input|inpath|infile|infa|query|src|source|gxfpath|gffpath|gtfpath|subjectpath|subject|database|genome|pep|cds|expr|xml|embl|vcf|region|bed|obo|fastq|fq|matrix|tree|mrna|fpkm|count|table|accession|species|primer|pattern|regex|rename|left|right|patch"

def guess(key):
    k = key.lower()
    if re.search(r"output|outpath|outfile|outfa|dest|result|report|save|outdir", k):
        return f"{D}/out/p4b_{key}.out"
    if re.search(r"column|col\b|index\b|keycolumn|sortcol|selectedcol|colindex", k):
        return 0
    if re.search(r"maxnum|numinafa|threads|topn|level", k):
        return 10
    if re.search(r"size|len|num|count|window|step|width|height|kbases|overlap|binning|bin", k):
        return 100
    if re.search(r"minvalue|maxvalue|value", k):
        return {"minvalue": 0, "maxvalue": 100}.get(k, 50)
    if re.search(r"methodname", k):
        return "FastaStat.process"
    if re.search(r"region\b|chrregion", k):
        return "monarda_chloro:1-40000"
    if re.search(r"^to$|mailto", k):
        return "test@example.com"
    if re.search(r"^subject$|title|body|text|message", k):
        return "test message from rpc test"
    if re.search(r"bool|is_|enable|show|include", k):
        return True
    if re.search(r"array|paths|inputpaths", k):
        return [f"{D}/data/monarda_chloro.gff3", f"{D}/data/monarda_chloro.gff3"]
    if re.search(r"pattern\b|motif", k):
        return "GAATTC"
    if re.search(IN_KW, k):
        for pat, path in POOL:
            if re.search(pat, k):
                return path
        return f"{D}/out/pin_expr.tsv"
    return None  # 不猜，留给下一轮报错

# TodoList 特殊流程：先建任务
todo_ok = False
txt, _ = rpc("TodoList.addTask", {"text": "rpc-test-task", "priority": "high"})
mo = re.search(r'"id"\s*:\s*"?([\w-]+)"?', txt)
todo_id = mo.group(1) if mo else None
w(f"# Phase 4b：PARAM-OTHER 定向救援\n\n预置：TodoList.addTask → {txt[:150]}\n")
if todo_id: w(f"取得 task id: {todo_id}\n")

TARGETS = [l.strip() for l in io.open("p4b_targets.txt") if l.strip()]
w(f"目标 {len(TARGETS)} 个方法，最多 12 轮迭代。\n")

results = {}
for i, m in enumerate(TARGETS, 1):
    params = {}
    if m.startswith("TodoList.") and todo_id:
        params["taskId"] = todo_id
    hist = []
    status, final = None, ""
    for rnd in range(12):
        txt, dt = rpc(m, params)
        hist.append((dict(params), txt, dt))
        try:
            resp = json.loads(txt)
        except Exception:
            status, final = "BAD-JSON", txt; break
        if resp.get("error"):
            msg = resp["error"].get("message", "")
            if resp["error"].get("code") == -32601:
                status, final = "NO-METHOD", msg; break
            mo = re.search(r"(\w+) is required", msg)
            if mo:
                key = mo.group(1)
                v = guess(key)
                if v is None:
                    status, final = "UNFILLABLE", msg; break
                params[key] = v
                continue
            status, final = "PARAM-OTHER", msg; break
        status, final = "PASS", txt; break
    results[m] = status
    w(f"\n### {m} → **{status}**")
    for p, txt, dt in hist[-3:]:
        w(f"- 参数: `{json.dumps(p, ensure_ascii=False)[:200]}`")
        short = txt if len(txt) <= 600 else txt[:600] + " …"
        w(f"\n```json\n{short.rstrip()}\n```\n*({dt:.1f}s)*")
    print(f"{i} {m} {status}")

from collections import Counter
w("\n\n## 汇总\n")
for st, n in Counter(results.values()).most_common():
    w(f"- {st}: {n}")
w("\n## 本轮新 PASS\n")
for m, st in sorted(results.items()):
    if st == "PASS": w(f"- {m}")
LOG.close()
print("PHASE4B DONE")

