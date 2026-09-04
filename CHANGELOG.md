# Changelog

所有显著变更记录于此。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [1.0.0] - 2026-09-04

首个公开发布版本。

### Added（新增）

- **click 框架 CLI**：全量命令结构化入口（`tbtools <group> <command>`），替代原 `tbplot.sh` 裸调用
  - 15 个分组：seq / expr / tree / syn / sets / chipseq / asm / gxf / mirna / table / blast / fastq / hmm / gwas / engine
  - 143 个绘图/分析命令（19 手动 typed click + 130 auto_command 转发）
  - venn2/3/4 原生 ArgsParser CLI（`tbtools sets venn2 --List1 ...`）
- **拼写纠错**：未知命令自动建议最相似命令（`tbtools syn circcos` → `circos`）
- **`tbtools help <命令>`**：快捷帮助入口，自动定位分组
- **`tbtools list [plots|tools|rpc]`**：命令清单（tools 过滤绘图类，66 纯工具）
- **`tbtools presets`**：7 种期刊预设（nature 89×89 / cell / presentation / poster 等）
- **`--preset` 统一选项**：所有绘图命令支持预设画布尺寸
- **`tbtools rpc start|methods|call`**：RPC 服务器管理（188 方法）
- **`tbtools doctor`**：环境诊断（Java/JAR/xvfb/blast/samtools 等）
- **配置文件**：`~/.config/tbtools-cli/config.toml`（JAR 路径 + 默认线程/格式/预设）
- **Python 测试套件**：`tests/test_cli.py` 44 测试 11 类（框架/命令/list/venn/拼写/tool fallback/preset/退出码/输入校验/help 质量/rpc）
- **Bash completion**：分组/子命令/工具三层补全（`scripts/tbtools-completion.bash`）
- **CI**：GitHub Actions（click 框架加载 + bash 语法 + pytest + metadata 校验）

### 数据规模

- 80 个 Java 桥（`bridges/*.java`，源码持久化，/tmp 清理免疫）
- 123 个 TBtools-II 引擎（GenericCli 反射桥 + 专用桥）
- 188 个 RPC 方法
- 30 个坑位提示（PITFALL_HINTS，`--help` 自动显示）
- 35 个全量回归测试用例（`examples/scripts/run_examples.sh` 8/8 必过）

### 修复（本轮）

- venn5/venn6 help 截断
- PITFALL_HINTS 双 ⚠️ emoji
- `tool` 未知命令退出码 1→2（与 click 一致）
- `list tools` 混入绘图命令（130→66 过滤）
- install.sh：`run_examples.sh` 路径 + `help`→`--help` + `server start`→`list rpc`
- CI：run_examples 路径 + pytest 套件
- version 硬编码数字 → 动态统计
- tool --help 只露 3 个命令 → 全列出 66 个

### Known Limitations（已知限制）

- stdin 管道：仅 stat-fasta 等少量工具支持 `/dev/stdin`（Java 引擎限制）
- dualsyn：引擎跑通但保存受限（旧 JJplot2 框架，非 JIGBasePanel）
- MotifStack / MountainPlot / multiSeqBlastVisualization：TBtools 源码空壳，无法 CLI 化
- ncbiPileUpPlot：交互弹窗选 query，不适合 CLI
- venn2-4：走 auto_command 转发（ignore_unknown_options），非 typed click（参数校验弱于手动命令）

### Upstream

- TBtools-II 2.535+（CJ-Chen）主 jar 需用户自备（install.sh 引导）
- 桥/引擎签名基于 2026-08 全量逆向（CFR 反编译 + jstack + 窗口遍历方案）

## [1.1.0] - 2026-09-04

### Added
- `tbtools completion bash|zsh|fish` 内建补全生成（A1）
- `run_java` 成功耗时统计 `⏱ 耗时 X.Xs`（A4）
- `list` TTY 分页（>20 行自动 pager）（A2）
- `list` 分组着色（TTY-only，零依赖 ANSI）（B1）
- `help` 增强：分组 + 坑位 + 示例 + 完整帮助入口（B2）
- 输出文件已存在警告（防覆盖）（B3）

### Fixed
- 顶层直调分组内命令 → 提示正确入口
- 输出目录不存在 → 立即报错（不挂 Java）
- 分组内未知子命令 → 最近命令纠错
- run_plot/run_java/auto_commands 补 command_name（报错带命令名 + 坑位提示）
- `tbtools new` 交互式向导（按「想做什么」生成命令，--list / --run）
- `tbtools check <文件...>` 格式探测器（格式/大小/行数/列数/样例）
- C2 早期格式警告：10 常用命令输入格式不匹配时 Java 执行前提示（13 处 pre_flight 接线）
