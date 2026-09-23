# 飞纪盘 64 插件 CLI 化评估(2026-09-23)

> 来源:`scripts/feijipan/feijipan_index.json`(64 分享 79 个 .plugin,~7GB)。
> 评估维度:CLI 化可行性(是否 headless 可跑/是否需 GUI/R 生态)/价值/工作量。

## 总览

| 类别 | 数量 | CLI 化结论 |
|---|---|---|
| **R/Shiny 生态插件** | 20 | ❌ 不属 CLI 化范围(TBtools-R Plugin 体系,需 Rserver + R 环境;与 Java 引擎 CLI 化是两条路线) |
| **Java/外部工具包装** | 44 | 🟡 可评估,按价值分级(见下) |

---

## 🥇 P0 高价值候选(建议优先,~6 个)

| 插件 | 功能 | CLI 化可行性 | 估计 |
|---|---|---|---|
| **P00321-Diamond GUI Wrapper** | Diamond 序列比对(插件自带 diamond 二进制) | ✅ 高(插件 bin/diamond 直接调;类似现有 quickAnno) | 1 天 |
| **P00331-mafft GUI Wrapper** | MAFFT 多序列比对 | ✅ 高(mafft 引擎调用,与 muscle 同级) | 1 天 |
| **P00620-MACS2 GUI Wrapper CallPeaks** | ChIP-seq 峰值调用 | 🟡 中(MACS2 是 Python 包,包装层薄) | 1-2 天 |
| **P00341-Root a PhyloTree** | 系统发育树定根 | ✅ 高(纯计算,类似 treeRooting) | 0.5 天 |
| **P00641-SuperDecode** | 突变分析工具包 | 🟡 中(多功能整合,需拆解) | 2 天 |
| **P00383-GenomeSyn_tool** | 基因组共线性 | 🟡 中(与 mcscanx 重叠?) | 1 天 |

## 🥈 P1 中价值(~8 个)

- **P00382-Mummer**(基因组比对,与现有重叠度?)
- **P00381-RepeatMaskandStatistics**(重复序列统计)
- **P00230-BEDtools Intersect**(⚠️ Win only,Linux 受限)
- **P00140-Sample Distance**(样本距离热图,与现有 pca/heatmap 重叠)
- **P00514-PanCoreDistribution**(核心/可变基因趋势)
- **P00213-GeneWindowCounter**(基因密度窗口)
- **P00481-Batch Protein Paramters Calc**(蛋白参数批量)
- **P00639-Crispr Stitch**(CRISPR 效率评估)

## 🥉 P2 低价值/特殊(~10 个)

- **P00312/P00360-Aspera**(数据下载,与 seqfetch 重叠)
- **P00440-Youtube Download / P00491-PPTX to Image PDF / P00500-QRcode / P00520-Batch Paper Fetch**(非生信核心)
- **P00313-Rapid Gene Family**(基因家族初筛,与现有重叠)
- **P00271-Quick Interval Gene Anno**(区间基因注释)
- **P00061-63 quickGenome/Fasta_Statistic**(统计,与 statFasta 重叠)

## ❌ 明确不做(R/Shiny 20 个 + Win-only 1 个 + 重复 ~5 个)

- R/Shiny 20 个(Rserver 生态,不属于 Java 引擎 CLI 化范畴)
- P00630 Ranbow(Win only)
- 与现有命令高度重叠的(quickGenome/statFasta/Aspera/Sample Distance 等)

---

## 建议路径

**若做 P0 6 个**:
1. 先用现有解析器(feijipan_resolver.py)下载对应 .plugin(需真实浏览器——resolver 已记录下载走浏览器按钮)
2. 逐个解包(plugins/ 结构:lib 引擎 jar + bin 二进制 + src 原始)
3. 参考现有 12 插件 CLI 化模式(plugins/README + COMMAND_REFERENCE 插件节)
4. 每个插件:解包 → 引擎逆向(CFR) → CLI 包装 → 真实数据验证 → 注册 CommandSpec

**工作量估计**:P0 6 个 ≈ 5-7 天(Diamond/mafft/Root 各 1 天,MACS2/SuperDecode/GenomeSyn 各 1-2 天)。

**决策点**:是否启动?P0 6 个价值排序:Diamond > mafft > Root-a-PhyloTree > MACS2 > SuperDecode > GenomeSyn。
