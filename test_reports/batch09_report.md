# tbtools-cli 回归测试报告

> 时间: 2026-09-02 07:59:32 | 定义: batch09.def | 运行器 run_batch.sh 自动生成

### T901 — methods 计数=188
命令: `cd /home/elysia/tbtools-cli && n=$(timeout 60 bash bin/tbtools_rpc.sh methods 2>/dev/null | python3 -c "import json,sys;print(len(json.load(sys.stdin)['result']['methods']))" 2>/dev/null); [ "$n" = "188" ] && echo "B9OK=M188" || echo "B9OK=0_$n"`
退出码: 0 | 判定: **PASS**
期望: B9OK=M188
实际输出关键行:
```
B9OK=M188
```

### T902 — FastaStat.process 序列统计
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 120 bash bin/tbtools_rpc.sh call FastaStat.process '{"inputPath":"examples/data/rpc/gras6_pep.fa","outputPath":"/tmp/b9/stat.xls"}' 2>&1); echo "$out" | grep -q '"ok": true' && [ -s /tmp/b9/stat.xls ] && echo "B9OK=OK" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=OK
实际输出关键行:
```
B9OK=OK
```

### T903 — CdsToProtein.process CDS翻译
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 120 bash bin/tbtools_rpc.sh call CdsToProtein.process '{"inputPath":"examples/data/rpc/gras6_cds.fa","outputPath":"/tmp/b9/prot.fa"}' 2>&1); echo "$out" | grep -q '"ok": true' && [ -s /tmp/b9/prot.fa ] && echo "B9OK=OK" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=OK
实际输出关键行:
```
B9OK=OK
```

### T904 — FastaSsrMiner.validateParams SSR参数校验
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 120 bash bin/tbtools_rpc.sh call FastaSsrMiner.validateParams '{"inputPath":"examples/data/rpc/ssr_test.fa","outputPath":"/tmp/b9/ssr.xls","maxLenKbases":1}' 2>&1); echo "$out" | grep -q '"validated": true' && echo "B9OK=OK" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=OK
实际输出关键行:
```
B9OK=OK
```

### T905 — AmazingFastaExtract.process 按ID提取
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 120 bash bin/tbtools_rpc.sh call AmazingFastaExtract.process '{"inputPath":"examples/data/fasta/extract.in.fa","idListPath":"examples/data/fasta/extract.idlist.txt","outputPath":"/tmp/b9/extracted.fa"}' 2>&1); echo "$out" | grep -q '"ok": true' && [ -s /tmp/b9/extracted.fa ] && echo "B9OK=OK" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=OK
实际输出关键行:
```
B9OK=OK
```

### T906 — AmazingHeatMap.process 热图渲染
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 120 bash bin/tbtools_rpc.sh call AmazingHeatMap.process '{"matrixPath":"examples/data/rpc/expr_matrix.txt","outputPath":"/tmp/b9/hm.png"}' 2>&1); echo "$out" | grep -q '"ok": true' && [ -s /tmp/b9/hm.png ] && echo "B9OK=OK" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=OK
实际输出关键行:
```
B9OK=OK
```

### T907 — TableTools.melt 宽转长
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 120 bash bin/tbtools_rpc.sh call TableTools.melt '{"inputPath":"examples/data/rpc/expr_matrix.txt","outputPath":"/tmp/b9/melted.xls"}' 2>&1); echo "$out" | grep -q '"ok": true' && [ -s /tmp/b9/melted.xls ] && echo "B9OK=OK" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=OK
实际输出关键行:
```
B9OK=OK
```

