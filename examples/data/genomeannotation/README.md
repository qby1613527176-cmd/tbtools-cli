# BAM 状态评估（bamstate, 引擎 57）真实数据验证（08/29 12:15）

## 验证环境
- BAM: GRAS 油茶 RNA-seq bam_subset（SRR14934325/SRR14934322，参考 HiC_scaffold_*）
- GFF3: ARR-B arrb21_for_biomuse.gff3（21 基因，HiC_scaffold_* seqid 与 BAM 匹配）
- 阈值: --coverageThr 0.5 --depthThr 3.0

## 结果
- SRR14934325: coverage 0.01%, depth 0.01, 21 基因中 0 表达
- SRR14934322: coverage 0.01%, depth 0.01, 21 基因中 0 表达
（bam_subset 是特定区域子集，ARR-B 基因不在覆盖区——引擎功能验证，非表达结论）

## 坑
- GFF3 必须 9 列标准格式（feature 列 gene/mRNA/CDS）——MCScanX 简化 6 列格式会被 GXFReader 拒绝
- BAM 染色体名必须与 GFF3 seqid 匹配
- BAM 需先 samtools index
