# 文档/发布视角独立评审 — tbtools-cli v1.4.65

> 2026-10-05 · 独立「文档/发布」视角批判性审查
> 范围：docs/（PLAN/SUBMISSION/LEFTOVER/PATTERNS）+ 总清单（47–51 波 + 待办）+ README + CHANGELOG
> 已知背景：评审 #115 预审 4/4 P1 + 3/3 P2 已响应——本报告只列**已响应项之外**的新问题。
> 立场：只找问题，不称赞。

## 总体结论：**不通过（P0×2 / P1×4 / P2×3）**

发布面（pyproject/CHANGELOG/README/docs 入口）与真实状态（git tag v1.4.65、counts.md）出现**系统性版本漂移**，且无任何文档化的发布流程来防止它。评审 #113 建立的「Generated Surface Gate」防住了 `docs/_generated/` 内部漂移，但**门禁没有覆盖 pyproject.toml version、CHANGELOG.md、README 硬编码数字、docs/*.md 静态页**——漂移全部发生在这四个盲区。送审包声称「自包含」实则引用仓库外路径，外部评审无法独立复算。

---

## 逐项

### F1. pyproject.toml version = 1.4.46，与实际发布 v1.4.65 脱节 19 个版本 — **P0**

- **发现**：`pyproject.toml:7 version = "1.4.46"`；git tag 已到 v1.4.65，`git log` 最近三笔（env_fp 补全 / CI skip 口径 / SUBMISSION 合一）均已发版。`pip install tbtools-cli` 装出的包 `tbtools --version`（若走 importlib.metadata）会报 1.4.46。
- **挑战**：README 宣称「数字权威源 `tbtools version --json` 防漂移」——但包元数据本身恰是最不该漂移的数字，且它是 PyPI/用户看到的版本号。47 连发没有一次 bump version 字段，说明「发版」动作里根本没有 bump 步骤。
- **建议**：发布 checklist 加「bump pyproject version + gen_metadata --check 联动校验 tag==pyproject」；或改用 setuptools-scm/hatch-vcs 从 tag 自动取版本，消灭手写字段。
- **严重度**：P0（对外可安装的元数据说谎）

### F2. CHANGELOG.md 断更于 [1.4.46]，1.4.47–1.4.65 共 19 个 release 无记录 — **P0**

- **发现**：CHANGELOG 头部为 `## [1.4.46] - 2026-10-04`；期间发生了执行验证 44→54（10 工具收编）、90% 里程碑、评审 #115 预审响应全闭环（v1.4.60–62）、env_fp 补全（v1.4.65）等**用户可见**的重大变更。
- **挑战**：CHANGELOG 遵循 Keep a Changelog 格式却完全不 keep。外部用户/评审者看 CHANGELOG 会以为项目停在两天前。而编年史（总清单）在仓库外（~/.openclaw/workspace/workflows/），CHANGELOG 是仓库内唯一的版本叙事载体——它缺席 = 仓库内无版本叙事。
- **建议**：每个 tag 必须对应 CHANGELOG 一节（可简化为 2–4 行）；发布 checklist 卡死「无 CHANGELOG 节 → 不打 tag」；至少把 1.4.47–65 一次性补录。
- **严重度**：P0（Keep a Changelog 承诺违约 + 版本叙事断裂）

### F3. README 与 counts.md 自相矛盾：execution_verified 44 vs 54 — **P1**

- **发现**：README 头部「数字权威源」行写 `execution_verified(44)`；同仓库 `docs/_generated/counts.md` 为 54。README 同段还有第二处漂移：`Project Structure` 节写 `tests/ pytest（83 passed` 与 `PITFALL_HINTS(46)`，实际是 619 passed / 49 hints。
- **挑战**：这正是评审 #113 P0-1 修过的同类病（26→44 漂移），修复时只把 gen_metadata --render 的输出面纳入门禁，**README 里手写的解释性数字仍是盲区**。README 一边自称「counts.md 自动生成防漂移」一边自己手写漂移数字，对外门面信用受损。
- **建议**：README 中所有执行验证/测试数/hints 数改为引用 counts.md 链接或徽章，删除手写数字；或 gen_metadata --check 增加 README 数字扫描（正则抽 `execution_verified\((\d+)\)` 类模式比对）。
- **严重度**：P1（对外门面与权威源矛盾）

