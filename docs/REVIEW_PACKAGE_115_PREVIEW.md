# 评审 #115 预审轮意见（REVIEW_PACKAGE_115_PREVIEW）

> 评审人：独立外部预审（MOSS，批判性审查轮） · 2026-10-05
> 范围：v1.4.46 → v1.4.59（git log 实测 15 commit，评审包自称 14——包封面写 v1.4.58 止，ed27a6f 评审包自身 commit 未计入；口径不一致本身值得注意）
> 证据：REVIEW_PACKAGE_115.md / EXEC_VERIFIED_LEFTOVER.md / REVERSE_ENGINEERING_PATTERNS.md / 总清单第 37–48 波 / git show（f504b19, 86b6be9, 32ee6be）/ tests/test_conformance_verified.py 源码抽查

## 总体结论：有条件通过

90% 执行验证与三件套门禁的工程量真实可信，但**「EXECUTION_VERIFIED」标签的语义强度被三处系统性稀释**（D1 域外缺陷贴绿标、D2 时间戳冻结、断言只验 sha256 格式不验内容），且 D3 归档中至少 2 例与项目自己的 P2 模式自相矛盾——需在评审 #115 正轮前澄清或修正，不阻断合并但阻断「90% 收官」的最终定性。

---

## D1. peakanno/peaktss「数据平移 +1e6」是否算真验证

**发现（事实）**
- 引擎 GxFOverlapIndexer binSize=10000 对 bin0（坐标 <10000）记录匹配失效，平移实验（+9000 即全匹配）证实为引擎缺陷（总清单第 47 波）。
- 解法为示例数据坐标 +1e6，实测 3/3 peak 注释，收编后标 EXECUTION_VERIFIED；spec note 补了「bin0 避让」。
- 编年史自述「真实测序数据天然百万级，引擎设计假设即如此」。

**挑战（质疑）**
1. **「真实数据天然百万级」是可证伪的**：细菌基因组 1–5 Mb，前 10 kb 内的 peak/TSS 完全合法；病毒基因组、单 scaffold 注释、叶绿体/线粒体（~16 kb / ~150 kb）整体落在 bin0。这不是边角案例，是一整类真实数据域被验证覆盖排除后仍贴绿标。
2. **标签名不副实**：EXECUTION_VERIFIED 证明的是「引擎在坐标 ≥10000 的输入域内可执行」，而工具契约（contract inputs）并未声明该输入域限制。用户拿小坐标数据喂一个「已验证」工具，得到的是**静默空结果**（无报错、无命中），比直接失败更危险。
3. **验证方向反了**：正常做法是「数据不动、缺陷记录为 known-issue + xfail」，现在变成「数据迁就缺陷、缺陷隐身」。spec note 里的「bin0 避让」是文档级补救，但门禁没有任何一条断言会在未来引擎 JAR 修复后提示「现在可以测 bin0 了」——缺陷被永久埋入。
4. **3/3 注释的断言强度**：注释成功 ≠ 注释正确。编年史未证明 peak→gene 映射被逐一核对到预期基因（只提了「含负链 gene2」一个点）。

**建议（可执行）**
- 证据语义降级或加域标注：verification_report 条目增加 `domain_note: "verified for coords >= binSize(10000); bin0 engine defect documented"`，或新增证据级别（如 EXECUTION_VERIFIED_WITH_DOMAIN_LIMIT）。
- 在 contracts/tools/peakanno.yaml 加输入前置条件（min coordinate），impl 层对 <10000 坐标数据显式告警而非静默空跑。
- 增加一条 xfail/known-issue 测试固定 bin0 缺陷，JAR 升级后自动翻红提示复测。
- 补一条映射正确性断言（peak1→gene1 等逐条比对），不止计数。

**严重度：P1**（标签失真 + 静默错误路径，但未虚构数据、缺陷有实证，不到 P0）

---

## D2. verified_at 冻结 + --check 结构化忽略

**发现（事实）**
- f504b19：verified_at 仅在 contract_fp 变化时刷新；gen_metadata --check 对 JSON 递归忽略 verified_at。
- contract_fp 覆盖 inputs/outputs/参数全字段（评审包自述）。

