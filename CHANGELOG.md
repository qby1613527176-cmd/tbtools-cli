# Changelog

所有显著变更记录于此。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

### 修复（RPC 测试交付包 N1-N41，09/21 · 批次 0-4 全部落地）

> 来源：WorkBuddy Windows 17 轮穷举测试（~1665 项/~812 通过），证据链与回归脚本见交付包 `workflows/tbtools_cli化_修复清单.md` + `tbtools-cli/docs/RPC_FIX_STATUS.md`。

**P0 输入保护（系统性）**：`core.py` run_java 统一接入 snapshot_inputs/verify_and_restore/cleanup_side_effects——引擎在用户输入上建库/清洗/写穿时自动恢复并告警（N37 四起输入清空事件防御）。

**P1 修复**：
- N19 findBestHomologyBatch 真实参数 impl（--inQueryProteinSet/--targetIdList/--outDir；旧 --queryFasta/--outTable 兼容；产物校验防静默成功）
- N23 mirnatarget 恢复完整管线（ssearch36 -m 10 → TargetScoreCli），输出落盘 + 防 in==out 清零
- N25 gffCdsPhaseCorrector 位置参数包装（防覆盖输入）
- N24 getLongestCompleteORF → GetLongestORF（弃 JavaFX 无 main 类）
- N26 msy 表驱动参数错位修复（显式拼 GenericCli）
- N27 multiEfp/efpHeat fake DatatypeConverter 源码入库 + ensure_bridge 自动重建 + direct classpath 补 build/
- N34/N35 RPC 自愈：pid 文件 + 健康探针 + call/methods 自动拉起 + rpc stop/status + OOM 转储 + 代理绕过
- N40 OneStepBuildATree 归因（引擎 IQ-TREE stderr 管道未排水，Windows 死锁）+ 包装层超时/依赖预检
- N1 java 绝对路径定位（TBTOOLS_JAVA > PATH > 常见位置）；N2 GUI 类工具黑名单无参即退；N28 Gxf 族 GTF 输入警告；N30 强输出存在性校验；N38 RPC 空消息友好兜底

**P2 快赢**：N3 tableMerge 引擎真实参数对齐；N10/N11 空输入统一报错；N12 heatmap --preset；N13 gwas 分组补齐（vcfAddID/mimicVqsr）；N14 doctor xvfb 平台感知；N15 banner 数字对齐；N16 check 识别 GFF3；N20 check 退出码；N29 mirnaIdentify docstring；N32 gel 无参防挂；N33 help 渲染接入 command_metadata.json（150 可选位透出）

**测试**：新增 tests/test_p0_protection.py 11 项 + 既有更新；全量 **81 passed 1 skipped**（基线 70/71）。

### 新增（GUI 面板逆向接口第二批，09/20 · #15~#29 共 17 个命令）

方法论同 `docs/GUI-INTERFACE-SOP.md`（反编译 GUIPanel StartButton 回调 → 拿权威 setter+process 调用链）。

