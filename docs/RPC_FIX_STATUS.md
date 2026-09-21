# RPC 交付包修复状态(N1–N41)

> 来源: `workspace/TBtools_RPC测试交付包.zip`(WorkBuddy Windows 穷举测试,~1665 项/~812 通过)
> 修复清单: `workspace/workflows/tbtools_cli化_修复清单.md` | 总清单: `workflows/tbtools_cli化_总清单.md`

## 批次 0 — P0 输入保护 ✅ 完成(2026-09-21)

### 输入保护基础设施(core.py,已接入 run_java 统一入口)
- `snapshot_inputs()`: 调用前快照输入文件(≤50MB 复制备份,>50MB 记 size+mtime),自动排除输出参数名/-cp/-jar
- `verify_and_restore()`: 调用后 sha1 比对,被引擎改写/删除的输入自动恢复并告警
- `cleanup_side_effects()`: 删除本次调用新产生的 TBtools 副作用残留(`*.TBtools.fa*`/`*.TBtoolsDB.*`/`*.tmpClean`/`*.sortedGXF` 等)
- N19 特判: query 重定向临时副本,仅当引擎改写副本(sha1 变)才把结果搬到 --outTable,防"静默成功"

### 三个缺陷单点修复(均实测通过)
| 缺陷 | 修复 | 验证 |
|---|---|---|
| **N19** findBestHomologyBatch | 新 impl `_findBestHomologyBatch_impl`: 真实参数 `--inQueryProteinSet/--inSubjectProteinSet/--targetIdList/--outDir`(旧 `--queryFasta/--outTable` 兼容);自动生成 targetIdList;自动创建 outDir;产物校验防静默成功 | `Best Forker Result:q1,q2 ==> s1,s2`,产物 All.s5.ids/All.s10.ids 落盘,输入 md5 不变 |
| **N23** mirnatarget | 新 impl 恢复完整管线: `ssearch36 -w 100 -W 25 -E X -m 10 -T 1 -i -U <mirna> <target>` → TargetScoreCli;输出落盘校验;拒绝输出==输入 | 输出表正确(ath-miR166→AT_TARGET 1.8e-14),输入 md5 不变 |
| **N25** gffCdsPhaseCorrector | 新 impl 命名参数→位置参数(`<in> <correct> <problematic> <report>`);拒绝 in==out 防覆盖 | "Processing completed successfully!",输出 464B |

### N37 残留清理
- examples/data 26 个副作用残留 → `/tmp/tb_n37_trash/`(trash 化,非删除);复查 0 残留

### 测试
- 新增 `tests/test_p0_protection.py` 11 项(snapshot/restore/cleanup/三 impl 防覆盖)
- 全量: **80 passed, 1 skipped**(`test_rpc_methods_no_server` 语义待批次 2 N34/N35 自动拉起后更新)

## 批次 1 — 复活类 N24/N26/N27 ✅ 完成（commit a527916）
- N24 getLongestCompleteORF → GetLongestORF 转发（JavaFX 无 main 类弃用）
- N26 msy 表驱动参数错位修复（显式拼 GenericCli: MultipleSpeciesSyteny plot + 3 setter）
- N27 multiEfp/efpHeat fake DatatypeConverter 源码入库 + ensure_bridge 自动重建 + direct classpath 补 build/；附带 efpHeat --key value 修复

## 批次 2 — RPC 稳定性 N34/N35/N40 ✅ 完成（commit c2eab5d）
- N34/N35: pid 文件 + 健康探针 + call/methods 前置自动拉起；rpc stop/status/--force；OOM 转储；代理绕过（N41）
- N40: javap 归因=引擎 IQ-TREE stderr 管道未排水（引擎级），包装层超时+预检加固

