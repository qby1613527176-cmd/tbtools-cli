"""CLI/MCP DX 测试(评审 #109): 错误引导、MCP 空输入、工作流链。

背景: 2026-10-02 MCP/CLI DX 优化——纠错建议只搜分组名(recipblast→blast 而非 recipBlast)、
MCP search 空输入返回裸 {}。修复后固化防回归。
"""
import json
import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _cli(*args, timeout=30):
    env = dict(os.environ)
    return subprocess.run([sys.executable, "-m", "tbtools_cli.cli", *args],
                          capture_output=True, text=True, timeout=timeout, cwd=ROOT, env=env)


def test_unknown_command_suggests_tool_not_group():
    """评审 #109: 'recipblast'(小写) 应建议 recipBlast 而非分组名 blast"""
    r = _cli("recipblast")
    assert r.returncode == 2
    assert "recipBlast" in r.stdout + r.stderr, f"应建议 recipBlast: {(r.stdout + r.stderr)[-200:]}"


def test_typo_command_fuzzy_suggest():
    """拼写错: 'recpblast' → recipBlast(模糊匹配全工具名)"""
    r = _cli("recpblast")
    assert "recipBlast" in r.stdout + r.stderr


def test_group_internal_typo_suggest():
    """分组内拼写错: 'blast recipBllast' → recipBlast"""
    r = _cli("blast", "recipBllast")
    assert "recipBlast" in r.stdout + r.stderr, f"分组内应建议: {(r.stdout + r.stderr)[-200:]}"


def test_mcp_search_empty_guidance():
    """MCP search 空输入: 返回用法引导(非裸 {})"""
    from tbtools_cli.mcp_server import search
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        d = json.loads(search(""))
    assert d.get("error") == "query 为空"
    assert "usage" in d and d["usage"]["examples"], "空查询应带用法示例"


def test_agent_workflow_chain():
    """Agent 工作流链: search→describe→validate 衔接顺畅"""
    r = _cli("search", "volcano plot", "--json")
    d = json.loads(r.stdout)
    assert "volcano" in [h["name"] for h in (d.get("hits") or [])], "search 应发现 volcano"
    r2 = _cli("tool-describe", "volcano", "--json")
    d2 = json.loads(r2.stdout)
    assert d2.get("inputs"), "describe 应含 inputs 契约"
    assert d2["inputs"][0]["format"] == "tsv"
    # validate 需真实文件, 此处只验证命令可调用(格式错误输入也应返回结构化结果而非崩)
    r3 = _cli("tool-validate", "volcano", "/nonexistent.tsv", "--json")
    assert r3.returncode == 0 or "valid" in r3.stdout, "validate 不应崩"


def test_version_has_authoritative_counts():
    """version 数字是动态统计(非硬编码)——含 metadata_commands 权威口径"""
    r = _cli("version", "--json")
    d = json.loads(r.stdout)
    assert d["version"].count(".") == 2, f"版本格式异常: {d['version']}"
    assert d.get("metadata_commands", 0) >= 290, f"metadata 命令数应 ~294: {d.get('metadata_commands')}"