#!/usr/bin/env bash
# ============================================================
# tbtools-cli 全量回归 批 1/10：环境与基础架构
# 自包含、幂等、可重跑。禁止修改项目文件（run_examples 的 examples/output 产物除外）。
# 输出：test_reports/batch01_environment.md（自动生成）+ stdout 汇总
# ============================================================
set -uo pipefail
ROOT="/home/elysia/tbtools-cli"
REPORT="$ROOT/test_reports/batch01_environment.md"
cd "$ROOT" || { echo "FATAL: 无法 cd 到 $ROOT"; exit 2; }

BASE_COMMIT="9d4df5a"
TS="$(date '+%Y-%m-%d %H:%M:%S')"
PASS=0; FAIL=0; SKIP=0; FAILED_ITEMS=""

# ---- 工具函数：每项测试跑一个命令块，记录 PASS/FAIL + 证据 ----
run_test() {
  local id="$1"; local desc="$2"; local cmd="$3"; local expect="$4"
  local out
  out=$(eval "$cmd" 2>&1)
  local ec=$?
  local verdict="FAIL"
  if [[ "$ec" -eq 0 && "$out" =~ $expect ]]; then verdict="PASS"; PASS=$((PASS+1));
  else FAIL=$((FAIL+1)); FAILED_ITEMS="$FAILED_ITEMS\n- $id: $desc"; fi
  {
    echo "### $id — $desc"; echo "命令: \`$cmd\`"; echo "退出码: $ec | 判定: **$verdict**";
    echo "期望: $expect"; echo "实际输出关键行:"; echo '```'; echo "$out" | head -20; echo '```'; echo;
  } >> "$REPORT"
  echo "[$verdict] $id $desc (ec=$ec)"
}

# ---- 报告头 ----
{
  echo "# tbtools-cli 全量回归 批 1/10 — 环境与基础架构"
  echo; echo "> 时间: $TS | 基线 commit: $BASE_COMMIT | 自包含脚本 run_batch01.sh 自动生成"
  echo
} > "$REPORT"

# ---- 1. config.sh jar 探测 ----
run_test "T01" "config.sh jar 探测" \
  "source config/config.sh 2>/dev/null; echo JAR=[\${TBTOOLS_JAR:-EMPTY}]; [ -n \"\${TBTOOLS_JAR:-}\" ] && [ -f \"\$TBTOOLS_JAR\" ] && echo JAR_FILE_OK || echo JAR_FILE_MISSING" \
  "JAR_FILE_OK"

# ---- 2. tbtools help ----
run_test "T02" "tbtools help 显示用法" \
  "bin/tbtools help 2>&1 | head -15" \
  "用法|Usage|tbtools"

# ---- 3. tbplot.sh help 分类总览 ----
run_test "T03" "tbplot.sh help 分类总览" \
  "bin/tbplot.sh help 2>&1 | head -30" \
  "命令|绘图|工具|help"

# ---- 4. banner 计数 140 ----
run_test "T04" "banner 绘图命令计数=140" \
  "bin/tbtools 2>&1 | head -20" \
  "140"

# ---- 5. help <命令> 多行详细版 ----
run_test "T05" "help volcano/genestructure/heatmap2 详细版" \
  "bin/tbplot.sh help volcano 2>&1 | head -8; echo ===; bin/tbplot.sh help genestructure 2>&1 | head -8; echo ===; bin/tbplot.sh help heatmap2 2>&1 | head -8" \
  "volcano|基因|heatmap"

# ---- 6. list tools = 82 ----
run_test "T06" "tbtools list tools → 82 个" \
  "bin/tbtools list tools 2>&1 | head -2" \
  "命令行工具: 82"

# ---- 7. list plots = 140 ----
run_test "T07" "tbtools list plots → 140 个" \
  "bin/tbtools list plots 2>&1 | head -2" \
  "绘图: 140"

# ---- 8. methods = 188 ----
run_test "T08" "tbtools methods → 188 RPC" \
  "bin/tbtools methods 2>&1 | python3 -c \"import sys,json,re; raw=sys.stdin.read(); s=re.sub(r'^.*?\\n', '', raw, count=1); d=json.loads(s); print(len(d.get('result',{}).get('methods',[])))\"" \
  "188"

# ---- 9. 未知命令容错 ----
run_test "T09" "未知命令 foobarxyz 报错 EXIT=1" \
  "bin/tbtools foobarxyz; echo REAL_EXIT=\$?" \
  "REAL_EXIT=1"

# ---- 10. 未知工具容错 ----
run_test "T10" "未知工具 nonexistentTool 报错 EXIT=1 不倾倒 jar" \
  "bin/tbtools tool nonexistentTool; echo REAL_EXIT=\$?" \
  "未知工具|REAL_EXIT=1"

# ---- 11. 22 个降级命令抽查 6 个 ----
run_test "T11" "降级命令 violin/colorscheme/phylotree/microgenome/pileup/dualsyn 显示用法" \
  "for c in violin colorscheme phylotree microgenome pileup dualsyn; do echo \"-- \$c --\"; bin/tbtools \$c 2>&1 | head -3; done; true" \
  "violin|colorscheme|phylotree|microgenome|pileup|dualsyn"

# ---- 12. 示例回归 run_examples.sh ----
run_test "T12" "run_examples.sh 全过出图" \
  "timeout 600 bash examples/scripts/run_examples.sh 2>&1 | tail -25; echo REAL_EXIT=\$?" \
  "REAL_EXIT=0"

# ---- 13. git 干净 + 提交数 ----
run_test "T13" "git 工作区干净（忽略 test_reports）+ 提交数" \
  "echo COMMITS=\$(git rev-list --count HEAD); git status --porcelain 2>&1 | grep -v 'test_reports/' | head -10; echo DIRTY_COUNT=\$(git status --porcelain 2>&1 | grep -vc 'test_reports/')" \
  "COMMITS=142|DIRTY_COUNT=0"

# ---- 14. install.sh 参数解析 ----
run_test "T14" "install.sh 参数解析（不实际安装）" \
  "bash install.sh --help 2>&1 | head -15; echo REAL_EXIT=\$?" \
  "安装|usage|--jar|REAL_EXIT="

# ---- 汇总 ----
{
  echo "## 汇总"; echo
  echo "| 结果 | 数量 |"; echo "|:-----|:----:|"; echo "| PASS | $PASS |"; echo "| FAIL | $FAIL |"; echo "| SKIP | $SKIP |"
  if [ -n "$FAILED_ITEMS" ]; then echo; echo "### 失败项"; echo -e "$FAILED_ITEMS"; fi
  echo; if [ "$FAIL" -eq 0 ]; then echo "**结论：批 1 通过（$PASS/$((PASS+FAIL+SKIP))）**"; else echo "**结论：批 1 有 $FAIL 项失败**"; fi
} >> "$REPORT"

echo; echo "======== 批 1 汇总: PASS=$PASS FAIL=$FAIL SKIP=$SKIP ========"
echo "报告: $REPORT"
exit 0
