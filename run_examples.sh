#!/usr/bin/env bash
# tbtools-cli 快速验证脚本 — 新用户一键跑通核心功能
# 用法: bash run_examples.sh
set -uo pipefail
cd "$(dirname "$0")"
PASS=0; FAIL=0; SKIP=0

ok()   { echo "  ✅ $1"; PASS=$((PASS+1)); }
fail() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
skip() { echo "  ⏭️  $1 (跳过)"; SKIP=$((SKIP+1)); }

echo "=============================================="
echo " tbtools-cli 快速验证（8 项核心功能）"
echo "=============================================="
echo ""

# 1. 环境
echo "1. 环境检查"
source config/config.sh 2>/dev/null
[ -n "${TBTOOLS_JAR:-}" ] && [ -f "$TBTOOLS_JAR" ] && ok "JAR: $TBTOOLS_JAR" || { fail "JAR 未找到"; exit 1; }

# 2. 帮助
echo "2. 帮助系统"
bin/tbplot.sh help >/dev/null 2>&1 && ok "tbplot.sh help" || fail "tbplot.sh help"
bin/tbtools help >/dev/null 2>&1 && ok "tbtools help" || fail "tbtools help"

# 3. 序列工具
echo "3. 序列工具"
bin/tbtools tool statFasta --inFasta examples/data/rpc/gras6_pep.fa --outPutFile /tmp/tbtools_ex_stat.xls >/dev/null 2>&1 && ok "statFasta" || fail "statFasta"

# 4. 绘图（SVG 输出）
echo "4. 绘图引擎"
mkdir -p /tmp/tbtools_ex
bin/tbplot.sh seqlogo examples/data/phylogeny/msa.fa /tmp/tbtools_ex/seqlogo.svg >/dev/null 2>&1 && ok "seqlogo" || fail "seqlogo"
bin/tbplot.sh volcano examples/data/deg.txt /tmp/tbtools_ex/volcano.svg >/dev/null 2>&1 && ok "volcano" || fail "volcano"
bin/tbplot.sh tree test_reports/data_b5/tree.config /tmp/tbtools_ex/tree.svg >/dev/null 2>&1 && ok "tree" || fail "tree"

# 5. 韦恩图
echo "5. 韦恩图"
java -Xmx2g -cp "$TBTOOLS_JAR" biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn2 \
  --List1 examples/data/set_0.txt --List2 examples/data/set_1.txt \
  --label1 A --label2 B --graph /tmp/tbtools_ex/venn2.svg --prefix /tmp/tbtools_ex/v2 --bgNum 30000 >/dev/null 2>&1 \
  && ok "venn2" || fail "venn2"

# 6. RPC（如服务器可用）
echo "6. RPC 数据工具"
if curl -s -m 5 http://127.0.0.1:8765/health >/dev/null 2>&1; then
  out=$(bin/tbtools_rpc.sh call FastaStat.process '{"inputPath":"examples/data/rpc/gras6_pep.fa","outputPath":"/tmp/tbtools_ex/stat_rpc.xls"}' 2>/dev/null)
  echo "$out" | grep -q '"ok": true' && ok "RPC FastaStat" || fail "RPC FastaStat"
else
  skip "RPC（服务器未启动，运行 tbtools server start）"
fi

# 7. 错误处理
echo "7. 错误处理"
err=$(bin/tbplot.sh tree /nonexistent.cfg /tmp/bad.svg 2>&1)
echo "$err" | grep -q "❌ 执行失败" && ok "友好错误提示" || fail "友好错误提示"

# 8. 未知命令
echo "8. 未知命令处理"
out=$(bin/tbplot.sh boguscmd 2>&1); echo "$out" | grep -q "未知命令" && ok "未知命令报错" || fail "未知命令报错"

echo ""
echo "=============================================="
echo " 结果: PASS=$PASS  FAIL=$FAIL  SKIP=$SKIP"
if [ "$FAIL" -eq 0 ]; then
  echo " ✅ 全部通过！tbtools-cli 工作正常。"
else
  echo " ❌ 有 $FAIL 项失败，请检查。"
fi
echo "=============================================="
exit $FAIL
