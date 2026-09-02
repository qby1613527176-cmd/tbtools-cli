# tbtools-cli 回归测试报告

> 时间: 2026-09-02 03:56:15 | 定义: batch04.def | 运行器 run_batch.sh 自动生成

### T401 — genestructure 基因结构图
命令: `cd /home/elysia/tbtools-cli && bin/tbplot.sh genestructure examples/data/gene_structure.gff examples/data/ids.txt /tmp/b4/gs.svg >/dev/null 2>&1; [ -s /tmp/b4/gs.svg ] && echo "B4OK=SVG_OK" || echo "B4OK=0"`
退出码: 0 | 判定: **PASS**
期望: B4OK=SVG_OK
实际输出关键行:
```
B4OK=SVG_OK
```

### T402 — motif Motif分布图（真实GRAS meme）
命令: `cd /home/elysia/tbtools-cli && bin/tbplot.sh motif test_reports/data_b4/meme_real.xml test_reports/data_b4/meme_ids.txt /tmp/b4/motif.svg >/dev/null 2>&1; [ -s /tmp/b4/motif.svg ] && echo "B4OK=SVG_OK" || echo "B4OK=0"`
退出码: 0 | 判定: **PASS**
期望: B4OK=SVG_OK
实际输出关键行:
```
B4OK=SVG_OK
```

### T403 — seqlogo 序列LOGO
命令: `cd /home/elysia/tbtools-cli && bin/tbplot.sh seqlogo examples/data/phylogeny/msa.fa /tmp/b4/logo.svg >/dev/null 2>&1; [ -s /tmp/b4/logo.svg ] && echo "B4OK=SVG_OK" || echo "B4OK=0"`
退出码: 0 | 判定: **PASS**
期望: B4OK=SVG_OK
实际输出关键行:
```
B4OK=SVG_OK
```

### T404 — heatmap2 聚类热图
命令: `cd /home/elysia/tbtools-cli && bin/tbplot.sh heatmap2 examples/data/expression2/expr_matrix.tsv /tmp/b4/hm2.svg >/dev/null 2>&1; [ -s /tmp/b4/hm2.svg ] && echo "B4OK=SVG_OK" || echo "B4OK=0"`
退出码: 0 | 判定: **PASS**
期望: B4OK=SVG_OK
实际输出关键行:
```
B4OK=SVG_OK
```

### T405 — cubeheatmap 3D立方体热图（group无表头）
命令: `cd /home/elysia/tbtools-cli && bin/tbplot.sh cubeheatmap test_reports/data_b4/cube_expr.tsv test_reports/data_b4/cube_group3_nohdr.tsv /tmp/b4/cube.svg >/dev/null 2>&1; [ -s /tmp/b4/cube.svg ] && echo "B4OK=SVG_OK" || echo "B4OK=0"`
退出码: 0 | 判定: **PASS**
期望: B4OK=SVG_OK
实际输出关键行:
```
B4OK=SVG_OK
```

### T406 — layoutheatmap 布局热图
命令: `cd /home/elysia/tbtools-cli && bin/tbplot.sh layoutheatmap test_reports/data_b4/layout2.tsv examples/data/expr/expr.tsv /tmp/b4/lh.svg >/dev/null 2>&1; [ -s /tmp/b4/lh.svg ] && echo "B4OK=SVG_OK" || echo "B4OK=0"`
退出码: 0 | 判定: **PASS**
期望: B4OK=SVG_OK
实际输出关键行:
```
B4OK=SVG_OK
```

### T407 — efpHeat eFP组织表达热图
命令: `cd /home/elysia/tbtools-cli && bin/tbplot.sh efpHeat examples/data/efp/plant_bg.tga examples/data/efp/sample2cc.txt examples/data/efp/expmat.tsv GENE1 /tmp/b4/efp.svg >/dev/null 2>&1; [ -s /tmp/b4/efp.svg ] && echo "B4OK=SVG_OK" || echo "B4OK=0"`
退出码: 0 | 判定: **PASS**
期望: B4OK=SVG_OK
实际输出关键行:
```
B4OK=SVG_OK
```

### T408 — multiEfp 多矩阵eFP
命令: `cd /home/elysia/tbtools-cli && bin/tbplot.sh multiEfp examples/data/efp/plant_bg.tga examples/data/efp/sample2cc.txt examples/data/efp/expmat.tsv GENE1 /tmp/b4/mefp.svg >/dev/null 2>&1; [ -s /tmp/b4/mefp.svg ] && echo "B4OK=SVG_OK" || echo "B4OK=0"`
退出码: 0 | 判定: **PASS**
期望: B4OK=SVG_OK
实际输出关键行:
```
B4OK=SVG_OK
```

### T409 — cddmotif CDD保守域图
命令: `cd /home/elysia/tbtools-cli && bin/tbplot.sh cddmotif test_reports/data_b4/cdd.hitdata.txt test_reports/data_b4/prot.fa /tmp/b4/cdd.svg examples/data/phylogeny/root.nwk >/dev/null 2>&1; [ -s /tmp/b4/cdd.svg ] && echo "B4OK=SVG_OK" || echo "B4OK=0"`
退出码: 0 | 判定: **PASS**
期望: B4OK=SVG_OK
实际输出关键行:
```
B4OK=SVG_OK
```

### T410 — pfammotif Pfam域图
命令: `cd /home/elysia/tbtools-cli && bin/tbplot.sh pfammotif test_reports/data_b4/pfamscan.txt test_reports/data_b4/prot.fa /tmp/b4/pfam.svg examples/data/phylogeny/root.nwk >/dev/null 2>&1; [ -s /tmp/b4/pfam.svg ] && echo "B4OK=SVG_OK" || echo "B4OK=0"`
退出码: 0 | 判定: **PASS**
期望: B4OK=SVG_OK
实际输出关键行:
```
B4OK=SVG_OK
```

### T411 — seqlentrack 序列长度骨架
命令: `cd /home/elysia/tbtools-cli && bin/tbplot.sh seqlentrack test_reports/data_b4/seqlen.txt /tmp/b4/seqlen.svg examples/data/phylogeny/root.nwk >/dev/null 2>&1; [ -s /tmp/b4/seqlen.svg ] && echo "B4OK=SVG_OK" || echo "B4OK=0"`
退出码: 0 | 判定: **PASS**
期望: B4OK=SVG_OK
实际输出关键行:
```
B4OK=SVG_OK
```

## 汇总

| 结果 | 数量 |
|:-----|:----:|
| PASS | 11 |
| FAIL | 0 |
| SKIP | 0 |

**结论：本批通过（11/11）**

---

## 附录（09/02 04:40 补测）

### T412 — amazingmeta 组合图（树+结构+域）
命令: `bin/tbplot.sh amazingmeta test_reports/data_b4/meme_real.xml examples/data/phylogeny/root.nwk /tmp/b4v/am.svg test_reports/data_b4/seqlen.txt`
退出码: 0 | 判定: **PASS**
期望: B4OK=SVG_OK
实际输出关键行:
```
amazingmeta=SVG_OK (5324 bytes)
```

> 批 4 实际全量 = 12/12（T401-T412 全 PASS）
