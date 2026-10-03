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
        """YAML 快照与代码真源全量 equality(评审 #110 建议③ + #111 P1-1 + #112 P0-1):
        用 _skip_overlay 拿纯代码 spec, canonical_snapshot(code) == canonical(code 投影 YAML)——
        一次覆盖 inputs/output_slots/parameters/layout/named_flags/capabilities/dependencies/
        relations/status/aliases(此前逐个 assert 只查 capabilities+inputs, 59 个 output_slots
        漂移测不出)。不一致=快照过期, 重跑 gen_metadata 而非手改 YAML。"""
        from tbtools_cli.command_spec import build_command_specs, load_contracts
        from tbtools_cli.identity import canonical_snapshot, yaml_to_snapshot
        contracts = load_contracts()
        # 纯代码真源(跳过 YAML 校验/兑底)——这才是与快照对比的正确基准
        specs = build_command_specs(force=True, _skip_overlay=True)
        # 全量验证不提前 break(曾 10 个就停, 字母序靠后工具从未被查=盲区)
        checked = 0
        for name, c in contracts.items():
            sp = specs.get(name)
            if not sp:
                continue
            _code = canonical_snapshot(sp)
            _yaml = yaml_to_snapshot(c)
            if _code != _yaml:
                _diff = sorted(k for k in _code if _code.get(k) != _yaml.get(k))
                raise AssertionError(
                    f"{name}: 快照过期 {_diff}——代码 {str({k: _code.get(k) for k in _diff})[:120]} "
                    f"!= 快照 {str({k: _yaml.get(k) for k in _diff})[:120]}, 重跑 gen_metadata --render")
            checked += 1
        assert checked > 0
