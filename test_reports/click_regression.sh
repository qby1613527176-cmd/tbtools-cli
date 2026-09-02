#!/usr/bin/env bash
# click 入口回归测试（对标 run_examples.sh）
set -uo pipefail
cd /home/elysia/tbtools-cli
P=0; F=0
ok()   { echo "  ✅ $1"; P=$((P+1)); }
fail() { echo "  ❌ $1"; F=$((F+1)); }

echo "===== click 入口回归测试 ====="

echo "1. version"
bin/tbtools version >/dev/null 2>&1 && ok "version" || fail "version"

echo "2. doctor"
bin/tbtools doctor >/dev/null 2>&1 && ok "doctor" || fail "doctor"

echo "3. seq logo"
bin/tbtools seq logo examples/data/phylogeny/msa.fa /tmp/cr1.svg >/dev/null 2>&1 && [ -s /tmp/cr1.svg ] && ok "seq logo" || fail "seq logo"

echo "4. seq msa"
bin/tbtools seq msa examples/data/phylogeny/msa.fa /tmp/cr2.svg >/dev/null 2>&1 && [ -s /tmp/cr2.svg ] && ok "seq msa" || fail "seq msa"

echo "5. expr volcano"
bin/tbtools expr volcano examples/data/deg.txt /tmp/cr3.svg >/dev/null 2>&1 && [ -s /tmp/cr3.svg ] && ok "volcano" || fail "volcano"

echo "6. expr heatmap"
bin/tbtools expr heatmap examples/data/expr/expr.tsv /tmp/cr4.svg --log2 --cluster-row >/dev/null 2>&1 && [ -s /tmp/cr4.svg ] && ok "heatmap" || fail "heatmap"

echo "7. expr pca"
bin/tbtools expr pca examples/data/expr/expr.tsv /tmp/cr5.svg row >/dev/null 2>&1 && [ -s /tmp/cr5.svg ] && ok "pca" || fail "pca"

echo "8. syn circos (动态转发)"
bin/tbtools syn circos examples/data/synteny/chrlen.txt examples/data/synteny/links.txt examples/data/synteny/genepos.txt /tmp/cr6.svg >/dev/null 2>&1 && [ -s /tmp/cr6.svg ] && ok "circos" || fail "circos"

echo "9. tree draw"
bin/tbtools tree draw test_reports/data_b5/tree.config /tmp/cr7.svg >/dev/null 2>&1 && [ -s /tmp/cr7.svg ] && ok "tree" || fail "tree"

echo "10. tool stat-fasta"
bin/tbtools tool stat-fasta examples/data/rpc/gras6_pep.fa /tmp/cr8.xls >/dev/null 2>&1 && [ -s /tmp/cr8.xls ] && ok "stat-fasta" || fail "stat-fasta"

echo "11. stdin 管道"
printf '>s1\nACGTACGT\n' | bin/tbtools tool stat-fasta - - >/dev/null 2>&1 && ok "stdin" || fail "stdin"

echo "12. --quiet"
bin/tbtools seq logo examples/data/phylogeny/msa.fa /tmp/cr9.svg --quiet >/dev/null 2>&1 && [ -s /tmp/cr9.svg ] && ok "quiet" || fail "quiet"

echo "13. 错误处理"
err=$(bin/tbtools seq logo /nonexistent /tmp/bad.svg 2>&1); echo "$err" | grep -q "❌" && ok "错误提示" || fail "错误提示"

echo "14. 退出码"
bin/tbtools seq logo /nonexistent /tmp/bad.svg >/dev/null 2>&1; [ $? -eq 2 ] && ok "退出码2" || fail "退出码"

echo ""
echo "===== 结果: PASS=$P  FAIL=$F ====="
[ $F -eq 0 ] && echo "✅ 全部通过" || echo "❌ 有 $F 项失败"
