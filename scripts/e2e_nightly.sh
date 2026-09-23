#!/usr/bin/env bash
# nightly 真实引擎 E2E(每日 CI): 代表命令 × 真实 JAR × 真实 examples 数据
# 断言: 退出码 0 + 输出文件存在且非 0 字节
# 用例选已实测稳定的命令(数据匹配); 扩展新用例需先本地验证
set -u
cd "$(dirname "$0")/.."
DATA=examples/data
OUT=$(mktemp -d)
PASS=0; FAIL=0; FAILED_LIST=()

run_case() {
  local group=$1 cmd=$2 outfile=$3; shift 3
  local svg_out=$OUT/$outfile
  python3 -m tbtools_cli.cli "$group" "$cmd" "$@" "$svg_out" >/dev/null 2>&1
  local ec=$?
  if [[ $ec -eq 0 && -s "$svg_out" ]]; then
    PASS=$((PASS+1)); echo "✅ $group $cmd"
  else
    FAIL=$((FAIL+1)); FAILED_LIST+=("$group $cmd (ec=$ec)")
    echo "❌ $group $cmd (ec=$ec)"
  fi
}

run_case expr volcano      outlier.svg    $DATA/deg.txt
run_case syn  msy          msy.svg        $DATA/synteny/msy/genes2.pos $DATA/synteny/msy/genes3.pos $DATA/synteny/msy/links2.txt
run_case tree rooting      rooted.nwk     $DATA/treeRooting/unrooted.nwk
# dualsyn: 输出须先于 --chr(click 位置参数在 option 前); 其余同 run_case
python3 -m tbtools_cli.cli syn dualsyn $DATA/synteny/dual.gff $DATA/synteny/dual.collinearity $OUT/dual.svg --chr1 1 --chr2 1 >/dev/null 2>&1
if [[ $? -eq 0 && -s "$OUT/dual.svg" ]]; then
  PASS=$((PASS+1)); echo "✅ syn dualsyn"
else
  FAIL=$((FAIL+1)); FAILED_LIST+=("syn dualsyn (ec=$?)"); echo "❌ syn dualsyn"
fi
run_case table tableCollapse coll.tsv     $DATA/table/tableCollapse.in.tsv 0

# 2026-09-23 补录(本地验证通过后加入): hclust 三列距离 / gxfSplit 前缀 / venn2 --graph
printf 'G1\tG2\t0.5\nG1\tG3\t1.2\nG2\tG3\t0.8\nG2\tG4\t1.5\nG3\tG4\t0.3\nG4\tG1\t2.0\n' > "$OUT/dist3.tsv"
run_case expr hclust        hclust.svg    "$OUT/dist3.tsv"
python3 -m tbtools_cli.cli gxf gxfSplit "$DATA/gxf/input.gff3" "$OUT/gx" >/dev/null 2>&1
if [[ $? -eq 0 && -s "$OUT/gx.split.1.gxf" ]]; then
  PASS=$((PASS+1)); echo "✅ gxf gxfSplit"
else
  FAIL=$((FAIL+1)); FAILED_LIST+=("gxf gxfSplit"); echo "❌ gxf gxfSplit"
fi
python3 -m tbtools_cli.cli sets venn2 --List1 "$DATA/table/uniq/m1.txt" --List2 "$DATA/table/uniq/m2.txt" --label1 A --label2 B --graph "$OUT/venn.svg" --prefix "$OUT/vp" >/dev/null 2>&1
if [[ $? -eq 0 && -s "$OUT/venn.svg" ]]; then
  PASS=$((PASS+1)); echo "✅ sets venn2"
else
  FAIL=$((FAIL+1)); FAILED_LIST+=("sets venn2"); echo "❌ sets venn2"
fi

echo ""
echo "════════════════════════════════"
echo "E2E nightly: PASS=$PASS FAIL=$FAIL"
if [[ $FAIL -gt 0 ]]; then
  printf '  失败: %s\n' "${FAILED_LIST[@]}"
  rm -rf "$OUT"
  exit 1
fi
rm -rf "$OUT"
exit 0