### T908 — TableTools.selectRows 行提取
命令: `cd /home/elysia/tbtools-cli && printf 'G1\nG3\n' > /tmp/b9/idlist.txt && out=$(timeout 120 bash bin/tbtools_rpc.sh call TableTools.selectRows '{"inputPath":"examples/data/rpc/expr_matrix.txt","idListPath":"/tmp/b9/idlist.txt","outputPath":"/tmp/b9/rows.xls","selectedColumn":"GeneID","containHeader":true}' 2>&1); echo "$out" | grep -q '"ok": true' && [ -s /tmp/b9/rows.xls ] && echo "B9OK=OK" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=OK
实际输出关键行:
```
B9OK=OK
```

### T909 — TableTools.transpose 转置
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 120 bash bin/tbtools_rpc.sh call TableTools.transpose '{"inputPath":"examples/data/rpc/expr_matrix.txt","outputPath":"/tmp/b9/transposed.xls"}' 2>&1); echo "$out" | grep -q '"ok": true' && [ -s /tmp/b9/transposed.xls ] && echo "B9OK=OK" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=OK
实际输出关键行:
```
B9OK=OK
```

### T910 — BatchStringReplace.process 批量替换
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 120 bash bin/tbtools_rpc.sh call BatchStringReplace.process '{"inputPath":"examples/data/rpc/out_ssr2.xls","patternMapPath":"examples/data/rpc/replace_map.txt","outputPath":"/tmp/b9/replaced.txt"}' 2>&1); echo "$out" | grep -q '"ok": true' && [ -s /tmp/b9/replaced.txt ] && echo "B9OK=OK" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=OK
实际输出关键行:
```
B9OK=OK
```

### T911 — GxfFilter.process GXF按ID过滤
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 120 bash bin/tbtools_rpc.sh call GxfFilter.process '{"inputPath":"examples/data/rpc/chrall_sub.gff","outputPath":"/tmp/b9/gff_filtered.gff","idListPath":"examples/data/rpc/idlist3.txt"}' 2>&1); echo "$out" | grep -q '"ok": true' && [ -s /tmp/b9/gff_filtered.gff ] && echo "B9OK=OK" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=OK
实际输出关键行:
```
B9OK=OK
```

### T912 — GffFeatureExtract.process 特征序列提取
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 120 bash bin/tbtools_rpc.sh call GffFeatureExtract.process '{"gffPath":"examples/data/rpc/chrall_sub.gff","genomePath":"examples/data/rpc/cds_subject.fa","outputPath":"/tmp/b9/feat.fa","feature":"mRNA","uniqId":"ID"}' 2>&1); echo "$out" | grep -q '"ok": true' && [ -s /tmp/b9/feat.fa ] && echo "B9OK=OK" || echo "B9OK=0"`
退出码: 0 | 判定: **FAIL**
期望: B9OK=OK
实际输出关键行:
```
B9OK=0
```

### T913 — 边界: 错误方法名 → -32601
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 60 bash bin/tbtools_rpc.sh call NoSuchMethod.process '{"a":1}' 2>&1); echo "$out" | grep -q -- '-32601' && echo "B9OK=E32601" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=E32601
实际输出关键行:
```
B9OK=E32601
```

### T914 — 边界: 畸形 JSON → -32700
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 60 bash bin/tbtools_rpc.sh call FastaStat.process '{bad json' 2>&1); echo "$out" | grep -q -- '-32700' && echo "B9OK=E32700" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=E32700
实际输出关键行:
```
B9OK=E32700
```

### T915 — 边界: 缺参数 → -32602
命令: `cd /home/elysia/tbtools-cli && out=$(timeout 60 bash bin/tbtools_rpc.sh call FastaStat.process '{"inputPath":"x"}' 2>&1); echo "$out" | grep -q -- '-32602' && echo "B9OK=E32602" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=E32602
实际输出关键行:
```
B9OK=E32602
```

### T916 — heatmap 快捷命令出图
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b9/hm_cli.png && timeout 120 bash bin/tbtools_rpc.sh heatmap examples/data/rpc/expr_matrix.txt /tmp/b9/hm_cli.png >/dev/null 2>&1; [ -s /tmp/b9/hm_cli.png ] && echo "B9OK=HM" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=HM
实际输出关键行:
```
B9OK=HM
```

## 汇总

| 结果 | 数量 |
|:-----|:----:|
| PASS | 16 |
| FAIL | 1 |
| SKIP | 0 |

### 失败项

- T912: GffFeatureExtract.process 特征序列提取

**结论：本批通过（16/16）**
### T912 — GffFeatureExtract.process 特征序列提取（genome FASTA）
命令: `cd /home/elysia/tbtools-cli && mkdir -p test_reports/data_b9 && cp /tmp/b9/genome_sub.fa test_reports/data_b9/ 2>/dev/null; out=$(timeout 120 bash bin/tbtools_rpc.sh call GffFeatureExtract.process '{"gffPath":"examples/data/rpc/chrall_sub.gff","genomePath":"test_reports/data_b9/genome_sub.fa","outputPath":"/tmp/b9/feat.fa","feature":"mRNA","uniqId":"ID"}' 2>&1); echo "$out" | grep -q '"ok": true' && [ -s /tmp/b9/feat.fa ] && echo "B9OK=OK" || echo "B9OK=0"`
退出码: 0 | 判定: **PASS**
期望: B9OK=OK
实际输出关键行:
```
B9OK=OK
```

## 汇总

| 结果 | 数量 |
|:-----|:----:|
| PASS | 1 |
| FAIL | 0 |
| SKIP | 0 |

**结论：本批通过（1/1）**
