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

    def test_schema_capable_consistent(self):
        """README hero/正文 Schema-capable 64 == 有 inputs 契约的命令数(command_metadata)"""
        import json
        meta = json.loads((ROOT / "tbtools_cli" / "command_metadata.json").read_text(encoding="utf-8"))
        schema = sum(1 for e in meta.values() if e.get("inputs"))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        m = re.search(r"Schema-capable (\d+)", readme)
        assert m, "README 缺 Schema-capable 数"
        assert int(m.group(1)) == schema, f"README Schema-capable({m.group(1)}) != 实际({schema})"

    def test_schema_capable_version_json(self):
        """十四轮 gate/arch P1(GPT): version --json schema_capable == README == counts.md
        三方同源——此前 counts.md 有、JSON 无, Agent 消费面不完整。"""
        import json
        import sys
        sys.path.insert(0, str(ROOT))
        import subprocess
        r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "version", "--json"],
                           capture_output=True, text=True, cwd=ROOT, timeout=60)
        d = json.loads(r.stdout)
        assert "schema_capable" in d, "version --json 缺 schema_capable 字段"
        counts = (ROOT / "docs" / "_generated" / "counts.md").read_text(encoding="utf-8")
        m = re.search(r"schema_capable: (\d+)", counts)
        assert m, "counts.md 缺 schema_capable"
        assert d["schema_capable"] == int(m.group(1)), \
            f"version --json({d['schema_capable']}) != counts.md({m.group(1)})"

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


class TestCountsSurfaceGuard:
    """第五轮自审 docs 结论(P1 守卫缺口): counts.md 全字段 vs 门面手写数字。

    本轮 6 处 P1 漂移(49/218/82/66/54)全部落在无守卫区——门面(README/README_EN/
    index/quickstart/agent)手写数字没有任何机器核对, 漂移无感再生。此守卫按句式
    抽取门面数字与 counts.md 权威比对; 同时禁止已修旧漂移值回再生。
    """

    def _counts(self) -> dict:
        d = {}
        for line in (ROOT / "docs" / "_generated" / "counts.md").read_text(encoding="utf-8").splitlines():
            m = re.match(r"- ([a-z_]+): (\d+)", line.strip())
            if m:
                d[m.group(1)] = int(m.group(2))
        return d

    def test_plot_commands_surface(self):
        n = self._counts()["metadata_plot_commands"]
        zh = (ROOT / "README.md").read_text(encoding="utf-8")
        idx = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")
        qs = (ROOT / "docs" / "quickstart.md").read_text(encoding="utf-8")
        assert re.search(rf"Plotting Engines \({n}\)", zh), f"README plot 标题 != {n}"
        assert re.search(rf"#plotting-engines-{n}", zh), f"README plot 目录锚点 != {n}"
        assert f"{n} 绘图/分析命令" in idx, f"docs/index.md plot != {n}"
        assert f"{n} 个绘图命令" in qs, f"docs/quickstart.md plot != {n}"

    def test_rpc_surface(self):
        n = self._counts()["rpc_methods"]
        zh = (ROOT / "README.md").read_text(encoding="utf-8")
        en = (ROOT / "README_EN.md").read_text(encoding="utf-8")
        assert f"{n} 方法" in zh, f"README rpc 方法数 != {n}"
        assert f"{n} RPC data tools" in en, f"README_EN rpc != {n}"

    def test_tools_bridges_surface(self):
        c = self._counts()
        t, b = c["tools"], c["bridges"]
        zh = (ROOT / "README.md").read_text(encoding="utf-8")
        en = (ROOT / "README_EN.md").read_text(encoding="utf-8")
        cref = (ROOT / "docs" / "COMMAND_REFERENCE.md").read_text(encoding="utf-8")
        faq = (ROOT / "docs" / "faq.md").read_text(encoding="utf-8")
        assert (f"{t} CLI 工具" in zh or f"{t} 个 CLI 工具" in zh), f"README tools != {t}"
        assert f"{t} CLI tools" in en, f"README_EN tools != {t}"
        assert re.search(rf"共 {t} 个工具", cref), f"COMMAND_REFERENCE 工具总数 != {t}"
        assert (f"{b} Java 桥" in zh or f"{b} 个 Java bridge" in zh), f"README bridges != {b}"
        assert f"{b} Java bridges" in en, f"README_EN bridges != {b}"
        assert f"{b} 个 Java bridge" in faq, f"docs/faq.md bridges != {b}"

    def test_pitfalls_surface(self):
        n = self._counts()["pitfall_hints"]
        zh = (ROOT / "README.md").read_text(encoding="utf-8")
        en = (ROOT / "README_EN.md").read_text(encoding="utf-8")
        assert f"{n} 条实测坑位" in zh, f"README pitfalls != {n}"
        assert f"{n} documented pitfalls" in en, f"README_EN pitfalls != {n}"

    def test_legacy_drift_values_banned(self):
        """已修旧漂移值不得回再生——扫描面=全量现状文档(docs/*.md + README 双语),
        排除历史记录(_worklog/self_review/CHANGELOG 的旧数字是审计历史非现状漂移)。
        六轮 docs P1-2: 第五轮只盖 5 门面, 82(COMMAND_REFERENCE)/110+(faq)恰在
        覆盖外——改全量扫描堵死"漂移无感再生结构外移"。"""
        files = [ROOT / "README.md", ROOT / "README_EN.md"]
        files += [p for p in (ROOT / "docs").rglob("*.md")
                  if "_worklog" not in str(p) and "self_review" not in str(p)
                  and p.name != "CHANGELOG.md"]
        text = "\n".join(p.read_text(encoding="utf-8") for p in files)
        for legacy, hint in [("213", "plot 旧值"), ("110+", "bridges 旧值"),
                             ("180+", "rpc 旧值"), ("54 capabilities", "capabilities 旧表述"),
                             ("共 82 个工具", "tools 旧数")]:
            assert legacy not in text, f"文档出现已修漂移值 {legacy!r}({hint})"
