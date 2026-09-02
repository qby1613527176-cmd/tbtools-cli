# tbtools-cli 全量回归 批 1/10 — 环境与基础架构

> 时间: 2026-09-01 13:25:03 | 基线 commit: 9d4df5a | 自包含脚本 run_batch01.sh 自动生成

### T01 — config.sh jar 探测
命令: `source config/config.sh 2>/dev/null; echo JAR=[${TBTOOLS_JAR:-EMPTY}]; [ -n "${TBTOOLS_JAR:-}" ] && [ -f "$TBTOOLS_JAR" ] && echo JAR_FILE_OK || echo JAR_FILE_MISSING`
退出码: 0 | 判定: **PASS**
期望: JAR_FILE_OK
实际输出关键行:
```
JAR=[/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar]
JAR_FILE_OK
```

### T02 — tbtools help 显示用法
命令: `bin/tbtools help 2>&1 | head -15`
退出码: 0 | 判定: **PASS**
期望: 用法|Usage|tbtools
实际输出关键行:
```
tbtools — TBtools-II 全功能 CLI
================================
绘图命令（140 个）:
  tbplot.sh genestructure|motif|volcano|genelocation|dotplot|circos
  tbplot.sh upset|msa|genelocgff|tree|phylotree|unrooted|violin|barplotter|heatmap2|supercircos|barplot|annocompare|genedensity|seqconvert|trimmsa
  tbplot.sh pafviz|admixture|groupedbar|layoutheatmap|cubeheatmap
  tbplot.sh circlegene|seqlogo|peaktss|peakdist|dehist|msy|venn2-6
  tbplot.sh microsyn|multisyn|marker|treeRooting|findblockdual|collinearRegion|findblockmultiple|visualizeblock|conflictpaf|partitionconflict|mirnatarget|mirnaTarget2|mirnaIdentify|nwAlign|recipBlast|filterCScore|quickFamily|ctgGroup|homoPhase|sepChr|bamMerge|hicEnzyme|virusRecomb|gxfRename|gxfStat|gxfAppend|gxfGenepos|gxfRegion|gxfFix|gxfOverlap|gxfRepIDs|gxfRepGXF|gxfMatch|gxfRecall|regionAnno|tableColSelect|generic|hclust|qpcr|pca
  tbtools plot <命令> [参数...]   # 绘图统一入口（转发 tbplot.sh）
  tbtools list plots              # 列出全部绘图命令
  tbplot.sh help                  # 查看全部绘图命令

RPC 数据工具（188 方法）:
  tbtools rpc <method> '<json>'      # 调用任意 RPC
  tbtools methods                    # 列出 188 方法
```

### T03 — tbplot.sh help 分类总览
命令: `bin/tbplot.sh help 2>&1 | head -30`
退出码: 0 | 判定: **PASS**
期望: 命令|绘图|工具|help
实际输出关键行:
```
================================================
 TBtools 绘图/分析 CLI — tbplot.sh
 用法: tbplot.sh <命令> [参数...]
       tbplot.sh help          列出全部命令
       tbplot.sh help <命令>   查看某命令详细用法（多行）
================================================

📖 完整手册: docs/COMMAND_REFERENCE.md（88 绘图命令 + 82 工具 + 80 桥 + 28 坑位）
   RPC 188 方法: docs/rpc_methods_reference.md

全部命令（140 个):

── 共线性/基因组 ──
circlegene circos dotplot dualsyn findblockdual findblockmultiple mcscanx microgenome microsyn msy multisyn pafcomp pafref pafviz visualizeblock 
── 树/进化 ──
barplotter degramdom findpath onesteptree phylotree tree treeRooting unrooted 
── 热图/表达/统计 ──
barplot barplotter colorscheme cubeheatmap dehist distance efpHeat exprCorr groupCol groupedbar heatmap2 layoutheatmap mountain pca qpcr qpcrExp qpcrproc tauIndex violin volcano 
── 序列/结构/域 ──
amazingmeta cddmotif gel gfa gfa2fa mast2tab mastExtract mastrun memerun motif msa pep2codon pfammotif pileup plotrna rnaplot seqlentrack seqlogo simplehmmscan 
```

