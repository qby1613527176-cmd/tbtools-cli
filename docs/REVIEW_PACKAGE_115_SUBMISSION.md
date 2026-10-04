# 评审 #115 送审包（SUBMISSION：输入 + 预审 + 响应闭环）

> 2026-10-05 · v1.4.62 · 一份自包含，可直接送外部评审（WorkBuddy/GPT/GLM/基础设施视角）
> 结构：① 评审输入（REVIEW_PACKAGE_115.md 全文见下节指引）② 独立预审意见 ③ 响应记录（4/4 P1 + 3/3 P2 已落地）

## 0. 快照（v1.4.62）

- 执行验证 **54/60 = 90%**（v1.4.27 的 7% 起，连续收编 17 个）；剩余 6 归档（EXEC_VERIFIED_LEFTOVER.md）
- 门禁 pytest 619 passed + 2 xfailed / ruff 0 / mypy 0（三件套本地齐跑）
- v1.4.19→v1.4.62 四十三连发

## 1. 评审输入

原包 `docs/REVIEW_PACKAGE_115.md`：变更清单（v1.4.46→59 共 15 commit）+ 待审决策 D1-D4 + 门禁证据 + AST 压缩版代码阅读提示（`docs/_generated/*.min.py`）。

## 2. 独立预审意见（本包自带的评审轮）

`docs/REVIEW_PACKAGE_115_PREVIEW.md`——独立视角批判性审查，**有条件通过（P0:0 / P1:5 / P2:3）**。核心质疑：
1. E2/E1：sha256 只验 64hex 格式 = EXECUTION_RAN 非 VERIFIED；合成数据循环验证
2. D2：contract_fp 未含引擎指纹——换 JAR verified_at 指向不存在的引擎
3. D3：pafref 未试 P2 路径即归档；microsyn 误分类为引擎缺陷
4. D1：bin0 缺陷被数据平移掩盖且无复测触发器；"真实数据天然百万级"可证伪
5. D4：模式表 P4/P5 分类错误、单例归纳成模式

## 3. 响应记录（预审后三连发，8/8 项已落地）

| 预审项 | 响应 | commit |
|:--|:--|:--|
| P1-1 E2/E1 断言强度 | SEMANTIC_CHECKS 10 工具内容级断言（keggEnrich p 值样板推广）+ "sha256 完整"措辞修正 | d4ed53a（v1.4.60） |
| P1-3 D3 归档判定 | pafref setter 补试 NPE 复现（引擎缺陷确凿）；microsyn 改类"数据合成未攻克" | 15b9902（v1.4.60） |
| P1-2 D2 引擎指纹 | env_fp（JAR+二进制 sha256 并列 contract_fp）；verified_at 双条件刷新；>90 天 TTL 软告警 | 86e4d41（v1.4.60） |
| P1-4 D1 域标注 | bin0 缺陷 xfail 固定测试（JAR 修复后 xpass 翻红）+ report domain_note + 负链断言加强 | bddfaa4（v1.4.61） |
| P2-6 D4 模式表 | P4/P5 移出 + 证据计数（n=2/2/4）+ P3 失败模式段 | 7a94715（v1.4.62） |
| P2-7 E3 mypy | import-untyped 全局→per-module（tbtools_cli.*） | 7a94715（v1.4.62） |
| P2-8 E4 skip 口径 | PLAN 注明"54 断言需含 examples/data 环境实跑；clean clone 52 skipped 不可复算" | 7a94715（v1.4.62） |

### 响应后的关键变化（对评审者的自证）
- **EXECUTION_VERIFIED 语义**：从"exit 0 + 非空 + sha256 格式"提升到"内容级语义断言"（10/10 收编工具）；证据含 env_fp（引擎本体）+ domain_note（输入域限定）+ verified_at（双条件新鲜度）
- **归档判定可审计**：pafref 的 setter 尝试记录在案；microsyn 归类修正
- **bin0 缺陷不再隐身**：xfail 固定 + 域标注，JAR 升级自动翻红
- **mypy 门禁口径**：豁免收窄 per-module，覆盖范围 25 files（tbtools_cli/）

## 4. 请外部评审聚焦

1. 响应是否充分（尤其 D1 平移绕过是否还需更硬处理）
2. env_fp 覆盖的引擎清单是否够（JAR/kallisto/Notung/GSEA——遗漏的引擎类：meme/mast 外部二进制是否该入）
3. SEMANTIC_CHECKS 的断言强度是否足够（结构性 vs 语义性）
4. 下一步方向（CI skip 修复 / 执行验证 100% 是否值得 / 评审节奏）