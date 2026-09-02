#!/usr/bin/env bash
# 批6 数据准备：构造 PAF/mcscanx-blast/supercircos-config/multisyn-lst/dotplot 输入
set -e
cd /home/elysia/tbtools-cli
mkdir -p test_reports/data_b6 /tmp/b6

# 1) PAF 13 列（pafviz/pafcomp/pafref 用）— 3 条比对照
cat > test_reports/data_b6/sample.paf << 'EOF'
qScaf1	5000	0	2000	+	tScaf1	8000	1000	3000	2000	2000	255	cm:i:2000
qScaf1	5000	2000	4000	+	tScaf2	6000	0	2000	2000	2000	60	cm:i:2000
qScaf2	4000	0	1500	-	tScaf1	8000	3000	4500	1500	1500	255	cm:i:1500
EOF
echo "PAF OK: $(wc -l < test_reports/data_b6/sample.paf) 条"

# 2) mcscanx blast tab6（Co_wgd 简化 GFF 配套）— 同基因自比 + 跨基因
cat > test_reports/data_b6/mcscanx.blast << 'EOF'
scaffold_2074_fragment_3	snap_masked-scaffold_2074_fragment_3-processed-gene-0.46	100.0	100	0	0	1	100	1	100	1e-50	200
scaffold_1853_fragment_2	maker-scaffold_1853_fragment_2-snap-gene-0.3	100.0	100	0	0	1	100	1	100	1e-50	200
scaffold_317_fragment_6	maker-scaffold_317_fragment_6-snap-gene-0.0	100.0	100	0	0	1	100	1	100	1e-50	200
scaffold_317_fragment_6	geneX_other	85.0	100	5	2	1	100	1	100	1e-30	150
EOF
echo "blast OK"

# 3) supercircos config（复用 synteny 数据）
cat > test_reports/data_b6/super.cfg << 'EOF'
[chrLen] examples/data/synteny/chrlen.txt
[link] examples/data/synteny/links.txt
[gene] examples/data/synteny/genepos.txt
[track] HeatMap examples/data/expr/expr.tsv 0 10000000 255,0,0 0,0,255 0,255,0 1000
[width] 800
[height] 800
EOF
echo "supercircos cfg OK"

# 4) multisyn lst 修正（指向 multi/ 下真实文件）
cat > test_reports/data_b6/gxf.lst << 'EOF'
examples/data/synteny/multi/sp1.gff
examples/data/synteny/multi/sp2.gff
examples/data/synteny/multi/sp3.gff
EOF
cat > test_reports/data_b6/collinear.lst << 'EOF'
examples/data/synteny/multi/sp1_sp2.collinearity
examples/data/synteny/multi/sp2_sp3.collinearity
examples/data/synteny/multi/sp3_sp1.collinearity
EOF
echo "multisyn lst OK"

# 5) dotplot 输入（简化 GFF + pairs + chrLayout）
cat > test_reports/data_b6/dot.gff << 'EOF'
Chr1	gene1	1000	5000	+
Chr1	gene2	6000	10000	+
Chr2	geneA	2000	6000	+
Chr2	geneB	7000	11000	+
EOF
cat > test_reports/data_b6/dot.pairs << 'EOF'
gene1	geneA
gene2	geneB
EOF
cat > test_reports/data_b6/dot.layout << 'EOF'
Genome: Chr1 Chr2
EOF
echo "dotplot inputs OK"

# 6) circlegene 输入（简化 GFF + mRNA ID 列表）
cat > test_reports/data_b6/cg.gff << 'EOF'
Chr1	TBtools	gene	1000	5000	.	+	.	ID=Gene1
Chr1	TBtools	mRNA	1000	5000	.	+	.	ID=Gene1.mRNA1;Parent=Gene1
Chr1	TBtools	gene	6000	10000	.	+	.	ID=Gene2
Chr1	TBtools	mRNA	6000	10000	.	+	.	ID=Gene2.mRNA1;Parent=Gene2
Chr2	TBtools	gene	2000	6000	.	+	.	ID=GeneA
Chr2	TBtools	mRNA	2000	6000	.	+	.	ID=GeneA.mRNA1;Parent=GeneA
Chr2	TBtools	gene	7000	11000	.	+	.	ID=GeneB
Chr2	TBtools	mRNA	7000	11000	.	+	.	ID=GeneB.mRNA1;Parent=GeneB
EOF
printf 'Gene1.mRNA1\nGene2.mRNA1\nGeneA.mRNA1\nGeneB.mRNA1\n' > test_reports/data_b6/cg.ids.txt
printf 'Gene1.mRNA1\tGeneA.mRNA1\nGene2.mRNA1\tGeneB.mRNA1\n' > test_reports/data_b6/cg.links.txt
echo "circlegene inputs OK"

# 7) msy 数据已在 synteny/msy/（genes2.pos/links2/layout2）
echo "ALL B6 DATA READY"
ls -la test_reports/data_b6/