- **系统发育管线（muscle→trimal→iqtree 全链实测闭环）**：`seq muscle`（#27 QuickRunMUSCLE；⚠️ 引擎硬编码 muscle3 -in/-out 语法在 muscle5 系统崩 → Python 直调自动探测 v3/v5）、`seq trimal`（#29 QuickTrimAL；automated1/gappyout/strict/strictplus 四模式）、`tree iqtree`（#28 QuickRunIQtree；MFP 自动选模/UFBoot/自由速率/ASC；⚠️ UFBoot 须 ≥1000 否则 IQ-TREE 2 静默失败，桥内加防御校验）
- **进化/树**：`tree kaks`（#15 PairWiseKaKsCalculator，Ka/Ks 计算；引擎自带 ArgsParser）、`tree subtree`（#23 GetSubNewickTreeGUIPanel→PhyloTreeMan.getSubTree，诱导子树提取）
- **序列**：`seq sixframe`（#16 SixFrameTranlater，六框翻译）、`seq longestorf`（#17 GetLongestORF，最长完整 ORF 预测）、`seq protparam`（#18 ProtParamWrapper，蛋白理化性质；⚠️ 联网 Expasy）、`seq genomefilter`（#19 QuickStatFasta+ExtractFasta 组合，长度过滤+可选 GXF 同过滤）、`seq seqpattern`（#20 QuickLocateSeqPattern，正则模式定位 GFF3）、`seq careclassify`（#22 PlantCAREResultClassify，PlantCARE 顺式元件 97 类分类）、`seq protsim`（#24 CalculateSimilarity，蛋白两两相似度矩阵）、`seq fa2tab`/`tab2fa`（#26 FastaTable 双向互转）
- **GFF**：`gxf bed2gff3`（#21 RegionBedToGFF3；⚠️ BED 第 4 列须为 `ID:链向:编码` 如 G01:+:C）
- **BLAST**：`blast xml2blasttab`/`xml2pairwise`（#25 BlastXmlToBlastFoolTable+BlastXMLToPairwise，补 GUI 四模式单选中注册表未覆盖的两个）

**排坑沉淀**：① RegionBedToGFF3.process line81 崩=BED 第 4 列 split(':') 期望 ID:strand:coding ② pairwise 需 Hsp_query-frame/Hsp_hit-frame 字段 ③ QuickLocateSeqPattern 的 setMaxLenKbases 是 chunk 参数非长度过滤（main() --maxSeqLen 才是）④ QuickRunMUSCLE 引擎 muscle3 语法硬编码，v5 系统须 Python 直调适配 ⑤ 'no space in path' 是无害 debug 日志 ⑥ IQ-TREE 2 UFBoot<1000 静默失败

**覆盖审计澄清**：DEGsDistPlot=dehist、GoTermparser=goParse、EnrichmentGrapher=barplot、GXFRepresentativeGrabber=gxfRepGXF、MSAtrimmer=trimmsa（面板名与 CLI 名差异导致的假阳性，实际已覆盖）

### 新增（GUI 面板逆向接口第三批，09/20 晚 · #27~#32 共 6 命令+管线闭环）

- **系统发育管线闭环（muscle→trimal→iqtree 全链实测）**：`seq muscle`（#27 QuickRunMUSCLE；⚠️ 引擎硬编码 muscle3 -in/-out 语法在 muscle5 系统崩 → Python 直调自动探测 v3/v5）、`seq trimal`（#29 QuickTrimAL；automated1/gappyout/strict/strictplus 四模式七格式）、`tree iqtree`（#28 QuickRunIQtree；MFP/UFBoot/FreeRate/ASC；⚠️ UFBoot<1000 被 IQ-TREE 2 静默拒绝→桥内防御校验）
- **比对修剪补充**：`seq gblocks`（#30 Jgblocks 纯 Java Gblocks 实现；main 仅 in/out 全参数须 setter 桥；GUI 默认 IS=0.5/FS=0.85/CP=8/BL1=15/BL2=10）
- **BLAST**：`blast bestid`（#31 BestIDConverter 双向 BLAST 最优 ID 转换；⚠️ CLI 公共 -t/--threads 吃掉引擎强制 --threads → 手写 impl 缺省注入 4）
- **GO**：`table goAnno`（#32 GoAnnoPipe GO 注释管道：blastx XML→query2gi→gi2go；⚠️ idmappingDb 须 **gzip 压缩**格式「ID; ID\tGO:num; GO:num」；自带 ArgsParser→direct）

### 新增（GUI 面板逆向接口第四批，09/21 凌晨 · #33~#37 共 7 命令）

- **序列**：`seq fasplit`（#33 QuickSpiltFasta 按记录拆分，区别于 filesplit 按行切；⚠️ --byCount true 须显式传）、`seq famerge`（#33 FastaMergerAndSpliter.Merge 多变长输入合并）、`seq gb2fa`（#36 genBank2Fasta，GenBank→FASTA 带头信息）
- **表格**：`table clearchar`（#34 FileCleaner.simplifyFile 非法字符→_）
- **BLAST**：`blast getseqdb`（#35 blastdbcmd -entry_batch；⚠️ 库须 -parse_seqids 建）、`blast findhomolog`（#37 FindBestHomology 最优同源查找，同引擎覆盖 GenomeAnnotationSlim+FindBestHomology 双面板）

