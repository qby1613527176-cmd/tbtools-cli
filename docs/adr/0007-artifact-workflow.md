# ADR-0007: Artifact / Workflow 一等公民(下一轮架构主题)

## 背景
第七份评审(#52)核心主张:从"命令集合"升级为 Agent Runtime,关键在
Artifact(数据载体)与 Workflow(组合单位)成为一等公民。
当前:provenance 已有 run manifest + DAG;ai/workflows.json 为静态声明;
Artifact 尚无独立模型。

## 决策(冻结目标)
1. **Artifact**: `Artifact(id/type/format/path/sha256/schema/producer/created_at)` dataclass;
   `artifact inspect <file>` 命令(读 provenance 输出结构化 Artifact)。
2. **WorkflowSpec**: YAML 声明(inputs/steps 引用上游 output);
   `workflow validate/plan/run/graph/provenance`。
3. **验收基线**(评审 §49):运行 muscle→trimal→iqtree 三步 workflow,
   产出 3 个 Artifact + 完整 DAG + 可 resume。

## 状态: 📋 路线图(不在本轮实施——多文件架构变更,单独立项)
## 不做什么(评审 §50):不再加命令/alias/第二套 Agent API/第二份 metadata
