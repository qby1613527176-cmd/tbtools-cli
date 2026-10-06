# Changelog

所有显著变更记录于此。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [1.4.82] - 2026-10-06

### 自评 5 视角响应(v1.4.81 后, P0×1 + 跨视角 P1 闭环)
- **P0 arch N1**: snapshot_inputs 输出回滚实测复现——cli.py manual 命令 15 处补 output_hint; java.py 接通保守兜底(真 positional ≥2 且末位产物后缀); docstring 对齐; 3 回归测试
- **README 294→298**: v1.4.81 统一到 298 后英雄行未同步(3 处)
- **tool-describe --json 补 verification_details**: 证据对象完整投影(权威源行指向真实字段)
- **counts.md 补 semantic_checked 动态计数**: 告别手写静态 '10'
- **arch N2/N3/N4**: add_command 别名 help 上移真源 / 截断 200→300 统一 / KNOWN_TOP_MANUAL 单一来源
- **门禁**: --check 298 命令/504 surface 全绿 / ruff 0 / mypy 0 / 149 passed

## [1.4.81] - 2026-10-06

### 外部红队审查响应(4 个 P1, 无 P0)——Evidence Surface 一致性
- **P1-1 CommandSpec 唯一运行真源**: 退掉 metadata fallback(manual 从源码扫描, 与 gen_metadata 同源); 别名注入双侧统一(依赖/manifest 对齐); 修互指环+死循环; 投影等价 0 差异(298=298)
- **P1-2 FULL 定义一致**: README 修正(parameters 恒声明, 无参数工具合法)
- **P1-3 证据完整投影**: verification_details 补 env_fingerprint/semantic_checked/domain_note
- **P1-4 叙事分层**: semantic_checked 10/54 明示
- **门禁**: pytest 264 passed / ruff 0 / mypy 0

## [1.4.80] - 2026-10-06

### 自审 P2 收官(product F11 命名约定)
- **COMMAND_REFERENCE 命名约定节**: camelCase(引擎类名直译)/全小写(新命令默认)/别名计划/tree 特例/engine 分组≠绘图引擎——三派并存承认化, 短期不改名(破坏兼容)
- **自审战役 24 项 P2 全部闭环**: 8 P0 + 21 P1 + 24 P2 全响应完毕
- **门禁**: ruff 0 / mypy 0

## [1.4.79] - 2026-10-06

### 自审 P2 批七(验证叙事诚实化)
- **arch F12-4**: _write_provenance 脆弱写法("snaps" in dir())→显式引用; inputs_set 语义注释修正
- **verified F7**: LEFTOVER 表加「活监控」列——6 工具明示有/无测试盯着(归档不再静态)
- **verified F8**: 报告 verification_tiers_note(CONFORMANCE_VERIFIED 试验层 n=1 明示, 防三层叙事超卖)
- **门禁**: pytest 15 passed / ruff 0 / mypy 0

## [1.4.78] - 2026-10-06

### 自审 P2 批六(死常量 + 新用户路径)
- **arch F12-2**: CANONICAL_SEMANTIC_FIELDS 死常量删除(双重源漂移风险)
- **arch F12-5**: agent_readiness 注释明示 params_declared 恒真(维度实际不参与分级)
- **product F10**: quickstart 重写(每条命令 JAR 依赖标注 + 零配置行为 + 退出码/错误码表 + readiness×verification 矩阵); reference.md 升级为参考入口
- **门禁**: pytest 44 passed / ruff 0 / mypy 0

## [1.4.77] - 2026-10-06

### 自审 P2 批五(docs 可接续性)
- **docs F9**: docs/README.md 维护者索引(活 plan/编年史/评审流向/生成物 vs 手写物/纪律)——新会话/贡献者不再靠口口相传; README Documentation 表加入口
- **docs F8**: 编年史补记第五十二至六十二波(v1.4.63-76)——记忆载体恢复完整
- **门禁**: ruff 0 / mypy 0

## [1.4.76] - 2026-10-06

### 自审 P2 批四(Agent 可执行性)
- **product F9**: search 分组标签改读元数据 group 字段——与 describe 同源(engine 是 runner 概念不再混入), Agent 不拼错命令
- **product F8**: tool-describe 支持批量(多命令 + --json 数组)——文案与行为一致; 未知命令集中报错; 补 readiness/verification 显示
- **门禁**: pytest 226 passed / ruff 0 / mypy 0

## [1.4.75] - 2026-10-06

### 自审 P2 批三(缓存失效 + 副作用清扫)
- **arch F7**: clear_specs_cache 统一清三处缓存(specs/_SPEC_GROUPS/_META_JSON)——死钩子变活入口; 注释修正
- **arch F11**: cleanup_side_effects 扩展扫输入目录(extra_dirs)——N37 副作用不再在别处 cwd 永久残留; P0-10 安全保留
- **门禁**: pytest 18 passed / ruff 0 / mypy 0

## [1.4.74] - 2026-10-06

### 自审 P2 批二(活文档 + 数据纪律)
- **docs F7**: PLAN.md 快照刷新 v1.4.55→v1.4.73 + 快照纪律注记(防再漂移) + C1-C3 评审表全状态
- **verified F4**: exec/README.md 数据来源全文档化(24 项/种子/生成方法); 引擎中间产物移出 git 防再入; peaks.xls length 列矛盾修正
- **门禁**: peakanno/peaktss 4 passed / ruff 0 / mypy 0

## [1.4.73] - 2026-10-06

### 自审 P2 批(死代码/句柄/缓存/硬下限)
- **verified F5**: test_report_counts 数据可用性硬下限(≥40/54)——删数据文件必须红; flag 参数跳过判定修正
- **verified F6**: provenance glob 死代码→PROV_COVERAGE 收集+汇总可见(缺口可审计)
- **verified F9**: 报告写入手柄 with 关闭
- **arch F8**: env_fp 身份缓存(mtime/size 短路, 0.7s→0.22s); hash 语义不变
- **arch F10**: 快照校验器裸 except→warn(校验器自身崩溃不再静默)
- **门禁**: pytest 相关 190 passed / ruff 0 / mypy 0

## [1.4.72] - 2026-10-06

### 自审 product F4 响应(最后一个 P1)
- **quickstart/index 数字对齐**: 218 绘图命令→213(权威 version --json); index 218 引擎/82 工具/v1.1.0→213+294+188+80/v1.4.71——版本叙事不再三处打架
- 自审 8 P0 + 21 P1 全部响应完毕

