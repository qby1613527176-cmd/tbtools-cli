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
