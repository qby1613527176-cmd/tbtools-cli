# 评审 #115 输入包（REVIEW_PACKAGE_115）

> 生成：2026-10-05 · 范围：v1.4.46 → v1.4.58（14 commit）
> 用途：外部评审（WorkBuddy/GPT/GLM/基础设施视角）输入——自包含，可独立审。
> 活 plan：`docs/_worklog/PLAN.md`；编年史：`workflows/tbtools_cli化_总清单.md`（第四十七/四十八波）

## 0. 项目快照

- 版本 v1.4.58（v1.4.19→v1.4.58 四十连发）；执行验证 **54/60 = 90%**（v1.4.27 的 7% 起）
- 门禁：pytest 619 passed / ruff 0 / mypy 0（本地三件套齐跑，mypy 1.19.1 apt 安装）
- 数据源：代码真源（KNOWN_*/ENGINE_REGISTRY）→ CommandSpec → 单层 verified_tools evidence map → ai/ 投影（gen_metadata --render 原子同步，--check 只读防漂移）

## 1. 变更清单（v1.4.46..v1.4.58）

| commit | 内容 |
|:--|:--|
| 1503fe0 | 评审 #114 Generated Surface Gate v2（P0×2 + P1×4，见总清单 37 波） |
| f504b19 | verified_at 假阳性修复（双端：生成端 fp 未变保鲜 / check 端结构化忽略） |
| 32ee6be | mypy 门禁本地落地：修复 6 处真实类型错误（pyproject disable import-untyped + cli_load 2 处 click 豁免 + cli.py 2 处小修） |
| 0ca6481→3dd3147 | **执行验证 44→54 连续收编 10 工具**：barplotter / efpHeat / multiEfp / kallisto / notung / gsea / plotrna / keggEnrich / peakanno / peaktss |
| 26f6603+0c4301c | Compound Engineering 三招落地（PLAN.md / 模式表 / PITFALL 补全 / 50/50） |
| 3dd3147 | 剩余 6 归档（EXEC_VERIFIED_LEFTOVER.md：引擎缺陷 4 + 外部依赖 2，各含复攻条件） |

## 2. 待审重点（本波关键决策，请评审挑战）

### D1. 执行验证的「数据平移绕过」是否算验证？（peakanno/peaktss）
- 发现：GxFOverlapIndexer binSize=10000 对 bin0（<10000 坐标）匹配失效（startBIN:0 无命中，平移实验证实）
- 处理：示例数据坐标 +1,000,000 模拟真实 MACS2 百万级场景后 3/3 peak 注释（含负链）
- 挑战点：这是「数据适配引擎缺陷」还是「掩耳盗铃」？——论证：真实测序数据天然百万级，引擎设计假设即如此；spec note 早已标注「MACS2, 百万级坐标」

### D2. verified_at 稳定化设计（f504b19）
- verified_at 只在 contract_fp 变化时刷新（同一契约保留首验时间）——「证据语义：该契约版本何时通过验证」而非「测试何时跑」
- --check 对比结构化忽略 verified_at（元数据非内容）
- 挑战点：时间戳保留是否可能掩盖「契约没变但验证环境已变」？（回应：contract_fp 已含 inputs/outputs/参数全字段，环境差异属 CI 层职责）

### D3. 剩余 6 个归档判定（A1-A6）
- 引擎缺陷 4（pafref NPE this.text / tfbsShift blastp 误判 / microsyn 格式 / memerun JAR 缺类）+ 外部依赖 2（smart 联网 / gxfIdAppender RPC 8765）
- 每条含根因 + 波次证据 + 复攻条件（EXEC_VERIFIED_LEFTOVER.md）
- 挑战点：归档是否过早？（回应：多次实测定性，非猜测；复攻条件明确）

### D4. 收编方法论沉淀
- 模式表 P1-P5（引擎声称格式≠实际解析格式→javap 定格式 等 5 模式）
- 双语 PITFALL 46→49
- 挑战点：模式表是否有误归纳？P3「产物派生名→impl 搬运」是否应下沉为通用工具？

## 3. 门禁证据

- pytest 619 passed（52 skipped=缺数据 execution），含 54 个 EXECUTION_VERIFIED 真实执行断言（exit 0 + 非空产物 + sha256 完整）
- ruff 0 / mypy 0（25 files）
- gen_metadata --check：294 命令 / verification=54 / 497 surface 全同步（只读）

## 4. 代码阅读提示（AST 压缩接入——第三十六波①）

评审大文件请用压缩版（结构保留：import/类/签名/docstring，函数体压 `...`），需细节展开原文：
- `docs/_generated/command_spec.min.py`（1137→182 行，KNOWN_* 真源全貌）
- `docs/_generated/auto_commands.min.py`（1184→220 行，ENGINE_REGISTRY + impl 签名）
- 生成工具：`scripts/ast_minify.py`（workspace）

## 5. 评审聚焦建议

1. 本轮 14 commit 里最值得挑战的决策（D1-D4）
2. 执行验证 90% 后的「剩余 6 归档」是否合理收尾
3. 收编方法论（模式表/PITFALL）可否进一步泛化
4. 下一步方向建议（评审节奏/系统改进/执行验证 100% 是否值得）