## [1.4.71] - 2026-10-06

### 自审 product F3/F5/F6 响应
- **F3 错误分类误导**: tool-run 执行前输入预检(flag 状态机)——缺失输入直接 TB002(check input path), 不再误导 TB001 wrapper bug; help 提示补 group 前缀
- **F5 list 静默吞参**: list plots 真正过滤绘图分组(原与全量相同); 未知类别报错; list --json 机器可读
- **F6 元数据截断**: _clip_desc 词边界截断+省略号(原 60 字符硬切出 [sor 半词); tool-index 无契约命令显式 schema:null(101/294); tree readiness=None 修复
- **门禁**: pytest 111 passed / ruff 0 / mypy 0

## [1.4.70] - 2026-10-06

### 自审 gate P1×5 响应(门禁体系补全)
- **P1-1 coverage 门禁化**: fail_under=35(实测 37% 基线)——覆盖率不再随测试膨胀无信号下降; omit 规则透明注释
- **P1-2 CI 依赖锁定**: requirements-ci.txt(ruff/mypy/pytest/click/PyYAML/pytest-cov 对齐本地)——防版本滚动 CI 突然红
- **P1-3 报告写入 opt-in**: TBTOOLS_WRITE_REPORT=1 才写 verification_report.json; 默认只读校验(名单漂移→红)——证据文件不被"跑了 pytest"污染
- **P1-4 skip 口径动态化**: CI 不再硬编码 52, 准确数见 -rfs 报告
- **P1-5 Tier-2 保鲜闭环**: nightly-e2e 真实 JAR 回写报告 + create-PR 提交; TTL 严格模式(>90 天 fail)
- **门禁**: pytest 26 passed(相关)/ruff 0/mypy 0/workflow YAML 校验通过

## [1.4.69] - 2026-10-06

### 自审 verified F2 响应(标签诚实性)
- **semantic_checked 分级**: verification_report.json 的 verified_tools 加 semantic_checked 字段(10/54 内容级)——下游可区分"验过内容"与"只验过跑过", 不再标签超卖
- **语义断言升级×4**: barplotter(PNG 像素色≥3)/plotrna(PDF 页面对象)/peakanno(基因-链向映射精确匹配)/keggEnrich(同行断言)——垃圾/错配内容不再通过
- **any() 评估**: 升级后断言函数内部已定向映射, gsea outDir 任一报告语义合理
- **门禁**: pytest 58 passed / ruff 0 / mypy 0

## [1.4.68] - 2026-10-06

### 自审 arch F5/F6 响应(P1×2)
- **F5 impl 双轨守卫死代码 + 选错版**: 冲突守卫移模块尾部 assert(循环内恒假=结构性死代码); cli_load 改 globals(手写版)优先——N3/N27 修复(tableMerge/efpHeat)不再被工厂版旁路; 头注释 13→33 计数修正
- **F6 executor 循环依赖闭合**: 不再绕行 workflow 门面 import 自己的 _execute_step(自引用); 测试 monkeypatch 移到真实位置; workflow re-export 仅作兼容
- **门禁**: pytest 相关 31 passed / ruff 0 / mypy 0

## [1.4.67] - 2026-10-06

### 自审 arch 响应轮(P0×1 + P1×4)
- **P0 F1 snapshot_inputs 反向破坏**: 输出文件被当输入快照 → verify_and_restore 把引擎新产物回滚成旧内容(静默数据破坏, 实测复现)。修复: impl 工厂从 doc 解析 <out...> 占位符 → output_hint 显式剔除(140/170 注册条覆盖) + 回归测试
- **P1 F2 N30 死代码**: 删尾部 ec_out 无条件复位(输出缺失检测永不生效) + err_text 初始化
- **P1 F3 env_fp 活性化**: 消费端比对 env_fingerprint(换 JAR/二进制 → 验证失效降级); 无 JAR 环境(CI)不刷新 env_fp 防交替全降级
- **P1 F4 env_fp 覆盖缺口**: _BINS 从 KNOWN_DEPENDENCIES_STRUCT 派生(补 blast 套件/RNAfold/hmmscan) + 插件 JAR 全量入指纹
- **门禁**: pytest 相关 60 passed / ruff 0 / mypy 0 / gen_metadata --check 全绿(verification=54)

## [1.4.66] - 2026-10-05

### 五视角自审响应轮（5×subagent 独立批判审查 → P0×8/P1×21/P2×24）
- **P0-1 tool-run --dry-run 解析修复**（自审 product F1）：tool 字段取命令名（args[1]）而非最后一个位置参数（输出文件名）；契约测试钉死
- **P0-2 dry-run status 语义修复**（自审 product F2）：status = inputs_valid AND dependencies_ready，新增 status_reasons 数组（此前自相矛盾误导 Agent）
- **P0-3 版本单一源修复**（自审 docs F1/gate P0-3）：pyproject 1.4.46→1.4.65（47 连发从未 bump）；CHANGELOG 补录 1.4.47–65 共 19 个版本
- **P0-4 gen_metadata 进门禁 + 静默 except 可见化**（自审 gate P0-1/P0-2）：mypy 覆盖 scripts/（修 3 错）；--check 补 repo→fresh 双向对比（render 缺失→红，自指陷阱闭环）；3 处写盘 except 改 stderr 告警
- **P1 响应**：xfail 翻红死代码修复（条件式：缺陷在→xfail，修复后→真断言 PASS）；supercircos cfg /tmp 易失→仓库相对路径（WSL 重启可复现修复）；README 数字同步（44→54 / 83→619 / 82→80 / 46→49）；RELEASING.md 发布流程 SOP（两个 P0 根因）；ruff exclude docs/_generated
- **门禁**: pytest 619+ passed / ruff 0 / mypy 0 / gen_metadata --check 全绿（含版本一致性）


## [1.4.65] - 2026-10-05
- **env_fp 覆盖补全**: engine_env_fingerprint 扩展到 13 个外部二进制(shutil.which 回退 plugins/lib/bin)——评审 #115 预审 P1-2 响应闭环
- **门禁**: pytest 619 passed + 52 skipped + 2 xfailed / ruff 0 / mypy 0

## [1.4.64] - 2026-10-05
- **CI skip 口径显式化**: test.yml 加 -rfs 使 EXECUTION_VERIFIED skip 自解释(评审 #115 E4/P2-8 延伸)

## [1.4.63] - 2026-10-05
- **评审 #115 送审包合一**: REVIEW_PACKAGE_115_SUBMISSION.md——输入 + 预审意见 + 逐条响应记录 + 4 焦点问题, 待外发

## [1.4.62] - 2026-10-05
- **评审 #115 预审 P2×3 收尾**: 模式表 P4/P5 移出重分类 + mypy import-untyped 按模块收窄 + skip 记账说明入 PLAN.md

## [1.4.61] - 2026-10-05
- **评审 #115 预审 P1-4**: bin0 缺陷 xfail 固定测试(peaktss/peakanno 低坐标)+ report domain_note 输入域标注

## [1.4.60] - 2026-10-05
- **评审 #115 预审 P1×3 响应**: env_fp 引擎环境指纹(与 contract_fp 并列不合并)+ verified_at TTL 软告警(>90 天); pafref P2 补试实证(引擎缺陷确认); microsyn 改类(数据合成未攻克); 语义断言 SEMANTIC_CHECKS 覆盖 10 工具(EXECUTION_RAN→VERIFIED)

## [1.4.59] - 2026-10-05
- **评审 #115 输入包 + AST 压缩版**: REVIEW_PACKAGE_115.md(v1.4.58 快照, 决策 D1-D4)+ scripts/ast_minfy.py 压缩(command_spec 1136→182 行, ~45% token)

## [1.4.58] - 2026-10-05
- **执行验证台账收官**: 剩余 6 工具归档 EXEC_VERIFIED_LEFTOVER.md(引擎缺陷 4: pafref/tfbsShift/microsyn/memrun + 外部依赖 2: smart/gxfIdAppender)——54/60 = 90% 收官

## [1.4.57] - 2026-10-05
- **执行验证 52→54(90%)**: peakanno+peaktss 收编——GxGOverlapIndexer bin0 引擎缺陷(坐标<10000 无命中)示例数据平移 +1e6 绕过; 属性优先级 gene: ID>geneID>gene_name, mRNA: Parent>geneID>gene_name

## [1.4.56] - 2026-10-05
- **Compound Engineering 三招落地**: 单一活 plan(PLAN.md A/B/C 分区)+ 模式归纳(REVERSE_ENGINEERING_PATTERNS P1-P5)+ PITFALL 补全; 清理 Notung provenance 残留

## [1.4.55] - 2026-10-05
- **执行验证 51→52(87%)**: keggEnrich 收编——真实 .keg 是扁平 5 列表(非 KEGG 层次格式)实锤

## [1.4.54] - 2026-10-05
- **执行验证 50→51(85%)**: plotrna 收编——名称误导实为 coverage plot(--genomeFA/--region/--SAM), spec 重写; 引擎内置折叠算法, RNAfold 依赖虚惊

## [1.4.53] - 2026-10-05
- **执行验证 49→50(83%)**: gsea 收编——query2go 一基因一行 + terms 逗号分隔(否则空 gmt); 归入 table group

## [1.4.52] - 2026-10-05
- **执行验证 48→49(82%)**: notung 收编——引擎忽略 out 参数写派生名; --outputdir tmp + impl glob move; 教训: 不黑名单解析外部工具参数, 用显式 --out 约定 + 原样透传

## [1.4.51] - 2026-10-05
- **执行验证 47→48(80%)**: kallisto 收编——reads 与 transcripts 配对(seed=42 自造 tx.fa + 76bp 切片 reads)

## [1.4.50] - 2026-10-05
- **执行验证 45→47(78%)**: efpHeat/multiEfp 收编——TGA 需 TrueColor type2; multiEfp 引擎硬编码 Windows 路径 → 自建 bridge MultiSuperHeatCli(setter + 反射调私有 initExp + save2SVG)

## [1.4.49] - 2026-10-05
- **执行验证 44→45(75%)**: barplotter 收编——数据格式三连坑(MCScanX collinearity / ctl 4 行逗号分隔 / gff 精确 ID 匹配); 引擎只出 PNG

## [1.4.48] - 2026-10-05
- **mypy 门禁本地落地**: 1.19.1(apt 装, PyPI 被墙)——修复 6 处类型错误, pyproject 配置对齐(ignore_missing_imports 收窄为按模块 override)

## [1.4.47] - 2026-10-05
- **Generated Surface Gate v2(评审 #114)**: P0×2 + P1×4——verified_at 假阳性漂移修复(时间戳与 contract_fp 分离, 否则新鲜度门禁恒定假阳性); --check 升级结构化对比

## [1.4.46] - 2026-10-04

### Generated Surface Gate(评审 #113)——P0×2 + P1×3
- **P0-1 生成物原子同步**: 重 render 让 command_metadata/ai/YAML/counts/README 全部同步到 execution_verified=44(pafviz COMPILEABLE→EXECUTION_VERIFIED); README 26→44——根因是收编新工具后没跑 gen_metadata --render
- **P0-2 gen_metadata --check 升级**: 命令集合检查→内容 freshness 检查(sha 对比 render 前后全部 surface)——模拟篡改 YAML 抓到漂移 1 文件; CI 防 44/33/26 复发
- **P1-1 verification registry 单层 evidence map**: report 加 verified_tools{tool: {level/contract_fingerprint/verified_at/corpus}}(不再 list+details 两段式)
- **P1-2 pafviz contract 语义修正**: note 13 列→PAF alignment 通用描述; KNOWN_RELATIONS 加 pafviz/pafref accepts PAF
- **P1-3 generated surface freshness 测试×3**: 抽查 5 工具四视图一致/counts==live census/verified_tools 单层完整
- **门禁**: pytest 609 passed / ruff 0 / mypy 0

## [1.4.45] - 2026-10-04

### 待办 #1 执行验证 43→44(覆盖率 72%→73%)
- **pafviz**: minimap2 造 PAF(18 列标准格式兼容) + syn 组收编
- 未收编: pafref(PafRefBaseCoverCalc --inPaf/--outTab 后 NPE this.text null 引擎缺陷)/kallisto(reads.fq 与 sequences.fa 不配对, 0 reads pseudoaligned 数据不匹配)
- **门禁**: pytest 606 passed / ruff 0 / mypy 0

## [1.4.44] - 2026-10-04

### 待办 #1 执行验证 39→43(覆盖率 65%→72%)——MEME 套件造真输出
- **memeViz**: 系统 meme 造真 MEME XML, 可视化 12KB SVG
- **motif**: ids 用序列名(非 motif id, 引擎 ID 匹配要求)
- **mastrun**: workingDir 模式 + harness 目录预创建修复(引擎 working directory 须已存在)
- **hmmerSearch**: target.fa 在前 hmmDb 在后(参数序) + hmmbuild 造真库 .raw 产物 890B
- 未收编: tfbsShift(blastp 子进程引擎误判成功为失败, 引擎缺陷)/microsyn(MCScanX 精确格式)
- **门禁**: pytest 604 passed / ruff 0 / mypy 0

## [1.4.43] - 2026-10-04

### 待办 #1 执行验证 35→39(覆盖率 58%→65%)
- **dotplot**: 4 列简化 GFF(chr gene start end, split[3] 需第 4 列) + genePair + 'Genome: chr list' layout
- **layoutheatmap**: layout 在前 expr 在后 + 样本名配对(S1-S4)——此前 expr 表头 A-E 与 layout SampleA-E 不配
- **qdot**: 现成 blast.tab6 + 4 列 gff + Genome: layout(QuickGenomeDotCli)
- **supercircos**: 行导向 config([chrLen]/[link]/[width])
- **门禁**: pytest 601 passed / ruff 0 / mypy 0

## [1.4.42] - 2026-10-04

### 待办 #1 执行验证 33→35(覆盖率 55%→58%)
- **goEnrich**: 造 mini.obo + gene2go.tsv + select_genes 收编(outDir 模式)
- **gel**: javap 反编译拿真实 flag(--MarkerRange/--FragmentRangeArr/--LaneLabels/--outGraph)——FragmentRangeArr 格式是'起点,终点;起点,终点'(逗号分对分号分段), 收编后 145KB SVG
- **产物发现 bug 修复(#113)**: workingDir 目录产物'仅当主产物为空时并入'→'总是并入去重'——goEnrich 的输入被误当主产物 → 目录扫描被跳过 → 真实 .xls 丢失
- 未收编: barplotter(collinearity 与 gff 基因完全匹配要求高)/gsea(set_min=15 数据需求高)
- **门禁**: pytest 597 passed / ruff 0 / mypy 0

## [1.4.41] - 2026-10-04

### 待办 #1 执行验证 29→33(覆盖率 48%→55%)——数据可造路线
- **hclust**: 三列距离文件(此前 dist.tsv 是矩阵被拒——数据格式造对即过)
- **pep2codon**: CDS+蛋白比对 ID 完全一致(此前 cds/pep 不配对)
- **multisyn**: gxf.lst + collinear.lst 可造(此前缺 .lst 文件)
- **preparespecies**: javap 反编译拿真实 flag(--prefix/--inGenomeFa/--inGXF/--outGenomeFa/--outGXF) + InputSpec cli_name 对齐
- 数据入 examples/data/exec/(可重复验证)
- **门禁**: pytest 595 passed / ruff 0 / mypy 0

## [1.4.40] - 2026-10-04

### 待办 #1/#2/#3——执行验证 26→29(48%) + 小修
- **#1 执行验证第二批**: recipBlast(blast 组, RBH 双向比对 4 产物)/mcscanxd(syn 组, MCScanX-SuperFast 4 产物)/msy(syn 组, 多物种共线 SVG)——examples/data 现成数据真实执行, 覆盖率 43%→48%(29/60)
- **#2 错误模板 {cmd} 替换**: runtime/java.py ArgsParser 拒绝提示的 tool-describe 字面量替换为 command_name(实测 tool-describe tpmCalc)
- **#3 README 绘图命令口径命名**: counts.md plot_commands_meta→metadata_plot_commands; README Plotting Engines 218→213(运行时真值)+锚点修正
- 未收编及原因: hmmerSearch(数据非 HMMER 库)/gxfIdAppender(走 RPC 非独立)/notung(数据格式)/kallisto(缺 fastq)/efpHeat/dotplot(形态复杂)
- **门禁**: pytest 591 passed / ruff 0 / mypy 0

## [1.4.39] - 2026-10-04

### workflow.py 拆分 executor.py(评审 #112 P2 收官——四层全拆完)
- workflow.py 1063→636 行(拆分前 1509, 四层拆分后 -58%), executor.py 独立 466 行: 状态机(_load_state/_save_state/_merge_state_step)/resume 闸门(_resume_gate)/执行器(_execute_step/_run_parallel)/入口(run)/validate_artifact
- **命名**: 原 runtime.py 与 tbtools_cli/runtime/ 子包冲突(ImportError)——改 executor.py
- **回归修复**: 拆分后 test_parallel_conformance 3 失败(测试 monkeypatch workflow._execute_step 失效)——_run_parallel/run 改经 workflow 命名空间延迟解析 _execute_step(测试 patch 恢复生效, 生产同源)
- 评审 #112 P2 四层全部完成: identity✅(v1.4.22)/dependency✅(v1.4.36)/compiler✅(v1.4.38)/executor✅
- **门禁**: pytest 588 passed / ruff 0 / mypy 0

## [1.4.38] - 2026-10-04

### workflow.py 拆分 compiler.py(评审 #112 P2 第二步)
- workflow.py 1458→1056 行(-402), compiler.py 独立 428 行: CompiledInvocation(三层 fingerprint)/compile_step_full/compile_step/_resolve/_stable_wf_id/resolve_input_binding/_bind_slots/_plan_to_spec/_default_args/WorkflowError
- workflow.py 从 compiler import 并 re-export(旧代码/测试 from workflow import compile_step_full/WorkflowError 仍可用, 符号同源验证); 无循环依赖(compiler 只依赖 identity/dependency)
- **门禁**: pytest 588 passed / ruff 0 / mypy 0

## [1.4.37] - 2026-10-03

### verification 证据对象投影(评审 #112 P1 收尾)
- ai/tools/*.json 的 verification 此前只有 level(EXECUTION_VERIFIED), 缺证据详情——Agent 无法判断证据新旧/是否匹配当前 contract
- gen_metadata 从 verification_report.json 读 execution_verified_details, ai/tools/*.json 加 verification_details{contract_fingerprint, verified_at, corpus}
- test_metadata 加投影断言(执行验证工具必须带证据对象)
- **门禁**: pytest 588 passed / ruff 0 / mypy 0

## [1.4.36] - 2026-10-03

### workflow.py 拆分 dependency.py(评审 #112 P2)
- 新建 tbtools_cli/dependency.py(92 行): resolve_dependencies(spec, cache) 三级优先(manifest→DEP_VERSION_ARGS→heuristic) + 模块级 _DEP_VERSION_CACHE(带可执行文件身份缓存 key)
- workflow.py 1509→1458 行: 探测段替换为调用; _DEP_VERSION_CACHE 改 re-export 同一对象(旧代码/测试 from workflow import 仍可用且共享状态)
- 功能等价验证: muscle 版本探测正常, identity/semantic/workflow/conformance 全绿
- **门禁**: pytest 587 passed / ruff 0 / mypy 0

## [1.4.35] - 2026-10-03

### Contract Agent Surface Freeze(评审 #112)——P0×2 + P1×3 + P2×2
- **P0-1 完整 canonical snapshot equality**: overlay 从"只查 inputs name+format"升级为 canonical_snapshot(code)==yaml_to_snapshot(yaml) 全量比较——**立即抓到 59 个 output_slots/outputs 漂移**(此前盲区); canonical_snapshot 镜像 to_metadata_entry 的 slots 投影逻辑; test_yaml_migration 升级为全量 equality
- **P0-2 删除 YAML→runtime capability 兑底**: 代码没 capability 就是没有, 快照有即过期 warn
- **P1 ai/ manifest 统一投影**: ai/tools/*.json 补齐 semantic_fp/readiness/verification/relations/output_slots/parameters/dependencies/aliases(此前削薄=双世界分裂); tool-index.jsonl 加 readiness/verification/semantic_fp(低体积高价值筛选字段); relations.json 从 CommandSpec 派生含 GROUP_RELATIONS fallback(此前直读 KNOWN_RELATIONS 双轨)
- **P2 gen_metadata 命名** "唯一数据源"→"唯一 metadata projection"; README 同步
- **门禁**: pytest 587 passed / ruff 0 / mypy 0

## [1.4.34] - 2026-10-03

### Contract Integrity Freeze(评审 #111)——P0×3 + P1×3
- **P0-1 YAML 不再覆盖 runtime truth**: _apply_contract_overlay 从覆盖改校验(实测 0 工具依赖 YAML 兑底)——不一致 warn 提示重跑 gen_metadata, 不再静默回退旧快照
- **P0-2 InputSpec.cli_name 进 identity + metadata**: canonical_contract inputs 加 cli_name(影响真实 argv 的字段必须进 fingerprint——1.4.31 加字段 1.4.33 才发现漏接); to_metadata_entry 导出 inputs cli_name(Agent 可见引擎真实 flag)
- **P0-3 验证数字统一 26**: counts.md/version --json 的 execution_verified = EXECUTION_VERIFIED + CONFORMANCE_VERIFIED(census 单源); README 14→26; 发布流程须跑 gen_metadata --render(默认模式不导出 YAML/不更新 counts)
- **P1-1 test_yaml_migration 独立真源比较**: _skip_overlay 拿纯代码 spec 对比快照; 修 10 个上限盲区(字母序靠后的 tpmCalc 从未被查——篡改测试实锤)
- **P1-2 tool-readiness.md 5/5 改 metadata coverage**: 与 readiness(FULL) 严格区分并注明勿混读
- **P1-3 execution-relevant fields 审计测试**: InputSpec 字段未进 canonical=测试失败(防复发)
- **门禁**: pytest 584 passed / ruff 0 / mypy 0

## [1.4.33] - 2026-10-03

### 代码真源 vs YAML 生成快照定型(评审 #110 建议③——四项全部收官)
- **实测**: contracts/tools/*.yaml 是 gen_metadata 单向导出(先清空重写, CommandSpec→YAML), 但 load_contracts docstring 仍声称 "YAML 声明优先"——文档与实现矛盾, 会让维护者把 YAML 当真源(1.4.15-1.4.24 双向覆盖复发)
- **修复**: load_contracts/_apply_contract_overlay/构建注释 "YAML 胜出" → "代码真源优先, YAML 是生成快照"; contracts/README.md 新增真源优先级图+覆盖行为+修改契约正确方式+历史教训; test_yaml_migration 文档更新为快照一致性验证(测试逻辑不变, 行为仍通过)
- **门禁**: pytest 581 passed / ruff 0 / mypy 0
- **评审 #110 四项全部完成**: ①验证分层(v1.4.32) ②SpecRegistry(v1.4.29) ③YAML 真源改名(v1.4.33) ④执行实证 14→26(v1.4.30-31)

## [1.4.32] - 2026-10-03

### 验证分层(评审 #110 建议①)——CONFORMANCE_VERIFIED + 两维正交
- **新层**: CONFORMANCE_VERIFIED(金链级) = EXECUTION_VERIFIED + golden chain 全断言(compile→execute→artifact→sha256→provenance→artifact_id); volcano 首个标杆(test_conformance 金链驱动)
- verification_level/census/contract_coverage 加 CONFORMANCE_VERIFIED 层
- verification_report.json 加 conformance_verified 名单; contract fp 变 → 连 conformance 一并降级
- **describe --json 暴露两维**: readiness(FULL/PARTIAL/LEGACY) + verification(CONFORMANCE/EXECUTION/COMPILEABLE/DECLARED)——Agent 直接可见"契约写得完整" vs "真的跑过", 防混淆
- gen_metadata/to_metadata_entry 注入两维进 command_metadata.json
- **门禁**: pytest 581 passed / ruff 0 / mypy 0

## [1.4.31] - 2026-10-03

### InputSpec cli_name——ArgsParser 工具契约与引擎参数名解耦(评审 #110 建议④)
- **发现(tpmCalc 实证)**: spec inputs 名(counts/lenInfo)与引擎真实 ArgsParser flag(--countsTable/--lenInfo)脱节——build_argv 按位置/缺省名拼, 引擎必然拒绝(Invalid arguments)
- **修复**: InputSpec 加 cli_name 字段; build_argv 任一 input 有 cli_name → 按 --flag value 拼; tpmCalc 标 cli_name + named_flags(--outTable)
- **执行验证 26/60(覆盖率 43%)**: tpmCalc 收编 EXEC_VERIFIED
- **门禁**: pytest 581 passed / ruff 0 / mypy 0

## [1.4.30] - 2026-10-03

### 执行验证 14→25(评审 #110 建议④)——覆盖率 23% → 42%
- **bridge 位置参数**: barplot(列名 Term/Pvalue 非索引)/circos/gxfAttr/gxfSplit/tableMerge(--inFileArr 形态)
- **direct --flag 风格**: longestorf(--inFa/--outORFs)/venn3/venn4(--List1..4 --graph --prefix)
- **plugin/manual**: newickRename(--inNwk/--renameMap/--outNwk)/treeRooting/upset
- 全部 examples/data 现成数据真实执行验证(产物非空 + sha256 完整)

### 产物发现三改进(实测驱动)
- discover_outputs: 0B 占位文件不算真产物, 继续 prefix 发现(longestorf 写 out.fa 0B + NoORF/Pep.fa)
- tool-run provenance 循环: 0B 产物走 prefix 发现(此前 _found_any 提前置真跳过兜底)
- tool-run workingDir 目录产物: meme/mast 类产物在目录内(t0 后新建文件, 防把输入当产物)

### 可信度发现
- **memerun 声明 FULL 但 JAR 缺 QuickRunMEME 类**(NoClassDefFoundError)——契约声明≠可执行, 记录不收入验证池
- **门禁**: pytest 580 passed / ruff 0 / mypy 0

## [1.4.29] - 2026-10-03

### SpecRegistry(评审 #110 P1)——294 spec 一次性构建缓存
- build_command_specs() 加模块级缓存(force=True 强制重建) + clear_specs_cache()
- Agent 高频链 search/describe/plan/validate/run 此前每次重建 294 spec(~105ms);多步 workflow 编译每 step 一次 = 50 步 5 秒纯 spec 重建——现缓存命中 0.000ms
- monkeypatch 场景兼容(测试可 patch 构建函数), clear_specs_cache() 供 KNOWN_* 变更后失效
- **门禁**: pytest 569 passed / ruff 0 / mypy 0

## [1.4.28] - 2026-10-03

### 可信度证据链(评审 #110)——P0×2 + P1×4
- **P0-1 execution-scoped artifact discovery**: discover_outputs 加 created_after（mtime >= 执行开始）——防 prefix discovery 捡旧 sibling 文件（程序失败/未重新生成时旧产物被当当前产物=假阳性）；tool-run 两处调用传 t0
- **P0-2 plan 纯静态**: plan() 加 runtime_resolve 参数（默认 False）——规划/validate 不读输入 sha/不探测依赖；run() 显式 True 保留完整 execution_fp（resume 篡改检测，曾因静态化导致闸门失效，已回归修复）
- **P1 verification 绑定 contract_fp**: execution_verified 记录 contract_fingerprint+verified_at+corpus——加载时比对当前 fp，contract 修改旧验证自动降级（篡改测试：volcano fp 变→EV 14→13）
- **P1 counts.md 权威化**: agent_ready_full/partial/legacy + execution_verified 进 counts.md；README 数字统一（59→60 FULL / schema-capable 129→63 有 inputs 契约）
- **门禁**: pytest 569 passed / ruff 0 / mypy 0

## [1.4.27] - 2026-10-02

### Contract 可信度(评审 #109)——执行验证 4 → 14
- **EXEC_VERIFIED 池扩充**: heatmap/pca/muscle/sixframe/genestructure/genelocgff/venn2/trimal/seqlogo/iqtree 10 个工具用 examples/data 现成数据真实执行验证(产物非空)——执行验证覆盖率 7% → 23%(verification_report.json 自动更新)
- **tool-run 无 provenance 兜底**: muscle(Python 直调)/iqtree(java 桥)不写 .tbtools.json 但产物真实——此前 artifacts=[] 让 Agent 看不到结果; 现兑底 build + prefix 发现
- **conformance_verified 测试修复**: provenance 断言由参数位置推断(3+ 参数越界)改为产物路径/glob 定位; provenance 降为加分项
- **门禁**: pytest 569 passed / ruff 0 / mypy 0

## [1.4.26] - 2026-10-02

### MCP/CLI DX 优化(评审 #109)
- **错误命令建议全工具名**: candidates 加入全量 spec 工具名(此前 'recipblast' 只匹配分组名 'blast')——大小写不敏感 + 模糊匹配 + 结果映射回真实大小写(recipblast→recipBlast)
- **MCP search 空输入引导**: 返回用法示例(非裸 {})——Agent 首次调用即知姿势
- **测试**: tests/test_dx_quality.py 6 用例(纠错/引导/Agent 工作流链 search→describe→validate/version 权威计数)
- **门禁**: pytest 559 passed / ruff 0 / mypy 0

## [1.4.25] - 2026-10-02

### Semantic Resolver 覆盖率(评审 #109)——语义发现 50% → 100%
- **语义索引**: search hay 加入 capabilities/relations 层(此前只匹配 name+help+class 字面词, 浪费 planner 已验证语义数据)
- **词干化**: extract↔extraction / genome↔genomes(仅词干相等防噪音工具)
- **停用词过滤**: by/id/list/of/with 不参与 AND('extract sequences by id list' 噪音词稀释语义)
- **排序重构**: 语义命中(能力/关系) > 全名精确 > name 凑巧——'blast sequences' 的 recipBlast(能力真源) 曾排 bestid(名字含 blast)之后
- **测试**: tests/test_search_quality.py 17 用例;门禁 pytest 553 passed / ruff 0 / mypy 0

## [1.4.24] - 2026-10-02

### Planner 决策质量(评审 #109)——规划正确率 29% → 93%
- **spec 数据根治**: 关键工具补精确 relations/capabilities(recipBlast/extractFasta/statFasta/dnDsCalculate/hmmsearch/sixframe 等曾全空或 seq 组万能中介污染); produces 补真实输出格式(statFasta→TSV 等)
- **算法改进**: _accepts 格式族语义匹配(aln↔ALIGNMENT); 起点截断不再丢 goal 命中工具; MULTI_INPUT 惩罚仅绑定失败才触发(recipBlast 曾被 -0.4 压制); capability 短语完全命中加分(2+ 词防噪音); 链起点与 goal 无关扣分; 透传跳覆盖链首
- **架构债清偿**: YAML contract 覆盖反向——代码真源(KNOWN_*)优先, YAML 仅兑底(旧 YAML 快照曾循环覆盖新标注, 评审 #108 单一真源方向)
- **测试**: tests/test_planner_quality.py 16 用例(教程实证 13 场景 + 高置信 + 无无关起点 + 数据无污染回归)
- **门禁**: pytest 536 passed / ruff 0 / mypy 0

## [1.4.23] - 2026-10-02

### 评审 #108 遗留 P1 三项完结
- **resolver 读 dependency_manifest**: KNOWN_DEPENDENCIES_STRUCT 每条目加 executable/version_args(hmmsearch→-h, muscle→-version, iqtree2→--version 等 17 条);解析优先级 manifest → DEP_VERSION_ARGS 表 → heuristic;contract-driven 终态达成
- **static_compile/runtime_resolve 分拆**: compile_step_full + CompiledInvocation 支持 runtime_resolve——validate 走 static 编译(不读输入内容/不 fork 外部工具, 保持纯静态检查), run 走完整 runtime identity;静态 contract/binding fp 两模式一致
- **identity 测试独立成文件**: TestReview107/108 性质矩阵拆到 tests/test_identity_properties.py;command_metadata.json 重新生成(投影同步)
- **门禁**: pytest 516 passed / ruff 0 / mypy 0

## [1.4.22] - 2026-10-01

### identity cleanup / dedup / invariant freeze(评审 #108)
- **P0 删重复常量**: 旧 CANONICAL_EXECUTION_FIELDS(含 outputs)残留已清——实测 fingerprint 本用无 outputs 版, 但两套常量并存=漂移风险, 现 EXECUTION_CONTRACT_FIELDS 全仓唯一
- **P0 fingerprint 唯一入口**: execution_contract_fingerprint 直接消费 canonical_execution_contract()(不再手动 filter, 杜绝 canonical 说 A / fp hash B)
- **P1-1 outputs projection 回归测试**: projection 变 → contract_fp/execution_fp 不变(output_slots 唯一真相)
- **P1-2 schema_version 拆分**: workflow_schema_version / contract_schema_version 两概念不再模糊
- **P1-4 拆出 identity.py**: canonical + fingerprint + 常量独立模块——解 command_spec↔workflow 双向依赖(均只向下依赖 identity); workflow 保留向后兼容 re-export
- **门禁**: pytest 514 passed / ruff 0 / mypy 0

## [1.4.21] - 2026-10-01

### identity 边界清理(评审 #107)—— P0×2 + P1×5
- **P0① schema_version 进 execution contract fp**: 新增独立 CONTRACT_SCHEMA_VERSION(与 workflow schema 解耦);契约结构升级→旧 fp 自动失效(resume 安全)
- **P0② binding 保留 symbolic refs**: 路径抽象但 ref 身份保留({input.genome}≠{input.transcriptome});修复"抹 ref 致不同语义 workflow 同 fp"
- **P1③ binding 不再混 content sha**: 删截断 16hex 层;binding=接线 / execution=接线+内容(full sha 在 execution input_shas)
- **P1④ semantic_fp full 64 hex**: metadata 存 full + short(展示截断, identity 不截)
- **P1⑤ outputs 退出 execution contract**: output_slots 唯一真相(outputs 是投影, 投影实现变≠契约变)
- **P1⑥ dep cache 带可执行身份**: name+path+mtime+size——长期 Agent 进程不再锁旧版本
- **P1⑦ DEP_VERSION_ARGS 表**: muscle/-version 等精确版本命令, 停止纯 heuristic 猜
- **测试**: TestReview107PropertyMatrix 10 性质矩阵;门禁 pytest 510 passed / ruff 0 / mypy 0

## [1.4.20] - 2026-10-01

### identity closure(第 31 份评审) + 门禁修复
- **P0-1 tool + schema_version 进 execution contract identity**: 同契约形状换工具→fp 不同(不再错误复用)
- **P0-2 relations 进 semantic canonical**: semantic_fp 名副其实(改 relations→fp 变)
- **P1-3 input sha full 64 hex**(不再 [:16])
- **P1-4 semantic_fingerprint 导出 metadata**(describe 可见; execution 侧不进)+ provenance 三层 fingerprint 补写
- **P1-5 六个性质测试**(tool/schema/relations/capability/input 路径/input 内容)——路径换同内容 fp 不变(内容寻址), 内容变 fp 变
- 门禁: pytest 500 passed / ruff 0 / mypy 0

## [1.4.19] - 2026-09-28

### identity 数学化收官(第 30 份评审)
- **binding_fp 纯符号化**: 只吃 raw symbolic binding(resolved 路径污染修复)
- **四层拆分**: Execution Contract / Semantic Metadata / Binding / Execution
- **dependency identity contract-driven**: spec.dependencies 声明解析
- **full SHA256**: 内部 64 hex,显示层截断

## [1.4.18] - 2026-09-28

### identity 数学定义干净化(第 29 份评审)
- **binding_fp 用 raw symbolic binding**(替换前 refs,非 resolved 路径)
- **canonical_contract() 统一契约指纹源**(含 output_slots/layout 等全字段)
- **resume 严格化**: 旧 state 无 fp → 一律重跑(假成功风险修复)
- **dependency identity**: execution_fp 含外部依赖版本(muscle/iqtree2)
- **sixframe 语义修正**(slot pep→dna,note 原文写反)
- identity→resume 回归矩阵 6 用例

## [1.4.17] - 2026-09-28

### identity→resume 纵贯(第 28 份评审)
- **fingerprint 数学语义重定义**: contract_fp=契约本身/binding_fp=符号绑定/execution_fp=contract+binding+输入 sha+runtime
- **fingerprint→resume 闸门**: state.fp ≠ 当前 fp → 重跑(篡改输入实测触发)
- **binding 路径禁 output guessing**(启发式回退只限 legacy args)
- **contract 修正**: volcano 输出 table→plot;muscle content_type→sequence(DNA+蛋白双兼容)
- **verification_census 加 COMPILE_VERIFIED**

## [1.4.16] - 2026-09-28

### slots 为真相(第 27 份评审)
- **P0【bug 修复】overlay 优先读 YAML output_slots**(slots 为唯一真相,outputs 为投影;v1.4.15 自引入的 content_type 丢失修复)
- **三层 identity**: contract_fingerprint → binding_fingerprint → execution_fingerprint
- **COMPILE_VERIFIED 指标**(测试产物名单,与声明级区分)
- contracts 重生成(63 个带 output_slots)

## [1.4.15] - 2026-09-28

### 语义统一(第 26 份评审)
- **OutputSpec 统一**: overlay 同步重建 output_slots;output_formats 唯一访问口
- **Binding Resolver**: resolve_input_binding(content_type 正式进入绑定决策)
- **output-slot→input-slot 配对匹配**;**串/并 warnings envelope 统一**
- **CompiledInvocation contract_fingerprint**;**deterministic ready queue**
- Tests A–E(overlay round-trip/output 一致/binding resolver/envelope parity/多 slot)

## [1.4.14] - 2026-09-28

### 旧语义旁路清理(第 25 份评审)
- **validate 消费 CompiledInvocation.outputs**(与 run 同语义,不再 argv 猜)
- **contracts 缓存文件指纹**(mtime+size 每文件 tuple)
- **overlay presence 检查**(显式 []=有意清空)
- **并行 persistence warning 收集**;**绑定 content_type 嗅探**
- **重名契约记录**(CONTRACT_DUPLICATE_NAME);schema 命名区分

## [1.4.13] - 2026-09-28

### 真相链补全(第 24 份评审)
- **verification 无 fallback**: 报告不存在→0 EXECUTION_VERIFIED(不再假验证;22 轮脚本回归修复)
- **Planner 首槽登记**: step1 首必填输入也进 required_inputs(三槽全列)
- **YAML 加载错误可见**: contract_load_errors()(CONTRACT_LOAD_ERROR)
- **named_flags/layout 投影 metadata**;_content_compat 遍历全部 output_slots
- **artifact 锁失败警告**(不再无保护继续)

## [1.4.12] - 2026-09-28

### Runtime 语义升级(第 23 份评审)
- **CompiledInvocation**: compile_step_full 返回结构(argv+inputs+outputs+parameters);Runtime 消费编译结构,不再从 argv 反推语义
- **Planner Template 正式化**: type=workflow_template + required_inputs 汇总(不再"看似可执行")
- **schema_version 全统一**: run/validate/planner 全部 WORKFLOW_SCHEMA_CURRENT
- **metadata 语义导出**: content_type/output_slots/named_flags(volcano=table/muscle=alignment)
- **register 警告记录**(register_warning 进结果)
- 🐛 specs_from_scans content_type 缩进 bug 修复(投影测试抓到 13 条不等价)

## [1.4.11] - 2026-09-28

### 语义收口 + Runtime conformance(第 22 份评审)
- **schema_version 统一**: planner 输出用 WORKFLOW_SCHEMA_CURRENT(消灭 1.0 硬编码)
- **cancel↔Popen 注册竞态修复**: 注册后立查 cancel_event(漏杀悬挂修复)
- **_bind_slots 模块级**: Planner 统一调用;required_workflow_inputs 元数据(机器可读"必须提供")
- **persistence 不静默吞**: _merge_state_step/artifact.register 返回警告文案
- **OutputSpec 输出槽位**: KNOWN_OUTPUT_SLOTS 8 工具;_content_compat 槽位级
- **verification 报告驱动**: verification_report.json(compile 59/exec 4);无报告不回退过时名单

## [1.4.10] - 2026-09-28

### 同一真相链(第 21 份评审)
- **P0-3【真 bug】并行 state "wf" 落盘**: _run_parallel 显式 workflow_id(不再 by_id.get('_wf_id','wf'))
- **Resume identity 校验**: state.workflow_id 不匹配→忽略旧状态全量执行
- **validate 干跑前拓扑排序**: 乱序 workflow 误报 COMPILE_ERROR 修复
- **Planner 解析统一**: multi_input_unsupported 矛盾消除(requires_workflow_inputs)
- **KNOWN_OUTPUT_CONTENT_TYPES**(A 侧输出语义)+ 首槽兼容标记

## [1.4.9] - 2026-09-27

### 半成品完工(第 20 份评审)
- **_bind_slots 正式接入 Planner**: MULTI_INPUT 多必填工具入选(dict slot 绑定;recipBlast 实测)
- **slot 匹配三级**: EXACT/COMPATIBLE/INCOMPATIBLE/UNRESOLVED(format+content_type)
- **_content_compat slot 级**: 读首必填 InputSpec.content_type(不再工具级查表)
- **并发 Runtime conformance**: 失败传播/崩溃恢复/并发 merge 3 用例
- **YAML 迁移规则**(test_yaml_migration)+ **verification 报告驱动**(verification_report.json)
- **contract_coverage 三层**: DECLARED 231/COMPILEABLE 58/EXECUTION_VERIFIED 5
- **schema_version 正式化**: 1.0=args/1.1=binding/2.0=binding-only

## [1.4.8] - 2026-09-27

### Runtime 工程阶段(第 19 份评审)
- **cancel fail-fast 打通**: cancel_event + killpg 在飞进程组 + 状态收敛(未启动 skipped)
- **每步原子落盘**: _merge_state_step(崩溃后 resume 可见已完成步骤)
- **多输入 binding**: dict slot 绑定({query, subject} 按 InputSpec 声明序展开;RBH 全链路实测)
- **content_type slot 级**: KNOWN_INPUT_CONTENT_TYPES(pep2codon cds=dna/pep_aln=protein)
- **layout 三漏洞**: 负 index 拒/required 覆盖检查/bool flag 语义
- **Contract YAML loader**: 190 个 YAML 正式覆盖层(merge 保 content_type 标注)
- **Execution Verification 分级**: EXECUTION_VERIFIED/COMPILEABLE/DECLARED
- 并行/cancel/resume conformance 测试 8 用例

## [1.4.7] - 2026-09-27

### 架构收口 + 语义层(roadmap 三项 + Phase 3)
- **CommandSpec 兼容层 Phase 3**: cli.py/cli_top.py/test_metadata.py 三处 legacy import 全部迁移到 CommandSpec;grandfather 白名单清零——CommandSpec 唯一入口达成
- **DAG 并行 scheduler**: ready-queue + ThreadPoolExecutor(默认 2 workers)+ fail-fast;**竞态修复**(在飞步骤结果丢失)
- **biological semantic type 功能化**: InputSpec.content_type(30 工具标注)+ fasta 语义嗅探(dna 进 blastp→警告)+ planner 语义边罚分
- **多输出 Artifact**: discover_outputs(prefix 型输出兄弟文件发现);mcscanx 回归 Tier-2
- **resolve_artifact()**: 返回完整 Artifact 对象;search envelope schema_version 统一
- **capability ontology 全覆盖**(51 能力)+ JDK/JRE 文档统一(JDK 11+,JRE 不够)

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
