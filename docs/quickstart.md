# 快速开始

## 0. 依赖速查（自审 product F10：每条命令的 JAR 依赖明示）

| 命令 | 需要 JAR？ | 零配置（无 JAR）行为 |
|:--|:--|:--|
| `tbtools version / list / search / help / tool-describe` | **否** | 正常（纯元数据/静态） |
| `tbtools expr volcano ...`（绘图/分析） | **是** | dry-run 显示 `dependencies.tbtools_jar.ready=false`；真实运行报 TB102 文件缺失前先 `doctor` 配置 |
| `tbtools new / check` | 否/部分 | 向导与文件检查纯本地 |

> 快速判断：`tbtools tool-describe <命令> --json` 输出 `availability.status` = `ready` / `missing_dependencies`。

## 1. 配置 JAR（三选一）

```bash
tbtools doctor                 # 环境自检,给指引
tbtools setup --auto           # 自动搜索本机 TBtools
tbtools fetch-jar --yes        # 自动下载官方包提取 JAR
```

## 2. 出第一张图

```bash
tbtools expr volcano examples/data/deg.txt volcano.svg --pval-cutoff 0.05
# 需要 JAR：是。未配置时先跑第 1 步；已配置则直接出图（DEG 火山图）
```

## 3. 探索

```bash
tbtools list plots             # 213 个绘图命令(权威数: tbtools version --json)
tbtools search volcano         # 模糊搜索（分组标签与元数据同源: [expr/manual]）
tbtools help volcano           # 命令详情(含坑位提示)
tbtools tool-describe volcano bamsort --json   # 批量机器描述(Agent 能力)
tbtools new                    # 交互式向导
```

## 4. 退出码 / 错误码（自审 product F10：此前散落，无单一参考）

| 退出码 | 含义 |
|:--|:--|
| 0 | 成功 |
| 1 | 参数/数据错（TB001 参数无效 → `--help`；分层码 TB101） |
| 2 | 文件缺失（TB002_FILE_NOT_FOUND → `check the input file path exists`；分层码 TB102） |
| 3 | 格式不匹配（TB003/TB004 → 检查列数/类型/分隔符/schema） |
| 4 | 内存不足（TB008 → `config.toml [defaults] memory` 调大） |

结构化错误（`--json` 协议）字段：`code`（分层码 TB1xx）/ `legacy_code` / `category`（input|core|engine|dependency|network）/ `retryable` / `suggested_action`——Agent 按 `suggested_action` 行动。

## 5. readiness × verification（自审 product F7 决策矩阵摘要，详见 agent-protocol.md）

| readiness \ verification | DECLARED（声明） | EXECUTION_VERIFIED（跑过） | CONFORMANCE_VERIFIED（金链） |
|:--|:--|:--|:--|
| FULL（契约完整） | 可直接试跑（契约可信） | **首选**（真实执行+产物+指纹证据） | 金链级（volcano 标杆） |
| PARTIAL（部分契约） | 试跑前建议 `tool-validate` | 可跑（证据在，契约略缺） | — |
| LEGACY（仅注册） | 不保证可跑（无契约） | — | — |

> 最小示例数据:`git clone` 仓库后 `examples/data/`。
