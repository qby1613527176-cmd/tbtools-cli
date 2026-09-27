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


def _warn_legacy_args(wf: dict):
    """legacy args 退役警告(评审 #76 P1-3): v1.x 兼容,v2.0 移除——迁移 binding。"""
    legacy = [s.get("id", "?") for s in (wf.get("steps") or []) if not s.get("binding")]
    if legacy:
        print(f"⚠️ DeprecationWarning: workflow {wf.get('id', '?')} 的 {len(legacy)} 个步骤({', '.join(legacy[:3])})"
              f"使用 legacy args 形态——v2.0 将移除,请迁移 binding 形态({{inputs/parameters/output}})",
              file=sys.stderr)


WORKFLOW_SCHEMA_CURRENT = "1.1"   # workflow schema: 1.0=args / 1.1=binding / 2.0=binding-only
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


def _resolve(value, outputs: dict):
    """引用解析: $step.output / {artifact: path}(Artifact 引用) / {input.X}。"""
    # P1-8/#62 P0-6: Artifact 引用({artifact: <path 或 art_id>};id 经索引解析——去路径化)
    if isinstance(value, dict) and "artifact" in value:
        from tbtools_cli.artifact import resolve as _aresolve
        ap = _aresolve(value["artifact"])
        if not ap:
            raise WorkflowError(f"Artifact 不存在(路径或 id 均无法解析): {value['artifact']}")
        return ap
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
        # binding 形态(契约): compile_step 统一编译(评审 #72 P0-3: run/validate 同一 compiler)
        if s.get("binding"):
            s = dict(s)
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
            _ci = compile_step_full(s, workdir, outputs)
            args = _ci.argv
            # 输出登记编译结构(评审 #88 P0-1): binding.outputs 精确,不再 out_args[-1] 猜
            steps.append({"id": s["id"], "tool": s["tool"], "args": args,
                          "_compiled_outputs": _ci.outputs})
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
    """原子写(评审 #70 P1-3): tmp+fsync+os.replace——中断不留半截 JSON。"""
    p = os.path.join(workdir, ".wf_state.json")
    tmp = p + f".tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)




class CompiledInvocation:
    """编译产物(评审 #88 P0-1): 上游已知的语义下游不再重猜。

    argv + 明确的 inputs/outputs/parameters/tool——Runtime/Artifact/Provenance/Resume
    全部消费 outputs 字段,不再用扩展名/args[-1] 从 argv 反推。"""

    def __init__(self, argv: list, inputs: list, outputs: list, parameters: dict, tool: str):
        self.argv = argv
        self.inputs = inputs
        self.outputs = outputs
        self.parameters = parameters
        self.tool = tool
        self.schema_version = WORKFLOW_SCHEMA_CURRENT  # 评审 #94 P1-3
        # contract fingerprint(评审 #94 P1-3): 编译产物哈希——resume/provenance 可验证同一性
        import hashlib as _hc
        import json as _jc
        self.contract_fingerprint = _hc.sha256(
            _jc.dumps({"argv": argv, "inputs": inputs, "outputs": outputs,
                       "parameters": parameters, "tool": tool},
                      sort_keys=True, default=str).encode()).hexdigest()[:16]


