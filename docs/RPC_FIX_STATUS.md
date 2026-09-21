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

## 批次 1 — 复活类 N24/N26/N27 ⏳ 子任务 A 进行中
## 批次 2 — RPC 稳定性 N34/N35/N40 ⏳ 子任务 B 进行中
## 批次 3-5 — 待批 1/2 收口后统一 review + commit
