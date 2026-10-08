"""文档一致性测试(评审 #66b): README/protocol/counts 与代码必须一致——否则文档在讲旧版。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestDocConsistency:
    def test_mcp_count_consistent(self):
        """README/protocol 的 MCP 原语数 == mcp_server 实际 @mcp.tool() 数"""
        src = (ROOT / "tbtools_cli" / "mcp_server.py").read_text(encoding="utf-8")
        actual = src.count("@mcp.tool()")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        protocol = (ROOT / "docs" / "agent-protocol.md").read_text(encoding="utf-8")
        m = re.search(r"MCP 暴露 (\d+) 个", readme)
        assert m, "README 缺 MCP 原语数声明"
        assert int(m.group(1)) == actual, f"README MCP 数({m.group(1)}) != 代码({actual})"
        m2 = re.search(r"(\d+) 个编排原语", protocol)
        assert m2 and int(m2.group(1)) == actual, f"protocol MCP 数 != 代码({actual})"

    def test_full_count_consistent(self):
        """README hero FULL 数 == readiness_census"""
        import sys
        sys.path.insert(0, str(ROOT))
        from tbtools_cli.command_spec import readiness_census
        census = readiness_census()
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        m = re.search(r"(\d+) FULL contracts", readme)
        assert m, "README hero 缺 FULL 数"
        assert int(m.group(1)) == census["FULL"], f"README FULL({m.group(1)}) != census({census['FULL']})"

    # F-NEW-7(五视角自审): 门面手写数字守卫——README/README_EN/agent.md 的
    # schema-capable/execution_verified/命令总数必须与 counts.md 权威一致
    # (--check 只扫生成式 surface, 门面文档手写数字无机器核对 → 漂移无感再生)。
    def _counts(self):
        import json
        return json.loads((ROOT / "docs" / "_generated" / "counts.md").read_text(encoding="utf-8")
                          .split(": ", 1)[1].rsplit("}", 1)[0] + "}")

    def test_schema_capable_consistent(self):
        """README hero/正文 Schema-capable 64 == 有 inputs 契约的命令数(command_metadata)"""
        import json
        meta = json.loads((ROOT / "tbtools_cli" / "command_metadata.json").read_text(encoding="utf-8"))
        schema = sum(1 for e in meta.values() if e.get("inputs"))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        m = re.search(r"Schema-capable (\d+)", readme)
        assert m, "README 缺 Schema-capable 数"
        assert int(m.group(1)) == schema, f"README Schema-capable({m.group(1)}) != 实际({schema})"

    def test_execution_verified_consistent(self):
        """README 权威源行 execution_verified == version --json"""
        import json
        import sys
        sys.path.insert(0, str(ROOT))
        import subprocess
        r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "version", "--json"],
                           capture_output=True, text=True, cwd=ROOT, timeout=60)
        d = json.loads(r.stdout)
        n = d.get("execution_verified")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        m = re.search(r"execution_verified\((\d+)\)", readme)
        assert m, "README 缺 execution_verified(N)"
        assert int(m.group(1)) == n, f"README execution_verified({m.group(1)}) != 实际({n})"

    def test_english_and_agent_spec_count_consistent(self):
        """README_EN/agent.md 命令总数 == 298(与中文 README 同源)"""
        en = (ROOT / "README_EN.md").read_text(encoding="utf-8")
        agent = (ROOT / "docs" / "agent.md").read_text(encoding="utf-8")
        zh = (ROOT / "README.md").read_text(encoding="utf-8")
        m_zh = re.search(r"(\d+) Agent-facing tools", zh)
        total = int(m_zh.group(1)) if m_zh else 298
        assert str(total) in en, f"README_EN 缺 {total} 声明"
        assert str(total) in agent, f"agent.md 缺 {total} 声明"