def compile_step_full(step: dict, workdir: str, outputs: dict) -> CompiledInvocation:
    """compile_step 的结构版(评审 #88): 返回 CompiledInvocation(argv+inputs+outputs)。"""
    from tbtools_cli.command_spec import build_command_specs
    binding = step.get("binding")
    bare = str(step.get("tool", "")).split()[-1]
    if binding:
        sp = build_command_specs().get(bare)
        if not sp:
            raise WorkflowError(f"WORKFLOW_INVALID_TOOL: {step.get('tool')}")
        _bi = binding.get("inputs", [])
        if isinstance(_bi, dict):
            inputs = []
            for slot in sp.inputs:
                if slot.name in _bi:
                    inputs.append(_resolve(_bi[slot.name], outputs))
                elif slot.required:
                    raise WorkflowError(
                        f"WORKFLOW_MISSING_INPUT: step {step.get('id')} 缺必填输入槽位 {slot.name}")
        else:
            inputs = [_resolve(v, outputs) for v in _bi]
        params = {k: _resolve(v, outputs) if isinstance(v, str) else v
                  for k, v in binding.get("parameters", {}).items()}
        out_raw = binding.get("output", "")
        outs = [_resolve(out_raw, outputs)] if out_raw else []
        try:
            argv = sp.invocation.build_argv(inputs=inputs, parameters=params,
                                            output=outs[0] if outs else "")
        except ValueError as e:
            raise WorkflowError(f"WORKFLOW_COMPILE_ERROR: step {step.get('id')} 编译失败: {e}") from e
        return CompiledInvocation(argv=argv, inputs=inputs, outputs=outs,
                                  parameters=params, tool=bare)
    argv = [_resolve(a, outputs) if isinstance(a, str) else a for a in step.get("args", [])]
    return CompiledInvocation(argv=argv, inputs=[], outputs=[], parameters={}, tool=bare)


def compile_step(step: dict, workdir: str, outputs: dict) -> list:
    """步骤 → 精确 argv(评审 #72 P0-2/P0-3: validate 与 run 同一 compiler)。

    两形态:
    ① binding 形态(契约): step.binding = {inputs: [...], parameters: {...}, output: "..."}
       → spec.invocation.build_argv(契约编译, 类型/未知/必填全检查)
    ② args 形态(legacy): step.args = [...] → 占位符解析({workdir}/{input.X}/$s.output/{artifact})
    """
    from tbtools_cli.command_spec import build_command_specs
    binding = step.get("binding")
    if binding:
        bare = str(step.get("tool", "")).split()[-1]
        sp = build_command_specs().get(bare)
        if not sp:
            raise WorkflowError(f"WORKFLOW_INVALID_TOOL: {step.get('tool')}")
        _bi = binding.get("inputs", [])
        if isinstance(_bi, dict):
            # slot 级绑定(评审 #80 P0-3): {slot_name: ref} → 按 InputSpec 声明序展开
            inputs = []
            for slot in sp.inputs:
                if slot.name in _bi:
                    inputs.append(_resolve(_bi[slot.name], outputs))
                elif slot.required:
                    raise WorkflowError(
                        f"WORKFLOW_MISSING_INPUT: step {step.get('id')} 缺必填输入槽位 {slot.name}")
        else:
            inputs = [_resolve(v, outputs) for v in _bi]
        params = {k: _resolve(v, outputs) if isinstance(v, str) else v
                  for k, v in binding.get("parameters", {}).items()}
        output = _resolve(binding.get("output", ""), outputs) if binding.get("output") else ""
        try:
            return sp.invocation.build_argv(inputs=inputs, parameters=params, output=output)
        except ValueError as e:
            raise WorkflowError(f"WORKFLOW_COMPILE_ERROR: step {step.get('id')} 编译失败: {e}") from e
    # legacy args 形态
    return [_resolve(a, outputs) if isinstance(a, str) else a for a in step.get("args", [])]

def _topo_sort(steps: list) -> list:
    """拓扑排序(depends_on 声明的步骤按依赖排序;环检测)。"""
    by_id = {s["id"]: s for s in steps}
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



def _merge_state_step(workdir: str, workflow_id: str, result: dict) -> str | None:
    """单步完成即合并落盘(P0-2 评审 #80): 崩溃后 resume 能看到已完成步骤。

    P1-4(评审 #86): 落盘失败返回警告文案(不再静默吞——resume 可信度问题必须可见)。"""
    try:
        state = _load_state(workdir)
        steps = state.get("steps", [])
        steps = [s for s in steps if s.get("id") != result["id"]]
        steps.append(result)
        _save_state(workdir, {"workflow": workflow_id, "status": "running", "steps": steps})
        return None
    except Exception as e:
        _warn = f"PERSISTENCE_WARNING: step {result.get('id')} state 落盘失败: {e}"
        print(f"⚠️ {_warn}", file=sys.stderr)
        return _warn

