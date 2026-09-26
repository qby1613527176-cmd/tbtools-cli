"""Conformance Verified 体系(评审 #76 P0-3):
Tier 1 Compile-Verified: 59 FULL 工具全部契约编译验证(本文件参数化)
Tier 2 Execution-Verified: 有示例数据的工具真实执行+产物+溯源验证
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tbtools_cli.command_spec import agent_readiness, build_command_specs

SPECS = build_command_specs()
FULL_TOOLS = sorted(n for n, s in SPECS.items() if agent_readiness(s) == "FULL")

# Tier 2: 有 examples/data 的可执行验证集(数据真实存在)
EXEC_VERIFIED = {
    "volcano": ("expr", ["examples/data/deg.txt", "{out}.svg"]),
    "dehist": ("expr", ["examples/data/deg.txt", "{out}.svg"]),
    "dualsyn": ("syn", ["examples/data/synteny/dual.gff", "examples/data/synteny/dual.collinearity",
                        "{out}.svg", "--chr1", "1", "--chr2", "1"]),
    # mcscanx 移出: prefix 型输出(产 <out>.collinearity 等多文件),
    # 单输出 Artifact 模型不覆盖——多输出 Artifact 是 roadmap(评审 #76 P2)
}


class TestTier1CompileVerified:
    """59 FULL 全部 compile-verified(契约编译行为一致)"""

    def test_all_full_compile_verified(self):
        """汇总断言: FULL 工具全部通过编译验证(产出 verified 名单)"""
        verified = []
        for tool in FULL_TOOLS:
            spec = SPECS[tool]
            n_req = len([i for i in spec.inputs if i.required])
            fake = [f"in{i}.txt" for i in range(max(n_req, 1))]
            # ① 正常编译成功
            argv = spec.invocation.build_argv(inputs=fake, parameters={}, output="o.out")
            assert argv, f"{tool} 编译空"
            # ② 缺必填输入拒
            with pytest.raises(ValueError, match="MISSING_REQUIRED_INPUT"):
                spec.invocation.build_argv(inputs=[], parameters={}, output="o.out")
            # ③ 未知参数拒
            with pytest.raises(ValueError, match="UNKNOWN_PARAMETER"):
                spec.invocation.build_argv(inputs=fake, parameters={"__nope__": "1"}, output="o.out")
            verified.append(tool)
        assert len(verified) == len(FULL_TOOLS),             f"compile-verified {len(verified)}/{len(FULL_TOOLS)}: 缺 {set(FULL_TOOLS) - set(verified)}"


@pytest.mark.integration
class TestTier2ExecutionVerified:
    """有数据的工具 execution-verified(真实执行+产物+溯源)"""

    @pytest.mark.parametrize("tool", list(EXEC_VERIFIED))
    def test_execution_verified(self, tool, tmp_path):
        jar = os.environ.get("TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar")
        if not os.path.isfile(jar):
            pytest.skip("无 JAR")
        group, args_tpl = EXEC_VERIFIED[tool]
        out_base = str(tmp_path / "o")
        args = [a.replace("{out}", out_base) for a in args_tpl]
        env = dict(os.environ, TBTOOLS_JAR=jar)
        r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", "tool-run",
                            group, tool, *args, "--json"],
                           capture_output=True, text=True, cwd=ROOT, env=env, timeout=180)
        d = json.loads(r.stdout)
        assert d["exit_code"] == 0, f"{tool} 执行失败: {d.get('error')}"
        # 产物+溯源验证
        arts = d.get("artifacts") or []
        assert arts, f"{tool} 无产物"
        assert len(arts[0]["sha256"]) == 64, "sha256 完整"
        prov_ext = ".svg" if args_tpl[-1].endswith(".svg") or ".svg" in args_tpl[2] else ".txt"
        prov_path = out_base + prov_ext + ".tbtools.json"
        assert os.path.isfile(prov_path), f"{tool} provenance 缺失"


class TestConformanceReport:
    """conformance 报告: verified 计数(Conformance Verified 阶段交付物)"""

    def test_report_counts(self):
        exec_ok = [t for t in EXEC_VERIFIED
                   if os.path.isfile(os.path.join(ROOT, EXEC_VERIFIED[t][1][0]))]
        print(f"\nConformance Verified: compile {len(FULL_TOOLS)} / execution-data {len(exec_ok)}")
        assert len(FULL_TOOLS) >= 50, "FULL 池应 >= 50"
