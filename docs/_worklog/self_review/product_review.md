# tbtools-cli v1.4.65 产品/CLI 可用性独立评审

- 评审视角：产品/CLI 可用性（不评审算法正确性；#115 已响应项不重复）
- 评审方式：真实跑 CLI（--help / list / search / help / tool-describe / tool-run --dry-run / version）+ 元数据抽查 + Agent 入口 + 文档
- 环境：JAR 未配置（`tbtools setup` 未跑）——恰好覆盖「新用户第一天」路径
- 日期：2026-10-05

## 总体结论

**不通过（有 P0）。** Agent 编排主入口 `tool-run --dry-run` 存在解析级 bug（把最后一个位置参数当工具名、把输出文件当缺失输入），dry-run 输出的 `status: "ready"` 与 `dependencies_ready: false` 自相矛盾——这是 Agent 规划阶段赖以决策的协议，错了会系统性误导下游。叠加版本号三处不一致（pyproject 1.4.46 / `version` 输出 1.4.46 / 发布声称 1.4.65；绘图命令数 218/213 两处打架）、quickstart 教的 `tbtools list plots` 被静默忽略参数，新用户/新 Agent 的「README → quickstart → 第一个任务」路径上有多个可信度和可用性地雷。294 命令中 233 个（LEGACY+PARTIAL）的元数据 description 是 60 字符截断的 usage 行，机器入口 `ai/tool-index.jsonl` 对 79% 的命令不提供可用的 inputs/parameters 契约——「294 Agent-facing tools」的宣传与机器可读现实有落差。

---

## 逐项发现

### F1. tool-run --dry-run 把最后一个位置参数解析为工具名 — P0
- **发现**：`tool-run --dry-run expr volcano examples/data/deg.txt out.svg` 输出 `"tool": "out.svg"`；`tool-run --dry-run --json asm bamsort missing.bam out.bam` 输出 `"tool": "out.bam"`，并报告 `missing input: out.bam`（输出文件被当成必须存在的输入）。`estimated_artifacts` 同时把输入文件 `examples/data/deg.txt` 列为产物。
- **挑战**：Agent 用 dry-run 做规划（评审 #37 的定位），工具名错=后续 describe/validate/job 全链错；输出当输入=几乎所有「输入不存在」场景永远报 not_ready，dry-run 失去意义。
- **建议**：定位参数解析逻辑（疑似取 args[-1] 或 nargs 错位），修正为「第一个 token 为命令（含 group 前缀形式），按元数据 inputs/outputs 角色区分输入与产物」；为 dry-run 加契约测试：tool 字段必须 ∈ 注册命令名。

### F2. dry-run 的 status 与 dependencies 自相矛盾 — P0
- **发现**：JAR 未配置时（`tbtools_jar.ready=false`，`dependencies_ready=false`），`tool-run --dry-run expr volcano ...` 仍输出 `"status": "ready"`、`"problems": []`。
- **挑战**：`status` 是 Agent 唯一的高层决策字段；依赖未就绪却报 ready，等于协议撒谎。同一语义下 volcano 报 ready、seq grep 报 not_ready，判据不透明。
- **建议**：`status = ready iff inputs_valid && dependencies_ready`；把 status 的判定规则写进 docs/agent-protocol.md 并在输出里带 `status_reasons` 数组。

### F3. 错误分类误导：缺失输入文件 → TB001「wrapper bug」 — P1
- **发现**：`tool-run --json expr volcano nonexist.txt out.svg`（输入文件不存在）返回 `TB001 / category: core / suggested_action: "wrapper bug; report with --verbose"`。但 `tool-validate`/预检明明能识别 missing input。同时建议行写 `tbtools volcano --help`——少了 group 前缀 `expr`，照做的用户会撞未知命令。
- **挑战**：Agent 按 `suggested_action` 行动，被引导去「报 bug」而非「修输入路径」，retryable=false 也封死了重试策略；错误码体系（TB000-TB009）存在但预检结果没映射进去。
- **建议**：tool-run 执行前先复用 tool-validate 的预检，missing input → 专门错误码（如 TB003 文件缺失）+ `suggested_action: "check input path"`；所有 help 提示自动补 group 前缀（元数据里有 `group` 字段，直接用）。

