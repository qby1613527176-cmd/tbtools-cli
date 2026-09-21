# 批次 1 状态（复活类：N24 / N26 / N27 + 附带 efpHeat）

> 完成时间：2026-09-21 · 仓库未 commit（等待 main 统一 review）

## 1.1 N24（P1）`tool getLongestCompleteORF` —— ✅ 已修复
**根因**：注册表 `getLongestCompleteORF → biocjava.bioIO.ORF.ORF`（JavaFX 应用类，无 main，任何调用失败）。
**修复**：`auto_commands.py` 新增 `_getLongestCompleteORF_impl` 转发到 `_longestorf_impl` → `GetLongestORF`（ArgsParser `--inFa/--outORFs` 实测可用，jar 类枚举确认无 OrfBatchLongestComplete 类，MaxORFPredict 无 main）。
**验证**：`tbtools tool getLongestCompleteORF --inFa examples/data/rpc/cds_subject.fa --outORFs /tmp/x.fa` → ORF 3.5KB + 翻译 Pep 1.3KB + NoORF 清单（蛋白输入 0 ORF 属正常，需核酸输入）。

## 1.2 N26（P1）`syn msy` ClassNotFoundException —— ✅ 已修复
**根因**：表驱动化重构（09/20）把 msy 注册为 `('msy','bridge','GenericCli',...)` 裸透传 → 用户参数被 GenericCli 当 `args[0]=engineClass`（`Class.forName("genes2.pos")`）；tbplot.sh 旧入口调用方式正确。
**修复**：`auto_commands.py` 新增 `_msy_impl`，按 tbplot.sh 已验证方式显式拼参：`GenericCli MultipleSpeciesSyteny plot <out> --set inSimplifiedGff <pos> --set genePairInfoFile <links> --set chrLayoutFile <layout>`。
**验证**：`tbtools syn msy examples/data/synteny/msy/{genes2.pos,links2.txt,layout2.txt} /tmp/tb_msy.svg` → 4428B SVG（10 JIGElement，1 面板）。

## 1.3 N27（P1）`expr multiEfp` NoClassDefFoundError DatatypeConverter —— ✅ 已修复
**根因**：fake `javax/xml/bind/DatatypeConverter` 编译产物在 `build/`（被 .gitignore 排除），全新 checkout 无法重建（它不在桥源码里，ensure_bridge 只编译 bridges/*.java）。
**修复三件套**：
1. 源码入库：`bridges/javax/xml/bind/DatatypeConverter.java`（Base64/Hex/基础类型全实现）
2. `core.py ensure_bridge`：任何桥编译时检测 fake 源码，缺失/过期即 `javac -d build/` 重建（删 class 模拟全新 checkout 验证自动重建 2918B）
3. `auto_commands.py _make_impl`：direct 命令 classpath `-cp JAR` → `-cp BUILD_DIR:JAR`（direct 类运行时也可见 fake class）

**附带修复**：`efpHeat` 引擎实为 `--key value` 式（`--inTGA/--inSample2CC/--expMat/--geneId/--outImg`），旧 docstring 位置参数写法拒参——新增 `_efpHeat_impl`（命名参数直通 + 位置参数自动转换）。
**验证**：multiEfp 官方 efp 三件套 → 35,680B SVG；efpHeat → 35,529B SVG；fake class 自动重建 ✓。

## 测试
- 全量 pytest：**81 passed, 1 skipped**（含批次 2 rpc 语义测试）
- 新增 `tests/test_p0_protection.py` 11 项（批次 0）+ 本批改动经真实命令验证

## 遗留
- efpHeat/multiEfp 的 docstring 在 `docs/COMMAND_REFERENCE.md` 与 README 仍为位置参数写法，建议后续统一为命名参数示例（低优先，README 数字防漂移 pytest 会兜底）