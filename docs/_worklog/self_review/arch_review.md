# tbtools-cli v1.4.65 架构/代码 独立批判性审查

- 日期: 2026-10-05
- 视角: 独立架构/代码审查（只找问题，不称赞）
- 范围: identity.py / command_spec.py / auto_commands.py / cli_load.py + cli_top.py / runtime/java.py / workflow 四层拆分
- 前置: 评审 #115 预审 4/4 P1 + 3/3 P2 已响应（v1.4.60-62），本审查聚焦已响应项**之外**的新问题
- 判定: **不通过** — P0 × 1，P1 × 5，P2 × 7

---

## 总体结论

三层 identity 拆分的**概念边界是清楚的**（contract=执行形状 / semantic=搜索规划 / env=引擎本体），但
**落地层普遍存在"写了不算数"的半截工程**：env_fp 只写不查、N30 输出缺失检测被后续代码无条件复位、
_IMPL_REGISTRY 冲突守卫结构性失效导致两个手写修复（N3/N27）被静默旁路。更严重的是 run_java 的
P0 输入保护本身存在一个**反向破坏**缺陷——它会把已存在的输出文件当输入快照，运行后用旧内容覆盖
刚产出的新产物（实测复现）。保护机制成了破坏机制，这是本审查唯一 P0。

四层拆分（identity/dependency/compiler/executor）方向正确，但 executor 仍存在函数内
`from workflow import _execute_step` 的自我绕行循环；`workflow.py` 同时扮演"上层 plan/validate"
与"下层 re-export 门面"两个角色，拆分未闭合。

---

## 逐项发现

### F1. 【P0】snapshot_inputs 把已存在的输出文件当输入 → 新产物被旧产物覆盖

- **位置**: `runtime/java.py` `snapshot_inputs()` / `verify_and_restore()`
- **发现**: 快照逻辑排除"out 型 flag 后面的值"（`_OUT_FLAG_RE`），但 **positional 布局没有 flag**——
  大多数 bridge 命令（`circos <chrLen> <link> <genePos> <outFile>` 等）的输出是裸位置参数。
  重跑且输出文件已存在时，输出文件被当作输入快照；引擎覆盖输出后，`verify_and_restore`
  检测到 sha 不一致 → **把旧输出复制回去覆盖刚生成的新输出**，并打印误导性的
  "⚠️ 输入保护：检测到引擎修改/删除了输入文件，已自动恢复"。
- **实测复现**（2026-10-05, /tmp/p0test）:
  ```
  args = [java,-Xmx3g,-cp,build:x.jar,SomeCli,in.tsv,out.svg]   # out.svg 已存在(OLD)
  snapshotted: ['in.tsv', 'out.svg']
  引擎写入 NEW-OUTPUT → verify_and_restore → [('out.svg','modified-restored')]
  out.svg 最终内容: OLD-OUTPUT   ← 新产物被静默回滚
  ```
- **挑战**: 这正是"输入快照/副作用清理误伤正常产物"的质疑点的实锤。影响面 = 全部 positional
  布局 + 输出已存在的重跑场景（resume 重跑、覆盖重算是日常操作）。用户看到的是成功退出 +
  一条"已恢复"警告，但产物是**上一轮的陈旧内容**——比报错更危险。
- **建议**: 输出槽识别不能只靠 flag 名正则。最低修复：`canonical` 侧已有 output 位置约定
  （positional 布局 = 末位参数），快照时跳过"末位且扩展名属于已知产物后缀"的参数；
  彻底修复：run_java 接受可选 `output_path` 参数（impl 工厂已知 runner/layout），从快照集
  显式剔除。同时把 verify_and_restore 的 restore 行为限定为"输入文件（运行前就存在且
  不在输出槽）"。
- **严重度**: **P0**（静默数据破坏 + 误导性日志）

### F2. 【P1】N30 输出缺失检测被 `if ec == 0: ec_out = 0` 无条件复位 → 死代码

- **位置**: `runtime/java.py` `run_java()` 尾部
- **发现**: 成功分支里 `check_missing_outputs` 命中时正确地 `ec_out = 1`；但函数尾部有
  ```python
  # 成功时 ec_out = 0
  if ec == 0:
      ec_out = 0
  ```
  只要子进程退出码为 0，ec_out 被无条件清零——N30 的"声明了强输出但未生成 → 报错"
  **永远不生效**，provenance 也记成 success。
