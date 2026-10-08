# 执行验证遗留状态（EXEC_VERIFIED_LEFTOVER.md）

> 2026-10-04 归档 · 执行验证 56/60 = 93%(memerun/microsyn 已移出)于 v1.4.57
> **2026-10-08 同步(N6)**: 现为 56/60 = 93%(memerun 转正 + microsyn 收编);
> 定性总表按「已关闭/活遗留/归档/悬空」四段(见下方状态列), 结论段与头部同源。
> **2026-10-07 更新**: memerun 已转正(v1.4.88 实测修复, EXEC_VERIFIED 55); microsyn 已收编(v1.4.91, multi/ 合成数据形态匹配+完整区间参数复攻成功, EXEC_VERIFIED 56);
> pafref/tfbsShift 已建 xfail 活测试固定(v1.4.88 TestKnownDefectsXfail)。剩余 3 个: pafref/tfbsShift(引擎缺陷, JAR 升级自动翻红)/smart(服务端已变, 归档)。
> 剩余 6 个工具为引擎级缺陷或外部依赖，**已定性、不再重复攻坚**（复攻条件见各条）。
> 活 plan 见 `docs/_worklog/PLAN.md`（A 区已完结）；本文件是 A 区遗留的权威存证。

## 定性总表

| 工具 | 类别 | 根因 | 证据（波次） | 复攻条件 | 活监控（自审 verified F7） | 状态(v1.4.91) |
|:--|:--|:--|:--|:--|:--|:--|
|:--|:--|:--|:--|:--|:--|
| pafref | 引擎缺陷 | PafRefBaseCoverCalc `--inPaf/--outTab` 后 `this.text` NPE | v1.4.45 | 需上游修 JAR | ✅ v1.4.88 建 xfail 活测试(修复自动翻红) | 活遗留(xfail 锚点) |
| tfbsShift | 引擎缺陷 | blastp 子进程误判成功为失败（子进程状态码逻辑反） | v1.4.44 | 需上游修 JAR | ✅ v1.4.88 建 xfail 活测试 | 活遗留(xfail 锚点) |
| microsyn | ✅ 已收编 | 原"数据合成未攻克"——multi/ 合成数据(sp1/sp2.gff+sp1_sp2.collinearity)形态恰好匹配 | v1.4.44 → v1.4.91 | 完整区间参数(--chr1/start1/end1...) + 数值染色体名 | ✅ v1.4.91 收编(0.55s SVG 双物种基因名) | ✅ 已关闭(10/07 收编, EXEC_VERIFIED 56) |
| memerun | ✅ 已转正 | JAR 缺类缺陷已随插件更新修复 | v1.4.30 → v1.4.88 | 实测 exit0+产物, 移入 EXEC_VERIFIED | ✅ v1.4.88 转正(0.96s) | ✅ 已关闭(10/07 转正) |
| smart | 外部依赖 | SMART 数据库联网查询（域注释） | v1.4.33-34 多波 | 网络通道或本地 SMART DB | ✅ 联网即可人工复验（外部通道） | 归档(外部通道) |
| gxfIdAppender | 外部依赖 | 走 RPC 8765（非独立引擎） | v1.4.30 | RPC 服务层暴露独立入口 | ⚠️ 无 issue/计划锚点——RPC 改造无限期挂起 | 悬空(RPC, 无锚点——除名外仍存证) |

## 逐条详情

### 1. pafref（PafRefBaseCoverCalc）— 引擎缺陷（P2 路径已实试）
- 现象：`--inPaf/--outTab` 真实执行后 NPE `Cannot invoke "String.toString()" because "this.text" is null`（paint 前状态缺失）
- **P2 模式补试（2026-10-05，评审 #115 预审 P1-3 质疑响应）**：setInFile/setOutFile/process() setter 直调同样 NPE——
  `java.util.regex.Matcher.getTextLength` on null `this.text` at process:69；setter 路径无法初始化该字段，
  引擎缺陷确凿（main 与 setter 双路径均无法绕）
- 判定：引擎内部状态字段初始化缺陷，非调用/数据问题
- 波次：v1.4.45（第三十四波）

### 2. tfbsShift（Plugin_PlantTFbindingMotifShift）— 引擎缺陷
- 现象：blastp 子进程实际成功但引擎判失败退出（子进程状态码判断逻辑写反/误读 stderr）
- 判定：引擎对子进程结果的误判，非输入问题（motif 参考数据完整）
- 波次：v1.4.44（第三十三波）

### 3. microsyn（MicroSyntenicAdvance）— 数据合成未攻克（分类修正，2026-10-05）
- 现象：MCScanX 精确格式要求（跨物种 GXF 基因匹配 + collinearity 结构），合成数据多次试配失败
- **分类修正（评审 #115 预审 P1 质疑响应）**：从「引擎缺陷」改类为「数据合成未攻克」——与
  本轮 10 个收编工具（合成数据攻坚成功）同属一类，只是难度更高（跨物种格式严格）
- 判定：非引擎缺陷；复攻条件 = 真实 MCScanX 数据或工厂式生成器
- 波次：v1.4.44 / v1.4.32

### 4. memerun（QuickRunMEME）— JAR 缺类
- 现象：`NoClassDefFoundError: QuickRunMEME`（声明 FULL 但 JAR 内无该类）
- 判定：TBtools 发行版缺该类，任何调用必失败
- 波次：v1.4.30（第十九波）

### 5. smart（SmartDomainAnnotation）— 联网
- 现象：SMART（EMBL）域注释需联网查询，无离线通道
- 判定：环境无外网到 SMART 的稳定通道（与 seqfetch 类联网工具不同，SMART 无 API 封装）
- 波次：v1.4.33-34

### 6. gxfIdAppender — RPC 依赖
- 现象：走 RPC 8765 通道（非独立 main/ArgsParser 引擎）
- 判定：需 RPC 服务层提供独立入口，属架构改造非契约问题
- 波次：v1.4.30

## 结论
- **执行验证 56/60 = 93%(memerun/microsyn 已移出)**（v1.4.27 的 7% 起，连续 47→54 共 17 个实测收编）
- 剩余 3 个不降级新建(pafref/tfbsShift 引擎缺陷等 JAR 升级, xfail 锚点盯梢; smart 归档外部通道); gxfIdAppender 悬空(RPC 通道, 无锚点——除名但仍存证)。