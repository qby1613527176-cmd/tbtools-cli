# 执行验证/数据 视角自审（verified_review.md）

> 2026-10-05 · 独立批判性审查 v1.4.65 · 聚焦评审 #115 预审已响应项（语义断言/引擎指纹/归档判定/域标注）**之外**的新问题
> 审查范围：test_conformance_verified.py / EXEC_VERIFIED_LEFTOVER.md / REVERSE_ENGINEERING_PATTERNS.md / examples/data/exec/ / verification_report.json
> 立场：找问题，不称赞。

## 总体结论

**不通过（有条件）**。EXEC_VERIFIED 体系的"骨架"（编译契约 + 真实执行 + 产物非空 + 指纹绑定）成立，但两处实质性漏洞使"VERIFIED"标签超卖：

1. **xfail 翻红机制实际不存在**（F1，P1）：`test_bin0_defect_xfail` 用命令式 `pytest.xfail()` 在 assert **之前**无条件抛出，其后 `assert real` 是死代码。无论 JAR 是否修复，该测试永远 xfail，**不可能 xpass**——文档与注释声称的"JAR 修复后自动 xpass 翻红提示复测"是假承诺。bin0 缺陷只是换了一种隐身方式。
2. **54 个 EXECUTION_VERIFIED 中仅 10 个有内容断言**（F2，P1）：其余 44 个的验证强度仍是"EXECUTION_RAN"（非空 + sha256 格式正确），而 verification_report.json 对二者不加区分地统一标 `EXECUTION_VERIFIED`。评审 #115 响应只覆盖了 19%，标签语义与证据强度不匹配的问题没有被解决，只是被部分缓解。

无 P0（不影响库本身正确性，属测试/证据基础设施问题）。P1×2，P2×7。

---

## 逐项发现

### F1. xfail 测试的翻红机制是死代码 —— P1

**发现**：`test_bin0_defect_xfail` 中 `pytest.xfail(reason=...)` 位于 `assert real` **之前**。命令式 `pytest.xfail()` 调用即抛出（imperative xfail），测试在此点终止并记 xfail；其后的 assert 永不执行。

**挑战**：注释与 LEFTOVER 叙事均声称"JAR 修复后此断言 xpass 翻红提示复测"——这是假的。JAR 修复后该测试依然 xfail（绿），缺陷修复无人知晓；反之若明天有人"修复"了缺陷但引入了新的静默失败模式，同样无信号。维护成本不是"低成本固定缺陷"，而是"永久性误文档"。

**建议**：改为声明式条件 xfail，让 assert 真正执行：
```python
@pytest.mark.xfail(reason="GxFOverlapIndexer bin0 缺陷(v1.4.57)", strict=False)
def test_bin0_defect_xfail(...):
    ...
    assert real  # 修复后产出非空 → XPASS(strict=False 不报错但报告 xpassed)
```
或保留命令式但放在**结果分支**上：`if not real: pytest.xfail(...)`，修复路径走正常 pass。同时把 `strict=True` 纳入讨论（修复后强制翻红 fail，必须人工摘除标记——比 xpass 静默更强的复测提醒）。

**严重度**：P1（证据完整性：声称的保护机制不存在）

---

### F2. 语义断言覆盖率 10/54，标签超卖 —— P1

**发现**：SEMANTIC_CHECKS 仅 10 条；44 个工具仍只验"非空 + sha256 是 64 hex"。且 10 条中断言强度参差：

- **内容级（真语义）**：keggEnrich（通路名+p 值）、kallisto（行数+TX1+表头）、peakanno（基因名齐）、notung（节点标记）。
- **结构级（计数代理）**：efpHeat/multiEfp（rect≥100 + 尺寸窗口）、peaktss（rect/line 计数）。
- **格式级（魔数+尺寸）**：barplotter（PNG 魔数 + 5–30KB）、plotrna（PDF 魔数 + 20–120KB）——这两条**不含任何内容信息**，垃圾内容但尺寸恰在窗口内照样通过；"语义断言"名不副实。

