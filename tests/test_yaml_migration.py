"""YAML 快照一致性(评审 #82 P1-5 + #110 建议③): contracts/tools/X.yaml 是 gen_metadata
导出的生成快照——与代码真源(KNOWN_*)一致; 不一致即快照过期(重跑 gen_metadata)。
评审 #110 建议③ 修正: 不再称 "YAML 胜出", 代码是唯一真源。"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TestYamlMigrationRule:
    def test_no_yaml_known_conflict(self):
        from tbtools_cli.command_spec import (KNOWN_CAPABILITIES, KNOWN_SCHEMAS,
                                              load_contracts)
        contracts = load_contracts()
        conflicts = []
        for name, c in contracts.items():
            # capabilities 冲突(YAML 声明了但 KNOWN 不同)
            if c.get("capabilities") and name in KNOWN_CAPABILITIES:
                if set(c["capabilities"]) != set(KNOWN_CAPABILITIES[name]):
                    conflicts.append(f"{name}: capabilities YAML{len(c['capabilities'])} != KNOWN{len(KNOWN_CAPABILITIES[name])}")
            # inputs 数量冲突(YAML 声明了 inputs 但 KNOWN_SCHEMAS 数量不同)
            if c.get("inputs") and name in KNOWN_SCHEMAS:
                if len(c["inputs"]) != len(KNOWN_SCHEMAS[name][0]):
                    conflicts.append(f"{name}: inputs YAML{len(c['inputs'])} != KNOWN{len(KNOWN_SCHEMAS[name][0])}")
        # 当前允许存在(迁移期),但记录规模——目标 v2 全 YAML
        if conflicts:
            import warnings
            warnings.warn(f"YAML/KNOWN 双写漂移 {len(conflicts)} 处(迁移期容忍,v2 收敛): {conflicts[:3]}",
                          stacklevel=1)

    def test_yaml_snapshot_matches_known(self):
        """YAML 快照与代码真源一致(评审 #110 建议③ + #111 P1-1 独立真源比较:
        用 _skip_overlay 拿纯代码 spec, 不经任何 YAML 覆盖/兑底, 防"overlay 后 spec 比 YAML"自我验证)。
        不一致=快照过期, 重跑 gen_metadata 而非手改 YAML。"""
        from tbtools_cli.command_spec import build_command_specs, load_contracts
        contracts = load_contracts()
        # 纯代码真源(跳过 YAML 校验/兑底)——这才是与快照对比的正确基准
        specs = build_command_specs(force=True, _skip_overlay=True)
        # 评审 #111 P1-1 修正: 全量验证不提前 break——曾 10 个就停, 字母序靠后的工具
        # (如 tpmCalc)从未被检查=评审指出的"测试抓不住问题"盲区
        checked = 0
        for name, c in contracts.items():
            sp = specs.get(name)
            if not sp:
                continue
            # capabilities: 代码真源 vs 快照(严格相等, 无兑底)
            if c.get("capabilities"):
                assert list(sp.capabilities) == list(c["capabilities"]),                     f"{name}: capabilities 快照过期(代码 {sp.capabilities} != 快照 {c['capabilities']}), 重跑 gen_metadata"
                checked += 1
            # inputs: 名称+格式 + cli_name(评审 #111 P0-2: cli_name 是执行语义, 必须一致)
            if c.get("inputs"):
                _code_in = [(i.name, i.format, getattr(i, "cli_name", "")) for i in sp.inputs]
                _yaml_in = [(i.get("name", ""), i.get("format", ""), i.get("cli_name", ""))
                            for i in c["inputs"]]
                assert _code_in == _yaml_in,                     f"{name}: inputs 快照过期(代码 {_code_in} != 快照 {_yaml_in}), 重跑 gen_metadata"
                checked += 1
        assert checked > 0
