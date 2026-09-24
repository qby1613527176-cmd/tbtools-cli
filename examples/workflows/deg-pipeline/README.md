# deg.pipeline 示例工作流

```bash
tbtools workflow validate examples/workflows/deg-pipeline/workflow.yaml   # 校验
tbtools workflow plan     examples/workflows/deg-pipeline/workflow.yaml   # 执行计划
tbtools workflow graph    examples/workflows/deg-pipeline/workflow.yaml   # mermaid 图
tbtools workflow run      examples/workflows/deg-pipeline/workflow.yaml   # 顺序执行(Artifact 链)
```

产物: `deg-pipeline.wf/` 下 volcano.svg + dehist.svg + 每步 provenance。
链式引用: 下游步骤可用 `$上游id.output` 引用上游产物(见 /tmp/test_chain.yaml 模式)。
