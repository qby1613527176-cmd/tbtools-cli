<!-- 外部实测报告存档：WorkBuddy 2026-09-18/19, Windows Server + TBtools-II 2.475, 油茶 WOX 真实数据 -->
<!-- P0-1/P0-2 已按本文补丁修复合入（见 CHANGELOG Unreleased）；未修项见 §4/§8 -->

# tbtools-cli 测试报告（工程版）：三轮实测 + BUG 定位 + 已验证修复补丁

> **本文档的目标**：让任何接手的人**不重复调试**就能 (a) 理解每个问题的根因，(b) 用 §3 的已验证补丁直接修复，(c) 用 §6 回归脚本确认修复没破坏别的。
> 环境：Windows Server · Git Bash(PortableGit 1.2.0) · Python 3.13.14(venv) · click 8.5.0 · JDK 17.0.13 · TBtools-II 2.475 portable · tbtools-cli 本地克隆
> 测试数据：油茶 CON genome v1.0 WOX 家族（17 CoWOX × 6 RNA-seq 样本真实定量数据）
> 时间：2026-09-18 ~ 09-19 · 测试人：WorkBuddy

---

## 目录

- §1 四轮测试总览（含 §1.1 第四轮补充发现 B1~B6）
- §2 环境搭建（Windows 可用配方 + 路径双风格规则）
- §3 BUG 详单（复现→现场→根因→补丁→验证；3.1 P0-1 / 3.2 P0-2 已修复，3.3 P0-3 / 3.4 P1-x / 3.5 P2-x 未修）
- §5 实测参数签名速查表（与官方文档冲突处以本表为准）
- §6 回归测试脚本（14/14 PASS）
- §7 文件索引
- §8 功能封装缺口（GUI 有、CLI 无/坏——优化的第二维度，G1~G7）
- 附：给优化者的最小行动清单

---

## §1 四轮测试总览

| 轮次 | 命令数 | 通过 | 死路 | 覆盖 |
|---|---|---|---|---|
| 第一轮（鉴定流程） | ~10 | 8 | 2 | genestructure / amazingmeta / genelocgff / structure / gxffilter / MCScanX / 重复分类 |
| 第二轮（绘图/杂项） | 10 | 9 | 1 | gxfStat / venn3 / dotplot / logo / phylotree / msa / genedensity / fastaExtract / circos |
| 第三轮（表达/表格/统计） | 17 | 13 | 4 | rpkmCal / groupCol / table×4 / tauIndex / exprCorr / distance / qpcr / heatmap / pca / hclust / upset / generic |
| 第四轮（blast/hmm/诊断/杂项，P0-1 修复后） | 14 | 12 | 2 | doctor / check / presets / help / twoSeqBlast / recipBlast / filterCScore / quickFamily / hmmExtract / venn2 / nwAlign / tableColSel / tableMerge / fqfaConv |

第三轮同时产出论文复现 R4 章节的直接可用数据（组织均值 RPKM、τ 指数、样本相关矩阵、表达热图）。

### §1.1 第四轮补充发现（P0-1 修复后实测）

**修复效果确认**：P0-1 补丁（`@click.pass_context` 拿子命令 Context）在 `blast`/`table`/`sets`/`tree`/`fastq`/`hmm` 各分组同样生效——命名参数现在能完整透传到引擎。

**通过明细**（round4 目录 `wox_run/tbcli/round4/`）：

| 命令 | 状态 | 要点 |
|---|---|---|
| `doctor` | ✅* | *误报 xvfb-run 缺失（Windows 无此依赖，见 B4） |
| `check <文件>` | ✅ | FASTA/HMM 格式探测可用（HMM 报成 "text"，小瑕疵） |
| `presets` | ✅ | 7 个出版预设（nature/cell/plant_journal/new_phytologist/wide/poster/gras） |
| `help <cmd>` | ❌ | `help rpkmCal` → "未找到命令"（P0-3 同类：未注册命令不可达） |
| `blast twoSeqBlast` | ✅ | 15 AtWOX × 48 CoWOX，255 hits。**前置条件：TBtools-II/bin 必须在 PATH（引擎内部 shell 调 makeblastdb/blastp）** |
| `blast recipBlast` | ✅ | RBH 正反互作表；参数 `--querySeqFile/--subjectSeqFile/--outDirAndPrefix` |
| `blast filterCScore` | ✅ | 255→68 行（cscore≥0.5）；`--inBlastTab6/--outBlastTab/--cscore` |
| `blast quickFamily` | ✅ | CoWOX→AtWOX 家族归类（q2s.tab.xls）；`final.IDset.txt` 为空待查 |
| `hmm hmmExtract` | ✅ | `--inHmmFile/--idListFile/--outHmmFile` |
| `sets venn2` | ✅ | `--List1/2 --label1/2 --graph --prefix` |
| `tree nwAlign` | ✅ | NW 全局比对；`--inFile_1/--inFile_2/--outFile`（每文件一条序列，行格式） |
| `table tableColSel` | ✅ | **按列名选列**（非行！）；idList 无匹配时引擎崩溃（见 B3） |
| `table tableMerge` | ✅ | `--inFileArr f1,f2 --inColIndexArr 0,0 --outTable`，MergedKey 合并 |
| `fastq fqfaConv` | ✅ | `--input/--output --mode fa2fq`；位置参数形式 `<in> <out> <fq2fa|fa2fq>` 静默失败 |

