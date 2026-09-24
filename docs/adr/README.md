# ADR(Architecture Decision Records)

tbtools-cli 重大架构决策记录(第七份评审 #52-45 要求)。

| ADR | 决策 | 状态 |
|---|---|---|
| [0001](0001-command-spec.md) | CommandSpec 为协议层唯一事实源;ENGINE_REGISTRY/CLI_TOOLS/CATEGORY_MAP 降为实现层 | ✅ 已落地(模型接管 metadata) |
| [0002](0002-metadata-single-source.md) | metadata/docs/ai 全部从 CommandSpec 投影,不反向 regex 解析 | ✅ 已落地 |
| [0003](0003-mcp-transport.md) | MCP 是 transport;当前 subprocess 隔离模式;embedded 模式为 v2 候选 | 🟡 现状稳定,embedded 待 benchmark |
| [0004](0004-input-isolation.md) | 输入快照恢复 + reflink(CoW)大文件 + cleanup 只删 t0 后新文件 | ✅ 已落地 |
| [0005](0005-provenance-model.md) | provenance 任意 artifact + run manifest + DAG;run/ 目录模型为 v2 候选 | 🟡 单文件模型稳定,run 目录待 Workflow 落地 |
| [0006](0006-legacy-removal.md) | bin/ 兼容层 v2.0.0 移除(已公告;v1.4 warning+replacement,v2.0 remove) | 📅 计划 |
| [0007](0007-artifact-workflow.md) | Artifact/Workflow 一等公民(下一轮架构主题) | 📋 路线图 |