另有三个具体弱点：
- `any(...)` 语义：多产物工具只要**任一**产物过断言即通过，其余产物可以是垃圾（P3 模式已记录 glob 搬运扫错文件的失败模式，语义断言恰恰没防住它）。
- `peakanno` 检查 gene1/2/3 **字符串存在**即可——注释错配（peak 挂错基因）但三个基因名都在文件里照样通过；"含负链"在 desc 里声称，断言里没验。
- `keggEnrich` 的 `"E-4" in text` 子串匹配：`1E-40` 也含 `"E-4"`（方向侥幸无害），但与"Glycolysis"的匹配未限定同行——通路名出现在第 3 列、E-4 出现在别处行也过。

**挑战**：预审响应把 keggEnrich 定为"样板推广为必须项"，实际推广率 19%。verification_report.json 的 `verified_tools` 对有/无内容断言的工具不做分级，下游消费者无法区分"验过内容"和"只验过跑过"。

**建议**：① verified_tools 增加 `semantic_checked: bool` 字段，让标签可区分；② barplotter/plotrna 至少加一条内容断言（PNG 有 tEXt/iTXt 之外的像素区非纯色判定过重——退而求其次：plotrna 可验 PDF 页面对象含 coverage 数值文本抽取；barplotter 可改输出 SVG 变体验元素）；③ peakanno 断言升级为"peak→最近基因"映射正确（含 gene2 负链的具体行匹配）；④ `any()` 改 `all()` 或主产物定向断言。

**严重度**：P1（证据强度与标签不符）

---

### F3. 尺寸窗口断言的跨环境脆弱性 —— P2

**发现**：efpHeat(30–50KB)、multiEfp(25–60KB)、barplotter(5–30KB)、plotrna(20–120KB) 用绝对字节窗口。SVG/PDF/PNG 体积受字体解析、JRE 版本、栅格 DPI、时间戳元数据影响——注释自承"SVG/PDF 时间戳字段除外"，即承认非确定，却用确定性窗口断言。

**挑战**：换 JRE/换字体环境，真阳性内容也可能掉出窗口 → 假失败；窗口放宽又退化为近乎无约束。这类断言的"确定性"前提不成立。

**建议**：尺寸窗口降级为 sanity 下限（>1KB 非空增强版），语义部分换结构性内容断言（SVG 特定 path/rect 的坐标或颜色值抽样；PDF 抽取文本含区域坐标 "chr1:1-1000"）。

**严重度**：P2

---

### F4. examples/data/exec/ 无文档、无生成器、混入引擎中间产物 —— P2

**发现**：
- 目录无 README，无逐文件来源说明；"seed 固定可复现"在测试注释中声称，但**仓库内没有生成脚本**（只有 meme.xml DTD 里有个无关 `<seed>0</seed>`）——合成数据如何造、seed 是多少，只存在于 worklog 记忆里，换人无从复现/扩展。
- 混入引擎运行中间产物：`plotrna/reads.sam.sorted.sam`、`reads.sam.sorted.sam.sorted.sam.sai`、`genome.fa.TBtools.fa`(+`.fai`)——命名链（`.sorted.sam.sorted.sam.sai`）明显是引擎自动派生，被一并提交。是输入还是产物？无文档无法区分，后续清理易误删或误导。
- 数据自洽性瑕疵：`peak/peaks.xls` 的 `length` 列三行全为 `1000300`（与 start/end 差 300 不符，高坐标批量改数的复制残留）——引擎可能不读该列所以不炸，但作为"权威合成数据"自相矛盾。
- 负例/边界例：除 peak 低坐标外，54 个工具无任何畸形输入/空输入/超大输入用例——但这与 LEFTOVER 的边界覆盖哲学一致（缺陷固定而非穷举），判 P2 不升级。

**建议**：① 加 `examples/data/exec/README.md`：逐目录来源（合成方法/seed/生成命令）、哪些是引擎中间产物；② 生成脚本入库（`scripts/gen_exec_data/`）或至少在 README 记录一次性生成命令；③ 引擎中间产物移入子目录 `plotrna/_engine_cache/` 或 .gitignore 排除（若测试真需要则 README 注明）；④ 修正 peaks.xls length 列。

**严重度**：P2

---

### F5. test_report_counts 无回归下限 —— P2

**发现**：收尾断言只有 `len(FULL_TOOLS) >= 50`。`exec_ok` 只是 print 不 assert——删 10 个数据文件，测试照样绿，EXEC_VERIFIED 名存实亡。

**建议**：`assert len(exec_ok) == len(EXEC_VERIFIED)`（数据缺失即红），或至少 `>= 54` 硬下限防倒退。

**严重度**：P2

---

