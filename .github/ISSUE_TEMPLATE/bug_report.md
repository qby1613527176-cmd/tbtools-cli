---
name: Bug report
about: 报告缺陷（命令崩溃 / 数据损坏 / 文档错误）
title: "[bug] 简短描述"
labels: bug
assignees: ''
---

**命令与版本**
- `tbtools version` 输出:（粘贴第一行）
- 操作系统:（Linux/WSL/macOS/Windows）
- 环境:（Python 版本;`echo $TBTOOLS_JAR` 是否设置）

**复现步骤**
```bash
# 最小复现命令（含输入文件路径）
tbtools <group> <cmd> <args...>
```

**实际行为**
（粘贴 stdout/stderr,含 `--verbose` 完整堆栈;注明退出码）

**期望行为**

**输入数据**
- 是否可用 `examples/data/` 复现?（是/否;否的话描述文件形态/大小）

**补充**
- 是否引擎级?(`java -cp $TBTOOLS_JAR <engineClass>` 直接调用是否同样失败——快速区分包装层 vs 引擎缺陷)
- 相关 issue / PITFALL 提示