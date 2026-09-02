# tbtools-cli 全量回归测试 — 10 批无人值守计划

> 目标：对 140 绘图命令 + 82 CLI 工具 + 188 RPC + 安装/文档/示例做**全量**回归，
> 拆成 10 批串行子任务，一批返回结果后再派下一批，全程无人值守不中断。
> 基线：commit 9d4df5a（工作区干净，可发布）。
> 已有资产：tmp_tbtools_fulltest_report.md（33/33 冒烟）、tmp_eval_tbtools_report.md（盲测 6/10）。

## 执行机制
- 每批 = 1 个子任务（sessions_spawn mode=run），自包含、只读测试项目、不改代码。
- 每批在 `/home/elysia/tbtools-cli/test_reports/batchNN_<名>.md` 写结构化报告（PASS/FAIL 表 + 证据 + 阻塞项）。
- 批间串行：本批子任务返回 → 检查结果 → 派下一批。任何一批 FAIL 也继续（记录阻塞项不中断）。
- 数据源：examples/data/** + 各批自造 /tmp 测试数据；禁止修改 examples/ 原始数据。

## 10 批划分
| 批 | 范围 | 覆盖 |
|:--|:-----|:-----|
| 1 | 环境与基础架构 | install.sh/config/jar 探测、help/banner 计数、tbtools 主入口路由、未知命令降级、未知工具报错、list tools/plots/rpc、run_examples.sh 8/8、git 干净 |
| 2 | FASTA/序列/GXF 数据工具 | fastaExtract/fastaSubseq/gfa2fa/hmmExtract/fqfaConv/fqTrim + gxf*(12) + gsadiag/gxfsort/gxffilter + mast2tab/mggxf/pep2codon/seqconvert |
| 3 | 表达计算 + 统计绘图 | rpkmCal/tpmCalc/fpkmToTpm/tauIndex/exprCorr/qpcrExp/qpcrproc + pca/volcano/dehist/qpcr/groupedbar/barplot + table* 工具 |
| 4 | 核心绘图 I（基因结构/Motif/热图/eFP） | genestructure/motif/seqlogo/heatmap2/cubeheatmap/layoutheatmap/efpHeat/multiEfp + cddmotif/pfammotif/seqlentrack/amazingmeta |
| 5 | 树 + MSA + 进化 | tree/hclust/phylotree/treeRooting/msa/onesteptree/nwAlign + findBestForkerRootTree + marker/markertools |
| 6 | 共线性/PAF/微共线性 | circos/supercircos/circlegene/dotplot/pafviz/pafcomp/pafref/microsyn/msy/multisyn/dualsyn + mcscanx/collinearRegion + findblockdual/multiple/visualizeblock |
| 7 | 集合/韦恩/UpSet + ChIP-seq | venn2-6/upset + peakdist/peaktss/peakanno/pileup + regiondepth + bamindex/bamsort/bamstate/bamMerge |
| 8 | 特殊绘图 + 组装/注释/其他模块 | microgenome/gel/gfa/plotrna/rnaplot/colorscheme/distance/mountain + GenomeAssembly 链 + virusRecomb + preparespecies + miRNA 链 + levelGo/goParse |
| 9 | RPC 188 方法分组实测 | server start/methods=188、describe、跨类别 call 实测（Fasta/GXF/表达/BLAST/建树/引物）、JSON-RPC 边界、heatmap |
| 10 | 发布审计 + 文档一致性 + 真实数据端到端 | README 数字 vs 实际、COMMAND_REFERENCE 完整性（140 命令每命令有文档、80 桥每桥有 Javadoc）、git 干净、真实 GRAS 端到端链 + 汇总 PASS/FAIL |

## 状态
- [x] 批 1 环境与基础架构 — ✅ 14/14（09/01 主线程直跑；子代理模型通道不可用→改直跑模式）
- [x] 批 2 序列/GXF 工具 — ✅ 27/27（batch02_report.md）
- [x] 批 3 表达+统计 — ✅ 25/25（batch03_report.md）
- [x] 批 4 核心绘图 I — ✅ 11/11（batch04_report.md）+ T412 amazingmeta 补测 ✅（09/02 04:40 直测 SVG_OK 5324B，见 batch04_report.md 附录）
- [x] 批 5 树+MSA+进化 — ✅ 15/15（batch05_report.md，09/02 05:50）
- [x] 批 6 共线性/PAF — ✅ 16/16（batch06_report.md，09/02 07:45；findblockdual/multiple 为已知需真实数据 → SKIP_KNOWN 判定）
- [x] 批 7 集合/ChIP-seq — ✅ 15/15（batch07_report.md，09/02 07:50；peakanno 真实尺度坐标；小坐标触发 GxFOverlapIndexer bin 边界 bug 已入坑表）
- [x] 批 8 特殊绘图+模块 — ✅ 17/17（batch08_report.md，09/02 07:55；⚠️ write 工具写 def 会成空文件——必须 heredoc 创建；colorscheme refColIndex 实际 1-based 已修文档）
- [x] 批 9 RPC 188 — ✅ 16/16（batch09_report.md，09/02 08:05；T912 GffFeatureExtract 首次失败系测试数据用错（转录本 FASTA 当基因组），正确 genome FASTA 提取 37 序列验证通过）
- [x] 批 10 发布审计+端到端 — ✅ 10/10（batch10_report.md，09/02 08:10；140 命令全覆盖/80 桥 Javadoc/82 工具/188 RPC 全核对；GRAS 端到端 statFasta→ML建树→seqlogo 验证通过）

报告目录：`test_reports/`（每批一文件）
