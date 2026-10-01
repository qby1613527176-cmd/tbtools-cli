"""Identity 层(评审 #108 P1-4 拆分): canonical contract / semantic identity / fingerprint。

职责边界(从 workflow.py 拆出):
  canonical_contract()            = 所有规范化 metadata / source model(总 canonical)
  canonical_execution_contract()  = 真正影响执行的字段(唯一入口)
  canonical_semantic_identity()   = Agent 搜索/规划身份
  *_fingerprint()                 = SHA256 指纹(contract/semantic/binding)

为什么独立: 解决 command_spec ↔ workflow 双向依赖——
  command_spec.to_metadata_entry() 需要 semantic_fingerprint,
  workflow 需要 canonical/fingerprint; 拆出本模块后两者只向下依赖 identity。

⚠️ 唯一真源约定(评审 #108 P0):
  EXECUTION_CONTRACT_FIELDS 只此一套, 不含 outputs(outputs 是 output_slots 投影)。
  不再允许第二套同义常量(CANONICAL_EXECUTION_FIELDS 曾残留致混淆)。
"""
from __future__ import annotations

WORKFLOW_SCHEMA_CURRENT = "1.1"   # workflow schema: 1.0=args / 1.1=binding / 2.0=binding-only

# ⑥ 评审 #106: fingerprint 计算规则版本(改规则即换版本→旧指纹自动失效,resume 安全)
FP_SCHEME_VERSION = "fp1"
# contract schema 版本(评审 #107 P0①): 独立于 workflow schema——
# workflow YAML 语法升级 ≠ 工具契约变化; 契约结构变化才 bump 这个
CONTRACT_SCHEMA_VERSION = "1"
# 评审 #107 P1⑦: 已知依赖的精确版本命令(终态迁往 dependency_manifest 字段)
# muscle5 只认 -version(--version 挂起/报错); 其余缺省回退 heuristic 顺序
DEP_VERSION_ARGS: dict = {
    "muscle": ("-version",),
    "iqtree2": ("--version", "-version"),
    "mafft": ("--version",),
    "trimal": ("-version", "--version"),
}

# ⑤ 评审 #106: Execution Contract 字段——纯执行身份(不含 tool 名/语义)
EXECUTION_CONTRACT_FIELDS = ("inputs", "output_slots", "parameters",
                             "layout", "named_flags")
# 评审 #107 P1⑤: outputs 从 execution identity 删除——output_slots 是 output 唯一真相,
# outputs 是投影(projection); 契约没变而投影实现变了不应改 execution identity。
# canonical_contract() 仍含 outputs(metadata/投影层), 但 execution_contract_fingerprint 不再吃它。


def canonical_execution_contract(spec) -> dict:
    """执行契约(评审 #106 P0): 纯执行身份——inputs/output_slots/parameters/layout/named_flags。
    不含 name(capabilities/relations/name 属 semantic identity,搜索/规划层)。"""
    return {k: v for k, v in canonical_contract(spec).items()
            if k in EXECUTION_CONTRACT_FIELDS}


def canonical_semantic_identity(spec) -> dict:
    """语义身份(评审 #106): name + capabilities + relations + dependencies——
    搜索/规划/Agent metadata 层使用,不进执行身份。"""
    c = canonical_contract(spec)
    return {"name": c.get("name"), "capabilities": c.get("capabilities"),
            "relations": c.get("relations"), "dependencies": c.get("dependencies")}


def canonical_contract(spec) -> dict:
    """唯一契约指纹源(评审 #100 P0-2): CommandSpec → 规范化契约 dict。

    contract_fingerprint 必须= SHA256(canonical_contract JSON)——
    含 inputs(全字段)/outputs/output_slots/parameters/layout/named_flags/capabilities/relations。
    任何一处契约变化(含 output_slots)都会改变 fingerprint。"""
    return {
        "name": spec.name, "kind": spec.kind, "group": spec.group,
        "inputs": [{"name": i.name, "format": i.format, "role": i.role,
                    "required": i.required, "content_type": i.content_type,
                    "columns": i.columns} for i in (spec.inputs or [])],
        "outputs": list(spec.outputs or []),
        "output_slots": [{"name": o.name, "format": o.format, "content_type": o.content_type}
                         for o in (spec.output_slots or [])],
        "parameters": [{"name": p.name, "type": p.type, "default": p.default,
                        "required": p.required, "cli_name": p.cli_name}
                       for p in (spec.parameters or [])],
        "layout": spec.invocation.layout,
        "named_flags": spec.invocation.named_flags,
        "capabilities": list(spec.capabilities or []),
        "dependencies": list(spec.dependencies or []),
        # P0-2(评审 #104): relations 进入 semantic canonical——semantic_fp 必须含它
        "relations": dict(spec.relations or {}),
    }


# 四层 identity 字段形式化(评审 #102 P1-4):
#   Execution Contract(执行身份): inputs/output_slots/parameters/layout/named_flags
#   Semantic Metadata(语义元数据): capabilities/relations/ontology——搜索/规划用,非执行身份
#   Runtime Identity(运行环境): tool/schema_version/runtime/deps
# ⚠️ 唯一真源: EXECUTION_CONTRACT_FIELDS 只此一套(评审 #108 P0)——已删旧重复常量
CANONICAL_SEMANTIC_FIELDS = ("capabilities", "relations", "dependencies")


def execution_contract_fingerprint(spec) -> str:
    """执行契约指纹(评审 #106 P0 + #107 P0① + #108 P0): 纯执行身份——
    canonical_execution_contract() 唯一入口(不再手动 filter, 杜绝两套字段组漂移)
    + tool + contract_schema_version + fp_scheme。
    capabilities/relations/name 不进(语义层,semantic_fingerprint 承担)。
    schema_version 独立于 workflow schema: 契约结构变化才改(评审 #107)。"""
    import hashlib as _hc
    import json as _jc
    c = canonical_execution_contract(spec)
    return _hc.sha256(_jc.dumps({**c,
                                 "tool": spec.name,
                                 "schema_version": CONTRACT_SCHEMA_VERSION,
                                 "fp_scheme": FP_SCHEME_VERSION},
                                sort_keys=True, default=str).encode()).hexdigest()


def semantic_fingerprint(spec) -> str:
    """语义指纹(评审 #106 P0): name + capabilities + relations + dependencies——
    搜索/规划语义层身份,与执行身份独立(评审明令: 不接 resume/execution)。"""
    import hashlib as _hc
    import json as _jc
    return _hc.sha256(_jc.dumps(canonical_semantic_identity(spec),
                                sort_keys=True, default=str).encode()).hexdigest()


def contract_fingerprint_for(spec) -> str:
    """执行契约指纹(短形;评审 #100 + #102): 与 execution_contract_fingerprint 同义,截 16 显示。"""
    return execution_contract_fingerprint(spec)[:16]


__all__ = [
    "WORKFLOW_SCHEMA_CURRENT", "FP_SCHEME_VERSION", "CONTRACT_SCHEMA_VERSION",
    "DEP_VERSION_ARGS", "EXECUTION_CONTRACT_FIELDS", "CANONICAL_SEMANTIC_FIELDS",
    "canonical_execution_contract", "canonical_semantic_identity", "canonical_contract",
    "execution_contract_fingerprint", "semantic_fingerprint", "contract_fingerprint_for",
]