**排坑沉淀**：① CLI 输入校验误拦非常规首参（输出文件/dbPrefix）→ 跳过名单（famerge/getseqdb）② makeblastdb 须 -parse_seqids 否则 blastdbcmd Skipped ③ DEAnalysisPrepare 的 ComparisonPrepare 是 JList/JPanel 交互对话框 → 判 GUI 强依赖不可 CLI 化

### 新增（GUI 面板逆向接口第五批，09/21 凌晨 · #38~#41 共 4 命令+SRA 组全清）

- **物种/SRA**：`table taxparse`（#38 NCBITaxonomy 批量分类解析，9 级分类列；⚠️ 联网 NCBI eutils）、`table srr2ena`（#39 GetENALinksOfSRR；⚠️ 联网 ENA filereport API+引擎自带 0~3s 限速；17 字段含 fastq_ftp/aspera）、`table sraxml2tab`（#40 ParseSRAXml2Table 离线 JDOM 解析 SRA XML→17 列信息表；自带 ArgsParser→direct）、`table sranum2info`（#41 BatchGetSRARecordInfo SRR 批量信息表；⚠️ 联网 NCBI Entrez+限速；自带 ArgsParser→direct）

**SRA 工具组 3/3 面板全清**（srr2ena/sraxml2tab/sranum2info）

### 新增（GUI 面板逆向接口第六批，09/21 凌晨 · #42~#45 共 4 命令）

- **比对/推荐**：`blast blat`（#42 BlatExecutor；**org.ucsc.blat 纯 Java BLAT 实现内嵌 jar 无需外部二进制**；9 输出格式默认 blast9+auto/dnadna/dnarna 三模式）、`engine seqrecommend`（#43 AssemblyGenomeDataSizeRecommand 测序量推荐；纯计算离线；400Mb Draft=Hifi 15-20X+HiC 30-60X）
- **下载/文献**：`seq seqfetch`（#44 NcbiSmartSeqFetchEntrezUtils NCBI 智能序列下载；ID 自动检测/转换/审计/apiKey/限速，NM_000546→TP53 mRNA）、`table pubmed`（#45 PubmedSearch；联网 eutils；期刊/标题/年份/IF/DOI 表）

**判不可做（第六批裁决）**：BlastXmlAlignment 可视化组（DotPlot/PileupGrapher/Shower——JJplot2GUI 是 Swing 交互窗 JustShowIt，非 JIGBasePanel 可 save2SVG，GUI 强依赖）、eRace（GenomeWalking 引擎复杂+GUI 表格渲染重）、SimpleDownloadSeq/BulkDownloadSeq（旧版下载引擎无 CLI 且功能被 seqfetch 覆盖，判冗余）、PlantPhyloTreeRebuild（PrepareDB 依赖已死网站 theplantlist.org 下载属级映射，内置仅 47 属；GUI 同病）

### 重构（auto_commands 表驱动化，09/20）

- **auto_commands.py 2105→461 行（-78%）**：审计发现原文件 309 个 def 仅 157 个唯一函数（历史合并整段重复，Python 后者覆盖前者）→ 按生效规格提取 ENGINE_REGISTRY（144 条：86 bridge + 58 direct）+ `_make_impl` 工厂动态生成
- **13 个特殊实现手写保留**：hmmsearch 转发 / gxfAttr 原生 / kallisto 二进制 / fimo 二进制 / notung 插件 / newickRename 插件 / hmmerSearch / memeViz / gsea / tfbsShift / mcscanxd / quickAnno / smart（各含独立预检/环境/参考数据逻辑）
- **正确性验证**：新旧模块 157 函数集合一致、doc 全一致（含编译器 docstring 制表符展开语义）、行为 0 不一致；端到端 bridge 型 hclust 出 nwk / direct 型 venn2 出 SVG / 注册表工具 statFasta 出表
- **ruff 46→0 errors**（顺带消灭整段重复冗余）；备份 auto_commands.py.bak_pre_tabledriven

