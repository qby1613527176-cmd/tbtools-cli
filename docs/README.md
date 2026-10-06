# docs/ — 维护者导航（自审 docs F9 响应）

> 面向**维护者/接续会话**的仓库内路标（不是用户文档——用户看 `docs/index.md` / quickstart）。
> 新会话接续：**先读本页 → PLAN.md（活 plan）→ 编年史总清单（历史）**，AGENTS.md 长期任务恢复协议同理。

## 文档地图

| 你要找 | 去这里 |
|:--|:--|
| **当前进度/待办**（活 plan） | `_worklog/PLAN.md`（唯一活 plan；快照纪律：只记可即时核对事实，波次细节归编年史） |
| **项目编年史**（波次记录/决策过程） | 仓库外：`workflows/tbtools_cli化_总清单.md`（workspace 侧）；仓库内波次级细节看 CHANGELOG |
| **发布流程**（硬 checklist） | `RELEASING.md`（bump/CHANGELOG/数字同步/tag 校验——自审 docs F5 补） |
| **命令参考**（用户侧权威） | `COMMAND_REFERENCE.md`（首部含**命名约定**：camelCase/全小写/别名计划/tree 特例/engine 分组语义）+ 自动生成 `_generated/commands.md` |
| **评审材料流向** | `REVIEW_PACKAGE_115.md`（输入包）→ `_PREVIEW.md`（预审意见）→ `_SUBMISSION.md`（送审包，待外发）；自审战役意见在 `_worklog/self_review/` |
| **架构/模式** | `REVERSE_ENGINEERING_PATTERNS.md`（引擎逆向模式）+ `_worklog/` 各批状态 + `adr/` |
| **GUI 逆向 SOP** | `GUI-INTERFACE-SOP.md` |
| **Agent 协议** | `agent-protocol.md`（Agent 调用约定/readiness×verification 决策矩阵） |
| **生成物 vs 手写物** | 手写：上表各 .md；**自动生成（勿手改）**：`_generated/`（gen_metadata --render 产物）、`command_metadata.json`、`ai/`（`--check` 防漂移） |

## 维护纪律

1. **发版必记波**（RELEASING.md checklist）：bump pyproject + CHANGELOG 补节 + 编年史追加波次——三处版本载体与 git tag 保持同步
2. **数字同步**：任何命令数/工具数/版本号改动 → `python3 scripts/gen_metadata.py --render` + `--check`（版本一致性门禁已内置）
3. **活文档**：PLAN.md 快照每次发版刷新；"活"不是声称出来的，是每次发版更新的纪律
4. **生成物只读**：`_generated/`、`ai/`、`command_metadata.json` 由 gen_metadata 生成——改数据源（ENGINE_REGISTRY/CLI_TOOLS）而非生成物

## 评审流向（#115 及后续）

```
REVIEW_PACKAGE_115.md(输入包) ──► _PREVIEW.md(预审意见) ──► 响应轮(v1.4.60-62) ──► _SUBMISSION.md(送审包) ──► 外发
                                                                                    └── 自审战役(2026-10-05, 8 P0+21 P1 闭环) ──► _worklog/self_review/
```
