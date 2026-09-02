# tbtools-cli 回归测试报告

> 时间: 2026-09-02 07:48:00 | 定义: batch07.def | 运行器 run_batch.sh 自动生成

### T701 — venn2 双集合韦恩
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/venn2.svg && timeout 90 java -Xmx2g -cp /mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn2 --List1 examples/data/set_0.txt --List2 examples/data/set_1.txt --label1 SetA --label2 SetB --graph /tmp/b7/venn2.svg --prefix /tmp/b7/v2 --bgNum 30000 >/dev/null 2>&1; [ -s /tmp/b7/venn2.svg ] && echo "B7OK=SVG_OK" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=SVG_OK
实际输出关键行:
```
B7OK=SVG_OK
```

### T702 — venn3 三集合韦恩
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/venn3.svg && timeout 90 java -Xmx2g -cp /mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn3 --List1 examples/data/set_0.txt --List2 examples/data/set_1.txt --List3 examples/data/set_2.txt --label1 A --label2 B --label3 C --graph /tmp/b7/venn3.svg --prefix /tmp/b7/v3 >/dev/null 2>&1; [ -s /tmp/b7/venn3.svg ] && echo "B7OK=SVG_OK" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=SVG_OK
实际输出关键行:
```
B7OK=SVG_OK
```

### T703 — venn4 四集合韦恩（Venn4Ellipse）
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/venn4.svg && timeout 90 java -Xmx2g -cp /mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.Venn4Ellipse --List1 examples/data/set_0.txt --List2 examples/data/set_1.txt --List3 examples/data/set_2.txt --List4 examples/data/set_3.txt --label1 A --label2 B --label3 C --label4 D --graph /tmp/b7/venn4.svg --prefix /tmp/b7/v4 >/dev/null 2>&1; [ -s /tmp/b7/venn4.svg ] && echo "B7OK=SVG_OK" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=SVG_OK
实际输出关键行:
```
B7OK=SVG_OK
```

### T704 — venn5 五集合韦恩
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/venn5.svg && timeout 120 bin/tbplot.sh venn5 /tmp/b7/venn5.svg examples/data/set_0.txt examples/data/set_1.txt examples/data/set_2.txt examples/data/set_3.txt examples/data/set_4.txt >/dev/null 2>&1; [ -s /tmp/b7/venn5.svg ] && echo "B7OK=SVG_OK" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=SVG_OK
实际输出关键行:
```
B7OK=SVG_OK
```

### T705 — venn6 六集合韦恩
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/venn6.svg && timeout 120 bin/tbplot.sh venn6 /tmp/b7/venn6.svg examples/data/set_0.txt examples/data/set_1.txt examples/data/set_2.txt examples/data/set_3.txt examples/data/set_4.txt test_reports/data_b7/set_5.txt >/dev/null 2>&1; [ -s /tmp/b7/venn6.svg ] && echo "B7OK=SVG_OK" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=SVG_OK
实际输出关键行:
```
B7OK=SVG_OK
```

### T706 — upset UpSet交集图
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/upset.svg && timeout 120 bin/tbplot.sh upset test_reports/data_b7/upset.sets.txt /tmp/b7/upset.svg >/dev/null 2>&1; [ -s /tmp/b7/upset.svg ] && echo "B7OK=SVG_OK" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=SVG_OK
实际输出关键行:
```
B7OK=SVG_OK
```

### T707 — peaktss Peak-TSS热图
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/peaktss.svg && timeout 120 bin/tbplot.sh peaktss test_reports/data_b7/genes_real.gff test_reports/data_b7/peak_real.xls /tmp/b7/peaktss.svg >/dev/null 2>&1; [ -s /tmp/b7/peaktss.svg ] && echo "B7OK=SVG_OK" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=SVG_OK
实际输出关键行:
```
B7OK=SVG_OK
```