**挑战（质疑）**
1. **contract_fp 是否含引擎侧指纹？** 评审包与 commit message 均未证明 fp 覆盖 TBtools JAR 哈希、kallisto ELF 二进制哈希、桥源码哈希。若不含，则「换了引擎 JAR、契约没变」时 verified_at 保留旧时间戳——**证据链声称的验证时间指向一个已经不存在的引擎**。这是本设计最大的洞，评审包对此零论证。
2. **双端叠加 = 新鲜度信号彻底死亡**：生成端冻结 + check 端忽略，单独看各自合理，合起来意味着 verified_at 不再有任何消费者——一个没人读的字段为什么还要维护？更危险的是它仍在 report 里展示，给读者造成「有新鲜度信息」的错觉。
3. **无 TTL 机制**：没有任何「验证超过 N 天需复跑」的告警。契约三年不变，验证时间戳就冻结三年，期间 Python 版本、JRE 版本、依赖库全变了——「环境差异属 CI 层职责」的回应回避了问题：CI 跑的是 pytest，pytest 里这 54 条断言的数据/引擎若变坏，没有任何机制把 verified_at 与「最近一次真实通过」对齐。
4. 修复动机是「消除恒定假阳性」，但假阳性的另一种修法是让 verified_at 不进 ai/ 投影（本就不该投影易变元数据）。选择冻结语义是更重的方案，评审包未论证为何弃轻取重。

**建议（可执行）**
- 把引擎指纹（JAR sha256 / 外部二进制 sha256 / 桥源码 hash）纳入 contract_fp 或并列的 env_fp，引擎变化即触发 verified_at 刷新——这是最小改动堵最大洞。
- 给 verified_at 加软 TTL（如 >90 天在 --check 输出 WARNING，不 fail），保留信号但不扰门禁。
- 明确文档化 verified_at 的语义与消费者，或干脆从投影面移除。

**严重度：P1**（引擎指纹问题若坐实，证据链失真为实质问题；其余为 P2 级设计瑕疵，合并按 P1 计）

---

## D3. 剩余 6 归档判定

**发现（事实）**
- 4 引擎缺陷（pafref NPE / tfbsShift blastp 误判 / microsyn 格式 / memerun 缺类）+ 2 外部依赖（smart 联网 / gxfIdAppender RPC 8765），各附根因、波次证据、复攻条件。

**挑战（质疑）**
1. **pafref 与自家 P2 模式自相矛盾**：模式表 P2 说「凡有完整 setter + 核心方法均可绕 main」，multiEfp 正是靠 setter+反射破解硬编码。而 pafref 的 NPE 是「paint 前 this.text 状态缺失」——这恰恰是「绕 main、按正确顺序调 setter 初始化状态」可能解决的形态。证据里看不到对 pafref 做过 P2 式 setter 序列尝试（只验了 PAF 数据格式）。**模式归纳了却不应用于存量归档，模式表的可信度本身受质疑**（与 D4 联动）。
2. **tfbsShift「状态码逻辑反」未试 shim 绕过**：若 blastp 实际成功而引擎误判，一个包退出码/stderr 的 wrapper 脚本替换 blastp 路径是常规绕过手段。编年史未见尝试记录。归档过早。
3. **microsyn 分类错误**：复攻条件写的是「需上游修 JAR **或真实 MCScanX 数据**」——后者说明这不是引擎缺陷，是「合成数据造不出来」，与本轮收编的 10 个工具（全是合成数据攻坚成功）属同一类问题，只是更难。把它放进「引擎缺陷 4」桶里，人为把「不可解」从 2 吹成 4，90% 收官的叙事因此显得更干净。**这是定性口径问题，直接影响「剩余 6 全为硬障碍」的结论。**
4. **smart 与其他联网工具口径不一**：seqfetch 类联网工具未归档（或有通道），SMART「无 API 封装」即归档——但未论证是否试过 SMART 的批量下载/本地库（SMART 提供可下载数据库），「复攻条件：本地 SMART DB」其实已经承认了非硬障碍。
5. **gxfIdAppender 复攻条件不可操作**：「RPC 服务层提供独立入口」——谁提供？本项目起 RPC 服务做测试夹具是可行的（8765 本地起服务），把架构改造全推给上游不算复攻条件，算放弃声明。

**建议（可执行）**
- pafref/tfbsShift：各补一次「P2 模式 / shim 绕过」的最小尝试并记录结果，失败再归档不迟；已归档则在 LEFTOVER 注明「未尝试 setter/shim 路径」。
- microsyn 从「引擎缺陷」改类为「数据合成未攻克」，与其他 10 个收编工具同口径；相应调整「硬障碍 6」的表述。
- smart/gxfIdAppender：复攻条件改写为本项目侧可执行动作（本地 SMART DB 下载脚本 / 测试夹具起 8765 mock 服务）。
- 在 LEFTOVER.md 顶部注明归档判定的尝试清单（试过什么、没试什么），让「已定性」可审计。

