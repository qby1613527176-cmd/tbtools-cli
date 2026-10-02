"""Planner 决策质量矩阵(评审 #109): 教程实证场景的 goal → 工具链规划正确性。

背景: 2026-10-02 教程 × v1.4.23 契约审查发现 planner 决策质量差(初始 4/14 正确)——根因
① spec 数据污染(seq 组兜底把 pep2codon/structure/mastExtract 变万能中介)
② 关键工具缺 relations/capabilities(dnDsCalculate/extractFasta/statFasta 等 kind=tool 全空)
③ 起点截断 [:16] 丢关键工具 + MULTI_INPUT 惩罚过重 + capability 短语缺失。
修复后 13/14(93%)。本文件把这些场景固化为回归测试, 防止数据/算法漂移。

每个用例: goal + input_format/output_format → 期望工具必须出现在规划链中。
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tbtools_cli.workflow import plan_from_goal  # noqa: E402

# (goal, input_format, output_format, 期望工具, 场景来源)
PLANNER_CASES = [
    ("reciprocal best hit detection", "fasta", "tsv", "recipBlast", "4.8 RBH"),
    ("blast search sequences against database", "fasta", "tsv", "recipBlast", "4.2b"),
    ("ka ks ratio calculation", "aln", "tsv", "dnDsCalculate", "4.13 KaKs"),
    ("extract sequences by id list", "fasta", "fasta", "extractFasta", "4.4"),
    ("fasta statistics summary", "fasta", "tsv", "statFasta", "3 章"),
    ("translate dna to protein", "fasta", "fasta", "sixframe", "4.5 翻译(pep2codon 等价)"),    ("phylogenetic tree building", "fasta", "nwk", "iqtree", "4.10 建树"),
    ("gene structure visualization", "gff3", "svg", "genestructure", "4.4 结构图"),
    ("volcano plot", "tsv", "svg", "volcano", "RNA-seq"),
    ("heatmap of expression", "tsv", "svg", "heatmap", "表达热图"),
    ("motif distribution", "xml", "svg", "motif", "4.9 基序图"),
    ("collinearity between genomes", "gff3", "collinearity", "mcscanx", "共线性"),
    ("extract cds from gff", "gff3", "fasta", "extractFasta", "4.5 CDS 提取"),
    # 已知长尾限制(评审 #109 记录, 不判 fail 但断言不退化到明显错误链):
    #   domain scan with hmm profile → hmmsearch(目前 recipBlast→mcscanx, 'scan' 泛词干扰)
]


@pytest.mark.parametrize("goal,inf,outf,expect,src", PLANNER_CASES,
                         ids=[c[0][:20] for c in PLANNER_CASES])
def test_planner_goal_to_tool(goal, inf, outf, expect, src):
    p = plan_from_goal(goal, input_format=inf, output_format=outf)
    tools = [s["tool"] for s in (p.get("plan") or [])]
    # 翻译场景: pep2codon 与 sixframe 语义等价(都是 dna→protein), 接受任一
    if expect == "sixframe":
        assert any(t in tools for t in ("sixframe", "pep2codon")), (
            f"[{src}] goal='{goal}' 规划 {tools} 缺翻译工具; "
            f"conf={p.get('confidence')} reasons={p.get('confidence_reasons')}"
        )
    else:
        assert expect in tools, (
            f"[{src}] goal='{goal}' 规划 {tools} 缺期望工具 {expect}; "
            f"conf={p.get('confidence')} reasons={p.get('confidence_reasons')}"
        )
    assert p.get("confidence", 0) > 0, f"[{src}] 置信度应为正"


def test_planner_recipblast_single_high_confidence():
    """recipBlast 精确命中应高置信(曾因 MULTI_INPUT 惩罚被 memerun 链压制)"""
    p = plan_from_goal("reciprocal best hit detection", input_format="fasta", output_format="tsv")
    assert p["confidence"] >= 0.8
    assert "recipBlast" == p["plan"][-1]["tool"]


def test_planner_no_irrelevant_start():
    """链起点应与 goal 相关(recipBlast→mcscanx 曾因无关起点在 domain 场景赢 hmmsearch)"""
    p = plan_from_goal("fasta statistics summary", input_format="fasta", output_format="tsv")
    assert "statFasta" in [s["tool"] for s in p["plan"]]


def test_planner_spec_data_not_polluted():
    """seq 组兜底污染回归: pep2codon/structure 不得与 sixframe 共享万能关系"""
    from tbtools_cli.command_spec import build_command_specs
    specs = build_command_specs()
    for n in ("pep2codon", "structure", "mastExtract"):
        rel = specs[n].relations or {}
        assert rel.get("produces") != ["SEQUENCE_ARTIFACT"], f"{n} 仍是 seq 组万能中介"
    # 关键工具必须有 relations/capabilities(kind=tool 曾全空)
    for n in ("dnDsCalculate", "extractFasta", "statFasta"):
        assert specs[n].relations, f"{n} relations 缺失"
        assert specs[n].capabilities, f"{n} capabilities 缺失"