- **挑战**: N30 是评审结项的保护项，现在它是死代码；且若哪天 ec_out 在此分支非零，紧接着
  的 `if ec_out != 0 and err_text` 会因 `err_text`（仅在 `ec != 0` 分支定义）抛 NameError——
  两个 bug 互相掩盖。
- **建议**: 删除尾部复位（ec_out 在 ec==0 时本来就是 0，该行本就多余），并把 `err_text`
  在函数开头初始化为 `""`。
- **严重度**: **P1**

### F3. 【P1】env_fp 只写不查：验证失效/恢复闸门都不消费它（评审 #115 响应只做了一半）

- **位置**: `identity.py engine_env_fingerprint()` → `command_spec.py _load_verification_report()`；
  `compiler.py execution_fingerprint`
- **发现**: 响应 #115 后 `verification_report.json` 的每个 verified_tools 条目写入了
  `env_fingerprint`，`verified_at` 刷新也用了双条件——但**消费端没有任何一处比对 env_fp**：
  - `_load_verification_report()` 的降级逻辑只比对 `contract_fingerprint`，换 JAR/换二进制
    后 EXECUTION_VERIFIED 标签照样保留——`env_fingerprint` 字段是装饰；
  - resume 闸门 `execution_fingerprint`（compiler.py）组成为
    contract+binding+input_shas+runtime(tbtools 版本)+deps 版本字符串——**不含 JAR sha /
    env_fp**。换 JAR 而 deps 版本字符串不变时，resume 会跳过本应重跑的步骤。
- **挑战**: "换引擎契约不变时 verified_at 不再指向已不存在的引擎"这一目标，目前只改变了
  时间戳显示，未改变任何判定行为。
- **建议**: ① `_load_verification_report` 增加 env_fp 不匹配 → discard（与 contract_fp 并列）；
  ② `execution_fingerprint` 组成加入 JAR sha（或整体 env_fp，注意缓存，见 F8）。
- **严重度**: **P1**

### F4. 【P1】env_fp 覆盖缺口：13 二进制清单与自家 KNOWN_DEPENDENCIES_STRUCT 不对齐

- **位置**: `identity.py engine_env_fingerprint()` 的 `_BINS` / `_paths`
- **发现**: 硬编码清单缺：
  - **blast 套件**（blastp/blastn/makeblastdb/blastdbcmd）——recipBlast/bestid/getseqdb/
    twoSeqBlast 的实际执行依赖，STRUCT 里明明白白声明了；
  - **RNAfold**（rnaplot/plotrna，STRUCT 有）、**hmmscan**（simplehmmscan，STRUCT 有）、
    **ssearch36**（mirnatarget 手写 impl 依赖，STRUCT 未声明也未入 fp——双层遗漏）、**fimo**；
  - **7 个插件 JAR**（Plugin_NewickRenamer / Plugin_HmmerSuite / Batch_MEME_Motif_Viz /
    Plugin_PlantTFbindingMotifShift / Plugin_OneStepMCScanX_Diamond / Plugin_QuickProteinAnno /
    Plugin_BatchSMART）——env_fp 只 hash 了主 JAR + Notung + GSEA 三个；
  - 参考数据（plantTF/ath.pep+binding.motifs、GSEA Dependency/）也不入指纹。
- **挑战**: 维护一份手写二进制清单去逼近一份 already-structural 的依赖声明，是重复真源。
- **建议**: `_BINS` 从 `KNOWN_DEPENDENCIES_STRUCT[*].executable` 动态派生 + 插件 JAR 走
  `plugins/lib/*.jar` 枚举（或显式注册表），删掉硬编码清单。
- **严重度**: **P1**

### F5. 【P1】_IMPL_REGISTRY 与手写 impl 双轨：冲突守卫结构性死代码，N3/N27 修复被旁路

- **位置**: `auto_commands.py` 注册循环 + 手写段；`cli_load.py _parse_auto_metadata`
- **发现**: 三个叠加问题：
  1. 冲突守卫 `if hasattr(sys.modules[__name__], f"_{_cmd}_impl"): raise SystemError`
     在**注册循环执行时**运行，而手写 def 全部在循环**之后**才定义——守卫永远为假，
     是结构性死代码；
  2. `_parse_auto_metadata` 优先 `_IMPL_REGISTRY.get(name)`。实测（2026-10-05）：
     `tableMerge`/`efpHeat` 解析到的是 **registry 工厂版**（裸直通），globals 里的
     N3（位置参数兼容转换）/N27（命名参数修复）手写修复**不生效**——工厂版与手写版
     并存且选错了版；
  3. 头注释"13 个特殊实现手写保留"实为 **~30 个**手写 impl（`grep -c "_impl"` = 44 处，
     手写约 30），文档与现实严重脱节。
