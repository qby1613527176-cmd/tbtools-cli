"""Semantic Resolver 覆盖率测试(评审 #109): tbtools search 语义发现质量。

背景: 2026-10-02 教程契约审查暴露 search 只匹配 name+help+class 字面词(14 场景 7/14=50%)。
修复: ①hay 加入 capabilities/relations 语义层 ②词干化(extract↔extraction) ③停用词过滤(by/id/of)
④排序: 语义命中>全名精确>name 凑巧(recipBlast caps 'blast' 应排 bestid 前)。修复后 14/14=100%。
本文件固化这些场景防回归。
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# (查询词, 期望工具族——任一命中即语义发现成功)
SEARCH_CASES = [
    ("reciprocal best hit", ["recipBlast"]),
    ("ka ks", ["dnDsCalculate"]),
    ("extract sequences by id list", ["extractFasta", "extractFastaSub", "fastaExtract"]),
    ("fasta statistics", ["statFasta"]),
    ("domain scan hmm profile", ["hmmsearch", "hmmerSearch"]),
    ("gene structure", ["genestructure"]),
    ("translate dna protein", ["sixframe", "cds2protein", "translater"]),
    ("build phylogenetic tree", ["iqtree"]),
    ("volcano plot", ["volcano"]),
    ("motif distribution", ["motif", "fimo", "memeViz"]),
    ("collinearity genomes", ["mcscanx", "mcscanxd", "collinearRegion"]),
    ("blast sequences", ["recipBlast", "blastp", "twoSeqBlast", "autoMakeBlastDb"]),
    ("expression heatmap", ["heatmap"]),
    ("extract cds gff", ["extractFasta", "extractGff3Region", "cds2protein"]),
]


def _search(kw: str) -> list:
    env = dict(os.environ)
    r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "search", kw, "--json"],
                       capture_output=True, text=True, timeout=60, cwd=ROOT, env=env)
    assert r.returncode == 0, f"search 失败: {r.stderr[-300:]}"
    data = json.loads(r.stdout)
    hits = data.get("hits") or []
    if hits and isinstance(hits[0], dict):
        return [h["name"] for h in hits]
    return [h[0] for h in hits]


@pytest.mark.parametrize("kw,alts", SEARCH_CASES, ids=[c[0][:18] for c in SEARCH_CASES])
def test_search_semantic_discovery(kw, alts):
    names = _search(kw)
    hit = [a for a in alts if a in names]
    assert hit, f"search '{kw}' top {len(names)} 无期望工具 {alts}; 实际: {names[:8]}"


def test_search_semantic_over_name_coincidence():
    """语义>名字凑巧: 'blast sequences' 应 recipBlast(top) 而非 bestid(名字含 blast)"""
    names = _search("blast sequences")
    assert names and names[0] == "recipBlast", f"recipBlast 应 top1, 实际: {names[:5]}"


def test_search_stem_and_stopwords():
    """词干化 + 停用词: 'extract sequences by id list' 应发现 extractFasta(top)"""
    names = _search("extract sequences by id list")
    assert names and names[0] == "extractFasta", f"extractFasta 应 top1, 实际: {names[:5]}"


def test_search_capability_semantic_layer():
    """capabilities 语义索引: 'domain scan' 应发现 hmmsearch 族(planner 同源数据)"""
    names = _search("domain scan hmm profile")
    assert any(n in ("hmmsearch", "hmmerSearch") for n in names[:5]), f"hmm 族应 top5: {names[:8]}"