def _execute_step(st: dict, workdir: str, timeout_s: int, state: dict, resume: bool,
                  cancel_event=None, proc_registry: dict | None = None) -> dict:
    """执行单步(DAG 并行可重入;评审: DAG scheduler)。

    GLM-4.7 P0: cancel_event 取消传播(入口检查) + Popen 进程组注册(可 killpg) +
    超时杀进程树 + 异常结构化(不吞 worker 异常)。
    """
    # resume: 已成功步骤跳过——但必须 Artifact 验证(产物存在+sha256)
    if resume and state.get("steps"):
        prev = next((x for x in state["steps"] if x["id"] == st["id"]), None)
        if prev and prev.get("status") == "succeeded":
            _out_p = prev.get("output")
            _valid = bool(_out_p and os.path.isfile(_out_p))
            if _valid:
                try:
                    _pr = json.load(open(_out_p + ".tbtools.json", encoding="utf-8"))
                    if _pr.get("exit_code") != 0:
                        _valid = False
                except Exception:
                    _valid = False
            if _valid and prev.get("output_sha256"):
                try:
                    import hashlib as _hl
                    _h = _hl.sha256()
                    with open(_out_p, "rb") as _fh:
                        for _c in iter(lambda: _fh.read(1 << 20), b""):
                            _h.update(_c)
                    if _h.hexdigest() != prev["output_sha256"]:
                        _valid = False
                except Exception:
                    _valid = False
            if _valid:
                return prev
            print(f"⚠️ resume: {st['id']} 状态成功但产物失效, 重新执行", file=sys.stderr)
    # 取消传播(GLM-4.7 P0-1): 入口检查——fail-fast 后新步骤不再启动
    if cancel_event is not None and cancel_event.is_set():
        return {"id": st["id"], "tool": st["tool"], "exit_code": None,
                "status": "cancelled", "output": None, "artifact_id": None,
                "output_sha256": None, "provenance": None, "log": None}
    tool_parts = st["tool"].split()
    log_path = os.path.join(workdir, f"{st['id']}.log")
    # Popen + 进程组注册(GLM-4.7 P0-1/P0-2): 可被 killpg;超时杀进程树(不再 worker 悬挂)
    _rc = None
    _timeout_hit = False
    try:
        with open(log_path, "w", encoding="utf-8") as lf:
            _p = subprocess.Popen(
                [sys.executable, "-m", "tbtools_cli.cli"] + tool_parts + st["args"],
                stdout=lf, stderr=subprocess.STDOUT,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                start_new_session=True,  # 进程组独立, killpg 可达
            )
            if proc_registry is not None:
                proc_registry[st["id"]] = _p
            # P0-3(评审 #86): cancel↔register 竞态——注册完成后立查 cancel_event
            # (若 cancel 在 wait 前已 set 且 killpg 先于注册执行,此步骤会漏杀→悬挂)
            if cancel_event is not None and cancel_event.is_set():
                try:
                    import signal as _sig2
                    os.killpg(os.getpgid(_p.pid), _sig2.SIGKILL)
                except Exception:
                    pass
                _p.wait(timeout=10)
                if proc_registry is not None:
                    proc_registry.pop(st["id"], None)
                return {"id": st["id"], "tool": st["tool"], "exit_code": -1,
                        "status": "cancelled", "output": None, "log": log_path}
            try:
                _rc = _p.wait(timeout=timeout_s)
            except subprocess.TimeoutExpired:
                _timeout_hit = True
                try:
                    import signal as _sig
                    os.killpg(os.getpgid(_p.pid), _sig.SIGKILL)
                except Exception:
                    _p.kill()
                _p.wait()
            finally:
                if proc_registry is not None:
                    proc_registry.pop(st["id"], None)
    except Exception as e:
        # worker 异常结构化(GLM-4.7 P0-3): 不抛出——转为 failed 步骤(带诊断)
        return {"id": st["id"], "tool": st["tool"], "exit_code": None,
                "status": "failed", "validation_warning": f"worker exception: {e}",
                "output": None, "artifact_id": None, "output_sha256": None,
                "provenance": None, "log": log_path}
    step_ok = (_rc == 0) and not _timeout_hit
    # 输出消费编译结构(评审 #88 P0-1): _compiled_outputs 优先——Runtime 不再从 argv 猜
    out = ""
    if st.get("_compiled_outputs"):
        out = st["_compiled_outputs"][0]
    if not out:
        try:
            from tbtools_cli.command_spec import build_command_specs as _bcs2
            _osp = _bcs2().get(str(st["tool"]).split()[-1])
            _outs_fmt = [str(o).lower() for o in (_osp.outputs if _osp else [])]
            if _outs_fmt:
                _exts = tuple("." + f for f in _outs_fmt if 1 <= len(f) <= 5)
                _cands = [a for a in st["args"] if isinstance(a, str) and a.lower().endswith(_exts)]
                if _cands:
                    out = _cands[-1]
        except Exception:
            pass
    if not out:
        out = st["args"][-1] if st["args"] else ""
    # Artifact ID 登记
    _art_id = None
    _out_sha = None
    _reg_warn = None
    if step_ok and out and os.path.isfile(out):
        try:
            from tbtools_cli.artifact import build as _ab, register as _areg
            _a = _ab(out, producer=st["tool"])
            _reg_err = _areg(_a)
            if _reg_err:
                _reg_warn = f"artifact register warning: {_reg_err}"
                print(f"⚠️ {_reg_warn}", file=sys.stderr)  # 评审 #88 P1-4
            _art_id = _a.id
            _out_sha = _a.sha256
        except Exception as _re:
            _reg_warn = f"artifact register exception: {_re}"
            print(f"⚠️ {_reg_warn}", file=sys.stderr)
    # 产物语义验证
    _vwarn = None
    if step_ok and out and os.path.isfile(out):
        _vok, _vmsg = validate_artifact(out)
        if not _vok:
            _vwarn = f"output validation failed: {_vmsg}"
            step_ok = False
    return {"id": st["id"], "tool": st["tool"], "exit_code": _rc,
            "status": "succeeded" if step_ok else "failed",
            **({"validation_warning": f"step timeout after {timeout_s}s (process tree killed)"} if _timeout_hit else {}),
            **({"validation_warning": _vwarn} if _vwarn else {}),
            **({"register_warning": _reg_warn} if _reg_warn else {}),
            "output": out if step_ok and os.path.isfile(out) else None,
            "artifact_id": _art_id,
            "output_sha256": _out_sha,
            "provenance": out + ".tbtools.json" if step_ok and os.path.isfile(out + ".tbtools.json") else None,
            "log": log_path}


