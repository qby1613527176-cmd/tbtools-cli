# miRNA 靶标预测（mirnatarget, 引擎 55）真实数据验证（08/29 12:15）

## 真实数据
- miRNA: gras_mirnas_125.fa（125 个山茶/拟南芥/水稻 miRNA）
- 靶标: gras_cds.fa（GRAS 油茶 CDS，HiC_scaffold 参考）
- m10: gras_125_ssearch_out.txt（ssearch36 -n -i -m 10，976 sw_frame 行）

## 结果（本文件 = 408 命中）
- osa-miR171a → 多个 GRAS 基因（HiC_scaffold_14/12/15/1...），score 7.0, E=5.3e-06
- 互补序列验证正确（UGAUUGAGCCGCGCCAAUAUC ↔ GATATTGGCGCGGCTCAATCA）

## 完整管线
1. ssearch36 -w 100 -W 25 -E <e> -m 10 -T <t> -i -U <mirna.fa> <target.fa> → m10
2. tbtools mirnatarget <mirna.fa> <target.fa> <out.tsv>（内部自动两步）

## 坑
- ssearch36 必须 -i（reverse-complement）才有 sw_frame
- TargetSoEngine 必须 setCurAligner(Ssearch36)（默认 Fasta36 NPE）
- 需 ssearch36 在 PATH（apt install fasta 或本地编译）
