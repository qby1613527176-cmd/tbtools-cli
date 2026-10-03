"""Workflow 一等公民(ADR-0007): YAML 声明的工作流——DAG 步骤依赖解析、Artifact 绑定、
并行调度、溯源、fingerprint-aware resume。

能力(v1.4.20+):
- workflow validate/plan/run/graph(provenance-graph 复用)
- 步骤引用上游输出: input: $step_id.output; binding 契约编译(CommandSpec)
- DAG 并行调度(ready-queue; depends_on 声明; 环检测; fail-fast 早取消; cancel 传播)
- 三层 identity fingerprint(contract/binding/execution; 内容寻址; resume 闸门)
- resume: 每步落盘 state 后可续; fp 不匹配 → 重跑(篡改拦截)
- artifact 登记 + provenance 旁文件(含三层 fingerprint; Agent 可读)
"""
from __future__ import annotations

import json
import os
import sys

# Identity 层(评审 #108 P1-4 拆分): canonical/fingerprint 常量与函数统一从 identity.py 引入——
# workflow 不再自行定义第二份(消除双源); command_spec 也只向下依赖 identity。
# ⚠️ 此处同时是向后兼容 re-export: 旧代码/测试从 workflow import semantic_fingerprint 等仍可用。
# 未直接使用的符号标 noqa: F401(有意 re-export, 评审 #108: 解 command_spec↔workflow 双向依赖)
from tbtools_cli.identity import (  # noqa: E402
    CONTRACT_SCHEMA_VERSION, DEP_VERSION_ARGS, EXECUTION_CONTRACT_FIELDS,  # noqa: F401
    FP_SCHEME_VERSION, WORKFLOW_SCHEMA_CURRENT, canonical_contract,  # noqa: F401
    canonical_execution_contract, canonical_semantic_identity,  # noqa: F401
    contract_fingerprint_for, execution_contract_fingerprint, semantic_fingerprint,  # noqa: F401
)

# dep 版本缓存(评审 #100 + #102 P1-2): 模块级声明, 防 flaky——同一进程内
# 外部依赖版本只探测一次(每次 compile fork 查版本会因超时/失败随机漂移 execution_fp);
# 缓存 key 带可执行文件身份(评审 #107 P1⑥: name+path+mtime+size)
# 评审 #112 P2: 缓存实体迁到 dependency.py, 此处 re-export 同一对象(旧代码/测试
# from workflow import _DEP_VERSION_CACHE 仍可用, 且与 dependency 共享状态)
from tbtools_cli.dependency import _DEP_VERSION_CACHE  # noqa: E402,F401

# Compiler 层(评审 #112 P2 拆分): binding/argv 编译逻辑迁到 compiler.py——
# ⚠️ re-export: 旧代码/测试 from workflow import compile_step_full/WorkflowError 等仍可用

# Runtime 层(评审 #112 P2 拆分): 状态机/执行器迁到 runtime.py——
# ⚠️ re-export: 旧代码/测试 from workflow import run/_execute_step 等仍可用
from tbtools_cli.executor import (  # noqa: E402
    run, _execute_step, _run_parallel, _resume_gate,  # noqa: F401
    _load_state, _save_state, _merge_state_step, validate_artifact,  # noqa: F401
)
from tbtools_cli.compiler import (  # noqa: E402
    WorkflowError, _resolve, _stable_wf_id, CompiledInvocation,  # noqa: F401
    compile_step_full, compile_step, resolve_input_binding,  # noqa: F401
    _bind_slots, _plan_to_spec, _default_args,  # noqa: F401
)



def _warn_legacy_args(wf: dict):
    """legacy args 退役警告(评审 #76 P1-3): v1.x 兼容,v2.0 移除——迁移 binding。"""
    legacy = [s.get("id", "?") for s in (wf.get("steps") or []) if not s.get("binding")]
    if legacy:
        print(f"⚠️ DeprecationWarning: workflow {wf.get('id', '?')} 的 {len(legacy)} 个步骤({', '.join(legacy[:3])})"
              f"使用 legacy args 形态——v2.0 将移除,请迁移 binding 形态({{inputs/parameters/output}})",
              file=sys.stderr)


# ⚠️ 命名区分(评审 #92 P1-4): 这是 **workflow schema version**,与 docs/agent-protocol.md 的
# Agent Protocol version(调用协议)是两个独立版本线——改名/升版时勿混淆。


