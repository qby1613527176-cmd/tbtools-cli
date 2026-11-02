# 规划器质量基线(Planner Quality Baseline)

> 规划器(workflow-plan)的质量作为持续回归目标, 不靠提示词和长文档支撑。
> 本文档是**指针式**索引(防双源漂移)——测试集与断言以代码为准。

## 质量基线(测试固化)

| 文件 | 内容 |
|:--|:--|
| `tests/test_planner_quality.py` | 13 黄金用例 + 3 定点回归(评分边界/语义冲突/配方链) |
| `tests/test_workflow.py` + `tests/test_workflow_contract.py` | 契约图/DFS/评分/绑定解析全链 |

## 评分边界(防漂移关键)

- `recipe_validated`: 配方链边过契约校验(contract+有格式)——全额 recipe_seed 奖励
- `recipe_unvalidated`: 配方链边未过契约校验或 legacy_relation+unknown——降级奖励
- 语义冲突(protein↔dna 等): **硬拒**(v1.5.8+, _dfs 后继扩展+配方种子链同一标准)
- `all_contract_edges`: 全链边过契约校验时加成(+0.2)

## 失败样例库(历史回归)

| 场景 | 历史 bug | 修复轮次 |
|:--|:--|:--|
| muscle→trimal→iqtree 被 preparespecies→iqtree 压制 | 深管线不加权 | #70 |
| recipBlast 单步 0.8 被泛泛链 0.9 压制 | capability 短语匹配缺失 | #109 |
| genestructure 因多必填输入被误伤输给 memeViz | 绑定性探测单格式 | #109 |
| 配方链 recipe_unvalidated 计契约边拿全额奖励 | 评分与证据脱钩 | 十七轮 |
| sixframe→longestorf(protein→dna)仍被推荐 | 语义冲突只扣分不拒绝 | 二十轮 |

## 当前边界(未覆盖, 防误读)

- 链长上限未硬约束(max_steps 软上限)
- 置信度下界无列(低置信链仍返回, 由 confidence 数值区分)
- xfail 失败样例库未独立成文件(内联在测试用例注释中)