**第四轮新增 BUG**：

- **B1（P1）blast 组隐式依赖外部二进制**：`twoSeqBlast` 引擎（CompareTwoSeqSet）内部 shell 调 `makeblastdb`/`blastp`，不在 PATH 时打印 `'*makeblastdb* 不是内部或外部命令'` 后**继续运行并静默无产物**。修复建议：core.py 启动时检测 TBtools-II/bin 并自动追加 PATH，或文档注明。
- **B2（P0，比 P0-2 更隐蔽）包装器吞引擎崩溃退出码**：`run_plot` 捕获引擎非零退出后仍返回 0（如 TableColSelector 崩溃 exit 1 → 包装器 exit 0 无输出）。堆栈只在 `--verbose` 时落临时文件，且**临时文件下次运行即焚**。修复建议：run_plot 把引擎退出码透传给进程退出码。
- **B3（P2）TableColSelector 空匹配集崩溃**：idList 与列名零匹配时 `StringBuilder.deleteCharAt` NPE（TableColSelector.java:174）而非优雅报错"no column matched"。
- **B4（P2）doctor 在 Windows 误报**：xvfb-run 是 Linux X11 依赖，Windows 上应跳过该项检测。
- **B5（P2）recipBlast 输出列 Subject_id 显示数据库内部编号**（`gnl|BL_ORD_ID|N`），真名在 Subject_def 列，易误导下游脚本取错列。
- **B6（规律确认）位置参数不映射普遍存在**：本轮 6 个命令（filterCScore/quickFamily/nwAlign/tableColSel/tableMerge/fqfaConv）位置参数全部静默失败，必须用引擎命名参数。**默认规则：所有引擎调用一律命名参数。**

**第四轮科学副产物**（服务八重验证第 9 项"直系同源"）：`round4/rbh_at15_query.fa_vs_CoWOX_proteins.fa.TBtools.table.xls` = 15 AtWOX 各自最佳 CoWOX 命中（如 AtWUS→CoWOX01 bitscore 104.8）；`famout.q2s.tab.xls` = CoWOX 家族归属。

---

## §2 环境搭建（Windows 可用配方）

### 2.1 组件路径

| 组件 | 路径 |
|---|---|
| TBtools jar | `C:\Users\Administrator\TBtools-II\TBtools_JRE1.6.jar` |
| tbtools-cli 仓库 | `C:\Users\Administrator\WorkBuddy\2026-09-18-23-36-01\tools\tbtools-cli\` |
| JDK 17 | `...\2026-09-18-23-36-01\tools\jdk-17.0.13+11\` |
| Python venv | `C:\Users\Administrator\.workbuddy\binaries\python\envs\default\`（需 `pip install click`） |
| Java 桥编译产物 | `tools/tbtools-cli/build/`（.class，含 GenericCli/TauCalcCli/ExprCorrCli/DistanceCli/QpcrDdctCli/UpSetCli/HeatmapCli 等） |

### 2.2 ⚠️ 路径双风格规则（本轮踩坑实证，Windows+Git Bash 必读）

| 用途 | 必须风格 | 原因 |
|---|---|---|
| `export PATH=...` 条目 | `/c/Users/...`（POSIX） | Git Bash 的 `command -v` 只认 POSIX 条目；Windows 风格条目会被静默忽略 → "Java 未安装" |
| `PYTHONPATH` | `C:/Users/...`（Windows） | python.exe 是 Windows 程序，不认 `/c/...` → `ModuleNotFoundError: No module named 'tbtools_cli'` |
| `python <脚本路径>` 参数 | `C:/Users/...`（Windows） | 同上；POSIX 路径被解释成 `C:\c\Users\...` |
| `java -cp` | `C:/...;C:/...`（Windows，分号） | 同上 |
| 数据文件参数 | 相对路径 | 以 cwd 为基准，无风格问题 |
| bash 内部 `cd`/`ls` | `/c/Users/...`（POSIX） | Windows 风格也能用但易混，统一 POSIX |

**口诀：给 bash 的用 POSIX，给 exe 的用 Windows。**

### 2.3 每次调用前的环境四件套

```bash
export PATH="/c/Users/Administrator/WorkBuddy/2026-09-18-23-36-01/tools/jdk-17.0.13+11/bin:\
/c/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts:\
/c/Users/Administrator/.workbuddy/binaries/PortableGit/versions/1.2.0/usr/bin:\
/c/Users/Administrator/.workbuddy/binaries/PortableGit/versions/1.2.0/bin:$PATH"
export JAVA_HOME="C:/Users/Administrator/WorkBuddy/2026-09-18-23-36-01/tools/jdk-17.0.13+11"
export TBTOOLS_JAR="C:/Users/Administrator/TBtools-II/TBtools_JRE1.6.jar"
export PYTHONPATH="C:/Users/Administrator/WorkBuddy/2026-09-18-23-36-01/tools/tbtools-cli"
```

为什么缺一不可（每个都实测踩过）：
1. 会话 bash 的 PATH 缺 `dirname/tail` → PortableGit usr/bin 必须进 PATH
2. 工具实现探测 `command -v java`，**无视 JAVA_HOME** → JDK bin 必须进 PATH（POSIX 风格！）
3. `bin/tbtools` L10 硬编码 `python3 -m tbtools_cli.cli` → venv Scripts 必须排在 base python 前，且 PYTHONPATH 必须指仓库根
4. `TBTOOLS_JAR` 供桥编译/调用定位 jar

### 2.4 三种调用通道

```bash
# ① 正规 click 分组命令 —— 参数转发完好，优先
tbtools expr heatmap m.tsv out.png --log2 --row-scale --cluster-row