def _run_parallel(steps: list, workdir: str, timeout_s: int, state: dict, resume: bool,
                  max_workers: int = 2, workflow_id: str = "") -> tuple[list, str | None]:
    """DAG 并行调度(评审: ready-queue;depends_on 工作流;fail-fast 早取消)。

    返回 (results 按完成序, failed_step_id 或 None)。线程安全: outputs 在 plan 期已解析,
    results 收集加锁;resume 状态只读。
    """
    import threading
    from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
    by_id = {s["id"]: s for s in steps}
    pending = set(by_id)
    done: dict = {}
    results, failed = [], None
    lock = threading.Lock()
    # P0-1(评审 #80): cancel_event + 进程组注册真正打通——失败后 kill 在飞步骤,状态收敛
    cancel_event = threading.Event()
    proc_registry: dict = {}

    def _ready():
        # P2(评审 #94): deterministic ready queue——按声明序排序(输出稳定可复现)
        _decl = {s["id"]: i for i, s in enumerate(steps)}
        return sorted(
            (sid for sid in pending
             if all(d in done for d in (by_id[sid].get("depends_on") or by_id[sid].get("dependsOn") or []))),
            key=lambda x: _decl.get(x, 999))

    def _kill_running():
        """失败触发: cancel_event + killpg 所有在飞进程组(P0-1 状态收敛)。"""
        cancel_event.set()
        import signal as _sig
        for sid2, proc in list(proc_registry.items()):
            try:
                if proc.poll() is None:
                    os.killpg(os.getpgid(proc.pid), _sig.SIGTERM)
            except Exception:
                pass

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        running: dict = {}
        # 条件含 running(竞态修复): pending 空但仍有在飞步骤时不能退出——否则结果丢失
        while (pending or running) and failed is None:
            for sid in _ready():
                running[pool.submit(_execute_step, by_id[sid], workdir, timeout_s, state, resume,
                                    cancel_event, proc_registry)] = sid
                pending.discard(sid)
            if not running:
                break
            finished, _ = wait(running, return_when=FIRST_COMPLETED)
            for fut in finished:
                sid = running.pop(fut)
                proc_registry.pop(sid, None)
                res = fut.result()
                with lock:
                    done[sid] = res
                    results.append(res)
                    _pw2 = _merge_state_step(workdir, workflow_id or "wf", res)
                    if _pw2:
                        res.setdefault("persistence_warnings", []).append(_pw2)  # P0-4(评审 #92)
                if res["status"] != "succeeded":
                    failed = sid
                    _kill_running()
                    # 收敛: 等在飞步骤全部结束(不返回半死状态)
                    for fut2 in list(running):
                        sid2 = running.pop(fut2)
                        try:
                            res2 = fut2.result(timeout=30)
                        except Exception:
                            res2 = {"id": sid2, "tool": by_id[sid2]["tool"], "exit_code": -1,
                                    "status": "cancelled", "output": None, "log": ""}
                        with lock:
                            results.append(res2)
                    # 未启动步骤标记 skipped(状态收敛)
                    for sid3 in sorted(pending):
                        with lock:
                            results.append({"id": sid3, "tool": by_id[sid3]["tool"],
                                            "exit_code": -1, "status": "skipped",
                                            "output": None, "log": ""})
                    pending.clear()
                    break
    return results, failed


