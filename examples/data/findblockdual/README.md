# FindBlockDual 真实数据验证（08/29 11:00）

## 验证环境
- query: Cr（山茶, CCRA）genome + gff（37390 mRNA, Chr01-XX + Contigs）
- subject: Cs（茶树, GWHASIV）genome + gff（45901 mRNA）
- queryId: evm.model.Chr06.1064（Chr06 中部基因，避开引擎首个基因 get(-1) 边界 bug）
- 参数: --leftEdge 10 --rightEdge 10 --expand 15 --threads 8
- BLAST: 本地 blastp/makeblastdb 2.16（TBtools 自动调用系统 PATH）

## 结果
检测到真实跨物种同源共线区块：
- query 区块: Cr Chr06:39758881-41727711（~1.2Mb, 21 基因, evm.model.Chr06.1049-1084）
- subject 区块: Cs GWHASIV00000001:12139947-13129910（~1Mb, 24 基因, TGY000527-579）
- 锚点: evm.model.Chr06.1064 的 blast 同源命中 TGY000538/540/557/562/563 等

## 坑（重要）
1. **queryId 不能选 GFF 第一个 mRNA**：hitIdIndex=0 时左扩循环 get(-1) IndexOutOfBounds 崩溃（真实数据才暴露）
2. **/tmp 是 tmpfs（16G 内存盘）**：双 3GB 基因组 init 残留 tmpWk 目录撑爆 → 必须 `-Djava.io.tmpdir=<磁盘路径>`（本验证用磁盘路径）
3. 基因组必须已解压且 fasta 头与 GFF seqid 匹配
