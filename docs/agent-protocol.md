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

`tool-describe <cmd> --json` 输出(**恒返回数组**, 单命令/多命令形状一致; 单命令取 `[0]`):

```json
[
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
]
```

> **注意**: 上例为**实际输出形状**——即使单命令也恒为长度 1 的数组, 取 `[0]` 后才是对象。
> 此前示例误展示裸对象, 照抄示例的 Agent 解析器会踩类型错误。

**Agent 只使用 contract 名(`pval_cutoff`);runtime 负责翻译为 CLI flag(`--pval-cutoff`)**。

### 6.1 验证证据与 env_fingerprint 爆破半径(自审 verified N3)

`verification_details`(tool-describe --json / ai/tools/*.json, 仅 EXECUTION_VERIFIED 工具存在):

```json
{
  "level": "EXECUTION_VERIFIED",
  "contract_fingerprint": "<64-hex>",
  "env_fingerprint": "<64-hex>",
  "verified_at": "ISO-8601",
  "last_passed_at": "ISO-8601",
  "corpus": "examples/data",
  "semantic_checked": true,
  "domain_note": "verified for coords >= binSize(10000)..."
}
```

> **注意**: 上例 `semantic_checked: true` 是**理想化示意**——
> 当前全库 56 条验证证据中 **11 条为 true**(有内容级语义断言, 见 SEMANTIC_CHECKS),
> 其余 45 条为 false(仅执行验证/金链 conformance 六步断言无内容级语义断言)。
> 读方以实际报告为准, 勿把示例当 schema 参照(层级≠证据强度超集)。

**时间语义(两个字段, 2026-10-11 拆分)**:

- `verified_at` = **首次验证时间**(该 contract+env 组合首次通过), 冻结不刷新——历史追溯用。
- `last_passed_at` = **最近一次通过时间**, 每次 pass 无条件刷新——TTL 保鲜检查(90 天)查它,
  解决"每晚验证成功仍被 90 天 TTL 判过期"的矛盾。旧报告(763e55c 前)无此字段时回退 `verified_at` 兼容。
- **时间戳格式**: v1.4.96 起写入端为 **UTC-aware ISO-8601**(如 `2026-10-12T17:20:28+00:00`);
  旧报告(py)的 naive 时间戳按 UTC 解释兼容(读取端 `_parse_naive` 统一归一)。同一报告中可能混存
  新旧格式(如 3 条 skip/xfail 继承的旧 naive 值), 判龄/对比一律按 UTC 语义处理, 勿按本地时区解读。

Agent 判定"验证是否新鲜"应读 `last_passed_at`(每夜 render 即保鲜), 而非 `verified_at`(可能冻结在首次)。

**⚠️ env_fingerprint 是全局单值**(JAR + plugins/lib 全部 jar + KNOWN_DEPENDENCIES 派生的全部
外部二进制哈希):**任何**一个外部二进制升级(如 muscle), 所有工具的验证都会降级——包括与该
二进制无关的工具。因此 `execution_verified` 计数是"验证机上完全同构环境"的读数; 用户机器
与验证机二进制版本不同时, `tbtools version --json` 的 execution_verified 会低于发布的 56。
这不是 bug, 是全局环境身份的保守语义: 证据只在同构环境可迁移。验证机之外拿到的
**env_fingerprint 定义(十二轮 docs/arch P2 补)**: 它是**二进制内容集合身份**——由每个
文件的 SHA-256(经 (path,mtime,ctime,size) 缓存)按稳定顺序(sorted 枚举)级联哈希;
**不含文件名/路径名**。因此同内容不同文件名 = 同指纹(插件重命名不改变环境身份);
插件按名加载失败会有显式报错兜底, 不依赖指纹区分。若未来按名加载的插件语义需要
区分文件名, 再评估将规范化相对路径纳入哈希(当前不推——路径入哈希会致 fetch-jar
移动/重装布局变化误伤全部证据)。
`EXECUTION_VERIFIED` 应视为"该版本在该环境跑过", 而非"当前环境可用"。

`verification_details.level` 是**报告时快照**; 当前判定看顶层 `verification` 字段(加载侧有
contract_fp/env_fp 双比对, 失配即降级)。两者分叉时 details 不投影(证据已失效)。

**CONFORMANCE_VERIFIED 继承语义**: 金链级(volcano)证据的保留规则——
- 本次金链测试 **pass** → 新证据(升级/刷新);
- 本次金链 **skip / 未运行**(如无 JAR 环境) → 若旧证据仍是 CONFORMANCE_VERIFIED 且
  contract_fp/env_fp 与旧证据一致 → **继承保留**; 指纹已变则降级(金链观测绑定旧契约);
- 本次金链 **fail** → **降级 EXECUTION_VERIFIED**(明确反观测, 不得保留)。
无 JAR 环境下读到的 CONFORMANCE_VERIFIED 表示"该契约+环境曾有金链通过证据且未被反证",
而非"本次运行金链通过"。

### 6.2 验证层级边界(能证明什么 / 不能证明什么)

| 指标 | 能证明 | 不能证明 |
|:--|:--|:--|
| `execution_verified`(56) | 该工具在真实引擎上执行成功且产物存在 | ❌ 产物内容科学正确 / 参数选择合理 |
| `semantic_checked`(11) | 产物通过内容级断言(如 est_counts 为正数) | ❌ 生物学结论正确(仅是数值合理性) |
| `conformance_verified`(1) | 金链六步全过(执行+产物+内容) | ❌ 推广到其他工具(n=1 试验层) |
| `readiness FULL`(60) | 输入/输出/能力/依赖契约声明完整 | ❌ 参数已审计(见 params_status) |
| `params_status complete`(8) | 参数契约经人工审计确认 | ❌ unknown(52) 表示未审计, 非「无参数」 |

⚠️ 验证层级**不构成科学正确性背书**——执行验证只证明「跑通了」，不证明「跑对了」。

### 6.3 params_status(参数契约审计状态)

每个工具的 `params_status` 字段(tool-describe --json / ai/tools/*.json / version --json 均可见):

- `complete`: 参数契约经人工审计(当前 8 个, 见 KNOWN_PARAMS)
- `unknown`: 参数契约未审计(当前 290 个)——**不代表无参数**, 只代表「未逐个核对」
- 预留(未启用): `partial`(部分审计) / `confirmed_none`(审计确认无参数)

`version --json` 的 `full_params_verified`/`full_params_unknown` 是 FULL 级工具的 params_status 拆分(如 8/52)。

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
- **binding 形态**(推荐): `binding: {inputs: [...或 {slot: ref}], parameters: {...}, output: "..."}`——契约编译(compile_step → InvocationSpec);多输入工具用 dict slot 绑定
- legacy `args` 形态兼容至 v2.0(DeprecationWarning)
- 状态: `.wf_state.json` 落盘 → `--resume` 断点续跑
- 产物: 每步 provenance + 语义验证(validation_warning)

## 10. Provenance

`<artifact>.tbtools.json`(成功与失败都写):

```json
{
  "command": "volcano",
  "invocation": "...",
  "tbtools_cli": "<当前版本号, 见 tbtools version --json>",
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