**严重度：P1**（microsyn 误分类 + pafref/tfbsShift 与 P2 矛盾，影响 90% 收官定性的真实性）

---

## D4. 模式表 P1–P5 归纳质量

**发现（事实）**
- P1（声称格式≠实际格式→javap）4 例实证；P2（main 硬编码可绕）1 例；P3（产物派生名→impl 搬运）2 例；P4（时间戳≠契约内容）1 例；P5（单源 census）1 例。

**挑战（质疑）**
1. **样本量与泛化不匹配**：P2/P4/P5 均单例归纳成「模式」。单例是经验，不是模式——P4/P5 更是项目内部管线纪律（元数据对比、census 单源），与「逆向工程」这一文档主题不符，**分类错误稀释了 P1–P3 的检索价值**。
2. **P3 未记录失败模式**：impl 层 glob 搬运在多产物/重名场景会扫错文件；kallisto/notung 都是单产物或可控 outputdir 的顺利案例。模式表只记成功形态，是幸存者偏差。
3. **P1 的 4 例全部出自 10/04 同一天同一批攻坚**——时间局部性强，是否「反复出问题的共性模式」需要跨批次证据，目前更像「本批次的四个坑」。
4. **最大问题：模式表未反向应用于归档存量**（见 D3-1）。一个归纳了 P2 却不拿去复查 pafref 的模式表，说明它目前是「总结文档」而非「工作协议」，与文档自述的用法（「下次遇到先按模式验证」）不符。

**建议（可执行）**
- P4/P5 移出本文档，并入管线/发布纪律文档；本文档聚焦真·逆向工程模式。
- 每条模式标注证据计数（n=1/n=2/n=4）与「未证伪但样本不足」状态，n=1 降级为 hypothesis。
- P3 补失败模式段（多产物 glob 风险）。
- 用 P2 复查 pafref/memerun（D3），把模式表从总结变成协议。

**严重度：P2**（归纳质量与归类问题，不阻断；但与 D3 联动的那条升为 P1 论据）

---

## 额外自由项

### E1. 数据合成策略（seed 固定可复现是否足够）
- **发现**：10 个收编工具全部使用 seed 固定合成数据（kallisto seed=42、gsea seed=7、plotrna seed=11 等），数据落库 examples/data/exec/。
- **挑战**：**循环验证风险**——数据是为「让引擎通过」而造的（keggEnrich 造 11 K term、barplotter 造 3 列 gff），验证的是「引擎接受我们按它的期望造的数据」，不是「工具能处理用户数据」。seed 固定解决的是可复现性，不解决代表性。多数工具缺「负例/边界例」断言（空输入、畸形行、大坐标与小坐标混合）。
- **建议**：每个 EXEC_VERIFIED 条目至少补一条语义断言（如 keggEnrich 已做的 p 值核对——这是全场最好的样板，应推广为必须项）；补 1–2 条负例测试。
- **严重度：P1**

### E2. EXEC_VERIFIED 断言强度（exit 0 + 非空 + sha256）
- **发现**（test_conformance_verified.py 源码实测）：`assert d["exit_code"]==0`；`assert real`（存在非空产物）；`assert all(len(a["sha256"])==64 ...)`——**断言的是 sha256 字段存在且为 64 位 hex，不是产物内容与黄金哈希一致**。
- **挑战**：这意味着产物内容完全不受约束——引擎输出任何非空垃圾（错误页、全零文件、日志而非数据）都通过。注释/编年史里的「sha256 完整」措辞（评审包亦沿用）具有误导性，读包人会以为是黄金哈希比对。加上 E1 的数据迁就，EXECUTION_VERIFIED 的实际语义接近「EXECUTION_RAN」。
- **建议**：①对确定性产物（seed 固定的合成数据理应产出确定性结果，SVG/PDF 时间戳字段除外）加黄金哈希或结构断言（SVG 元素数、tsv 列数/关键值）；②至少把报告字段改名（如 artifact_nonempty_sha256_recorded）消除「完整=正确」的误读；③语义断言与 E1 合并处理。
- **严重度：P1**

