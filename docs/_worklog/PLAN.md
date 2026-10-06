# tbtools-cli 活 PLAN（需求 → 实现 → 验证 单一入口）

> 第三十二波 Compound Engineering 第①招「单一 plan artifact 收敛」落地件 — 2026-10-04
> **本文件是当前唯一活的进度 plan**；docs/_worklog/ 其余 .md 均为历史存档（头部已标）。
> 编年史/坑表仍在 `workflows/tbtools_cli化_总清单.md`（波次记录）；本文件只管「现在做什么、到哪了」。

## 当前快照（2026-10-06 04:20 · 自审战役收官后刷新）

> ⚠️ 快照纪律（自审 docs F7 响应）：本区**只能记录可即时核对的事实**（版本/门禁数字从 git tag 与 `tbtools version --json` 推导），
> 任何波次级细节一律看 `workflows/tbtools_cli化_总清单.md`（编年史）——本文件不复制编年史内容，避免双源漂移。

- **版本**：见 `git describe --tags`（快照纪律：不手写版本号，防漂移）
- **执行验证**：54/60 = 90%（v1.4.27 的 7% 一路）
- **自审战役**：五视角 8 P0 + 21 P1 全部闭环（v1.4.66-72）+ 5 个高价值 P2（v1.4.73）
- **门禁**：pytest 621+ passed / ruff 0 / mypy 0（三件套本地齐跑）
  - ⚠️ 口径注（评审 #115 预审 E4）：54 条 EXECUTION_VERIFIED 断言需**含 examples/data 的环境**实跑；clean CI clone 下 52 条 skipped=缺数据 exec，90% 无法复算——CI 应含数据或显式报 skip 清单
- **最近波次**：详见编年史总清单（v1.4.73 波）

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
| C1 | 评审 #115 发起 | ✅ 预审+响应轮全闭环（v1.4.60-62: P1-1/2/3/4 + P2×3 全落地）；送审包 SUBMISSION.md 已产出待外发 |
| C2 | AST 压缩在下次评审前启用 | ✅ 已接入（压缩版入库 docs/_generated/*.min.py） |
| C3 | 五视角自审战役（2026-10-05） | ✅ 8 P0 + 21 P1 全闭环（v1.4.66-72）；5 个高价值 P2（v1.4.73）；5 份意见 + 响应尽在 docs/_worklog/self_review/ |

## 进行中

- **当前**：P2 优化收尾（剩余低危 P2×若干，见各 self_review 报告）→ 可选项：外发评审 #115 SUBMISSION 等外部反馈

## 历史存档指针（docs/_worklog/）

- BATCH1_STATUS.md — 批次1 复活类（09/21）归档
- BATCH2_STATUS.md — 批次2 RPC 稳定性（09/21）归档
- RPC_FIX_STATUS.md — RPC 交付包 N1-N41（09/21 完成）归档
- EXTERNAL_TEST_REPORT_20260919.md — WorkBuddy 外部实测报告（未修项见 §4/§8）
- biodoer_modules_candidates.txt / rpc_methods_list.txt — 探索期参考资料（08/29）