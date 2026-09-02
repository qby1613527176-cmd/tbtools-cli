#!/usr/bin/env bash
# 批2 测试数据构造脚本（幂等）
# 生成 test_reports/data_b2/ 下的测试输入
set -euo pipefail
D="/home/elysia/tbtools-cli/test_reports/data_b2"
mkdir -p "$D"

# gxfMatch 用 genome.fa（含 chr1，匹配 input.gff3）
cat > "$D/genome.fa" <<'EOF'
>chr1
ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT
>chr2
TTTTGGGGCCCCAAAATTTTGGGGCCCCAAAATTTT
EOF

# pep2codon: cds.fa + pep.aln.fa（ID 需一致）
cat > "$D/cds.fa" <<'EOF'
>g1
ATGGCTAGCCTGTAA
>g2
ATGCATGGCTAA
EOF
cat > "$D/pep.aln.fa" <<'EOF'
>g1
MASL-
>g2
MHG--
EOF

# mggxf: genePair + simplified gff
cat > "$D/genePair.tsv" <<'EOF'
g1	g2
g3	g4
EOF
cat > "$D/sim.gff" <<'EOF'
chr1	g1	100	500	+
chr2	g2	700	900	-
chr3	g3	100	300	+
chr4	g4	400	600	-
EOF

# seqconvert 输入
cat > "$D/seq_in.fa" <<'EOF'
>seq1
ACGTACGTACGT
>seq2
TTTTCCCCAAAA
EOF

echo "data_b2 构造完成:"; ls -la "$D"