# ② 直调 java —— 万能兜底（§3 修复前是唯一可靠通道）
#    jar 内引擎:
java -cp "$TBTOOLS_JAR" biocjava.bioDoer.Table.TableMelt --inFile a.tsv --outFile b.txt
#    桥(build/ 编译产物): 类路径用分号 + Windows 风格
java -cp "C:/path/to/build;C:/path/to/TBtools_JRE1.6.jar" TauCalcCli in.tsv out.tsv

# ③ tbtools tool <name> —— P0-1 修复后已可用（见 §3.1），命名参数必须"空格分隔"（见 §5 注1）
```

---

## §3 BUG 详单

> 格式：复现步骤 → 现场输出（逐字）→ 根因（含源码/机制分析）→ 修复补丁（before/after diff）→ 验证结果 → 残留风险。
> **P0-1 / P0-2 已在本仓库修复并回归验证（14/14 PASS）。**

### 3.1 P0-1｜`tbtools tool` 分组丢全部参数

**严重级**：P0（~80 个 tool 命令经新入口全部不可用）
**状态**：✅ 已修复（`tbtools_cli/cli.py` ToolGroup.resolve_command）

#### 复现步骤（修复前）

```bash
# 直接调 java 是成功的（对照组）：
java -cp "$TBTOOLS_JAR" biocjava.bioDoer.Table.TableColCollaspe \
     --inTable expr_rpkm.tsv --inGrpInfo groupinfo.tsv \
     --outTable group_mean.tsv --ColType Mean
# → 静默成功，group_mean.tsv 生成 ✅

# 走包装器：
tbtools tool groupCol --inTable expr_rpkm.tsv --inGrpInfo groupinfo.tsv \
     --outTable group_mean.tsv --ColType Mean
```

#### 现场输出（修复前，逐字）

```
[Usage]:
	--inTable	Set Input Value Table with header and row names. [Required]
	--inGrpInfo	Set Sample to Group Info.formatted as "SampleName\tGroupName". without header [Required]
	--outTable	Set Output Value Table. [Required]
	--ColType	Set Collaspe Type, Sum | Mean | Max | Min | Var | Std [Default:Sum]
...
[Error]:
	Argument [--inGrpInfo] Should be Setted
⏱ 耗时 0.2s (groupCol)
EXIT=2
```

→ 引擎收到的参数表为空。`=` 写法、空格写法、位置参数三种形态全部一样。

#### 根因（已用最小复现实验实锤）

`tbtools_cli/cli.py` L331-347（修复前）：

```python
class ToolGroup(click.Group):
    def resolve_command(self, ctx, args):
        try:
            return super().resolve_command(ctx, args)
        except click.UsageError:          # click 8.5: 未知命令抛 NoSuchCommand(UsageError 子类)，能接住
            if args:
                name = args[0]
                impl = getattr(_ac, f'_{name}_impl', None)
                if impl:
                    ...
                    cmd = click.Command(name=name,
                        callback=lambda: sys.exit(impl(list(ctx.args))),   # ← BUG 在这行
                        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
                        help=help_text)
                    return name, cmd, args[1:]
```

**问题**：`lambda` 闭包捕获的 `ctx` 是 `resolve_command` 的入参——即 **tool 分组自己的 Context**，不是随后 click 为 fake Command 创建的子命令 Context。click 转发子命令时会把参数放进**子命令的 `ctx.args`**，而分组级 `ctx.args` 恒为空 → `impl(list(ctx.args))` 永远收到 `[]`。

**最小复现实验**（`wox_run/tbcli/round3/mini_repro_toolgroup.py`，click 8.5.0 实测）：

```
== 复现 BUG ==
  [BUGGY] 收到参数: [] | protected: []            ← 1:1 复刻原代码，参数全丢