### 新增（GUI 面板逆向接口，09/20 · 14 个命令）

方法论：反编译 GUIPanel StartButton 回调 → 拿权威 setter+process 调用链 → 绕 GUI 弹窗直驱（public process()/plot()/buildPanel()/postGraph 重载）。详见 `docs/GUI-INTERFACE-SOP.md`。

- **注释**：`tool eggnog`（eggNOG-mapper 官方 CLI 移植 CliParser→EmapperPipeline）
- **序列**：`tree nwAlign`（Needleman-Wunsch，替换旧静默失败的 SimpleBatchProcess 实现）
- **共线**：`syn pafviz`（PAF dot 图）、`syn mcscanxd`（OneStep MCScanX-SuperFast，diamond 加速）
- **MEME 管线全覆盖**：`seq meme`（发现）、`seq mast`（搜索）、`seq fimo`（扫描）、`seq meme2tab`（XML→表）、`seq makemotif`（序列→motif）、`seq mpattern`（motif 序列标注图）、`seq memeViz`（可视化）
- **集合/统计/群体**：`sets upset`（UpSet 图）、`expr gbar`（分组柱状图+显著性）、`engine admixture`（Q 矩阵可视化，修复 .lst 参数不匹配）
- **GO/注释**：`table golevel`（层级统计+柱状图）、`table sricher`（超几何富集+BH）、`gxf gdensity`（基因密度 bin）
- **判定不可做**：GoCompare（getColDivide 列名索引 bug + main() ArgsParser bug，引擎缺陷）；BlastZone（交互式 GUI 强依赖）

### 修复（外部代码审查，09/20 · 6 批）

第三方 AI 通读仓库审查，逐条核实后修复：

- **README 命令名脱节（最严重）**：118 个裸命令示例 117 个顶层不可调用 → 顶层自动转发（`tbtools venn2` → `tbtools sets venn2`）+ 4 个旧名别名（seqlogo/heatmap2/genestructure/treeRooting）
- **ruff lint 落地，抓出 4 类真问题**：F811 12 处（`auto_commands.py` 中间嵌第二个文件头，清理 200+ 行重复定义）、F601 3 处（CATEGORY_MAP 重复键）、F821（shutil 未导入）、F401/F541 等 38 处自动清理
- **PITFALL_HINTS 重复键**：onesteptree/simplehmmscan 各定义两次静默覆盖，合并去重
- **README 数字防漂移**：27→100 桥、140→174 命令等 7 处修正 + 防漂移 pytest（TestReadmeCounts）
- **README 示例图画廊**：6 张 SVG（heatmap/venn/upset/tree/synteny/bar，fulltest 数据实测）
- **get_jar 去导入期全盘 glob**：import 从秒级降到 0.074s，深搜移入 find_jar_deep()
- **Windows 支持声明**：Requirements + 中文版明确（工具类/RPC 可用，绘图类受 xvfb 限制）
- **probe 假 jar 测试**：CI 无真 jar 也能验证死命令探测逻辑（TestProbeWithFakeJar）

### 新增（插件 CLI 化，09/19-09/20）