def run(wf: dict, workdir: str, timeout_s: int = 600, resume: bool = False) -> dict:
    """执行 workflow(depends_on 拓扑排序;失败即停, 返回结构化结果)。

    resume=True 时跳过已成功步骤(读 .wf_state.json;v2 断点续跑)。
    """
    os.makedirs(workdir, exist_ok=True)
    # DAG: 有 depends_on 的步骤拓扑重排(评审 #66 P0-3)
    if any(s.get("depends_on") or s.get("dependsOn") for s in wf["steps"]):
        wf = dict(wf)
        wf["steps"] = _topo_sort(wf["steps"])
    state = _load_state(workdir) if resume else {}
    # Resume identity 校验(评审 #84 P0-2): state 的 workflow 标识必须匹配当前 wf——
    # 不同 workflow 同 workdir 时错误跳过(崩溃恢复边界)
    if resume and state.get("steps"):
        _state_wf = state.get("workflow") or state.get("id") or ""
        if _state_wf and _state_wf != wf["id"]:
            print(f"⚠️ resume: state 属于 {_state_wf},当前 {wf['id']}——忽略旧状态全量执行", file=sys.stderr)
            state = {}
        else:
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
    t0 = time.time()
    _persistence_warnings: list = []
    # DAG 并行调度(depends_on 工作流且 TBTOOLS_WF_PARALLEL!=0;默认 2 workers——Java 内存约束)
    _has_dag = any(s.get("depends_on") or s.get("dependsOn") for s in wf["steps"])
    _parallel = _has_dag and len(steps) > 1 and os.environ.get("TBTOOLS_WF_PARALLEL", "1") != "0"
    if _parallel:
        results, failed_at = _run_parallel(steps, workdir, timeout_s, state, resume,
                                           max_workers=int(os.environ.get("TBTOOLS_WF_WORKERS", "2")),
                                           workflow_id=wf["id"])
        # 评审 #94 P1-2: 并行步骤级 persistence_warnings 汇总到顶层(与串行一致)
        for _r in results:
            for _pw3 in _r.get("persistence_warnings", []):
                if _pw3 not in _persistence_warnings:
                    _persistence_warnings.append(_pw3)
        # 结果按声明序重排(输出稳定)
        _order = {s["id"]: i for i, s in enumerate(steps)}
        results.sort(key=lambda r: _order.get(r["id"], 999))
    else:
        results = []
        failed_at = None
        for st in steps:
            res = _execute_step(st, workdir, timeout_s, state, resume)
            results.append(res)
            _pw = _merge_state_step(workdir, wf["id"], res)  # P0-2: 每步落盘
            if _pw:
                _persistence_warnings.append(_pw)
            if res["status"] != "succeeded":
                failed_at = st["id"]
                break
    if failed_at:
        _save_state(workdir, {"workflow": wf["id"], "status": "failed", "steps": results})
        return {"schema_version": WORKFLOW_SCHEMA_CURRENT, "workflow": wf["id"], "status": "failed",
                "failed_at": failed_at, "steps": results,
                "duration_s": round(time.time() - t0, 1)}
    _save_state(workdir, {"workflow": wf["id"], "status": "succeeded", "steps": results})
    return {"schema_version": WORKFLOW_SCHEMA_CURRENT, "workflow": wf["id"], "status": "succeeded",
            "steps": results, "duration_s": round(time.time() - t0, 1),
            **({"persistence_warnings": _persistence_warnings} if _persistence_warnings else {}),
            "artifacts": [r2["output"] for r2 in results if r2["output"]]}



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
                _ci = compile_step_full(s, _dry_wd, _dry_outputs)
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

