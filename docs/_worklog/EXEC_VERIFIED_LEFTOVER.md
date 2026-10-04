# 执行验证遗留状态（EXEC_VERIFIED_LEFTOVER.md）

> 2026-10-04 归档 · 执行验证 54/60 = 90% 收官于 v1.4.57
> 剩余 6 个工具为引擎级缺陷或外部依赖，**已定性、不再重复攻坚**（复攻条件见各条）。
> 活 plan 见 `docs/_worklog/PLAN.md`（A 区已完结）；本文件是 A 区遗留的权威存证。

## 定性总表

| 工具 | 类别 | 根因 | 证据（波次） | 复攻条件 |
|:--|:--|:--|:--|:--|
| pafref | 引擎缺陷 | PafRefBaseCoverCalc `--inPaf/--outTab` 后 `this.text` NPE | v1.4.45 | 需上游修 JAR |
| tfbsShift | 引擎缺陷 | blastp 子进程误判成功为失败（子进程状态码逻辑反） | v1.4.44 | 需上游修 JAR |
| microsyn | 数据合成未攻克 | MCScanX 精确格式（跨物种 GXF/共线性严格匹配）——专门造数据无法复现官方数据形态 | v1.4.44 / v1.4.32 | 真实 MCScanX 数据或工厂式数据生成 |
| memerun | 引擎缺陷 | JAR 缺 `QuickRunMEME` 类（NoClassDefFoundError） | v1.4.30 | JAR 升级带上该类 |
| smart | 外部依赖 | SMART 数据库联网查询（域注释） | v1.4.33-34 多波 | 网络通道或本地 SMART DB |
| gxfIdAppender | 外部依赖 | 走 RPC 8765（非独立引擎） | v1.4.30 | RPC 服务层暴露独立入口 |

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
- **执行验证 54/60 = 90% 收官**（v1.4.27 的 7% 起，连续 47→54 共 17 个实测收编）
- 剩余 6 个不降级新建/不重复攻坚（其中 microsyn 按数据角度归类，非引擎缺陷）；若上游 JAR 升级（pafref/tfbsShift/memerun）或数据/通道就位（microsyn/smart/gxfIdAppender），按本表复攻条件恢复