- **建议**: 显式 `HANDWRITTEN = {...}` 集合，注册循环跳过集合内名字（并把守卫移到模块尾部
  assert）；或 `_parse_auto_metadata` 改为 globals 优先。二选一，消灭"两个版本同时存在
  且选择规则反直觉"的状态。顺带把头注释数量修正。
- **严重度**: **P1**（已造成两个修复静默失效）

### F6. 【P1】executor↔workflow 循环依赖残留：四层拆分未闭合

- **位置**: `executor.py:283,368`；`workflow.py` re-export 段
- **发现**: executor 函数内 `from tbtools_cli.workflow import _execute_step, _topo_sort, plan`——
  `_execute_step` **本来就定义在 executor 自己里面**，workflow 只是 re-export。等于
  executor 绕到上层门面 import 自己的符号；同时 `plan/_topo_sort` 属 plan 层却被 executor
  反向引用。workflow.py 既是"上层（plan/validate/plan_from_goal）"又是"下层（re-export
  门面）"，四层（identity/dependency/compiler/executor）之外实际还有第五层职责。
- **建议**: plan/_topo_sort/validate 从 workflow.py 迁入 compiler.py（或新 planner.py），
  workflow.py 只做薄门面；executor 删除 self-import 绕行。
- **严重度**: **P1**（架构层面；不立即出错，但"拆分后职责清晰"的声明不成立）

### F7. 【P2】clear_specs_cache 是死钩子 + 同一真相三处缓存

- **位置**: `command_spec.py:clear_specs_cache`；`cli_load.py _SPEC_GROUPS / _load_meta_json`
- **发现**: `clear_specs_cache` **全仓零调用点**（grep 仅注释提及，且注释写的是不存在的
  `_clear_specs_cache` 名字）。同时 spec 分组在 `cli_load._SPEC_GROUPS` 另有一套懒缓存、
  metadata 在 `_load_meta_json` 第三套——同一真相三处缓存，全部无失效机制（只能靠进程
  重启）。注释承诺的"KNOWN_* 变更调 clear"实际无处可调。
- **建议**: 要么删注释承认"进程内不可变"，要么把三处缓存统一挂到 clear_specs_cache 下。
- **严重度**: P2

### F8. 【P2】engine_env_fingerprint 全量 hash 无缓存 + PATH 依赖

- **位置**: `identity.py engine_env_fingerprint()`
- **发现**: 每次调用对主 JAR + 13 个二进制做全量 sha256（数百 MB IO），无 mtime/size 短路
  缓存；且 `shutil.which` 解析使指纹依赖调用时 PATH——同机不同 PATH 得出不同 fp。一旦按
  F3 建议接入 verification/resume 热路径，会造成 ① 每次 compile 数百 MB 重复读盘；
  ② PATH 抖动导致 verified_at 无谓刷新/resume 误判。
- **建议**: 以 (path, mtime, size) 为 key 的结果缓存（复用 `_DEP_VERSION_CACHE` 模式）。
- **严重度**: P2（当前只在测试里调用，接入即升级 P1）

### F9. 【P2】command_spec import 期副作用：import 即构建 294 specs + 全量 overlay 比对

- **位置**: `command_spec.py` 模块级 `_CONFORMANCE_VERIFIED, _EXEC_VERIFIED, _COMPILE_VERIFIED
  = _load_verification_report()`
- **发现**: import command_spec 即：读 verification_report.json → `_bcs_for_verify()` 构建全部
  specs → 每个 spec 跑 canonical_snapshot vs yaml_to_snapshot 全量 equality。实测冷 import
  ~0.27s，且 overlay 的 DeprecationWarning 会在 **import 期**向 stderr 抛出（CLI 任何子命令
  包括 `--help` 都触发）。库式使用（MCP server、测试收集）都被迫付这笔账。
- **建议**: verification 名单改懒加载（首次 `verification_level` 调用时算）。
- **严重度**: P2

### F10. 【P2】_apply_contract_overlay 裸 `except Exception: pass` —— 校验器静默全灭

- **位置**: `command_spec.py _apply_contract_overlay`
- **发现**: canonical_snapshot/yaml_to_snapshot 任何一个出 bug（字段改名、类型变化），
  快照一致性校验**整体静默失效**，连一条日志都没有。评审 #112 建的 Contract Integrity
  Freeze 的实际可靠性 = 这两个函数永远不出错。
