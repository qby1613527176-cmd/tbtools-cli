"""第 14 份评审回归: workflow 契约化 validate/输出识别/resume sha/inspect bug。"""
import json
import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_cli(*args, timeout=60):
    env = dict(os.environ, TBTOOLS_JAR=os.environ.get(
        "TBTOOLS_JAR", "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar"))
    r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", *args],
                       capture_output=True, text=True, timeout=timeout, cwd=ROOT, env=env)
    return r.returncode, r.stdout, r.stderr


class TestWorkflowValidate:
    def test_valid_workflow(self):
        ec, out, _ = run_cli("workflow", "validate", "examples/workflows/gxf-ops/workflow.yaml")
        assert ec == 0
        assert json.loads(out)["valid"] is True

    def test_invalid_tool_detected(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("""id: t
steps:
  - id: s1
    tool: nosuchtool
    args: ["{input}", "{workdir}/a.out"]
""")
        ec, out, _ = run_cli("workflow", "validate", str(bad))
        assert ec == 3
        d = json.loads(out)
        assert any(e["code"] == "WORKFLOW_INVALID_TOOL" for e in d["errors"])

    def test_invalid_dependency_and_binding(self, tmp_path):
        bad = tmp_path / "bad2.yaml"
        bad.write_text("""id: t
steps:
  - id: s1
    tool: tableCollapse
    args: ["{input}", "{workdir}/a.tsv"]
  - id: s2
    tool: tableCast
    depends_on: ["s9"]
    args: ["$s1.output", "$s9.output", "{workdir}/b.tsv"]
""")
        ec, out, _ = run_cli("workflow", "validate", str(bad))
        assert ec == 3
        codes = [e["code"] for e in json.loads(out)["errors"]]
        assert "WORKFLOW_INVALID_DEPENDENCY" in codes and "WORKFLOW_INVALID_BINDING" in codes

    def test_cycle_detected(self, tmp_path):
        bad = tmp_path / "bad3.yaml"
        bad.write_text("""id: t
steps:
  - id: s1
    tool: tableCollapse
    depends_on: ["s2"]
    args: ["{input}", "{workdir}/a.tsv"]
  - id: s2
    tool: tableCast
    depends_on: ["s1"]
    args: ["{input}", "{workdir}/b.tsv"]
""")
        ec, out, _ = run_cli("workflow", "validate", str(bad))
        assert ec == 3
        assert any(e["code"] == "WORKFLOW_CYCLE" for e in json.loads(out)["errors"])


class TestArtifactInspectBug:
    def test_missing_file_not_found(self):
        ec, out, _ = run_cli("artifact", "inspect", "/tmp/definitely_not_exist_xyz.svg", "--json")
        assert ec == 3
        d = json.loads(out)
        assert d["status"] == "not_found" and d["error"]["code"] == "ARTIFACT_NOT_FOUND"

    def test_artifact_id_stable_and_long(self, tmp_path):
        sys.path.insert(0, ROOT)
        from tbtools_cli.artifact import build
        p = tmp_path / "a.svg"
        p.write_text("<svg>x</svg>")
        a1, a2 = build(str(p)), build(str(p))
        assert a1.id == a2.id, "ID 应稳定"
        assert len(a1.id) == 4 + 32, "ID 应为 art_ + sha256[:32]"
        assert len(a1.sha256) == 64, "sha256 完整 64 位"


class TestWorkflowIdStable:
    def test_cross_process_stable(self):
        sys.path.insert(0, ROOT)
        from tbtools_cli.workflow import plan_from_goal
        p1 = plan_from_goal("volcano plot", input_format="tsv")
        r = subprocess.run([sys.executable, "-c",
                            "import sys; sys.path.insert(0,'.');"
                            "from tbtools_cli.workflow import plan_from_goal;"
                            "print(plan_from_goal('volcano plot', input_format='tsv')['workflow']['workflow_id'])"],
                           capture_output=True, text=True, cwd=ROOT)
        assert p1["workflow"]["workflow_id"] == r.stdout.strip(), "workflow_id 应跨进程稳定"
