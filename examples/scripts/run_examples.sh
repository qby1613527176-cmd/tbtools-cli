#!/usr/bin/env bash
# ============================================================
# run_examples.sh — 运行全部示例，验证 TBtools CLI（新 Python 入口）
# 用法: ./run_examples.sh [输出目录]
# 依赖: TBTOOLS_JAR 已配置(未配置时先 tbtools setup/fetch-jar)
# ============================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DATA="$ROOT/examples/data"
OUT="${1:-$ROOT/examples/output}"
mkdir -p "$OUT"

# 统一入口: 优先 python -m(源码), 兼容已 pip 安装的 tbtools
if command -v tbtools >/dev/null 2>&1; then
    TB="tbtools"
else
    TB="python3 -m tbtools_cli.cli"
fi

echo "=============================================="
echo " TBtools CLI 示例运行(新入口: $TB)"
echo " 输出目录: $OUT"
echo "=============================================="

# 1. 基因结构图 (seq genestructure)
echo ""
echo "[1/8] 基因结构图 (genestructure)"
$TB seq genestructure "$DATA/gene_structure.gff" "$DATA/ids.txt" "$OUT/01_gene_structure.svg" 2>&1 | tail -1

# 2. 热图（聚类）(expr heatmap)
echo ""
echo "[2/8] 热图 (heatmap)"
$TB expr heatmap "$DATA/expression.tsv" "$OUT/02_heatmap.svg" --row-scale --cluster-row --cluster-col 2>&1 | tail -1

# 3. PCA (expr pca)
echo ""
echo "[3/8] PCA (pca)"
$TB expr pca "$DATA/expression.tsv" "$OUT/03_pca.svg" row 2>&1 | tail -1

# 4. 火山图 (expr volcano)
echo ""
echo "[4/8] 火山图 (volcano)"
$TB expr volcano "$DATA/deg.txt" "$OUT/04_volcano.svg" --pval-cutoff 0.05 --fc-cutoff 1.0 2>&1 | tail -1

# 5. 序列 LOGO (seq logo)
echo ""
echo "[5/8] 序列 LOGO (seqlogo)"
$TB seq logo "$DATA/sequences.fa" "$OUT/05_seqlogo.svg" 2>&1 | tail -1

# 6. 五集合韦恩 (sets venn5: 位置参数 <out> <setA..E> [labels])
echo ""
echo "[6/8] 五集合韦恩 (venn5)"
$TB sets venn5 "$OUT/06_venn5.svg" "$DATA/set_0.txt" "$DATA/set_1.txt" "$DATA/set_2.txt" \
    "$DATA/set_3.txt" "$DATA/set_4.txt" A B C D E 2>&1 | tail -1

# 7. 差异表达双直方图 (expr dehist)
echo ""
echo "[7/8] 差异表达双直方图 (dehist)"
$TB expr dehist "$DATA/deg.txt" "$OUT/07_dehist.svg" 2>&1 | tail -1

# 8. UpSet 交集图 (sets upset: 位置参数 <set1..N.txt> <out.svg>)
echo ""
echo "[8/8] UpSet 交集图 (upset)"
printf 'E1\nE2\nE3\n' > "$OUT/08_setA.txt"
printf 'E2\nE3\nE4\n' > "$OUT/08_setB.txt"
printf 'E3\nE4\nE5\n' > "$OUT/08_setC.txt"
$TB sets upset "$OUT/08_setA.txt" "$OUT/08_setB.txt" "$OUT/08_setC.txt" "$OUT/08_upset.svg" 2>&1 | tail -1

echo ""
echo "=============================================="
echo " 完成！示例输出在: $OUT"
ls -la "$OUT"/*.svg 2>/dev/null | awk '{print "  " $NF " (" $5 "B)"}'
echo "=============================================="
