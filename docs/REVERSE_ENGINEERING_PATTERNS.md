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

## P4: 时间戳/元数据 ≠ 契约内容 —— 门禁对比要区分

**实证**：verified_at 每次测试刷新 → ai/tools 漂移恒定假阳性（v1.4.47 双端修复：生成端 fp 未变保鲜、check 端结构化忽略）。
**动作**：freshness 门禁对比时，把"何时验证"与"验证了什么"分离。

## P5: README/help 里 README.md 计数 ≠ 运行时口径 —— 单源 census

**实证**：v1.4.34 P0-3 后 verification 数字统一 census 单源；收编新工具必须 `gen_metadata --render` 全视图原子同步。
**动作**：收编/改 spec 后发布流程必跑 render（v1.4.47/48 曾漏跑致 ai/ 时间戳滞后）。