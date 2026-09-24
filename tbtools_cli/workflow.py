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
    steps = []
    outputs = {}
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


def run(wf: dict, workdir: str, timeout_s: int = 600) -> dict:
    """顺序执行 workflow(失败即停, 返回结构化结果)。"""
    os.makedirs(workdir, exist_ok=True)
    steps = plan(wf, workdir)
    # 每步输出父目录预创建(否则 Java 输出目录预检报错)
    for st in steps:
        for a in st["args"]:
            if isinstance(a, str) and os.path.splitext(a)[1] and os.path.sep in a:
                os.makedirs(os.path.dirname(os.path.abspath(a)), exist_ok=True)
    results = []
    t0 = time.time()
    for st in steps:
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
        results.append({"id": st["id"], "tool": st["tool"], "exit_code": r.returncode,
                        "status": "succeeded" if step_ok else "failed",
                        "output": out if step_ok and os.path.isfile(out) else None,
                        "provenance": out + ".tbtools.json" if step_ok and os.path.isfile(out + ".tbtools.json") else None,
                        "log": log_path})
        if not step_ok:
            return {"schema_version": "1.0", "workflow": wf["id"], "status": "failed",
                    "failed_at": st["id"], "steps": results,
                    "duration_s": round(time.time() - t0, 1)}
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