### F4. 版本号与命令数三处不一致 — P1
- **发现**：pyproject.toml=1.4.46，`tbtools version`=v1.4.46，发布口径=v1.4.65；绘图命令数 quickstart 写 218、README 锚点/正文写 213、`version` 输出「213 绘图/分析命令 + 201 auto_commands + 188 RPC」。
- **挑战**：评审/复现/引用时对不上号；用户无法确认自己装的是不是被评审的版本。`version` 自称「权威数字」却不等于发布号。
- **建议**：单一版本源（pyproject → 运行时读取，禁止硬编码）；quickstart/README 的数字改为构建期注入或统一改成「见 tbtools version」。

### F5. quickstart 教的 `tbtools list plots` 参数被静默忽略 — P1
- **发现**：`tbtools list plots` 与 `tbtools list` 输出完全相同（全量分组列表），既不报错也不过滤；`list --help` 下没有任何选项（无 --json、无类别枚举说明），但 --help 文案提到「plots/tools/rpc」。
- **挑战**：新用户照 quickstart 操作，得到与注释「218 个绘图命令」不符的全量输出，第一印象是「文档和工具对不上」。静默吞参数比报错更糟——用户以为过滤生效了。
- **建议**：实现 CATEGORY 过滤（plots/tools/rpc/分组名）或显式报错「未知类别」；list 加 --json（Agent 需要机器可读的命令清单，目前只有人读格式）。

### F6. 79% 命令的机器元数据是 60 字符截断的 usage 行 — P1
- **发现**：command_metadata.json 294 条中 LEGACY 102 + PARTIAL 131；bridge 类命令的 `help` 字段在 60 字符处硬截断（例：admixture 的 description 结束于半个词 `[sor`），无 parameters/inputs/capabilities 字段。ai/tool-index.jsonl 同样：`capabilities: []`、`input_formats: []`、`output_formats: []` 全空，description 截断。另发现 1 条命令（`tree`）readiness/verification 为 null，取值域不完整。
- **挑战**：README 宣传「294 Agent-facing tools」，但 Agent 对 233 个命令拿到的结构化信息≈0，还得自己解析截断的 usage 字符串——「Agent-facing」名不副实。截断半个词说明是代码切片而非人工摘要，属于明显质量瑕疵。
- **建议**：description 截断改为按词/句边界 + 省略号；tool-index 对无契约命令显式标 `schema: null` 而非空数组（空数组语义是「无输入」还是「未知」？）；修复 `tree` 的 null readiness（枚举校验加入生成管线）。

### F7. readiness × verification 组合语义无文档 — P1
- **发现**：readiness ∈ {FULL 60, PARTIAL 131, LEGACY 102, null 1}，verification ∈ {DECLARED 230, EXECUTION_VERIFIED 53, COMPILEABLE 9, CONFORMANCE_VERIFIED 1, null 1}。两维组合（如 PARTIAL+EXECUTION_VERIFIED vs FULL+DECLARED）的实际含义、Agent 能否据此决定「能不能直接跑」，在 docs/agent-protocol.md / README / quickstart 中均无判定表。
- **挑战**：字段存在≠可用。Agent 面对 6×5 的矩阵只能瞎猜；「DECLARED 230」意味着 78% 的命令声明了但没验证过，这个数字应该写进宣传口径的限定语。
- **建议**：docs/agent-protocol.md 加一节「readiness/verification 决策矩阵」：每个组合一行（含义/能否 dry-run/能否 job-submit/风险）；semantic_fingerprint 的用途（变更检测？缓存键？）同样一句话说明，否则是死字段。

