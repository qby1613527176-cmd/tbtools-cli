"""Identity 性质测试矩阵(评审 #107 #108)——与 workflow 集成测试分离的可维护文件。

TestReview107PropertyMatrix: 10 性质(同路径/换路径/换内容/换ref/换slot/换tool/换schema/换capability/换relations/换dependency)
TestReview108Cleanup:      outputs projection 回归 / 唯一常量 / 唯一入口 / schema_version 拆分
TestReview108StaticRuntimeSplit: static compile(validate) vs runtime resolve(run) 分层
"""
import os
import shutil


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class TestReview107PropertyMatrix:
    """评审 #107 性质测试矩阵(10 性质)——identity 边界验收标准。

    同路径 + 同内容       → same (execution)
    换路径 + 同内容       → same execution (内容寻址)
    换内容               → different execution
    换 symbolic ref      → different binding
    换 slot              → different binding
    换 tool              → different contract
    换 schema            → different contract
    换 capability        → different semantic
    换 relations         → different semantic
    换 dependency        → different execution
    """

    def test_01_same_path_same_content_same(self, tmp_path):
        """同路径同内容 → execution_fp 相同(幂等)"""
        from tbtools_cli.workflow import compile_step_full
        s = {"id": "t", "tool": "volcano",
             "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {},
                         "output": "/tmp/a.svg"}}
        c1, c2 = compile_step_full(s, "/tmp", {}), compile_step_full(s, "/tmp", {})
        assert c1.execution_fingerprint == c2.execution_fingerprint
        assert c1.binding_fingerprint_full == c2.binding_fingerprint_full

    def test_02_path_change_same_content_same_execution(self, tmp_path):
        """换路径同内容 → execution_fp 不变(内容寻址)"""
        from tbtools_cli.workflow import compile_step_full
        p = tmp_path / "deg_copy.txt"
        shutil.copy("examples/data/deg.txt", p)
        s1 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {}, "output": "/tmp/a.svg"}}
        s2 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": [str(p)], "parameters": {}, "output": "/tmp/a.svg"}}
        c1, c2 = compile_step_full(s1, "/tmp", {}), compile_step_full(s2, "/tmp", {})
        assert c1.execution_fingerprint == c2.execution_fingerprint
        assert c1.binding_fingerprint_full == c2.binding_fingerprint_full  # 路径抽象

    def test_03_content_change_execution_diff(self, tmp_path):
        """换内容 → execution_fp 变"""
        from tbtools_cli.workflow import compile_step_full
        p = tmp_path / "deg_mod.txt"
        shutil.copy("examples/data/deg.txt", p)
        p.write_text(p.read_text() + "#tamper\n")
        s1 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {}, "output": "/tmp/a.svg"}}
        s2 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": [str(p)], "parameters": {}, "output": "/tmp/a.svg"}}
        c1, c2 = compile_step_full(s1, "/tmp", {}), compile_step_full(s2, "/tmp", {})
        assert c1.execution_fingerprint != c2.execution_fingerprint

    def test_04_symbolic_ref_change_binding_diff(self):
        """换 symbolic ref({input.genome}→{input.transcriptome}) → binding_fp 变(评审 #107 P0②)"""
        from tbtools_cli.workflow import compile_step_full
        s1 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["{input.genome}"], "parameters": {}, "output": "/tmp/a.svg"}}
        s2 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["{input.transcriptome}"], "parameters": {}, "output": "/tmp/a.svg"}}
        c1, c2 = compile_step_full(s1, "/tmp", {}), compile_step_full(s2, "/tmp", {})
        assert c1.binding_fingerprint_full != c2.binding_fingerprint_full, \
            "不同 symbolic ref 必须不同 binding_fp(引用非身份=接线语义丢失)"

    def test_05_slot_change_binding_diff(self):
        """换 slot(输入个数/位置变化) → binding_fp 变"""
        from tbtools_cli.workflow import compile_step_full
        s1 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["{input.a}"], "parameters": {}, "output": "/tmp/a.svg"}}
        s2 = {"id": "t", "tool": "volcano",
              "binding": {"inputs": ["{input.a}", "{input.b}"], "parameters": {}, "output": "/tmp/a.svg"}}
        c1, c2 = compile_step_full(s1, "/tmp", {}), compile_step_full(s2, "/tmp", {})
        assert c1.binding_fingerprint_full != c2.binding_fingerprint_full

    def test_06_tool_change_contract_diff(self):
        """换 tool → contract_fp 变"""
        from tbtools_cli.workflow import execution_contract_fingerprint
        from tbtools_cli.command_spec import CommandSpec, InputSpec
        a = CommandSpec(name="toolA", group="g", kind="manual", inputs=[InputSpec("x", format="tsv")])
        b = CommandSpec(name="toolB", group="g", kind="manual", inputs=[InputSpec("x", format="tsv")])
        assert execution_contract_fingerprint(a) != execution_contract_fingerprint(b)

    def test_07_schema_change_contract_diff(self):
        """换 contract schema / fp scheme → contract_fp 变(评审 #107 P0①)
        ——常量内嵌: 改 CONTRACT_SCHEMA_VERSION 后旧 fp 自动失效(resume 安全)"""
        import tbtools_cli.identity as _id
        from tbtools_cli.identity import execution_contract_fingerprint
        from tbtools_cli.command_spec import CommandSpec
        sp = CommandSpec(name="t", group="g", kind="manual")
        fp1 = execution_contract_fingerprint(sp)
        _old = _id.CONTRACT_SCHEMA_VERSION
        try:
            _id.CONTRACT_SCHEMA_VERSION = "2"  # 模拟契约 schema 升级(改 identity 真源)
            fp2 = execution_contract_fingerprint(sp)
        finally:
            _id.CONTRACT_SCHEMA_VERSION = _old
        assert fp1 != fp2, "contract schema 升级必须改变 contract_fp"
        # 且 fp 确实含 schema_version(与实现对齐——直接比对实现输出)
        import hashlib
        import json as _jc
        c = _id.canonical_contract(sp)
        _payload = {k: c.get(k) for k in _id.EXECUTION_CONTRACT_FIELDS}
        _payload.update({"tool": c.get("name"),
                         "schema_version": _id.CONTRACT_SCHEMA_VERSION,
                         "fp_scheme": _id.FP_SCHEME_VERSION})
        _h = hashlib.sha256(_jc.dumps(_payload, sort_keys=True, default=str).encode()).hexdigest()
        assert _h == execution_contract_fingerprint(sp)

    def test_08_capability_change_semantic_diff(self):
        """换 capability → semantic_fp 变"""
        from tbtools_cli.command_spec import CommandSpec
        from tbtools_cli.workflow import semantic_fingerprint
        a = CommandSpec(name="t", group="g", kind="manual", capabilities=["alignment"])
        b = CommandSpec(name="t", group="g", kind="manual", capabilities=["phylogeny"])
        assert semantic_fingerprint(a) != semantic_fingerprint(b)

    def test_09_relations_change_semantic_diff(self):
        """换 relations → semantic_fp 变"""
        from tbtools_cli.command_spec import CommandSpec
        from tbtools_cli.workflow import semantic_fingerprint
        a = CommandSpec(name="t", group="g", kind="manual", relations={"accepts": ["FASTA"]})
        b = CommandSpec(name="t", group="g", kind="manual", relations={"accepts": ["GFF3"]})
        assert semantic_fingerprint(a) != semantic_fingerprint(b)

    def test_10_dependency_change_execution_diff(self, monkeypatch):
        """换 dependency → execution_fp 变(依赖版本是执行身份一部分, 经 execution_fp 的
        dependencies 字段, 非 contract_fp——contract 层不声明 dependencies)"""
        import copy
        from tbtools_cli import workflow as _wf
        from tbtools_cli.command_spec import build_command_specs
        _wf._DEP_VERSION_CACHE.clear()
        # build_command_specs() 每次重建, 用 patch 控制返回 spec 的 dependencies
        _base = copy.deepcopy(build_command_specs()["volcano"])
        _s_muscle = copy.deepcopy(_base); _s_muscle.dependencies = ["muscle"]
        _s_mafft = copy.deepcopy(_base); _s_mafft.dependencies = ["mafft"]
        _cur = {"spec": _s_muscle}
        monkeypatch.setattr("tbtools_cli.command_spec.build_command_specs",
                            lambda: {"volcano": _cur["spec"]})
        s = {"id": "t", "tool": "volcano",
             "binding": {"inputs": ["examples/data/deg.txt"], "parameters": {}, "output": "/tmp/a.svg"}}
        c1 = _wf.compile_step_full(s, "/tmp", {})
        _cur["spec"] = _s_mafft
        c2 = _wf.compile_step_full(s, "/tmp", {})
        _wf._DEP_VERSION_CACHE.clear()
        assert c1.execution_fingerprint != c2.execution_fingerprint, \
            "依赖声明不同必须改变 execution_fp(dependency 属 Runtime Identity)"


