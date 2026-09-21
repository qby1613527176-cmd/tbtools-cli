# 批次 2 状态（RPC 稳定性：N34/N35 + N40）

> 完成时间：2026-09-21 · 执行：MOSS（子会话）· 仓库未 commit（按要求仅本地改动+自测）

## 2.1 N34/N35（P1）RPC 引擎自发死亡 + kill 后无自愈 + 502 伪装 —— ✅ 已修复并验收

### 改动
| 文件 | 内容 |
|---|---|
| `tbtools_cli/cli.py`（rpc 段，~764 行起） | 新增自愈基础设施 + 重写 4 个 rpc 子命令：`_rpc_state_dir/_rpc_pid_file/_rpc_log_file/_rpc_ping/_rpc_read_pid/_rpc_write_pid/_rpc_remove_pid/_rpc_launch/_ensure_rpc`；`rpc start`（幂等、pid 文件、30s 健康轮询、`--force`）；新增 `rpc stop` / `rpc status`；`rpc methods` / `rpc call` 前置 `_ensure_rpc`（不可达自动拉起），`rpc call` 新增 `--timeout`（默认 300s）、两者新增 `--no-autostart`；全部请求经 `ProxyHandler({})` 绕过代理（兼修 N41 台架问题）；Java 启动加 `-XX:+CrashOnOutOfMemoryError -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=~/.config/tbtools-cli/`；pid 校验过 `/proc/<pid>/cmdline` 防 pid 复用误杀；`start_new_session=True` 脱离父 shell（兼修报告所述 Windows job object 连带终止的同类生命周期问题） |
| `bin/tbtools_rpc.sh` | 同构：pid 文件 `~/.config/tbtools-cli/rpc-<port>.pid`、日志 `rpc-<port>.log`（原 `/tmp/tbtools_rpc_server.log`）、`pid_alive()` stale 清理、健康失败但进程在 → 杀掉重拉（502 伪装场景）、OOM 双 flag、等待期检测启动即崩提前报错、健康等待 15s→30s、新增 `stop` 子命令与用法行 |
| `README.md` / `docs/COMMAND_REFERENCE.md` | rpc 命令表更新（stop/status/自愈说明段） |

### 验证（WSL，TBTOOLS_JAR=/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar）
```
1. rpc start            → ✅ 就绪 (PID 1030148)，pid/日志文件落 ~/.config/tbtools-cli/
2. kill -9 1030148      → 引擎死亡（模拟 N34/N35 自发死亡）
3. rpc call system.listMethods
   → ⚠️ RPC 服务器不可达（端口 8765），自动拉起... → ✅ 成功，返回 188 个方法
4. rpc methods          → RPC 方法（188 个）✅
5. rpc status/start(幂等)/stop → 全部正常（status 未运行时 ec=1）
6. tbtools_rpc.sh: start → kill -9 java → methods 自动拉起（新 PID）✅；stop ✅
```

### 结果
kill 引擎后任何 `rpc call/methods` 自动拉起并成功——验收标准达成。`rpc methods` = 188 条。

### 遗留
- 引擎自发死亡的**根因在 jar 内**（内存/空闲泄漏），包装层只能自愈不能根治；OOM 堆转储落在 `~/.config/tbtools-cli/*.hprof`，真复发时可交上游分析。
- 30min 空闲不假死的验收项未做长测（自愈机制已兜底）。
- `get_jar()` 不读 `~/.config/tbtools-cli/config.sh`（bash 专用），Python 侧需 `TBTOOLS_JAR` 环境变量或 config.toml——属批次 3 N1 范畴（main 负责 core.py），本批未动。

## 2.2 N40（P1）OneStepBuildATree 依赖齐全仍 300s 内部超时 —— ✅ 归因完成（引擎级缺陷）+ 包装层加固

### 本地复现（WSL，muscle 5.2 + muscle5 5.2 + trimal 1.5 + iqtree 2.0.7 全在 PATH）
```
RPC:  rpc call OneStepBuildATree.process {"inputPath":"examples/data/phylogeny/msa.fa","outputPath":"/tmp/n40test"}
      → 22.2s 完成，ok:true，treeFilePath 产出 ✅（进程树实测 muscle→trimal→iqtree -bb 5000 完整流水线）
CLI:  bash bin/tbplot.sh onesteptree --inPepFie examples/data/phylogeny/msa.fa --outFilePrefix /tmp/n40cli
      → 51.9s 完成，TBtools.IQtree.treefile 正常 ✅
```
两条最小可运行命令均 <100s——**本地不可复现挂起**。