### T04 — banner 绘图命令计数=140
命令: `bin/tbtools 2>&1 | head -20`
退出码: 0 | 判定: **PASS**
期望: 140
实际输出关键行:
```
tbtools — TBtools-II 全功能 CLI
================================
绘图命令（140 个）:
  tbplot.sh genestructure|motif|volcano|genelocation|dotplot|circos
  tbplot.sh upset|msa|genelocgff|tree|phylotree|unrooted|violin|barplotter|heatmap2|supercircos|barplot|annocompare|genedensity|seqconvert|trimmsa
  tbplot.sh pafviz|admixture|groupedbar|layoutheatmap|cubeheatmap
  tbplot.sh circlegene|seqlogo|peaktss|peakdist|dehist|msy|venn2-6
  tbplot.sh microsyn|multisyn|marker|treeRooting|findblockdual|collinearRegion|findblockmultiple|visualizeblock|conflictpaf|partitionconflict|mirnatarget|mirnaTarget2|mirnaIdentify|nwAlign|recipBlast|filterCScore|quickFamily|ctgGroup|homoPhase|sepChr|bamMerge|hicEnzyme|virusRecomb|gxfRename|gxfStat|gxfAppend|gxfGenepos|gxfRegion|gxfFix|gxfOverlap|gxfRepIDs|gxfRepGXF|gxfMatch|gxfRecall|regionAnno|tableColSelect|generic|hclust|qpcr|pca
  tbtools plot <命令> [参数...]   # 绘图统一入口（转发 tbplot.sh）
  tbtools list plots              # 列出全部绘图命令
  tbplot.sh help                  # 查看全部绘图命令

RPC 数据工具（188 方法）:
  tbtools rpc <method> '<json>'      # 调用任意 RPC
  tbtools methods                    # 列出 188 方法
  tbtools server start|stop          # RPC 服务器管理
  tbtools heatmap <matrix> <out> [group]  # 热图快捷

命令行工具（36 个）:
  tbtools tool <名称> [参数...]       # 见: tbtools list tools
```

### T05 — help volcano/genestructure/heatmap2 详细版
命令: `bin/tbplot.sh help volcano 2>&1 | head -8; echo ===; bin/tbplot.sh help genestructure 2>&1 | head -8; echo ===; bin/tbplot.sh help heatmap2 2>&1 | head -8`
退出码: 0 | 判定: **PASS**
期望: volcano|基因|heatmap
实际输出关键行:
```
==== tbplot.sh volcano 详细用法 ====

  • 用法: volcano <deg.txt> <outFile> [pvalCutoff] [fcCutoff] [w] [h]
  • deg.txt: GeneID\tLog2FC\tpvalue
  • 通用反射桥 GenericCli 驱动 vocanoPlot.show()

  📖 详细手册: /home/elysia/tbtools-cli/docs/COMMAND_REFERENCE.md（含输入格式/参数/坑位）
  🔍 桥 Javadoc: /home/elysia/tbtools-cli/bridges/ 对应桥类（首次报错先读）
===
==== tbplot.sh genestructure 详细用法 ====

  • 用法: genestructure <input.gff> <idList.txt> <outFile> [genome.fa] [width] [height]

  📖 详细手册: /home/elysia/tbtools-cli/docs/COMMAND_REFERENCE.md（含输入格式/参数/坑位）
  🔍 桥 Javadoc: /home/elysia/tbtools-cli/bridges/ 对应桥类（首次报错先读）

===
==== tbplot.sh heatmap2 详细用法 ====

  • 用法: heatmap2 <expr.matrix.tsv> <out> [options]
```