## 批次 3 — 其余 P1（N1/N2/N28/N30/N38）✅ 完成（commit 待）
- N1 get_java(): TBTOOLS_JAVA > PATH > 常见路径，绝对路径调用告别 PATH 误导
- N2 GUI 工具黑名单（RNAplotAdvance 等 5 个）无参即退不弹窗
- N28 Gxf 族 GTF 输入预检警告（引擎 GENCODE NPE 无法修，至少不裸奔）
- N30 check_missing_outputs 强输出参数存在性校验（长路径/静默失败→非零退出）
- N38 RPC 空消息/占位符友好兜底
- 测试: 81 passed 1 skipped（test_rpc_methods_no_autostart 改 -p 9999 确定性语义）

## 批次 4-5 — P2 快赢 + P3 收尾 ✅ 完成（commit ede7eb8）
- N3 tableMerge: 引擎真实参数 --inFileArr/--inColIndexArr/--outTable；位置参数兼容 impl；包装层首参跳过校验
- N10/N11 空输入文件统一友好报错（引擎 0 字节裸崩 statFasta/heatmap 解决）
- N12 heatmap 补 --preset；N13 gwas 分组补齐（vcfAddID/mimicVqsr）；N14 doctor xvfb 平台感知
- N15 banner 数字对齐；N16 check 识别 GFF3；N20 check 失败非零退出；N29 mirnaIdentify docstring；N32 gel 无参防挂
- N33 help 渲染接入 command_metadata.json（150 可选位透出）
- CHANGELOG 已更新；全量 81 passed 1 skipped
- 回归脚本 Linux 化：交付包 run_p*.py 为 Windows 专用（路径/taskkill），Linux 侧由 pytest 81 项 + run_examples 兜底；如需在 Windows 回归环境复跑可直接用原脚本

## 全部批次状态（N1-N41 修复完成度）
| 批次 | 内容 | 状态 |
|---|---|---|
| 0 | P0 输入保护 N19/N23/N25 + N37 | ✅ a527916 |
| 1 | 复活类 N24/N26/N27 + efpHeat | ✅ a527916 |
| 2 | RPC 自愈 N34/N35 + N40 归因 | ✅ c2eab5d |
| 3 | 其余 P1 N1/N2/N28/N30/N38 | ✅ 7826fe5 |
| 4 | P2 快赢 N3/N10-N16/N20/N29/N32/N33 | ✅ ede7eb8 |
| 5 | P3 收尾/文档/测试 | ✅ 本文件+CHANGELOG |
| 4b | 补充核查 N4/N5/N6/N21/N22/N36 | ✅ 本批 |

### 补充核查（用户质疑后逐条对照缺陷速览，20:02）
- **N4 cubeheatmap**：引擎对 group 列数假设严格（官方 cube_group.tsv 仍崩，引擎缺陷确凿）→ docstring+PITFALL 文档化 group 格式（非修引擎）
- **N5 groupedbar**：数据格式=每行 group\tvalue（非矩阵）→ docstring 文档化；矩阵输入引擎崩溃已注明
- **N6 extractFeatureFromGTF**：main 硬编码路径；核心 setter 齐全 → **桥已写**（bridges/ExtractFeatureGTFCli.java，setGtfFile/preProcess/setInGenome/process 跑通引擎流程）；⚠️ 输出落盘语义未完全逆向（process 返回值空），**未注册为正式命令**，保留资产待后续确认
- **N6 parallelMD5Check**：位置参数式 `<md5_list> [threads]`，注册表直通参数形态易错（ec=3）→ 新增 _parallelMD5Check_impl 参数校验+文档化，实测 OK:1 FAILED:0
- **N21**：TodoList.updateTask/moveTask/deleteTask 参数名为 `id`（引擎 RPC 约定，非 REST 惯例）→ 保持原名，此处文档化；
- **N22/N36**：Gxf 族对 BED 输入报误导性『can not decide GFF3 or GTF』+ GxfStat NPE → _warn_gtf_input 扩展：.bed 输入明确警告不支持格式
- 引擎级不修（已文档化）：N28 Gxf 族 GENCODE GTF NPE、N39 GxfGeneDensityProfiler、N40 引擎超时、N38 家族 3 方法、N17 校验深度、N31 二进制垃圾 NPE、N36 GxfStat NPE、N4/N5 引擎崩溃
