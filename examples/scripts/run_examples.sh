#!/usr/bin/env bash
# ============================================================
# run_examples.sh — 运行全部示例，验证 TBtools CLI
# 用法: ./run_examples.sh [输出目录]
# ============================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BIN="$ROOT/bin"
DATA="$ROOT/examples/data"
OUT="${1:-$ROOT/examples/output}"
mkdir -p "$OUT"

echo "=============================================="
echo " TBtools CLI 示例运行"
echo " 输出目录: $OUT"
echo "=============================================="

# 1. 基因结构图
echo ""
echo "[1/8] 基因结构图 (genestructure)"
"$BIN/tbplot.sh" genestructure "$DATA/gene_structure.gff" "$DATA/ids.txt" "$OUT/01_gene_structure.svg" 900 400 2>&1 | tail -1

# 2. 热图（聚类）
echo ""
echo "[2/8] 热图 (heatmap2)"
"$BIN/tbplot.sh" heatmap2 "$DATA/expression.tsv" "$OUT/02_heatmap.svg" --rowScale --clusterRow --clusterCol 2>&1 | tail -1

# 3. PCA
echo ""
echo "[3/8] PCA (pca)"
"$BIN/tbplot.sh" pca "$DATA/expression.tsv" "$OUT/03_pca.svg" row true 900 700 2>&1 | tail -1

# 4. 火山图
echo ""
echo "[4/8] 火山图 (volcano)"
"$BIN/tbplot.sh" volcano "$DATA/deg.txt" "$OUT/04_volcano.svg" 0.05 1.0 900 700 2>&1 | tail -1

# 5. 序列 LOGO
echo ""
echo "[5/8] 序列 LOGO (seqlogo)"
"$BIN/tbplot.sh" seqlogo "$DATA/sequences.fa" "$OUT/05_seqlogo.svg" 2>&1 | tail -1

# 6. 五集合韦恩
echo ""
echo "[6/8] 五集合韦恩 (venn5)"
"$BIN/tbplot.sh" venn5 "$OUT/06_venn5.svg" "$DATA/set_0.txt" "$DATA/set_1.txt" "$DATA/set_2.txt" "$DATA/set_3.txt" "$DATA/set_4.txt" A B C D E 2>&1 | tail -1

# 7. 差异表达双直方图
echo ""
echo "[7/8] 差异表达双直方图 (dehist)"
"$BIN/tbplot.sh" dehist "$DATA/deg.txt" "$OUT/07_dehist.svg" 1000 700 2>&1 | tail -1

# 8. UpSet 交集图
echo ""
echo "[8/8] UpSet 交集图 (upset)"
"$BIN/tbplot.sh" upset <(printf 'SetA\tE1\tE2\tE3\nSetB\tE2\tE3\tE4\nSetC\tE3\tE4\tE5\n') "$OUT/08_upset.svg" 900 700 2>&1 | tail -1

echo ""
echo "=============================================="
echo " 完成！示例输出在: $OUT"
ls -la "$OUT"
echo "=============================================="