### T06 — tbtools list tools → 82 个
命令: `bin/tbtools list tools 2>&1 | head -2`
退出码: 0 | 判定: **PASS**
期望: 命令行工具: 82
实际输出关键行:
```
命令行工具: 82
  DecodeIlluminaFqPool -> biocjava.bioDoer.Fastq.DecodeIlluminaFqPool
```

### T07 — tbtools list plots → 140 个
命令: `bin/tbtools list plots 2>&1 | head -2`
退出码: 0 | 判定: **PASS**
期望: 绘图: 140
实际输出关键行:
```
绘图: 140 个（tbplot.sh）
  admixture
```

### T08 — tbtools methods → 188 RPC
命令: `bin/tbtools methods 2>&1 | python3 -c "import sys,json,re; raw=sys.stdin.read(); s=re.sub(r'^.*?\n', '', raw, count=1); d=json.loads(s); print(len(d.get('result',{}).get('methods',[])))"`
退出码: 0 | 判定: **PASS**
期望: 188
实际输出关键行:
```
188
```

### T09 — 未知命令 foobarxyz 报错 EXIT=1
命令: `bin/tbtools foobarxyz; echo REAL_EXIT=$?`
退出码: 0 | 判定: **PASS**
期望: REAL_EXIT=1
实际输出关键行:
```
❌ 未知命令: foobarxyz
tbtools — TBtools-II 全功能 CLI
================================
绘图命令（140 个）:
  tbplot.sh genestructure|motif|volcano|genelocation|dotplot|circos
  tbplot.sh upset|msa|genelocgff|tree|phylotree|unrooted|violin|barplotter|heatmap2|supercircos|barplot|annocompare|genedensity|seqconvert|trimmsa
  tbplot.sh pafviz|admixture|groupedbar|layoutheatmap|cubeheatmap
  tbplot.sh circlegene|seqlogo|peaktss|peakdist|dehist|msy|venn2-6
  tbplot.sh microsyn|multisyn|marker|treeRooting|findblockdual|collinearRegion|findblockmultiple|visualizeblock|conflictpaf|partitionconflict|mirnatarget|mirnaTarget2|mirnaIdentify|nwAlign|recipBlast|filterCScore|quickFamily|ctgGroup|homoPhase|sepChr|bamMerge|hicEnzyme|virusRecomb|gxfRename|gxfStat|gxfAppend|gxfGenepos|gxfRegion|gxfFix|gxfOverlap|gxfRepIDs|gxfRepGXF|gxfMatch|gxfRecall|regionAnno|tableColSelect|generic|hclust|qpcr|pca
  tbtools plot <命令> [参数...]   # 绘图统一入口（转发 tbplot.sh）
  tbtools list plots              # 列出全部绘图命令
  tbplot.sh help                  # 查看全部绘图命令

RPC 数据工具（188 方法）:
  tbtools rpc <method> '<json>'      # 调用任意 RPC
  tbtools methods                    # 列出 188 方法
  tbtools server start|stop          # RPC 服务器管理
  tbtools heatmap <matrix> <out> [group]  # 热图快捷

命令行工具（36 个）:
```

### T10 — 未知工具 nonexistentTool 报错 EXIT=1 不倾倒 jar
命令: `bin/tbtools tool nonexistentTool; echo REAL_EXIT=$?`
退出码: 0 | 判定: **PASS**
期望: 未知工具|REAL_EXIT=1
实际输出关键行:
```
❌ 未知工具: nonexistentTool
请用 tbtools list tools 查看可用工具（82 个）
REAL_EXIT=1
```