def load_workflow(path: str) -> dict:
    """加载 YAML workflow 并基础校验(schema_version 正式化, 评审 #82 P2-8)。"""
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
    _warn_legacy_args(wf)  # 评审 #76 P1-3: legacy 退役警告
    # schema_version 正式化(评审 #82 P2-8): 无版本按 args=1.0 推断;2.0 拒 args
    _sv = str(wf.get("schema_version", ""))
    if not _sv:
        wf["schema_version"] = "1.1" if any(s.get("binding") for s in wf["steps"]) else "1.0"
    elif _sv.startswith("2"):
        if any(not s.get("binding") for s in wf["steps"]):
            raise WorkflowError("schema_version 2.0 为 binding-only——存在 args 形态步骤,请迁移 binding")
    return wf




def plan(wf: dict, workdir: str, runtime_resolve: bool = False) -> list[dict]:
    """生成执行计划: 每步展开为 [cmd, args](顺序)。

    占位符: {workdir} → 执行目录;{input.X} → workflow inputs 声明;$step.output → 上游产物。
    runtime_resolve(评审 #110 P0-2): 默认 False=纯静态(规划/validate 不读输入 sha);
    run() 传 True 以获得完整 execution_fp(resume 闸门需要 input sha 检测篡改)。
    """
    steps: list = []
    outputs: dict = {}
    inputs = wf.get("inputs", {}) or {}
    for s in wf["steps"]:
        # binding 形态(契约): compile_step 统一编译(评审 #72 P0-3: run/validate 同一 compiler)
        if s.get("binding"):
            s = dict(s)
            _raw_binding = dict(s["binding"])  # P0-1(评审 #100): raw symbolic binding(替换前)
            _bj = json.dumps(s["binding"])
            for k, v in inputs.items():
                _bj = _bj.replace("{input." + k + "}", str(v))
            # {input} 裸占位(planner 生成)→ 首个/唯一 input(评审 #74)
            if "{input}" in _bj:
                if inputs:
                    _first = str(next(iter(inputs.values())))
                    _bj = _bj.replace("{input}", _first)
                else:
                    raise WorkflowError(f"step {s.get('id')} 引用 {{input}} 但 workflow 无 inputs 声明")
            _bj = _bj.replace("{workdir}", workdir)
            s["binding"] = json.loads(_bj)
            _ci = compile_step_full(s, workdir, outputs, symbolic_override=_raw_binding,
                                    runtime_resolve=runtime_resolve)  # 评审 #110 P0-2: 由 plan 参数决定
            args = _ci.argv
            # 输出登记编译结构(评审 #88 P0-1): binding.outputs 精确,不再 out_args[-1] 猜
            steps.append({"id": s["id"], "tool": s["tool"], "args": args,
                          "_compiled_outputs": _ci.outputs,
                          "_execution_fingerprint": _ci.execution_fingerprint,
                          "_contract_fingerprint": _ci.contract_fingerprint,
                          "_binding_fingerprint": _ci.binding_fingerprint})  # 评审 #104
            outputs[s["id"]] = {"output": _ci.outputs[0] if _ci.outputs
                                        else os.path.join(workdir, f"{s['id']}.out")}
            continue
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


def _topo_sort(steps: list) -> list:
    """拓扑排序(depends_on 声明的步骤按依赖排序;环检测)。"""
    done, ordered = set(), []
    remaining = list(steps)
    while remaining:
        progressed = False
        for s in list(remaining):
            deps = s.get("depends_on") or s.get("dependsOn") or []
            if all(d in done for d in deps):
                ordered.append(s)
                done.add(s["id"])
                remaining.remove(s)
                progressed = True
        if not progressed:
            raise WorkflowError(f"depends_on 存在循环依赖: {[s['id'] for s in remaining]}")
    return ordered



