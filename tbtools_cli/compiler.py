"""Compiler 层(评审 #112 P2 拆分): workflow.py 中 binding/argv 编译逻辑独立成模块。

包含:
  - _resolve: 占位符/Artifact 引用解析({input.X}/$step.output/{artifact: id})
  - _stable_wf_id: 稳定 workflow_id(sha256 派生, 防 Python hash 随机化)
  - CompiledInvocation: 编译产物(三层 fingerprint: contract/binding/execution)
  - compile_step_full / compile_step: workflow step → 精确 argv
  - resolve_input_binding / _bind_slots: binding 契约接线
  - _plan_to_spec / _default_args: plan 链 → 可执行 WorkflowSpec

workflow.py 从本模块 import 并 re-export(旧代码 from workflow import compile_step_full 等仍可用)。
"""
from __future__ import annotations

import os
import subprocess  # noqa: F401  (CompiledInvocation 内 runtime 探测用)
import time  # noqa: F401

# Identity 层(评审 #108: 单向依赖)——fingerprint 函数与 schema 常量
from tbtools_cli.identity import (
    CONTRACT_SCHEMA_VERSION, WORKFLOW_SCHEMA_CURRENT, execution_contract_fingerprint,
    semantic_fingerprint,  # noqa: F401
)


class WorkflowError(Exception):
    """workflow 编译/执行错误(评审 #72 P0-2: 统一错误类型)。"""



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



def _stable_wf_id(goal: str) -> str:
    """稳定 workflow_id(评审 #66b P0-5): sha256 派生——Python hash() 每次进程随机化(PYTHONHASHSEED),
    跨 run/resume/日志引用全断;sha256 同 goal 同 ID。"""
    import hashlib
    return hashlib.sha256(goal.encode("utf-8")).hexdigest()[:10]




class CompiledInvocation:
    """编译产物(评审 #88 P0-1): 上游已知的语义下游不再重猜。

    argv + 明确的 inputs/outputs/parameters/tool——Runtime/Artifact/Provenance/Resume
    全部消费 outputs 字段,不再用扩展名/args[-1] 从 argv 反推。"""

    def __init__(self, argv: list, inputs: list, outputs: list, parameters: dict, tool: str,
                 symbolic_binding: dict | None = None, runtime_resolve: bool = True):
        self.argv = argv
        self.runtime_resolve = runtime_resolve  # 评审 #108 P1-2: False=static(validate/plan)
        self.inputs = inputs
        self.outputs = outputs
        self.parameters = parameters
        self.tool = tool
        # 评审 #108 P1-2: 不模糊 schema_version——分两个概念
        self.workflow_schema_version = WORKFLOW_SCHEMA_CURRENT  # workflow YAML 语法版本
        self.contract_schema_version = CONTRACT_SCHEMA_VERSION  # execution identity 契约版本
        # 三层 identity 数学语义(评审 #98 P1-1 重定义):
        #   contract_fp = 契约本身(tool + schema_version + spec 契约内容)——输入换了它不变
        #   binding_fp  = 符号绑定(slot refs/parameters,未解析路径)——解析结果换了它不变
        #   execution_fp = contract_fp + binding_fp + 已解析输入 artifact sha + runtime 版本
        import hashlib as _hc
        import json as _jc
        # P0-2(评审 #100 + #102 P1-1): contract_fp = execution_contract_fingerprint(执行契约层)
        try:
            from tbtools_cli.command_spec import build_command_specs as _bcs3
            _sp3 = _bcs3().get(tool)
            self.contract_fingerprint_full = (
                execution_contract_fingerprint(_sp3) if _sp3 else
                _hc.sha256(_jc.dumps({"tool": tool}, sort_keys=True).encode()).hexdigest())
        except Exception:
            self.contract_fingerprint_full = _hc.sha256(
                _jc.dumps({"tool": tool}, sort_keys=True).encode()).hexdigest()
        self.contract_fingerprint = self.contract_fingerprint_full[:16]  # 显示截断(评审 #102 P1-3)
        # symbolic binding(评审 #98 + #102 P0): binding_fp = SHA256(raw symbolic binding)
        # ——raw binding 本身已含 inputs/parameters/output 的符号 refs;
        # 不混入已解析的 parameters(resolved 路径污染修复:
        # genome={input.genome} 换路径不应改变 binding identity)
        # binding identity 归一化(评审 #104 性质⑤ + #107 P0②):
        #   具体文件路径(path) → 抽象为路径无关(路径非身份; 内容由 execution input_shas 承载)
        #   symbolic ref({input.x}/$input.x) → **保留 ref 身份**(接线结构属于 binding identity)
        #   slot 位置 → 保留(保序/保 key)
        # 即: 路径无关 ≠ 引用无关——{input.genome} 和 {input.transcriptome} 必须不同 fp。
        def _canon_ref(v: object) -> object:
            """评审 #107 P0②: 路径抽象, ref 保留。"""
            if isinstance(v, str):
                _s = v.strip()
                if (_s.startswith("{") and _s.endswith("}")) or _s.startswith("${"):
                    return {"ref": _s}
                if os.path.isfile(_s) or "/" in _s or "\\" in _s:
                    return {"path": True}
                return _s
            if isinstance(v, list):
                return [_canon_ref(x) for x in v]
            if isinstance(v, dict):
                return {k: _canon_ref(x) for k, x in v.items()}
            return v

        _norm: dict[str, object] = {}
        for _k, _v in (symbolic_binding or {}).items():
            if _k == "inputs":
                if isinstance(_v, list):
                    _entries = []
                    for _i, _x in enumerate(_v):
                        _r = _canon_ref(_x)
                        if isinstance(_r, dict):
                            _e: dict[str, object] = {"slot": _i}
                            _e.update(_r)
                        else:
                            _e = {"slot": _i, "value": _r}
                        _entries.append(_e)
                    _norm[_k] = _entries
                elif isinstance(_v, dict):
                    _norm[_k] = {sk: _canon_ref(x) for sk, x in _v.items()}
                else:
                    _norm[_k] = _v
            else:
                # 非 inputs 键(parameters/output): 保留字面值——
                # 评审 #107 P0②: 路径抽象只针对 inputs 接线槽位;
                # output/parameters 是字面契约内容, 不同值必须不同 binding_fp
                _norm[_k] = _v
        self.binding_fingerprint_full = _hc.sha256(
            _jc.dumps(_norm, sort_keys=True, default=str).encode()).hexdigest()
        self.binding_fingerprint = self.binding_fingerprint_full[:16]
        # execution_fp(评审 #98): + 已解析输入 artifact sha + runtime 版本
        # 评审 #108 P1-2: runtime_resolve=False(validate/plan)时跳过 fork 探测——
        # 静态编译不读输入内容/不 fork 外部工具版本(Agent 大规模规划不探测几十个 executable)
        _input_shas: list[str] = []
        _rt_ver = "unknown"
        _deps: dict = {}
        if self.runtime_resolve:
            for _ip in inputs:
                try:
                    import hashlib as _h2
                    _h = _h2.sha256()
                    with open(str(_ip), "rb") as _f:
                        for _c in iter(lambda: _f.read(1 << 20), b""):
                            _h.update(_c)
                    _input_shas.append(_h.hexdigest())  # P1-3(评审 #104): full 64 hex
                except OSError:
                    _input_shas.append("missing")
            try:
                from tbtools_cli import __version__ as _rt_ver
            except Exception:
                _rt_ver = "unknown"
        # 🟠 dependency identity(评审 #100 + #102 P1-2): contract-driven——
        # 按 spec.dependencies 声明解析(不硬编码 muscle/iqtree2;换版=不同执行)
        # 评审 #108 P1-2: runtime_resolve=False 时也不探测依赖(validate 不 fork)
        # 评审 #112 P2: 探测逻辑拆到 dependency.py(三级优先+缓存), workflow 只调用
        if self.runtime_resolve:
            try:
                from tbtools_cli.dependency import (resolve_dependencies,
                                                    _DEP_VERSION_CACHE as _dep_cache_inst)
                _dep_spec = _sp3 if '_sp3' in dir() and _sp3 else None
                if _dep_spec is not None:
                    _deps = resolve_dependencies(_dep_spec, _dep_cache_inst)
            except Exception:
                pass
        # P1-3(评审 #102): full SHA256(64 hex 内部;显示层才截断)
        self.execution_fingerprint = _hc.sha256(
            _jc.dumps({"contract": self.contract_fingerprint_full,
                       "binding": self.binding_fingerprint_full,
                       "input_shas": _input_shas, "runtime": _rt_ver,
                       "dependencies": _deps},
                      sort_keys=True).encode()).hexdigest()