### F8. tool-describe 帮助文案与行为不一致；manual/bridge 信息量断层 — P2
- **发现**：分组帮助写 `tbtools tool-describe <命令>...`（暗示支持多个），实际只接受单个 COMMAND，多给报 `Got unexpected extra arguments`。非 --json 模式下 manual 命令（volcano）有真描述，bridge 命令（bamsort）的「描述」就是原始 usage 行复读。
- **挑战**：文案诱导批量用法然后报错；describe 作为「Agent 能力」主入口，对 79% 命令返回的信息量与 list 无差异，没有存在价值。
- **建议**：要么支持多个命令（批量 describe 对 Agent 很值），要么改文案；非 --json 输出至少把截断 help 补全 + 标出 readiness/verification。

### F9. search 的分组标签与 describe 矛盾 — P2
- **发现**：`search volcano` 显示 `[engine/manual]`，而 `tool-describe volcano` 与元数据均为 `group: expr`。engine 是 runner/类别概念，expr 是调用分组，两个入口混用命名空间。
- **挑战**：Agent 按 search 结果拼 `tbtools engine volcano` 会失败。分组名是 CLI 的公共 API，两个入口必须同源。
- **建议**：search 标签直接读元数据 `group` 字段；如确需展示 runner，分两个字段显示。

### F10. 新用户「第一个真实任务」路径有断点 — P2
- **发现**：quickstart 第 2 步直接 `tbtools expr volcano examples/data/deg.txt volcano.svg`，但 dry-run 显示 `dependencies.tbtools_jar.ready=false` 时 quickstart 没说「JAR 未配置时这条会怎样」（实际 manual plot 是否依赖 JAR 未知——文档没区分哪些命令需要 JAR）；reference.md 只有 5 行，是指向 2600 行 COMMAND_REFERENCE.md 的跳板页，新用户从 reference 得到的「参考」接近为空。完整堆栈路径 `/tmp/tbtools_err.xxx` 提示「重启后清除」——Agent 跨会话无法回溯错误。
- **挑战**：quickstart 的每条命令都应该在「零配置」和「已配置」两种状态下有预期行为说明；5 行的 reference.md 不如直接合并进 COMMAND_REFERENCE 首部。
- **建议**：quickstart 每条命令标注「需要 JAR：是/否」；reference.md 补齐退出码表 + 错误码表 + readiness 说明（当前全部散落）；错误堆栈落盘到 `~/.cache/tbtools/` 并在 job-result 里引用。

### F11. 历史包袱：camelCase 命令名 + 分组语义混杂 — P2
- **发现**：命令名风格三派并存——camelCase（bamMerge, admixtureViz, filterCScore）、全小写（bamsort, volcano, blat）、大小写敏感歧义（`tree` 既是分组名又是命令名，元数据里 `tree` 命令 readiness=null 疑似就是被分组遮蔽的受害者）。`list` 输出按 asm/blast/chipseq/engine/... 分组，但 `engine` 组名为「通用」，与 README 的「Plotting Engines (213)」用词撞车（engine=分组 vs engine=绘图引擎）。
- **挑战**：命名不一致直接抬高记忆成本和 search 噪音；`tree` 命令/分组同名是实际 bug 温床（F6 的 null 值即实例）。
- **建议**：短期不改名（破坏兼容），但：① 修复 `tree` 命令被遮蔽问题；② docs/commands.md 加「命名约定」一节承认三派并存并给出别名计划；③ engine 分组改名 general 或在文档中强制区分「分组 engine」与「绘图引擎」。

---

## 最值得改的 3 点

1. **修 tool-run --dry-run 解析 + status 语义（F1+F2）**：这是 Agent 规划的唯一入口，当前工具名取错、输出当输入、ready 与依赖状态矛盾，三者叠加 = dry-run 协议不可用。修一处代码 + 加契约测试，收益最大。
2. **统一数字与文档的真相源（F4+F5+F10）**：版本号单源化、quickstart 命令数与 list 行为对齐、每条 quickstart 命令标注 JAR 依赖——新用户前 10 分钟的信任是这时候建立的，现在每一步都有对不上号的小伤口。
3. **给 294 命令的机器入口定「最低可读标准」（F6+F7）**：description 截断修掉、无契约命令显式 `schema: null`、readiness×verification 决策矩阵进 agent-protocol.md。否则「294 Agent-facing tools」只是营销数字，Agent 实际可用的是那 60 个 FULL。
