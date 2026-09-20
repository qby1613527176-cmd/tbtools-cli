# 全功能测试数据集（examples/fulltest/data/）

一键生成（可重现）：
```bash
python3 examples/fulltest/generate_fulltest_data.py   # 输出到 examples/fulltest/data/
```

**设计原则**：内部完全自洽——CDS 可翻译回蛋白、GFF 坐标落在 genome 内、
reads 是转录本真实切片、同源对共享祖先序列（diamond 可 hit）、
promoter 含 motif 实例（fimo 有真命中）。所有数据由固定随机种子生成，
每次运行结果一致。

---

## 数据文件 → 命令映射

### 🔤 序列 / 结构（seq）
| 文件 | 内容 | 适用命令 |
|:--|:--|:--|
| `pep.fa` | 20 条蛋白（140aa，语法真实） | `tool statFasta`、`seq tfbsShift` |
| `cds.fa` | 对应 CDS（可翻译回 pep） | `tool cds2protein` |
| `genome.fa` | 3 scaffold DNA（承载 CDS） | `fastq fastaSubseq`、GFF 联动 |
| `promoter.fa` | 400bp 启动子 ×20（6 条含 motif 实例） | `seq fimo` |
| `sample.hmm` | HMMER 域模型（hmmbuild 生成） | `hmm hmmerSearch`、`hmm hmmExtract` |
| `hmmer_target.fa` | HMM 扫描靶标（含信号） | `hmm hmmerSearch` |
| `hmm_ids.txt` | Pfam ID 列表 | `hmm hmmerSearch` |

### 📊 表达 / 统计（expr）
| 文件 | 内容 | 适用命令 |
|:--|:--|:--|
| `expr.tsv` | 20 基因 × 6 样本（3+3 组） | `expr heatmap`、`expr pca`、`expr groupCol` |
| `sample_group.tsv` | 样本→分组 | `expr groupCol` |
| `deg.tsv` | DEG 表（log2FC+pvalue） | `expr volcano`、`expr dehist` |
| `counts.tsv` + `leninfo.tsv` | 定量输入 | `tool rpkmCal` |
| `qpcr.tab` | qPCR Ct 表 | `expr qpcr` |
| `dist.tsv` | 基因×样本矩阵 | `expr heatmap`、`expr distance`（矩阵） |
| `dist3.tsv` | 三列距离文件 | `expr hclust`（**注意：hclust 要三列**） |

### 🌳 树 / 进化（tree）
| 文件 | 内容 | 适用命令 |
|:--|:--|:--|
| `tree.nwk` | 通用小树 | `tree phylotree`、`tree unrooted`、`tree rooting` |
| `gene.nwk` | 基因树（叶子 `Species_G` 前缀） | `tree notung`、`tree treeRooting` |
| `species.nwk` | 物种树 | `tree notung` |
| `msa.fa` | 多序列比对 | `seq msa`、`seq seqlogo`（可 hmmbuild） |

### 🧬 共线性（syn）
| 文件 | 内容 | 适用命令 |
|:--|:--|:--|
| `genome1.fa` / `genome2.fa` | 染色体级 DNA（Chr1/Chr2 单染色体 ×18 基因） | `syn mcscanxd` |
| `genome1.gff` / `genome2.gff` | 对应 GFF（gene/mRNA/CDS 三层） | `syn mcscanxd`、`gxf gxfAttr` |
| `genome1.pep.fa` / `genome2.pep.fa` | 18 对同源蛋白 | `blast twoSeqBlast` |

### 🎯 GO / 富集（table）
| 文件 | 内容 | 适用命令 |
|:--|:--|:--|
| `go.obo` | mini GO 本体（MF/CC/BP + 3 子项） | `table goEnrich` |
| `gene2go.tsv` | 背景注释（G01-10 富集凋亡/激酶） | `table goEnrich` |
| `select_deg.txt` | 选择集（G01-05 全带 GO:0006915） | `table goEnrich`（**P=0.016 显著**） |
| `rank.rnk` | GSEA 预排序 | `table gsea` |
| `query2go.tsv` | 基因→GO | `table gsea` |

### 🔬 HMM / MEME / 插件
| 文件 | 内容 | 适用命令 |
|:--|:--|:--|
| `motifs.meme` | MEME 5.x motif 库（M1 ACGT） | `seq fimo`、`seq memeViz` |
| `transcripts.fa` + `reads_1.fq`/`reads_2.fq` | 转录本 + 双端 reads（真实切片） | `expr kallisto` |
| `set1..3.txt` | 韦恩 3 集合 | `sets venn2/3` |

### 🗂️ 表格 / 杂项
| 文件 | 内容 | 适用命令 |
|:--|:--|:--|
| `wide.tsv` | 宽表 | `table tableMelt` |
| `long.tsv` | 长表 | `table tableCast` |
| `idmap.tsv` | ID 重命名映射 | `tool gxfRename`/`newickRename` 参考 |
| `ids.txt` | ID 列表 | `fastq fastaExtract` |
| `anno.gff3` | GFF3（gene/mRNA/CDS） | `gxf gxfAttr`、GFF 系列 |
| `sample.fq` | FASTQ 样例 | `fastq fqfaConv` |

---

## 已验证链路（2026-09-20）

| 命令 | 结果 |
|:--|:--|
| `tool statFasta` | ✅ 20 条统计 |
| `gxf gxfAttr` | ✅ 20 mRNA 属性表 |
| `sets venn2` | ✅ 出图 |
| `expr hclust`（dist3.tsv） | ✅ 聚类树 |
| `tree phylotree` | ✅ SVG |
| `table goEnrich` | ✅ apoptotic process P=0.016 富集 |
| `hmm hmmerSearch` | ✅ 域命中（跨文件系统已修） |
| `expr kallisto` | ✅ abundance（双端） |
| `syn mcscanxd` | ✅ blast 1:1 + 全套产物（区块 0 与官方 comparative 数据一致，见下） |
| `tree notung` | ✅ reconcile + LOST 事件 |
| `seq fimo` | ✅ 237 命中 |

## ⚠️ 已知说明

- **mcscanxd 共线区块 = 0**：TBtools 自带 `examples/data/comparative` 在
  MCScanX 原版下同样 0 区块——微型合成基因组的正常行为（MCScanX 需要
  上万级真实基因密度）。本数据保证**全部上游环节正确**（diamond 1:1 命中、
  36 基因读入、3 染色体对比较、全套产物），适合验证"命令能否跑通"，
  不代表真实基因组级别结果。
- **notung**：reconcile 产物写当前工作目录（Notung 行为），叶子名必须
  `Species_G01` 物种前缀格式。
- **hclust**：输入必须是三列距离文件（`dist3.tsv`），表达矩阵会失败。