### E3. mypy 门禁 disable_error_code 是否放水
- **发现**：pyproject 全局 `disable_error_code=['import-untyped']`；cli_load 2 处定点 type ignore；mypy 覆盖 25 files。
- **挑战**：①全局禁用 import-untyped 不只豁免 yaml——未来新增任何无 stub 依赖的 import 错误都被静默，放水半径随时间扩大；应改 per-module override（`[[tool.mypy.overrides]] module="yaml.*"`）。②「mypy 0（25 files）」覆盖面未含 tests/ 与 scripts/（gen_metadata.py 恰是本轮改动核心却疑似不在门禁内——需核实 exclude 配置），门禁数字的覆盖声明不完整。③monkey-patch click 用 type ignore[method-assign] 是正当豁免，无异议。
- **建议**：import-untyped 收窄到 per-module；确认并文档化 mypy 的文件覆盖清单（为何 25），把 scripts/gen_metadata.py 纳入。
- **严重度：P2**

### E4.（附加发现）门禁数字的可移植性
- **发现**：pytest 619 passed 中 52 skipped =「缺数据 execution」。即在不落库数据的环境（干净 CI clone？），54 条执行断言会全部 skip，90% 无法被第三方复算。
- **挑战**：评审包声称门禁可独立审计，但执行验证恰恰是 skip 掉的部分。「pytest 619 passed」与「54 EXECUTION_VERIFIED」并存于同一门禁记录，未说明在何种环境下 54 条真实跑过。
- **建议**：门禁记录注明「54 条执行断言在含 examples/data 的环境实跑通过」；CI 增加一个不 skip 的 job 或显式报告 skip 清单。
- **严重度：P2**

---

## P0/P1 问题清单汇总

| # | 项 | 问题 | 严重度 |
|:--|:--|:--|:--|
| — | （无 P0） | 未发现虚构证据或门禁造假；工程量真实 | — |
| 1 | D1 | EXECUTION_VERIFIED 标签未限定输入域，bin0 缺陷被数据平移掩盖且无复测触发器 | P1 |
| 2 | D2 | contract_fp 未含引擎/JAR 指纹（未证），verified_at 冻结+忽略双叠加杀死新鲜度信号 | P1 |
| 3 | D3 | microsyn 误分类为引擎缺陷（实为数据合成未攻克）；pafref/tfbsShift 未试 P2/shim 路径即归档，与自家模式表矛盾 | P1 |
| 4 | D4+D3 | 模式表 P2 归纳后不反向应用于存量归档，模式表定位（总结 vs 协议）不清 | P1（论据并入 D3） |
| 5 | E1/E2 | 断言强度不足：sha256 只验格式不验内容，缺语义断言；合成数据循环验证风险 | P1 |
| 6 | D4 | P4/P5 分类错误、n=1 归纳、P3 幸存者偏差 | P2 |
| 7 | E3 | import-untyped 全局禁用半径过大；mypy 覆盖 25 files 口径不明 | P2 |
| 8 | E4 | 52 skipped 使 90% 不可被第三方环境复算 | P2 |

**P0：0 · P1：5 · P2：3**

---

## 给实现方的回复建议

**必须改（P1，建议评审 #115 正轮前响应）**
1. **E2+ E1 断言升级**：至少为确定性产物加内容级断言（黄金哈希或结构断言），并修正「sha256 完整」的误导措辞。这是性价比最高的一处——直接提升全部 54 条验证的可信度。
2. **D2 引擎指纹入 fp**：把 JAR/外部二进制 sha256 纳入 contract_fp（或并列 env_fp），堵住「换引擎后 verified_at 说谎」的洞。
3. **D3 重分类与补试**：microsyn 改类「数据合成未攻克」；pafref 补一次 P2 式 setter 尝试（或 LEFTOVER 注明未试）；「硬障碍 6」表述相应修正。

**可辩护（回应即可，不必改代码）**
- D1 的数据平移本身可辩护（真实 MACS2 场景确实百万级、spec note 早有声明），但需补域标注/前置告警，把「静默空结果」路径堵掉即可，不必撤销收编。
- verified_at 冻结的「证据语义」论证成立（契约版本何时通过验证），可保留该语义，只需补 env 维度和 TTL 告警。
- D4 模式表 P1 的四连实证扎实，可辩护；只需承认 P2/P4/P5 样本量并重分类。
- E3 的两处 click type ignore 属正当豁免，可辩护。

**明确反对的辩护（若实现方提出，不接受）**
- 「真实数据天然百万级所以 bin0 无所谓」——见 D1-1，病毒/细胞器/scaffold 数据域整体被排除。
- 「环境差异属 CI 层职责」——CI 跑的是同一套 pytest，没有独立环境验证层，此回应是循环论证。
- 「剩余 6 全为硬障碍」——microsyn 与 smart 的复攻条件自述已承认非纯硬障碍。