def validate_workflow(wf: dict) -> dict:
    """Workflow 契约验证(评审 #68 P0-1): Syntax→Graph→Tool Contract→Binding 四层。

    返回 {valid, errors:[{code, step?, tool?, message}]}——结构化 errors,不只 plan/不 plan。
    code: WORKFLOW_INVALID_TOOL / WORKFLOW_INVALID_DEPENDENCY / WORKFLOW_CYCLE /
          WORKFLOW_INVALID_BINDING / WORKFLOW_MISSING_STEP_ID
    """
    from tbtools_cli.command_spec import build_command_specs
    specs = build_command_specs()
    errors = []
    steps = wf.get("steps") or []
    ids = [s.get("id") for s in steps]
    # Layer 1 Syntax: id 唯一/非空
    for i, sid in enumerate(ids):
        if not sid:
            errors.append({"code": "WORKFLOW_MISSING_STEP_ID", "step": f"#{i + 1}",
                           "message": "step 缺 id"})
    if len(ids) != len(set(ids)):
        errors.append({"code": "WORKFLOW_DUP_STEP_ID",
                       "message": f"step id 重复: {[x for x in set(ids) if ids.count(x) > 1]}"})
    idset = set(i for i in ids if i)
    # Layer 2 Tool Contract: tool 存在(带组名或裸名)
    for s in steps:
        tool = str(s.get("tool", ""))
        bare = tool.split()[-1] if tool else ""
        if bare and bare not in specs:
            errors.append({"code": "WORKFLOW_INVALID_TOOL", "step": s.get("id"),
                           "tool": tool, "message": f"工具不存在: {tool}"})
    # Layer 3 Graph: depends_on 引用存在 + 环检测
    for s in steps:
        for d in (s.get("depends_on") or s.get("dependsOn") or []):
            if d not in idset:
                errors.append({"code": "WORKFLOW_INVALID_DEPENDENCY", "step": s.get("id"),
                               "message": f"depends_on 引用不存在的 step: {d}"})
    if not any(e["code"].startswith("WORKFLOW_") and e["code"] != "WORKFLOW_MISSING_STEP_ID"
               and "DUP" not in e["code"] and "TOOL" in e["code"] for e in errors):
        try:
            _topo_sort([s for s in steps if s.get("id")])
        except WorkflowError as e:
            errors.append({"code": "WORKFLOW_CYCLE", "message": str(e)})
    # Layer 2b Binding 编译(评审 #72 P0-2): binding 形态步骤走 compile_step 干跑——validate==compile success
    # P0-4(评审 #84): 干跑前拓扑排序(与 run 一致;$step.output 须在依赖之后声明)
    _dry_steps = steps
    if any(s.get("depends_on") or s.get("dependsOn") for s in steps):
        try:
            _dry_steps = _topo_sort(steps)
        except WorkflowError:
            pass  # 环错误已在 Layer 3 捕获
    import tempfile as _tf
    _dry_wd = _tf.mkdtemp(prefix="tb_wfval_")
    _dry_outputs: dict = {}
    for s in _dry_steps:
        if s.get("binding"):
            try:
                # P0(评审 #92): validate 消费 CompiledInvocation.outputs(不再 argv 扩展名猜)
                # 评审 #108 P1-2: validate 用 static compile(runtime_resolve=False)——
                # 不 fork 外部工具探测版本/不读输入内容(validate 保持纯静态检查)
                _ci = compile_step_full(s, _dry_wd, _dry_outputs, runtime_resolve=False)
                _dry_outputs[s.get("id")] = {"output": _ci.outputs[0] if _ci.outputs
                                                     else f"{s.get('id')}.out"}
            except WorkflowError as e:
                errors.append({"code": "WORKFLOW_COMPILE_ERROR", "step": s.get("id"),
                               "message": str(e)})
    # Layer 4 Binding: $step.output 引用存在 + 在依赖之前声明
    import re as _re
    for s in steps:
        for a in s.get("args", []):
            if isinstance(a, str):
                for ref in _re.findall(r"\$([A-Za-z0-9_]+)\.output", a):
                    if ref not in idset:
                        errors.append({"code": "WORKFLOW_INVALID_BINDING", "step": s.get("id"),
                                       "message": f"绑定了不存在的 step 输出: ${ref}.output"})
                    deps = set(s.get("depends_on") or s.get("dependsOn") or [])
                    if deps and ref not in deps:
                        errors.append({"code": "WORKFLOW_INVALID_BINDING", "step": s.get("id"),
                                       "message": f"${ref}.output 引用但 depends_on 未声明 {ref}"})
    return {"schema_version": WORKFLOW_SCHEMA_CURRENT, "valid": not errors,
            "steps": len(steps), "errors": errors}

