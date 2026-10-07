# RELEASING — 发布流程（硬 checklist）

> 自审 docs F5（2026-10-05）补：v1.4.19→v1.4.65 四十七连发的步骤此前只在编年史惯性里，
> grep 零命中 → 两个 P0（pyproject 版本不 bump / CHANGELOG 断更）的根因就是无 SOP。
> **本文件是唯一发布流程真源。发版必须逐项打勾。**

## 前置：完成一项可发布的变更

- 代码/文档改动已提交（`git add -A && git commit`）
- 质量门禁全绿：
  ```bash
  pytest tests/ -q && ruff check . && python3 -m mypy tbtools_cli/ scripts/gen_metadata.py
  python3 scripts/gen_metadata.py --check   # 含版本一致性门禁（vX.Y.Z 与 tag/README 对齐）
  ```
- ⚠️ pytest 全量按默认 deselect 跳过真实执行（无 JAR 环境 52 skipped）；有 JAR 时 Tier-2 真实执行应跑

## 发版步骤（逐项打勾）

1. **bump 版本**：`pyproject.toml` 第 7 行 `version = "v1.4.XX"` 改成新版本号
   （`tbtools version` / `__init__.py` 自 pyproject 单一源读取，无需改别处）
2. **更新 CHANGELOG.md**：顶部插入 `## [1.4.XX] - 日期` 段，条目风格：
   - `### 变更类型` + 要点列表（用 git log 从上一 tag 概括，如 `git log v1.4.YY..HEAD --oneline`）
   - 门禁数字一行：`**门禁**: pytest N passed + M skipped / ruff 0 / mypy 0`
3. **同步 agent-facing 数字**（自审 v1.4.86 docs F-NEW-9：不再靠人工核对，人工步骤结构性无效——上轮 v1.4.81 就是发版动作自己制造 294→298 漂移的）：
   ```bash
   python3 scripts/gen_metadata.py --render   # 刷新 counts.md / ai/ 全部生成式 surface
   python3 scripts/gen_metadata.py --check    # 全绿 = 数字已同步（含版本门禁）
   grep -n "Agent-facing tools" README.md     # 引用块数字应指向 counts.md（agent_ready_full/execution_verified/semantic_checked）
   ```
   README 里的具体数字必须**引用 counts.md 而非手写**；`--check` 全绿即视为数字核对完成。
4. **跑门禁确认**：第「前置」节三条全绿
5. **提交 + 打 tag**：
   ```bash
   git add -A && git commit -m "feat: <一句话>"
   git tag v1.4.XX
   ```
6. **push 同步**（网络可用后）：
   ```bash
   git push origin main --tags
   ```
7. **生成式 surface 落库**：若本版改了命令/spec（新收编工具）：
   ```bash
   python3 scripts/gen_metadata.py --render
   git add -A && git commit -m "chore: generated surface 同步(v1.4.XX)" && git tag v1.4.XX
   ```
8. **记忆同步**（MOSS 工作区惯例）：总清单追加波次 → MEMORY.md → 当日 daily note
9. **PyPI 发布（可选但推荐，2026-10-07 沉淀一键脚本）**：
   ```bash
   python3 scripts/release_pypi.py            # 全流程(门禁→快照→build→twine check→冒烟→upload→拉取验证)
   python3 scripts/release_pypi.py --dry-run  # 只 build+check+冒烟, 不上传(验证打包质量)
   ```
   - 前置：`~/.pypirc` token(600 权限)；pyproject 版本已 bump + tag 已打
   - 流程要点：verification_report.json 复制为包内快照(安装态 census/describe 可见验证证据，否则 exec_verified=0)；
     sdist 由 MANIFEST.in 约束(prune plugins/examples/tests, 防 JAR/二进制 75.8MB 进包)；
     twine/冒烟 venv 自动临时创建；上传后 simple 索引传播延迟自动重试拉取验证

## 版本一致性门禁（自动化）

`gen_metadata.py --check` 含版本门禁（自审 docs F1 响应）：
- `pyproject.toml` version == 最新 git tag（否则 ❌ 返回非 0）
- README.md 含当前 `vX.Y.Z`（否则 ❌）
- 发版时先 bump pyproject + 加 README badge 版本，--check 才过

## 回滚/修正

- 已 push 的坏 tag：`git tag -d v1.4.XX && git push origin :refs/tags/v1.4.XX`
  再重新发下一版（不覆盖历史 tag）
- 未 push：直接 `git tag -d v1.4.XX` 重发即可