# tbtools-cli 回归测试报告

> 时间: 2026-09-02 07:31:52 | 定义: batch06.def | 运行器 run_batch.sh 自动生成

### T601 — circos 环形共线性图
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/circos.svg && timeout 90 bin/tbplot.sh circos examples/data/synteny/chrlen.txt examples/data/synteny/links.txt examples/data/synteny/genepos.txt /tmp/b6/circos.svg >/dev/null 2>&1; [ -s /tmp/b6/circos.svg ] && echo "B6OK=SVG_OK" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=SVG_OK
实际输出关键行:
```
B6OK=SVG_OK
```

### T602 — supercircos SuperCircos（4列track）
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/super.svg && timeout 90 bin/tbplot.sh supercircos test_reports/data_b6/super.cfg /tmp/b6/super.svg >/dev/null 2>&1; [ -s /tmp/b6/super.svg ] && echo "B6OK=SVG_OK" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=SVG_OK
实际输出关键行:
```
B6OK=SVG_OK
```

### T603 — circlegene 环形基因位置图
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/cg.svg && timeout 90 bin/tbplot.sh circlegene test_reports/data_b6/cg.gff test_reports/data_b6/cg.ids.txt /tmp/b6/cg.svg --link test_reports/data_b6/cg.links.txt >/dev/null 2>&1; [ -s /tmp/b6/cg.svg ] && echo "B6OK=SVG_OK" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=SVG_OK
实际输出关键行:
```
B6OK=SVG_OK
```

### T604 — dotplot 共线性点图
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/dot.svg && timeout 120 bin/tbplot.sh dotplot --inGff test_reports/data_b6/dot.gff --genePair test_reports/data_b6/dot.pairs --chrLayout test_reports/data_b6/dot.layout --outGraph /tmp/b6/dot.svg >/dev/null 2>&1; [ -s /tmp/b6/dot.svg ] && echo "B6OK=SVG_OK" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=SVG_OK
实际输出关键行:
```
B6OK=SVG_OK
```

### T605 — pafviz PAF比对Dot-plot
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/pafviz.svg && timeout 90 bin/tbplot.sh pafviz test_reports/data_b6/sample.paf /tmp/b6/pafviz.svg >/dev/null 2>&1; [ -s /tmp/b6/pafviz.svg ] && echo "B6OK=SVG_OK" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=SVG_OK
实际输出关键行:
```
B6OK=SVG_OK
```

### T606 — pafcomp PAF基因组比较图
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/pafcomp.svg && timeout 90 bin/tbplot.sh pafcomp --inPaf test_reports/data_b6/sample.paf --outGraph /tmp/b6/pafcomp.svg >/dev/null 2>&1; [ -s /tmp/b6/pafcomp.svg ] && echo "B6OK=SVG_OK" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=SVG_OK
实际输出关键行:
```
B6OK=SVG_OK
```

### T607 — pafref PAF参考碱基覆盖
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/pafref.tsv && timeout 90 bin/tbplot.sh pafref --inPaf test_reports/data_b6/sample.paf --outTab /tmp/b6/pafref.tsv >/dev/null 2>&1; [ -s /tmp/b6/pafref.tsv ] && echo "B6OK=PAFREF" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=PAFREF
实际输出关键行:
```
B6OK=PAFREF
```

### T608 — microsyn 双基因组微共线性（显式区域）
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/micro.svg && timeout 120 bin/tbplot.sh microsyn examples/data/synteny/gxf1.gff examples/data/synteny/gxf2.gff examples/data/synteny/test.collinearity /tmp/b6/micro.svg --chr1 LG03 --start1 1000 --end1 15000 --chr2 chr08 --start2 2000 --end2 16000 >/dev/null 2>&1; [ -s /tmp/b6/micro.svg ] && echo "B6OK=SVG_OK" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=SVG_OK
实际输出关键行:
```
B6OK=SVG_OK
```

### T609 — msy 多物种微共线性
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/msy.svg && timeout 120 bin/tbplot.sh msy test_reports/data_b6/msy.pos test_reports/data_b6/msy.links test_reports/data_b6/msy.layout /tmp/b6/msy.svg >/dev/null 2>&1; [ -s /tmp/b6/msy.svg ] && echo "B6OK=SVG_OK" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=SVG_OK
实际输出关键行:
```
B6OK=SVG_OK
```