def graph(wf: dict) -> str:
    """mermaid 工作流图(评审 #66 P0-3: 读取 depends_on 画真 DAG, 不再线性链)。"""
    lines = ["graph LR"]
    has_dep = False
    for s in wf["steps"]:
        deps = s.get("depends_on") or s.get("dependsOn") or []
        if deps:
            has_dep = True
            for d in deps:
                lines.append(f"    {d} --> {s['id']}[{s['tool'].split()[-1]}]")
        else:
            lines.append(f"    input --> {s['id']}[{s['tool'].split()[-1]}]")
    if not has_dep:
        # 无显式 depends_on 时按声明顺序画链(兼容旧格式)
        prev = None
        for s in wf["steps"]:
            if prev:
                lines.append(f"    {prev} --> {s['id']}[{s['tool'].split()[-1]}]")
            prev = s["id"]
    return "\n".join(lines)

# ── 输出语义验证器(评审 #52 P1-11)──
def plan_from_goal(goal: str, input_format: str = "", output_format: str = "",
                   max_steps: int = 4) -> dict:
    """目标驱动规划: 输入类型 + 目标/输出类型 → relations/capability 推导工具链。

    算法: 起点=接受 input_format 的工具(relations.accepts 或 inputs.format 匹配)
    → 沿 next_step 扩展 → 终点=产出 output_format 或 capability 匹配 goal 的工具。
    返回 {goal, plan:[{step, tool, reason}], confidence, alternatives}。
    """
    from tbtools_cli.command_spec import build_command_specs
    specs = build_command_specs()
    goal_l = goal.lower()
    # ── 契约图搜索(评审 #70 P0-3): A.outputs ↔ B.inputs 真实配对,DFS 探索所有分支 ──
    def _accepts(tool_spec, fmt: str) -> bool:
        """接受性判断(评审 #109): 字面 + 格式族语义匹配——
        'aln' 应命中 ALIGNMENT 族, 'fa' 应命中 FASTA 族(原实现只字面相等, 组织级 ALIGNMENT 永远匹配不到 'aln')。"""
        if not fmt:
            return False
        ins_fmts = [i.format.lower() for i in (tool_spec.inputs or [])]
        rel_acc = [a.lower() for a in ((tool_spec.relations or {}).get("accepts") or [])]
        if fmt.lower() in ins_fmts or fmt.lower() in rel_acc:
            return True
        # 格式族语义匹配(评审 #72 P1-1 复用): aln↔ALIGNMENT, fa↔FASTA, tsv↔TABLE
        # _FORMAT_FAMILIES 在闭包内后定义, 调用时已存在(运行时解析)
        in_family = {f: fam for fam, members in _FORMAT_FAMILIES.items() for f in members}
        fmt_fam = in_family.get(fmt.lower())
        if fmt_fam:
            for acc in ins_fmts + rel_acc:
                if acc in in_family and in_family[acc] == fmt_fam:
                    return True
                if acc.lower() == fmt_fam or fmt.lower() == acc.lower():
                    return True
        return False

    def _produces(tool_spec) -> list:
        outs = [str(o).lower() for o in (tool_spec.outputs or [])]
        rel_prods = [p.lower() for p in ((tool_spec.relations or {}).get("produces") or [])]
        return outs + rel_prods

    def _goal_match(name):
        spec = specs[name]
        caps = " ".join(spec.capabilities + (spec.__dict__.get("capabilities_ontology") or [])).lower()
        prods = " ".join(_produces(spec))
        hay = caps + " " + prods + " " + name.lower()
        for k in goal_l.split():
            if len(k) < 3:
                continue
            root = k[:7] if len(k) > 7 else k
            if root in hay or any(wd.startswith(root) for wd in hay.replace(".", " ").replace("-", " ").split()):
                return True
        return False

    # format ontology(评审 #72 P1-1): 格式族 + 三级匹配(exact/compatible/incompatible)
    _FORMAT_FAMILIES = {
        "sequence": {"fasta", "fa", "fastq", "faa", "fna", "pep"},
        "alignment": {"aln", "alignment", "trimmed_alignment", "clustal", "maf", "sto", "afa"},
        "table": {"tsv", "csv", "txt", "xls", "xlsx", "count_table", "table", "tab"},
        "tree": {"nwk", "tree", "treefile", "newick", "tre", "contree"},
        "annotation": {"gff", "gff3", "gtf", "bed", "gxf"},
        "graphics": {"svg", "png", "pdf"},
        "synteny": {"collinearity", "anchors", "blast", "m8"},
        "mapping": {"sam", "bam", "paf"},
    }

    def _fmt_level(a: str, b: str) -> str:
        """格式匹配级别: exact(1.0) / compatible(同族 0.7) / incompatible(0)。
        子串匹配降级为 compatible(不再是 exact)。"""
        a, b = a.lower(), b.lower()
        if a == b:
            return "exact"
        for fam in _FORMAT_FAMILIES.values():
            if a in fam and b in fam:
                return "compatible"
        # 子串(如 trimmed_alignment vs alignment)——同一语义家族但弱化
        if (len(a) >= 3 and a in b) or (len(b) >= 3 and b in a):
            return "compatible"
        return "incompatible"

    def _fmt_match(a: str, b: str) -> bool:
        return _fmt_level(a, b) != "incompatible"

    def _edge(a_name: str, b_name: str) -> str | None:
        """A→B 兼容边: A 产出格式 ∩ B 接受格式(契约图核心)。"""
        for ofmt in _produces(specs[a_name]):
            ins_fmts = [i.format.lower() for i in (specs[b_name].inputs or [])]
            rel_acc = [x.lower() for x in ((specs[b_name].relations or {}).get("accepts") or [])]
            for ifmt in ins_fmts + rel_acc:
                if _fmt_match(ofmt, ifmt):
                    return ofmt
        return None

    def _content_compat(a_name: str, b_name: str) -> bool | None:
        """content_type 兼容(评审 #82 P0-3: slot 级): A 输出语义 vs B 首必填输入槽位语义。
        None=无标注(中性);True=兼容;False=冲突(protein→dna 工具)。"""
        from tbtools_cli.command_spec import KNOWN_CONTENT_TYPES
        # B 输入语义: slot 级(首必填 InputSpec.content_type),回退工具级
        b_spec = specs.get(b_name)
        cb = None
        if b_spec and b_spec.inputs:
            _req = [i for i in b_spec.inputs if i.required]
            cb = (_req[0].content_type if _req else b_spec.inputs[0].content_type)
            if cb == "generic":
                cb = None
        if not cb:
            cb = KNOWN_CONTENT_TYPES.get(b_name)
        # A 输出语义(评审 #86 P1-5: output_slots 槽位级最优先 → KNOWN_OUTPUT → 工具级)
        from tbtools_cli.command_spec import KNOWN_OUTPUT_CONTENT_TYPES
        # output-slot → input-slot 配对(评审 #94 P1-1):
        # A 每个 output slot 与 B 每个 input slot 找兼容对(不再"A 第一槽 vs B 第一槽")
        _a_spec2, _b_spec2 = specs.get(a_name), specs.get(b_name)
        if _a_spec2 and _a_spec2.output_slots and _b_spec2 and _b_spec2.inputs:
            for _os in _a_spec2.output_slots:
                for _is in _b_spec2.inputs:
                    if _os.content_type != "generic" and _is.content_type != "generic":
                        if _os.content_type == _is.content_type:
                            return True
                        if "table" in (_os.content_type, _is.content_type):
                            return True
                        if {_os.content_type, _is.content_type} <= {"alignment", "protein", "dna"}:
                            return True
            if any(o.content_type != "generic" for o in _a_spec2.output_slots) and \
                    any(i.content_type != "generic" for i in _b_spec2.inputs):
                return False  # 有标注但无兼容对 → 冲突
        ca = None
        _a_spec = _a_spec2
        if _a_spec and _a_spec.output_slots:
            for _os in _a_spec.output_slots:
                if _os.content_type and _os.content_type != "generic":
                    ca = _os.content_type
                    break
        if not ca:
            ca = KNOWN_OUTPUT_CONTENT_TYPES.get(a_name) or KNOWN_CONTENT_TYPES.get(a_name)
        if not ca or not cb:
            return None
        if ca == cb:
            return True
        if cb == "table" or ca == "table":
            return True
        if ca == "alignment" and cb in ("protein", "dna"):
            return True
        if ca in ("dna", "protein") and cb == "alignment":
            return True
        return False

    def _edge_info(a_name: str, b_name: str) -> dict:
        """边信息(评审 #72 P1-2): {type: contract|legacy_relation, match: exact|compatible}。"""
        ofmt = _edge(a_name, b_name)
        if ofmt:
            ins_fmts = [i.format.lower() for i in (specs[b_name].inputs or [])]
            lvl = max((_fmt_level(ofmt, f) for f in ins_fmts), default="compatible",
                      key=lambda x: {"exact": 1, "compatible": 0.5, "incompatible": 0}[x])
            return {"type": "contract", "format": ofmt, "match": lvl}
        rel_next = (specs[a_name].relations or {}).get("next_step", [])
        if b_name in rel_next:
            return {"type": "legacy_relation", "format": "", "match": "unknown"}
        return {"type": "none", "format": "", "match": "incompatible"}

    # 可执行性三态(评审 #74 P0-4): EXECUTABLE(单必填输入可绑定)/
    # PARTIALLY_BINDABLE(有可选输入)/UNEXECUTABLE(多必填输入,planner 无法绑定→排除,不入选)
    def _bindability(name: str) -> str:
        """评审 #82 P0-1: 多必填输入不再一律 UNEXECUTABLE——slot resolver 可绑定则入选。
        MULTI_INPUT: >1 必填(经 _bind_slots 生成 dict 绑定,额外槽位引用 workflow inputs)"""
        spec = specs[name]
        req = [i for i in (spec.inputs or []) if i.required]
        if len(req) > 1:
            return "MULTI_INPUT"
        if len((spec.inputs or [])) > 1:
            return "PARTIALLY_BINDABLE"
        return "EXECUTABLE"

    def _bind_slots_local(name: str, first_ref: str, wf_inputs: dict) -> dict | None:
        return _bind_slots(name, first_ref, wf_inputs, specs)

    # 起点(去重: 评审 #70 P0-5——同一工具 schema+relations 双命中不再重复探索)
    starts, _seen_starts = [], set()
    for name, spec in specs.items():
        if _accepts(spec, input_format) and name not in _seen_starts:
            _seen_starts.add(name)
            starts.append(name)
    starts = [n for n in starts if not (
        _bindability(n) == "MULTI_INPUT" and not (specs[n].inputs or []))]

    # DFS 契约图搜索(深度≤max_steps; 有向无环: 不回访链内节点)
    plans = []  # [(chain, edge_fmts)]
    def _dfs(chain: list, fmts: list):
        cur = chain[-1]
        if _goal_match(cur) and chain:
            plans.append((list(chain), list(fmts)))
            return
        if len(chain) >= max_steps:
            return
        # 后继: 契约兼容(outputs→inputs)或 relations.next_step
        nexts = []
        rel_next = (specs[cur].relations or {}).get("next_step", [])
        for cand in specs:
            if cand == cur or cand in chain:
                continue
            # 评审 #82 P0-1: MULTI_INPUT 可入选(slot resolver 绑定);无 inputs 契约才排除
            if _bindability(cand) == "MULTI_INPUT" and not (specs[cand].inputs or []):
                continue
            ef = _edge(cur, cand)
            if ef:
                nexts.append((cand, ef, 0))  # 契约边优先
            elif cand in rel_next:
                nexts.append((cand, (rel_next and "relation") or "", 1))
        # 分支排序: 契约边优先, 然后目标可达性(goal_match/2跳)优先——防 [:8] 截断关键路径
        nexts.sort(key=lambda x: (x[2],
                                  0 if _goal_match(x[0]) else 1,
                                  0 if any(_edge(x[0], c2) and _goal_match(c2) for c2 in specs if c2 != x[0]) else 1))
        for cand, ef, _prio in nexts[:8]:  # 分支上限防爆炸
            _dfs(chain + [cand], fmts + [ef])

    # 起点排序(评审 #70): ① 直接 goal 匹配 ② 2 跳可达 goal(如 muscle→trimal→iqtree)
    def _reach_goal_2hop(name: str) -> bool:
        for cand in specs:
            if cand != name and _edge(name, cand) and (_goal_match(cand) or
                    any(_edge(cand, c2) and _goal_match(c2) for c2 in specs)):
                return True
        return False
    starts.sort(key=lambda n: (0 if _goal_match(n) else 1, 0 if _reach_goal_2hop(n) else 1))
    # 评审 #109(Planner 决策质量): 起点截断不再丢关键工具——
    # goal 直接命中的起点必须全保留(recipBlast 等 MULTI_INPUT 工具曾因排序靠后掉出 [:16] 永不被探索),
    # 其余按序补足到上限(防爆炸仍保留)
    _goal_starts = [n for n in starts if _goal_match(n)]
    _rest = [n for n in starts if not _goal_match(n)]
    for st in (_goal_starts + _rest)[:24]:
        _dfs([st], [])
    if not plans:
        direct = [n for n in specs if _goal_match(n)]
        if direct:
            plans = [([direct[0]], [])]
    # 置信度: reasons-based(评审 #70 P0-4——不再按链长)
    def _score(chain, fmts):
        if not chain:
            return 0.0, []
        reasons, score = [], 0.0
        if input_format and _accepts(specs[chain[0]], input_format):
            reasons.append("input_format_exact"); score += 0.3
        if output_format and output_format.lower() in _produces(specs[chain[-1]]):
            reasons.append("output_format_exact"); score += 0.3
        if _goal_match(chain[-1]):
            reasons.append("capability_match"); score += 0.2
        # 目标词命中终点工具名(评审 #70: 语义优先——volcano>barplot, iqtree>degramdom)
        _final = chain[-1].lower()
        if any((k[:7] if len(k) > 7 else k) in _final for k in goal_l.split() if len(k) > 2):
            reasons.append("name_match"); score += 0.15
        # 工具全名直接出现在目标文本(最强语义信号: goal 含 "volcano" → volcano 工具)
        if chain[-1].lower() in goal_l:
            reasons.append("exact_name_in_goal"); score += 0.2
        # 评审 #109(Planner 决策质量): capability 短语完全命中——
        # goal "reciprocal best hit" 与 capability "reciprocal_best_hit" 归一化后相等 → 强信号。
        # 解决 recipBlast(能力精确描述 goal) 单步 0.8 被泛泛链(0.9)压制的评分失真。
        # 仅 2+ 词短语匹配(单词 'visualization' 会命中所有可视化工具=噪音)
        _goal_ngrams = set()
        _gwords = [w for w in goal_l.split() if len(w) > 2]
        for _gi in range(len(_gwords)):
            for _gj in range(_gi + 2, len(_gwords) + 1):
                _goal_ngrams.add("_".join(_gwords[_gi:_gj]))
        for _cap in (specs[chain[-1]].capabilities or []):
            if _cap in _goal_ngrams:
                reasons.append("capability_phrase_match"); score += 0.25
                break
        # 评审 #109(Planner 决策质量): 链起点与 goal 无关 → 扣分——
        # recipBlast→mcscanx 曾靠"起点 input_exact + 终点弱命中 + 契约边"在 domain scan 场景
        # 赢过 hmmsearch(2 词命中); 起点无 goal 命中 = 该链不是为这个 goal 服务的
        if chain and not _goal_match(chain[0]):
            score -= 0.2
            reasons.append("irrelevant_start")
        # capability 短语对 start 链工具同样有效(recipBlast 在链中段时)
        for _mid_ in chain:
            for _cap in (specs[_mid_].capabilities or []):
                if _cap in _goal_ngrams and _mid_ != chain[-1]:
                    score += 0.10
                    break
        contract_edges = sum(1 for f in fmts if f and f != "relation")
        if contract_edges == len(chain) - 1 and len(chain) > 1:
            reasons.append("all_contract_edges"); score += 0.2
        # 深管线加分(每契约边 +0.05;评审 #70: muscle→trimal→iqtree 应胜过 preparespecies→iqtree)
        score += 0.05 * contract_edges
        # 模糊边小罚(子串匹配不如精确匹配可信)
        fuzzy = sum(1 for f in fmts if f and f != "relation" and f not in
                    [i.format.lower() for i in (specs[chain[fmts.index(f) + 1]].inputs or [])])
        score -= 0.05 * fuzzy
        # content_type 冲突边罚(评审 semantic type: protein 链误入 dna 工具→降级)
        for i in range(len(chain) - 1):
            if _content_compat(chain[i], chain[i + 1]) is False:
                score -= 0.3
                reasons.append("content_type_conflict")
                break
        # 多必填输入降级(评审 #70 P0-2 → #109 修正): 仅当 slot resolver 无法绑定才罚。
        # 绑定性探测用**多格式虚拟输入**(gff3+txt+fasta+tsv…)——单输入探测会让第二必填槽
        # (如 genestructure 的 ids/txt)永远解析失败, 误伤真工具(genestructure 曾因此输给 memeViz)
        _probe_inputs = {f"_src_{i}": f"input.{f}" for i, f in
                         enumerate([input_format, "txt", "fasta", "tsv", "gff3", "nwk", "aln"] if input_format
                                   else ["txt", "fasta", "tsv", "gff3"])}
        for t in chain:
            _req = [i for i in (specs[t].inputs or []) if i.required]
            if len(_req) > 1:
                if _bind_slots_local(t, "{input}", _probe_inputs) is None:
                    score -= 0.4
                    reasons.append("multi_input_unbindable")
                    break
        # 评审 #109(Planner 决策质量): 空壳 manual(0 inputs 无签名)不可执行 → 降权——
        # structure/smart 等空壳曾靠 name/capability 词根赢过真工具(genestructure 2 inputs)
        for t in chain:
            _sp_t = specs[t]
            if _sp_t.kind == "manual" and not (_sp_t.inputs or []) and not _sp_t.class_name:
                score -= 0.25
                reasons.append("shell_manual")
                break
        # 透传跳惩罚(评审 #70 → #109 加强): 输入格式≈输出格式 且不相关 goal = 无增值前缀/中间步。
        # 覆盖链首(pep2codon 作 fasta→fasta 起点曾无限增值却抢规划)——
        # exact 透传(fasta→fasta)重罚, 兼容透传(alignment→trimmed_alignment 修剪)轻罚;
        # goal 匹配的步骤豁免(muscle 在 phylogeny 目标是增值)
        for _mi, mid in enumerate(chain[:-1] if len(chain) > 1 else []):
            _ins = [i.format.lower() for i in (specs[mid].inputs or [])] + \
                    [a.lower() for a in ((specs[mid].relations or {}).get("accepts") or [])]
            _outs = _produces(specs[mid])
            if _goal_match(mid):
                continue
            _worst = 0.0
            for _i in _ins:
                for _o in _outs:
                    _lv = _fmt_level(_i, _o)
                    if _lv == "exact":
                        _worst = max(_worst, 0.3)
                    elif _lv == "compatible":
                        _worst = max(_worst, 0.10)
            if _worst:
                score -= _worst
                reasons.append("passthrough_prefix" if _mi == 0 else "passthrough_middle")
                break
        return round(score, 2), reasons  # 内部不截断, 输出时 cap
    best = max(plans, key=lambda p: _score(*p)[0]) if plans else ([], [])
    # 精确名单步优先(评审 #70): 目标点名工具且单步高分 → 不塞无关前缀(peakanno→volcano)
    _exact_singles = [p for p in plans if len(p[0]) == 1 and p[0][0].lower() in goal_l
                      and _score(*p)[0] >= 0.8]
    if _exact_singles:
        best = max(_exact_singles, key=lambda p: _score(*p)[0])
    best_score, best_reasons = _score(*best) if best[0] else (0.0, [])
    chain_tools = best[0]
    _fmts_padded = [None] + list(best[1])  # fmts 是边(比 chain 少 1),首步补 None 防 zip 截断
    wf_spec = _plan_to_spec(goal, [(t, f"contract graph({fm})" if fm else "start") for t, fm in zip(chain_tools, _fmts_padded)],
                            input_format, output_format) if chain_tools else None
    return {
        "schema_version": WORKFLOW_SCHEMA_CURRENT,  # P0-2(评审 #86): 统一不再硬编码
        "goal": goal,
        "input_format": input_format or None,
        "output_format": output_format or None,
        "plan": [{"step": i + 1, "tool": t, "reason": r} for i, (t, r) in
                 enumerate([(t, f"contract graph({fm})" if fm else "start")
                            for t, fm in zip(chain_tools, _fmts_padded)])],
        "workflow": wf_spec,  # 可执行 WorkflowSpec(评审 #64 P0-2: plan → 对象)
        "confidence": min(best_score, 0.99),  # reasons-based 数值(向后兼容)
        "confidence_reasons": best_reasons,
        # planning_score(评审 #72 P1-3): level/score/evidence 结构
        "planning_score": {
            "score": min(best_score, 0.99),
            "level": ("high" if best_score >= 0.8 else
                      "medium" if best_score >= 0.5 else "low"),
            "evidence": best_reasons,
        },
        "alternatives": len(plans) - 1,
        "rejected": [
            {"tool": n, "status": "UNEXECUTABLE",
             "reason": f"需要 {len([i for i in (specs[n].inputs or []) if i.required])} 个必填输入, planner 单输入绑定无法供给"}
            for n in specs
            if _accepts(specs[n], input_format) and _bindability(n) == "UNEXECUTABLE"
        ][:5],
    }





