# examples/data/exec/ — 执行验证数据（EXECUTION_VERIFIED 证据源）

> 自审 verified F4 响应（2026-10-06）：本目录此前无文档、无生成说明、混入引擎中间产物——"seed 固定可复现"只存在于测试注释，换人无从复现。
> **纪律：本目录只放确定性输入（合成数据 + 参考数据）；引擎运行中间产物禁止入库**（移入 `_engine_cache/` 或测试 tmp）。

## 目录/文件来源

| 文件/目录 | 用途（喂给哪个 EXEC_VERIFIED 工具） | 来源/生成方法 |
|:--|:--|:--|
| `barplotter/` | barplotter（bplot.gff + bplot.synteny + bplot.ctl） | 合成：简化 GFF 基因注释 + 共线性对 + 4 行逗号分隔 ctl（v1.4.49 收编） |
| `collinear.lst.txt` / `gxf_lst.txt` | multisyn（多物种共线） | 合成：gxf 列表 + collinear 列表（引擎格式实锤） |
| `dp_gff.txt` / `dp_layout.txt` / `dp_pairs.txt` | dotplot / qdot | 合成：4 列简化 GFF + `Genome: chr list` layout + genePair（v1.4.55 收编） |
| `gene2go.tsv` / `mini.obo` / `select_genes.txt` | goEnrich | 合成：最小 GO 本体 + 基因映射 + 选中集 |
| `gsea/` | gsea（query2go + rank.rnk） | 合成：一基因一行的 query2go（terms 逗号分隔）+ 排序基因列表（v1.4.53 收编） |
| `hclust3col.tsv` | hclust | 合成：3 列距离矩阵 |
| `hmm/` | hmmsearch / hmmerSearch | 合成：HMM profile + 目标肽 |
| `kallisto/` | kallisto（tx.fa + 76bp 切片 reads） | 合成：seed=42 自造转录组 + 切片 reads（100% 配对，v1.4.51 收编） |
| `kegg/` | keggEnrich（ref.keg + annotation.tsv + selectIds.txt） | 合成：扁平 5 列 .keg（真实格式实锤）+ 注释 + 选中集（v1.4.55） |
| `lh_expr.tsv` / `lh_layout.tsv` | layoutheatmap | 合成：layout 在前 expr 在后（样本名配对 S1-S4） |
| `meme/` | memeViz / motif / mastrun | 系统 meme 造真 MEME XML + motif ids（v1.4.55 收编） |
| `notung/` | notung | 合成：可协调树 + 基因树（--outputdir 派生名，impl 搬运） |
| `peak/` | peakanno / peaktss（genes.gff3 + peaks.xls） | 合成：坐标 **+1e6 平移**绕 bin0 缺陷（<10000 无命中）；`peaks_low.*` 为低坐标缺陷固定测试输入 |
| `pep_aln.fa` / `pep_cds.fa` | pep2codon | 合成：CDS + 蛋白比对 |
| `plotrna/` | plotrna（genome.fa + reads.sam） | 合成：基因组切片 + SAM reads（覆盖 region chr1:1-1000） |
| `sc_genome.txt` / `sc_link.txt` / `scc.cfg` | supercircos | 合成：chrLen + link（cfg 用**仓库相对路径**，勿改回 /tmp——v1.4.66 修复 WSL 易失） |
| `test.paf` | pafviz | minimap2 造 PAF（18 列标准格式，v1.4.46 收编） |

## 生成纪律

- 数据确定性：合成数据 seed 固定（kallisto seed=42 等），**改 seed 需同步更新语义断言**（SEMANTIC_CHECKS 内容级断言）
- 引擎中间产物（`.sorted.sam*` / `.TBtools.fa*` / `.fai` / `.sai` / `_engine_cache/`）：**不入库**——测试在 tmp 运行生成，不会污染本目录
- 数据自洽：修改任何文件前确认被喂工具的解析要求（P1 模式：文档声称格式 ≠ 实际解析格式，先 javap）

## 验证依赖

EXEC_VERIFIED 54 工具断言需本目录数据 + 真实 JAR 环境实跑；clean CI（无数据/JAR）下相应用例 skip（口径见 PLAN.md）。
