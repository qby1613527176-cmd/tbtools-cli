# Agent Protocol(Agent Runtime Contract v1.0)

> tbtools-cli 面向 Agent 的**正式协议契约**。所有 Agent-facing API(search/describe/validate/plan/run/result/job/artifact/provenance/env)必须遵守本文档。
> 版本: `protocol_version: "1.0"` | 变更策略: 1.x 向后兼容(只增不删/不改语义);2.x 破坏性变更走 deprecation。

## 1. 协议总则(七条铁律)

1. **stdout = 协议**: `--json` 模式下 stdout **只承载协议数据**(纯 JSON,`json.loads(stdout)` 必须成功)
2. **stderr = 日志**: 人类可读日志/Java 输出/进度/警告全走 stderr
3. **错误结构稳定**: 所有错误是结构化对象(见 §4),不是自然语言
4. **artifact identity 稳定**: 产物用 **Artifact 模型**(§5)描述,不是裸路径
5. **exit_code ≠ status**: exit_code 是进程语义(0/1/2/3/4/5/6);status 是业务语义(success/failed/validation_error/...)
6. **discovery 无副作用**: search/describe/validate 不启动计算、不修改文件、不下载依赖
7. **schema_version 必带**: 所有 JSON 输出含 `"schema_version": "1.0"`

## 2. 调用链(Agent Execution Loop)

```
search(发现) → describe(理解) → validate(预检) → plan(规划)
→ run(执行) → artifact(产物检查) → result(结果) → provenance(溯源)
```

- **plan**: `tbtools workflow plan/run`(Workflow 是正式决策层;search 只做工具发现,不承担任务规划)
- **长任务**: `tool-submit → job-status → job-result` 替代同步 `tool-run`

## 3. 统一 JSON 结构

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "schema_version": "1.0",
  "status": "success | failed | not_ready",
  "data": {},
  "error": null
}
```

## 4. 错误契约(ErrorSpec)

```json
{
  "code": "TB102",
  "legacy_code": "TB002_FILE_NOT_FOUND",
  "category": "input | dependency | engine | core | agent",
  "retryable": false,
  "suggested_action": "check the input file path exists"
}
```

- 分层码: TB0xx core/runtime | TB1xx input | TB2xx dependency | TB3xx engine | TB4xx agent
- `retryable=true` 时 Agent 可安全重试(建议修复 `suggested_action` 后)

## 5. Artifact 模型(统一产物描述)

tool-run / tool-result / artifact inspect / workflow **共用同一模型**:

```json
{
  "id": "art_xxx",
  "type": "plot | table | sequence | annotation | phylogenetic_tree | alignment | report | log | data",
  "format": "svg | tsv | fasta | newick | ...",
  "path": "/abs/path",
  "size": 64025,
  "sha256": "<完整 64 位>",
  "producer": "volcano",
  "created_at": "...",
  "validation": {"valid": true, "detail": "svg xml valid"}
}
```

## 6. Tool Contract(CommandSpec)

`tool-describe <cmd> --json` 输出(稳定字段):

```json
{
  "schema_version": "1.0",
  "id": "tbtools.expr.volcano",
  "uri": "tbtools://expr/volcano",
  "name": "volcano",
  "group": "expr",
  "kind": "manual|bridge|direct|tool",
  "help": "...",
  "capabilities": ["differential_expression", "visualization"],
  "capabilities_ontology": ["expression", "expression.differential", ...],
  "inputs": [{"name": "deg", "format": "tsv", "columns": ["GeneID","Log2FC","pvalue"], "required": true}],
  "outputs": ["svg"],
  "parameters": [{"name": "pval_cutoff", "type": "float", "default": 0.05, "cli_name": "--pval-cutoff"}],
  "dependency_manifest": [{"name": "iqtree2", "type": "binary", "required": true, "platforms": ["linux"]}],
  "relations": {"accepts": ["DEG_TABLE"], "produces": ["VOLCANO_PLOT"], "next_step": ["goEnrich"]},
  "status": "stable|beta|platform-limited|network-required",
  "alias_of": null
}
```

**Agent 只使用 contract 名(`pval_cutoff`);runtime 负责翻译为 CLI flag(`--pval-cutoff`)**。

## 7. MCP 接口

- **9 个编排原语**(不是 200+ 工具): search / tool_describe / tool_validate / tool_run / **workflow_plan** / job_submit / job_status / job_result / tool_provenance
- 参数: `arguments: dict`(结构化,**正式**)> `args: list[str]`(legacy)> `args: string`(deprecated)
- `tool-run --json`: stdout 纯 JSON(执行期日志进 stderr)
- Agent 默认安全: engine reflection 关闭(`TBTOOLS_AGENT_MODE`/`[agent.policy]`)

## 8. exit_code 语义

| code | 语义 |
|---|---|
| 0 | success |
| 1 | invalid argument / engine crash / dependency missing |
| 2 | file not found(TB002/TB102) |
| 3 | input format/schema error(TB003/TB103) |
| 4 | out of memory(TB008) |
| 5 | policy error(engine reflection 被拒) |
| 6 | bridge compile failed(TB_BRIDGE_COMPILE_FAILED) |

## 9. Workflow(YAML)

```yaml
id: my.pipeline
steps:
  - id: align
    tool: seq muscle
    args: ["{input.fasta}", "{workdir}/aln.fa"]
  - id: tree
    tool: tree iqtree
    args: ["$align.output", "{workdir}/tree.nwk"]
```

- 引用: `{workdir}` / `{input.X}` / `$step.output` / `{artifact: <path>}`
- 状态: `.wf_state.json` 落盘 → `--resume` 断点续跑
- 产物: 每步 provenance + 语义验证(validation_warning)

## 10. Provenance

`<artifact>.tbtools.json`(成功与失败都写):

```json
{
  "command": "volcano",
  "invocation": "...",
  "tbtools_cli": "1.3.0",
  "exit_code": 0,
  "parameters": {...},
  "outputs": ["/abs/out.svg"],
  "inputs": [{"path": "...", "sha256": "<完整 64 位>"}],
  "input_count": 1,
  "timestamp": "..."
}
```

`provenance-graph <dir>`: 按输入/输出路径关联成运行链 DAG(文本/JSON/mermaid)。

## 变更策略

- protocol 1.x:只增字段,不改语义(旧字段永保留)
- protocol 2.x:破坏性变更,提供 legacy 兼容至少一个大版本