# ── Workflow Planner(评审 #62 P0-5): 目标 → 自动规划 ──
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
        if not fmt:
            return False
        ins_fmts = [i.format.lower() for i in (tool_spec.inputs or [])]
        rel_acc = [a.lower() for a in ((tool_spec.relations or {}).get("accepts") or [])]
        return fmt.lower() in ins_fmts or fmt.lower() in rel_acc

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
    for st in starts[:16]:
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
        # 多必填输入降级(评审 #70 P0-2): planner 单输入绑定, >1 必填输入的工具当前不可执行
        for t in chain:
            _req = [i for i in (specs[t].inputs or []) if i.required]
            if len(_req) > 1:
                score -= 0.4
                reasons.append("multi_input_unsupported")
                break
        # 透传跳惩罚(评审 #70): 中间步 输入格式≈输出格式 且不相关 goal = 无增值(preparespecies→iqtree)
        for mid in chain[1:-1] if len(chain) > 1 else []:
            _ins = [i.format.lower() for i in (specs[mid].inputs or [])] +                    [a.lower() for a in ((specs[mid].relations or {}).get("accepts") or [])]
            _outs = _produces(specs[mid])
            if any(_fmt_match(i, o) for i in _ins for o in _outs) and not _goal_match(mid):
                score -= 0.15
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




def _stable_wf_id(goal: str) -> str:
    """稳定 workflow_id(评审 #66b P0-5): sha256 派生——Python hash() 每次进程随机化(PYTHONHASHSEED),
    跨 run/resume/日志引用全断;sha256 同 goal 同 ID。"""
    import hashlib
    return hashlib.sha256(goal.encode("utf-8")).hexdigest()[:10]



def resolve_input_binding(source: str, slot) -> tuple[str, str]:
    """Binding Resolver(评审 #94 P0-3): 候选输入 vs InputSpec 的匹配级别。

    返回 (ref, level): level = EXACT / COMPATIBLE / INCOMPATIBLE / UNRESOLVED。
    content_type 真正进入(fasta 可嗅探时内容冲突→INCOMPATIBLE)。"""
    ref = source
    fmt = str(source).rsplit(".", 1)[-1].lower() if isinstance(source, str) else ""
    if not slot.format or not fmt:
        return ref, "UNRESOLVED"

    def _content_ok() -> bool:
        if slot.content_type in ("dna", "protein") and os.path.isfile(str(source)):
            from tbtools_cli.runtime.validation import sniff_fasta_content
            sniffed = sniff_fasta_content(str(source))
            return sniffed == "unknown" or sniffed == slot.content_type
        return True

    if slot.format.lower() == fmt:
        return (ref, "EXACT") if _content_ok() else (ref, "INCOMPATIBLE")
    a, b = slot.format.lower(), fmt
    if a == b or (len(a) >= 3 and a in b) or (len(b) >= 3 and b in a):
        return (ref, "COMPATIBLE") if _content_ok() else (ref, "INCOMPATIBLE")
    return ref, "INCOMPATIBLE"


