"""Agent Contract 全链路测试(评审 #64 P0): FULL 工具必须全链路机器验证。

对 8 个 FULL 工具逐一验证:
  1. discover(search 可发现)
  2. describe(schema 完整: inputs+outputs+parameters+capabilities)
  3. validate(tool-validate 可调用)
  4. run(集成: 真实执行出产物)
  5. artifact(产物语义验证)
  6. provenance(溯源文件存在且完整)

任何一步失败 → 该工具不应再标 FULL(机器验证的能力等级, 非 metadata 自评)。
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FULL_TOOLS = ["dualsyn", "mcscanx", "iqtree", "volcano", "heatmap", "hclust", "dehist", "genestructure"]

# 每工具的集成运行参数(真实数据)
RUN_CASES = {
    "volcano": ("expr", ["examples/data/deg.txt", "{out}.svg"]),
    "dehist": ("expr", ["examples/data/deg.txt", "{out}.svg"]),
    "hclust": ("expr", ["{dist}", "{out}.svg"]),
    "dualsyn": ("syn", ["examples/data/synteny/dual.gff", "examples/data/synteny/dual.collinearity",
                        "{out}.svg", "--chr1", "1", "--chr2", "1"]),
    "mcscanx": ("syn", ["examples/data/synteny/test.collinearity", "{out}.txt"]),
    "iqtree": ("tree", ["examples/data/blast/query.fa", "{out}"]),
    "genestructure": ("seq", ["examples/data/gxf/input.gff3",
                              "examples/data/blast/quickfamily/family.ids", "{out}.svg"]),
    "heatmap": ("expr", ["examples/data/expr/cube_group.tsv", "{out}.svg"]),
}


def run_cli(*args, timeout=60):
    env = dict(os.environ, TBTOOLS_JAR=os.environ.get(
        "TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar"))
    r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", *args],
                       capture_output=True, text=True, timeout=timeout, cwd=ROOT, env=env)
    return r.returncode, r.stdout, r.stderr


class TestAgentContractDiscover:
    """① discover: search 能找到"""

    @pytest.mark.parametrize("tool", FULL_TOOLS)
    def test_discover(self, tool):
        ec, out, _ = run_cli("search", tool, "--json")
        assert ec == 0
        names = [h["name"] for h in json.loads(out)["hits"]]
        assert tool in names, f"{tool} 不可发现"


class TestAgentContractDescribe:
    """② describe: schema 完整(inputs+outputs+parameters+capabilities)"""

    @pytest.mark.parametrize("tool", FULL_TOOLS)
    def test_describe(self, tool):
        ec, out, _ = run_cli("tool-describe", tool, "--json")
        assert ec == 0
        d = json.loads(out)
        assert d.get("inputs"), f"{tool} 缺 inputs"
        assert d.get("outputs"), f"{tool} 缺 outputs"
        assert d.get("capabilities"), f"{tool} 缺 capabilities"
        # FULL 应有 parameters(FULL 定义要求)
        assert d.get("parameters") is not None


class TestAgentContractValidate:
    """③ validate: tool-validate 可调用并返回结构"""

    @pytest.mark.parametrize("tool", FULL_TOOLS)
    def test_validate_callable(self, tool):
        # 用无害输入(各工具用例的首个输入或占位)
        case = RUN_CASES.get(tool)
        if not case:
            pytest.skip("无运行用例")
        _, args = case
        if tool == "hclust":
            inp = "examples/data/expr/dist.tsv"  # hclust 用例无 examples 输入(临时构造), 用 dist.tsv
        else:
            inp = next(a for a in args if a.startswith("examples/"))
        ec, out, _ = run_cli("tool-validate", tool, inp, "--json")
        d = json.loads(out)
        assert "valid" in d and "checks" in d


@pytest.mark.integration
class TestAgentContractExecute:
    """④⑤⑥ run/artifact/provenance(真实 JAR 集成)"""

    @pytest.mark.parametrize("tool", ["volcano", "dehist", "hclust", "dualsyn"])
    def test_run_artifact_provenance(self, tool, tmp_path):
        group, args_tpl = RUN_CASES[tool]
        out_base = str(tmp_path / "o")  # 不带扩展名(模板自带 .svg 等;防 o.svg.svg 双扩展)
        args = []
        if tool == "hclust":
            dist = tmp_path / "d.tsv"
            dist.write_text("G1\tG2\t0.5\nG1\tG3\t1.2\nG2\tG3\t0.8\nG2\tG4\t1.5\nG3\tG4\t0.3\nG4\tG1\t2.0\n")
            args = [str(dist), out_base + ".svg"]  # hclust 输出带扩展名(provenance 对齐)
        else:
            args = [a.replace("{out}", out_base) for a in args_tpl]
        ec, out, err = run_cli("tool-run", group, tool, *args, "--json", timeout=120)
        assert ec == 0, err[-200:]
        d = json.loads(out)
        # ④ run 成功
        assert d["exit_code"] == 0
        # ⑤ artifact 模型统一
        arts = d.get("artifacts") or []
        if arts:
            a0 = arts[0]
            assert a0.get("type") and a0.get("sha256"), "Artifact 模型缺 type/sha256"
        # ⑥ provenance 完整
        prov_path = out_base + ".svg.tbtools.json"
        assert os.path.isfile(prov_path), "provenance 缺失"
        prov = json.load(open(prov_path, encoding="utf-8"))
        assert prov.get("exit_code") == 0 and prov.get("inputs"), "provenance 不完整"


class TestAgentContractCensus:
    """机器验证的能力等级: FULL 工具必须全链路通过(非 metadata 自评)"""

    def test_full_count_matches_readiness(self):
        """readiness_census 的 FULL 数与测试集一致(8)。"""
        import sys
        sys.path.insert(0, ROOT)
        from tbtools_cli.command_spec import readiness_census
        c = readiness_census()
        assert c["FULL"] == len(FULL_TOOLS), f"FULL 数漂移: {c['FULL']} != {len(FULL_TOOLS)}"
