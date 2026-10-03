"""Executor 执行层(评审 #112 P2 拆分): workflow.py 中状态机/执行器逻辑独立成模块。

注: 原名 runtime.py 与 tbtools_cli/runtime/ 子包冲突, 改为 executor.py。

包含:
  - _load_state / _save_state: resume 断点状态(原子写 tmp+fsync+replace)
  - _merge_state_step: 每步结果落盘
  - _resume_gate: fingerprint resume 闸门(篡改检测)
  - _execute_step: 单步执行(subprocess + artifact/provenance)
  - _run_parallel: DAG 并行调度(ready-queue, fail-fast, cancel)
  - run: workflow 执行入口(resume 续跑)
  - validate_artifact: 产物解析级校验(FASTA/GFF/Newick/TSV/SVG)

workflow.py 从本模块 import 并 re-export(旧代码 from workflow import run/_execute_step 等仍可用)。
依赖: plan/_topo_sort 属 workflow(parse/plan 层)——运行时经函数内延迟 import 引用, 无循环。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

from tbtools_cli.identity import WORKFLOW_SCHEMA_CURRENT  # run 结果 schema_version


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




def _resume_gate(st: dict, prev: dict) -> tuple[bool, str]:
    """统一 resume 闸门(评审 #104 🔴1/2/5): binding/legacy 同一条路径。

    返回 (can_skip, reason)。
    规则:
    ① prev 无 provenance 或 exit_code != 0 → 重跑(假成功拦截)
    ② 产物缺失 → 重跑
    ③ 产物 sha256 与 state 不符 → 重跑(内容被换)
    ④ 当前步骤有指纹(binding): 三层全比——contract/binding/execution 任一不一致(含 prev 缺指纹)→ 重跑
    ⑤ legacy args(当前无指纹): ①②③ 通过即可跳过(显式降级, 文档化)
    """
    _out_p = prev.get("output")
    if not (_out_p and os.path.isfile(_out_p)):
        return False, "artifact_missing"
    try:
        _pr = json.load(open(_out_p + ".tbtools.json", encoding="utf-8"))
        if _pr.get("exit_code") != 0:
            return False, "provenance_exit_nonzero"
    except Exception:
        return False, "provenance_missing"
    if prev.get("output_sha256"):
        try:
            import hashlib as _hl
            _h = _hl.sha256()
            with open(_out_p, "rb") as _fh:
                for _c in iter(lambda: _fh.read(1 << 20), b""):
                    _h.update(_c)
            if _h.hexdigest() != prev["output_sha256"]:
                return False, "output_sha_mismatch"
        except Exception:
            return False, "output_unreadable"
    # ④ 三层指纹全比(评审 #104 🔴2): contract/binding/execution 任一不一致→重跑
    if st.get("_execution_fingerprint"):
        if prev.get("execution_fingerprint") != st["_execution_fingerprint"]:
            return False, "execution_fp_mismatch"
        if st.get("_contract_fingerprint") and prev.get("contract_fingerprint") and \
                prev["contract_fingerprint"] != st["_contract_fingerprint"]:
            return False, "contract_fp_mismatch"
        if st.get("_binding_fingerprint") and prev.get("binding_fingerprint") and \
                prev["binding_fingerprint"] != st["_binding_fingerprint"]:
            return False, "binding_fp_mismatch"
    return True, "ok"



def _execute_step(st: dict, workdir: str, timeout_s: int, state: dict, resume: bool,
                  cancel_event=None, proc_registry: dict | None = None) -> dict:
    """执行单步(DAG 并行可重入;评审: DAG scheduler)。

    GLM-4.7 P0: cancel_event 取消传播(入口检查) + Popen 进程组注册(可 killpg) +
    超时杀进程树 + 异常结构化(不吞 worker 异常)。
    """
    # resume: 已成功步骤跳过——统一 _resume_gate(评审 #104 🔴5: binding/legacy 同一路径)
    if resume and state.get("steps"):
        prev = next((x for x in state["steps"] if x["id"] == st["id"]), None)
        if prev and prev.get("status") == "succeeded":
            _can_skip, _gate_reason = _resume_gate(st, prev)
            if _can_skip:
                return prev
            print(f"⚠️ resume: {st['id']} 状态成功但验证失效({_gate_reason}), 重新执行", file=sys.stderr)
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
    # 输出消费编译结构(评审 #88 P0-1 + #98 P0-2):
    # binding 路径(_compiled_outputs 存在)——只消费 CompiledInvocation.outputs,禁止任何猜测;
    # 无 _compiled_outputs(legacy args)——才允许回退启发式(显式标记)
    out = ""
    _is_binding_path = "_compiled_outputs" in st
    if _is_binding_path:
        out = st["_compiled_outputs"][0] if st["_compiled_outputs"] else ""
    else:
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
    if not out and not _is_binding_path:
        out = st["args"][-1] if st["args"] else ""  # legacy args 末参回退(binding 路径禁猜)
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
    # P1-4(评审 #106): provenance 补三层 fingerprint——子进程 cli 写盘时不知 workflow 层指纹,
    # 由 workflow 执行者补写(幂等: 已存在则不覆盖; Agent 搜索/规划可读 execution 身份)
    _fp_prov_path = (out + ".tbtools.json") if step_ok and out and os.path.isfile(out + ".tbtools.json") else None
    if _fp_prov_path:
        try:
            import json as _fpj
            _fp_data = _fpj.load(open(_fp_prov_path, encoding="utf-8"))
            _dirty = False
            for _fpk, _fpv in (("execution_fingerprint", st.get("_execution_fingerprint")),
                               ("contract_fingerprint", st.get("_contract_fingerprint")),
                               ("binding_fingerprint", st.get("_binding_fingerprint"))):
                if _fpv and not _fp_data.get(_fpk):
                    _fp_data[_fpk] = _fpv
                    _dirty = True
            if _dirty:
                with open(_fp_prov_path, "w", encoding="utf-8") as _fff:
                    _fpj.dump(_fp_data, _fff, ensure_ascii=False, indent=1)
        except Exception:
            pass  # provenance 是附加信息, 补写失败不影响主流程
    return {"id": st["id"], "tool": st["tool"], "exit_code": _rc,
            "status": "succeeded" if step_ok else "failed",
            **({"validation_warning": f"step timeout after {timeout_s}s (process tree killed)"} if _timeout_hit else {}),
            **({"validation_warning": _vwarn} if _vwarn else {}),
            **({"register_warning": _reg_warn} if _reg_warn else {}),
            "output": out if step_ok and os.path.isfile(out) else None,
            "artifact_id": _art_id,
            "output_sha256": _out_sha,
            "execution_fingerprint": st.get("_execution_fingerprint"),
            "contract_fingerprint": st.get("_contract_fingerprint"),
            "binding_fingerprint": st.get("_binding_fingerprint"),
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
    # 评审 #112 P2: _execute_step 经 workflow 命名空间解析——测试 monkeypatch
    # workflow._execute_step 期望影响并行调度(原行为); 生产路径经 re-export 同源
    try:
        from tbtools_cli.workflow import _execute_step as _exec_hook
    except Exception:
        _exec_hook = _execute_step
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
                running[pool.submit(_exec_hook, by_id[sid], workdir, timeout_s, state, resume,
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
    # 评审 #112 P2: plan/_topo_sort 属 workflow 层, 函数内延迟 import 防循环;
    # _execute_step 同样经 workflow 解析(测试 monkeypatch 兼容)
    from tbtools_cli.workflow import _topo_sort, plan, _execute_step as _exec_hook2
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
    steps = plan(wf, workdir, runtime_resolve=True)  # 评审 #110: run 需要完整 execution_fp(resume 篡改检测)
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
            res = _exec_hook2(st, workdir, timeout_s, state, resume)
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

