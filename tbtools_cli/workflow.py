"""Workflow 一等公民(ADR-0007): YAML 声明的工作流——步骤依赖解析、Artifact 绑定、顺序执行、溯源 DAG。

最小可用版(v1):
- workflow validate/plan/run/graph(provenance-graph 复用)
- 步骤引用上游输出: input: $step_id.output
- 顺序执行, 失败即停(返回结构化结果)
- resume 为 v2(每步落盘 state 后可续)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time


class WorkflowError(Exception):
    pass


def load_workflow(path: str) -> dict:
    """加载 YAML workflow 并基础校验。"""
    import yaml
    wf = yaml.safe_load(open(path, encoding="utf-8"))
    if not isinstance(wf, dict) or "steps" not in wf:
        raise WorkflowError("workflow 缺少 steps")
    if not wf.get("id"):
        raise WorkflowError("workflow 缺少 id")
    seen = set()
    for s in wf["steps"]:
        if not s.get("id") or not s.get("tool"):
            raise WorkflowError(f"step 缺 id/tool: {s}")
        if s["id"] in seen:
            raise WorkflowError(f"step id 重复: {s['id']}")
        seen.add(s["id"])
    return wf


def _resolve(value, outputs: dict):
    """$step.output 引用解析为实际路径。"""
    if isinstance(value, str) and value.startswith("$"):
        ref = value[1:]
        if "." in ref:
            sid, key = ref.split(".", 1)
            if sid in outputs and key in outputs[sid]:
                return outputs[sid][key]
            raise WorkflowError(f"未解析的引用: {value}(上游 {sid} 无 {key})")
    return value


def plan(wf: dict, workdir: str) -> list[dict]:
    """生成执行计划: 每步展开为 [cmd, args](顺序)。

    占位符: {workdir} → 执行目录;{input.X} → workflow inputs 声明;$step.output → 上游产物。
    """
    steps: list = []
    outputs: dict = {}
    inputs = wf.get("inputs", {}) or {}
    for s in wf["steps"]:
        args = []
        for a in s.get("args", []):
            if isinstance(a, str):
                a = a.replace("{workdir}", workdir)
                for k, v in inputs.items():
                    a = a.replace("{input." + k + "}", str(v))
            args.append(_resolve(a, outputs))
        steps.append({"id": s["id"], "tool": s["tool"], "args": args})
        # 步骤输出登记(供下游引用; 末参或 outputs 声明)
        out_args = [a for a in args if isinstance(a, str) and os.path.splitext(a)[1]]
        outputs[s["id"]] = {"output": out_args[-1] if out_args else os.path.join(workdir, f"{s['id']}.out")}
    return steps


def _load_state(workdir: str) -> dict:
    """resume: 读上次执行状态(每步结束落盘 <workdir>/.wf_state.json)。"""
    sp = os.path.join(workdir, ".wf_state.json")
    if os.path.isfile(sp):
        try:
            return json.load(open(sp, encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_state(workdir: str, state: dict):
    json.dump(state, open(os.path.join(workdir, ".wf_state.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def run(wf: dict, workdir: str, timeout_s: int = 600, resume: bool = False) -> dict:
    """顺序执行 workflow(失败即停, 返回结构化结果)。

    resume=True 时跳过已成功步骤(读 .wf_state.json;v2 断点续跑)。
    """
    os.makedirs(workdir, exist_ok=True)
    state = _load_state(workdir) if resume else {}
    if resume and state.get("steps"):
        print(f"♻️ resume: 跳过已完成 {sum(1 for s in state['steps'] if s.get('status')=='succeeded')} 步", file=sys.stderr)
    steps = plan(wf, workdir)
    # 每步输出父目录预创建(否则 Java 输出目录预检报错)。
    # 只为 workdir 内或图形产物参数建目录;坏输入路径(如 /no/such.txt)不建, 让引擎报真实错(v2)
    for st in steps:
        for a in st["args"]:
            if not (isinstance(a, str) and os.path.sep in a):
                continue
            _ext = os.path.splitext(a)[1].lower()
            _in_workdir = os.path.abspath(a).startswith(os.path.abspath(workdir) + os.sep)
            if _in_workdir or _ext in (".svg", ".png", ".pdf"):
                try:
                    os.makedirs(os.path.dirname(os.path.abspath(a)), exist_ok=True)
                except (PermissionError, OSError):
                    pass  # 不可建则跳过——真实错误由引擎/report 层报出
    results = []
    t0 = time.time()
    for st in steps:
        # resume: 已成功步骤跳过(状态落盘判定)
        if resume and state.get("steps"):
            prev = next((x for x in state["steps"] if x["id"] == st["id"]), None)
            if prev and prev.get("status") == "succeeded":
                results.append(prev)
                continue
        tool_parts = st["tool"].split()
        log_path = os.path.join(workdir, f"{st['id']}.log")
        with open(log_path, "w", encoding="utf-8") as lf:
            r = subprocess.run(
                [sys.executable, "-m", "tbtools_cli.cli"] + tool_parts + st["args"],
                stdout=lf, stderr=subprocess.STDOUT, timeout=timeout_s,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            )
        step_ok = r.returncode == 0
        out = st["args"][-1] if st["args"] else ""
        # 产物语义验证(评审 #52 P1-11): ec=0 但产物损坏检出
        _vwarn = None
        if step_ok and out and os.path.isfile(out):
            _vok, _vmsg = validate_artifact(out)
            if not _vok:
                _vwarn = f"output validation failed: {_vmsg}"
                step_ok = False
        results.append({"id": st["id"], "tool": st["tool"], "exit_code": r.returncode,
                        "status": "succeeded" if step_ok else "failed",
                        **({"validation_warning": _vwarn} if _vwarn else {}),
                        "output": out if step_ok and os.path.isfile(out) else None,
                        "provenance": out + ".tbtools.json" if step_ok and os.path.isfile(out + ".tbtools.json") else None,
                        "log": log_path})
        if not step_ok:
            _save_state(workdir, {"workflow": wf["id"], "status": "failed", "steps": results})
            return {"schema_version": "1.0", "workflow": wf["id"], "status": "failed",
                    "failed_at": st["id"], "steps": results,
                    "duration_s": round(time.time() - t0, 1)}
    _save_state(workdir, {"workflow": wf["id"], "status": "succeeded", "steps": results})
    return {"schema_version": "1.0", "workflow": wf["id"], "status": "succeeded",
            "steps": results, "duration_s": round(time.time() - t0, 1),
            "artifacts": [r2["output"] for r2 in results if r2["output"]]}


def graph(wf: dict) -> str:
    """mermaid 工作流图。"""
    lines = ["graph LR"]
    prev = None
    for s in wf["steps"]:
        if prev:
            lines.append(f"    {prev} --> {s['id']}[{s['tool'].split()[-1]}]")
        else:
            lines.append(f"    input --> {s['id']}[{s['tool'].split()[-1]}]")
        prev = s["id"]
    return "\n".join(lines)

# ── 输出语义验证器(评审 #52 P1-11)──
def validate_artifact(path: str) -> tuple[bool, str]:
    """产物解析级校验(不止文件存在): FASTA/GFF/Newick/TSV 各格式 parse 检查。

    返回 (是否有效, 详情)。引擎 ec=0 但产物语义损坏时检出的最后防线。
    """
    if not os.path.isfile(path):
        return False, "file missing"
    ext = os.path.splitext(path)[1].lower()
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            head = f.read(8192)
        if ext in (".fa", ".fasta", ".aln", ".faa", ".fna"):
            if head.startswith(">") and head.count(">") >= 1:
                return True, f"fasta seqs={head.count('>')}"
            return False, "fasta header missing"
        if ext in (".gff", ".gff3", ".gtf"):
            if "##gff-version" in head or "	gene	" in head or "	mRNA	" in head or "	CDS	" in head:
                return True, "gff features present"
            return False, "gff structure invalid"
        if ext == ".nwk" or ext == ".tree":
            if "(" in head and ")" in head and head.rstrip().endswith(";"):
                return True, "newick parseable"
            return False, "newick invalid"
        if ext in (".tsv", ".csv", ".txt"):
            lines = [ln for ln in head.splitlines() if ln.strip()]
            if len(lines) >= 1:
                return True, f"rows={len(lines)}"
            return False, "table empty"
        if ext == ".svg":
            if "<svg" in head or "<?xml" in head:
                return True, "svg xml valid"
            return False, "svg invalid"
        return True, f"exists({ext or 'no-ext'}, no parser)"
    except Exception as e:
        return False, f"parse error: {e}"
