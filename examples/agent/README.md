# Agent 实战示例(User goal → search → plan → validate → run → artifact → provenance)

## phylogeny/(系统发育演示)

```bash
# 1 发现(按任务)
tbtools search --capability phylogeny --json
# 2 理解
tbtools tool-describe iqtree --json
# 3 预检
tbtools tool-validate tree rooting examples/data/treeRooting/unrooted.nwk --json
# 4 规划(决策层)
tbtools workflow plan examples/agent/phylogeny/workflow.yaml
# 5 执行
tbtools workflow run examples/agent/phylogeny/workflow.yaml
# 6 Artifact 检查
tbtools artifact inspect phylogeny.wf/rooted.nwk --json
# 7 溯源 DAG
tbtools provenance-graph phylogeny.wf --mermaid
```

产物: `phylogeny.wf/`(aln.svg + rooted.nwk + 每步 provenance + .wf_state.json)