- **§8 外部报告缺口全清**：G4 goEnrich/keggEnrich（GO/KEGG 富集桥）、G1 hmmsearch（HMM Search 别名）、G7 gxfAttr（GXF 属性/ID 对照，Python 原生）、G5 doctor 死命令探测（probe_dead_engines，揪出并修复 5 个死注册）、G2 tree draw 挂起根治（stdin 预检）
- **插件 CLI 化 8 个**（plugins/ 目录，来源 = TBtools 插件商店 122 插件）：`table gsea`（GO 预排序 GSEA）、`tree notung`（基因树-物种树 reconcile）、`seq tfbsShift`（植物 TF motif 偏移）、`seq memeViz`（MEME motif 可视化）、`hmm hmmerSearch`（HMMer 全库扫描）、`expr kallisto`（RNA-seq 定量）、`syn mcscanxd`（MCScanX-SuperFast）、`tree newickRename`；**09/20 第四批追加 4 个**（累计 12）：`syn qdot`（基因组 dot plot，绕开插件 quickShow GUI 崩溃直驱 dotdotdot）、`blast quickAnno`（diamond 蛋白注释，db 需带描述行）、`seq smart`（SMART 域注释，POST EMBL 约 65s）、`seq fimo`（FIMO motif 扫描，直调系统 fimo）
- **已评估跳过**：CutSignalP（P00062，Windows-only PE+python DLL）
- **坑位提示**：插件自带 "Linux" 二进制实为 Mach-O（macOS）——已清出并回退系统/conda 真 ELF（kallisto 0.51.1 + hdf5 依赖库随包）

### 修复（外部实测报告合入，WorkBuddy 2026-09-18/19 · Windows + TBtools-II 2.475 · 油茶 WOX 真实数据）

- **P0-1 `tbtools tool` 分组丢全部参数**：`ToolGroup.resolve_command` 的 lambda 闭包捕获分组自身 Context（`ctx.args` 恒空），~80 个转发命令参数全丢。改 `@click.pass_context` 拿子命令 Context（报告 §3.1 补丁原文，对方回归 14/14 PASS）
- **P0-2 `bin/tbcli.py` Windows GBK 崩溃 + 退出码失真**：`_run_tool` 三处 stderr 读取无编码参数，中文 Windows 上 Java 输出 GBK 字节 → `UnicodeDecodeError` 且误报失败。加 `_read_err` utf-8→gbk 降级探测（报告 §3.2 补丁原文）
- **130 处 xvfb 双重嵌套**（自查发现）：`auto_commands.py` 全部 `_impl` 在 `java_args` 内嵌 `xvfb-run` 前缀，与 `run_plot` 按需 prepend 构成双重嵌套；Windows 无 xvfb-run 时 `FileNotFoundError` 且误报「Java 未安装」。统一移除，xvfb 归 `run_plot` 单点处理
- **P0-3 82 个 CLI 工具新入口不可达**：原注册表仅在旧入口 `bin/tbcli.py`，`tbtools tool rpkmCal/statFasta/tpmCalc` 等全部「未找到」。抽取共享注册表 `tbtools_cli/cli_tools_registry.py`（82 项），新旧入口共用；`ToolGroup` 解析链：手动命令 → auto_commands `_impl` → 注册表直转；`help`/`list tools`/未知工具列表同步覆盖注册表

### 已知未修（报告待办，见 docs/EXTERNAL_TEST_REPORT_20260919.md）

- B2：Windows 上报「包装器吞引擎崩溃退出码」——Linux 复核不复现（EXIT=1 正确透传），待 Windows 环境复现定位
- README 的 `engine` 分组示例不存在（`tool generic` 仅适用返回 JIGSubPanel 的绘图引擎）；`--key=value` 写法被 ArgsParser 系引擎拒绝（文档需统一空格写法）
- B3/P1-1/P1-2/P1-5/P2-1 等引擎级问题；§8 封装缺口 G1~G7（hmmsearch/GO 富集/GXF ID 对照等）

## [1.0.0] - 2026-09-04

首个公开发布版本。

### Added（新增）

- **click 框架 CLI**：全量命令结构化入口（`tbtools <group> <command>`），替代原 `tbplot.sh` 裸调用
  - 15 个分组：seq / expr / tree / syn / sets / chipseq / asm / gxf / mirna / table / blast / fastq / hmm / gwas / engine
  - 143 个绘图/分析命令（19 手动 typed click + 130 auto_command 转发）
  - venn2/3/4 原生 ArgsParser CLI（`tbtools sets venn2 --List1 ...`）
