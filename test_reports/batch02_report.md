# tbtools-cli 回归测试报告

> 时间: 2026-09-01 13:33:11 | 定义: batch02.def | 运行器 run_batch.sh 自动生成

### T201 — fastaExtract 按ID提取
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/ex.fa && bin/tbplot.sh fastaExtract examples/data/fasta/extract.in.fa examples/data/fasta/extract.idlist.txt /tmp/b2/ex.fa >/dev/null 2>&1; echo "B2OK=$(grep -c '^>' /tmp/b2/ex.fa 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=2
实际输出关键行:
```
B2OK=2
```

### T202 — fastaSubseq 坐标提序列
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/sub.fa && bin/tbplot.sh fastaSubseq examples/data/fasta/subseq.in.fa examples/data/fasta/subseq.pos.txt /tmp/b2/sub.fa >/dev/null 2>&1; echo "B2OK=$(grep -c '^>' /tmp/b2/sub.fa 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=2
实际输出关键行:
```
B2OK=2
```

### T203 — gfa2fa GFA转FASTA
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/gfa.fa && bin/tbplot.sh gfa2fa examples/data/fasta/sample.gfa /tmp/b2/gfa.fa >/dev/null 2>&1; echo "B2OK=$(grep -c '^>' /tmp/b2/gfa.fa 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=2
实际输出关键行:
```
B2OK=2
```

### T204 — fqfaConv FASTQ转FASTA
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/fq.fa && bin/tbplot.sh fqfaConv examples/data/fastq/convert.in.fq /tmp/b2/fq.fa fq2fa >/dev/null 2>&1; echo "B2OK=$(grep -c '^>' /tmp/b2/fq.fa 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=2
实际输出关键行:
```
B2OK=2
```

### T205 — fqTrim 双端修剪
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/trim.fq && bin/tbplot.sh fqTrim examples/data/fastq/reads.fq /tmp/b2/trim.fq >/dev/null 2>&1; echo "B2OK=$(grep -c '^@' /tmp/b2/trim.fq 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=4
实际输出关键行:
```
B2OK=4
```

### T206 — hmmExtract HMM按NAME提取
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/hmm.hmm && bin/tbplot.sh hmmExtract examples/data/hmm/sample.hmm examples/data/hmm/ids.txt /tmp/b2/hmm.hmm >/dev/null 2>&1; echo "B2OK=$(grep -c '^NAME' /tmp/b2/hmm.hmm 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=1
实际输出关键行:
```
B2OK=1
```

### T207 — mast2tab MEME XML转表格
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/mast.tab && bin/tbplot.sh mast2tab examples/data/meme/sample.mast.xml /tmp/b2/mast.tab >/dev/null 2>&1; echo "B2OK=$(wc -l < /tmp/b2/mast.tab 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=4
```

### T208 — mastExtract MAST命中提序列
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/mastex.txt && bin/tbplot.sh mastExtract examples/data/meme/mast.in.fa examples/data/meme/sample.mast.xml /tmp/b2/mastex.txt >/dev/null 2>&1; echo "B2OK=$(wc -l < /tmp/b2/mastex.txt 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=3
```

### T209 — mggxf GenePair转LinkedRegion
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/lr.txt && bin/tbplot.sh mggxf test_reports/data_b2/genePair.tsv test_reports/data_b2/sim.gff /tmp/b2/lr.txt GenePair >/dev/null 2>&1; echo "B2OK=$(wc -l < /tmp/b2/lr.txt 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=2
```

### T210 — pep2codon 蛋白比对回译密码子
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/codon.fa && bin/tbplot.sh pep2codon test_reports/data_b2/cds.fa test_reports/data_b2/pep.aln.fa /tmp/b2/codon.fa >/dev/null 2>&1; echo "B2OK=$(wc -l < /tmp/b2/codon.fa 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=4
```

### T211 — seqconvert FASTA转Phylip
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/out.phy && bin/tbplot.sh seqconvert -i test_reports/data_b2/seq_in.fa -o /tmp/b2/out.phy -iF fasta -oF phylip >/dev/null 2>&1; echo "B2OK=$(grep -c 'seq1' /tmp/b2/out.phy 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=1
```

### T212 — nwAlign NW全局比对
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/nw.out && bin/tbplot.sh nwAlign examples/data/align/nw.seq1.txt examples/data/align/nw.seq2.txt /tmp/b2/nw.out >/dev/null 2>&1; echo "B2OK=$(wc -l < /tmp/b2/nw.out 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=16
```

### T213 — gsadiag 基因结构诊断
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/diag.xls && bin/tbplot.sh gsadiag examples/data/gxf/input.gff3 /tmp/b2/diag.xls >/dev/null 2>&1; [ -s /tmp/b2/diag.xls ] && echo "B2OK=FILE_OK" || echo "B2OK=0"`
退出码: 0 | 判定: **PASS**
期望: B2OK=FILE_OK
实际输出关键行:
```
B2OK=FILE_OK
```

### T214 — gxfsort GFF排序
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/sorted.gff3 && bin/tbplot.sh gxfsort examples/data/gxf/input.gff3 /tmp/b2/sorted.gff3 >/dev/null 2>&1; echo "B2OK=$(grep -c '^chr' /tmp/b2/sorted.gff3 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=5
```