def compile_step_full(step: dict, workdir: str, outputs: dict,
                      symbolic_override: dict | None = None,
                      runtime_resolve: bool = True) -> CompiledInvocation:
    """compile_step 的结构版(评审 #88): 返回 CompiledInvocation(argv+inputs+outputs)。

    runtime_resolve(评审 #108 P1-2): False = static compile(validate/plan 用)——
    只做契约编译 + contract/binding fp, 不 fork 外部工具探测依赖版本/不读输入内容 sha;
    True = 完整 runtime identity(execution_fp 含 input_shas + dep 版本 + runtime 版本)。
    """
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
        # P0-1(评审 #100): binding_fp 用 raw symbolic binding(替换前 refs)
        # + 评审 #107 P1③: 不再把内容 sha 混入 binding——
        #   binding_fp 只描述"怎么接"(wiring), 内容身份由 execution_fp 的 input_shas 承载。
        #   (旧实现 _content_addr 把路径换成截断 16 hex sha 进 binding, 已删除——
        #    截断身份 + 身份层耦合, 违反分层: binding=接线 / execution=接线+内容)
        _sym = symbolic_override or dict(binding)
        return CompiledInvocation(argv=argv, inputs=inputs, outputs=outs,
                                  parameters=params, tool=bare,
                                  symbolic_binding=_sym, runtime_resolve=runtime_resolve)
    argv = [_resolve(a, outputs) if isinstance(a, str) else a for a in step.get("args", [])]
    return CompiledInvocation(argv=argv, inputs=[], outputs=[], parameters={}, tool=bare,
                              runtime_resolve=runtime_resolve)


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


def resolve_input_binding(source: str, slot) -> tuple[str, str]:
    """Binding Resolver(评审 #94 P0-3): 候选输入 vs InputSpec 的匹配级别。

    返回 (ref, level): level = EXACT / COMPATIBLE / INCOMPATIBLE / UNRESOLVED。
    content_type 真正进入(fasta 可嗅探时内容冲突→INCOMPATIBLE)。"""
    ref = source
    fmt = str(source).rsplit(".", 1)[-1].lower() if isinstance(source, str) else ""
    if not slot.format or not fmt:
        return ref, "UNRESOLVED"

    def _content_ok() -> bool:
        # "sequence" 双兼容(评审 #98 P1-2): muscle 类 DNA+蛋白通用 aligner
        if slot.content_type == "sequence" and os.path.isfile(str(source)):
            from tbtools_cli.runtime.validation import sniff_fasta_content
            return sniff_fasta_content(str(source)) in ("dna", "protein", "unknown")
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