### F6. provenance glob 检查是死代码 —— P2

**发现**：`_has_any_prov` 两段计算（含 glob 宽容匹配）的结果**从未被使用**——既不 assert 也不 log。注释解释"缺失不失败"，那这段计算连信息价值都没有（测试输出里看不到哪些工具缺 provenance）。

**建议**：要么删，要么改成 `warnings.warn`/计数汇总 print，让"哪些工具无 provenance"可见。

**严重度**：P2

---

### F7. LEFTOVER 复攻条件可操作性不足；microsyn 改类后有残留口径 —— P2

**发现**：
- 6 条复攻条件中 4 条（pafref/tfbsShift/memerun 等"需上游修 JAR"）**无触发机制**——JAR 版本无跟踪（env_fingerprint 只在测试跑时记录，无人比对 JAR 升级事件），"复攻条件"是静态愿望而非可操作流程。正确做法已有先例却不引用：bin0 用 xfail 固定缺陷，pafref 的 NPE 完全可同法固定（执行→断言 NPE→xfail），让 JAR 升级自动产生信号。三条引擎缺陷归档后**没有任何活测试盯着**，与 bin0 的处理不一致——这是真正的不自洽。
- microsyn 改类为"数据合成未攻克"后，与本轮 10 个收编工具同类的表述成立，但收编工具都有测试守着，microsyn 归档后无测试、无数据占位、无生成器雏形——"同类"只停留在定性表上。
- gxfIdAppender 的"RPC 8765 架构改造"无任何 issue/计划锚点，等于无限期挂起。

**建议**：① 三条 JAR 缺陷各补一个 xfail 固定测试（模式照抄 bin0，顺带验证修复后翻绿路径——与 F1 修复联动）；② LEFTOVER 表加"活监控"列（有测试盯着 / 纯文档归档）；③ microsyn 若认"数据合成"类，至少留一个 skipped 的生成器占位测试。

**严重度**：P2

---

### F8. "90% 收官"叙事的分母与金链空心化 —— P2

**发现**：54/60=90% 的分母含 6 个已定性不可执行工具；若按"可执行工具"口径即 100%,"90% 收官"反而**低报了**——叙事选择了更显进程感的口径，属包装瑕疵而非造假。更实质的问题：三层验证的顶层 CONFORMANCE_VERIFIED 自评审 #110 设立至今**只有 volcano 1 个**，金链升级路径（产物语义+sha256+provenance+artifact_id 全验）无推广计划、无第二批候选——"三层体系"实际是两层的，顶层是展品。

**建议**：要么给金链定推广路线（下批 5 个候选+时间表），要么在报告中明示"CONFORMANCE_VERIFIED 为试验层（n=1）"，避免三层叙事超卖。

**严重度**：P2

---

### F9. verification_report.json 由测试副作用写出 + 文件句柄未关 —— P2

**发现**：`_jr.dump(_report, open(..., "w"))` 句柄永不关闭（CPython 靠 GC 兜底，PyPy/嵌入式解释器下可能写不全）；且报告只在 Tier1 测试跑时刷新——单独跑 Tier2（integration 标记）后报告是陈旧的，但 verified_at 语义（"该契约版本何时通过验证"）恰由该文件承载，运行组合影响证据新鲜度却没有说明。

**建议**：`with open(...) as f: json.dump(...)`；在 PLAN/发布纪律区注明"报告权威来源 = 全量 conformance 运行"。

**严重度**：P2

---

## 最值得改的 3 点

1. **F1 修 xfail 翻红**（P1，半小时工作量）：`pytest.xfail()` 移到结果分支或改声明式 xfail——否则"缺陷固定"是个永远不响的闹钟，且此模式正要推广到 F7 的三条 JAR 缺陷，错模板复制三份。
2. **F2 给 verified_tools 加 `semantic_checked` 分级 + 消灭魔数尺寸伪语义**（P1）：让 54 个 EXECUTION_VERIFIED 中"验过内容"的 10 个与"只验过跑过"的 44 个在机器可读层可区分——这是标签诚实性的最低成本修复。
3. **F7+F4 数据/归档的"活化"**（P2，联动）：三条 JAR 缺陷补 xfail 固定测试、exec/ 补 README+生成器说明、test_report_counts 加 `== len(EXEC_VERIFIED)` 下限——把"归档不遗忘、数据可复现"从叙事变成机制。