### T708 — peakdist Peak染色体分布
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/peakdist.svg && timeout 120 bin/tbplot.sh peakdist examples/data/chipseq/chrlen2.txt examples/data/chipseq/peak_std.xls /tmp/b7/peakdist.svg >/dev/null 2>&1; [ -s /tmp/b7/peakdist.svg ] && echo "B7OK=SVG_OK" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=SVG_OK
实际输出关键行:
```
B7OK=SVG_OK
```

### T709 — peakanno Peak基因注释（真实尺度）
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/peakanno.tsv && timeout 120 bin/tbplot.sh peakanno test_reports/data_b7/genes_real.gff test_reports/data_b7/peak_real.xls /tmp/b7/peakanno.tsv >/dev/null 2>&1; [ -s /tmp/b7/peakanno.tsv ] && echo "B7OK=ANNO" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=ANNO
实际输出关键行:
```
B7OK=ANNO
```

### T710 — pileup BLAST pile-up
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/pileup.svg && timeout 120 bin/tbplot.sh pileup test_reports/data_b7/blast.xml /tmp/b7/pileup.svg >/dev/null 2>&1; [ -s /tmp/b7/pileup.svg ] && echo "B7OK=SVG_OK" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=SVG_OK
实际输出关键行:
```
B7OK=SVG_OK
```

### T711 — regiondepth SAM区域覆盖深度
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/rd.txt && timeout 120 bin/tbplot.sh regiondepth test_reports/data_b7/sample.sam Chr1:1000-2100 /tmp/b7/rd.txt >/dev/null 2>&1; [ -s /tmp/b7/rd.txt ] && echo "B7OK=RD" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=RD
实际输出关键行:
```
B7OK=RD
```

### T712 — bamsort BAM排序
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/sorted.bam && timeout 120 bin/tbplot.sh bamsort test_reports/data_b7/sample.bam /tmp/b7/sorted.bam coordinate /tmp >/dev/null 2>&1; [ -s /tmp/b7/sorted.bam ] && echo "B7OK=BAM" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=BAM
实际输出关键行:
```
B7OK=BAM
```

### T713 — bamindex BAM索引
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/sorted.bam.bai && timeout 120 bin/tbplot.sh bamindex /tmp/b7/sorted.bam /tmp/b7/sorted.bam.bai >/dev/null 2>&1; [ -s /tmp/b7/sorted.bam.bai ] && echo "B7OK=BAI" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=BAI
实际输出关键行:
```
B7OK=BAI
```

### T714 — bamstate BAM覆盖状态统计
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b7/bamstate.tsv && timeout 150 bin/tbplot.sh bamstate /tmp/b7/bamstate.tsv test_reports/data_b7/genes.gff test_reports/data_b7/sample_sorted.bam >/dev/null 2>&1; [ -s /tmp/b7/bamstate.tsv ] && echo "B7OK=STATE" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=STATE
实际输出关键行:
```
B7OK=STATE
```

## 汇总

| 结果 | 数量 |
|:-----|:----:|
| PASS | 15 |
| FAIL | 0 |
| SKIP | 0 |

**结论：本批通过（15/15）**
### T715 — bamMerge 区域覆盖合并BAM
命令: `cd /home/elysia/tbtools-cli && rm -rf /tmp/b7/bm_out && timeout 150 bin/tbplot.sh bamMerge test_reports/data_b7/genes_real.gff /tmp/b7/bamdir /tmp/b7/bm_out >/dev/null 2>&1; [ -s /tmp/b7/bm_out/merged_sorted.bam ] && echo "B7OK=MERGED" || echo "B7OK=0"`
退出码: 0 | 判定: **PASS**
期望: B7OK=MERGED
实际输出关键行:
```
B7OK=MERGED
```

## 汇总

| 结果 | 数量 |
|:-----|:----:|
| PASS | 1 |
| FAIL | 0 |
| SKIP | 0 |

**结论：本批通过（1/1）**
