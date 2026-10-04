# tbtools-cli 活 PLAN（需求 → 实现 → 验证 单一入口）

> 第三十二波 Compound Engineering 第①招「单一 plan artifact 收敛」落地件 — 2026-10-04
> **本文件是当前唯一活的进度 plan**；docs/_worklog/ 其余 .md 均为历史存档（头部已标）。
> 编年史/坑表仍在 `workflows/tbtools_cli化_总清单.md`（波次记录）；本文件只管「现在做什么、到哪了」。

## 当前快照（2026-10-04 22:45）

- **版本**：v1.4.55（v1.4.19→v1.4.55 三十七连发）
- **执行验证**：54/60 = 90%（v1.4.27 的 7% 一路）
- **门禁**：pytest 619 passed / ruff 0 / mypy 0（三件套本地齐跑）
- **最近波次**：47 波 = peakanno/peaktss 收编（90% 里程碑）（扁平 .keg 格式实锤）

## 待办需求（DRIVER = 需求；IMP = 实现；VER = 验证）

### A. 执行验证（✅ 完结于 90%，v1.4.57）

> 剩余 6 个（A1-A6）已定性归档至 `docs/_worklog/EXEC_VERIFIED_LEFTOVER.md`（引擎缺陷/外部依赖，复攻条件见档）

| ID | 工具 | 状态 |
|:--|:--|:--|
| A1-A6 | pafref/tfbsShift/microsyn/memerun/smart/gxfIdAppender | 🗂️ 已归档（引擎缺陷 4 + 外部依赖 2），详见 EXEC_VERIFIED_LEFTOVER.md |
| A7-A8 | peakanno/peaktss | ✅ 已收编（v1.4.57，bin0 边界绕过） |

### B. 系统改进（50/50 规则，第③招）

| ID | 需求 | 状态 | IMP | VER |
|:--|:--|:--|:--|:--|
| B1 | skills_repo 周度蒸馏自动化（09/11 搁置） | 待排期 | ☐ | ☐ |
| B2 | AST 压缩接入评审/修复流程（第三十六波①） | 工具已就绪，首次实战待用 | ☐ | ☐ |
| B3 | 输出废话削减（第三十六波②） | 行为纪律，已部分生效 | ✅ | ☐ |
| B4 | 模式表维护（第②招） | 已建 docs/REVERSE_ENGINEERING_PATTERNS.md（P1-P5） | ✅ | ✅ |
| B5 | 单一 plan 收敛（本文件） | 本次落地 | ✅ | ✅ |

### C. 评审节奏

| ID | 需求 | 状态 |
|:--|:--|:--|
| C1 | 评审 #115 发起 | 输入包已就绪 docs/REVIEW_PACKAGE_115.md（v1.4.59），待送外部评审 |
| C2 | AST 压缩在下次评审前启用 | ✅ 已接入（压缩版入库 docs/_generated/*.min.py） |

## 进行中

- **当前**：B 线（Compound 三招落地中）→ 完成后转 B2（AST 首次实战：攻 A7/peaktss 时用）

## 历史存档指针（docs/_worklog/）

- BATCH1_STATUS.md — 批次1 复活类（09/21）归档
- BATCH2_STATUS.md — 批次2 RPC 稳定性（09/21）归档
- RPC_FIX_STATUS.md — RPC 交付包 N1-N41（09/21 完成）归档
- EXTERNAL_TEST_REPORT_20260919.md — WorkBuddy 外部实测报告（未修项见 §4/§8）
- biodoer_modules_candidates.txt / rpc_methods_list.txt — 探索期参考资料（08/29）