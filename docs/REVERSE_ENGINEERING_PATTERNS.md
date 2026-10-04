# 逆向工程模式表（REVERSE_ENGINEERING_PATTERNS）

> 第三十二波 Compound Engineering 第②招「审查加模式归纳」落地件 — 2026-10-04
> 用法：每批修复/收编完成后，把**共性模式**（非单点坑）追加到本表；单点坑仍走 PITFALL_HINTS。
> 模式 = 同类工具反复出问题的根因 → 下次遇到先按模式验证，不必重新踩一遍。

## P1: 引擎文档/名称声称的格式 ≠ 实际解析格式 —— 反编译定格式再说

**实证**（2026-10-04 四连）：
| 工具 | 声称 | 实际（javap -c 验证） | 批次 |
|:--|:--|:--|:--|
| keggEnrich | .keg = KEGG FTP 层次 A/B/C/D | **扁平 5 列 tab 表**（split \t 直映射 Kterm 五字段） | 45 |
| gsea | query2go 任意 gene→term 映射 | **每基因一行逗号分隔**（否则 .gmt 空 → 0 集） | 43 |
| notung | 位置参数即可 | 带值 flag 众多，值会被当位置参数 → **显式 --out 约定** | 42 |
| efpHeat | class 名像"类.方法"不可调 | **generateSuperHeatMap 是独立类**，ArgsParser main 直调 | 40 |

**动作**：拿到生僻引擎先 `javap -c` 看解析逻辑（split/prepare 方法），一次定格式，别猜。

## P2: main() 有演示性硬编码 ≠ 引擎不可 CLI 化

**实证**：multiEfp（main 硬编码第二个矩阵路径 ExpressData1.txt）→ 绕 main 走 setter + 反射 private 初始化 + 核心方法（08/31 破解，10/04 重建桥成功）。
**判定**：凡有完整 setter + 核心方法（返回 JIGBasePanel/产物）均可绕 main。

## P3: 产物写派生名/工作目录 ≠ 产物丢失 —— impl 层搬运（kallisto 模式）

**实证**：Notung（`<gene>.reconciled` 派生名）、kallisto（abundance.tsv 在临时目录）。
**动作**：外部工具产物路径不受控时，impl 内 `--outputdir/--out 指定` + glob 搬运到 out 参数，测试天然通过。
**失败模式（评审 #115 预审 P2-6 补录）**：多产物/重名场景 glob 会扫错文件（`<gene>.*reconciled*` 匹配多个时取错）；
  搬运必须按 outputdir 白名单 + 主产物优先级，且搬运后校验内容语义（衔接 P1 内容断言）。

<!-- P4(时间戳≠契约内容)/P5(单源 census) 已于 2026-10-05 移出本文档——
    二者是管线/发布纪律而非逆向工程模式(评审 #115 预审 P2-6); 落点在
    docs/_worklog/PLAN.md 发布纪律区与总清单波次记录。 -->

## 模式证据强度标注

> 评审 #115 预审 P2-6 质疑「单例归纳成模式」成立——各模式标注证据计数与状态：
> - n≥2 = 模式（有跨案例支撑）；n=1 = hypothesis（经验级，待第二案例验证）

| 模式 | 证据计数 | 状态 |
|:--|:--|:--|
| P1 声称格式≠实际解析格式→javap | n=4（keggEnrich/gsea/notung/efpHeat） | ✅ 模式 |
| P2 main 硬编码→绕 setter+核心方法 | n=2（multiEfp 成功 / pafref 尝试失败实证缺陷） | ✅ 模式 |
| P3 产物派生名→impl 搬运 | n=2（Notung/kallisto） | ✅ 模式 |