# 门禁/工程独立审查 — tbtools-cli v1.4.65

审查日期: 2026-10-05 · 审查视角: 独立门禁/工程(只找问题) · 范围: pyproject.toml / scripts/gen_metadata.py / .github/workflows/test.yml / tests/test_conformance_verified.py / tests/verification_report.json
前置: 评审 #115 预审 4/4 P1 + 3/3 P2(语义断言/引擎指纹/归档判定/域标注/模式表/mypy 收窄/skip 口径)视为已响应,本审查只列**新增发现**。

## 总体结论: 不通过(有条件)

门禁框架完整但存在三个自伤性盲区:**守门人自身不受检**(gen_metadata.py 不在 mypy/ruff 有效覆盖内,实测 3 个 mypy 错误长期存在)、**关键防御路径全靠 `except Exception: pass` 静默降级**(--check 可对"生成步骤整个崩掉"报全同步)、**版本源漂移**(pyproject=1.4.46 vs 实际 v1.4.65,wheel 携带错误版本号发布)。P0×3,P1×5,P2×3。

---

## P0

### P0-1 gen_metadata.py(门禁本体)不在任何静态检查覆盖内,实测 3 个 mypy 错误
- **发现**: pyproject `[tool.mypy]` 无 files 限定但 CI 显式 `mypy tbtools_cli/`; ruff 全仓 lint 但 `E501/E722/E701/E702` 忽略 + scripts/gen_metadata.py 内大量单行多语句风格恰好落在被忽略规则上。实测 `mypy scripts/gen_metadata.py` 报 3 错: 219/450 `var-annotated`(check_untyped_defs 全局开启但不查它)、559 `import-untyped`(yaml stub 缺失——pyproject 的豁免收窄到 `tbtools_cli.*`,恰好把 scripts/ 挡在豁免外)。
- **挑战**: #115 P2-7 把 import-untyped 豁免从全局收窄到 `tbtools_cli.*` 是正确方向,但执行结果是**门禁脚本自身失去了豁免又没有被纳入检查**——收窄只保护了包内,守门人被留在真空中。gen_metadata.py 560+ 行、承载 --check/--render/TTL/投影全部逻辑,是全仓最高杠杆文件,却是检查密度最低的文件。
- **建议**: CI 增加 `mypy scripts/gen_metadata.py`(或 pyproject `files = ["tbtools_cli", "scripts/gen_metadata.py"]`),并对 `scripts.*` 加 per-module `import-untyped` 豁免(yaml)或装 types-PyYAML; 修掉 2 个 var-annotated。ruff 对 scripts/ 至少恢复 E9(语法错误级)。
- **严重度**: P0