### F4. docs/ 静态入口页大面积过期：index.md 自称 v1.1.0 / 218 引擎 — **P1**

- **发现**：`docs/index.md`（mkdocs 首页）写「218 绘图引擎」「版本 v1.1.0(41 项缺陷修复)」——当前 214 引擎 / v1.4.65。`docs/quickstart.md` 同样写 218。`docs/faq.md` 说「JRE 8+」而 README 说「JDK 11+ 必须（JRE 不够）」——两文档对同一问题给出**相反**答案。`docs/reference.md`/`docs/rpc.md` 各 5 行，是占位空壳。
- **挑战**：docs/ 是 mkdocs 站点源（mkdocs.yml 存在），即对外文档站。新用户从文档站首页读到 v1.1.0 + JRE 8，按 FAQ 装了 JRE 就会踩 bridge 编译失败的坑。README 与 docs 站是两套对外门面，只有 README 在维护。
- **建议**：docs/index.md/quickstart.md 数字改为指向 counts.md 或 README；FAQ 的 Java 要求与 README 统一为 JDK 11+；要么删掉 v1.1.0 版本自述改为「当前版本见 release 页」，要么纳入发布 checklist 同步项。reference.md/rpc.md 空壳要么补内容要么从 mkdocs nav 摘除。
- **严重度**：P1（对外文档站误导安装决策）

### F5. 无发布流程文档：四十七连发的步骤只存在于编年史惯性里 — **P1**

- **发现**：全仓库 grep「发布流程/发版/release 流程」零命中；CONTRIBUTING.md 只有质量门禁，无 release 章节。v1.4.19→65 的 commit/tag/render/push 步骤只能从总清单每波末尾「发布 vX（sha）」反推。F1/F2 两个 P0 的直接根因即此——没有 SOP 就没有 bump/CHANGELOG 步骤。
- **挑战**：单人项目可以靠记忆发版，但 (a) 编年史本身会换会话/换 Agent 接续，(b) 项目有 pip 包和 GitHub release badge，已是「对外发布」形态。新 Agent 接续时无法从仓库内任何文件得知「发版要做哪几步」。
- **建议**：新建 `docs/RELEASING.md`（或 CONTRIBUTING 加节），最小内容：① bump pyproject ② 跑三件套门禁 + gen_metadata --check ③ CHANGELOG 补节 ④ gen_metadata --render 同步 surface ⑤ commit/tag/push + GitHub release ⑥ 总清单波次记录。把 F1–F4 全部变成 checklist 条目。
- **严重度**：P1（流程缺失，是 P0 的根因）

### F6. 送审包「自包含」声称不实：引用仓库外路径 + 三文件拼接 — **P1**

- **发现**：SUBMISSION 头注「一份自包含，可直接送外部评审」，但：① §1 评审输入是 `docs/REVIEW_PACKAGE_115.md` 的另一文件（变更清单/门禁证据不在 SUBMISSION 内）；② REVIEW_PACKAGE_115.md 又引用「编年史：`workflows/tbtools_cli化_总清单.md`（第四十七/四十八波）」——该文件在 `~/.openclaw/workspace/workflows/`，**不在本仓库**，外部评审拿不到；③ SUBMISSION 快照 v1.4.62，而仓库已发 v1.4.65（env_fp 补全恰是 SUBMISSION §4 自问「meme/mast 外部二进制是否该入」的落地）——送审包发出时即过期，且过期内容正好是它自己提出的待审问题。
- **挑战**：「自包含」的含义应是「外部评审只读这一个文件即可审」。现状是要审全须读 3 个仓库内文件 + 1 个仓库外文件，且快照落后 3 版。另外 PREVIEW/SUBMISSION/PACKAGE 三文件命名近似（REVIEW_PACKAGE_115.md / _PREVIEW.md / _SUBMISSION.md），职责区分只写在各自头部，无索引。
- **建议**：SUBMISSION 改为真正单文件（内联变更清单摘要 + 门禁证据摘要 + 关键链接全部换成仓库内相对路径或 commit 链接）；发出前刷新快照到 HEAD；三文件关系在 docs/ 某索引页画一张流向图（输入 → 预审 → 响应闭环）。评审节奏上，v1.4.63–65 三笔要么补进 SUBMISSION 要么明确「下轮评审范围」。
- **严重度**：P1（评审材料可审性打折）

