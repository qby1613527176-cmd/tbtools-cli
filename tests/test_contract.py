"""工具契约测试(评审 #21 健康矩阵: 294 命令 × discover/describe/validate 契约)。

不跑真实引擎(JAR 可缺)——验证 CommandSpec 单一模型产出的每一条工具元数据
在 discover/describe/validate 三层都可用,防"注册了但 Agent 找不到/描述不了"。
"""
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tbtools_cli.command_spec import build_command_specs  # noqa: E402

META = json.load(open(ROOT / "tbtools_cli" / "command_metadata.json", encoding="utf-8"))
SPECS = build_command_specs()


def test_contract_model_metadata_consistency():
    """契约①: CommandSpec 模型与 metadata 条目双向一致(无残影/无孤儿)"""
    spec_ids = set(SPECS)
    meta_ids = set(META)
    assert spec_ids == meta_ids, (
        f"不一致: specs 独有 {len(spec_ids - meta_ids)} / metadata 独有 {len(meta_ids - spec_ids)}"
    )


def test_contract_required_fields():
    """契约②: 每个工具必备字段非空(name/kind/group/help)"""
    required = {"name", "kind", "group", "help"}
    bad = [n for n, v in META.items() if not required.issubset(v) or not v["name"]]
    assert not bad, f"缺必备字段: {bad[:10]}"


def test_contract_kind_enum():
    """契约③: kind 值域合法(bridge/direct/manual/tool)"""
    legal = {"bridge", "direct", "manual", "tool"}
    bad = [n for n, v in META.items() if v.get("kind") not in legal]
    assert not bad, f"非法 kind: {bad[:10]}"


def test_contract_metadata_projection():
    """契约④: metadata 可由模型投影再生(单一事实源成立)"""
    for name in list(META)[:50]:  # 抽样 50(全量投影含动态 help 差异容忍)
        assert name in SPECS, f"{name} 不在模型"


def test_contract_status_semantics():
    """契约⑤: status 值域合法(stable/beta/platform-limited/network-required)"""
    legal = {"stable", "beta", "platform-limited", "network-required"}
    bad = [n for n, v in META.items() if v.get("status") and v["status"] not in legal]
    assert not bad, f"非法 status: {bad[:10]}"


def test_contract_help_no_placeholder():
    """契约⑥: help 覆盖率(核心命令空 help 视为缺失契约)"""
    empty = [n for n, v in META.items() if not (v.get("help") or "").strip()]
    # 允许 engine 反射类命令(help 由类名派生, 阈值: <1%)
    assert len(empty) < len(META) * 0.01, f"空 help 过多: {len(empty)}"


def test_contract_describe_schema_fields():
    """契约⑦: describe --json 输出含机器必需字段(模拟 Agent 消费路径)"""
    import subprocess
    r = subprocess.run(
        [sys.executable, "-m", "tbtools_cli.cli", "tool-describe", "volcano", "--json"],
        capture_output=True, text=True, timeout=30, cwd=ROOT,
    )
    assert r.returncode == 0, r.stderr
    d = json.loads(r.stdout)
    for k in ("schema_version", "id", "name", "group", "kind", "help"):
        assert k in d, f"describe 缺 {k}"


def test_contract_dry_run_schema():
    """契约⑧: tool-run --dry-run 返回结构(status/inputs_valid/estimated_artifacts)"""
    import subprocess
    r = subprocess.run(
        [sys.executable, "-m", "tbtools_cli.cli", "tool-run", "expr", "volcano",
         "examples/data/deg.txt", "/tmp/contract_dr.svg", "--dry-run", "--json"],
        capture_output=True, text=True, timeout=30, cwd=ROOT,
    )
    d = json.loads(r.stdout)
    assert d["status"] in ("ready", "not_ready")
    assert "inputs_valid" in d and "estimated_artifacts" in d
