import sys
#!/usr/bin/env python
"""Phase4: RPC 188 方法自动补参深测
迭代策略：空参 → 解析 "-32602: xx is required" → 按参数名关键词填真实数据 → 重试（≤4 轮）
"""
import io, json, os, re, sys, time, urllib.request

os.environ.setdefault("TBTOOLS_JAR", "C:/Program Files/TBtools/TBtools_JRE1.6.jar")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
LOG = io.open("P4_LOG.md", "w", encoding="utf-8", newline="\n")
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
            txt = r.read().decode("utf-8", "replace")
        return txt, time.time() - t0
    except Exception as e:
        return json.dumps({"error": str(e)}), time.time() - t0

# 参数名 → 真实数据池（按关键词优先匹配）
POOL = [
    (r"pep|protein", f"{D}/data/monarda_chloro_pep.fa"),
    (r"cds|codon|nucl", f"{D}/data/monarda_chloro_cds.fa"),
    (r"genome|genomefa", f"{D}/data/monarda_chloro.clean.fa"),
    (r"chrlen|chrlength|chrheight|chromlength", f"{D}/data/chloro_chrlen.tsv"),
    (r"matrix", f"{D}/out/atpin_sipin_matrix.tsv"),
    (r"gff|gxf|gtf|anno|gene", f"{D}/data/monarda_chloro.gff3"),
    (r"tree|nwk|newick|phylo", f"{D}/out/pin8_genetree.treefile"),
    (r"expr", f"{D}/out/pin_expr.tsv"),
    (r"fastq|fq|read", f"{D}/out/sim_reads.fq"),
    (r"query", f"{D}/out/pin10.fa"),
    (r"subject|ref|reference|db|blastdb", f"{D}/data/monarda_chloro_pep.fa"),
    (r"idlist|ids|genelist|idfile", f"{D}/out/chloro_ids.txt"),
    (r"group", f"{D}/out/sample_group.tsv"),
    (r"deg|fc|log2fc|pvalue", f"{D}/out/pin_deg.tsv"),
    (r"collinear|ks|kaks", f"{D}/out/fake_collinearity.tsv"),
    (r"vcf", f"{D}/out/p2_fake.vcf"),
    (r"xml", f"{D}/out/t2b5.xml"),
    (r"emb|gb", f"{D}/data/monarda_chloro.embl"),
    (r"index|idx", f"{D}/out/p2_faid.idx"),
    (r"region|bed|coord", f"{D}/out/coords.bed"),
    (r"rnafold|fold|dot", f"{D}/out/p2_rnafold.txt"),
    (r"obo|go\b|ontology", f"{D}/data/go.obo"),
    (r"kegg", f"{D}/out/kegg_reference.keg"),
]
IN_KW = r"input|inpath|infile|infa|query|src|source|file1|matrix|tree|genome|pep|cds|expr|xml|embl|vcf|region|bed|obo|kegg|fastq|fq|idlist|group|collinear|fold|index|ref"
OUT_KW = r"output|outpath|outfile|outfa|out|dest|result|report|targetpath|save"

def guess_param(key):
    k = key.lower()
    if re.search(OUT_KW, k):
        return f"{D}/out/p4_{key}.out"
    # 整数/标量优先（column/index 等会被 IN_KW 的 index 误吞）
    if re.search(r"column|col\b|index|regex|size|count|num|length|minvalue|maxvalue|value|topn|level|thread|kmer|window|step|width|height|kbases", k):
        return {"minvalue": 0, "maxvalue": 100, "regex": "^[AG].*"}.get(k, 0)
    if re.search(r"bool|is_|enable|show", k):
        return True
    if re.search(r"pathlist|paths|inputpaths|array|listfile", k):
        return [f"{D}/out/pin_expr.tsv"]
    if re.search(r"methodname|taskid|id\b", k):
        return "FastaStat.process"
    if re.search(IN_KW, k):
        for pat, path in POOL:
            if re.search(pat, k):
                return path
        return f"{D}/out/pin_expr.tsv"
    # 标量
    return {"threads": 4, "numofthreads": 4, "kmer": 31, "maxlenkbases": 160,
            "binning": 100, "window": 1000, "windowsize": 1000, "step": 100,
            "topn": 10, "level": 2, "colindex": 0, "keycolindex": 0,
            "minlen": 50, "maxlen": 5000, "threadsnum": 4, "num": 10,
            "n": 10, "width": 800, "height": 600}.get(k.replace("_", ""), 100)

req = urllib.request.Request(RPC, data=json.dumps({"jsonrpc": "2.0", "method": "system.listMethods", "params": {}}).encode(), headers={"Content-Type": "application/json"})
methods = json.loads(urllib.request.urlopen(req, timeout=30).read())["result"]
if isinstance(methods, dict):
    methods = methods.get("methods", list(methods.keys()))
w(f"# Phase 4：RPC 自动补参深测（{len(methods)} 方法 × 迭代补参 ≤4 轮）\n")
w("> 每方法：空参 → 解析 `xx is required` → 按参数名关键词从真实数据池填充 → 重试。\n"
  "> 最终 ok=true 记为 PASS；返回参数校验错误记为 PARAM-GAP（穷尽 4 轮仍未填全）；其他错误原样记录。\n")

SKIP = {"system.listMethods"}
results = {}
for i, m in enumerate([x for x in methods if x not in SKIP], 1):
    params = {}
    hist = []
    status, final = None, ""
    for rnd in range(4):
        txt, dt = rpc(m, params)
        hist.append((dict(params), txt, dt))
        try:
            resp = json.loads(txt)
        except Exception:
            status, final = "BAD-JSON", txt
            break
        if resp.get("error"):
            msg = resp["error"].get("message", "")
            if resp["error"].get("code") == -32601:
                status, final = "NO-METHOD", msg
                break
            mo = re.search(r"(\w+) is required", msg)
            if mo and rnd < 3:
                key = mo.group(1)
                params[key] = guess_param(key)
                continue
            status, final = "PARAM-OTHER", msg
            break
        status, final = "PASS", txt
        break
    results[m] = status
    w(f"\n### {m} → **{status}**")
    for p, txt, dt in hist:
        w(f"- 尝试参数: `{json.dumps(p, ensure_ascii=False)[:220]}`")
        short = txt if len(txt) <= 700 else txt[:700] + " …"
        w(f"\n```json\n{short.rstrip()}\n```\n*({dt:.1f}s)*")
    print(f"{i} {m} {status}")

from collections import Counter
w("\n\n## 汇总\n")
for st, n in Counter(results.values()).most_common():
    w(f"- {st}: {n}")
    print(st, n)
w("\n## PASS 方法清单\n")
for m, st in sorted(results.items()):
    if st == "PASS": w(f"- {m}")
w("\n## PARAM-GAP 方法清单（4 轮仍未补全参数）\n")
for m, st in sorted(results.items()):
    if st == "PARAM-GAP": w(f"- {m}")
LOG.close()
print("PHASE4 DONE")