- **建议**: except 里至少 `warnings.warn("snapshot check itself failed: ...")`——校验器自身
  故障必须可观测。
- **严重度**: P2

### F11. 【P2】cleanup_side_effects 只扫 CWD，输入目录的副作用残留漏清

- **位置**: `runtime/java.py cleanup_side_effects`
- **发现**: N37 族副作用文件（`*.TBtools.fa*`、`*.TBtoolsDB.*`）是引擎**在输入文件旁边**落的，
  而 cleanup 只 `os.listdir(os.getcwd())`。用户在别处 cwd 跑 `tbtools seq recipBlast --querySeqFile
  /data/q.fa ...` → `/data/*.TBtoolsDB.*` 永久残留。
- **建议**: 对 snaps 里每个输入的 dirname 各扫一遍（preexisting 快照也需按目录建）。
- **严重度**: P2

### F12. 【P2】YAML 快照双序列化器 + 死常量 + 微问题簇

- **位置**: 多处
- **发现**:
  1. YAML 导出（gen_metadata → `to_metadata_entry` 投影）与快照校验（identity
     `canonical_snapshot`/`yaml_to_snapshot`）是**两套独立序列化器**描述同一契约形状，
     字段默认值（role=file / required=True / content_type=generic）靠人工保持同步——
     单向导出的方向是对的，但比较器双实现内置漂移风险（F10 的 except 还把它盖住）；
  2. `CANONICAL_SEMANTIC_FIELDS` 常量全仓零使用（grep 仅定义+导出）——评审 #108 刚消灭
     重复常量，这套又留下了；
  3. `runtime/java.py` 不能作为首个导入模块（core 尾部 re-export 依赖——直接
     `import tbtools_cli.runtime.java` 触发 circular ImportError，实测）；import 顺序敏感；
  4. `_write_provenance` 的 inputs 识别会把"已存在的输出文件"计入 inputs（与 F1 同根因）；
     `"snaps" in dir()` 脆弱写法；
  5. `KNOWN_PARAMS` 只有 8 个工具有参数契约，但 `agent_readiness` 注释称"parameters 声明
     存在即可"——`params_declared = True` 恒真，该维度实际不参与分级，注释在误导读者
     以为有判定。
- **严重度**: P2

---

## 汇总

| # | 发现 | 严重度 |
|---|------|--------|
| F1 | snapshot_inputs 快照已存在输出 → 新产物被旧产物覆盖（实测复现） | **P0** |
| F2 | N30 输出缺失检测被 `if ec==0: ec_out=0` 复位成死代码 | P1 |
| F3 | env_fp 只写不查：验证降级与 resume 闸门都不消费 | P1 |
| F4 | env_fp 二进制/插件 JAR 覆盖缺口（blast 套件/RNAfold/hmmscan/ssearch36/7 插件） | P1 |
| F5 | _IMPL_REGISTRY 双轨：守卫死代码，tableMerge/efpHeat 手写修复被旁路（实测） | P1 |
| F6 | executor↔workflow 循环残留（executor 从 workflow import 自己的符号） | P1 |
| F7 | clear_specs_cache 死钩子 + 三处缓存无失效机制 | P2 |
| F8 | env_fp 全量 hash 无缓存 + PATH 依赖 | P2 |
| F9 | command_spec import 期构建 294 specs + overlay 副作用 | P2 |
| F10 | overlay 裸 except 吞掉校验器自身故障 | P2 |
| F11 | cleanup_side_effects 只扫 CWD，输入目录残留漏清 | P2 |
| F12 | 双序列化器/死常量/import 顺序敏感/微问题簇 | P2 |

## 最值得改的 3 点

1. **F1（P0）**：快照集排除输出槽。这是保护机制反向破坏用户数据的实锤，影响所有 positional
   布局命令的重跑场景；修复成本小（末位产物后缀跳过 → 中期 output_path 显式传入），收益是
   消除"重跑拿旧结果"的静默错误。
2. **F3+F4（P1）**：把 env_fp 做完整——消费端接入 `_load_verification_report` 失效判定与
   execution_fp（JAR sha），二进制清单改从 KNOWN_DEPENDENCIES_STRUCT 派生。否则评审 #115
   的响应只是写了一个没人读的字段。
3. **F5（P1）**：消灭 _IMPL_REGISTRY/手写 impl 双轨。两个已结项修复（N3/N27）当前不在线上
   生效，且冲突守卫是死代码——用显式 HANDWRITTEN 集合收口，并顺手修 F2 的 ec_out 复位
   （同一区域的"保护被静默废掉"同类病）。
