# tbtools-cli 回归测试报告

> 时间: 2026-09-02 06:24:59 | 定义: batch05.def | 运行器 run_batch.sh 自动生成

### T501 — tree TreeMeta多轨道树
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b5/tree.svg && bin/tbplot.sh tree test_reports/data_b5/tree.config /tmp/b5/tree.svg >/dev/null 2>&1; [ -s /tmp/b5/tree.svg ] && echo "B5OK=SVG_OK" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=SVG_OK
实际输出关键行:
```
B5OK=SVG_OK
```

### T502 — phylotree 系统发育树视图
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b5/phylo.svg && bin/tbplot.sh phylotree examples/data/phylogeny/phylo.nwk /tmp/b5/phylo.svg >/dev/null 2>&1; [ -s /tmp/b5/phylo.svg ] && echo "B5OK=SVG_OK" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=SVG_OK
实际输出关键行:
```
B5OK=SVG_OK
```

### T503 — unrooted 无根树可视化
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b5/unrooted.svg && bin/tbplot.sh unrooted examples/data/phylogeny/phylo.nwk /tmp/b5/unrooted.svg >/dev/null 2>&1; [ -s /tmp/b5/unrooted.svg ] && echo "B5OK=SVG_OK" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=SVG_OK
实际输出关键行:
```
B5OK=SVG_OK
```

### T504 — treeRooting MAD定根
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b5/rooted.nwk && bin/tbplot.sh treeRooting examples/data/treeRooting/unrooted.nwk /tmp/b5/rooted.nwk >/dev/null 2>&1; [ -s /tmp/b5/rooted.nwk ] && echo "B5OK=ROOTED" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=ROOTED
实际输出关键行:
```
B5OK=ROOTED
```

### T505 — msa MSA可视化
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b5/msa.svg && bin/tbplot.sh msa examples/data/phylogeny/msa.fa /tmp/b5/msa.svg >/dev/null 2>&1; [ -s /tmp/b5/msa.svg ] && echo "B5OK=SVG_OK" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=SVG_OK
实际输出关键行:
```
B5OK=SVG_OK
```

### T506 — nwAlign Needleman-Wunsch双序列比对
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b5/nw.out && bin/tbplot.sh nwAlign examples/data/align/nw.seq1.txt examples/data/align/nw.seq2.txt /tmp/b5/nw.out >/dev/null 2>&1; [ -s /tmp/b5/nw.out ] && echo "B5OK=NW" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=NW
实际输出关键行:
```
B5OK=NW
```

### T507 — hclust 三列距离聚类树
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b5/hc.nwk && bin/tbplot.sh hclust test_reports/data_b5/dist_real.tsv /tmp/b5/hc.nwk >/dev/null 2>&1; [ -s /tmp/b5/hc.nwk ] && echo "B5OK=HCLUST" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=HCLUST
实际输出关键行:
```
B5OK=HCLUST
```

### T508 — onesteptree 一步法ML树
命令: `cd /home/elysia/tbtools-cli && rm -rf /tmp/b5/ot && mkdir -p /tmp/b5/ot && timeout 280 bin/tbplot.sh onesteptree --inPepFie examples/data/rpc/gras6_pep.fa --outFilePrefix /tmp/b5/ot --bbTime 1000 >/dev/null 2>&1; [ -s /tmp/b5/ot/TBtools.IQtree.contree ] && echo "B5OK=MLTREE" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=MLTREE
实际输出关键行:
```
B5OK=MLTREE
```

### T509 — marker MarkerFilter 标记过滤
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b5/mf.out && bin/tbplot.sh marker MarkerFilter examples/data/marker/markers_0-1.tsv /tmp/b5/mf.out >/dev/null 2>&1; [ -s /tmp/b5/mf.out ] && echo "B5OK=MF" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=MF
实际输出关键行:
```
B5OK=MF
```

### T510 — marker MarkerDist 标记距离
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b5/md.out && bin/tbplot.sh marker MarkerDist examples/data/marker/markers_0-1.tsv /tmp/b5/md.out >/dev/null 2>&1; [ -s /tmp/b5/md.out ] && echo "B5OK=MD" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=MD
实际输出关键行:
```
B5OK=MD
```

### T511 — marker SampleDist 样本距离
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b5/sd.out && bin/tbplot.sh marker SampleDist examples/data/marker/markers_0-1.tsv /tmp/b5/sd.out >/dev/null 2>&1; [ -s /tmp/b5/sd.out ] && echo "B5OK=SD" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=SD
实际输出关键行:
```
B5OK=SD
```

### T512 — markertools filter 等位频率过滤
命令: `cd /home/elysia/tbtools-cli && out=$(bin/tbplot.sh markertools filter examples/data/marker/markers_0-1.tsv 2>&1); [ -n "$out" ] && echo "B5OK=MKF" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=MKF
实际输出关键行:
```
B5OK=MKF
```

### T513 — markertools dist 样本距离
命令: `cd /home/elysia/tbtools-cli && out=$(bin/tbplot.sh markertools dist examples/data/marker/markers_0-1.tsv 2>&1); [ -n "$out" ] && echo "B5OK=MKD" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=MKD
实际输出关键行:
```
B5OK=MKD
```

### T514 — markertools sampledist 群体距离
命令: `cd /home/elysia/tbtools-cli && out=$(bin/tbplot.sh markertools sampledist examples/data/marker/markers_0-1.tsv 2>&1); [ -n "$out" ] && echo "B5OK=MKS" || echo "B5OK=0"`
退出码: 0 | 判定: **PASS**
期望: B5OK=MKS
实际输出关键行:
```
B5OK=MKS
```

## 汇总

| 结果 | 数量 |
|:-----|:----:|
| PASS | 14 |
| FAIL | 0 |
| SKIP | 0 |

**结论：本批通过（14/14）**
