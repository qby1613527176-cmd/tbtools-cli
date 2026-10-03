# contracts/tools/*.yaml — 生成快照（勿手改）

> **这不是契约真源。** 本目录由 `scripts/gen_metadata.py` 从代码中的
> CommandSpec 单向导出（先清空再重写），是**协议可读的生成快照/覆盖层**。

## 真源优先级（评审 #110 建议③）

```
代码真源（优先）：
  tbtools_cli/command_spec.py
    ├── KNOWN_* 表（KNOWN_INPUTS / KNOWN_OUTPUT_SLOTS / KNOWN_CAPABILITIES
    │              / KNOWN_RELATIONS / KNOWN_DEPENDENCIES / KNOWN_PARAMS
    │              / KNOWN_NAMED_FLAGS / KNOWN_ALIASES ...）
    ├── ENGINE_REGISTRY（引擎命令表）
    ├── CLI_TOOLS / cli_tools_registry.py（工具注册表）
    └── CommandSpec 单一契约模型（command_spec.py 构建逻辑）
        │
        │ 单向导出（gen_metadata.py --render）
        ▼
contracts/tools/*.yaml（生成快照，勿手改，勿当真源）
```

## 覆盖行为（加载时）

- `load_contracts()` 读 YAML；`build_command_specs()` 构建后 `_apply_contract_overlay()`
  用 YAML 做**向后兼容覆盖**。
- **capabilities**：代码真源优先——YAML 仅在代码未声明时兜底（
  `if not spec.capabilities: spec.capabilities = yaml 值`），防止旧快照覆盖新标注。
- **inputs/outputs/parameters**：保留 YAML 覆盖（历史兼容层）；但 YAML 是导出的，
  正常情况下与代码一致，偏离即视为快照过期——请重跑 `gen_metadata.py` 而非手改 YAML。

## 修改契约的正确方式

1. 改代码真源：`tbtools_cli/command_spec.py`（KNOWN_* 表或构建逻辑）
2. 重生成快照：`python3 scripts/gen_metadata.py --render`
3. 跑门禁：`pytest` / `ruff` / `mypy`

## 历史教训

1.4.15–1.4.24 曾出现「代码 ↔ YAML 双向覆盖」：YAML 被当作真源手工修改，
旧值通过导出-覆盖循环持久化，导致 planner 语义丢失（如 mastExtract 的
capabilities 被旧快照 `['sequence']` 覆盖新标注 `['motif','sequence_extraction']`）。
评审 #110 建议③ 定型：**代码是唯一真源，YAML 是导出物**。