---
name: Feature request
about: 建议新命令 / 新功能（含 TBtools 引擎 CLI 化）
title: "[feat] 简短描述"
labels: enhancement
assignees: ''
---

**要解决的场景**
（想做什么;原始 TBtools GUI 面板名/引擎名若有请给）

**建议形态**
（命令名、参数、输出格式;参照 `tbtools list plots` 现有风格）

**可参考的引擎**
（如 `biocjava.*` 类名 / RPC 方法名——`tbtools rpc methods` 可查;或插件 .plugin 来源）

**验收标准**
（用什么数据能验证?是否已能用 `tbtools engine <class> key=value` 兜底?）

**工作量提示**（供维护者参考）
- [ ] 引擎有 ArgsParser(直接注册) / 需写桥 / 需 Python 包装
- [ ] 需联网 / 外部二进制
- [ ] 属于引擎级缺陷(记录 PITFALL 而非新命令)