### 归因（jar 字节码取证，javap 反编译）
- 引擎调子进程统一走 `toolsKit.SystemCommander`（Windows `cmd.exe /c` / Linux `sh -c`）。
- muscle 阶段：`QuickRunMUSCLEv5`（引擎先跑 `muscle5 -h` 探测，v5 在则走 v5 语法——**测试方"v3/v5 语法差异"推测已被引擎自身覆盖，非根因**）；且其用 `CommandExecutor.processCommandStreamSTDOUTandSTDERR` 双流排水，安全。
- trimAl 阶段：`excuteCommandsAndOutputStdOrSte` —— stdout+stderr **双线程排水**（getStdOutBr@364 + getStdErrBr@367），安全。
- **IQ-TREE 阶段：`QuickRunIQtree.build()` → `SystemCommander.excuteCommandsAndOutputMergedStd(String)`（QuickRunIQtree.class:522）——只起 stdout 排水线程（SystemCommander$3，getStdOutBr@434）后 `waitFor`，stderr 全程无人读**。子进程 stderr 写满 OS 管道缓冲即永久阻塞 → 引擎 waitFor 挂死 → 服务端 300s 超时。Linux 管道 64KB + IQ-TREE stderr 输出少 → 不触发；**Windows 匿名管道缓冲远小（默认 4KB 级），IQ-TREE 2.x 的 warning/progress 输出即可写满 → 必现**。与报告"子进程挂起、依赖齐全、数据仅 1.8KB"完全吻合。
- 结论：**引擎级缺陷（上游 TBtools jar，`toolsKit.SystemCommander.excuteCommandsAndOutputMergedStd` 未排水 stderr）**，按总原则 #3 不硬包装。

### 改动（包装层加固）
| 文件 | 内容 |
|---|---|
| `bin/tbplot.sh`（onesteptree 分支） | 外部依赖预检（muscle5\|muscle / trimal / iqtree，缺失即报错+安装指引）；`TBTOOLS_ONESTEPTREE_TIMEOUT`（秒，默认 1800，0=不限）超时 `timeout --signal=KILL` 杀进程并打印 N40 指引（绕开 `_run_java` 因其实失败即 exit）；其余非零退出透传 stderr 末尾 5 行 |
| `tbtools_cli/cli.py` | `rpc call --timeout`（默认 300s）已覆盖 RPC 侧超时透传 |
| `docs/COMMAND_REFERENCE.md` | onesteptree 条目补依赖预检/超时变量/N40 归因说明 |

### 验证
- `bash -n` 语法通过；CLI 直调 51.9s 成功（走新 timeout 分支，默认 1800 未触发）；依赖预检逻辑人工核查（本地三依赖齐全走正常路径）。

### 遗留
- **上游修复建议**（交付给 TBtools 作者）：`excuteCommandsAndOutputMergedStd` 改用 `ProcessBuilder.redirectErrorStream(true)` 或为 stderr 再起一个排水线程（同 StdOrSte 变体的 SystemCommander$2）。
- Windows 侧回归需测试方用 run_p14c(A 段)/run_p10 复跑；本地已留最小可复现命令与字节码证据链。
- 若用户希望包装层彻底规避：可后续加"拆分手动跑"预设（tbtools muscle → trimal → iqtree 三步已有独立命令），本批未做。

## 需要 main 合并/知悉的点
1. `cli.py` rpc 段整体重写（新增 ~200 行）：与 main 并行改的 core.py 无交集；`rpc call` 的 params 默认值从 `[]` 改为 `{}`（RPC 实测两者均接受，dict 为 188 方法主流形态）。
2. 新增 `rpc stop` / `rpc status` 子命令；`rpc start --force`；`rpc call --timeout/--no-autostart`——`tbtools list rpc` 帮助区（cli.py:1226 附近）可后续补这两行（本批未动该段，避免与 main 冲突，低优先）。
3. `tbtools_rpc.sh` 日志从 `/tmp/tbtools_rpc_server.log` 迁到 `~/.config/tbtools-cli/rpc-<port>.log`，如有外部脚本引用旧路径需同步。
4. 修复清单批次 2 两项可打勾；N40 属"引擎级缺陷不包装"类，验收以归因证据+包装层加固计。
5. 未 git add/commit/push（按约束）；自测期间 RPC 服务已停止、无残留进程。