def _bind_slots(name: str, first_ref: str, wf_inputs: dict, specs: dict) -> dict | None:
    """slot 级绑定(评审 #80 P0-3 + #82 P0-2 + #86 P0-1 模块级): 首必填槽 ← 链引用;
    其余必填槽 ← workflow inputs。匹配级别: EXACT / COMPATIBLE / INCOMPATIBLE / UNRESOLVED。"""
    spec = specs.get(name)
    if not spec:
        return None
    ins = [i for i in (spec.inputs or []) if i.required]
    if not ins:
        return None
    binding = {ins[0].name: first_ref}
    if first_ref.startswith("$"):
        binding["__first_slot_match"] = "UPSTREAM_EDGE"
    elif first_ref == "{input}" or first_ref.startswith("{input."):
        binding["__first_slot_match"] = "WORKFLOW_INPUT"
    for slot in ins[1:]:
        hit, hit_level = None, "UNRESOLVED"
        for in_name, in_val in wf_inputs.items():
            # P0-3(评审 #94): Binding Resolver 统一(content_type 正式进入)
            _ref, _lvl = resolve_input_binding(str(in_val), slot)
            if _lvl == "EXACT":
                hit, hit_level = "{input." + in_name + "}", "EXACT"
                break
            if _lvl == "COMPATIBLE":
                hit, hit_level = "{input." + in_name + "}", "COMPATIBLE"
        if not hit:
            return None
        binding[slot.name] = hit
        binding[f"__{slot.name}_match"] = hit_level
    return binding

