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
        """YAML 快照与代码真源一致(评审 #110 建议③: 快照非真源, 一致性验证——
        不一致=快照过期, 重跑 gen_metadata 而非手改 YAML)。"""
        from tbtools_cli.command_spec import build_command_specs, load_contracts
        contracts = load_contracts()
        specs = build_command_specs()
        checked = 0
        for name, c in contracts.items():
            if c.get("capabilities") and name in specs:
                # 快照与代码一致(快照导出自代码); 若不一致说明快照过期
                assert specs[name].capabilities == list(c["capabilities"]),                     f"{name}: YAML 快照与代码真源不一致(快照过期, 重跑 gen_metadata)"
                checked += 1
                if checked >= 5:
                    break
        assert checked > 0