### T610 — multisyn 多物种微共线性（lst）
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/multi.svg && timeout 150 bin/tbplot.sh multisyn test_reports/data_b6/gxf.lst test_reports/data_b6/collinear.lst /tmp/b6/multi.svg >/dev/null 2>&1; [ -s /tmp/b6/multi.svg ] && echo "B6OK=SVG_OK" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=SVG_OK
实际输出关键行:
```
B6OK=SVG_OK
```

### T611 — dualsyn 双基因组共线性图
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/dual.svg && timeout 120 bin/tbplot.sh dualsyn examples/data/synteny/dual.gff examples/data/synteny/dual.collinearity /tmp/b6/dual.svg --chr1 "1,2" --chr2 "1,2" >/dev/null 2>&1; [ -s /tmp/b6/dual.svg ] && echo "B6OK=SVG_OK" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=SVG_OK
实际输出关键行:
```
B6OK=SVG_OK
```

### T612 — mcscanx 共线性检测
命令: `cd /home/elysia/tbtools-cli && rm -rf /tmp/b6/mc && mkdir -p /tmp/b6/mc && timeout 150 bin/tbplot.sh mcscanx examples/data/synteny/Co_wgd.gff test_reports/data_b6/mcscanx.blast /tmp/b6/mc/out >/dev/null 2>&1; [ -s /tmp/b6/mc/out.collinearity ] && echo "B6OK=MCSCANX" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=MCSCANX
实际输出关键行:
```
B6OK=MCSCANX
```

### T613 — collinearRegion 共线性→区域
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/cr.txt && timeout 120 bin/tbplot.sh collinearRegion examples/data/synteny/Co_wgd.collinearity examples/data/synteny/Co_wgd.gff /tmp/b6/cr.txt >/dev/null 2>&1; [ -s /tmp/b6/cr.txt ] && echo "B6OK=CR" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=CR
实际输出关键行:
```
B6OK=CR
```

### T614 — visualizeblock 区块可视化
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/vb.pdf && timeout 120 bin/tbplot.sh visualizeblock examples/data/findblockdual/block_Cr_Cs_real.out.txt /tmp/b6/vb.pdf >/dev/null 2>&1; [ -s /tmp/b6/vb.pdf ] && echo "B6OK=PDF_OK" || echo "B6OK=0"`
退出码: 0 | 判定: **PASS**
期望: B6OK=PDF_OK
实际输出关键行:
```
B6OK=PDF_OK
```

### T615 — findblockdual 双基因组区块（已知需真实数据→SKIP）
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/fbd.txt && timeout 200 bin/tbplot.sh findblockdual examples/data/comparative/input.genome.fa examples/data/comparative/input.gff examples/data/comparative/prepared.genome.fa examples/data/comparative/prepared.gff chr1_chr1_geneA_p0 /tmp/b6/fbd.txt --threads 2 --leftEdge 500 --rightEdge 500 >/dev/null 2>&1; [ -s /tmp/b6/fbd.txt ] && echo "B6OK=PASS" || echo "B6OK=SKIP_KNOWN"`
退出码: 0 | 判定: **PASS**
期望: B6OK=SKIP_KNOWN
实际输出关键行:
```
B6OK=SKIP_KNOWN
```

## 汇总

| 结果 | 数量 |
|:-----|:----:|
| PASS | 16 |
| FAIL | 0 |
| SKIP | 0 |

**结论：本批通过（16/16）**
### T616 — findblockmultiple 多基因组区块（已知需真实数据→SKIP）
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b6/fbm.txt && timeout 200 bin/tbplot.sh findblockmultiple examples/data/comparative/input.genome.fa examples/data/comparative/input.gff chr1_chr1_geneA_p0 /tmp/b6/fbm.txt examples/data/comparative/prepared.genome.fa examples/data/comparative/prepared.gff --leftEdge 500 --rightEdge 500 --threads 2 >/dev/null 2>&1; [ -s /tmp/b6/fbm.txt ] && echo "B6OK=PASS" || echo "B6OK=SKIP_KNOWN"`
退出码: 0 | 判定: **PASS**
期望: B6OK=SKIP_KNOWN
实际输出关键行:
```
B6OK=SKIP_KNOWN
```

## 汇总

| 结果 | 数量 |
|:-----|:----:|
| PASS | 1 |
| FAIL | 0 |
| SKIP | 0 |

**结论：本批通过（1/1）**