== 验证修复 ==
  [FIXED] 收到参数: ['--inTable=x.tsv', '--inGrpInfo=y.tsv', 'out.tsv', 'Mean']   ← pass_context 版完整透传
```

（注意复现实验本身还有个坑：子分组必须显式 `@cli.group("tool", cls=ToolGroupBuggy)` 传自定义类，漏了会复现不出来——真实仓库是传了的。）

#### 修复补丁（已应用 + 已验证）

```diff
  tbtools_cli/cli.py · ToolGroup.resolve_command
-                     cmd = click.Command(name=name,
-                         callback=lambda: sys.exit(impl(list(ctx.args))),
+                     # FIX(P0-1): 旧写法闭包捕获 tool 分组自身 Context（ctx.args 恒空），
+                     # 所有参数被丢弃。改用 pass_context 拿子命令自己的 Context。
+                     @click.pass_context
+                     def _fwd(sctx, _impl=impl):
+                         sys.exit(_impl(list(sctx.args)))
+                     cmd = click.Command(name=name,
+                         callback=_fwd,
                          context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
                          help=help_text)
```

（`_impl=impl` 默认参数是防闭包晚绑定的标准写法。）

#### 验证结果（修复后实测）

```
$ tbtools tool groupCol --inTable expr_rpkm.tsv --inGrpInfo groupinfo.tsv --outTable group_mean_fix.tsv --ColType Mean
⏱ 耗时 0.4s (groupCol)                        EXIT=0
-rw-r--r-- 1 Administrator 197121 1226 ... group_mean_fix.tsv   ← 与直调 java 产出字节级一致

$ tbtools tool tauIndex group_mean.tsv tau_fix.tsv
⏱ 耗时 0.3s (tauIndex)   tau_fix.tsv 1568 字节 ✅

$ tbtools tool upset sets.txt upset_fix.png
[tbplot] 已保存: upset_fix.png   18829 字节（= 直调 UpSetCli 产出同尺寸）✅
```

回归脚本 A 组 8 项全 PASS（§6）。

#### 残留风险

- fake Command 的 callback `sys.exit(impl(...))` 使 click 的 `standalone_mode` 异常处理失效——impl 抛 Python 异常时不会有友好报错（可接受，impl 内部已 try）。
- `--verbose/--quiet` 等公共选项在转发命令上不可用（fake Command 未声明），文档不应宣传这些选项对 tool 分组生效。

---

### 3.2 P0-2｜旧入口 `bin/tbcli.py` Windows GBK 崩溃 + 退出码失真

**严重级**：P0（rpkmCal/statFasta 等仅注册于此入口；崩溃且误报失败）
**状态**：✅ 已修复（`bin/tbcli.py` _run_tool）

#### 复现步骤（修复前）

```bash
python bin/tbcli.py tool rpkmCal --countsTable counts.tsv --lenInfo leninfo.tsv --outTable rpkm_out.tsv
```

#### 现场输出（修复前，逐字）

```
▶ rpkmCal -> biocjava.bioDoer.ExpressionLevelCalculator.RPKMcalculator

❌ 执行失败（退出码 1）
Traceback (most recent call last):
  File "...\bin\tbcli.py", line 488, in <module>
    elif c == "tool" and len(sys.argv) >= 3: cmd_tool(sys.argv[2], sys.argv[3:])
  File "...\bin\tbcli.py", line 296, in cmd_tool
    sys.exit(_run_tool(f"java -Xmx4g -cp {JAR} {cls} {' '.join(args)}", name))
  File "...\bin\tbcli.py", line 216, in _run_tool
    lines = f.readlines()
  File "<frozen codecs>", line 325, in decode
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb2 in position 7: invalid start byte
```

**双重欺骗**：ls 检查发现 `rpkm_out.tsv` 其实**已经生成（2038 字节，内容正确）**——java 实际成功，包装器却报"执行失败"。

#### 根因

`bin/tbcli.py` L208-216（修复前）：

```python
_err_file = tempfile.mktemp(prefix="tbtools_err.")
r = subprocess.run(java_cmd, shell=True, stderr=open(_err_file, "w"))
if r.returncode != 0:
    ...
    with open(_err_file) as f:          # ← BUG：无 encoding 参数
        lines = f.readlines()
```

链条：① 中文 Windows 上 Java 的 stderr 输出 **GBK** 字节（如 `系统找不到指定的路径` 的 0xb2）；② venv Python 3.13 以 UTF-8 模式运行（`open()` 默认 utf-8）；③ 读 stderr 崩 UnicodeDecodeError；④ 该引擎失败时 stderr 还会写 GBK 字节的告警 → 退出码非 0 → 触发读 stderr 的代码路径。**退出码≠实际成败**，产物检查才是真相。

#### 修复补丁（已应用 + 已验证）

```diff
  bin/tbcli.py · _run_tool
+ def _read_err(p):
+     raw = open(p, "rb").read()
+     for enc in ("utf-8", "gbk"):
+         try: return raw.decode(enc)
+         except UnicodeDecodeError: continue
+     return raw.decode("utf-8", errors="replace")
  ...
- with open(_err_file) as f:
-     lines = f.readlines()
+ lines = _read_err(_err_file).splitlines()
  ...
- _err_text = open(_err_file).read()
+ _err_text = _read_err(_err_file)
  ...
- with open(_err_file) as f:
-     _sys.stderr.write(f.read())
+ _sys.stderr.write(_read_err(_err_file))
```

#### 验证结果（修复后实测）

```
$ python bin/tbcli.py tool rpkmCal --countsTable counts.tsv --lenInfo leninfo.tsv --outTable rpkm_fix.tsv
▶ rpkmCal -> biocjava.bioDoer.ExpressionLevelCalculator.RPKMcalculator
EXIT=0
-rw-r--r-- ... 2038 ... rpkm_fix.tsv     ← 与直调 java 产出字节级一致（2038B）
```

回归脚本 B 组 PASS。

#### 残留风险

- `_run_tool` 用 `subprocess.run(java_cmd, shell=True)`——Windows 下走 cmd.exe，路径含空格/特殊字符时有注入与引号问题，建议改 list 参数形式（本轮路径无空格未触发）。
- 退出码失真的根源（引擎失败时 stderr 有 GBK 内容 → returncode!=0，或反之）未在引擎侧根治；包装层新增"产物存在性"检查仍是建议项（见 §4 P2-1）。

---

### 3.3 P0-3｜README 承诺的功能在新入口不存在（未修）

**严重级**：P0（文档级欺骗，AI/脚本按 README 写的命令全部失败）
**状态**：❌ 未修（影响面大，需要架构决策，留给后续优化）

#### 逐条复现与现场

```bash
$ tbtools tool rpkmCal --countsTable ... --lenInfo ... --outTable ...
❌ 未知工具: rpkmCal          ← 后跟 130 个可用命令列表，无 rpkmCal
# rpkmCal/statFasta/tpmCalc/fpkmToTpm 等 82 个 CLI 工具只注册在旧入口 bin/tbcli.py L64/L140 的
# CLI_TOOLS 字典；新入口 tbtools_cli/cli.py 的 ToolGroup 只从 auto_commands.py 取 _<name>_impl，
# 两个注册表互不相通。

$ tbtools engine biocjava.bioIO.FastX.FastaIndex.QuickStatFasta inFile=x.fa --call stat
❌ 'biocjava.bioIO.FastX.FastaIndex.QuickStatFasta' 不是 'engine' 分组内的命令
# README L607-608 首推的"万能反射兜底"，engine 分组根本不存在。近等价物是
# tbtools tool generic ...（但见 §4 P1-4 的限制）。

$ tbtools tool generic biocjava.bioIO.FastX.FastaIndex.QuickStatFasta stat out.txt --set inFasta x.fa
错误: 方法链未返回 JIGSubPanel，无法保存
# generic 桥(GenericCli.java)只为绘图引擎设计：它调 <method>() 后要求返回值是 JIGSubPanel 才能存图。
# 纯计算引擎(如 QuickStatFasta.stat() 返回 void)算完即弃，结果不落盘。
# —— README 的 QuickStatFasta 示例即使参数名对了也走不通。
```

#### 修复建议（按工程量排序）

1. **注册表同步器**（推荐）：写脚本读 `bin/tbcli.py` 的 `CLI_TOOLS` 字典（L64/L140 附近，`"rpkmCal": "biocjava.bioDoer.ExpressionLevelCalculator.RPKMcalculator"` 格式），自动生成 `auto_commands.py` 的 `_impl` 函数文本并追加。82 个工具一次解决。
2. 或者废弃 `bin/tbcli.py`，把 CLI_TOOLS 迁入 `tbtools_cli/` 作为唯一注册表。
3. `engine` 分组：要么实现（透传 GenericCli），要么从 README 删除。
4. 文档注明 `tool generic` 仅适用于"方法返回 JIGSubPanel"的绘图引擎（判断标准见 GenericCli.java 头注释）。

#### 临时绕法

直调 java（§2.4 ②），引擎类名可在 `bin/tbcli.py` 的 CLI_TOOLS 里查；或用 javap 探测引擎字段名（见 §3.4）。

---

### 3.4 P1-x｜引擎级问题（jar 不可改，wrapper 层缓解）

#### P1-1｜`tree one-step` 死命令（第二轮发现）

```bash
$ tbtools tree one-step CoWOX_proteins.fa out_prefix
Exception: ClassNotFound Phylogenetics.OneStepTree      ← 2.475 jar 无此类
# cli.py L320-330 硬编码该类名。修复建议: tbtools doctor 启动时对全部注册类做
# Class.forName 探测，列出死命令（一次 java -cp jar <类> 无参运行即可探测）。
# 绕法: muscle + IQ-TREE 分步（复现流程已验证）。
```

#### P1-2｜引擎硬编码作者机器路径 + 无参不打印 Usage

```bash
$ java -cp jar biocjava.bioDoer.Table.TableMelt            # 无参运行
Exception in thread "main" java.io.FileNotFoundException:
  H:\PlantsRNADatabase\miRNA\Oryza_sativa\...\cluster.re.txt   ← 作者机器的路径!
# 同类: RPKMcalculator → C:\Users\CJ\Documents\BlastStationDB\gene.length
#       TableTransposer → C:\Users\CJ\Downloads\iris.data
# 逼出参数表的技巧: 喂假参数逼 ArgsParser 报 Usage
$ java -cp jar biocjava.bioDoer.Table.TableMelt --bogus x
[Error]: invalid aruguments --bogus
[Usage]: --inFile ... --outFile ...                      ← 真实参数名在此
# 建议做成 wrapper 的 --probe 模式；wrapper 应在发 java 前先做必传参数静态检查。
```

#### P1-3｜`--key=value` 写法被 ArgsParser 拒绝（本轮新发现）

```bash
$ tbtools tool groupCol --inTable=expr_rpkm.tsv ...      # click 层转发 OK(修复后)
[Error]: invalid aruguments --inTable=expr_rpkm.tsv      ← 引擎层拒绝 = 写法
# TBtools ArgsParser 只认 "--key value"(空格分隔)。README 的 bridge 部分示例
# (如 readyaml 的 key=value) 适用于反射引擎, 但 ArgsParser 系引擎一律空格。
# 文档所有命令示例应统一为空格写法。
```

#### P1-4｜引擎字段名与文档不符（javap 是权威）

```bash
$ java -cp jar biocjava.bioIO.FastX.FastaIndex.QuickStatFasta   # README 说字段叫 inFile
→ NPE at FileTools.isGzip                                  ← inFile 是错的
$ javap -p -cp jar biocjava.bioIO.FastX.FastaIndex.QuickStatFasta
  private java.io.File inFasta;                            ← 真实字段名
# 排障 SOP: 引擎行为诡异时 javap -p 查字段名 + 反射 setter(GenericCli --set 用
# set<Field> 命名约定) 推断参数名。
```

#### P1-5｜错误堆栈临时文件即焚（排障杀手）

```bash
# wrapper 报错时提示: 🔍 完整堆栈: C:\...\Temp\tbtools_err.xxxxx (--verbose 显示，重启后清除)
# 实测: 该文件在**下一次任何 tbtools 命令运行时被清理**，不是"重启后"。
# 且 fake Command 转发路径下 --verbose 选项不可用(见 §3.1 残留风险)。
# 排障只能直调 java 抓 stderr。
# 建议: 错误堆栈文件保留至下次同类命令成功，或直接内联打印。
```

#### P1-6｜wmic.exe 沙箱拦截（Windows 特有，次生现象）

```bash
# 现象: P0-1 未修复时, tbtools tool upset 报错且触发 wmic.exe 启动被安全策略拦
#       ( PROGRAM BLOCKED ... wmic.exe )。
# 验证: P0-1 修复后同一命令不再触发（参数正常 → UpSetCli 正常退出）。
# 结论: wmic 调用是丢参数异常路径上的次生行为, 非独立 bug; 但 java 收尾处调 wmic
#       的行为仍值得上游排查（可能是系统信息探测）, 在受限环境会拦截。
```

---

### 3.5 P2-x｜元问题

**P2-1 静默失败**：引擎成功时零输出（groupCol/rpkmCal 直调静默完成）。唯一可靠判定是产物文件 mtime。建议 wrapper 统一加产物验证（解析 `--out*` 参数 → 命令后查文件）。

**P2-2 环境解析链脆弱**：§2.2/2.3 全部条目。建议 `tbtools doctor` 增加：PATH 逐项检查 java/python3 可达、PYTHONPATH 试 import、click 版本输出、探测死命令清单。

---

## §5 实测参数签名速查表（与文档冲突以本表为准）

> 注1：**所有 ArgsParser 系引擎一律 `--key value` 空格分隔，`--key=value` 会被拒绝（§3.4 P1-3）。**
> 注2：Java 类路径 Windows 下桥+jar 用分号：`java -cp "build目录;jar"`。

| 引擎/桥 | 真实签名 |
|---|---|
| RPKMcalculator (jar) | `--countsTable <tsv> --lenInfo <tsv> --outTable <tsv>` |
| TableColCollaspe (groupCol) | `--inTable <tsv> --inGrpInfo <无表头 Sample\tGroup> --outTable <tsv> --ColType Sum\|Mean\|Max\|Min\|Var\|Std` |
| TableMelt | `--inFile <宽表> --outFile <长表>` （不是 inTable!） |
| TableCast | `--inFile <3列长表> --outFile <宽矩阵>` |
| TableTransposer | `--inTable <tsv> --outTable <tsv> [--inColSep \t]` |
| TableUniq | `--inTab <tsv> --colIndex <N> --outFile <tsv> [--showFreq true]` |
| TauCalcCli (桥) | 位置 `<inExpTab> <outTAU>` |
| ExprCorrCli (桥) | 位置 `<inFPKM> <outCorrMat>` |
| DistanceCli (桥) | 位置 `<in.tsv> <col1> <col2> <euclidean\|pearson\|pearsonDist>`（列索引从 0 起） |
| QpcrDdctCli (桥) | 位置 `<in.tab> <out.xls>`；输入行 `gene\tcontrolCt\tExprCt` |
| UpSetCli (桥) | 位置 `<sets.txt 名\t成员...> <out.png> [w] [h]` |
| HeatmapCli (桥) | `<matrix> <out> [--log2 --rowScale --clusterRow --clusterCol --width --height]` |
| GenericCli (桥) | `<engineClass> <method> <outFile> [--set 字段名 值 ...]`；**仅支持返回 JIGSubPanel 的绘图方法**；字段名用 javap 查（例 QuickStatFasta=`inFasta`） |
| 万能探测法 | `java -cp jar <引擎类> --bogus x` → 逼出完整 [Usage] |

---

## §6 回归测试脚本（14/14 PASS）

位置：`wox_run/tbcli/round3/regression_round3.sh`，直接 `bash regression_round3.sh`。

- A 组（8 项）：tool 分组转发（P0-1 修复验证）—— groupCol/tauIndex/exprCorr/tableMelt/tableCast/tableTranspose/tableUniq/upset
- B 组（1 项）：旧入口 rpkmCal（P0-2 修复验证）
- C 组（3 项）：正规 click 命令（heatmap/pca/hclust，确认修复无回归）
- D 组（2 项）：直调 java 兜底链路（RPKMcalculator/QpcrDdctCli）
- E 组（2 项）：已知死路（期望 FAIL：tool rpkmCal 未注册 / tree one-step ClassNotFound），用于确认哪些问题仍未修

判定标准：退出码 + 产物文件存在且非空。脚本内置 §2.2 路径双风格规则。

**最近一次运行：PASS=14 FAIL=0，回归全绿 ✅（2026-09-19 05:41）**

---

## §7 文件索引

```
工作区/
├── tbtools-cli测试报告_三轮汇总与优化清单.md   # 本文
├── tools/tbtools-cli/
│   ├── tbtools_cli/cli.py                 # P0-1 已修复(L331 ToolGroup.resolve_command)
│   ├── bin/tbcli.py                       # P0-2 已修复(L208+ _run_tool)；CLI_TOOLS 注册表(L64/L140, P0-3 待迁)
│   └── build/                             # Java 桥 .class
├── wox_run/tbcli/round3/
│   ├── mini_repro_toolgroup.py            # P0-1 最小复现+修复对照实验（click 8.5.0）
│   ├── regression_round3.sh               # 回归脚本 14/14 PASS
│   ├── prep_inputs.py                     # 测试输入生成器
│   ├── group_mean_fix.tsv / tau_fix.tsv / rpkm_fix.tsv   # 修复后包装器产出
│   ├── group_mean.tsv / tau.tsv / corr.tsv               # 直调产出（R4 直接可用）
│   └── heatmap_test.png / pca_test.png / upset_fix.png / hc.nwk
├── wox_run/tbcli/round4/                  # 第四轮（blast/hmm/诊断）产出
│   ├── twoSeq_out.txt / cscore_out.txt    # 255 hits → cscore 过滤 68
│   ├── rbh_*.TBtools.table.xls / rbh_*.xml  # RBH 直系同源表（八重验证第9项证据）
│   ├── famout.q2s.tab.xls                 # quickFamily 家族归类
│   └── venn2.png / extracted.hmm / nw_out.txt / merged_out.tsv / conv_test.fq
└── .workbuddy/memory/2026-09-19.md        # 过程记忆
```

---

## §8 功能封装缺口（GUI 有、CLI 无/坏——优化的第二维度）

> 前面的 P0/P1/P2 是"已有功能有 bug"；本节是**反过来：GUI 里明明有的功能，CLI 层不可用**，导致自动化管线只能用 Python/外部工具补位。这些同样是需要优化的地方，修复收益=每项解锁一条无头自动化步骤。以油茶 WOX 实战（48 基因鉴定+论文复现）为实测背景。

| # | GUI 功能（TBtools-II 官方有） | CLI 现状 | 实测证据 | 缺失影响与补位方案 | 优化建议 |
|---|---|---|---|---|---|
| G1 | **HMM Search**（hmmsearch 招牌功能） | hmm 组只封装了 `hmmExtract`（抽 HMM 子集），**无 hmmsearch wrapper**；自带 `hmmsearch.exe` 本机崩溃 | 第二轮：hmmpress/hmmsearch.exe 双双崩；PF00046 复验改 pyhmmer | 家族鉴定核心步骤无头不可用 → pyhmmer 补位 | CLI 加 `hmm search` 命令（java -cp 调 jar 内引擎或 shell 调 bin/hmmsearch）；先查 exe 崩溃原因（缺 DLL？工作目录？） |
| G2 | **TreeShow**（多注释轨道树渲染，GUI 明星） | `tree draw` 对应引擎**挂起无响应**（非报错） | 第一轮实测挂起，被迫自写 Newick 解析器+SVG 渲染器 | 发表级树图无法自动化 → 自写渲染器补位 | 排查挂起（疑似等待 stdin/图形上下文）；或桥接 bat 模式 |
| G3 | **蛋白理化性质**（MW/pI/疏水） | CLI 无对应命令 | S1.6 用 biopython ProtParam 补位（MW 17.97-170.85kDa） | 一条 biopython 就顶了，影响小 | 低优先级：jar 里有引擎则桥接，没有就算了 |
| G4 | **GO/KEGG 富集**（GUI 招牌） | table 组只有 `goParse/levelGo`（词典解析），**无 enrichment 统计引擎** | 流程 S 步骤富集分析被迫外部化 | 富集全靠 clusterProfiler/R 或自写 | 高价值：桥接 jar 内 GO 富集引擎；CLI 已有 goParse 打底 |
| G5 | **一步法建树** | `tree one-step` ClassNotFound（2.475 jar 无该引擎，2.535+ 才有） | 第二轮死命令 P1-1 | muscle→trimal→iqtree 手工串（我们本就如此） | 升级 jar 或 CLI 里显式标注版本要求并 fallback 到三步串 |
| G6 | **RNA-seq 定量** | ❌ GUI 也没有（只有 FGettools 下载） | R4 用 kallisto 补位 | 非 TBtools 职责，记录以免误判"CLI 缺失" | 无需优化；CLI 可加 kallisto/hisat2 外部工具编排 |
| G7 | **GXF ID 对照产出**（GXF Info Extractor） | gxf 组未暴露该功能的直接等价命令 | S0.2 id_map 用自写 Python（48/48 零失败，需边界锚定防 gene-408.3 误匹配） | ID 映射是所有下游的入口，错了全错 | 暴露 gxfInfo 类命令；或文档给 GFF 属性解析的 Table 系列组合用法 |

**规律总结**：CLI 封装倾向"输入文件→图片/表格"的**批处理型引擎**（143 绘图+130 工具），GUI 里的**交互式/依赖外部二进制的功能**（HMM、富集、树查看）基本没进 CLI。因此无头管线中 TBtools 覆盖率约一半，其余靠 pyhmmer/biopython/kallisto/自写脚本。

**插件路线评估（为什么"装插件"解决不了 §8）**：TBtools-II 确实有插件体系（GUI 的 Plugin Store，插件为独立 jar）。但 ① 插件**只在 GUI 进程内运行**，没有 CLI 入口——tbtools-cli 走 `java -cp 主jar 类名` 路线，插件 jar 的类名未知且部分依赖 GUI 上下文，包装不了；② 插件安装靠 GUI 插件商店（网络+GUI），无头环境装不了（本机 2.475 portable 目录连 plugins/ 文件夹都尚未生成）；③ §8 的缺口**大多不在插件层**：G1 hmmsearch 崩溃、G2 tree draw 挂起是核心 jar/二进制问题，G3/G4 理化与 GO 富集是核心 GUI 自带功能而非插件。插件能加的是长尾专项功能（如 Fcirc、lncRNA 类），对补齐本节缺口无济于事。

---

## 附：给优化者的最小行动清单

1. **先跑** `bash regression_round3.sh` 确认基线 14/14（改动前后各跑一次）
2. **P0-3 注册表同步**：`bin/tbcli.py` CLI_TOOLS → 生成 auto_commands `_impl`（§3.3 方案1），同步后把回归脚本 E 组第一条移入 A 组
3. **P1-1 死命令探测**：`tbtools doctor` 加 `Class.forName` 预检
4. **P2-1 产物验证**：wrapper 统一解析 `--out*`/末位文件参数做存在性检查
5. **文档对齐**：§5 速查表合入 `docs/COMMAND_REFERENCE.md`；README 删除 engine 示例、补 Windows 章节（含 §2.2 双风格规则）
6. **§8 封装缺口按收益排序**：G4 GO 富集桥接 > G1 hmmsearch wrapper（先修 exe 崩溃）> G7 ID 对照命令 > G5 one-step 版本探测 > G2 tree draw 挂起排查 > G3 理化（可放弃）；G6 定量本就非 TBtools 职责，可做外部工具编排可选
7. 全部完成后提交 git，commit message 建议 `fix(cli): forward tool-group args via pass_context; gbk-safe stderr; #P0-1 #P0-2`
8. 完整代码行号与修复 diff 以 §3 各小节为准；§1.1 B1~B6 与 §8 G1~G7 为第四轮新增，同样可直接开工

---
*报告 v3（工程版·四轮）· 2026-09-19 · 含已验证补丁：P0-1（ToolGroup 参数转发）、P0-2（GBK 解码）· 回归 14/14 PASS · 新增 §1.1 第四轮 BUG（B1~B6）与 §8 封装缺口（G1~G7）*