### P0-2 --check/render 的关键环节 15 处 `except Exception: pass`——防御链静默降级,假阴性系统性存在
- **发现**: gen_metadata.py 中 census、coverage 统计、TTL 检查、error-codes、relations、readiness matrix、contracts YAML 导出、CATEGORY_MAP 导入、`scan_manual_commands` 第 3 步、ai/tools 残影清理前的列表等 **15 处 `except Exception`**(12 处直接 pass)。致命组合: `render_ai_manifest` 内 error-codes/relations/contracts 任一步抛异常 → 临时目录里这些文件**不生成** → `_written` 是按"实际生成了什么"收集的 → repo 里对应的旧文件**根本不进对比集** → --check 输出"497 个 surface 全同步"。即某生成步骤整体崩坏时门禁反而更绿。
- **挑战**: "497 surface 全同步"的表面数是可缩水的——surface 集合由渲染结果自报,崩得越多 surface 越少、越容易"全同步"。这是自指式检查的经典陷阱: 用被检系统的输出定义检查范围。
- **建议**: ① 所有 except 至少 `print(f"⚠️ {step} 降级: {e}")`(保留信号); ② --check 模式对"repo 存在但 fresh 未生成"的 expected surface(error-codes.json/relations.json/contracts/tools/*.yaml/tool-readiness.md 等已知区域)做**反向存在性断言**——repo 有而 fresh 无 = 生成失败 = fail; ③ `import yaml` 失败这类环境缺依赖应直接 fail(--check 的 contracts 导出被静默跳过即属此类)。
- **严重度**: P0

### P0-3 版本源漂移: pyproject.toml `version = "1.4.46"`,实际发布线 v1.4.65
- **发现**: pyproject.toml 第 7 行 `version = "1.4.46"`; `tbtools version` 输出 `tbtools-cli v1.4.46`; identity.py 注释已写到 v1.4.65,git log 连续评审响应提交。即最近 ~19 个版本的提交从未 bump 包版本,wheel/sdist 若此刻构建将携带 1.4.46。
- **挑战**: 门禁验证了 497 个 generated surface 的一致性,却没有任何 gate 校验"包版本 == 发布版本"。counts.md 校验数字防漂移,版本号恰恰是全仓唯一不被校验的关键数字。
- **建议**: ① 版本收敛到单一源(pyproject 或 `tbtools_cli/__init__.py.__version__` 二选一,另一处动态读); ② CI 加一步 `assert pyproject.version == cli.version`; ③ 若走 tag 发布,加 tag↔version 一致性检查。
- **严重度**: P0

---

## P1

### P1-1 coverage 纯展示无门槛,且 omit 规则不透明
- **发现**: pyproject `[tool.coverage.report]` 无 `fail_under`; CI `pytest --cov ... | tail -6` 后无任何阈值断言,覆盖率只看不拦。omit 了 cli_load.py 与 runtime/__init__.py 但无注释说明理由(cli_load 承载 CATEGORY_MAP——gen_metadata 分组推断依赖它)。
- **挑战**: "Coverage report (visible, non-blocking)" 名义诚实,但三件套(pytest/ruff/mypy)里 coverage 实际不是门禁成员; 覆盖率随 673 测试膨胀可以单调下降而无任何信号。
- **建议**: 设 `fail_under`(从当前实测值起步,哪怕 40%),或显式在 README/CI 注明"coverage 是观测指标非门禁"并定期人工审。
- **严重度**: P1

### P1-2 CI 依赖全不 pin,与本地环境无锁定对齐
- **发现**: CI `pip install click pytest ruff pyyaml mypy` 全部 latest,无 requirements-ci.txt/无 hash; ruff/mypy 版本滚动可能: 新版引入新规则 → CI 突然红(非代码变更); 或本地旧版通过、CI 新版失败,反之亦然。mypy 配置注释自称"与 CI 一致"但 CI 的 mypy 版本本身是浮动的,"一致"无从锚定。
- **建议**: 增加 `requirements-ci.txt`(或 pip-tools/uv lock)pin ruff/mypy/pytest/click/pyyaml,CI 与本地共用。
- **严重度**: P1

### P1-3 测试副作用直写 repo 工作树(tests/verification_report.json),证据可被本地环境污染
- **发现**: `test_all_full_compile_verified`(Tier1,无 integration marker,**任何环境都跑**)每次执行都重写 tests/verification_report.json。verified_at 保留逻辑依赖 contract_fp+env_fp 双匹配——但**本机无 JAR / 换了 JAR 路径 / 外部二进制缺失时 env_fp 不同**,54 个工具的 env_fingerprint 与 verified_at 被整体刷新为该机器的环境指纹和时间。开发者随手 `git add -A` 即把个人机器(甚至 CI ubuntu-latest)的指纹提交为"权威验证证据"。
- **挑战**: 证据文件的写入者与证据的消费者混在同一 git 流里,且写入触发条件是"跑了 pytest"而非"完成了验证"。--check 的 `_surface_hash` 特意忽略 verified_at 防假阳性,但**不忽略 env_fingerprint**——本地无 JAR 跑一次 pytest + 提交 = 54 条证据的 env_fp 漂移 + ai/tools/*.json 联动漂移。
- **建议**: ① 报告写入改为显式 opt-in(如 `TBTOOLS_WRITE_REPORT=1` 或独立脚本 `scripts/refresh_verification.py`),pytest 默认只读对比; ② 至少 env_fp 不匹配时**拒写**并告警,而非静默刷新。
- **严重度**: P1

### P1-4 skip 口径注释硬编码"52",实测 integration 已 69——口径文档化方式本身又漂移了
- **发现**: test.yml 注释 `echo "⚠️ 若输出含 52 skipped..."`; 实测 `-m integration` 收集 69 个(54 exec + 2 bin0 xfail + 其他集成),加上无 JAR 环境其他 skip,实际 skip 数早已不是 52。#115 E4 的"skip 口径显式报告"响应方式是把一个**会过期的数字**写进 CI echo 文案。
- **挑战**: 用硬编码数字回应"口径要显式"的评审,制造了新的漂移点——三个月后 CI echo 说 52、实际 71,比不解释更误导。
- **建议**: echo 改为动态(`pytest --collect-only -m integration | 计数`),或只说"EXECUTION_VERIFIED 断言在无 JAR 时 skip,数量见 -rfs 报告"不绑定具体数; PLAN.md 的 54/60 同理标注"截至 v1.4.65"。
- **严重度**: P1

### P1-5 Tier-2 真实执行证据在主 CI 完全缺席,exec_verified 54 的保鲜依赖手工/本地
- **发现**: test.yml(主门禁)无 JAR → 54 个 EXECUTION_VERIFIED 参数化用例全 skip; nightly-e2e.yml 存在但本审查未确认其是否跑 test_conformance_verified 全量 + 是否把新 verified_at/env_fp 回传仓库。主分支保护所依赖的"execution_verified: 54"数字,其再验证频率=有人记得在本机跑。
- **挑战**: 软 TTL(90 天 print)是唯一保鲜机制,而 print 在 CI log 里无人看(自己已注明"软告警不阻断")。若 nightly 不回写报告,54 条证据的 verified_at 会无限期停在最后一次本机运行。
- **建议**: 明确 nightly-e2e 是否回写 verification_report.json(自动 PR 或 artifact); 若不回写,TTL 升级为: >90 天在 nightly job 里 fail(而非 print),或自动开 issue。
- **严重度**: P1

---

## P2

### P2-1 报告结构四重冗余: execution_verified list / execution_verified_details / verified_tools / compile+conformance lists
- **发现**: verification_report.json 5 个 key 中 `execution_verified`(54 list)与 `execution_verified_details`(54 map)与 `verified_tools`(54 map)三份同信息; details 与 verified_tools 的条目字段几乎逐字重复(contract_fingerprint/env_fingerprint/verified_at/corpus/domain_note)。兼容旧读取器是保留理由,但整个文件由测试**覆盖式重建**——旧读取器兼容的对象根本不存在持久旧版。
- **建议**: 收敛为 `verified_tools` 单源(含 level 字段已可派生 execution/conformance 名单); compile_verified 保留(FULL 池名单,语义不同); 删除 execution_verified_details 与 execution_verified list,提供 `_load_verification_report` 端派生函数过渡一个版本。
- **严重度**: P2

### P2-2 counts/render 中 `rpc_methods: 188` 等硬编码数字自称"权威口径单一源"
- **发现**: render_commands_md 的 counts dict 中 `"rpc_methods": 188` 直接字面量,注释"(固定)"; counts.md 自称"自动生成,勿手改,README 数字以此对齐"——但该文件里有一个只能靠手改的数字。README 若与 188 对齐,则 README 的权威源仍是人。
- **建议**: rpc 方法数从代码扫描(rpc server 方法表/bridges 枚举)派生,或从 counts.md 移除并注明"RPC 方法数见 <源文件>",勿让硬编码披上"自动生成"外衣。
- **严重度**: P2

### P2-3 673 测试(题述 619+ 已过时)中防漂移/框架类占比高,单测边际价值递减且无分层预算
- **发现**: 673 collected(0.33s 收集); 大量测试本质是"metadata 数字断言/投影一致性快照"(test_yaml_snapshot_matches_known 类),价值是防漂移而非行为验证。当前无快速层/全量层划分(pytest marker 只有 integration),本地全跑成本尚低但增长无约束; CI 主 job 跑全量+跑两遍(coverage 一遍、正式一遍),重复执行。
- **建议**: ① 引入 `fast` marker 或按目录分层,PR 门禁跑 fast+投影一致性,nightly 跑全量; ② CI 去掉 coverage 与正式 pytest 的重复执行(`--cov` 合入正式跑); ③ 对"快照类"测试计数设上限预警(如占比 >40% 时提醒),倒逼行为测试占比。
- **严重度**: P2

---

## 最值得改的 3 点

1. **把守门人纳入门禁**(P0-1+P0-2 合并治理): gen_metadata.py 进 mypy/ruff 覆盖,15 处 `except Exception: pass` 改为"降级必告警 + 已知 surface 反向存在性断言"。一次修复同时消除"守门人不受检"和"崩了反而更绿"两个自伤盲区——这是全仓杠杆最高的一处改动。
2. **版本号单一源 + CI 校验**(P0-3): pyproject 与 CLI 输出版本对齐并加 assert 步骤。改动 10 行,消除"wheel 携带 1.4.46 发布"的静默事故。
3. **verification_report.json 写入权限收紧 + 结构收敛**(P1-3+P2-1): pytest 默认不直写 repo(改显式脚本/env 开关),报告收敛到 verified_tools 单源。同时解决"证据被本地环境污染"和"四重冗余"——证据可信度是 EXECUTION_VERIFIED 标签的地基。