- **拼写纠错**：未知命令自动建议最相似命令（`tbtools syn circcos` → `circos`）
- **`tbtools help <命令>`**：快捷帮助入口，自动定位分组
- **`tbtools list [plots|tools|rpc]`**：命令清单（tools 过滤绘图类，66 纯工具）
- **`tbtools presets`**：7 种期刊预设（nature 89×89 / cell / presentation / poster 等）
- **`--preset` 统一选项**：所有绘图命令支持预设画布尺寸
- **`tbtools rpc start|methods|call`**：RPC 服务器管理（188 方法）
- **`tbtools doctor`**：环境诊断（Java/JAR/xvfb/blast/samtools 等）
- **配置文件**：`~/.config/tbtools-cli/config.toml`（JAR 路径 + 默认线程/格式/预设）
- **Python 测试套件**：`tests/test_cli.py` 44 测试 11 类（框架/命令/list/venn/拼写/tool fallback/preset/退出码/输入校验/help 质量/rpc）
- **Bash completion**：分组/子命令/工具三层补全（`scripts/tbtools-completion.bash`）
- **CI**：GitHub Actions（click 框架加载 + bash 语法 + pytest + metadata 校验）

### 数据规模

- 80 个 Java 桥（`bridges/*.java`，源码持久化，/tmp 清理免疫）
- 123 个 TBtools-II 引擎（GenericCli 反射桥 + 专用桥）
- 188 个 RPC 方法
- 30 个坑位提示（PITFALL_HINTS，`--help` 自动显示）
- 35 个全量回归测试用例（`examples/scripts/run_examples.sh` 8/8 必过）

### 修复（本轮）

- venn5/venn6 help 截断
- PITFALL_HINTS 双 ⚠️ emoji
- `tool` 未知命令退出码 1→2（与 click 一致）
- `list tools` 混入绘图命令（130→66 过滤）
- install.sh：`run_examples.sh` 路径 + `help`→`--help` + `server start`→`list rpc`
- CI：run_examples 路径 + pytest 套件
- version 硬编码数字 → 动态统计
- tool --help 只露 3 个命令 → 全列出 66 个

### Known Limitations（已知限制）

- stdin 管道：仅 stat-fasta 等少量工具支持 `/dev/stdin`（Java 引擎限制）
- dualsyn：引擎跑通但保存受限（旧 JJplot2 框架，非 JIGBasePanel）
- MotifStack / MountainPlot / multiSeqBlastVisualization：TBtools 源码空壳，无法 CLI 化
- ncbiPileUpPlot：交互弹窗选 query，不适合 CLI
- venn2-4：走 auto_command 转发（ignore_unknown_options），非 typed click（参数校验弱于手动命令）

### Upstream

- TBtools-II 2.535+（CJ-Chen）主 jar 需用户自备（install.sh 引导）
- 桥/引擎签名基于 2026-08 全量逆向（CFR 反编译 + jstack + 窗口遍历方案）

## [1.1.0] - 2026-09-04

### Added
- `tbtools completion bash|zsh|fish` 内建补全生成（A1）
- `run_java` 成功耗时统计 `⏱ 耗时 X.Xs`（A4）
- `list` TTY 分页（>20 行自动 pager）（A2）
- `list` 分组着色（TTY-only，零依赖 ANSI）（B1）
- `help` 增强：分组 + 坑位 + 示例 + 完整帮助入口（B2）
- 输出文件已存在警告（防覆盖）（B3）

### Fixed
- 顶层直调分组内命令 → 提示正确入口
- 输出目录不存在 → 立即报错（不挂 Java）
- 分组内未知子命令 → 最近命令纠错
- run_plot/run_java/auto_commands 补 command_name（报错带命令名 + 坑位提示）
- `tbtools new` 交互式向导（按「想做什么」生成命令，--list / --run）
- `tbtools check <文件...>` 格式探测器（格式/大小/行数/列数/样例）
- C2 早期格式警告：10 常用命令输入格式不匹配时 Java 执行前提示（13 处 pre_flight 接线）