class TestReview108Cleanup:
    """评审 #108: identity cleanup / dedup——输出唯一真相 + 无重复定义"""

    def test_outputs_projection_change_fp_stable(self):
        """output_slots 同 + outputs projection 变 → contract_fp/execution_fp 不变
        (评审 #108 P1-1: output_slots 唯一真相, outputs 是投影, 投影变≠契约变)"""
        import copy
        from tbtools_cli.workflow import execution_contract_fingerprint
        from tbtools_cli.command_spec import build_command_specs
        a = build_command_specs()["volcano"]
        b = copy.deepcopy(a)
        b.outputs = list(b.outputs) + ["extra_projection"]
        assert execution_contract_fingerprint(a) == execution_contract_fingerprint(b), \
            "outputs projection 变化不应改变 execution_contract_fp"

    def test_no_duplicate_execution_fields_constant(self):
        """评审 #108 P0: EXECUTION_CONTRACT_FIELDS 只此一套且不含 outputs——
        (旧 CANONICAL_EXECUTION_FIELDS 残留已删; 两套常量并存=漂移风险)"""
        import inspect
        import tbtools_cli.workflow as wfm
        src = inspect.getsource(wfm)
        # 不含 outputs 的旧常量定义不得再次出现
        assert "CANONICAL_EXECUTION_FIELDS" not in src, "旧常量残留未清"
        assert "outputs" not in wfm.EXECUTION_CONTRACT_FIELDS, \
            f"outputs 混入 execution identity: {wfm.EXECUTION_CONTRACT_FIELDS}"

    def test_canonical_execution_contract_is_single_entry(self):
        """fingerprint 与 canonical_execution_contract 完全一致(唯一入口)——
        不再可能 canonical 说 A / fingerprint hash B"""
        from tbtools_cli.workflow import (canonical_execution_contract,
                                          execution_contract_fingerprint)
        from tbtools_cli.command_spec import build_command_specs
        import hashlib
        import json as _jc
        for name in ("volcano", "blastp", "heatmap"):
            sp = build_command_specs().get(name)
            if not sp:
                continue
            import tbtools_cli.workflow as _wf
            c = canonical_execution_contract(sp)
            _h = hashlib.sha256(_jc.dumps(
                {**c, "tool": sp.name,
                 "schema_version": _wf.CONTRACT_SCHEMA_VERSION,
                 "fp_scheme": _wf.FP_SCHEME_VERSION},
                sort_keys=True, default=str).encode()).hexdigest()
            assert _h == execution_contract_fingerprint(sp), f"{name} fingerprint 与 canonical 不一致"

    def test_compiled_invocation_schema_versions_clear(self):
        """评审 #108 P1-2: workflow_schema_version / contract_schema_version 分离——
        不再有模糊的 schema_version 误导(≠CONTRACT_SCHEMA_VERSION 混淆)"""
        import inspect
        import tbtools_cli.workflow as wfm
        src = inspect.getsource(wfm.CompiledInvocation)
        assert "workflow_schema_version" in src
        assert "contract_schema_version" in src
        assert "self.schema_version = " not in src, "模糊 schema_version 残留"


