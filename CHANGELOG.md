# Changelog

所有显著变更记录于此。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [1.4.6] - 2026-09-26

### Conformance Verified(第 18 份评审)
- **layout 严格错误检查(禁 silent skip)**: INVALID_LAYOUT_INPUT/MISSING_LAYOUT_OUTPUT/MISSING_LAYOUT_PARAMETER/UNKNOWN_LAYOUT_PARAMETER/INVALID_LAYOUT_TOKEN
- **planner binding 填 ParamSpec 默认值**(volcano: pval_cutoff 0.05/fc_cutoff 1.0/w 1000/h 800)
- **Conformance Verified 体系**: Tier1 compile-verified(59 FULL 全部)+ Tier2 execution-verified(volcano/dehist/dualsyn 真实执行+产物+sha+溯源)
- **legacy args 退役警告**(DeprecationWarning 提示迁移 binding,v2.0 移除)

## [1.4.5] - 2026-09-26

### 契约闭环 + WOX 实跑修复(第 17 份评审 + WOX 问题单)
- **P06-A【严重】wheel 缺 runtime 子包修复**: pyproject `packages=["tbtools_cli"]` 只打顶层包 → `packages.find` auto-discovery(pip install 后 `ModuleNotFoundError: tbtools_cli.runtime` 根因;wheel 实测含 java.py)
- **Planner 直接生成 binding**: 生成 spec→validate→run 全闭环(同一 compile_step)
- **UNEXECUTABLE 三态**: 多必填输入工具明确排除(非低分,rejected 列表含原因)
- **InvocationSpec token layout**: 精确 argv token 序列编译
- **contract_coverage 六维分级** + conformance corpus(tests/conformance/*.json)
- P06-B __version__ 防御回退;P07 doctor jar 版本显示 + 三平台 Java 提示

## [1.4.4] - 2026-09-25

### 契约最后一公里(第 16 份评审)
- **InvocationSpec grammar 升级**: named-flag 布局(venn2: `--List1 a --List2 b --graph out.svg`)+ KNOWN_NAMED_FLAGS;positional 布局兼容
- **validate/run 同一 compiler**: `compile_step` 共享(binding 形态契约编译;validate 抓 WORKFLOW_COMPILE_ERROR;run 实测)
- **format ontology**: 8 格式族 + exact/compatible/incompatible 三级匹配
- **edge 标注**: `{type: contract|legacy_relation, match level}`;**planning_score** `{score, level, evidence}`
- **Artifact lock Windows msvcrt 兜底**;MCP embedded envelope 统一
- **Contract Coverage**: counts.md 契约完备度统计(invocation_compilable 63/294)
- **conformance 测试**: 59 FULL 工具编译契约 + 金链 executable

## [1.4.3] - 2026-09-25

### Contract Compiler(第 15 份评审)
- **InvocationSpec**: `CommandSpec.invocation.build_argv(inputs/parameters/output)` → 精确 argv(类型验证/未知参数/必填输入检查;消灭 {input}/$step.output/args[-1] 三层猜测)
- **Planner 契约图**: A.outputs↔B.inputs 真实配对(模糊格式匹配)+ DFS 全分支 + 目标可达排序 + 多必填输入降级 + 透传跳惩罚 + 精确名单步优先;confidence reasons-based(数值+reasons)
- **resume 执行 fingerprint**: workflow 定义变更 → 全部重跑
- **Artifact 索引 flock**(并发防丢,补)+ `_save_state` 原子写
- **MCP 错误 envelope 统一**(CLI_ERROR/TIMEOUT 结构化)
- **artifact inspect 列名契约**(producer columns 验证表头)
- workflow_id 完整身份(goal+contracts+chain+schema 版本)
- 金链契约测试 tests/test_contract_compiler.py(13 用例)

## [1.4.2] - 2026-09-25

### Workflow 契约化(第 14 份评审)
- **validate 契约化**: Syntax→Graph→Tool Contract→Binding 四层,结构化 errors(WORKFLOW_INVALID_TOOL/DEPENDENCY/CYCLE/BINDING),exit 3
- **输出识别契约化**: CommandSpec outputs 扩展名匹配(不再 args[-1] 纯猜)
- **resume 完整 sha256 验证**: state 记录 output_sha256,产物篡改→强制重跑(实测)
- **artifact inspect 不存在 bug 修**: ARTIFACT_NOT_FOUND exit 3(此前返回 truthy)
- workflow_id 含 constraints / Artifact ID sha256[:32] / 索引 flock 并发安全
- MCP 参数契约只读 spec(KNOWN_PARAMS 旁路清除)+ bool 参数 flag 形式

## [1.4.1] - 2026-09-25

### 修复(第 13 份评审)
- **P0-5【真 bug】workflow_id 稳定化**: `abs(hash(goal))` → sha256 派生(Python hash() 受 PYTHONHASHSEED 影响每次进程随机化,跨 run/resume 引用全断;实测跨进程同 ID)
- README hero FULL 数 8→59 同步(FULL 判定修正后)
- workflow 类 docstring/sanity 命名收敛
- tests/test_doc_consistency.py: README/protocol MCP 数/FULL 数与代码一致性防文档漂移

## [1.4.0] - 2026-09-24

### Agent Runtime 协议一致性收口(第 9-12 份外部评审全落地)

- **Agent Protocol v1.0 正式文档**(docs/agent-protocol.md: 七铁律/调用链含 plan/错误分层/Artifact 模型/变更策略)
- **Artifact 一等公民完整化**: 完整 SHA-256 64 位(不再 16 位截断/256-512MiB 截断) + 稳定身份 ID(art_<sha256[:16]>, 同内容同 ID, 支持缓存/去重/resume) + 索引原子写(tmp+fsync+os.replace 并发安全) + resolve 身份验证(stale ID 拒绝)
- **Workflow 一等公民完整化**: depends_on 拓扑排序 + 真 DAG graph + resume Artifact 验证(state 成功≠可信, 产物+provenance 失效重跑) + workflow_plan(目标→CommandSpec 契约推导, CLI+MCP 9 原语) + WorkflowSpec 对象化(depends_on/input/output_contract/selection_reason) + Artifact ID 登记
- **MCP 完整化**: 9 编排原语(含 workflow_plan) + Schema-bound 参数(cli_name 翻译) + 强类型验证(INVALID_PARAMETER_TYPE) + arguments dict + embedded 模式 + agent 默认关 reflection
- **Agent-ready 分级**: FULL 判定修正(outputs 检查+无参数区分, FULL 8→59 真实契约完整工具) + readiness_census + doctor Readiness Report + counts.md 自动统计 + tool-readiness.md
- **CommandSpec 唯一事实源**: 全量 294 投影等价测试证明 + cli_load._group_of 模型优先 + legacy registry deprecation + tests/test_registry_discipline(禁新 import)
- **工程**: tool-readiness/contracts YAML/README hero 精简/平台矩阵/仓库卫生(dist/egg-info/.coverage 去跟踪)
- **测试**: pytest 269(新增 agent_contract 全链路/registry_discipline) / ruff 0 / mypy strict 0

## [1.3.0] - 2026-09-24

### Tool Contract 收敛(第 4-6 份外部评审全落地, 40+ commits)

- **协议契约五层全闭合**: inputs(columns 列名契约 6 核心命令) + parameters(ParamSpec 类型/默认值 8 命令) + outputs(任意 artifact) + capabilities(186) + relations(184)/dependency_manifest(结构化依赖)
- **MCP 增强**: arguments dict(inputs/outputs/parameters 结构化) + 分组命令空格拆分修复 + 结构化参数(空格路径安全) + MCP/CLI timeout 统一
- **Agent 接口新增**: doctor --json(含 compat 矩阵)/capabilities(环境能力检测)/tool-run --dry-run(预检+预估产物)/--quiet/provenance-graph(运行链 DAG: 文本/JSON/mermaid)/plugin list/job-clean
- **可靠性修复**: ensure_bridge 编译失败即中断(TB_BRIDGE_COMPILE_FAILED, 不再 ClassNotFound 掩盖)/RPC 启动互斥锁(flock 并发安全)/errors.py NoClassDefFoundError|DatatypeConverter bug/无图形输出命令 job 终态误判修复/provenance 任意 artifact(TSV/GFF/NWK 等)+运行后 inputs 误吞输出 bug
- **安全**: config.toml [security] allow_engine_reflection(engine 反射可关, ec=5 策略错误码)
- **测试**: tests/test_contract.py(294 命令契约 8+2 用例) + tests/test_jobs.py(5) + expected_commands.json manifest(54 核心命令)
- **工程**: --runtime-threads 命名空间/mypy CI 文案对齐/coverage 基线可见/README 按任务索引(12 场景)/飞纪盘 64 插件评估报告

## [1.2.0] - 2026-09-23

### Agent 运行时(2026-09-22 晚 - 09-23, GPT/GLM 两轮评审落地)

- **Agent 能力 1-7 全显式**: search(多词/反向/能力图)、tool-describe(schema/能力/依赖/可用性/关系)、tool-validate(--force)、tool-run(--json 纯协议/--timeout)、tool-result、tool-provenance、rpc methods 默认静态发现(--autostart)
- **单一命令模型(CommandSpec)**: 294 命令全模型化, metadata 由模型投影生成(无残影); 65 命令结构化 schema; 25→185 命令 capability 标注(29 能力域); 15 核心命令语义关系图(accepts/produces/next_step)
- **ai/ 机器接口层**: tool-index.jsonl(294)/capability-index/workflows(4 可规划流程)/relations/单工具 schema/error-codes
- **Error Contract**: TB001-TB012 错误码注册表 + classify_error; 失败也写 provenance(error: code/retryable/suggested_action); tool-run 失败返回结构化 error
- **Job 模型**: tool-submit(--timeout)/job-status(状态机 running→succeeded/failed/cancelled/timed_out + 惰性终态判定)/job-log/job-result/job-cancel(进程组整杀)
- **core.py 拆分**: 942→512 行(errors.py 独立 + runtime/java.py 执行/输入保护/provenance)
- **供应链**: fetch-jar SHA256 校验(下载 zip+提取 jar, 记录 config.toml)+ doctor 校验现 jar
- **CI**: nightly-e2e(每日 01:00 UTC 真实 JAR 5 命令出图断言 + pytest/ruff)
- **README 数字机器化**: 30+ 处手写精确数字清零→范围口径 + counts.md/version --json 权威源; TestReadmeCounts 改造为权威源一致性
- **兼容层治理**: alias_of 结构化(6 别名不污染工具空间); README Agent 接口节

## [1.1.0] - 2026-09-22

### 架构重构（09/22 · 批次 A/B/C 全量落地,commit 384ddee..1b0c716）

- **metadata 单一数据源**：`scripts/gen_metadata.py` 生成 `command_metadata.json`（276 命令;ENGINE_REGISTRY 172 + CLI_TOOLS 82 + 手动 + bridges 118 合并）+ `--check` 防漂移 + `--render` 生成命令清单
- **拆 cli.py 1642→533 行**：cli_rpc（自愈基础设施）/ cli_load（动态注册）/ cli_top（顶层命令）
- **CI 真实化**：ruff 全仓库硬阻断（0 errors）/ shellcheck 0 / 全量 pytest / 无 jar CLI 冒烟 / onboarding-e2e 真实 jar 8 命令出图断言
- **质量修复**：PITFALL 6 个重复键（barplot 列名实测修正）、版本号单一源（importlib.metadata）、Homepage 指向本仓库

### 第二轮外部审查修复（09/22 · 评分 美观 7 / 易用 7.5 / 可维护 6.5 / 生态 5）

- README 精简 701→322 行（命令罗列改自动生成清单 docs/_generated/commands.md）
- docs/_worklog/ 收拢工作日志;CONTRIBUTING.md + issue 模板
- README 示例图入库（.gitignore 全局 *.svg 曾导致 GitHub 死链,已豁免）
- 命名规范/示例表/中文节/漂移修正

### 修复（RPC 测试交付包 N1-N41，09/21 · 批次 0-4 全部落地）

> 来源：WorkBuddy Windows 17 轮穷举测试（~1665 项/~812 通过）。全部 N1-N41 修复已完成并通过三轮复审，
> 分诊明细见 `docs/_worklog/RPC_FIX_STATUS.md`（P0×2/P1×12/P2×14/P3×12：18 修复 / 14 平反 / 2 引擎级 / 6 环境 / 14 数据格式）。

- **P0 输入保护（系统性）**：run_java 统一 snapshot/verify/restore/cleanup——引擎在用户输入上建库/清洗/写穿时自动恢复并告警（N37 四起输入清空事件防御）；0 字节输入统一拦截（N10/N11）；强输出存在性校验（N30）
- **P1 引擎 IO 修复**：N19 findBestHomologyBatch 真实参数 + 防静默成功；N23 mirnatarget 完整管线（ssearch36→TargetScoreCli）；N25 gffCdsPhaseCorrector 位置参数包装；N24/N26 手写 impl 复活
- **RPC 自愈**：pid 文件 + 健康轮询 + 自动重启 + --timeout + 代理绕过（N34/35/38/40/41）；N40 上游 jar 缺陷仅包装层加固
- **其余**：N1 get_java 解析顺序 / N2 GUI 黑名单 / N27 bridge DatatypeConverter / N3 tableMerge 真实参数 / N28 gxf 族警告 / N33 help 回退等（详见 RPC_FIX_STATUS.md）

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

### 已知未修（报告待办，见 docs/_worklog/EXTERNAL_TEST_REPORT_20260919.md）

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

## [0.9.0] - 2026-09-04

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