### F7. PLAN.md「唯一活 plan」快照过期 10 个版本，活文档不活 — **P2**

- **发现**：PLAN.md 快照「2026-10-04 22:45 · v1.4.55 · 最近波次 47 波」；实际 v1.4.65、波次到 51+（且 v1.4.63–65 三笔连总清单都没记，见 F8）。C 区「P1-4 D1 待下轮」实际已于 v1.4.61 落地。
- **挑战**：PLAN.md 自称「当前唯一活的进度 plan」，但快照字段无更新机制，靠的是人手记得改。它与总清单的分工（活 plan vs 编年史）在 PLAN 头部说清楚了——这点没问题——问题是「活」没有纪律保障，两天就过期。
- **建议**：快照区只保留**自动生成或必随 commit 更新**的字段（版本可从 tag 推导的就不手写）；或接受「快照有过期时间戳」并在头部注明「快照截至 X，之后见 git log」。C 区评审节奏表随每轮响应立即更新（v1.4.61 落地时就该勾掉 P1-4）。
- **严重度**：P2（内部文档时效性）

### F8. 编年史断更：v1.4.63–65 三笔发布无波次记录 — **P2**

- **发现**：总清单终于第五十一波（v1.4.62）；其后三笔 commit（d9349b1 SUBMISSION 合一 → 01a2862 CI skip 报告 → 0efa108 env_fp 补全，即 v1.4.63–65）无任何波次条目。env_fp 补全是 SUBMISSION §4 自问的实质响应，属于该入史的决策。
- **挑战**：编年史是项目的记忆载体（AGENTS.md 长期任务恢复协议依赖它），断更意味着下次接续问「env_fp 覆盖了哪些外部二进制」时无据可查，只能翻 git log——编年史的存在意义被架空。
- **建议**：补记第五十二波（v1.4.63–65）；并反思「发版必记波」是否也要进 RELEASING checklist（与 F5 合并）。
- **严重度**：P2（内部记忆断档）

### F9. 文档体系无索引/入口页：新 Agent 接续路径靠口口相传 — **P2**

- **发现**：docs/ 下 14 个 .md + _worklog/ 7 个 + adr/，**无 docs/README.md 或导航页**说明「现在做什么看 PLAN、历史看总清单、评审看 SUBMISSION、命令看 COMMAND_REFERENCE」。mkdocs 的 index.md 是面向用户的营销页，不面向维护者。PLAN.md 头部虽然声明了自己的地位，但一个新会话从仓库根进入时没有任何路标指向它（README 的 Documentation 表只列了 COMMAND_REFERENCE 和 rpc_methods_reference）。
- **挑战**：AGENTS.md 的「长期任务恢复协议」假定接续者知道去读 PLAN/总清单，但那是 workspace 侧纪律；仓库内自描述缺失。对外贡献者（CONTRIBUTING 的读者）也完全不知道 PLAN 的存在。
- **建议**：新建 `docs/README.md`（维护者导向索引：活 plan / 编年史位置 / 评审包流向 / 生成物 vs 手写物清单），README 的 Documentation 表加一行指向它。
- **严重度**：P2（可接续性）

---

## 最值得改的 3 点

1. **写 `docs/RELEASING.md` 并把 F1–F4 全变成 checklist 硬性条目**（bump pyproject / CHANGELOG 补节 / README+docs 数字同步 / tag 一致性校验）。两个 P0 的共同根因是「发版无 SOP」；门禁只防 generated surface，不防手写字段——checklist + gen_metadata --check 扩展到 pyproject/CHANGELOG/README 数字扫描可一次性堵住。
2. **一次性补齐版本叙事**：pyproject bump 到 1.4.65（或改 vcs 自动版本）、CHANGELOG 补录 1.4.47–65（可压缩为 3–4 个合并节）、总清单补第五十二波。让仓库内三个版本载体（pyproject/CHANGELOG/编年史）与 git tag 重归一致。
3. **送审包真自包含化 + 发前刷快照**：SUBMISSION 内联评审输入摘要，编年史引用换成仓库内可访问的形式（摘录或移入 docs/），快照对齐 HEAD；三文件（PACKAGE/PREVIEW/SUBMISSION）在 docs/README.md 里画清流向。否则下一轮外部评审仍会卡在「拿不到总清单」。