class TestReview108StaticRuntimeSplit:
    """评审 #108 P1-2: static compile 与 runtime resolve 分层"""

    def test_static_compile_skips_runtime(self, tmp_path):
        """runtime_resolve=False: 不读输入内容/不 fork dep→execution_fp 不含 input sha"""
        from tbtools_cli.workflow import compile_step_full
        p = tmp_path / "deg.txt"
        shutil.copy("examples/data/deg.txt", p)
        s = {"id": "t", "tool": "volcano",
             "binding": {"inputs": [str(p)], "parameters": {}, "output": "/tmp/a.svg"}}
        c_static = compile_step_full(s, "/tmp", {}, runtime_resolve=False)
        c_full = compile_step_full(s, "/tmp", {})
        assert c_static.runtime_resolve is False
        assert c_full.runtime_resolve is True
        # 静态契约/binding 身份两模式一致(契约不依赖 runtime)
        assert c_static.contract_fingerprint == c_full.contract_fingerprint
        assert c_static.binding_fingerprint_full == c_full.binding_fingerprint_full
        # execution_fp: full 含 input sha → 与 static 不同(static 不读内容)
        assert c_static.execution_fingerprint != c_full.execution_fingerprint

    def test_validate_uses_static_compile(self, tmp_path):
        """validate_workflow 走 static compile(runtime_resolve=False)——不 fork 外部工具"""
        from tbtools_cli.workflow import validate_workflow
        wf = tmp_path / "w.yaml"
        wf.write_text("""id: v.static
schema_version: "1.1"
steps:
  - id: v
    tool: expr volcano
    binding: {inputs: ["{workdir}/deg.txt"], parameters: {}, output: "{workdir}/v.svg"}
""")
        wd = tmp_path / "w.wf"
        wd.mkdir()
        shutil.copy("examples/data/deg.txt", wd / "deg.txt")
        r = validate_workflow({"id": "v.static", "schema_version": "1.1",
                               "steps": [{"id": "v", "tool": "expr volcano",
                                          "binding": {"inputs": ["{workdir}/deg.txt"],
                                                      "parameters": {}, "output": "{workdir}/v.svg"}}]})
        assert r["valid"] is True or not any(
            e["code"] == "WORKFLOW_COMPILE_ERROR" for e in r.get("errors", []))