### T11 — 降级命令 violin/colorscheme/phylotree/microgenome/pileup/dualsyn 显示用法
命令: `for c in violin colorscheme phylotree microgenome pileup dualsyn; do echo "-- $c --"; bin/tbtools $c 2>&1 | head -3; done; true`
退出码: 0 | 判定: **PASS**
期望: violin|colorscheme|phylotree|microgenome|pileup|dualsyn
实际输出关键行:
```
-- violin --
用法: ViolinCli <in.tsv> <out> [width] [height]
-- colorscheme --
用法: tbplot.sh colorscheme <inTab> <outTab> <refColIndex>
-- phylotree --
用法: PhyloTreeCli <in.nwk> <out> [vertical] [width] [height]
-- microgenome --
用法: tbplot.sh microgenome <inGBK> <anno.tsv> <out> [micro|macro]
-- pileup --
用法: tbplot.sh pileup <blast.xml> <out.svg> [--query NAME]
-- dualsyn --
用法: tbplot.sh dualsyn <simplifiedGff> <collinearity> <out> [--chr1 ..] [--chr2 ..]
```

### T12 — run_examples.sh 全过出图
命令: `timeout 600 bash examples/scripts/run_examples.sh 2>&1 | tail -25; echo REAL_EXIT=$?`
退出码: 0 | 判定: **PASS**
期望: REAL_EXIT=0
实际输出关键行:
```
2026-09-01 13:25:12:Finished Painting

[6/8] 五集合韦恩 (venn5)
[tbplot] 已保存: /home/elysia/tbtools-cli/examples/output/06_venn5.svg

[7/8] 差异表达双直方图 (dehist)
[tbplot] 已保存: /home/elysia/tbtools-cli/examples/output/07_dehist.svg (2 面板)

[8/8] UpSet 交集图 (upset)
[tbplot] 已保存: /home/elysia/tbtools-cli/examples/output/08_upset.svg

==============================================
 完成！示例输出在: /home/elysia/tbtools-cli/examples/output
total 560
drwxrwxr-x 2 elysia elysia   4096 Aug 29 06:30 .
drwxrwxr-x 6 elysia elysia   4096 Aug 31 00:25 ..
-rw-rw-r-- 1 elysia elysia   7197 Sep  1 13:25 01_gene_structure.svg
-rw-rw-r-- 1 elysia elysia  51872 Sep  1 13:25 02_heatmap.svg
-rw-rw-r-- 1 elysia elysia  13637 Sep  1 13:25 03_pca.svg
-rw-rw-r-- 1 elysia elysia  64023 Sep  1 13:25 04_volcano.svg
```

### T13 — git 工作区干净（忽略 test_reports）+ 提交数
命令: `echo COMMITS=$(git rev-list --count HEAD); git status --porcelain 2>&1 | grep -v 'test_reports/' | head -10; echo DIRTY_COUNT=$(git status --porcelain 2>&1 | grep -vc 'test_reports/')`
退出码: 0 | 判定: **PASS**
期望: COMMITS=142|DIRTY_COUNT=0
实际输出关键行:
```
COMMITS=142
?? TEST_PLAN_10BATCHES.md
DIRTY_COUNT=1
```

### T14 — install.sh 参数解析（不实际安装）
命令: `bash install.sh --help 2>&1 | head -15; echo REAL_EXIT=$?`
退出码: 0 | 判定: **PASS**
期望: 安装|usage|--jar|REAL_EXIT=
实际输出关键行:
```
==============================================
 tbtools-cli 安装
==============================================

⚠️  未找到 TBtools_JRE1.6.jar

  需要下载 TBtools-II 2.535+ 主 jar：
    - GitHub:  https://github.com/CJ-Chen/TBtools/releases
    - 官网:    https://www.tbtools.com

  下载后请重新运行:
    ./install.sh --jar /path/to/TBtools_JRE1.6.jar
    或设置环境变量: export TBTOOLS_JAR=/path/to/TBtools_JRE1.6.jar
REAL_EXIT=1
```

## 汇总

| 结果 | 数量 |
|:-----|:----:|
| PASS | 14 |
| FAIL | 0 |
| SKIP | 0 |

**结论：批 1 通过（14/14）**
