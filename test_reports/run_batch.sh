#!/usr/bin/env bash
# ============================================================
# tbtools-cli 全量回归 — 通用测试运行器
# 用法: bash run_batch.sh <定义文件> <输出报告>
# 定义文件每行(tab分隔): ID<TAB>DESC<TAB>EXPECT<TAB>CMD
#   只读测试项目; run_examples 等允许产物除外
# ============================================================
set -uo pipefail

DEF="${1:?需定义文件}"
REPORT="${2:?需报告路径}"
[ -f "$DEF" ] || { echo "FATAL: 定义文件不存在 $DEF"; exit 2; }

TS="$(date '+%Y-%m-%d %H:%M:%S')"
PASS=0; FAIL=0; SKIP=0; FAILED_ITEMS=""

# 报告头
{
  echo "# tbtools-cli 回归测试报告"
  echo; echo "> 时间: $TS | 定义: $(basename "$DEF") | 运行器 run_batch.sh 自动生成"
  echo
} > "$REPORT"

run_test() {
  local id="$1"; local desc="$2"; local expect="$3"; local cmd="$4"
  local out; local ec; local verdict
  out=$(eval "$cmd" 2>&1); ec=$?
  if [[ "$ec" -eq 0 && "$out" =~ $expect ]]; then verdict="PASS"; PASS=$((PASS+1));
  else verdict="FAIL"; FAIL=$((FAIL+1)); FAILED_ITEMS="$FAILED_ITEMS\n- $id: $desc"; fi
  {
    echo "### $id — $desc"
    echo "命令: \`$cmd\`"
    echo "退出码: $ec | 判定: **$verdict**"
    echo "期望: $expect"
    echo "实际输出关键行:"
    echo '```'; echo "$out" | head -15; echo '```'
    echo
  } >> "$REPORT"
  echo "[$verdict] $id $desc (ec=$ec)"
}

# 逐行执行定义（tab 分隔; 空行/# 开头跳过）
while IFS=$'\t' read -r id desc expect cmd; do
  [ -z "${id:-}" ] && continue
  case "$id" in \#*) continue;; esac
  run_test "$id" "$desc" "$expect" "$cmd"
done < "$DEF"

# 汇总
{
  echo "## 汇总"; echo
  echo "| 结果 | 数量 |"; echo "|:-----|:----:|"; echo "| PASS | $PASS |"; echo "| FAIL | $FAIL |"; echo "| SKIP | $SKIP |"
  if [ -n "$FAILED_ITEMS" ]; then echo; echo "### 失败项"; echo -e "$FAILED_ITEMS"; fi
  echo; if [ "$FAIL" -eq 0 ]; then echo "**结论：本批通过（$PASS/$((PASS+FAIL+SKIP))）**"; else echo "**结论：本批有 $FAIL 项失败**"; fi
} >> "$REPORT"

echo; echo "======== 汇总: PASS=$PASS FAIL=$FAIL SKIP=$SKIP ========"
echo "报告: $REPORT"
exit 0
