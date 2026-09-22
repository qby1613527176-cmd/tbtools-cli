# Contributing to tbtools-cli

感谢你愿意为 tbtools-cli 贡献！请先读 README 掌握全貌，再按本指南操作。

## 开发环境

```bash
git clone git@github.com:qby1613527176-cmd/tbtools-cli.git
cd tbtools-cli
pip install -e .            # 可编辑安装（拿到 `tbtools` 命令 + 包元数据）
pip install pytest ruff     # 质量门禁
# 需要真实引擎测试时:
#   1) 下载 TBtools_JRE1.6.jar（TBtools-II release / scripts/fetch_jar）
#   2) export TBTOOLS_JAR=/path/to/TBtools_JRE1.6.jar
```

## 质量门禁（提交前必须全绿）

```bash
ruff check .                # 全仓库 0 errors（硬性）
shellcheck -S warning bin/*.sh install.sh run_examples.sh config/config.sh scripts/*.sh
python3 -m pytest tests/    # 88+ passed
python3 scripts/gen_metadata.py --check   # metadata 与运行时一致（防漂移）
```

## 架构速览（改代码前先对齐）

| 文件 | 职责 |
|---|---|
| `tbtools_cli/auto_commands.py` | `ENGINE_REGISTRY` 表驱动命令定义（name/kind/class/xmx/runner/doc）+ 特殊手写 impl |
| `tbtools_cli/cli_tools_registry.py` | 82 个 CLI 工具共享注册表（`tool <name>` 兜底转发） |
| `tbtools_cli/command_metadata.json` | **唯一数据源**（276 命令;由 `scripts/gen_metadata.py` 生成/校验） |
| `tbtools_cli/cli.py` | 入口 + 分组手动命令（~530 行;拆分后瘦身） |
| `tbtools_cli/cli_load.py` | 动态注册（分组映射/加载/纠错） |
| `tbtools_cli/cli_rpc.py` | RPC 分组 + 自愈基础设施 |
| `tbtools_cli/cli_top.py` | 顶层命令（version/doctor/list/new 等） |
| `tbtools_cli/core.py` | run_java 包装 + 输入保护 + PITFALL_HINTS |
| `bridges/*.java` | 引擎反射桥（setter+process → 保存图形） |

## 新增命令的推荐路径

1. 首选：往 `ENGINE_REGISTRY` 加条目（表驱动自动注册 + help 从 doc 取）
2. 桥类命令：`bridges/<Name>Cli.java`（参照同级桥;setter+process+save2Graph 模式）
3. 工具类：`cli_tools_registry.py` 加映射
4. 新命令要有 examples 数据 + PITFALL 提示（有坑就写，别让下一个用户踩）
5. 跑 `python3 scripts/gen_metadata.py`(写 metadata)+ `--check`(验证)

## 基准（不要破坏）

- `tbtools list plots` = 218 | `list tools` = 191 | `version` 数字随注册表动态
- `pytest tests/test_metadata.py`（metadata 与运行时一致性）必须过
- 输入保护（core.py snapshot/verify/restore）：引擎不能改用户输入文件（N19/N37 教训）

## PR 流程

1. 小步提交,`fix:`/`feat:`/`docs:`/`refactor:`/`chore:` 前缀 + 中文说明
2. push 前跑上面全部门禁
3. PR 描述:改了什么/为什么/验证输出(截图/SVG 产物/测试结果)
4. CI(test.yml)必须绿;涉及 jar 的命令在 onboarding-e2e 说明验证方式

## 已知边界(别浪费时间去"修")

- 引擎级缺陷(上游 TBtools jar 内):Gxf 族 GENCODE GTF NPE、OneStepBuildATree 超时、GxfGeneDensityProfiler NPE 等——记录到 PITFALL/docs 即可
- `tbplot.sh`/`tbcli.py`/`tbengine.sh`/`tbtools_rpc.sh` 是兼容层(已打 deprecation 警告),**计划 v2.0.0 移除**;新功能一律走 Python 入口