### T215 — gxffilter GFF按ID过滤
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/filtered.gff3 && printf 'gene1\ngene3\n' > /tmp/b2/ids.txt && bin/tbplot.sh gxffilter examples/data/gxf/input.gff3 /tmp/b2/ids.txt /tmp/b2/filtered.gff3 >/dev/null 2>&1; echo "B2OK=$(grep -c '^chr' /tmp/b2/filtered.gff3 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=2
```

### T216 — gxfRename GFF重命名
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/renamed.gff3 && bin/tbplot.sh gxfRename examples/data/gxf/input.gff3 /tmp/b2/renamed.gff3 examples/data/gxf/rename.map.tsv >/dev/null 2>&1; echo "B2OK=$(grep -c 'AT1G' /tmp/b2/renamed.gff3 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=5
```

### T217 — gxfStat GFF统计
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/stat.xls && bin/tbplot.sh gxfStat examples/data/gxf/input.gff3 /tmp/b2/stat.xls >/dev/null 2>&1; [ -s /tmp/b2/stat.xls ] && echo "B2OK=FILE_OK" || echo "B2OK=0"`
退出码: 0 | 判定: **PASS**
期望: B2OK=FILE_OK
实际输出关键行:
```
B2OK=FILE_OK
```

### T218 — gxfAppend GFF加前缀
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/app.gff3 && bin/tbplot.sh gxfAppend examples/data/gxf/input.gff3 /tmp/b2/app.gff3 XX_ >/dev/null 2>&1; echo "B2OK=$(grep -c 'XX_' /tmp/b2/app.gff3 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=5
```

### T219 — gxfGenepos 基因位置+染色体长度
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/gp.txt /tmp/b2/cl.txt && bin/tbplot.sh gxfGenepos examples/data/gxf/input.gff3 /tmp/b2/gp.txt /tmp/b2/cl.txt >/dev/null 2>&1; echo "B2OK=$(wc -l < /tmp/b2/gp.txt 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=2
```

### T220 — gxfRegion 区域保留
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/region.gff3 && bin/tbplot.sh gxfRegion examples/data/gxf/input.gff3 test_reports/data_b2/region.txt /tmp/b2/region.gff3 >/dev/null 2>&1; echo "B2OK=$(grep -c '^chr' /tmp/b2/region.gff3 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=3
```

### T221 — gxfOverlap 区域重叠过滤
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/overlap.gff3 && bin/tbplot.sh gxfOverlap examples/data/gxf/input.gff3 test_reports/data_b2/overlap_region.txt /tmp/b2/overlap.gff3 >/dev/null 2>&1; echo "B2OK=$(grep -c '^chr' /tmp/b2/overlap.gff3 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=3
```

### T222 — gxfRepIDs 代表转录本映射
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/repid2.txt && bin/tbplot.sh gxfRepIDs examples/data/gxf/gxfutils/repgxf/cs_rep.out.gff3 /tmp/b2/repid2.txt >/dev/null 2>&1; echo "B2OK=$(wc -l < /tmp/b2/repid2.txt 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=33
```

### T223 — gxfRepGXF 代表转录本提取
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/repgxf.gff3 && bin/tbplot.sh gxfRepGXF examples/data/gxf/gxfutils/repgxf/cs_head600.gff3 /tmp/b2/repgxf.gff3 >/dev/null 2>&1; echo "B2OK=$(grep -c '^GWH' /tmp/b2/repgxf.gff3 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=534
```

### T224 — gxfMatch GFF与基因组匹配检查
命令: `cd /home/elysia/tbtools-cli && bin/tbplot.sh gxfMatch examples/data/gxf/input.gff3 test_reports/data_b2/genome.fa > /tmp/b2/match.log 2>&1; echo "B2OK=$(grep -ci 'matched' /tmp/b2/match.log 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=1
```

### T225 — gxfRecall 恢复mRNA特征
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/recall.gff3 && bin/tbplot.sh gxfRecall examples/data/gxf/input.gff3 /tmp/b2/recall.gff3 >/dev/null 2>&1; echo "B2OK=$(grep -c '^chr' /tmp/b2/recall.gff3 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=5
```

### T226 — regionAnno 区域注释
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/anno.tsv && bin/tbplot.sh regionAnno examples/data/gxf/input.gff3 test_reports/data_b2/anno_region.txt /tmp/b2/anno.tsv >/dev/null 2>&1; [ -s /tmp/b2/anno.tsv ] && echo "B2OK=FILE_OK" || echo "B2OK=0"`
退出码: 0 | 判定: **PASS**
期望: B2OK=FILE_OK
实际输出关键行:
```
B2OK=FILE_OK
```

### T227 — gxfFix GFF修复
命令: `cd /home/elysia/tbtools-cli && rm -f /tmp/b2/fixed.gff3 && bin/tbplot.sh gxfFix examples/data/gxf/fix.input.gff3 /tmp/b2/fixed.gff3 >/dev/null 2>&1; echo "B2OK=$(grep -c '^chr' /tmp/b2/fixed.gff3 2>/dev/null)"`
退出码: 0 | 判定: **PASS**
期望: B2OK=[1-9]
实际输出关键行:
```
B2OK=4
```

## 汇总

| 结果 | 数量 |
|:-----|:----:|
| PASS | 27 |
| FAIL | 0 |
| SKIP | 0 |

**结论：本批通过（27/27）**