def _plan_to_spec(goal: str, chain: list, input_format: str, output_format: str) -> dict:
    """plan 链 → 可执行 WorkflowSpec(评审 #74 P0-1: 直接生成 binding, 不再 args 拼接)。

    binding 形态: {inputs, parameters, output}——workflow run 走 compile_step → InvocationSpec,
    同一 compiler 闭环(validate==compile success)。
    """
    from tbtools_cli.command_spec import build_command_specs as _bcs
    _specs = _bcs()
    steps = []
    for i, (tool, reason) in enumerate(chain):
        sid = f"step{i + 1}"
        _sp = _specs.get(tool)
        _ins = _sp.inputs if _sp else []
        _outs = _sp.outputs if _sp else []
        rel = (_sp.relations or {}) if _sp else {}
        # binding: 首步输入={input}, 后续=$prev.output;输出=workdir/工具名.契约格式扩展名
        _in_ref = "{input}" if i == 0 else f"$step{i}.output"
        _EXT_MAP = {"svg": ".svg", "png": ".png", "pdf": ".pdf", "tsv": ".tsv", "txt": ".txt",
                    "json": ".json", "nwk": ".nwk", "treefile": ".nwk", "newick": ".nwk",
                    "fa": ".fa", "aln": ".fa", "gff3": ".gff3", "collinearity": ".collinearity"}
        _ofmt = (_outs[0] if _outs else output_format or "out")
        _ext = _EXT_MAP.get(str(_ofmt).lower(), "." + str(_ofmt).lower())
        # 参数默认值填充(评审 #76 P0-2): binding 带 ParamSpec 默认,不再是空 parameters
        _defaults = {p.name: p.default for p in (_sp.parameters if _sp else [])
                     if p.default is not None}
        # MULTI_INPUT 接入(评审 #82 P0-1 + #86 P0-1): 多必填槽位经 _bind_slots 统一解析
        _req = [x for x in (_sp.inputs if _sp else []) if x.required]
        if len(_req) > 1:
            _slot_binding = _bind_slots(tool, _in_ref, {}, _specs) or {}
            # _bind_slots 无 wf_inputs 时额外槽位解析失败→生成 requires_inputs 占位
            _required_extra = []
            for _slot in _req[1:]:
                if _slot.name not in _slot_binding:
                    _slot_binding[_slot.name] = "{input." + _slot.name + "}"
                    _required_extra.append({"slot": _slot.name, "format": _slot.format,
                                            "content_type": _slot.content_type})
            _inputs_field: object = _slot_binding
        else:
            _required_extra = []
            _inputs_field = [_in_ref]
        steps.append({
            "id": sid,
            "tool": tool,
            "depends_on": [f"step{i}"] if i > 0 else [],
            "binding": {"inputs": _inputs_field, "parameters": _defaults,
                        "output": "{workdir}/%s%s" % (tool, _ext)},
            "input_contract": _ins[0].format if _ins else (rel.get("accepts") or [input_format])[0] if rel.get("accepts") else input_format,
            "output_contract": (_outs[0] if _outs else (rel.get("produces") or [output_format])[0] if rel.get("produces") else output_format),
            "selection_reason": reason,
            **({"required_workflow_inputs": _required_extra} if _required_extra else {}),
        })
    # Planner Template 正式化(评审 #88 P0-2): 不是 executable workflow——
    # 需用户提供 required_inputs 后才能执行(type + 汇总元数据,不再"看似可执行")
    _all_required = []
    for s in steps:
        for ri in s.get("required_workflow_inputs", []):
            _all_required.append({"step": s["id"], **ri})
    # P0-1(评审 #90): step1 首槽也是外部必填({input})——登记进 required_inputs
    if steps and chain:
        _sp0 = _specs.get(chain[0][0]) if chain else None
        if _sp0 and _sp0.inputs:
            _first_req = [i for i in _sp0.inputs if i.required]
            if _first_req:
                _all_required.insert(0, {"step": "step1", "slot": _first_req[0].name,
                                         "format": _first_req[0].format,
                                         "content_type": _first_req[0].content_type,
                                         "source": "workflow_main_input"})
    return {
        "schema_version": WORKFLOW_SCHEMA_CURRENT,
        "type": "workflow_template" if _all_required else "workflow",  # 评审 #88
        "required_inputs": _all_required,  # Agent 必须提供才能执行的输入清单
        "workflow_id": f"wf_{_stable_wf_id(goal + '|' + input_format + '|' + output_format + '|' + '>'.join([t for t, _ in chain]) + '|wf' + WORKFLOW_SCHEMA_CURRENT)}",
        "goal": goal,
        "steps": steps,
    }


def _default_args(tool: str, i: int, chain: list, input_format: str, output_format: str) -> list:
    """从 CommandSpec 生成步骤参数(评审 #66 P0-4: InputSpec/outputs 驱动, 不再猜位置参数)。

    输入: 首步={input}, 中间步=$prev.output(对齐 InputSpec.format)
    输出: CommandSpec outputs 首格式 → 对应扩展名(.svg/.tsv/.nwk...)
    """
    from tbtools_cli.command_spec import build_command_specs as _bcs
    args = []
    _sp = _bcs().get(tool)
    ins = (_sp.inputs, _sp.outputs) if _sp else None
    if i == 0:
        args.append("{input}")
    else:
        args.append("$step%d.output" % i)
    # 输出格式: CommandSpec outputs 首格式 → 扩展名
    _EXT_MAP = {"svg": ".svg", "png": ".png", "pdf": ".pdf", "tsv": ".tsv", "txt": ".txt",
                "json": ".json", "nwk": ".nwk", "treefile": ".nwk", "fa": ".fa", "aln": ".fa",
                "aln.fa": ".fa", "gff3": ".gff3", "xls": ".xls", "collinearity": ".collinearity",
                "meme": ".meme", "db": ".db", "out": ".out"}
    if ins and ins[1]:
        _ofmt = ins[1][0] if isinstance(ins[1], list) else str(ins[1])
        ext = _EXT_MAP.get(str(_ofmt).lower(), "." + str(_ofmt).lower())
    else:
        ext = "." + (output_format or "out") if output_format else ".out"
    args.append("{workdir}/%s%s" % (chain[i][0], ext))
    return args
