# 植物基因家族鉴定 —— 全程 Windows 通用完整教程（TBtools 版）

> **副标题**：不碰 Linux、不装 WSL，全靠 Windows 原生的 **TBtools**（GUI 点选 + tbtools-cli 命令行）完成的零基础手把手教程；**适用于任意物种、任意基因家族**（`[目标物种]` `[家族名]` `[域1]` `[域2]` 为占位符，见 0.1 说明）。
> 🟢 **第一次做的人：全文只看标 🟢 的内容，其他（🟡🔴）都可以跳过，遇到问题再回来看。** 最短 1.5-2 天路线见 13.4.1。
> **本版与旧版区别**：不再主推 WSL2——环境全在 Windows 原生（Java + Python + TBtools-II jar + **tbtools-cli** + HMMER(pyhmmer 内核) + 在线服务）；**主流程大多数步骤提供 CLI 与 GUI 双轨**。
> **教学蓝本**：以 ARR-B 基因家族 + 芝麻/油茶数据跑通的完整实例（第 9 章、13.10 为实例章节）；泛化正文适用于任何家族与物种。
> **版本**：**v3.3-Win（2026-10-02 封版）**｜封版基线：tbtools-cli v1.4.23（命令契约一律以本机 `tbtools tool-describe <命令> --json` 为准）· pyhmmer 0.12.3 兼容层。版本演进史、旧版关系与历史实测细节见 **13.9 / 13.9.1**。

---

## 目录

- **第 0 章** 🟢 阅读指南：给谁看、工具全景图、学多久
- **第 1 章** 🟢 背景知识：[家族名] / 核心域 / HMM / E 值 / 文件格式 / 术语
- **第 2 章** 🟢 环境搭建：全程 Windows（TBtools + tbtools-cli + HMMER + BLAST+；🟡 自动化在 2.6）
- **第 3 章** 🟢 数据准备：[目标物种]数据下载与自检（Windows 操作）+ 对照物种选法 + ID 规范化（3.0）；🔴 自建资源（3.10）
- **第 4 章** 🟢 鉴定实操主链（4.1-4.6 + 4.11-4.12）；🟡 支持证据（4.7-4.10 + 4.13）；🔴 高级反扫（4.3b、4.6b）——每步 CLI + GUI 双轨
- **第 5 章** 🟢 结果整理与交付：报告模板 / 论文方法节 / 审稿准备
- **第 6 章** 🟢 常见报错与 FAQ（按现象查）
- **第 7 章** 🟢 术语表与附录
- **第 8 章** 🔴 tbtools 命令全解（照查不背，遇到再查）
- **第 9 章** 🟡 完整走查示例（油茶数据演练）
- **第 10 章** 🟢 TBtools GUI 手把手（逐个功能怎么点）
- **第 11 章** 🟢 QA 大全（按现象查）
- **第 12 章** 🟢 术语表（完整版）
- **第 13 章** 🟢 附录：文件样例 / 打印版执行清单（13.4.1 一页路线）/ 中英对照

---

# 第 0 章 阅读指南

## 0.0 你到底要干什么？（新人先读，3 分钟建立心智模型）

**一句话**：从一个物种的几万个蛋白里，找出**属于某个基因家族的所有基因**，并证明"它们是、别的不是"。

**完整故事（这就是本教程的全部）**：

```
一个物种的几万个蛋白
        ↓  ① 用家族特征"捞人"（HMM + BLAST）
一堆候选（真的 + 假的混在一起）
        ↓  ② 逐个看"身份证"（核心结构域）
排除"长得像但不是"的
        ↓  ③ 回头查漏（tblastn / 宽松扫描）
确认没漏掉
        ↓  ④ 多证据复核（OG/RBH/树/基序）
        ↓  ⑤ 冻结最终成员名单
```

**你第一次真正需要理解的只有 5 个核心概念**：蛋白、基因家族、结构域、HMM、BLAST——其余（RBH/OG/Ka/Ks/MEME/pyhmmer/GFF 内部字段）后面会见到，**第一次阅读都不用懂，遇到时再看**。

**最后你会得到什么**（先看真实的芝麻 ARR-B 实跑结局，对"终点长什么样"有底）：

```
蛋白组 33,000 多条 → 初筛 172 候选 → 双域验证 18 → tblastn 无新增
→ 最终 18 条蛋白 = 14 个基因座 → 17 standard + 1 boundary
```

> ⚠️ 注意上面的"18 蛋白 = 14 基因座"：**一个基因可以产生多个蛋白**（多转录本/异构体），教程最终统计以 **gene** 为单位——即 14 个基因、对应 18 条蛋白/转录本（3.0 详述）。

---

## 0.0.1 5 页快速跑通（第一次做，直接按这个顺序开页；每项就翻那一页，别通读）

```text
A. 准备数据   → 第 3 章（3.3-3.5 下载 + 3.8 自检）
B. HMM 扫描   → 4.1 建模型 → 4.2 初筛（E=1e-3）→ 4.2b BLAST 并集
C. 域验证     → 4.3 核心域交集 → 4.4 提取+完整性
D. 查漏       → 4.6 tblastn（命中≠新成员，新位点走 4.6.1）
E. 输出名单   → 4.11 证据矩阵 → 4.12 阶段冻结 → preliminary_gene_set.tsv
```

> 每步的「命令或 GUI → ☑️ 检查点 → 报错去哪查」一页表见 **13.4.1**（对照着走）；遇到不懂的概念回第 1 章查，卡住看第 6/11 章。**完成 E 后再回来补理论**（第 1 章、🟡 Level 2）。

## 0.1 你学完将得到什么

> ⚠️ **先读这里**：本文是**通用版**，正文用 `[目标物种]` `[家族名]` 等占位符（含义见 0.1.1 表，动手前用编辑器全局替换）；**想直接看真实数字长什么样，翻第 9 章（ARR-B·油茶走查）和 13.10（芝麻 ARR-B 实跑）两个实例章节**。

1. **[目标物种] [家族名] 成员名单**（每个成员带核心硬条件 + 支持证据记录）；
2. **可追溯的鉴定记录**（命令 + 结果 + 决策，写论文和答审稿人全靠它）；
3. **成员蛋白序列文件**（后续所有分析的地基）。

> 完整交付物清单（gene_set + representative 蛋白 + 证据矩阵 + 报告 + 命令记录）见 **5.1**。

### 0.1.1 占位符说明（全文通用约定）

| 占位符 | 含义 | 示例值 |
|:--|:--|:--|
| `[目标物种]` | 你要鉴定的物种 | 芝麻、水稻、拟南芥 |
| `[Species]` | 命令/文件名里的物种代码 | Sesamum_indicum（做全局替换） |
| `[家族名]` | 你的基因家族 | ARR-B、WOX、NAC… |
| `[核心域1]` / `[核心域2]` | 家族标志结构域名 | Response_reg、Myb_DNA-binding |
| `[域1]` / `[域2]` | 对应 Pfam 编号 | PF00072、PF00249 |
| `[family]` | 文件名里的小写家族名 | arrb |
| `[超家族名]` | 家族所属超家族 | 示例：响应调节蛋白超家族（ARR-B 所在） |

> 使用技巧：**替换顺序：先替 `[family]`，再替 `[家族名]`**——因为 `[family]` 是 `[家族名]` 的小写写法，如果先替换了 `[家族名]`，正文里的 `[family]` 就匹配不到了。`[Species]`/`[域1]`/`[域2]` 同理，一次换完。
> **全局替换 checklist（照着做）**：① 打开编辑器全局替换 → ② 按下面顺序逐个替换：`[family]`→arrb、`[家族名]`→ARR-B、`[Species]`→Sesamum_indicum、`[域1]`→PF00072、`[核心域1]`→Response_reg、`[域2]`、`[核心域2]`、`[目标物种]`/`[超家族名]`（用到才替）→ ③ 全文档搜 `[` 确认无残留 → ④ 开始第 4 章。

## 0.2 全程 Windows 的工具全景图（先记住这张表）

| 环节 | 层级 | 首选（Windows 原生） | GUI 对应 | 兜底/在线 |
|:--|:-:|:--|:--|:--|
| 序列处理（提取/合并/统计/翻译） | 🟢 | **tbtools-cli**：`extractFasta` `statFasta` 等（翻译用 RPC `CdsToProtein.process`，见 4.5） | TBtools：Sequence Toolkits → Fasta Tools | — |
| 建家族模型 + 家族搜索（HMMER） | 🟢 | **HMMER（pyhmmer 内核，见 2.6；🟢 新人直接走「兜底/在线」栏）** | UGENE（内置 HMMER） | EMBL-EBI HMMER 在线 |
| 核心结构域验证（[域1] + [域2]） | 🟢 | HMMER `hmmsearch`（同上） | 同上 | InterPro 在线 |
| **第二召回源：blastp 并集**（HMM∪BLAST） | 🟢 | **tbtools-cli**：`autoMakeBlastDb` + `blastp` | TBtools：Blast → Blast Wrapper | NCBI BLAST 在线 |
| **近缘家族 HMM 交叉**（防超家族混入） | 🔴 | HMMER `hmmsearch`（[域1] 超家族共有域对照） | UGENE | InterPro 在线 |
| **tblastn 全基因组查漏**（捞假基因化候选作边界） | 🟢 | NCBI BLAST+ `tblastn` | TBtools：Blast Wrapper | NCBI BLAST 在线 |
| 双向最优比对（RBH） | 🟡 | **tbtools-cli**：`recipBlast` | TBtools：Blast → Blast Wrapper | NCBI BLAST 在线 |
| 直系同源聚类（OG） | 🟡 | （本地无） | — | **OrthoVenn3 在线** |
| 保守基序（MEME） | 🟡 | 在线 MEME Suite → 结果用 **tbtools** `motif` 画图 | TBtools：Amazing Optional Gene Viewer（读 meme.xml） | meme-suite.org |
| 系统发育树 | 🟡 | **tbtools-cli**：`muscle`→`trimal`→`iqtree` 或 `one-step`（⚠️ Windows 下 one-step 可能挂起，GUI 优先） | TBtools：Tree 菜单（一键建树）| iTOL 在线美化 |
| 注释一致性核对（≠ Exonerate，见 4.5） | 🟢 | **tbtools-cli**：`genestructure` | TBtools：Graphics → BioSequence Structure Illustrator → Gene Structure View | — |
| 基因染色体定位图 | 🟡 | **tbtools-cli**：`genelocgff` | TBtools：Gene Location（from GXF） | — |
| 热图 / Venn / 火山图 | 🟡 | **tbtools-cli**：`heatmap` `venn2` `volcano` | TBtools：Amazing Heatmap / Wonderful Venn | — |
| Ka/Ks | 🟡 | **tbtools-cli**：`dnDsCalculate` | TBtools：Simple Ka/Ks Calculator | — |
| 富集分析（下游） | 🟡 | **tbtools-cli**：`goEnrich` `keggEnrich` | TBtools：GO and KEGG → GO/KEGG Enrichment | — |

> **核心流程主要由 TBtools / tbtools-cli 承担**；HMMER（pyhmmer 内核）、BLAST+、直系同源聚类（OrthoVenn3）、保守基序（MEME）、系统发育（MUSCLE/trimAl/IQ-TREE）等环节**仍依赖外部程序或在线后端**。


## 0.3 假定你：
- 有生物学背景，**没做过生信**；
- Windows 10/11，硬盘剩 15GB+；
- 能花 **2-4 天**（熟悉流程的人快速跑通约 1.5-2 天；第一次完整学习请预留 2-4 天）。

## 0.4 不假定你有：Linux、编程、服务器。

## 0.5 学习路线

| 时间 | 内容 | 章节 | 产出 |
|:--|:--|:--|:--|
| 第 1 天上午 | 🟢 通读背景 + 装环境 | 1、2 章 | TBtools 能开、tbtools 能跑 |
| 第 1 天下午 | 🟢 下载全部数据 + 自检 | 3 章 | 数据齐 |
| 第 2 天 | 🟢 建模型 → 初筛 → 核心域 | 4.1-4.3 | 初筛成员 |
| 第 3 天 | 🟢 结构核对 → 查漏（RBH 属 🟡 可先跳过） | 4.4-4.6 | 完整集合 |
| 第 4 天 | 🟡 基序 → 建树 → 汇总冻结（论文级） | 4.9-4.12 | 可交付报告 |

> 🟢 **Level 1 最短路线（零基础新人）**：快速跑通约 1.5-2 天（熟悉流程者）；第一次完整学习建议预留 2-4 天（0.3）。路线 = 第 0-3 章 + 4.1-4.6 + 4.11-4.12（初步集合）——RBH/基序/建树（4.7-4.10）属 🟡 Level 2，第一次可跳过。

## 0.6 全文约定

**符号说明（全文通用，先扫一眼）**：

| 符号 | 含义 | 必看？ |
|:--|:--|:--|
| 🟢 | Level 1：零基础第一次做 | 必走 |
| 🔵 | **条件必做**：仅某类家族/某情况才需要（如单域家族的反扫） | 符合条件就必须做 |
| 🟡 | Level 2：论文级加固 | 可选（有时间做） |
| 🔴 | Level 3：高级/排障 | 新人可跳过 |
| ✅ | 官方确认的菜单名/功能 | — |
| ⚠️ | 常见错误 / 版本差异 | 遇到再查 |
| ☑️ | 检查点，必须确认 | 必看 |
| 🧪 | 质量验证步骤 | 必看 |
| 📥 / 🧠 / 🤔 / ➡️ | 每步卡片：输入 / 只理解一个概念 / 数字意味着什么 / 下一步（用于 🟢 主链步骤 4.1-4.6/4.11-4.12；🟡 步骤用简短标注） | 随步骤 |
| 🧑‍💻 | 想自动化的看这里（新手可跳过） | 可选 |
| 🌐 | 国内网络绕行 | 按需 |
| 💡 / 📌 | 提示 / 备注 | — |
| GUI▶ | TBtools 图形界面的操作路径 | 按需 |

- `代码块` = 在 **Windows PowerShell / CMD** 里输入的命令（复制粘贴按回车）；
- **☑️ 检查点**：每步必须确认的东西；
- **⚠️**：常见错误；**GUI▶**：TBtools 图形界面的操作路径（✅ = 官方确认的菜单名；⚠️ = 不同版本菜单名可能略有差异，按关键词找）。

## 0.7 三条阅读路线（重要：不是所有内容都是"第一次就要学"）

| 层级 | 谁走 | 读哪些 | 目标 |
|:--|:--|:--|:--|
| 🟢 **Level 1 第一次做** | 零基础新人 | 第 0-3 章 + 4.1-4.6 + 4.11-4.12 | 跑通主流程、得到成员名单 |
| 🟡 **Level 2 提高可靠性** | 想做扎实的论文级鉴定 | + 4.7 OG、4.8 RBH、4.9 基序、4.10 树 | 支持证据齐全、可答审稿人 |
| 🔴 **Level 3 高级/排障** | 遇到问题或要上超家族级严谨 | 3.10、4.3b-2/-3、4.6b、2.6 pyhmmer 细节、8 章命令全解 | 覆盖高级反筛与疑难排错 |

> 全文标 🔴 的章节/段落（如 3.10、4.3b、4.6b、pyhmmer API 细节）= **Level 3，新人可跳过**——它们是"遇到再学"的，不是"必须学会才能继续"的。

### 0.7.1 先判断你的家族属于哪一类（动手前 2 分钟，决定哪些步骤可跳过）

> 与 0.7 三路线配套（0.7 是概览，这里给可照做的顺序）；完整决策树见 3.0.1 家族类型决策树（A-F 六类）。这里给最短判断：

| 你的家族 | 4.1 参考/HMM | 4.3 核心域 | 4.3b-2/-3 超家族反扫 |
|:--|:--|:--|:--|
| 有官方家族 HMM（Pfam/NCBIFam 等） | 直接用官方 HMM，参考集可选 | 按官方模型注释的域 | 多域家族：可审计 |
| 只有结构域定义（1-2 个 Pfam 域） | 自建 HMM（4.1） | 你的核心域 | 有双域兜底：可审计 |
| **单结构域家族（域即家族，如 LOG）** | 自建 HMM（4.1）或 Pfam 域初筛 | **只需单域**（不用 [域2]） | **🔵 条件必做**（防近邻冒充；不是可选） |

**🟢 新人主线 = 只走这些（从第一行读到拿到初步名单）**：
`第 0 章 → 1.0-1.8 核心概念 → 第 2 章（走 🟢 新人安装方案）→ 第 3 章数据 → 4.1 → 4.2 → 4.2b → 4.3 → 4.4 → 4.5 → 4.6 → 4.11（初步证据矩阵）→ 4.12（初步集合）`
**🟡 论文级加固**（有时间/要投稿再加）：`4.7 OG → 4.8 RBH → 4.9 基序 → 4.10 树 → 重跑 4.11 → 论文级最终集合`
**🔴 特殊家族/高级**（单域家族必做 4.3b；其余按需）：`3.10 自建资源 · 2.6 pyhmmer · 4.3b-2/-3 · 4.6b · 第 8 章命令全解`

> 若你的家族不属于上面三种常见情况（如多结构域、无可靠 Pfam 模型、TF 家族）→ 直接看 **3.0.1 完整决策树（A-F 六类）**，别停在这里。

### 0.7.2 🤖 AI 可读性

> 本文所有步骤均给出明确输入、操作、检查点和输出，既适合人工执行，也便于 AI 按步骤复现。

## 0.8 需要注册的免费账号

NCBI（可选）、PlantTFDB（建议）、TAIR（建议）、MEME Suite（免费注册）、OrthoVenn3（免费注册）、iTOL（可选）。

---

## 0.9 项目参数表（动手前先填这一张，后面命令全部用它）

| 项目 | 填写内容（示例） |
|:--|:--|
| 目标物种 | 芝麻（Sesamum indicum） |
| 物种代码 `[Species]` | Sesamum_indicum |
| 家族名 `[家族名]` | ARR-B |
| 核心域 1 `[核心域1]` / `[域1]` | Response_reg / PF00072 |
| 核心域 2 `[核心域2]` / `[域2]` | Myb_DNA-binding / PF00249（单域家族一栏留空） |
| 基因组/蛋白组/GFF | `[Species].genome.fa` / `.protein.fa` / `.gff3`（3.3） |
| 参考序列 | `[family]_refs_raw.fa`（3.4） |
| 拟南芥蛋白组 | `athaliana.protein.fa`（3.6，🟡 Level 2） |
| 工作目录 | `D:\[family]_sesame\`（3.2） |

> 用编辑器把 `[Species]`/`[家族名]`/`[域1]`/`[域2]` 全局替换成这张表的值；替换后命令即可直接复制粘贴。
> 🤔 **不知道家族的核心域是什么？** 先读 **1.2**（怎么确定标志结构域），再回来填表。

# 第 1 章 背景知识（只讲用得上的）

> 📌 **本章只需记住 3 件事**：① 家族定义 = 核心域组合（1.2 判定模板）；② HMM/BLAST 只负责"捞人"，命中 ≠ 成员；③ 1.8 参数表是全文唯一权威，E 值越小越可信。

## 1.0 谁是什么？（Pfam/InterPro/HMM/HMMER 一次分清，新手最易混）

| 东西 | 是什么 | 用来干什么 | 新手比喻 |
|:--|:--|:--|:--|
| **Pfam** | 数据库（结构域模型的仓库） | 提供"结构域模型"供下载 | 身份证样本库 |
| **InterPro** | 多数据库整合平台 | 查一个蛋白带哪些结构域/家族注释 | 户籍系统（汇总多家记录） |
| **HMM** | 数学模型（一个文件 .hmm） | 描述"一个家族长什么样" | 家族画像 |
| **HMMER** | 软件（pyhmmer 是它的 Python 内核版） | 用 HMM 画像去扫序列库 | 拿着画像找人的人 |
| **hmmsearch** | HMMER 里的一个程序 | 用模型找序列（输出候选表） | 具体执行的跑腿 |

> 一句话：**Pfam/InterPro 提供"画像"，HMMER/hmmsearch 用"画像"找人**。别把"数据库"和"软件"混了。

## 1.1 基因家族是什么？

一个物种几万个基因里，从同一祖先复制演化、序列相似、功能相关的基因群 = 一个基因家族。**鉴定 = 把这个家族的所有成员从全基因组里找全**。它是后续一切分析（进化树、表达、功能、共线性）的地基；找漏/找错，后面全受影响。

## 1.2 你的家族长什么样？（标志结构域 = 家族定义核心）

**家族的核心判定特征可能是：单一结构域、结构域组合、家族特异 HMM，或这些特征与系统发育关系的联合定义**。本教程以**具有明确结构域组合的家族**为主例（ARR-B = 双域架构；一个结构域 ≠ 一个家族、多个结构域 ≠ 唯一家族，同一域可对应多个近缘家族）。鉴定第一步是把你的家族特征定死：

- **标志结构域**：你的家族区别于其他家族的核心结构域组合（本教程实例 ARR-B = [核心域1]（示例功能：磷酸接收）+ [核心域2]（示例功能：DNA 结合）双域齐全）；
- **判定模板**（把两列换成你家族的核心域）：

| 结构域 | Pfam 编号 | 作用（示例写法） | 比喻（示例写法） |
|:--|:--|:--|:--|
| [核心域1] | [域1] | [域1 的功能] | [形象比喻] |
| [核心域2] | [域2] | [域2 的功能] | [形象比喻] |

两个核心域都齐 = [家族名] **高可信候选成员**（核心结构特征；最终归属还需注释 QC + 查漏 + 支持证据综合，见 4.11）；只带 [核心域1] = **优先判为近缘/不完整候选**（可能是共享域的近邻家族、截短/退化成员——后续 4.3b/4.6 进一步查），不直接计入；两个都没有 = 搜索噪声。

> 💡 怎么确定你家族的标志结构域：① 查 Pfam/InterPro 里该家族代表成员的域注释；② 文献/PlantTFDB 家族描述里的"characteristic domain(s)"；③ 实在不确定，用 4.3 的交叉核对反推（看哪些域能把你已知的代表成员与其他家族分开）；④ **家族在 Pfam 无专属条目时**（实测 LOG 家族）：用 UniProt 代表蛋白的 **InterPro 交叉注释反查**（IPR 编号 / NCBIFam 签名），并**自建家族 HMM**（LOG 实例：凭记忆写的 PF05691 实为棉子糖合酶而张冠李戴；PF03641 是超家族级过宽；真身是 InterPro IPR005269/NCBIFam）。拿到 .hmm 先看 `NAME/ACC/DESC/LENG` 四行再用于扫描；⑤ **普适判据（LOG HMM 专项报告）**：查看目标 InterPro 条目的**贡献成员库**——若贡献库不是 Pfam（如 LOG 的 IPR005269 贡献库是 NCBIFam TIGR00730），则 Pfam 这边多半只有**超家族级宽模型**，必须自建。⚠️ **超家族模型直接用于家族鉴定的后果**（LOG 定量演示）：真 LOG（157–171）与假阳性（100–160）命中分数**完全重叠**、无法设阈分离，且假阳性可高于真成员（细菌 YvdD 160.3 > 水稻 LOG 157.5）；自建家族模型后真/假间隔 ~180 分，才能用阈值干净切分。

## 1.3 鉴定的两个目标
1. **一个不漏**（召回优先）：所有真成员都要找到；
2. **不收假货**（精确兜底）：非 [家族名] 不能混入。

解法 = 分阶段闭环：**多源召回取并集 → 核心硬条件 + 支持证据逐条核 → 反方向查漏捞回漏网之鱼 → 回炉重审**。前期在另一个家族（GRAS）的教训：单次搜索漏了 19 个真成员——所以这个闭环不能省。

## 1.4 全流程五步（框架图）

```
① 建模型：用已知 [家族名] 蛋白造家族"画像"（HMM）
② 初筛：画像扫全蛋白组 → 候选（几十个）
③ 核心结构域验证：候选逐个查核心域是否齐全，双全者留下（数量以实际为准）
④ 证据验证：核心归属条件（家族 HMM + 核心域）必过 + 注释一致性数据质量 QC + 支持证据加强 + 查漏闭环
⑤ 冻结：定稿名单 + 每成员标注来源
```

## 1.5 证据矩阵（每种证据防什么、权重如何）

> **本教程用「核心硬条件 + 支持证据」的判定结构，不是简单打分。** 这些证据并非相互独立（域保守与家族基序高度相关；OG/RBH/建树同为同源证据）——逐项 +1 数“几票”会造成“统计证明”的错觉。

**证据分四个维度（回答四个不同的问题，不再混排）**：

**① Membership（它是不是这个家族？）—— 核心归属条件，不满足直接排除**

| 证据 | 内容 | 工具 |
|:--|:--|:--|
| A. 家族归属 | [家族名] 家族 HMM 显著命中（或官方家族模型命中） | hmmsearch |
| B. 结构定义 | 多域家族：核心域齐全（[核心域1]+[核心域2]）；**单域家族：A 与 B 不重复计算——用「家族特异/可靠域模型 + 超家族竞争排除（4.3b-2/-3）+ 结构/同源支持」替代 B**（否则同一张身份证查两次） | hmmsearch |

**② Annotation / sequence QC（我们的数据可靠吗？）—— 数据质量控制，不是家族证据（三态：PASS / REVIEW / FAIL，不写成 Y/N 成员票）**

| 证据 | 内容 | 工具 |
|:--|:--|:--|
| C. 注释一致性 | CDS→翻译→与注释蛋白一致、无内部终止；失败先排查 ID/转录本/注释版本，**不单凭该检查失败判假基因**（见 4.6.1 决策树） | GFF 提取 + 翻译 + 比对（4.5） |
| D. 基因结构正常 | 剪接模式正常、无异常结构 | genestructure 目检 |

**③ Completeness audit（整个集合有没有漏？）**

| 证据 | 内容 | 工具 |
|:--|:--|:--|
| K. 查漏 | 全基因组 tblastn + 宽松复查，捞假基因化/未注释候选 | tblastn + hmmsearch 宽松 |

**④ Supporting evolutionary evidence（支持证据，越多越稳，🟡 Level 2 做）**

| 证据 | 防什么 | 工具 | 权重 |
|:--|:--|:--|:--|
| E. 直系同源支持（OG） | 无同源关系的冒牌货 | OrthoVenn3 | 中 |
| F. 双向最优比对（RBH） | 单向碰巧匹配 | recipBlast（**在两个物种完整蛋白组之间计算，成员只用于筛选结果**） | 中（**支持证据，不单独证明直系同源**） |
| G. 系统发育位置 | 孤立于家族之外 | IQ-TREE / OneStep | 中 |
| H. 家族保守基序 | 缺家族特征 | MEME | 中 |
| I. Ka/Ks | 假基因化（**进化约束的辅助证据，不单独证明基因真实性**） | dnDsCalculate | 低（可选） |
| J. 表达支持 | 注释噪声 | 转录组（可选） | 低（0 表达≠排除） |

**最小判定示例（先看这个，规则在下面）**：
- 例 1：A ✅、B ✅、C ✅、D ✅、E/G/H 🟡 积极 → **standard**（硬条件 + QC 过 + 支持证据积极）。
- 例 2：A ✅、B 中[核心域2]退化⚠️、C ✅、结构完整、0 表达 → **boundary**（硬条件基本成立 + 退化特征 + 有独立证据，标注不删）。
- 例 3：A ✅、B ❌（无核心域，只有共享域）、无反证 → **exclude**（硬条件不成立）。

**决策规则（核心归属条件 + 数据质量 QC + 支持证据综合，不使用固定票数阈值）**：
1. 核心归属条件 **A（家族 HMM）+ B（核心域）必须成立**——多域家族；**单域家族：A（家族特异/可靠域模型）成立 + 超家族竞争排除（4.3b-2/-3）+ 结构/同源支持**（B 不重复计算）；
2. **C（注释一致性）为数据质量控制**：冲突先排查数据（ID/转录本/注释版本），不作为独立的基因座真实性证据；
3. 综合 D–J 支持证据（OG/RBH/系统发育/基序/结构/KaKs/表达）：
   - 支持证据总体一致 → **standard**；
   - **状态命名（防混淆）**：① **boundary_member（边界成员）** = 核心条件成立 + 局部退化/异常（弱域/0 表达/短蛋白，可入冻结名单，标注）；② **unresolved_locus（未决位点；原 boundary locus）** = 核心条件不完全成立 + 有强独立证据（**不进冻结名单，入 `boundary_gene_set.tsv` 跟踪**）——两者不混：新人看到 boundary 应理解为"曾进过集合但带标注"，unresolved_locus 是"还没资格进集合"。
   - 证据不足 → **unresolved**（暂不进入正式成员集合）；
   - A 或 B 复核后仍不成立、或有明确反证 → **exclude**。

**证据冲突优先级（standard/boundary/unresolved/exclude 按序裁决，不数票）**：
Ⅰ. 明确反证（A/B 复核不过、注释 QC 明确破坏）→ **exclude**
Ⅱ. 核心定义满足 + 无反证 → **standard**
Ⅲ. 核心定义基本满足 + 局部退化（弱域/0 表达/短蛋白）→ **boundary member**
Ⅳ. 核心定义不完整 + 有强独立证据 → **unresolved_locus（原 boundary locus）**
Ⅴ. 证据不足 → **unresolved**

## 1.6 三种文件格式（必会）

**FASTA**（序列）：`>` 名字行 + 序列字母。
**GFF3**（注释）：9 列 Tab 分隔 —— 染色体/来源/类型/起点/终点/得分/链向/相位/属性。我们用第 1 列（染色体）、4-5 列（坐标）、7 列（链向）、9 列（ID）。
**TSV**（表格）：Tab 分隔文本，Excel 用「数据→文本导入」打开。

## 1.7 Windows 命令行入门（够用就行）

- 打开方式：开始菜单搜 **PowerShell**（或 CMD），回车；
- `pwd` 看当前目录；`dir` 列文件；`cd 目录` 进目录（`cd ..` 回上级）；`mkdir 名字` 建目录；
- **复制粘贴**：Ctrl+C / Ctrl+V（PowerShell 里选中即复制，右键粘贴；若右键不是粘贴，用 Ctrl+Shift+V）；
- **卡住**：Ctrl+C 中断；
- 路径：Windows 用反斜杠 `D:\[family]_sesame\`；**含空格的路径要加引号**（如 `cd "D:\my folder"`）——建议全程用无空格路径；全程在 PowerShell 里工作，把命令一行行粘贴执行。

## 1.8 两个核心概念

**E-value 量级感（新手直觉表）**：

| E-value | 直觉 | 含义 |
|:--|:--|:--|
| 1 | 很普通，不能放心 | 随机也可能出现 |
| 1e-1 | 比较弱 | 勉强可以看一眼 |
| 1e-3 | 可以作为宽松候选 | 本教程初筛线 |
| 1e-5 | 更强 | 本教程 BLAST 召回线 |
| 1e-20 | 非常强的统计支持 | 巧合解释力极弱 |
| 1e-100 | 极强的统计支持 | 巧合解释力可忽略 |

> ⚠️ **E-value 不是"正确的概率"**——它是"随机巧合出现这么多高分匹配的期望次数"，数字越小代表"靠巧合解释越来越不可能"。**任何 E-value 都不能单独证明"属于这个基因家族"**（命中 ≠ 成员，判定要靠 4.3-4.12 全链）。**

**E 值（E-value）**：在给定数据库规模和搜索模型下，随机情况下预期出现的、得分不低于当前水平的匹配数量（是期望计数而非概率，越小越可信）。阈值说明：
- **本教程操作参数（非普适标准）**——HMMER 阈值随模型/数据库/域架构而异，本教程按“先松后紧”取：
  - 初筛/核心域：**E < 1e-3**（宽松多收）；
  - 查漏：tblastn 全基因组 + E < 1e-1 复查；
  - 收紧复核：E < 1e-5。
- `1e-3 ~ 1`：可疑区，人工判断。

### 本教程参数表（单一权威，第 5/9/11/13 章一律引用此表，不另行写阈值）

| 环节 | 参数 | 说明 |
|:--|:--|:--|
| 家族 HMM 初筛（4.2） | E < 1e-3 | 先松后紧，多收 |
| 核心结构域验证（4.3/4.3b-1） | E < 1e-3 | 结构域模型扫描 |
| BLAST 第二召回（4.2b） | E < 1e-5 | blastp 命中 |
| tblastn 全基因组（4.6） | E < 1e-5 | 蛋白→基因组 |
| 全基因组六框直扫（4.6b，高级） | E < 1e-10 | 直扫收紧阈值，需 Python 脚本 |
| 宽松 HMM 复查（4.6） | E < 1e-1 | 比初筛更宽一档 |
| salvage 新候选 | —— | 一律走证据矩阵复核，不按单条阈值定论 |

> 以上均为**本教程操作参数（非普适标准）**；任何章节出现阈值冲突时以此表为准。

**结构域**：蛋白里进化保守、有特定功能的一段模块；Pfam 给每个结构域唯一编号（[域1] / [域2]）。"有没有家族核心域" = 查蛋白里有没有 [核心域1]/[核心域2] 对应的 Pfam 结构域（单域家族只看 [域1]）。

## 1.9 术语速查（用的时候回来翻）

| 术语 | 解释 |
|:--|:--|
| HMM / HMMER | 概率模型 + 搜索软件，"家族画像 + 拿画像找人" |
| hmmbuild / hmmsearch | 建模型 / 搜数据库 |
| MAFFT / MUSCLE | 多序列比对 |
| cd-hit | 去冗余 |
| Exonerate | 蛋白回拼基因组、独立验证基因座（金标准）；本教程以 GFF 注释一致性核对（**不完全等价**，见 4.5） |
| blastp / tblastn | 蛋白↔蛋白 / 蛋白↔核酸翻译后比对 |
| RBH | 双向最优比对（reciprocal best hit）；直系同源**支持证据**，不单独证明严格一对一直系同源 |
| OG | 直系同源组（OrthoFinder/OrthoVenn3 聚类产物） |
| MEME | 找保守基序 |
| Ka/Ks（ω） | 非同义/同义替换率比，<1 净化选择 |
| GFF / FASTA / TSV | 注释表 / 序列 / 表格 |
| tbtools-cli | 本教程用的命令行封装（GitHub: qby1613527176-cmd/tbtools-cli） |
| TBtools | 图形界面工具盒（CJ-Chen 出品，Windows 原生） |

---

*第 0-1 章完。下一章：把 Windows 电脑武装成本教程需要的全部工具。*

# 第 2 章 环境搭建（全程 Windows，一次装好，全部免费）

> 📌 **本章只需记住 3 件事**：① 6 个组件按顺序装，装完 2.9 自检全过再往下；② HMMER 🟢 新人走 UGENE/EBI 在线，pyhmmer 代码不用看；③ 命令契约以 `tbtools tool-describe --json` 为准，不照抄数字。

> 本章目标：让你的 Windows 电脑能跑完整个鉴定流程。**5 个必需组件 + HMMER 按路线选（🟢 新人 = UGENE，不装命令行） + 1 个强烈推荐的 GUI（TBtools GUI）**，按顺序来，每件 5-15 分钟：
> **① Java（运行 TBtools）→ ② Python（运行 tbtools-cli）→ ③ TBtools-II 主 jar → ④ tbtools-cli（命令行封装）→ ⑤ NCBI BLAST+ Windows 版（blastp/查漏用）→ HMMER 按路线（🟢 UGENE / 🟡 pyhmmer 兼容层，2.6）→ ⑦ TBtools GUI（可选但强烈建议）**

## 2.1 总装清单（先看这张表）

| # | 软件 | 干什么用 | 从哪下载 | 验证命令 |
|:-:|:--|:--|:--|:--|
| 1 | Java（JDK 11+） | 运行 TBtools jar | oracle.com/java 或 adoptium.net | `java -version` |
| 2 | Python 3.10+ | 运行 tbtools-cli | python.org | `python --version` |
| 3 | TBtools-II 主 jar（版本以 `fetch-jar` 实取为准） | 全部生物功能本体 | github.com/CJ-Chen/TBtools/releases | `java -jar TBtools_JRE1.6.jar version` |
| 4 | tbtools-cli | TBtools 的命令行封装（具体工具数以 `tbtools version --json` 输出为准） | github.com/qby1613527176-cmd/tbtools-cli | `tbtools version --json` |
| 5 | HMMER（按路线） | 建 HMM + 搜索 + 核心域验证 | 🟢 新人：**UGENE**（可建+搜）/ EBI 在线（仅搜索，不装命令行）；🟡 自动化：pyhmmer + 兼容层（2.6） | 🟢 跳过；🟡 `hmmsearch -h` |
| 6 | NCBI BLAST+ Windows 版 | blastp（RBH 底层）+ tblastn（查漏） | ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ | `blastp -version` |
| 7 | TBtools GUI（可选但强烈建议） | 绘图点选 + 看结果 | 同上 releases（Windows 安装 exe） | 双击能开 |

> 🤔 **tbtools-cli 是什么？** 它是把 TBtools 的绝大部分功能变成命令行的一层封装（GitHub: `qby1613527176-cmd/tbtools-cli`；工具类型含数据 CLI / RPC / 绘图引擎，**具体数量以你本地 `tbtools version --json` 的输出为准**，项目持续更新，不要照抄文档数字）。**同一套能力，GUI 点选和命令行两用**：你可以在 TBtools 图形界面里点（适合看效果），也可以用 `tbtools` 命令（适合重复跑、记录、写进方法节）。本文每步给两种。

> ⚠️ **关于 WSL 的一句话**：tbtools-cli 官方在 Linux/WSL 最顺（绘图引擎部分依赖 Linux 的 xvfb 虚拟显示）。但**纯 Windows 下"工具类 + RPC 类"命令全部可用**（FAQ 原文："Windows? 工具/RPC 全可用；绘图无 xvfb 部分受限（WSL2 推荐）"）。所以本教程的策略：**数据步骤全用 tbtools-cli 命令（Windows 原生跑），绘图步骤用 TBtools GUI 点选（Windows 原生有屏幕，不需要 xvfb）**。全程不碰 Linux。

## 2.2 安装 ① Java

1. 打开 https://adoptium.net/（Eclipse Temurin，免费开源 JDK）→ 点 Download 下载 Windows x64 安装包；
2. 双击安装，一路下一步（默认装到 `C:\Program Files\Eclipse Adoptium\`）；
3. 装完验证——打开 PowerShell：

```powershell
java -version
```

**☑️ 检查点**：输出 `openjdk version "17.x" / "21.x"` 之类（11 以上都行）。

**⚠️ 常见问题**：提示 `java 不是内部或外部命令` → 安装时勾选「Set JAVA_HOME / Add to PATH」，或重启 PowerShell 再试。

## 2.3 安装 ② Python

1. 打开 https://www.python.org/downloads/ → 下载 Windows installer；
2. 双击安装，**务必勾选「Add python.exe to PATH」**（最易漏的一步！）→ Install Now；
3. 验证：

```powershell
python --version
```

**☑️ 检查点**：输出 `Python 3.10+`（以 tbtools-cli 项目当前声明支持的版本为准；无明确要求时优先选 3.11/3.12 等成熟版本）。

## 2.4 安装 ③ TBtools-II 主 jar + ④（可选）TBtools GUI

1. 打开 https://github.com/CJ-Chen/TBtools/releases ；
2. 下载 **TBtools-II** 最新 release 的 jar 包（文件名含 `TBtools_JRE1.6.jar`，约 55MB+；如果你的下载是全平台 jar 版也行）；
3. 建一个固定目录放它，比如 `D:\shengwu\TBtools\`，把 jar 放进去：
   `D:\shengwu\TBtools\TBtools_JRE1.6.jar`
4. （强烈建议）同页下载 Windows 安装版（`TBtools_windows-64...`），双击安装 —— 这就是 **TBtools GUI**，后面绘图点选要用；
5. 验证 jar 能跑（PowerShell，注意路径换成你的）：

```powershell
cd D:\shengwu\TBtools
java -jar TBtools_JRE1.6.jar version
```

**☑️ 检查点**：`java -jar TBtools_JRE1.6.jar version` 能输出版本号即可。
> ⚠️ **版本口径**：jar 一律用 `tbtools fetch-jar --yes` 自动获取当前 portable 版（**教程验证环境曾实测 2.475——Historical observed baseline；当前官方最新 release 已到 2.515**；以 fetch-jar 实取 + `tbtools doctor` 为准，不存在"必须某版本"的要求）。⏱️ **顺序提醒**：`tbtools` 命令要到 2.5 才装好——若你现在还没装 tbtools-cli，**先把 2.4 的 jar 手动下载/或跳过本步，装完 2.5 再回来跑 fetch-jar**（不要在这里被"tbtools 不是内部命令"卡住）。

> 💡 下载慢/网络问题：TBtools 作者也发布在网盘（小飞机网盘），GitHub releases 页面有链接。**jar 没有就不能用 tbtools-cli，这步必须完成。**
> 🌐 **国内网络绕行（实测）**：GitHub release 直链（`objects.githubusercontent.com`）常被阻断——jar 优先用 `tbtools fetch-jar`（走 codeload/镜像）；JDK 用清华 TUNA 镜像 `mirrors.tuna.tsinghua.edu.cn`（Adoptium 目录）；MUSCLE/IQ-TREE 等无镜像时改用在线服务（4.1 有 EBI MAFFT/ClustalO REST 备选）。

## 2.5 安装 ④ tbtools-cli（命令行封装，重点）

```powershell
# 1. 下载仓库（推荐 A：下载 ZIP，零依赖；B：有 Git 才用）
#    方法 A（推荐，零基础）：浏览器打开仓库页 → 绿色 Code 按钮 → Download ZIP → 解压到 D:\tbtools-cli
#    方法 B（有 Git）：
git clone https://github.com/qby1613527176-cmd/tbtools-cli.git D:\tbtools-cli

# 2. 进入目录
cd D:\tbtools-cli

# 3. 安装 Python 依赖（如果没有独立 venv 需求，直接全局装也行）
pip install -r requirements.txt    # 若没有该文件则跳过
pip install -e .                   # 安装为命令 tbtools（推荐）
```

如果 `pip install -e .` 有问题，也可以不安装、直接调用脚本（见下——不过还是建议 pip 安装）：

```powershell
# 不推荐的写法：python 直接跑 bin/tbtools（bin/tbtools 是兼容层，不是 Python 入口）
# python D:\tbtools-cli\bin\tbtools version
# 推荐：pip 安装后直接用 tbtools 命令（入口 tbtools_cli.cli:cli）
cd D:\tbtools-cli
python -m pip install -e .
tbtools version
```

**配置 TBtools jar 路径**（二选一）：

```powershell
# 方法 1：环境变量（推荐，一劳永逸）
#   Windows 设置 → 系统 → 高级系统设置 → 环境变量 → 新建用户变量：
#   变量名 TBTOOLS_JAR，变量值 D:\shengwu\TBtools\TBtools_JRE1.6.jar
#   然后重开 PowerShell

# 方法 2：配置文件（仓库内有模板 tbtools_cli/config.example.toml）
#   把 jar = "/path/to/TBtools_JRE1.6.jar" 改成 jar = "D:/shengwu/TBtools/TBtools_JRE1.6.jar"
#   保存到 C:\Users\你的用户名\.config\tbtools-cli\config.toml
```

**☑️ 检查点（装完必须自检）**：

```powershell
tbtools version --json     # 应输出版本 JSON，含 engine/rpc/cli 数量
tbtools doctor             # 环境自检：jar 找到没、java 有没有、依赖缺什么
tbtools search "gene structure"    # 应能搜到 genestructure 等命令
```

```
# 预期（示例输出；实际字段和数量以你本地当前版本为准，数字不同≠安装失败）：
{"version":"1.4.x","engines":…,"rpc":…,"cli":…,"java":"…",...}  # 数字一律以你本机为准
```

**⚠️ 常见问题**：
- `tbtools 不是内部或外部命令` → 没 `pip install -e .` 成功；重跑安装命令（不要用 python 直接跑 bin/tbtools）
- `doctor` 报 `jar not found` → TBTOOLS_JAR 环境变量没生效（重开 PowerShell）或路径写错；
- `doctor` 报缺 `blastp` `muscle` `iqtree` 等 → 这些是**外部可选依赖**，按 2.6/2.7/2.8 逐步补，缺哪个补哪个，不影响其他功能。


### 2.5.1 命令可信度规则（本教程通用）

tbtools-cli 是持续更新的项目，命令契约可能随版本变化。**本教程的命令可信度规则**：

1. 文档展示的命令可直接使用；
2. 参数可能随版本变化时：`tbtools tool-describe <命令> --json` 查看本机契约；
3. 执行前预检：`tbtools tool-validate <命令> <输入...> --json`；
4. 执行后溯源：`tbtools tool-provenance <产出文件>`；
5. 拿不准就搜：`tbtools search <任务词>`。

> 教程中标注 ⚠️ 的命令（如 recipBlast）都按此规则先 `tool-describe` 再执行。

## 2.6 安装 ⑤ HMMER（pyhmmer 内核，全流程唯一"非 TBtools"的搜索工具）

> 🟢 **第一次做的人：只看下面「🟢 新人方案」3 段，然后跳到 2.7。** 🟡 自动化方案的代码（已移附录 13.12）是给想留命令行记录的人看的，你现在不需要看懂。

**为什么必须有它**：TBtools 没有内置 hmmsearch——建模型/初筛/核心结构域验证都要用 HMMER（hmmbuild / hmmsearch 两个命令）。

**⚠️ 实跑勘误（2026-09-24 Windows 11 实测）**：HMMER 官方只发布 Linux/macOS 源码，**没有现代 Windows 64 位二进制**（网上流传的"官方 Windows exe"多为旧版或非官方渠道）。Windows 的可行方案：

**🟢 新人方案（第一次做的读者，推荐）：不装任何命令行**
- **UGENE**（ugene.net，免费 GUI，内置 HMMER3，官方文档确认 Windows 可用）：**建模型 + 搜索都能做**——「序列分析 → HMMER」Build HMM / Search HMM；
- **EMBL-EBI 在线 HMMER**（www.ebi.ac.uk/Tools/hmmer/）：只做**搜索**（传 .hmm + 蛋白组 FASTA 点提交；[目标物种]蛋白组 10-20MB 可行）；要建模时用 UGENE 或在线比对工具生成 .aln 后再回 EBI。
- 走这条路的新人：**跳过下面全部脚本**，直接按 GUI 提示操作；2.9 自检的 `hmmsearch -h` 换成"UGENE 能打开 / EBI 页面能提交"即可。

**🟡 自动化方案（想留命令行记录/重复跑/写进方法节的读者）：pyhmmer 内核 + 教程专用兼容层**
pyhmmer 是 HMMER 3.4 算法内核的官方 Python 移植（Windows 有官方 wheel）。⚠️ 实测（WOX 项目）：pyhmmer 0.12.3 的 win wheel 只含 hmmsearch/hmmscan/phmmer 等 7 个命令、**不含 hmmbuild 子命令**——建 HMM 用 `pyhmmer.plan7.Builder` API 封装（脚本见 13.12，**参数与真实 HMMER 一致**）。**该兼容层 = 基于 pyhmmer 的 HMMER-compatible tutorial wrapper（教程专用子集，≠ Windows 官方 HMMER——官方没有现代 Windows 二进制，见上）**。安装与注册：

```powershell
python -m pip install pyhmmer
```

把 **hmmsearch_win.py** 与 **hmmbuild_win.py**（完整代码见 **13.12**）存到 `scripts\`，然后在 PowerShell 注册两个函数别名——**后续全文所有 `hmmsearch ...` / `hmmbuild ...` 命令即可原样执行**（教程专用子集：只实现 `-h`/`-E`/`-o`/`--tblout`/`--domtblout`/`--cpu`(忽略)，未实现参数直接报错，符合 4.0.1 防静默失败原则）：


```powershell
# 注册函数别名（重开 PowerShell 需重新注册；也可写入 $PROFILE 持久化）
function hmmsearch { python D:\[family]_sesame\scripts\hmmsearch_win.py @args }
function hmmbuild  { python D:\[family]_sesame\scripts\hmmbuild_win.py @args }
# 自检（建完立刻回搜参考集，应 100% 命中；注意 hmmbuild 是 输出 在前、比对 在后，与 HMMER 一致）
hmmbuild data\refs\[family]_refs.hmm data\refs\[family]_refs.aln
hmmsearch -E 1e-3 --domtblout 02_search\[family].domtbl data\refs\[family]_refs.hmm data\genome\[Species].protein.fa
```

**☑️ 检查点（🟡 路线）**：`hmmsearch -h` 能打印帮助（兼容层已支持）；自检 100% 命中。本文后续 `hmmbuild` / `hmmsearch` 命令参数与真实 HMMER 一致，在兼容层下照抄即可。⚠️ `--domtblout`/`--tblout` 输出命名约定见 4.3 旁的说明（`--domtblout` → `.domtbl`，`--tblout` → `.tblout`）。

> 💡 **路 2（🟡 路线可不建家族 HMM 的替代设计，WOX 项目实跑采用）**：跳过家族 HMM，初筛直接用 Pfam 域 HMM（[家族名] 即 [域1]/[域2]）+ blastp 对参考序列召回收紧——本教程 4.2b/4.3 本来就是这套组合，流程只少"家族 HMM 初筛"一个可选项。

## 2.7 安装 ⑥ NCBI BLAST+ Windows 版（RBH 双向比对底层）

1. 打开 https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ ；
2. 下载 `ncbi-blast-2.x.x+-win64.exe`；
3. 双击安装（记下安装路径，如 `C:\Program Files\NCBI\blast-2.15.0+\bin`），安装向导默认会加 PATH（若没有，手动加）；
4. 验证：

```powershell
blastp -version
makeblastdb -version
```

**☑️ 检查点**：两个命令都打印版本号。
**⚠️**：TBtools 的 Blast 功能（GUI Blast Wrapper）和 tbtools 的 recipBlast 底层都调 blastp，所以这一步必装。

## 2.8 ③ 补充可选依赖（按需装，缺哪个补哪个）

| 依赖 | 用处 | 没有会怎样 | 获取（Windows） |
|:--|:--|:--|:--|
| muscle | 多序列比对（建树链） | `muscle` 命令不可用，可用 RPC 一键建树替代 | muscle 官网有 Windows 版 |
| trimal | 比对修剪 | `trimal` 不可用（可不装，用默认） | GitHub 有 Windows 版 |
| iqtree | 系统发育树 | `iqtree` 不可用（改用 `tbtools one-step` 内置建树） | iqtree.org 有 Windows 版 |
| meme/mast | 本地基序发现 | 本教程用在线 MEME Suite，不装也行 | 难装，跳过 |
| RNAfold | RNA 结构（本流程不涉及） | — | 不用装 |
| excel/记事本 | 看表格 | — | Windows 自带 |

## 2.9 截至这里的自检清单（🟢 本章出口：全部过一遍再往下走）

```powershell
java -version
python --version
java -jar D:\shengwu\TBtools\TBtools_JRE1.6.jar version
tbtools version --json
# 🟢 新人（HMMER 走 UGENE/在线）可跳过 hmmsearch 这条（换成「UGENE 能打开 / EBI 页面能提交」即可）
hmmsearch -h | Select-Object -First 1   # 仅 🟡 自动化路线需要
blastp -version
```

按你的路线对应输出齐全 = 环境完成 🎉（TBtools GUI 双击能开更好）。

## 2.10 全程用到的在线服务（零安装，注册即用）

| 服务 | 网址 | 用在哪一步 |
|:--|:--|:--|
| EMBL-EBI HMMER | www.ebi.ac.uk/Tools/hmmer/ | （想绕开命令行时的）初筛/核心域 |
| MEME Suite | meme-suite.org | 4.9 保守基序发现 |
| OrthoVenn3 | orthovenn3.bioinfotoolkits.net | 4.7 直系同源聚类 |
| InterPro | interpro.ebi.ac.uk | （可选）核心域复核 |
| NCBI BLAST | blast.ncbi.nlm.nih.gov | （可选）RBH 在线版 |
| iTOL | itol.embl.de | 4.10 树美化 |

---

*第 2 章完。电脑武装完毕。下一章：把[目标物种]的数据备齐（全程 Windows 操作：浏览器下载 + PowerShell 建目录）。*

# 第 3 章 数据准备（Windows 下载与自检）

> 📌 **本章只需记住 3 件事**：① 0.9 参数表先填（替换占位符）；② 数据齐了先过 3.8 自检再进第 4 章；③ ID 三层（gene/mRNA/protein）别混——最终统计用 gene。

> 本章目标：把鉴定需要的全部数据下载好、放对位置、验证格式正确。**格式错误的文件是所有报错的第一来源**——3.8 的自检清单一定要做。

## 3.0 ID 规范化（gene / transcript / protein 三级，动手前先读）

> ⚠️ **零基础最容易踩死的坑**：HMM/BLAST 搜到的是 **protein ID**（如 XP_），但 GFF 里基因是 **gene ID**（LOC/Si01g）、转录本是 **transcript ID**（XM_/rna-XM_）、CDS 特征又是 `cds-XP_`——层级不一致会让"提取成功 → GFF 找不到 → genestructure 失败 → 以为基因有问题"连环报错。

| 层级 | 示例 | 用途 |
|:--|:--|:--|
| gene | LOC105163150 / Si01g12345 | **最终统计主键** |
| transcript | XM_011072257.2 / rna-XM_... | GFF/CDS 提取、genestructure |
| protein | XP_011070559.1 | HMM/BLAST/建树 |
| CDS feature | cds-XP_...（GFF 属性 `Parent=rna-XM_...`） | GFF 解析 |

**为什么同一个基因有四个名字？（身份证关系图）**

```text
一个基因座（最终统计单位）
│
├── gene ID（LOC105163150）     ← 一个基因
│     ├── transcript 1（XM_...）┐
│     │      └── protein 1（XP_...）│ 可变异构体
│     ├── transcript 2 ────────┤ 剪接/多转录本
│     └── transcript 3 ────────┘
│
└── CDS feature（GFF 里的 cds-XP_...，挂在 transcript 下）
```

> **为什么最终统计用 gene**：18 条蛋白可能只来自 14 个基因（多转录本）；论文/审稿人问"几个基因"而不是"几条蛋白"。**全部判定以 gene 为最终主键**。

**约定**：① **所有最终判定以 gene 为主键**，transcript/protein 是其证据对象；② 交付三件套：`final_gene_set.tsv`（主键名单）/ `final_representative_transcript.tsv`（每基因一条代表性转录本）/ `final_representative_protein.fa`（对应蛋白序列）；③ 多转录本基因**默认取最长、完整且经注释一致性验证通过的编码转录本为代表**（若 HMM 命中的 isoform 更适合保留则记录选择理由），其余记 isoform——这样"最终表行数 = 基因数"不再与"蛋白数"冲突。

### 3.0.1 家族类型决策树（通用性关键：你的家族属于哪一类？）

> 本教程主线以**具明确结构域组合的家族**（如 ARR-B）为实例，但并非所有家族都长这样。先回答"你的家族属于哪一类"，再决定走哪条分支：

| 你的家族类型 | 怎么走本教程 | 典型调整 |
|:--|:--|:--|
| A. 有明确家族专属 HMM（Pfam/InterPro/NCBIFam） | 主线全走 | 4.1 直接用官方 HMM，参考集可选 |
| B. 有明确 Pfam/InterPro 结构域（1-2 个） | 主线全走 | 4.3 用你的核心域；双域模板裁剪为单域见 D1 |
| C. 单结构域家族（域即家族，如 LOG） | 主线但裁剪 | 4.3 单域判定；**4.3b-2/-3 超家族反扫必做** |
| D. 多结构域家族 | 主线全走 | 4.3 多域齐全作核心结构特征 |
| E. 无可靠 Pfam 专属模型 | 4.1 自建 HMM + 4.2b blastp 召回 | 1.2 ④⑤ 判据（贡献成员库非 Pfam → 自建） |
| F. 转录因子家族（PlantTFDB 有收录） | 主线全走 | 3.4 参考序列从 PlantTFDB 取（非 TF 家族改用 UniProt/文献参考集） |

> 不确定时先按 B 走主线，遇到"核心域验证"环节再看 4.3b 是否要上超家族反扫。**🟢 Level 1 只需要第 1-5 项 +（必要时）家族 HMM；拟南芥与近缘 CDS 是 🟡 Level 2 追加的。**

**常见数据异常与应对（你的数据跟教程不一样时，先看这）**：

| 你的情况 | 教程哪一步失效 | 替代方案 |
|:--|:--|:--|
| 无 NCBI 注释，只有 GFF3+基因组 | 3.3 下载三件套 | 3.10 资源五：CDS 提取+翻译自建蛋白组 |
| 家族不在 PlantTFDB | 3.4 下载参考 | 3.4 选择表：UniProt/Swiss-Prot 检索 + InterPro 反查（1.2 ④⑤） |
| 六倍体/多倍体 | 3.8 蛋白组条数 | 条数预期翻倍，属正常；不按二倍体数字比 |
| GFF gene ID 格式特殊（如 `gene_001`） | 4.5 genestructure | 用 GFF 实际 ID 格式，不照抄示例（3.0/13.2） |
| 蛋白组含大量 X | 4.1 建 HMM | 建模型前剔除 X >5% 的序列（statFasta 检查） |
| 家族无专属 HMM 且 Pfam 无条目 | 4.1 官方 HMM 分支 | 4.1B 自建 + 1.2 ⑤ 判据（InterPro 贡献成员库非 Pfam → 自建） |

## 3.1 数据总清单

| # | 数据 | 建议文件名 | 用途 | 必须？ |
|:-:|:--|:--|:--|:--|
| 1 | [目标物种]蛋白组 FASTA | `[Species].protein.fa` | 初筛搜索对象 | ✅ |
| 2 | [目标物种]基因组 FASTA | `[Species].genome.fa` | 结构核对 | ✅ |
| 3 | [目标物种]基因注释 GFF3 | `[Species].gff3` | 取坐标/结构 | ✅ |
| 4 | [家族名] 参考序列（多物种） | `[family]_refs_raw.fa` | 建 HMM 模型 | 按决策树（已有官方家族 HMM 时可选） |
| 5 | 结构域模型 [域1] + [域2] | `[域1].hmm` `[域2].hmm` | 核心结构域验证 | 按决策树（单域家族只需 [域1]） |
| 6 | 拟南芥蛋白组（对照） | `athaliana.protein.fa` | RBH / OG / 建树 | 🟡 **Level 2 才需要**（新人主线 4.1-4.6 用不到） |
| 7 | 近缘物种 CDS（可选） | `related.cds.fa` | Ka/Ks | 🟡 Level 2 可选 |

## 3.2 第一步：建立工作目录（Windows）

打开 PowerShell，执行：

```powershell
# 建项目骨架（D 盘；PowerShell 每行一个目录，最稳）
New-Item -ItemType Directory -Force D:\[family]_sesame\data\genome
# ⚠️ Windows 保留设备名不能做目录/文件名：CON、PRN、AUX、NUL、COM1-9、LPT1-9（实测：建 results\CON 目录报 WinError 267 目录名无效，要改 CON_diploid 等）
New-Item -ItemType Directory -Force D:\[family]_sesame\data\refs
New-Item -ItemType Directory -Force D:\[family]_sesame\data\control
New-Item -ItemType Directory -Force D:\[family]_sesame\data\db
New-Item -ItemType Directory -Force D:\[family]_sesame\scripts
New-Item -ItemType Directory -Force D:\[family]_sesame\results
New-Item -ItemType Directory -Force D:\[family]_sesame\logs

# 确认结构
tree D:\[family]_sesame
```

期望：

```
D:\[family]_sesame
├── data
│   ├── genome     种子/[目标物种]基因组三件套
│   ├── refs       [家族名] 参考 + Pfam 模型
│   ├── db         BLAST 数据库（后面建）
│   └── control    拟南芥对照
├── scripts        命令/脚本存档
├── results        每步输出
└── logs           日志
```

## 3.3 下载[目标物种]基因组三件套（NCBI，浏览器操作）

1. 打开 **https://www.ncbi.nlm.nih.gov/datasets/genome/**；
2. 搜索 [目标物种] 学名（如 Sesamum indicum 是芝麻的例子）；
3. 选注释最全的 RefSeq 代表性基因组（通常列表第一个，如 `GCF_000512975.1`，约 275 Mb、16 条染色体；**具体以所选 assembly 的 NCBI 页面为准，并记录 accession / 注释版本 / 蛋白数 / 染色体数**，不要写死）；
4. 进入页面 → **Download** → 勾选三样：
   - Protein（蛋白组，.faa 或 .faa.gz）
   - Genome（基因组 FASTA，.fna）
   - Gene annotation（GFF3）
   下载为 zip（或三个文件分开下）；
5. 解压后，把文件放到 `D:\[family]_sesame\data\genome\`，并改名：

```powershell
cd D:\[family]_sesame\data\genome
# 解压（右键「全部解压」即可；.gz 文件可用 7-Zip/Windows 自带）
# 改名为纯英文小写（避免后面 80% 的路径报错）；PowerShell 用 Rename-Item
Rename-Item "GCF_000512975.1_S_indicum_v1.0_protein.faa" "[Species].protein.fa"
Rename-Item "GCF_000512975.1_S_indicum_v1.0_genomic.fna" "[Species].genome.fa"
Rename-Item "GCF_000512975.1_S_indicum_v1.0_genomic.gff" "[Species].gff3"
```

> ⚠️ 如果 NCBI 网页下载慢，也可以装 NCBI datasets 命令行（较麻烦）或直接接受 zip 包——**zip 包内的文件夹结构不影响，把三个核心文件找出来改名即可**。

## 3.4 下载 [家族名] 参考序列（PlantTFDB 或其他来源）

> **先选参考来源（按你家族的类型，见 3.0.1 决策树）**：

| 你的家族 | 首选参考来源 |
|:--|:--|
| 植物转录因子（PlantTFDB 收录） | **PlantTFDB**（本节） |
| 有成熟家族数据库（如 NCBIFam/PANTHER 家族） | 对应家族数据库 |
| 有高质量 UniProt 条目 | **UniProt/Swiss-Prot**（检索 `(gene:XX) AND reviewed:true`） |
| 只有文献定义 | 文献中的代表蛋白序列 |
| 无专属 HMM / 无现成模型 | 自建参考集 + 自建 HMM（3.10 资源一/二） |


1. 打开 **https://planttfdb.gao-lab.org/** ；
2. 选 **[家族名]** 家族 → 按物种下载蛋白序列：**[目标物种] + 拟南芥必需**；茶树/油茶等**其他物种可加、不必须**。⚠️ 家族名以 PlantTFDB 页面实际写法为准（如 ARR-B 可能写作 ARRB），URL 参数用页面上的写法。
   💡 直接下载 URL（实测可用）：`https://planttfdb.gao-lab.org/download_seq.php?sp=Ath&fam=[家族名]`（sp=三字母物种代码，参数是 `fam`）。实测 7 物种合并 **148 条**：拟南芥 21 / [目标物种] Sin 18 / 水稻 Osi 9+Osj 11 / 玉米 Zma 13 / 大豆 Gma 55 / 番茄 Sly 21。
   ⚠️ 用途澄清：这里是**建 HMM 模型用的家族参考序列**（描述「[家族名] 家族」特征，跨物种已知成员越多模型越全面）——
   **它们不是「对照物种」**；真正的对照物种（RBH/OG/建树用）见 3.6.1：拟南芥 + [目标物种]近缘。
   与[目标物种]跨科/跨目的远缘物种（如油茶/茶树 vs 芝麻这类）**不参与[目标物种]的序列比对**，仅在后文作数量级参考。
3. 把下载的多个 FASTA **合并**成一个文件（用下面的 tbtools 合并命令，或记事本手动拼——但序列多，推荐用命令；也可以分别放着，后面建模型时先合并）：

```powershell
# 用 tbtools 把多个 fasta 合并成一个（若你下载了 3 个文件）
# 先放一起：
Get-Content athaliana_[family].fa, sesamum_[family].fa, csinensis_[family].fa | Set-Content D:\[family]_sesame\data\refs\[family]_refs_raw.fa
# 或者用 tbtools 的合并工具（RPC FastaMerge.process）：
# tbtools rpc call FastaMerge.process '{"inputPaths":["a.fa","b.fa","c.fa"],"outputPath":"[family]_refs_raw.fa"}'
```

## 3.5 下载两个结构域模型（Pfam/InterPro，全物种通用，只下一次）

1. 浏览器打开 https://www.ebi.ac.uk/interpro/entry/pfam/ ；
2. 搜 `[域1]` → [核心域1] 页面 → 找 HMM 下载（Download → HMM）→ 存为 `D:\[family]_sesame\data\refs\[域1].hmm`；
3. 同样下载 `[域2].hmm`（[核心域2] 的 Pfam 模型）。

**☑️ 检查点**：用记事本打开两个 .hmm，第一行应含 `HMMER3`（如果是 HTML 乱码 = 下错了网页，找真正的 Download 按钮）。
> ⚠️ **实跑坑**：InterPro wwwapi 下载的 .hmm 实际是 **gzip 流**，直接喂 HMMER 会报 "format not recognized"。判断：看文件头字节是否为 `1f 8b`（gzip 魔数）——是则先解压再确认首行 HMMER3。解压方式：`gunzip` 不可用时用 **7-Zip 右键解压**，或 `tar -xzf`（Windows 10+ 自带）。

## 3.6 下载拟南芥蛋白组（TAIR）

1. 打开 https://www.arabidopsis.org/ ；
2. **Download → Sequences → Protein**（TAIR10 或更新版本）→ 下载 zip；
3. 解压到 `D:\[family]_sesame\data\control\`，改名 `athaliana.protein.fa`。

> **主线默认用 TAIR 蛋白组**（本节下载的 `athaliana.protein.fa`）——**第一次实验建议就按 TAIR 走，不换源**。⚠️ 替代数据源（NCBI RefSeq，实测 48,265 条）含大量可变剪接异构体，会使严格互指率虚低——若换源，13.10 实跑里的"RefSeq 48,265"口径需对应调整，且与 TAIR 计数**不可直接比较**。RBH 用拟南芥**全蛋白组**即可（recipBlast 会自己找出最优互指对）。

### 3.6.1 对照物种怎么选（⚠️ 重要，先读再动）

**对照物种 = 用于 RBH 双向比对（4.8）、OG 聚类（4.7）、系统发育树（4.10）的参考**。选择原则：**模式物种（必需）+ [目标物种]近缘（加分）**。

| 优先级 | 物种 | 与[目标物种]关系 | 用途 | 建议 |
|:--|:--|:--|:--|:--|
| 1（必需） | **拟南芥 *Arabidopsis thaliana*** | 远缘但注释最全 | 家族定义/参照物种（经典成员口径以数据库为准） | **默认必用**：注释质量高、家族研究最充分的参照（植物基因家族研究惯例）；​若你的家族已在某个近缘物种被研究得更充分，可换那个物种作主要参照 |
| 2（强烈建议） | **[目标物种]同属/同科的近缘种**（有公开基因组的优先） | 近缘 | 直系同源判定、亚家族分类更贴近真实 | NCBI 搜 [目标物种] 学名/属名看有无公开基因组；有就加 |
| 3（可选） | [目标物种]所属目内其他近缘物种（有公开基因组的） | 同目 | OG/树补充对照 | 有现成数据就加 |
| ❌ 不要用 | 与[目标物种]跨科/跨目的远缘物种（如实例中的山茶科 vs 芝麻） | 远缘 | — | 只用于数量级参考（7.3），**不参与序列比对** |

> 通俗解释：拟南芥是 [家族名] 研究最充分的**参照物种**——本教程采用的拟南芥参考集合含 15 个经典 [家族名]；注意不同数据库/注释版本对该计数的口径可能有出入，论文里写"采用 … 参考集合"即可，不要写死"定义物种=15”。拿拟南芥当参照是行业惯例；再加一个[目标物种]近缘物种，相当于"自带方言词典"，让直系同源判定和亚家族划分更贴近[目标物种]。这两层就够了。

## 3.7 可选项
- **近缘物种 CDS（Ka/Ks）**：优先 **[目标物种]同种/同属/同科**的近缘物种（由近到远）；没有就跳过 Ka/Ks（证据矩阵中为低权重支持证据，缺失不影响硬条件判定），报告注明。**不要拿模式物种（如拟南芥）或跨科的远缘物种做 Ka/Ks**（替换饱和，结果失真）——Ka/Ks 需要的是可比的直系同源 CDS，近缘标准比 3.6.1 的对照物种更严。
- **转录组（表达支持）**：有公开表达矩阵可直接查成员是否表达；原始数据处理是另一套流程，本教程不展开。

## 3.8 数据自检清单（🟢 本章出口：下载完逐项打勾）

```powershell
cd D:\[family]_sesame\data

# ① [目标物种]蛋白组条数——先看"是否像一个完整蛋白组"（例：多数二倍体植物 2-4 万条；倍性/注释策略会显著改变，0 条或 5 条 = 明显下错文件）—— 用 tbtools：
tbtools tool statFasta --inFasta genome\[Species].protein.fa
#    或 GUI：TBtools → Sequence Toolkits → Fasta Tools → Fasta Stats，选蛋白组文件
#    输出里看 Sequences 数量

# ② 基因组文件大小（几百 MB）
dir genome\*.fa*

# ③ GFF gene 行数——数量级与蛋白组相当（无固定值，明显偏少 = 可能下错/注释不全）—— 记事本打开看前几行；或用 tbtools GXF 工具统计

# ④ [家族名] 参考条数——"是否覆盖多个可靠物种/已知成员"（无固定要求；≥10 条且跨物种即可起步）
#    GUI：Fasta Stats 看 [family]_refs_raw.fa

# ⑤ .hmm 文件：记事本看第一行是否 HMMER3

# ⑥ 拟南芥条数（TAIR 约 2.7 万；用 RefSeq 则 4.8 万，口径不同属正常）：Fasta Stats 看 athaliana.protein.fa
```

**数字对不上的处理**：

| 现象 | 原因 | 处理 |
|:--|:--|:--|
| 蛋白组只有几条 | 下成了单基因文件 | 重下，找 `protein` 关键字 |
| GFF 打不开/乱码 | gz 没解压 | 右键解压 |
| .hmm 是 HTML | 下错链接 | 找官方 Download 按钮 |
| 文件名有中文/空格 | 命令全部报错 | 一律改名纯英文小写 |

## 3.9 最终目录长这样

```
D:\[family]_sesame\data
├── genome\[Species].protein.fa / .genome.fa / .gff3
├── refs\[family]_refs_raw.fa / [域1].hmm / [域2].hmm
├── control\athaliana.protein.fa
├── db\            （空，4.8 建库用）
```

---

## 3.10 自建资源完整构建教程（🔴 Level 3 高级：五个核心资源，从零复现；新人可跳过——主线用现成资源即可）

> 正文 4.1-4.8 只讲"怎么用"这些资源；本节讲"怎么造"。五个资源：**① 参考集** → **② 家族 HMM** → **③ 超家族竞争面板** → **④ RBH 库** → **⑤ 无蛋白注释时的自译蛋白组**。每项给 ① TBtools 图形界面 → ② 命令行等价 → ③ 检查点（数字不对就停下）。Python 脚本仅作"无网络/无人值守"兜底。

### 资源一：参考集整理（→ `[family]_refs_for_search.fa`）

**目的**：blastp 召回和建模都需要纯净的植物参考；原始检索会混入细菌条目（同查询会把原核同源刮进来）和冗余。

1. UniProt 网页检索：`(gene:[家族名]) AND (organism_id:[目标物种] OR organism_id:[近缘物种]) AND reviewed:true` → 导出 fasta → `[family]_refs_uniprot_raw.fa`；
2. TBtools → **Sequence Toolkits → Fasta Extract (Recommended)**：贴入物种 accession 列表，剔除细菌/冗余条目 → `[family]_refs_for_search.fa`；
3. 再抽一次拟南芥子集 → `athaliana_[family].fa`（RBH 注释用）；
4. **Sequence Toolkits → Fasta Stater** 看统计。

**☑️ 检查点**：条数是整数预期（LOG 例 20 条）；长度在家族典型区间（LOG 例 143–266 aa）；无原核 accession 开头。**命令行等价**：`python build_refs.py`（UniProt REST 下载 + 过滤）。

### 资源二：家族 HMM（→ `[family]_refs.hmm`，正文 4.1 的完整版）

1. **MSA**：TBtools → **Sequence Toolkits → Multiple Sequence Alignment**（Muscle 内嵌；或 ClustalO/MAFFT），输入 `[family]_refs_for_search.fa` → `[family]_refs.aln`；
2. **hmmbuild**：TBtools 暂无 hmmbuild 图形包装，用 HMMER 命令一行（或 2.6 兼容层）：
   ```powershell
   hmmbuild [family]_refs.hmm [family]_refs.aln
   ```
3. **自检（回 TBtools）**：**Others → Simple HMM Search**（不同版本菜单位置可能不同，搜关键词 "Hmmer Search"）：参考集 vs 新建模型 → 要求 **N/N 全部命中且 E ≤ 1e-3**——缺任何一条 = 比对有问题，回第 1 步。

**☑️ 检查点**：模型首行 `HMMER3/f`；自检 100% 命中（LOG 例 20/20，模型长 222）。**兜底**：`python build_family_hmm.py`（pyhmmer 内核，同三步）。

### 资源三：超家族竞争面板（→ `superfamily_panel/`，正文 4.3b-3 的完整版）

**目的（为什么它是"改判机器"）**：家族域模型（如 TIGR00730/PF03641）只能判定"超家族内"，分不出本家与近邻。把超家族空间**聚成簇、逐簇建 HMM**，成员归哪个簇分高——归到非本家族簇就改判剔除。

1. **收超家族空间**：用超家族级模型（[域1] 或家族所在超家族 Pfam 条目）对全蛋白组做 **Advanced Hmmer Search**（模型 ID 列表写超家族条目一行）→ 命中 ID 表 → **Fasta Extract (Recommended)** 拉出全部命中序列；
2. **聚簇**（~45 条规模人肉可行）：命中序列 + N 条参考 → **Multiple Sequence Alignment** → 按两两一致率 ≥35% 分堆 → 参考所在堆 = **cl1**，其余大堆 = **cl2 / cl3**…（脚本路线：`python superfamily_cluster_hmm.py` 自动聚类+建模）；
3. **逐簇建 HMM**：每簇各自 MSA → `hmmbuild cl1.hmm cl1.aln`（同资源二）；
4. **面板反扫**：**Simple HMM Search** 跑 N 次（hmm = cl1/cl2/cl3…，序列 = 全部成员 + 空间序列）→ 每个蛋白取 **bitscore 最高的簇**即其归属。

**☑️ 验收**：N 条参考必须全落 cl1；cl2/cl3 里应有被改判出去的近邻条目（LOG 实绩：GWHERBT 边缘 11 条、Cosmantha 的 298 aa 条目都是被 cl2 碾压式改判——"第二模型复确认会放行的错误，竞争归属能抓住"）。

### 资源四：RBH 库（→ `athaliana_db`，正文 4.8 前置）

- **GUI 一步（免手动建库）**：TBtools → **Blast → Reciprocal Blast**：A = 成员蛋白，B = `athaliana.protein.fa` → Start——TBtools **内部自动 makeblastdb**；
- **命令行（想留档时）**：
  ```powershell
  makeblastdb -in athaliana.protein.fa -dbtype prot -out athaliana_db
  blastp -query members.fa -db athaliana_db -outfmt 6 -evalue 1e-5 -max_target_seqs 1
  ```

**☑️ 检查点**：抽一个已知直系对（如 CON scaffold_3 → AtLOG3 89.7%）确认双向最优；RBH 比例在多倍体里本就低（1/4 ~ 4/15），不是错误。

### 资源五：无蛋白注释 → 自译蛋白组（"只有 GFF3+基因组"的物种，通用技能）

**目的**：有的组装官方只发布 GFF3 不给蛋白 fasta；任何这类物种都这样处理（LOG 例：Changlin40 六倍体，129,804 基因自译）。

1. **CDS 提取**：TBtools → **Sequence Toolkits → Gtf/Gff3 Sequences Extractor**：输入 gff3 + 基因组 fasta；模式选 **CDS**；**勾选每基因只保留最长转录本** → `[Species].cds.fa`；
2. **翻译**：**Sequence Toolkits → CDS to Protein Translator**（标准密码子表）→ `[Species].protein.fa`；
3. ⚠️ **翻译结果里的内部 `*` 别洗掉**——它是 S4 质控信号（含 `*` 或异常短 → boundary/fragment），提前清洗反而丢信息。

**☑️ 检查点**：蛋白表头数 = CDS 表头数；抽 3 条负链基因确认方向正确（翻译产物对家族域模型有命中即方向对）；下游注释一致性应为 ~1.0000。**兜底**：`python gff2protein.py <gff3> <genome> <prefix>`（支持 .gz 输入）。

### 六、总自检表（走到哪查到哪）

| 资源 | TBtools 检查点 | 不达标怎么办 |
|:--|:--|:--|
| 参考集 | Fasta Stater：条数、长度区间 | 回 UniProt 补下载/查过滤 |
| 家族 HMM | Simple HMM Search 反扫 N/N（E≤1e-3） | 检查 MSA 是否有条目未对齐 |
| 超家族面板 | N 参考全落 cl1；cl2/cl3 含近邻条目 | 聚类阈值 35% 上下微调重分 |
| RBH 库 | 已知直系对双向最优 | 检查输入 ID 空格/版本号 |
| 自译蛋白组 | 表头数一致；负链方向正确；S5≈1.0000 | 检查 GFF Parent-ID 链与最长转录本选项 |

### 七、坑表（本教程实跑沉淀，GUI 路线同样适用）

1. 簇模型 `.hmm` 曾落盘截断——打不开时从 `.aln.fa` 补建，别重跑全流程；
2. pyhmmer `Builder.build_msa` 第二参数必须 `plan7.Background`；MSA 必须先设 `.name`；个别簇模型 `hmm.write()` 会挂起 → **簇模型内存构建直接使用**；
3. Pfam 全库面板批量扫描用 `pyhmmer.hmmer.hmmsearch(hmms, seqs, cpus=8)` 批量接口；
4. MSA 缓存不感知序列集变化——**加新组合后必须删比对缓存**，否则 FastTree 报 tip 缺失（4.10）；
5. 多组合务必串行跑；tblastn 输出为 8 列 outfmt，解析索引 sstart=p[6]/send=p[7]（4.0.1）。

*第 3 章完。数据齐了。下一章进入正题：一步一步鉴定，每步给 CLI 命令 + GUI 路径。*

# 第 4 章 鉴定实操（主链 4.1-4.12（12 主步，含 4.2b/4.3b 等子步）+ 4.13 可选进阶；每步 CLI + GUI 双轨）

> 📌 **本章只需记住 3 件事**：① 搜索命中 ≠ 成员（先松后紧只负责捞人）；② 核心硬条件 A（家族 HMM）+ B（核心域）必须成立，C 是 QC，其余是支持证据；③ 每步看 ☑️ 检查点，卡住先查 4.0.1 再查第 6/11 章。

> **本章格式**：每步 = 做什么 → 原理 → **CLI 命令**（PowerShell 直接复制）→ **GUI▶ 路径**（TBtools 点选）→ 预期输出 → ☑️ 检查点 → ⚠️ 报错。
> **约定**：CLI 命令里 `tbtools` 指 tbtools-cli（2.5 装的）；`hmmsearch/hmmbuild` 指 HMMER（pyhmmer 内核兼容层，见 2.6）；路径用 `D:\[family]_sesame\...`，粘贴时**把路径换成你实际的**。
> 记得把每一步的重要命令存到 `D:\[family]_sesame\scripts\stepN.txt`——这是论文可复现性的硬要求。

> ### ⚠️ 最重要的一个概念：**搜索命中 ≠ 基因家族成员**
>
> HMM / BLAST 只负责"把可能的人找出来"（捞人）。
> **命中只说明"像"，不说明"是"**——真伪要靠后面的核心结构域验证、证据矩阵逐项核。
> 所以教程里每一步初筛后都说"现在只是候选，还没开始正式判定"，这不是客套，是规则。

**你现在在流程的哪一层？（每做到一步，回来看一眼）**

```text
① 找参考 ─→ ② 建家族画像 ─→ ③ 初筛候选（捞人） ─→ ④ 验证候选（看身份证）
─→ ⑤ 查漏（有没有漏人） ─→ ⑥ 综合证据（多证据复核） ─→ ⑦ 冻结最终成员
```

## 4.0 本章地图

| 步 | 层级 | 做什么 | CLI 命令 | GUI（TBtools） |
|:-:|:-:|:--|:--|:--|
| 4.1 | 🟢 | 建家族 HMM 模型（宽松参数起步） | `hmmbuild` | UGENE / EMBL-EBI 在线 |
| 4.2 | 🟢 | 全蛋白组初筛（**先松后紧**：初筛 E=1e-3） | `hmmsearch` | 同上 |
| 4.2b | 🟢 | **blastp 第二召回（HMM ∪ BLAST 取并集）** | `autoMakeBlastDb` + `blastp` | Blast → Blast Wrapper |
| 4.3 | 🟢 | 核心结构域验证 | `hmmsearch` ×2 | 同上 / InterPro 在线 |
| 4.3b-1/-2/-3 | 🔵 | **超家族交叉核对 + 邻近家族减法 + 全超家族反扫**（单域家族**条件必做** / 多域家族可选） | `hmmsearch`（超家族共有域对照 / 各邻近家族 HMM 反扫） | UGENE / CDD PSSM |
| 4.4 | 🟢 | 提取候选 + 完整性检查 | `tbtools tool extractFasta` / `statFasta` | Fasta Tools → Amazing Fasta Extractor / Fasta Stats |
| 4.5 | 🟢 | **注释一致性核对**（CDS→翻译→比对；≠ Exonerate，见正文） | `tbtools genestructure` + GFF 提取 | BioSequence Structure Illustrator → Gene Structure View |
| 4.6 | 🟢 | 查漏（**tblastn 全基因组** + 宽松复查） | `tblastn` | Blast Wrapper |
| 4.7 | 🟡 | 直系同源聚类（OG） | — | OrthoVenn3 在线 |
| 4.8 | 🟡 | RBH 双向最优比对（**直系同源的支持证据**） | `tbtools recipBlast` | Blast → Blast Wrapper |
| 4.9 | 🟡 | 家族基序（MEME） | 在线 MEME + `tbtools motif`（本地 `memerun` 为可选高级） | 在线 MEME → Amazing Optional Gene Viewer |
| 4.10 | 🟡 | 系统发育树 | `tbtools one-step` / `muscle`→`trimal`→`iqtree` + `tbtools tree` | Tree → One Step Build a ML Tree；iTOL 美化 |
| 4.11 | 🟢 | **证据矩阵汇总**（核心硬条件 + 支持证据） | 文本/Excel + `tbtools` 表格工具 | TBtools TableTools |
| 4.12 | 🟢 | 集合冻结 | 文本整理 | — |

---

### 4.0.1 防静默失败四习惯（实跑验证后固化，每条命令都遵守）

tbtools 命令"跑完但什么都没发生"是 Windows 新手最大的时间杀手。实跑总结四条习惯：

1. **执行前**：`tbtools tool-describe <命令> --json` 看参数风格（位置参数 vs `--key value` ArgsParser、命令大小写）；
2. **执行后**：`dir` 验证产物文件出现且非 0 字节；
3. **静默失败排查表**：命令大小写（`autoMakeBlastDb` ≠ `automakeblastdb`）→ 参数风格（ArgsParser 必须 `--key value`）→ ID 类型（蛋白 XP_ / 转录本 XM_ / gene 需区分）→ 输入是否 gzip → 输出路径是否存在。

4. **输出解析与 outfmt 列定义一一对应**（油茶 LOG 实测：8 列 tblastn outfmt 按 9 列索引解析 → 全部行被 `len(p)<9: continue` 静默跳过、计数 0 且无报错）——解析前打印首行列数做断言；"静默 0 结果"先核对解析/outfmt，再怀疑环境。

## 4.1 Step 1：取得家族 HMM（已有官方 HMM 直接用；没有才自建）

> **分叉（按 3.0.1 决策树）**：
> **4.1A 已有官方家族 HMM**（Pfam/NCBIFam/家族数据库）→ 下载/核对 `.hmm` 文件头 `HMMER3/f` → **直接跳到 4.2**（跳过下面 4.1B 全部自建内容）。
> **4.1B 没有官方 HMM** → 走下面自建全程（参考集 → MSA → hmmbuild）。
> 🎯 **这一关解决什么**：把已知的家族参考蛋白，加工成一张"家族画像"（HMM 文件）。
> 🧠 **只理解一个概念**：HMM = 家族画像（把参考序列对齐，记住"哪些位置经常长什么样"），建一次、反复用。
> 📥 **输入**：`[family]_refs_for_search.fa`（第 3 章备好的参考集）
> 🟢 **成功后你会看到**：`[family]_refs.hmm` 存在、记事本打开第一行是 `HMMER3/f`、自检回搜参考绝大多数命中。
> 🤔 **这个数字意味着什么**：画像越准，后面"捞人"越准。
> ➡️ **下一步**：4.2 拿画像去扫全蛋白组。
> 🧑‍💻 **想自动化的（新手可跳过看下方 GUI）**：本步命令见下，或直接走「GUI▶ 路径」。

### 原理
- **cd-hit 去冗余**：参考序列里大量近亲（>90% 相同），全部纳入会带偏画像 → 每组留代表（TBtools 无内置；参考集不大时也可跳过，影响有限）；
- **MAFFT/MUSCLE 比对**：把序列对齐到同源位点；
- **hmmbuild 建模型**：从比对算出每个位置的氨基酸概率分布 → `.hmm` 文件。

### CLI 命令（HMMER Windows；比对用 tbtools 或在线）

```powershell
cd D:\[family]_sesame\data\refs

# ① 定稿「搜索用参考集」：统一命名为 [family]_refs_for_search.fa（后面 4.2b/4.6 都引用这个名字）
#    不做 cd-hit（参考 ≤200 条时）：直接复制原文件
Copy-Item [family]_refs_raw.fa [family]_refs_for_search.fa
#    做 cd-hit（参考 >200 条时推荐；cd-hit Windows 版见 GitHub: weizhongli/cdhit releases）：
#    cdhit -i [family]_refs_raw.fa -o [family]_refs_rep.fa -c 0.9
#    Copy-Item [family]_refs_rep.fa [family]_refs_for_search.fa

# ② 多序列比对（显式命令链，产出 [family]_refs.aln）
tbtools muscle [family]_refs_for_search.fa [family]_refs.aln
#   （或用 GUI/在线 MAFFT 比对后保存为 [family]_refs.aln——只要这个文件名即可）
#   🌐 国内网络无本地 MUSCLE 二进制时，可用 EBI Job Dispatcher REST（实测 ClustalO 比 MAFFT 稳）：
#      POST https://www.ebi.ac.uk/Tools/services/rest/clustalo/run → 轮询 status → 先 GET /resulttypes/<jobid> 列类型 → 拉 fa（FASTA 比对）端点
#      ⚠️ 端点以 /resulttypes 为准（LOG 项目实测：aln-fasta 返回 400、FASTA 比对在 fa 端点；/result/<jobid>/out 是运行日志不是比对结果）

# ③ 建 HMM 模型（HMMER，2.6 装）
hmmbuild [family]_refs.hmm [family]_refs.aln
```

**GUI▶ 路径**：
- 比对：TBtools **Sequence Toolkits → Multiple Sequence Alignment**（选输入 FASTA、算法选 MUSCLE/MAFFT，输出比对文件）；或在线 MAFFT（mafft.cbrc.jp，上传→提交→下载）；
- 建模型：TBtools 无内置 hmmbuild → **UGENE**（菜单：Analyze → HMMER → Build HMM；可建模型 + 搜索）。⚠️ **EBI 在线 HMMER 只能搜索已有 .hmm，不能建模型**（见 2.6）——别在 EBI 找 Build 按钮。🍀 更简单：模型就建一次，用命令行 30 秒搞定即可。

### 预期输出
```
# hmmbuild 成功会打印：
#  HMM file:    [family]_refs.hmm
#  Model length: 342
```

### ☑️ 检查点
`[family]_refs.hmm` 存在；记事本打开第一行是 `HMMER3/f`。

### 🧪 自建 HMM 的质量验证三步（自建模型必做，LOG HMM 专项报告流程）
1. **自检（灵敏度）**：hmmsearch 回搜参考集——**绝大多数应被稳定召回**（若参考集本身异质/高度分化，个别弱成员属正常）；**已知成员大量漏掉才说明比对/建模有问题**，优先查 MSA 与参考集质量（LOG 实例 19/19，240–419）；
2. **负对照（特异性）**：搜一个最近缘外家族/同域异家族蛋白——应不命中（LOG 实例：真赖氨酸脱羧酶 CadA 完全不命中）；
3. **与超家族模型并行对比（区分度）**：同库分别用自建模型与 Pfam 超家族级模型搜参考集，自建模型的真成员 score 应显著高于旁系/假阳性、存在可分辨间隔（LOG 定量：自建 376–419 vs 假阳性 ≤194，间隔 ~180；PF03641 则为 157–171 vs 100–160 完全重叠）。
> 💡 自建特异模型后可收紧阈值（如 LOG 建议 E≤1e-20 + bit score ≥150 片段 / ≥250 完整 + domain 覆盖率 >70%）；参数表的"先松后紧"适用于初筛阶段，收紧阶段用双阈值更稳。

### ⚠️ 常见错误
| 现象 | 原因 | 解决 |
|:--|:--|:--|
| `hmmbuild 不是内部或外部命令` | 🟡 兼容层：function 没注册 / hmmbuild_win.py 不在 scripts；🟢 新人不存在此问题（UGENE/EBI 在线） | 🟡 重开终端重注册（2.6 的 function 定义），或检查 `scripts\hmmbuild_win.py` 与 pyhmmer 是否装上——Windows 无官方 hmmbuild.exe（2.6 勘误） |
| 报 `alignment has no columns` | .aln 是空的 | 比对没成功，回查 MAFFT/MUSCLE 输出 |
| 参考序列里有非法字符（大量 X） | 下载的序列质量差 | 建模型前用 tbtools statFasta 看，剔除异常序列 |

---

## 4.2 Step 2：全蛋白组初筛（hmmsearch，**先松后紧**）
> 🎯 **这一关解决什么**：用画像扫[目标物种]全部蛋白，把"可能像这个家族"的捞出来。
> 🧠 **只理解一个概念**：**现在只是"捞人"，命中 ≠ 成员**——扫出来的叫"候选"，还没开始正式判定。
> 📥 **输入**：`[family]_refs.hmm` + `[Species].protein.fa`
> 🟢 **成功后你会看到**：候选名单（芝麻 ARR-B 实跑 172 个；你的数字不同没关系）
> 🤔 **这个数字意味着什么**：候选 = "可能像"，里面混着真的和假的（后面 4.3 逐个验）。
> ➡️ **下一步**：4.2b 加 BLAST 再捞一遍，两边并集防漏。
> 🧑‍💻 **想自动化的（新手可跳过看下方 GUI）**：命令见下，或直接走「GUI▶ 路径」。

> ⚠️ **关键实战经验：初筛用宽松参数（E=1e-3），不要一上来就 E=1e-5 严格扫。**
> 理由：家族里演化分化大、结构域变弱的真成员，严格阈值直接扫丢；后面再想捞就得全基因组重跑（4.6）。**先宽松多收，靠核心域 + 证据矩阵收紧**——本教程全流程的节奏就是"先松后紧"。

### CLI 命令

```powershell
cd D:\[family]_sesame\results
mkdir 02_search
# 初筛：宽松阈值 E=1e-3（本教程操作参数，非普适标准；阈值随模型/库大小而异，见 1.8）
hmmsearch -E 1e-3 --domtblout 02_search\[family].domtbl -o 02_search\[family].hmmsearch.out D:\[family]_sesame\data\refs\[family]_refs.hmm D:\[family]_sesame\data\genome\[Species].protein.fa
#   （兼容层单线程，无需 --cpu；真实 HMMER 才用 --cpu 4）
```

**执行时间**：[目标物种] 3 万蛋白，几分钟到 20 分钟。

### 读结果 + 提取候选

```powershell
notepad 02_search\[family].domtbl
```

> ⚠️ **不要靠肉眼数固定列号**：`--domtblout`（域表）和 `--tblout`（序列表）列结构不同；HMMER 版本升级列也可能变。**安全做法：Excel 导入（分隔符选 Tab）后，按表头文字识别列**——E 值那列叫 `full sequence E-value`（域级用 `i-Evalue`），序列名列是第一列 `target name`。筛选：E 值 ≤ 0.001 → 取第一列（target name）→ 去重 → 存 `[family]_candidates.txt`。

**初筛候选数异常排查**（数量异常先查这里，不据此删/加成员）：

| 现象 | 排查 |
|:--|:--|
| 候选 0 | ① 模型首行是否 `HMMER3/f`；② 蛋白组是否真是蛋白（有 T/U 字母 = 下成 DNA）；③ E 阈值是否过严（先用 1e-3）；④ 模型是否与物种亲缘太远 |
| 候选几千 | ① 模型是否超家族级过宽（如误用 Pfam 超家族条目）；② 是否用了域模型而非家族模型；③ 蛋白组是否含大量可变剪接异构体 |

---

## 4.2b Step 2b：blastp 第二召回（HMM ∪ BLAST 取并集）
> 🎯 **这一关解决什么**：防止 HMM 漏掉"分化太大、画像对不上"的真成员——用 BLAST 从"像某个具体已知成员"的角度再捞一遍。
> 🧠 **只理解一个概念**：HMM = 对照"家族画像"；BLAST = 对照"具体蛋白"；两个角度取并集，尽量捞全（**并集只负责不遗漏，不负责判定**）。
> 📥 **输入**：参考集 + [目标物种]蛋白组
> 🟢 **成功后你会看到**：`candidates_union.txt`（并集名单）+ `candidates_union.fa`（序列）
> 🤔 **这意味着什么**：从此以后的所有步骤都用**并集名单**，别丢 BLAST 源的候选。
> ➡️ **下一步**：4.3 逐个看"身份证"。
> 🧑‍💻 **新手可跳过命令**：直接用下方「GUI▶ 路径」（Blast Wrapper）。

### CLI 命令

```powershell
cd D:\[family]_sesame\results
mkdir 02b_blast

# ① 建[目标物种]蛋白组 BLAST 库（tbtools 自动建库，底层调 makeblastdb）
# ⚠️ 参数风格（实跑确认）：autoMakeBlastDb 是 ArgsParser 引擎，位置参数会静默零输出，要用 --key value：
tbtools tool autoMakeBlastDb --inFasta D:\[family]_sesame\data\genome\[Species].protein.fa --outBase 02b_blast\[Species]_db

# ② blastp：参考 [家族名] 蛋白（4.1 的去冗余代表序列） vs [目标物种]蛋白组
blastp -query D:\[family]_sesame\data\refs\[family]_refs_for_search.fa -db 02b_blast\[Species]_db -outfmt 6 -evalue 1e-5 -num_threads 4 -out 02b_blast\refs_vs_[Species].tsv

# ③ 取 blast 命中的[目标物种]基因 ID（第 2 列 subject）→ 去重 → 02b_blast\blast_hits.txt（命令行做法，不用 Excel）
#    Get-Content "02b_blast\refs_vs_[Species].tsv" | ForEach-Object { ($_ -split "`t")[1] } | Sort-Object -Unique | Set-Content "02b_blast\blast_hits.txt"
# ④ 与 HMM 候选取并集（A ∪ B，去重）：
#    Get-Content "02_search\[family]_candidates.txt","02b_blast\blast_hits.txt" | Sort-Object -Unique | Set-Content "02b_blast\candidates_union.txt"
#    （或 tbtools 表格工具 TableTools 合并去重）
# ⑤ 提取并集序列（供 4.3 核心结构域验证用）
tbtools tool extractFasta --inFa D:\[family]_sesame\data\genome\[Species].protein.fa --inIDList 02b_blast\candidates_union.txt --outFa 02b_blast\candidates_union.fa
```

**GUI▶ 路径**：TBtools **Blast → Blast Wrapper → Several Sequences To a Big File** ✅：query 放参考蛋白、target 选[目标物种]蛋白组、输出选 Table 格式；同样把 HMM 与 blast 两份名单在 Excel 里并集。

### ☑️ 检查点
- 并集候选数一般会多于单源（具体增幅视数据；不设固定比例预期）；
- **后续所有步骤（核心域/完整性/结构/查漏）以并集名单为对象**，别丢 blast 源的候选。

### 4.2c 建 ID 桥表（candidate_id_map.tsv，protein→transcript→gene 一次性打通，后面全靠它）

做完 4.2b 并集后，把候选的 protein ID **一次性映射到 gene 层级**——4.3 到 4.12 的每一步都从这张表取 ID，不再临时猜（3.0 的 ID 三层是概念，这张表是实操）。**新手 70% 的卡壳都出在这里，务必一次做对**。

**第一步：先认清你的 GFF 是哪种 ID 体系**（三种常见，关联方式不一样）：

| 注释体系 | protein 怎么出现在 GFF | 怎么找 transcript / gene |
|:--|:--|:--|
| **RefSeq**（NCBI 下载） | CDS 行 `ID=cds-XP_...;Parent=rna-XM_...` | protein→transcript：取 CDS 行的 `Parent=`（rna-XM_…）；transcript→gene：再拿 XM_ 搜 mRNA 行取 `Parent=`（LOC…） |
| **MAKER**（自建注释常见，如油茶 CON） | protein ID **就是** mRNA ID（`maker-...-gene-0.1-mRNA-1`） | 同一个 ID 既是 protein 也是 transcript；gene = 去掉 `-mRNA-1` 后缀（`maker-...-gene-0.1`） |
| **GWH / 部分多倍体注释** | CDS 行写 `Protein_Accession=GWHPERBTxxxxx`（蛋白 FASTA 表头是另一套 ID） | protein→transcript：取该 CDS 行的 `Parent=`（如 `YC.xxG...-1A.t1`）；transcript→gene：mRNA 行的 `Parent=` |

**第二步：生成桥表**（candidate_id_map.tsv，Tab 分隔，列如下）：

| 列 | 内容 | 例 |
|:--|:--|:--|
| protein_id | HMM/BLAST 搜到的蛋白 ID | XP_020549869.1 |
| transcript_id | 蛋白所属转录本 | XM_020696012.1 |
| gene_id | 转录本所属基因 | LOC105172165 |
| is_representative | 该基因代表转录本？（Y/N，4.12 选代表用） | Y |
| source | HMM / BLAST / 并集 | HMM |

**生成方式（任选其一；推荐 B + 抽查）**：

**方式 A：手动 Excel 法（≤30 条候选时最直观，顺便理解结构）**
1. 打开 GFF（大文件用记事本能搜就行；Excel 会卡）；
2. Ctrl+F 搜第一个 protein ID（RefSeq 搜 `XP_020549869.1`；MAKER 搜 `gene-0.1-mRNA-1`；GWH 搜 `GWHPERBT000001`）——找到它的 CDS/特征行，看 `Parent=` 就是 transcript_id；
3. 拿 transcript_id 再搜 mRNA 行，`Parent=` 就是 gene_id；
4. 一条候选填一行 → 全部填完，另存为 `candidate_id_map.tsv`。
> 💡 推荐组合：**先手动做 10 条**（搞懂结构），**剩下用方式 B 批量**，两种结果在 Excel 里拼起来。

**方式 B：批量映射（推荐）**
```powershell
cd D:\[family]_sesame\results\02b_blast
# ① gene → 代表性 mRNA ID（GxfRepresentativeIds；方法名以 tbtools methods | Select-String Gxf 实测为准）
tbtools rpc call GxfRepresentativeIds.process '{"inputPath":"D:/[family]_sesame/data/genome/[Species].gff3","outputPath":"D:/[family]_sesame/results/02b_blast/mrna_ids.txt"}'
# ② 再拿 mRNA ID 列表从 GFF 提取对应 protein ID（见 4.5 的 gxffilter / Gtf/Gff3 Sequences Extractor）
# ③ protein / transcript / gene 三列拼进 Excel → candidate_id_map.tsv
```
**方式 C：完全手动核验**——A 的全程手动版，适合候选极少（<10 条）时直接照抄 GFF 行，不赘述。

**第三步：标 is_representative**
同一 gene 有多条 protein（可变剪接异构体）时：**默认选最长转录本**那条标 `Y`（4.12 用它做代表序列），其余标 `N`。⚠️ 注意区分两种用途：**4.5 验证阶段用 HMM 命中的那个转录本**（不是最长！见 4.5），**4.12 交付阶段才用代表转录本**——桥表里两列都留着，各步骤按需取。

**第四步：完成后核对（☑️ 全过再往下）**
- [ ] 行数 = 候选 protein 数（candidates_union 去重后）；
- [ ] gene_id 去重数 ≤ 行数（多个 protein 可属同一 gene，正常）；
- [ ] 每条 protein_id 在 GFF 都能找到（找不到 = 版本后缀 / 大小写 / 体系认错 → 回 3.0 处理）；
- [ ] 抽 3 条反向核对：拿 gene_id 去 GFF 搜，能回到对应 mRNA 和 protein。

**后续用途速查（每步取哪列）**：

| 步骤 | 用桥表的哪列 |
|:--|:--|
| 4.3 核心域验证 | protein_id（扫域模型） |
| 4.5 注释一致性 | transcript_id（提 CDS、genestructure） |
| 4.6 查漏 | gene_id（对照 GFF 位点） |
| 4.11 证据矩阵 | gene_id（判定主键） |
| 4.12 冻结 | gene_id（名单）+ transcript_id / protein_id（三件套提取） |

**常见错误**：① 蛋白 ID 在 GFF 里搜不到——先确认体系（第一步的表）；② 一个 gene 三条 protein 只填了一行——gene 行去重后数量骤减是正常的，别把 protein 行删了；③ `is_representative` 全填了 Y——每个 gene 只能有 1 个 Y。

## 4.3 Step 3：核心结构域验证（判定核心）
> 🎯 **这一关解决什么**：候选逐个查"身份证"——核心结构域齐不齐，把"长得像但缺关键域"的排除。
> 🔑 **ID 提醒**：本步候选是 **protein ID**（XP_…）；4.5 genestructure 要 **mRNA ID**、4.12 冻结用 **gene ID**——三层关系见 3.0 身份证图；protein→mRNA→gene 的转换：从 GFF 的 CDS 行 `Parent=` 取 mRNA、从 mRNA 行 `Parent=` 取 gene，或 `tbtools rpc call GxfRepresentativeIds.process`（4.5 示例）。
> 🧠 **只理解一个概念**：家族成员 = 核心域齐全；只有共享域 = 近邻家族（不是本家族）；都没有 = 噪声。
> 📥 **输入**：并集候选序列 + `[域1].hmm` + `[域2].hmm`
> 🟢 **成功后你会看到**："核心域齐全"名单（芝麻 18 个；数量不设固定预期，0 或异常多才回查）
> 🤔 **这意味着什么**：核心域齐全才进入"候选成员"队列；其他的记入排除/近邻表。
> ➡️ **下一步**：4.4 提序列 + 查蛋白完整性。
> 🧑‍💻 **新手可跳过命令**：直接用下方「GUI▶ 路径」（Amazing Fasta Extractor + InterPro 在线 / venn2 交集）。

### 做什么
对每个候选：① 提取蛋白序列；② 分别用 [域1]（[核心域1]）和 [域2]（[核心域2]）模型扫描；③ 核心域都命中 = 进入**"高可信候选成员集合"**——还不是最终冻结成员（后面 4.4-4.12 的 QC/查漏/支持证据后才定稿）。

### CLI 命令

```powershell
cd D:\[family]_sesame\results
mkdir 03_domains

# ① 候选序列直接用 4.2b 的并集文件（HMM ∪ BLAST；不要再退回 HMM 单源！）
#    02b_blast\candidates_union.fa 已在 4.2b ⑤ 生成

# ② 两个结构域分别扫（先松后紧：先宽松 E=1e-3 多收，真伪在 4.3b/4.11 收紧）
hmmsearch -E 1e-3 --tblout 03_domains\[域1].tblout D:\[family]_sesame\data\refs\[域1].hmm 02b_blast\candidates_union.fa
hmmsearch -E 1e-3 --tblout 03_domains\[域2].tblout D:\[family]_sesame\data\refs\[域2].hmm 02b_blast\candidates_union.fa

# ③ 分别取名单（--tblout 输出用 .tblout 后缀；--domtblout 才用 .domtbl）
#    [域1].tblout 第 1 列 = 有[核心域1]的候选；[域2].tblout 第 1 列 = 有 [核心域2]的候选
#    Excel 各筛一次：按 `full sequence E-value` 列筛 ≤ 1e-3（见 1.8），取 `target name` 列 → 去重 → 存 [域1].txt / [域2].txt
# ④ 求交集（两个名单都出现 = 核心域齐全）
#    Excel：新表放两边 ID → 或用 tbtools 表格工具 TableTools
```

**GUI▶ 路径（等价做法）**：
- ① 提取：TBtools **Sequence Toolkits → Fasta Tools → Amazing Fasta Extractor**：选蛋白组 → initialize → 把候选 ID 列表粘进去 → Start，输出候选序列文件 ✅（官方 README 确认此功能）
- ② 核心域（**批量，不要逐个传**）：**UGENE 内置 HMMER 批量扫描**——把候选序列一次性扫 [域1]/[域2] 两个模型各一次，导出两个命中名单 → Excel 取交集。⚠️ **InterPro 在线只用于单蛋白疑难复核**（把 172 个候选逐个传 InterPro 是巨大的工作量，不是主批量路线）；
- ③④ 交集：Excel 两个工作表各放一份 ID，用 VLOOKUP/COUNTIF 找两边都有的（或 tbtools `venn2` 一步出交集：`tbtools venn2 --List1 [域1].txt --List2 [域2].txt --label1 [核心域1] --label2 [核心域2] --graph 03_domains\venn.svg --prefix 03_domains\venn`——交集 ID 会单独输出 ✅）。

### 预期输出

```
全候选:     86
核心域齐全:   21（示例数字，不设普适范围）
仅[核心域1]:   30        ← 疑似 [超家族近缘成员]
无[核心域1]:   35        ← 噪声
```

### ☑️ 检查点
- 核心域齐全数量**不设普适范围**（油茶 20 仅为示例）；数量仅作 QC 触发信号——例如 0 或异常大量时回查输入/ID/模型/注释，**不据此保留或删除成员**；
- 核心域名单里的 ID 能在 GFF 搜到。

### ⚠️ 常见错误
| 现象 | 原因 | 解决 |
|:--|:--|:--|
| 核心域为 0 | .hmm 是 HTML 或候选序列为空 | 检查 PF*.hmm 第一行；检查 extractFasta 输出条数 |
| 核心域 100+ | [域1] 太宽（很多同超家族蛋白都有）| **只 [核心域1] 不算 [家族名]**，必须看"核心域齐全"数 |
| extractFasta 提示未找到 ID | 命名带版本后缀/大小写 | 名单里统一去掉 `.数字` 后缀 |

---

## 4.3b-1 超家族交叉核对（防超家族成员混入）

### 为什么必须有这一步
[家族名]（或更普遍地，你的家族）常常属于一个更大的**超家族**：超家族所有成员共有一个核心域（[核心域1]），而 [家族名] 额外特有 [核心域2]（[超家族近缘成员] 与同超家族其他成员只有 [核心域1]）。如果只拿 [家族名] 家族 HMM 扫描，阈值稍松就会把**同超家族的其他成员**扫进候选——它们"长得像 [家族名]"但不是 [家族名]。
> 4.3 的核心结构域验证已在防这件事（核心域齐全才留下），但**单靠自家 HMM 看不出"误收的是哪个近邻家族"**；用超家族共享域（[域1]）+ 近缘家族模型交叉扫一遍，把混入者定性排除，才能避免"超家族成员冒充 [家族名]"的经典错误（油茶排坑：OG0002391 曾混入非 [家族名] 的单域成员）。

### CLI 命令

```powershell
cd D:\[family]_sesame\results
mkdir 03b_cross

# ① 对并集候选分别扫超家族共享核心域 + [家族名]特有核心域（宽松 E=1e-3）
hmmsearch -E 1e-3 --tblout 03b_cross\[域1]_all.tblout D:\[family]_sesame\data\refs\[域1].hmm 02b_blast\candidates_union.fa
hmmsearch -E 1e-3 --tblout 03b_cross\[域2]_all.tblout D:\[family]_sesame\data\refs\[域2].hmm 02b_blast\candidates_union.fa

# ② 进阶对照（可选但推荐）：建一个近缘家族（[超家族近缘成员]）的 HMM
#    PlantTFDB 下载 [超家族近缘成员] 参考序列 → 同 4.1 三步（去冗余→比对→hmmbuild）→ typeA.hmm
#    然后：hmmsearch -E 1e-3 --tblout 03b_cross\typeA.tblout typeA.hmm 02b_blast\candidates_union.fa
```

### 判读（Excel 汇总）

| 模式 | 含义 | 处理 |
|:--|:--|:--|
| [核心域1] + [核心域2] 核心域 | [家族名] | 留下（进 4.4） |
| 仅 [核心域1] 无 [核心域2] | **优先判为近缘/不完整候选**（也可能是截短蛋白、退化成员、注释错误、假基因化——4.6 会进一步查） | 记入 [超家族近缘成员]补充表/待复核；**除非后续证据证明属目标家族，否则不直接计入** |
| 均无 | 噪声 | 排除 |
| 在 [超家族近缘成员] HMM 下强命中、[家族名] 核心域弱命中 | **超家族误收信号** | 回 4.6.1 证据链复核，多半排除 |

### ☑️ 检查点
- 留下的"核心域齐全"名单里，**没有只在近缘家族模型下强命中的成员**；
- 被排除的"仅 [核心域1]"候选全部登记（这是 [超家族近缘成员] 课题的素材）。

### 4.3b-2 邻近家族减法复核（🔵 条件必做：**单域家族必做**；多域家族 ⚪ 可选审计）

超家族交叉核对（上面）用的是"共享域 vs 特有域"的结构判定；**减法复核更进一步**：拿演化关系最近的家族做"诱饵"，对候选池做**竞争性检验**——真成员应命中家族模型远强于诱饵（或在 CDD 全库 PSSM 下无任何邻近家族特异域）。

**到底要不要做（WOX 项目实测教训，ISSUES_LOG P19）**：

| 你家族的硬条件 | 减法复核 | 依据 |
|:--|:--|:--|
| **单域家族**（无多域硬条件兜底） | **必做** | ARR-B 教程中减法"零增量"是因双域条件更强；WOX 是单域家族，不做则 2 条 HD-Zip IV（START+MEKHLA+Homeobox 四域）混入，靠减法才定位剔除 |
| 多域家族（如双域齐全硬条件） | 可选审计（冻结后补做即可） | 双域条件在逻辑上已强于减法，减法排除面全部落在双域已排除集内 |

**Windows 实现（无 hmmbuild 时）**：NCBI **CDD 全库 PSSM**（Batch CD-Search，db=cdd, smode=full）对最终成员做竞争性检验——覆盖 START/MEKHLA/KNOX/BEL/bZIP 等全部邻近家族，效力等同且覆盖面比手建诱饵 HMM 更广（WOX 实例：21 成员中 10 条获 specific 级 Homeodomain、11 条仅 superfamily 级但无任何邻近家族特异域，全部维持判定；2 条呈 HD-Zip IV 四域架构被剔除并留档案）。有 hmmbuild 时亦可建各邻近家族诱饵 HMM 做竞争性 E 值判别。

**判读与记录**：成员出现邻近家族特异域（specific 级 CDD 命中）或诱饵 HMM 占优 → 排除并单列剔除档案（证据链：域架构 + 同源性区间 + 树长枝位置）；全部通过 → 集合可辩护性提升。**写进报告的表述**："以 CDD 全库 PSSM/诱饵 HMM 对成员做邻近家族竞争性检验，无成员呈邻近家族特征（单域家族此项为必要步骤）"。

### 4.3b-3 全超家族 HMM 反向扫描（🔵 条件必做：**单域家族必做**；多域家族强烈建议）

> **教训（用户审读后指出，LOG 项目实测）**：只补一个"本家族官方特异模型"反扫（LOG 项目最初只补了 IPR005269 的 TIGR00730）**只能验证"成员是不是本家族"，检不出"成员其实是超家族里另一个家族"**——邻近家族成员在"本家族模型"下也会有弱命中，单靠一个模型无法区分。

**彻底做法（单域家族必做，多域家族强烈建议）**：把超家族**结构化拆分**，逐个家族反扫候选池——

1. **列超家族成员家族清单**：依据 InterPro 超家族树 / 域架构 / 文献，列出与目标家族同属一个超家族或共域的全部邻近家族（LOG 实例的 PRH 超家族 ≈ LOG 自身 + PpnN/MND 嘌呤嘧啶核苷酸酶 + 广义 PRH/核苷酸酶 + 赖氨酸/鸟氨酸脱羧酶等）；
2. **每个家族建 HMM**：各自自建（有 hmmbuild / pyhmmer plan7.Builder），或取官方模型（LOG 例：本家族 IPR005269→NCBIFam TIGR00730；邻近家族取各自 InterPro/NCBIFam/Pfam 签名，赖氨酸脱羧酶即 Pfam PF03641 原版）；
3. **全部模型对候选池反向全扫**：同一候选池分别过每个家族 HMM，记录各模型 E 值/score；
4. **竞争判定**：真成员 = 仅被**本家族 HMM** 显著强命中（score 间隔清晰）；被**任一邻近家族 HMM 更强命中**的候选 = **超家族混入嫌疑** → 复核域架构与系统发育位置 → 排除并留档案（域架构 + 同源性 + 树位证据链）。

**Windows 实现**：无 hmmbuild 时用 NCBI CDD 全库 PSSM 按家族分类解读（**替代性正交筛查策略，非"等效力"**——CDD PSSM ≠ HMMER profile HMM ≠ 竞争簇 HMM，三者不视为相互独立的票）；有 hmmbuild/hmmer 时逐家族 hmmbuild + hmmsearch 竞争扫描。**报告表述**："将超家族拆分为 N 个成员家族并分别构建 HMM 对候选池反向扫描；成员均仅被本家族模型显著命中，无混入（附反扫家族清单与各自命中数）"。

**✅ 实测案例（油茶 LOG，S3y 两层反筛）**：第一层 **Pfam 全库面板**——30,134 个家族 HMM 批量反扫候选池（pyhmmer hmmer.hmmsearch，每组合约 30 秒）：超家族级 PF03641 命中 CON 3 / GWHERBT 22 条（E≤1e-5）；成员最佳归属直接抓出混入（CON 两条 397/352 aa "成员"最佳归属 K_trans 动力蛋白 → 剔除；GWHERBT 013587→Pol_BBD、033078→PB1/RVT_3、110910→Ribosomal_L39 等）。第二层 **自建聚类 HMM 面板**——超家族空间序列（参考 + 超家族模型全部命中）按 35% 对一致性贪心聚类成簇，每簇各自建 HMM，全部成员竞争性归属（取 bitscore 最高的簇）：LOG 例 45 序列 → 3 簇 [37,5,3] → 簇 HMM 220/298/156 aa → CON 那条曾被官方 TIGR00730 支持的 scaffold_11 被归入独立近邻簇、GWHERBT 7 条边缘被改判 cl2/cl3 簇。**核心教训："第二模型复确认"会放行的错误（单点模型互相背书），"竞争性归属"能抓住**——反筛的价值不在多一个模型，而在把候选放回超家族空间里选边站队。

## 4.4 Step 4：提取成员序列 + 蛋白完整性初检
> 🎯 **这一关解决什么**：把核心域齐全的成员序列提出来，检查蛋白"健康度"（有没有内部终止密码子 `*` = 假基因化信号、有没有大量 `X`）。
> 🧠 **只理解一个概念**：内部 `*` = 翻译提前断掉 = 这个"基因"可能已经坏了（假基因化）——记下它走边界决策，不直接删。
> 📥 **输入**：核心域齐全名单 + 蛋白组
> 🟢 **成功后你会看到**：成员蛋白文件（条数 = 核心域成员数），无内部 `*`
> ➡️ **下一步**：4.5 核对注释靠不靠谱。
> 🧑‍💻 **新手可跳过命令**：用 GUI「Fasta Extractor / Fasta Stats」。

### CLI 命令

```powershell
cd D:\[family]_sesame\results
mkdir 04_integrity

# ① 提取核心域成员序列
tbtools tool extractFasta --inFa D:\[family]_sesame\data\genome\[Species].protein.fa --inIDList 03_domains\[family]_dual_domain.txt --outFa 04_integrity\[family]_members.fa

# ② 统计每条序列的常规指标（长度、GC 等；重点看有没有 * 行）
tbtools tool statFasta --inFasta 04_integrity\[family]_members.fa

# ③ 查内部终止：在结果目录里搜序列文件中的 "*"
#    PowerShell 一行统计每个序列里的星号数量（把序列按行查）：
Select-String -Path 04_integrity\[family]_members.fa -Pattern '*' -SimpleMatch | Select-Object -First 10
```

**GUI▶ 路径**：
- ① TBtools **Fasta Tools → Amazing Fasta Extractor**（同上）；
- ② TBtools **Fasta Tools → Fasta Stats**（选中成员文件，看每条序列长度/是否含异常字符）；或用记事本搜索 `*`。

### ☑️ 检查点
- 无**内部**终止密码子（末端单个 `*` 属正常翻译终止，可去掉再比较）；有内部 `*` 则记下该成员走 4.6.1/4.6.2 证据链，不直接删；
- 序列条数 = 核心域成员数。

**提取条数不对排查**：

| 现象 | 原因 | 解决 |
|:--|:--|:--|
| 提取条数 < 名单数 | ID 带版本后缀 / 大小写不一致 | 统一去 `.数字` 后缀，或 `FastaIDSimplifier` |
| 提取条数 = 0 | ID 列表格式错（空行/空格） | `Get-Content ids.txt | Where-Object { $_.Trim() } | Set-Content ids_clean.txt` 再提取 |
| 提取条数 > 名单数 | 蛋白组里有重复 ID | `FastaIDRenamer` 去重，或手动检查覆盖 |

---

## 4.5 Step 5：注释一致性核对（Windows 版）
> 🎯 **这一关解决什么**：核对注释靠不靠谱——GFF 里的 CDS 能不能翻译出和注释蛋白一致的序列（发现版本错位/提前终止）。
> 🔑 **ID 转换三步走（新手 70% 卡在这，先读）**：protein ID（XP_…）→ 从 GFF 的 CDS 行 `Parent=` 取 **mRNA ID**（rna-XM_…）→ 从 mRNA 行 `Parent=` 取 **gene ID**。**genestructure 的 idList 只认 mRNA ID**（不是蛋白 ID）；或直接 `tbtools rpc call GxfRepresentativeIds.process` 一步映射（见下 CLI）。
> 🧠 **只理解一个概念**：这是**数据质量控制**，不是"基因座真实存在"的证据（Windows 无 Exonerate，本步 ≠ Exonerate，论文如实写）。
> 📥 **输入**：`[Species].gff3` + 成员名单
> 🟢 **成功后你会看到**：全部成员 4 项通过（identity/coverage/无内部终止/结构正常）
> ➡️ **下一步**：4.6 回头查漏。
> 🧑‍💻 **新手可跳过命令**：用 GUI「Gtf/Gff3 Sequences Extractor → Translate → Two Sequences Blast」。

### 原版（服务器/Linux 环境）做了什么
油茶流程用 **Exonerate** 做 protein-to-genome 回拼：把蛋白序列直接比到基因组 DNA 上，验证基因座在基因组里真实存在、外显子/内含子剪接正确、零移码。这是基因座真实性方面最强的验证。

### 本步骤的定位（⚠️ 先读这段）
Windows 环境没有 Exonerate。本步骤实际验证的是：**GFF3 注释的 CDS 能否翻译出与注释蛋白一致的蛋白**（注释一致性核对）。它能发现：注释蛋白与 CDS 不一致（版本错位）、内部提前终止（假基因化信号）、明显异常的基因结构。
> **它不能完全替代 Exonerate**：注释本身错误（exon 边界错/转录本错/漏 exon）、或基因组上存在更合理匹配位点时，仅凭"CDS 与注释蛋白一致"看不出来。**给新人的一句话：这一步检查的是"这份 GFF 自己前后一不一致"，不是"这个基因一定真实存在"。** 论文方法节**如实写「GFF 注释一致性核对（CDS→翻译→比对）」，不要写成 Exonerate 等价**；审稿人追问时说明 Windows 环境限制 + 本步骤实际验证的内容。

### 主流程（只走 CDS 路径）
> ⚠️ **验证阶段必须用 hit protein 所属的转录本**（protein → 其 transcript → 其 CDS → 翻译 → 与**这个** protein 精确比较）。**不要拿"最长转录本"去对命中的另一个 isoform**——会误报注释不一致（两个不同剪接体的 identity 可能只有 70-80%，那是 isoform 差异不是注释错误）。"最长转录本"只是 4.12 交付阶段的代表选择原则。
```text
GFF3 → 按【hit protein 所属的转录本】提取 CDS → 翻译 → 与这个蛋白比对
        （记录 identity / coverage / 内部终止 / 长度差 4 个指标）
```

### CLI 命令

```powershell
cd D:\[family]_sesame\results
mkdir 05_structure

# 0️⃣ 先把全量 GFF 切成成员子集（165MB 全量 GFF 直接跑 genestructure 会超时被杀——先切再跑，实测 253 行 3.1 秒出图）：
#    gxffilter 会保留目标 ID 所在行 + 它下面的所有子特征（mRNA/exon/CDS），参数以 tool-describe 为准：
tbtools tool-describe gxffilter --json          # 先看本机契约（命令名/参数可能随版本变化）
tbtools gxffilter D:\[family]_sesame\data\genome\[Species].gff3 05_structure\[family]_mrna_ids.txt 05_structure\[family]_subset.gff3
#    → 输入1：全量 GFF；输入2：成员 mRNA ID 列表（每行一个，来自 4.2c 桥表的 transcript_id 列）；输出：子集 GFF
#    ☑️ 验证子集：记事本打开 [family]_subset.gff3，应只含成员的 gene/mRNA/exon/CDS 行，且能看到完整的 9 列结构
#    ⚠️ 没有 gxffilter 时的备选（PowerShell 按 gene ID 筛行）：
#    $ids = Get-Content 05_structure\[family]_mrna_ids.txt
#    Get-Content D:\[family]_sesame\data\genome\[Species].gff3 | Where-Object { $l = $_; $ids | Where-Object { $l -match $_ } } | Set-Content 05_structure\[family]_subset.gff3

# ① 基因结构图——注意：genestructure 的 idList 要求 **mRNA/转录本 ID**（RefSeq 里是 rna-XM_...），不是蛋白 ID
#    先建 gene → 代表性 mRNA 映射（或在 4.2c 桥表里已有 transcript_id 列直接取用）：
#    tbtools rpc call GxfRepresentativeIds.process '{"inputPath":"D:/[family]_sesame/data/genome/[Species].gff3","outputPath":"D:/[family]_sesame/results/05_structure/[family]_mrna_ids.txt"}'
#    然后拿【子集 GFF】画图（不要拿全量！）：
# 参数风格以本机为准：先 `tbtools tool-describe genestructure --json` 确认是位置参数还是 --key value
# （本教程按位置参数写：<gff> <ids> <out>）
tbtools genestructure D:\[family]_sesame\results\05_structure\[family]_subset.gff3 05_structure\[family]_mrna_ids.txt 05_structure\[family]_structure.svg

# ② 提取【每个 hit protein 所属转录本】的 CDS（先做 protein→transcript 映射，见 4.2c ID 桥表；GUI 见下；产出 CDS，不是 gene 区 DNA！）
#    → 05_structure\[family]_members.cds.fa
#    ⚠️ 不要在这步就取"最长转录本"——那是 4.12 交付阶段的事，验证阶段必须用命中的那个转录本

# ③ 翻译（当前仓库契约：RPC CdsToProtein.process；'cds2protein' 不是顶层 CLI 命令）
tbtools rpc call CdsToProtein.process '{"inputPath":"D:/[family]_sesame/results/05_structure/[family]_members.cds.fa","outputPath":"D:/[family]_sesame/results/05_structure/[family]_members.cds.pep.fa"}'

# ④ 与注释蛋白逐条双向比对，记 4 个指标（identity/coverage/内部终止/长度差）
tbtools twoSeqBlast 05_structure\[family]_members.cds.pep.fa 04_integrity\[family]_members.fa 05_structure\cds_vs_anno.tsv --prog blastp
```

**GUI▶ 路径**：
- ① **Graphics → BioSequence Structure Illustrator → Gene Structure View (From GFF3/GTF)**：GFF + 成员 ID → Start ✅；同菜单 **Amazing Optional Gene Viewer**（树+motif+结构三联图，4.9 用）；
- ② **Sequence Toolkits → Gff3/GTF Manipulator → Gtf/Gff3 Sequences Extractor** ✅：GFF → Initialize → Feature 选 **CDS**、ID 按转录本（Parent/mRNA）→ 基因组 FASTA → 输出每个转录本 CDS（不含内含子）；
- ③ 翻译：**Fasta Tools → Translate**；
- ④ 比对：**Blast → Blast Wrapper → Two Sequences Blast**（或 `tbtools twoSeqBlast`）。

### 判读标准（4 指标，写进报告）

| 指标 | 通过标准 | 说明 |
|:--|:--|:--|
| identity / coverage | **优先要求 exact match（100%）**；若蛋白与 GFF 来源不同，记录实际 identity/coverage 并说明来源差异 | CDS 翻译蛋白与注释蛋白一致 |
| 内部终止 | 无内部 `*`（允许末端一个终止符） | 不提前终止 |
| 长度差 | CDS 翻译蛋白长度与注释蛋白一致（允许末端 stop 差异） | 长度差大 = 转录本选错/含内含子 |
| 基因结构图 | 结构正常 | 多外显子基因有正常剪接模式（油茶成员 5-11 外显子） |

**☑️ 检查点**：全部成员 4 项通过 = 注释一致性核对通过；个别失败 → 走 4.6.1/4.6.2 证据链与边界决策。

### ⚠️ 常见错误
| 现象 | 原因 | 解决 |
|:--|:--|:--|
| Gtf/Gff3 Sequences Extractor 输出空 | Feature 选错/没 Initialize | Feature 选 CDS，上下游填 0 |
| genestructure 图里某成员没有 | ID 格式差异 | 用 GFF 实际 ID（带 mRNA 后缀）重试 |
| CDS 翻译出 * / 长度差大 | 选成 gene 区（含内含子）或最长的不是主转录本 | 重选 Feature=CDS；多转录本取最长 |
| 某成员在 GFF 中不存在 | ID 映射错误 | 回 4.4 核对命名（去版本后缀） |

> 📝 **报告里怎么写**：方法节写「基因结构以 GFF 注释一致性核对验证：按转录本提取 CDS → 翻译 → 与注释蛋白比对（identity/coverage/无内部终止）。该步骤在 Windows 环境实现，验证注释内部一致性，**不能视为对 Exonerate protein-to-genome 比对的完全替代**」。其余证据按证据矩阵记录。

---

## 4.6 Step 6：查漏（tblastn 全基因组 + 宽松复查）
> 🎯 **这一关解决什么**：回头扫一遍，防止漏掉注释里没有的成员（假基因化/未注释/退化成员）。
> 🧠 **只理解一个概念**：tblastn 只是"定位器"——告诉你相似性落在基因组的哪里，**不自动代表"这是完整基因"**（新位点要按完整链条复核，见 4.6.1/4.6b）。
> 📥 **输入**：参考蛋白 vs `[Species].genome.fa`（+ 宽松 hmmsearch 复查）
> 🟢 **成功后你会看到**：tblastn 命中位点表 + 宽松扫描差集
> 🤔 **这意味着什么**：强命中落在已知成员位点 = 一致；新位点 = 进"待复核"队列，不过完证据链不收/不删。
> ➡️ **下一步**：4.7-4.10 支持证据（🟡 Level 2，可选）→ 4.11 证据矩阵汇总。
> 🧑‍💻 **新手可跳过命令**：用 GUI「Blast Wrapper」跑 tblastn。

严格/宽松扫描都基于**注释蛋白组**——注释漏掉、或已假基因化的基因（内部终止/截短/移码，演化中正在丢失功能的拷贝）不会出现在蛋白组里，只能靠**蛋白序列去扫基因组 DNA（tblastn）**捞出来。
> **定位澄清（重要）**：tblastn 是「基因组层面的**查漏定位器**」，不是完整基因模型构建器——它只告诉你蛋白相似性落在基因组哪个位置（可能有内含子的局部 exon 样区域），**不会自动给出正确的植物基因模型**。在缺少独立蛋白-基因组拼接/基因模型证据时，**不得仅凭 tblastn 命中直接纳入最终成员集合**。
> 实战经验：这套"HMM+blast 取并集"方法偶尔会漏，漏的主要是假基因化/未注释候选——tblastn 把它们**定位**出来；它们进入「待验证 genomic locus」列表后，仍需独立基因模型验证 + 蛋白/结构域证据 + 证据链复核，才能决定是否纳入（油茶 378.17 就是典型：弱域/低表达/基因座真实，最终按边界成员处理）。**本教程 Windows 环境能做到"发现潜在漏网基因座"，但不保证对未注释新位点完成完整 gene model 重建**——遇到这类新位点，如实记录为 unresolved 或在有服务器/Linux 环境时用 Exonerate 类工具补验。

### CLI 命令（两条通道都跑）

```powershell
cd D:\[family]_sesame\results
mkdir 06_salvage

# ① 通道 1：tblastn 全基因组扫（蛋白→基因组 DNA，含未注释区）
#    先建[目标物种]基因组 DNA 库（一次）
makeblastdb -in D:\[family]_sesame\data\genome\[Species].genome.fa -dbtype nucl -out 06_salvage\genome_db -parse_seqids
#    用成员/参考蛋白扫全基因组
tblastn -query D:\[family]_sesame\data\refs\[family]_refs_for_search.fa -db 06_salvage\genome_db -outfmt 6 -evalue 1e-5 -num_threads 4 -out 06_salvage\tblastn_genome.tsv

# ② 通道 2：更宽的 hmmsearch 复查（E=1e-1，比初筛再松一档）
hmmsearch -E 1e-1 --domtblout 06_salvage\[family]_loose.domtbl -o NUL D:\[family]_sesame\data\refs\[family]_refs.hmm D:\[family]_sesame\data\genome\[Species].protein.fa
#    （-o NUL：Windows 的空设备，丢弃人读输出；Linux 用户别改成 /dev/null 以外的东西——本教程是 Windows）
```

### 判读

| 通道 | 怎么判 |
|:--|:--|
| **tblastn** | 强命中落在**已知成员位点** = 一致 ✅；落在**新位点** = 潜在未注释/假基因化候选 → **按下方「新位点复核链条」处理** |
| **hmmsearch 宽松复查** | Excel 按表头筛选 E 值 ≤ 0.1 → 与 4.3 名单差集 = 新候选 → 核心域复验（同 4.3 命令） |

**🧭 新位点复核链条（tblastn 新位点按此走，不许直收直删）**：
新位点 → 蛋白相似性命中 → 六框翻译找完整 ORF——**ORF 完整性应根据目标家族蛋白典型长度、核心域覆盖、起止密码子、内部终止/移码与 GFF/RNA 证据综合判断；"≥120 aa" 只是 LOG 实例的经验过滤值，不是通用基因判定标准**（短蛋白家族要相应下调）→ 核心域（[核心域1]+[核心域2]）→ [家族名] 家族 HMM → 注释/结构检查 → OG/RBH/系统发育支持 → 才考虑新成员。⚠️ E 值显著只说明"曾有过同源序列"，不说明"现在有完整基因"（LOG 实例：4 个 E≤1e-35 强座位六框翻译后均无完整 ORF → 判假基因化位点不计成员）；"能翻译全长"只证明非明显截短，**不直接等于正常 [家族名]**，有内部终止/移码/截短 → **边界候选**。

### 新候选证据链定性（4.6.1 前导）
新候选（无论哪个通道来的）一律走 4.6.1 证据链，**不允许直接收或直接删**。

### 4.6b 终极查漏：绕过注释直接扫基因组（🔴 **高级**：仅当正常流程结果存疑时进入——新人跳过）

**什么时候用（先做注释质量体检，命中任一就去）**：
① 正常流程成员数远低于近缘物种预期（如二倍体只有 2-3 条，而近缘二倍体普遍 7-10 条）；
② 出现明显截断/垃圾蛋白模型（如注释只给出 46 aa 的"CDS"，而家族典型长度 150-270 aa）；
③ 多倍体/自建注释（MAKER 等 ab initio 管线）——这类注释**不假定完整**。

> ⚠️ **为什么必须绕过注释**：正常流程（4.1-4.6）假定"注释完整"——只扫注释蛋白组。但**自动注释器会系统性漏基因**（见下），漏掉的分化拷贝在蛋白层面根本不存在，HMM 扫蛋白组永远够不着。油茶 CON 实测：正常流程只鉴定出 3 个 LOG，绕过注释重扫又找回 5 个（= 8 座位，与二倍体预期对上）。

**流程（Windows/纯 Python 实测；四步：扫 → 重建 → 校验 → 分类）**：

**S10a 六框翻译 HMM 扫描（先定位"信号在哪"）**
1. **六框翻译**：每条序列 6 个阅读框全翻译；大基因组纯 Python 逐密码子太慢 → **numpy 向量化密码子查表**（bytes→uint8→码表索引→氨基酸），分钟级完成；
2. **分块**：HMMER 单目标序列硬上限 100,000 残基 → 按 ~90 kb 翻译残基一块、块间 ~500 aa 重叠切分（坐标映射加回偏移）；
3. **扫描**：家族 HMM + 官方第二模型双扫，全基因组规模下收紧阈值（E≤1e-10）控制假阳性；
4. **聚类成基因座**：同序列上间隔 ≤5 kb 的命中合并（**5 kb 是 LOG 实例经验值，按基因密度调整**），对照注释基因区/冻结名单/已知伪基因座分类。

**S10b HSP 链 → 剪接模型重建（关键：把"信号"变成"基因模型"）**
- 用家族参考蛋白（如拟南芥 LOG1-9）对候选座位做 **tblastn**，拿到带完整坐标的 HSP 链（`-outfmt "6 qseqid sseqid pident length evalue bitscore qstart qend sstart send"`——**务必包含 qstart/qend**，否则没法把 HSP 映射回参考蛋白坐标）；
- 按参考蛋白坐标把一串 HSP **拼接成剪接模型**：HSP 覆盖的基因组区段 = 外显子，HSP 之间 = 内含子；按 GT-AG 剪接信号/相邻外显子边界重建 mRNA；**每个外显子用自身 HSP 的读码框**（相位随坐标变化，frames 常混合 1/2/3；相邻不同 frame 的 HSP 不得合并，间隔 ≤60 bp 且同 frame 才并）；
- 重建 mRNA 翻译成蛋白（用标准密码子表，⚠️ 自写翻译脚本务必 64 密码子全表断言，防 GCN/ACN 类笔误）。
> ⚠️ **提取窗口用 ±6kb，别用 ±1kb**（S11 实测教训）：±1kb 会把 **5′ 外显子截掉**（连阳性对照成员都被截到 ~105 aa 误判"模型缺陷"）——**"候选但模型缺陷（core 命中、基序在位、0 终止子、长度 <120 aa）"必须先换宽窗口重提取排除提取伪影，才能定性为缺陷/残留**（±6kb 复验曾一次找回 7 个被误杀的真座位）。**两层区分（S11y 定稿）**：宽窗口（±6kb，必要时 ±15kb）复验后 ORF 恢复增长 = 提取伪影，按真基因重建；**复验后 ORF 仍不增长 = 组装/注释层面 5′ 外显子真实缺失**（或 HSP 无信号），维持截短片段定性，不再追。

**S10c 在【重建 CDS】上做 ORF + 家族基序校验（不是六框残基上！）**
- ORF 完整性：无内部终止子、长度达家族典型区间；
- **家族特异催化/保守基序**：在重建的剪接 CDS 上查（如 LOG 的 `PGGxGTxxE` 催化核心 + `MHxRK` 催化组氨酸上下文——LOG 实例 4 条恢复成员全部携带，见下）；
> ⚠️ **为什么不能在六框翻译上查基序**：**家族基序可能恰好跨剪接边界**（分落在两个外显子，如 LOG 的 `IALPG | GGYGTLEE`）——六框翻译本来就该在剪接处断开，搜基序对真实剪接基因**系统性假阴性**，对假基因残迹反而有效。真伪判据只能看重建 CDS / 参考基序区段的基因组比对，不是六框残基。

**S10d 分类（双层裁决）**
| 结果 | 判定 |
|:--|:--|
| 完整 ORF + 基序完整（重建 CDS 上） | **真漏检新成员** → 收为成员，标注"**基因组层面恢复**"，论文单独列示 |
| 基序区被终止子截断 / 同源性大幅掉档（如 34-52%） | 退化假基因残留（论文里可写为假基因化证据） |
| 无注释/无 RNA 证据 | 只能证明"座位存在"，不能判定"完整基因"——如实标注 |

**自动注释器为什么漏（5 种情况，任选其一就漏）**：
1. **选错剪接位点** → 移码或提前终止，蛋白模型烂掉（CON 的 1089.4 就给了个 46 aa 垃圾 CDS）；
2. **漏掉一个外显子** → 只留下一个短 CDS；
3. **外显子边界偏移 1-2 bp** → 拼接后基序被拆散；
4. **把完整 ORF 拆成两个间区 ORF** → 长度太短，HMM 域 E 值不显著；
5. **间区基因缺乏 RNA-seq/同源证据** → 被基因预测器直接忽略（CON 3 个新座位全在注释间区）。

> 🧭 **为什么偏偏是这类家族（根本机制）**：自动注释器不是"找全所有真实基因"，而是"在给定证据下找最可能的基因模型"——当 RNA-seq / 同源蛋白 / 手工校对不足时，统计先验主导，而先验偏爱：**长 ORF、典型剪接位点、有表达证据、有同源支持、不与间区/重复序列打架**。跨外显子基序的基因（如 LOG）在每条证据链上都低于检测限：junction read 稀疏（低表达时可能 0-1 条）、短 ORF 统计上像噪声被过滤、无同源 hints 失去锚定、冷门家族在公共数据库和预测器训练集里双重欠代表。**证据弱 × 先验不利 × 阈值不友好 = 假阴性相乘放大**——对这类基因，预测器"不预测"反而比"预测错"得分更高。
> 两个层面的假阴性必须分开归因：**没有家族特异 HMM = 下游鉴定问题**；**注释器漏跨外显子基因 = 基因结构预测问题**（缺 RNA-seq/同源证据的直接结果）——两者叠加才导致"一个二倍体只有 2-3 个成员"的表观结果。

**判读（补充）**：HMM 直扫（42 基因座）召回远高于 tblastn（4 基因座）——**对高度歧化成员，六框直扫才是查漏底牌**；但"注释外命中 ≠ 新成员"必须先走 S10b-S10d。⚠️ **不要用"模型坐标覆盖并集"替代 ORF/基序验证**（LOG 六倍体实测：伪基因座覆盖 116 ≥ 真基因 115，降解残迹在六框上累积命中会伪造高覆盖）。

> 🧭 **座位数 > 成员数 = 常态，不是矛盾**（LOG E8：Changlin40 98 基因座中仅 12 个落在注释基因上、成员 8 个）。裁决用**双层证据**：① 坐标比对——座位窗与成员坐标逐一求交；② 蛋白水平独立打分——注释座位解析出 mRNA → 蛋白对家族模型打分，无命中者 = 信号只在六框 ORF（假基因化/移码片段）→ 排除。座位级对应 + 蛋白级否决缺一不可。

> ✅ **CON 实例（LOG，2026-10-09 四组合 S10 定稿）**：正常流程 3 个 → 绕过注释六框 + HSP 剪接重建 + ORF/基序校验 → **找回 5 个**（CONnewLOG4-8：全部携带完整催化装置 MHxRK + PGGxGTxxE、0 内部终止子；其中 CONnewLOG8 原被判"伪基因"，逐外显子读码框修正后重建为 231 aa 完整 ORF）→ **CON 库存 = 3 注释 + 5 基因组恢复 = 8 座位**。5 个中 1 个在注释基因内部（注释只给 46 aa 垃圾 CDS）、3 个全在注释间区、1 个原"伪基因"升格；对照验证：已知真成员正确判为真基因、已剔除的判为残留——判据区分度好。四组合合计 S10 恢复 25 个座位（CON 5 / GWHERBT 7 / Cosmantha 2 / Changlin40 11），均过官方 TIGR00730 复确认（40/40）。⚠️ 重建模型写论文前建议：有 RNA-seq 拉回贴剪接位点确认外显子边界，或至少以"基因组层面证据支持的同源座位"单独列示。
## 4.6.1 Case Study：退化域边界成员怎么判（油茶 378.17 完整案例——**实例化判定表，不是通用固定五项清单**）

> ⚠️ 下面 5 项证据是油茶 378.17 当年的完整实录，**不是每个边界候选都必须凑齐这 5 项**（尤其 RBH 属 🟡 Level 2、功能注释非主线矩阵）。**通用边界规则**：① 核心归属条件仍成立（或单域家族 A 成立）；② 存在退化/异常（弱域、短蛋白、0 表达等）；③ 至少有 1-2 个**独立**证据支持保留（结构完整 / 同源 / 官方模型命中等）；④ 没有明确反证 → **boundary**。

> **这是全教程最重要的案例**：查漏捞出一个「家族模型强命中、[核心域1]完好、[核心域2]退化、低/零表达」的候选时，怎么定性别慌。油茶 378.17 的完整证据链如下，照同样的步骤处理你自己的边界候选：
对每个重点怀疑对象收集 5 项证据：

```powershell
# 假设新候选 Si99g00001：
# 证据1 家族模型强度：在 [family]_loose.domtbl 里看它的 E 值
Select-String -Path 06_salvage\[family]_loose.domtbl -Pattern "Si99g00001" | Select-Object -First 2
# 证据2 各域 E 值（[域1]_loose / [域2]_loose 里查）
# 证据3 结构核对：同 4.5（CDS 提取→翻译→比对）
# 证据4 与拟南芥 [家族名] 的 blastp 最优命中（做完 4.8 后回填）
# 证据5 功能注释：eggNOG-mapper 在线（bioinformatics.embl.de）贴序列 → 是否落在 [家族相关通路]
```

**判定表（每候选填一张）**：

| 证据 | 通过标准 | 实测 | 过？ |
|:--|:--|:--|:--|
| 1 家族模型 | E < 1e-10（强） | | ☐ |
| 2a [核心域1] | E < 1e-3（见参数表） | | ☐ |
| 2b [核心域2] | E < 1e-3 即算"存在"（退化也算） | | ☐ |
| 3 结构核对 | CDS 全长翻译、无内部终止 | | ☐ |
| 4 RBH | best hit 是拟南芥 [家族名] | | ☐ |
| 5 功能注释 | [家族相关通路] | | ☐ |

### 4.6.2 边界成员决策树

```
新候选证据齐了吗？
├─ 证据3（注释一致性）失败 → 先查 ID/转录本/注释版本（QC 排查）→ 能解释则修复 → 仍失败但 A/B 成立且有 1-2 个独立证据 → **unresolved/boundary**；明确破坏（如 A/B 复核不过）→ exclude
├─ 证据1/2 弱（域退化）但 3/4/5 过 → 收为【边界成员】：纳入+标注 boundary
├─ 全过 → 标准成员
└─ 只有单域 → 排除（记 [超家族近缘成员]候选）
```

**原则**：拿不准**宁可收为边界并标注，不要直接删**；收了就要如实标注，不能悄悄混进标准成员。

### ☑️ 检查点
成员总数**不设普适区间**（避免"答案先验污染"）；数量明显偏离已发表同源家族/近缘物种时，对照文献、其他注释版本、组装完整性**解释差异**（不补数、不删数）；每个新增成员都有证据链记录。

---

*4.1-4.6 完成：你已经有"核心域 + 结构核对通过 + 查漏"的成员集合（含可能的边界成员）。下一步：直系同源聚类和 RBH——把"像 [家族名]"升级为"确实是 [家族名] 的直系同源"。*

## 4.7 Step 7：直系同源聚类（OG，在线 OrthoVenn3）

> 🟡 **Level 2 支持证据步骤（可先跳过；第一次做可先跳过，想做扎实的论文级鉴定再看）**：本步骤**不会改变 Level 1 的核心判定规则**（A+B 硬条件 + C QC 已在 4.1-4.6 完成）；作用是提高可信度、解释边界成员、提供论文证据。

### 做什么
把「[目标物种]候选 + 拟南芥蛋白组（必需）+ [目标物种]近缘物种蛋白（可选）」一起聚类，验证每个[目标物种]候选的直系同源归属（至少与拟南芥 [家族名] 同簇为佳）。注意：物种特异扩张 / 基因丢失 / 高度分化 / 数据库采样不均时，目标成员形成**自己的 OG 而无拟南芥成员，不自动等于假成员**——需结合 RBH、系统发育等其他证据；**OG 始终是支持证据而非硬条件**。

> ⚠️ 对照物种选择见 3.6.1：拟南芥必用；与[目标物种]跨科/跨目的远缘物种**不参与聚类**。

### 为什么用在线
OrthoFinder 无 Windows 版；**OrthoVenn3**（orthovenn3.bioinfotoolkits.net）提供在线 orthology/cluster 分析（全鼠标操作），可作为同源支持证据——注意不同工具的聚类算法与参数不完全相同，结果按支持证据解读。tbtools 的 `quickFamily`（refPep+familyIds+queryPep → 同源鉴定）可作补充。

### 操作步骤（全程鼠标）
1. 打开 https://orthovenn3.bioinfotoolkits.net/ → 注册/登录；
2. **Create Analysis** → 上传两个蛋白文件：
   - [目标物种]成员（`04_integrity\[family]_members.fa` + 4.6 新增成员合并）
   - 拟南芥蛋白组（`control\athaliana.protein.fa`）。⚠️ 两种模式：**正式分析传完整蛋白组**（结果可作直系同源判定支持证据）；仅当服务上传限制时才传 [家族名] 子集，**子集模式只能称 homology/reference clustering，不作独立直系同源判定依据**
   - 建议选 "OrthoVenn (standard)" 模式（**不要选 fast 模式**——fast 聚类更粗，支持证据力弱）；
   - 任务失败常见原因：文件含非法字符、序列名含空格/重复——重命名后重传；
3. 提交，等待任务完成（半小时到几小时，可关页面，会用邮件/页面通知）；
4. 结果页 → **Orthologous clusters** 表 → 找每个[目标物种]成员所在的簇 → 看该簇是否同时含拟南芥 [家族名]；
5. 导出簇表（Download）存到 `results\07_ortho\`；
6. 用 Excel VLOOKUP 把每个成员的 OG ID 填进 4.11 证据矩阵的 **E_OG** 列。

### ☑️ 检查点
- 优先观察成员是否与已知家族参考形成合理 OG；若形成**物种特异 OG 而无拟南芥成员，不自动排除**，转入 RBH/树等其他支持证据复核；
- 孤立簇（只有[目标物种]自己）或与无关家族同簇 → 回 4.6.1 证据链人工复核。

### ⚠️ 常见问题
- 非模式物种名识别：OrthoVenn3 按上传文件自动建簇，不依赖物种库，上传即用；
- 全蛋白组太大超出上传限制（一般几万条内 OK）：传拟南芥 [家族名] 子集即可。

---

## 4.8 Step 8：RBH 双向最优比对（tbtools recipBlast 一步完成）

> 🟡 **Level 2 支持证据步骤（可先跳过）**：本步骤**不会改变 Level 1 的核心判定规则**（A+B 硬条件 + C QC 已在 4.1-4.6 完成）；作用是提高可信度、解释边界成员、提供论文证据。

### 做什么
双向最优比对：[目标物种]**全蛋白组** ↔ 拟南芥**全蛋白组**，互为最佳命中（互指）作为**直系同源的支持证据**。
> ⚠️ **RBH 必须在两个物种的完整蛋白组之间计算**；成员候选只用于**最后筛选** RBH 结果，**不作为反向搜索数据库**——否则目标物种的旁系拷贝缺失会让拟南芥被迫指回成员，制造假互指（RBH 定义被改变）。
注意：互指是直系同源的启发式判定，**不单独证明严格的一对一直系同源**（植物基因组普遍有 WGD 与旁系扩张，最佳命中可能只是其拷贝之一）。**tbtools 的 `recipBlast` 一步完成双向 + 互指**（底层调 NCBI blastp）。

### CLI 命令

```powershell
cd D:\[family]_sesame\results
mkdir 08_rbh
cd D:\[family]_sesame\results\08_rbh
# 注意：recipBlast 输出由命令在当前目录生成（先建目录再 cd）

# ① 先确认本机契约（v1.4.23 为位置参数 <query.fa> <subject.fa> <outPrefix>；参数形态一律以本机为准）：
tbtools tool-describe recipBlast --json

# ② 双向都在【完整蛋白组】上跑：query = [目标物种]全蛋白组，subject = 拟南芥全蛋白组
tbtools recipBlast D:\[family]_sesame\data\genome\[Species].protein.fa D:\[family]_sesame\data\control\athaliana.protein.fa rbh

# ③ 看结果（正反向 blast 表 + 互指对都在当前目录，先 dir 看实际文件名）
dir
# ④ 按成员名单筛选互指对（成员只用于筛结果，不参与建库）：
#    从互指对文件里，只保留 query 在【成员名单】（4.11 证据矩阵的 gene_id / protein_id）里的行；
#    PowerShell 一行筛（把成员名单换成你的）：
#    Get-Content rbh_best_hits.tsv | Where-Object { $m = $_; Get-Content ..\..\04_integrity\[family]_members.txt | Where-Object { $m -match $_ } } | Set-Content rbh_members_only.tsv
#    或 Excel：成员名单一列 + 互指对一列 → VLOOKUP 匹配
# ⑤ 逐成员记录：best hit 是否 AtLOG？是否互指？→ 填 4.11 证据矩阵的 F_RBH 列（Y/N/?，见 4.11 每列来源表）
```

⚠️ **命令契约以当前版本为准**：recipBlast 在 v1.4.23 为**位置参数**形态（`<query.fa> <subject.fa> <outPrefix>`），不同版本可能不同——**一律先 `tbtools tool-describe recipBlast --json` 确认本机接口**，输出文件名/位置以 tool-describe 为准，不要照抄固定参数名。reciprocal best hits 对是核心结果（正反向各一份 blast 表 + 互指对）。
> 🔧 **若 recipBlast 静默空跑（0 输出 0 报错）**：先 `tbtools tool-describe recipBlast --json` 确认参数签名；再 `tbtools tool-validate recipBlast <query> <subject> --json` 预检（会提示缺参）；输出文件名不是预期时先 `dir` 看实际文件名；仍异常则见 **13.10 历史记录**（v1.3.0 位置参数未绑定缺陷的 BLAST+ 手动退路，1.4.x 已修，仅作参考）。

**GUI▶ 路径：走 10.10（推荐，一步双向）**：TBtools **Blast → Reciprocal Blast**：A = [目标物种]**全蛋白组**、B = 拟南芥**全蛋白组** → Start（内部自动建库）→ 结果含双向表 + 互指对，再按成员名单筛选（步骤见 **10.10**）。
- 备选（10.4 的 Blast Wrapper 手动法）：Blast Wrapper 正反各跑一次，Excel 判互指——正向每个成员取 **bitscore 最优**（并列/近似并列人工复核），反向查该命中是否反指回同一成员 = 互指。

### 判读
| 结果 | 含义 | 处理 |
|:--|:--|:--|
| [目标物种]成员 best hit 是拟南芥 [家族名] 且互指 | 直系同源**支持** ✅ | 记入记录表 |
| best hit 是 [家族名] 但不互指 | 可能是旁系同源 | 记录，报告说明 |
| best hit 完全不是 [家族名] | 可疑 | 回 4.6.1 证据链复核（若是拟南芥同超家族其他成员 = 超家族混入信号，结合 4.3b 结果一起看） |

### ☑️ 检查点
**不设固定 RBH 通过率**：WGD、旁系扩张、注释不全会使互指比例偏低。逐成员记录 best hit 与互指情况；低比例仅作整体 QC 信号，不作为成员排除标准。**若严格互指率 <10%，先核对拟南芥数据源（TAIR vs RefSeq），再下结论**。

### ⚠️ 常见错误
| 现象 | 原因 | 解决 |
|:--|:--|:--|
| `blastp 不是内部或外部命令` | BLAST+ 没装/没在 PATH | 回 2.7 |
| recipBlast 报格式错 | query 文件混入非蛋白序列 | 用 4.4 的成员文件，先 statFasta 确认 |
| 结果表为空 | 拟南芥序列名格式问题 | 换 `twoSeqBlast` 先测一对 |

---

## 4.9 Step 9：家族保守基序（MEME 在线发现 + tbtools 画图）

> 🟡 **Level 2 支持证据步骤（可先跳过）**：本步骤**不会改变 Level 1 的核心判定规则**（A+B 硬条件 + C QC 已在 4.1-4.6 完成）；作用是提高可信度、解释边界成员、提供论文证据。

### 做什么
MEME 在成员蛋白里**从头找保守基序**，验证成员携带家族特征（[核心域1]相关 + [核心域2]相关基序）。这是论文标配图（基序分布图）的素材。

### ① 在线发现基序（meme-suite.org）
1. 打开 https://meme-suite.org/ → 注册/登录；
2. **MEME** → 上传 `[family]_members.fa`（含 4.6 新增成员）；参数：
   - motif 数量 `10`；宽度 Min 6 / Max 50；出现方式默认（**以上为本实例起始参数，非通用标准**——成员 <10 条时 motif 调到 5-8，成员 >50 时调到 15-20）；
3. 提交 → 等结果（几分钟到几小时，记下任务 ID）；
4. 结果页看 motif 显著性（本实例曾观察到 E<1e-20 的显著基序；**本教程不把该值作为通用成员判定阈值**——且 MEME 的 E 值与 HMMER 的 E 值不可直接比较，报告里分开写）→ **下载 meme XML 文件**（`meme.xml`）→ 存 `results\09_meme\meme.xml`。

### ② tbtools 画基序分布图（读 meme.xml）

```powershell
cd D:\[family]_sesame\results\09_meme
# 参数顺序以 `tbtools tool-describe motif --json` 为准；报参数错先 describe
tbtools motif meme.xml 04_integrity\[family]_member_ids.txt motif_pattern.svg 2000 1200
# 第二参数 = 成员 ID 列表(每行一个 ID; 契约非序列文件——MotifCli 按 ID 从 meme.xml 画对应序列)。
# 无现成 ID 列表时，用 PowerShell 从 members.fa 提 ID（Windows 没有 grep/sed）：
#   Get-Content [family]_members.fa | Where-Object { $_ -like ">*" } | ForEach-Object { $_.Substring(1) } | Set-Content [family]_member_ids.txt
```

**GUI▶ 路径（同图可视化，还能叠树）**：
- TBtools **Graphics → BioSequence Structure Illustrator → Amazing Optional Gene Viewer** ✅（官方 README 确认，输入 = Newick 树 + MEME XML + GFF）——一次出「树 + 基序 + 基因结构」三联图，是基因家族论文的黄金标准总览图（油茶 Fig1 就是这风格）。

### ☑️ 检查点
- MEME 结果用于确认成员集合呈现一致的家族保守模式（**不设「≥5 个基序」作为成员资格阈值**；无显著基序最多触发人工复核）；
- 至少一个基序与家族特征相关（**以下 motif 编号及功能解释仅属 ARR-B 示例：MEME-1/2=DNA 结合区、MEME-4=[核心域1] 区；通用流程只记录 motif presence/significance，不预设 motif 编号**）；
- 若无显著基序 → 成员集合值得重新质疑（回 4.3 查核心域判定）。

---

## 4.10 Step 10：系统发育树（tbtools 一键建树）

> 🟡 **Level 2 支持证据步骤（可先跳过）**：本步骤**不会改变 Level 1 的核心判定规则**（A+B 硬条件 + C QC 已在 4.1-4.6 完成）；作用是提高可信度、解释边界成员、提供论文证据。

### 做什么
把「[目标物种]成员 + 拟南芥 [家族名]（必需）+ [目标物种]近缘物种 [家族名]（可选）」一起建进化树：① 再次确认归属（成员应位于 [家族名] 预期分支、与参考序列形成合理拓扑；异常长枝 / 跑到邻近家族 / 独立异常分支 → 复核，**单系非硬性期待**）；② 为后续亚家族分类铺路。

> ⚠️ 对照物种选择见 3.6.1；与[目标物种]跨科/跨目的远缘物种不作为[目标物种]建树的对照。

### CLI 命令（tbtools 内置一键链 muscle/trimal/iqtree）

> ⚠️ **重建树前删比对缓存**（LOG 实测）：序列集从 N 扩到 N' 后用旧比对文件跑 FastTree 会报 `target not in this tree`/tip 缺失——缓存文件（如 `tree_set.aln.fa`）不感知序列集变化，**新增组合后必须删除重建**：`Remove-Item 10_tree\*.aln* -ErrorAction SilentlyContinue`。

```powershell
cd D:\[family]_sesame\results
mkdir 10_tree

# ① 组装输入：[目标物种]成员 + 拟南芥成员文件（若你只有全蛋白组，先 extractFasta 出 [家族名] 子集）
tbtools tool extractFasta --inFa D:\[family]_sesame\data\control\athaliana.protein.fa --inIDList at_[family]_ids.txt --outFa 10_tree\at_[family].fa
#    （at_[family]_ids.txt = 拟南芥 [家族名] 成员 ID 列表：可从 3.10 资源一的 athaliana_[family].fa 提取，或按文献/PlantTFDB 拟南芥条目整理；若没有现成列表，也可用全部拟南芥成员蛋白建树，只是树会大很多）
Get-Content 04_integrity\[family]_members.fa, 10_tree\at_[family].fa | Set-Content 10_tree\[family]_tree_input.fa

# ② 建树——⚠️ Windows 速览：
#    GUI 主方案：TBtools → Tree → One Step Build a ML Tree（稳定，推荐）
#    CLI 备用（⚠️ 实验性）：tbtools-cli 的 OneStepBuildATree 在 Windows 下
#    IQ-TREE 阶段存在上游管道 stderr 阻塞问题，可能长时间挂起——
#    卡死时：先 Ctrl+C，再清残留进程 `Get-Process iqtree -ErrorAction SilentlyContinue | Stop-Process`，
#    然后改用分步直链（muscle→trimal→iqtree）重试，或切 TBtools GUI 建树（两种都行）。
# JSON 的 options 字段名以 `tbtools methods | Select-String OneStep` 实际输出为准（可能叫 ultrafast/ufboot）
tbtools rpc call OneStepBuildATree.process '{"inputPath":"D:/[family]_sesame/results/10_tree/[family]_tree_input.fa","outputPath":"D:/[family]_sesame/results/10_tree","options":{"ultraFastBS":true,"threads":4}}'

# 若上面方法参数名不符，用分步直链：
# tbtools muscle [family]_tree_input.fa 10_tree\aln.fa          （比对）
# tbtools trimal 10_tree\aln.fa 10_tree\aln.trim.fa          （修剪；若 tbtools trimal 不可用，用系统 trimal 全路径或跳过修剪直接 iqtree）
# tbtools iqtree 10_tree\aln.trim.fa 10_tree\out --ufboot 1000 （建树；⚠️ UFBoot 必须 ≥1000）
```

**GUI▶ 路径**：
- 建树：TBtools **Tree 菜单 → One Step Build a ML Tree**（选输入 FASTA → 输出目录；内部即 MUSCLE+IQ-TREE）⚠️（菜单名以你的版本为准，关键词 "One Step" / "ML Tree"）；
- 树美化：把输出的 `.treefile` 上传 **iTOL 在线**（itol.embl.de）或本地 FigTree 打开，最终导出论文级树图。

### 看结果
| 文件 | 内容 |
|:--|:--|
| `*.treefile` | 树文件（Newick） |
| `*.iqtree` | 报告（最佳模型，方法节引用，如 JTT+F+I+R3） |
| `*.contree` | 共识树（画图用这个） |

### ☑️ 检查点
- `.treefile` 生成；记下 `.iqtree` 里的最佳模型名；
- 检查成员是否位于 [家族名] 预期分支/亚家族附近；孤立、长枝或位置异常的成员进入人工复核（系统树为支持证据，非硬门槛）。

---

## 4.11 Step 11：证据矩阵汇总（核心交付物）
> 🎯 **这一关解决什么**：把所有证据汇总成一张表——审稿人问"凭什么说它是 [家族名]"，答案全在这张表。
> 🧠 **只理解一个概念**：**核心归属条件（A 家族 HMM + B 核心域）必须成立；C 注释一致性是数据质量控制；其余 D-K 是支持证据——不数票、不设固定阈值。**
> 📥 **输入**：4.3-4.10 的全部结果
> 🟢 **成功后你会看到**：`verification_matrix.tsv`，每行一个成员 + 判定（standard/boundary/unresolved/exclude）+ 理由
> ➡️ **下一步**：4.12 冻结。
> 🧑‍💻 **新手可跳过命令**：Excel 建表即可。

汇总 4.3-4.10 的结果成一张表——**审稿人问"凭什么说它是 [家族名]"，答案全在此表**。

**做法（Excel 最直观）**：建 `verification_matrix.tsv`（Excel 另存为 Tab 分隔），列如下：

| 基因ID | A家族HMM | B核心域 | C注释一致性 | D结构 | E_OG | F_RBH | G系统树 | H基序 | I_KaKs | J_表达 | K查漏 | 判定 | 理由 |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| Si01g12345 | Y | Y | Y | Y | Y | Y | Y | Y | - | 无 | 无新增 | standard | 硬条件全过，E/F/G/H 积极 |
| Si99g00001 | Y | Y | Y | Y | Y | N | ? | Y | - | 0 | 新候选 | boundary | [核心域2] 退化、无互指、0 表达 |
| ... | | | | | | | | | | | | | |

- **Y** = 该项通过；**N** = 未过；**?** = 待复核；**-** = 未做。**`-`（主动不做，如无近缘 CDS）与 `?`（做了但结果不确定）不能混用**；
- 判定（证据矩阵，见 1.5）：**核心归属条件 A（家族 HMM）+ B（核心域）必须成立；C（注释一致性）为数据质量控制；综合 E/F/G/H 等支持证据 → standard / boundary / unresolved / exclude 四分类。不使用固定票数阈值**。

**每一列从哪来、怎么判（A-K 对照表）**：

| 列 | 从哪来 | Y 的标准 |
|:--|:--|:--|
| A 家族 HMM | 4.2 的 `[family].domtbl` | E < 1e-3（见 1.8） |
| B 核心域 | 4.3 的 [域1]/[域2] 交集 | 多域家族：双域齐全；单域家族：单域 + 4.3b-2/-3 通过 |
| C 注释一致性 | 4.5 的 `cds_vs_anno.tsv` | identity/coverage ≥95% 且无内部终止（跨版本比对允许 <100%，报告说明） |
| D 结构 | 4.5 结构图 | 结构正常 |
| E_OG | 4.7 簇表 | 与拟南芥家族成员同簇；**物种特异 OG 记 `?` 不记 N** |
| F_RBH | 4.8 互指表 | 互指 = Y；不互指 = N；best hit 非家族 = `?` |
| G 系统树 | 4.10 树 | 位于家族分支 = Y；长枝/异常 = `?` |
| H 基序 | 4.9 MEME | 有家族特征基序 = Y |
| I_KaKs | 4.13.1 | 有近缘 CDS 才填；无数据 = `-` |
| J_表达 | 3.7 | 有表达数据才填；无数据 = `-` |
| K 查漏 | 4.6 | 无新增 = `-`；有新候选 = 记来源并复核 |

> 🟢 **Level 1（只走 4.1-4.6 + 本步）的输出 = 初步成员集合（Preliminary gene set）**：**A（家族 HMM）+ B（核心域）= 成员硬条件必须通过；C（注释一致性）= 数据 QC，三态（PASS / REVIEW / FAIL）**——C 出问题先排查数据（ID/版本/注释，见 4.5），可解释则修复、无法解释但不构成反证 → REVIEW（不自动剔除）、明确破坏且 A/B 不成立 → FAIL 排除。查漏无新增。通过者可作 preliminary 名单。
> 🟡 **Level 2（补 4.7-4.10 支持证据后）的输出 = 论文级最终集合（Paper-grade final set）**：再加 OG/RBH/树/基序交叉印证。
> 写报告/论文时把两者说清（"初步鉴定 N 个 → 支持证据复核后定稿 M 个"），避免"最终成员"被误读。
- Ka/Ks 可选项做法：`tbtools tool dnDsCalculate --inAln <密码子比对.fa> --outPairwiseKaKs <out.tsv>`（需成员 CDS + 近缘物种 CDS 的密码子比对——**密码子比对必须按 CDS 阅读框，不能直接用蛋白比对**）；无数据就 "-"，不影响判定。

**表格工具**：TBtools **TableTools**（17 个表格工具：选列/排序/转置/合并，GUI 路径 Sequence Toolkits → Table Tools ⚠️）或 `tbtools` 下 TableTools.* RPC 方法，可辅助处理和表。

### ☑️ 检查点
每行 **A（家族 HMM）+ B（核心域）全 Y**——**多域家族**；**单域家族：A（家族特异/可靠域模型）全 Y + 超家族竞争排除通过（4.3b-2/-3）+ 结构/同源支持满足判定**（B 不重复计算，见 1.5）。**C（注释一致性）为数据质量 QC**（失败先排查 ID/转录本/注释版本，能解释则修复，不能解释但有生物学证据 → boundary/unresolved，明确破坏才 exclude）；支持证据列如实记录（Y/N/-）。**所有行人工复核**（无法判定的记入待复核清单，不静默丢）。

---

## 4.12 Step 12：集合冻结（**阶段冻结 / 最终冻结**两档）
> 🎯 **这一关解决什么**：定稿——成员 + 基因坐标 + 来源汇总成总表，导出最终蛋白序列。
> 🧠 **只理解一个概念**：**两档冻结 = 阶段冻结（Freeze 1：Level 1 主链完成，出 `preliminary_gene_set.tsv`）与最终冻结（Freeze 2：Level 2 支持证据完成，出 `final_gene_set.tsv`）**——任何一档冻结后，该档分析以这张表为准、不再改动（要改 = 重跑该档下游 + 说明理由）。
> 📥 **输入**：证据矩阵 + GFF 坐标 + 成员名单
> 🟢 **成功后你会看到**：`preliminary_gene_set.tsv`/`final_gene_set.tsv`（行数 = 成员数）+ 对应层级 `*_representative_protein.fa`（每基因一条代表蛋白）
> 🤔 **这意味着什么**：🎉 鉴定完成。数量偏离近缘物种/文献时对照解释，**不补数不删数**。
> 🧑‍💻 **新手可跳过命令**：Excel 合并即可。

### 做什么
把**当前层级**的成员 + 基因坐标 + 来源标注汇总成一张总表，并导出每基因一条代表蛋白。此后**该层级的分析以这张表为准，不再改动**。**代表序列选择：默认取最长、完整且经 4.5 验证通过的编码转录本；若命中的 isoform 更适合保留则记录理由**（见 3.0 约定③）。**交付命名统一为三件套（见 3.0 约定）**：🟢 Level 1 → `preliminary_gene_set.tsv` / `preliminary_representative_transcript.tsv` / `preliminary_representative_protein.fa`；🟡 Level 2 → `final_gene_set.tsv` / `final_representative_transcript.tsv` / `final_representative_protein.fa`。（流程中的 `[family]_members.fa` 是候选中间文件，不是最终交付。）

### CLI 命令

```powershell
cd D:\[family]_sesame\results
mkdir 12_final

# ① 从 GFF 提取所有基因的坐标（染色体/起/止/链向）→ 用 tbtools 的 GXF 工具
# ⚠️ 该 RPC 默认 featurePattern=cds；要 gene 位置必须显式指定 gene；方法名以 `tbtools methods | Select-String Gxf` 实测为准：
tbtools rpc call GxfToGenePos.process '{"inputPath":"D:/[family]_sesame/data/genome/[Species].gff3","outputPath":"D:/[family]_sesame/results/12_final/all_genes_pos.tsv","chrLenPath":"D:/[family]_sesame/results/12_final/chrlen.tsv","featurePattern":"gene"}'
# ② Excel：把成员名单 join 坐标表（VLOOKUP）→ preliminary/final_gene_set.tsv
#    具体：新表放基因坐标（①的输出）→ 加一列 VLOOKUP 按 gene_id 匹配成员名单的判定列（standard/boundary）
#    → 再补 source 列（从 4.11 证据矩阵的来源列，或 hmm_dual_domain 之类标注）
#    → 存 preliminary/final_gene_set.tsv（按层级；join 前先确认成员名单 ID 与 GFF gene ID 格式一致——都去版本后缀，见 3.0/13.2）
# ③ 三件套映射（gene → 代表 transcript → 代表 protein ID → 提 FASTA）——【用 4.2c 的 ID 桥表，不用重新建映射】：
#    ⚠️ gene ID 不能直接去 protein.fa 提序列（protein.fa 的 ID 是蛋白 XP_…，不是 gene！）——
#    打开 candidate_id_map.tsv（4.2c 生成的），筛出 is_representative=Y 的行：
#    → 这一行的 transcript_id 列 = representative_transcript.tsv 的内容
#    → 这一行的 protein_id 列 = 提取 FASTA 要用的 ID 列表
#    （没有桥表时的兜底：GxfRepresentativeIds 取代表性 mRNA → 再按 mRNA 取 protein ID，同上两步）
#    → 存 representative_transcript.tsv + representative_protein_ids.txt（每行一个 protein ID）
$proteinIds = "12_final\preliminary_representative_protein_ids.txt"   # 每行一个 protein ID（XP_…，不是 gene ID！）
$reprFa     = "12_final\preliminary_representative_protein.fa"
tbtools tool extractFasta --inFa D:\[family]_sesame\data\genome\[Species].protein.fa --inIDList $proteinIds --outFa $reprFa
# ☑️ 核对：extractFasta 输出条数 = gene_set 行数（每基因 1 条代表蛋白）；抽 3 条 ID 与桥表一致
```

**GUI▶ 路径**：
- ① TBtools **Gff3/GTF Manipulator** 系列（Gff3 To Gene Pos / Gff3 Statistics）⚠️；
- ② Excel 完成（VLOOKUP）；
- ③ Amazing Fasta Extractor。

### final_gene_set.tsv 模板（核心交付物）

```
gene    chr    start    end    strand   status   source   og_id   rbh_best_hit
Si01g12345   Chr1   100000   105000   +   standard   hmm_dual_domain   OG1   AtARR1
Si99g00001   Chr5   8880000  8895000  -   boundary   myb_degenerate_low_expr   OG1   AtARR12
```

### ☑️ 最终检查点
1. 行数 = 最终成员数。**数量范围仅用于发现明显异常，不得作为成员保留/删除条件**（不同物种/注释版本/参考集数量各异；拟南芥 15、茶树 23、油茶 21 只是参照）；
2. 每行有坐标、链向、来源；
3. 最终蛋白文件条数与表一致；
4. 数量明显偏离近缘物种/文献时 → 对照已发表研究、其他注释版本、orthogroup、组装完整性解释差异；**不要为了"凑常见数字"补数或删数**。

> 💾 备份：把 `D:\[family]_sesame\results` 整个目录复制一份（移动硬盘/网盘）。**🟢 Level 1 阶段冻结（Freeze 1）完成 🎉**（若继续 🟡 Level 2：4.7-4.10 → 重跑 4.11 → **最终冻结（Freeze 2）**出 `final_gene_set.tsv`）

---

## 4.13 可选进阶：Ka/Ks + [超家族近缘成员] 顺带鉴定 + 表达支持

> 三个「可选但不吃亏」的补充。Ka/Ks 是证据矩阵 I 项（有近缘物种 CDS 就做）；[超家族近缘成员] 顺带鉴定给补充材料加一张表；表达支持在你有转录组数据时最完整。

### 4.13.1 Ka/Ks（tbtools dnDsCalculate）

**原理**：拿成员蛋白在近缘物种找直系同源 CDS，计算非同义/同义替换率比 ω：ω<1 = 净化选择倾向（功能保留的常见表现）。**注意：Ka/Ks 只是进化约束的辅助证据，不单独证明基因真实性**——ω 受序列长度、同义位点数、比对质量、替换饱和与所选模型影响；假基因也不一定稳定得到高 ω。

**前提**：近缘物种（同属/同科）的 CDS。**没有就跳过、报告注明；千万别拿拟南芥这种远缘物种做**（替换饱和，ω 失真）。

**CLI 命令**：

```powershell
# 前提：成员 CDS + 近缘物种 CDS 先各自提取（见 4.5 的 Gtf/Gff3 Sequences Extractor，feature=CDS）再做密码子比对（muscle 或在线 MAFFT）
tbtools tool dnDsCalculate --inAln 05_structure\[family]_cds_aln.fa --outPairwiseKaKs 08_rbh\kaks_out.tsv
#    （ArgsParser 契约：--inAln 输入密码子比对 FASTA --outPairwiseKaKs 输出表；引擎自带逐对 Ka/Ks）
```

**GUI▶**：TBtools **Sequence Toolkits → Simple Ka/Ks Calculator (NG)** ⚠️（选两组 CDS + 配对表，输出 ω；NG = 串行版，参数简单）。

**判读**：Ka/Ks 用作进化约束的辅助证据，**不单独判断成员真假/功能状态**（ω 受序列长度、比对质量、同义替换数影响；假基因不一定稳定得到高 ω）。记录各成员 ω；异常者触发人工复核，不作为排除依据。

### 4.13.2 [超家族近缘成员] 顺带鉴定（1 小时，补充表素材）

4.3/4.6 已经挖出了「只有[核心域1]、没有 [核心域2]」的那批候选——它们几乎可以肯定包含 [超家族近缘成员]。给补充材料加一张 [超家族近缘成员]表：

```powershell
# 从 4.6 的宽松扫描结果里抓"有 [核心域1] 无 [核心域2]"名单：
#   [域1]_loose.domtbl 第 1 列 = 有 [核心域1] 的；[域2]_loose.domtbl = 有 [核心域2] 的
#   Excel：差集（有 [核心域1] 且不在 [核心域2] 名单）= typeA_candidates.txt
```

> ⚠️ [超家族近缘成员] 的正式判定还需另立标准（排除 [家族名] 特征），这里只给候选名单，正文不要当结论发。

### 4.13.3 表达支持（有转录组时，概要）

完整做法（质控→比对→定量）是另一套流程。鉴定阶段只需要一个近似答案：**成员有没有表达信号**。查 NCBI GEO 上[目标物种]公开表达矩阵（TPM/FPKM），直接查成员 ID 在不在、值是否 >0。0 表达 ≠ 删除（油茶 378.17 先例），而是边界标注素材。

---

*第 4 章完。下一章：整理成能交差、能写进论文的报告。*

# 第 5 章 结果整理与交付

> 📌 **本章只需记住 3 件事**：① 交付三件套命名（preliminary/final_gene_set + representative_transcript + representative_protein，见 3.0）；② 方法节如实写"注释一致性核对"，≠ Exonerate；③ scripts 命令记录是复现性硬要求。

> 鉴定跑完只是第一步。这章教你把结果整理成**能交差、能写进论文、能抗审稿人提问**的交付物。审稿人绝大多数问题集中在"你凭什么说这个基因是/不是这个家族的"——报告模板每一条都留了证据位。

## 5.1 交付物清单（🟢 本章出口：全部交付物就位再交付）

| # | 文件 | 内容 | 给谁看 |
|:-:|:--|:--|:--|
| 1 | `preliminary_gene_set.tsv`（🟢 Level 1）/ `final_gene_set.tsv`（🟡 Level 2） | 成员表（基因/染色体/坐标/链向/状态/来源） | 所有人 |
| 2 | `preliminary_representative_protein.fa`（🟢）/ `final_representative_protein.fa`（🟡） | 每基因一条代表蛋白序列 | 合作者（后续分析） |
| 3 | `verification_matrix.tsv` | 证据矩阵记录表（硬条件+支持证据） | 导师/审稿人 |
| 4 | `identification_report.md` | 鉴定报告（方法+结果+决策） | 导师/论文 |
| 5 | `[family]_refs.hmm` | 家族模型 | 存档（可复现） |
| 6 | `scripts\step*.txt` + `logs\` | 全部命令记录 | 可复现性 |

> **可复现性提示**：仅提供最终结果而缺少关键参数、输入文件和运行记录，会显著降低可重复性，增加方法审查难度。第 4 章每一步的命令都存进 `D:\[family]_sesame\scripts\`，一个都不要删。

## 5.2 鉴定报告模板（复制改写）

```markdown
# [目标物种] [家族名] 基因家族鉴定报告

## 1. 摘要
本研究在[目标物种]参考基因组（版本/accession：____，共 ____ 个基因注释）全蛋白组中进
行 [家族名] 家族系统鉴定。经 HMM 搜索、核心结构域（[核心域1], [域1] +
[核心域2], [域2]）验证及证据矩阵核查（核心硬条件 + 支持证据），鉴定到 ____ 个 [家族名] 成员
（标准 ____，边界 ____）。

## 2. 方法
### 2.1 数据
参考基因组及注释：____（版本、来源）；蛋白组 ____ 条蛋白质。
### 2.2 家族模型
参考序列：[参考来源（PlantTFDB/UniProt/文献）] [家族名]（____ 物种），去冗余后 ____ 条，多序列比对
（MUSCLE/MAFFT），hmmbuild 构建 HMM 模型。
### 2.3 候选鉴定与证据矩阵
1. HMM 全蛋白组搜索（E<1e-3，见参数表）：____ 个候选
2. 核心结构域验证（[域1]+[域2]，E<1e-3，见参数表）：____ 个核心域齐全
3. 蛋白完整性（无内部终止）：____/____
4. 基因结构核对（CDS 提取→翻译→注释蛋白全长比对，TBtools 实现）：
   ____/____ 全长一致、无移码
5. 宽松阈值查漏（E<1e-1，见参数表）：新增候选 ____，纳入 ____
6. 直系同源聚类（OrthoVenn3，含拟南芥）：____/____ 归入含 [家族名] 的簇
7. RBH 双向最优比对（vs 拟南芥全蛋白组，tbtools recipBlast）：____/____ 互指
8. MEME 保守基序：____ 个显著基序（不设固定 E 值阈值，显著性以 MEME 输出报告为准），含家族特征基序
### 2.4 判定标准
核心归属条件（家族 HMM + 核心域）全过 + 注释一致性 QC 无明显冲突 + 支持证据充分 = 标准成员；核心条件过但带退化特征/支持证据弱/注释存疑 = 边界成员；核心条件不过或注释 QC 明确破坏 = 排除。

## 3. 结果
### 3.1 成员列表（final_gene_set.tsv，按层级 preliminary/final）
### 3.2 统计
成员总数 ____（标准 ____ / 边界 ____）；染色体分布：____；
支持证据积极项：____ 项（不设固定票数阈值，整体互相印证即可）。
### 3.3 边界成员说明（如有）
逐一列出证据链（家族 E 值/各域 E 值/结构核对/RBH/功能注释）及纳入理由。

## 4. 与其他物种对比
| 物种 | [家族名] 数量 | 来源 |
|:--|:--|:--|
| 拟南芥 | _（示例 15）_ | RBH 对照/文献 |
| 已发表近缘种 | _（示例 23/21）_ | 已发表 |
| [目标物种] | ____ | 本研究 |

> ⚠️ 上表**仅作数量级参考**（判断[目标物种]数量是否合理）；这些物种与[目标物种]亲缘较远（[目标物种]所属分类 vs 山茶科），**不参与序列比对**。序列比对的对照物种 = 拟南芥 + [目标物种]近缘（见 3.6.1）。

## 5. 附件
preliminary/final_gene_set.tsv · *_representative_transcript.tsv · *_representative_protein.fa · verification_matrix.tsv · scripts · logs
```

## 5.3 论文方法节（英文模板）

```
### Identification of [家族名] genes in [目标物种]
Reference [家族名] proteins were retrieved from [参考数据库/来源] (including the
established reference species [REFERENCE_SPECIES]), deduplicated with CD-HIT,
aligned with MUSCLE/MAFFT, and used to build an HMM (hmmbuild). The HMM was searched against the complete [TARGET_SPECIES]
proteome (hmmsearch, E < 1e-3), and a second recovery source was added via
BLASTP of reference [家族名] proteins against the [TARGET_SPECIES] proteome; candidates
from both sources were unioned. Candidates were required to carry both the
[核心域1] ([域1]) and [核心域2] ([域2]) domains (core structural
features; cross-checked against superfamily-shared domain models to exclude
non-family members that share only the core domain). Each candidate was then evaluated against
core criteria - family HMM hit, dual-domain presence, and annotation/CDS
consistency (CDS extraction, translation, and identity/coverage checks against
the annotated proteins) - plus supporting evidence: gene structure, orthology
(OrthoVenn3), reciprocal best-hit BLAST against the A. thaliana proteome,
phylogenetic placement, and conserved motifs (MEME). A relaxed tblastn
whole-genome scan was performed to recover unannotated or pseudogenized
candidates, which were handled as boundary candidates after evidence review.
Candidates passing all core criteria were retained as standard members when
supporting evidence was positive; candidates with verified loci but degenerate
domains or lack of expression were flagged as boundary members.
This identified N [家族名] genes in [TARGET_SPECIES] (N standard + N boundary); the
count is reported and compared with published counts in related species.
```

## 5.4 审稿人常见问题预备

| 问题 | 从哪找答案 |
|:--|:--|
| 怎么保证没漏成员？ | 查漏步骤 + 结构核对全过 + 文献量级对比 |
| 凭什么算 [家族名]？ | 核心硬条件（家族 HMM + 核心域 + 注释一致性）+ 同源/系统发育/基序等支持证据 |
| 边界成员凭什么算？ | 每个边界的证据链（4.6.2 判定表） |
| 低表达的为何没排除？ | 判定 = 核心硬条件 + 支持证据矩阵，非单一证据一票否决；0 表达只影响支持证据 J，不破坏硬条件 |
| 方法可复现吗？ | scripts 全命令 + 参数表 + 模型文件 |

---

# 第 6 章 常见报错与 FAQ（照着查）

> 📌 **本章用法**：按现象查（安装→数据→运行→判断四类）；命令 0 结果先查 4.0.1 再怀疑环境；找不到答案时带着报错原文 + 上一步检查点结果去问。

## 6.0 我现在遇到了什么？（错误 → 去哪查）

```text
程序打不开 / 命令不存在        → 第 2 章（安装）
命令运行了但 0 结果            → 4.0.1（先查参数/解析，再查环境）
有候选但不知道是不是成员       → 4.3（看身份证）
GFF 里找不到我的 ID            → 3.0（ID 层级）/ 4.5
最终数量很奇怪                 → 4.6 查漏 / 4.11 证据矩阵 / 13.6
HMM 扫出全是奇怪蛋白           → 1.2（家族编号对不对）
```

> 详细问答见本章各节与第 11 章 QA 大全。

## 6.1 安装类

**Q1：`java 不是内部或外部命令`？** 没装 JDK 或没加 PATH。回 2.2，安装时勾 Add to PATH。
**Q2：`tbtools 不是内部或外部命令`？** pip install -e . 没成功。重跑 `python -m pip install -e .`；不要用 python 直接跑 bin/tbtools（那是兼容层）。
**Q3：`tbtools doctor` 报 jar not found？** TBTOOLS_JAR 环境变量没生效（重开 PowerShell）或路径错。直接设用户变量 TBTOOLS_JAR=D:\shengwu\TBtools\TBtools_JRE1.6.jar。
**Q4：`hmmsearch 不是内部或外部命令`？** 🟡 自动化路线排查：① PowerShell 函数 `hmmsearch` 是否注册（2.6 的 function 定义，重开终端要重注册/写 $PROFILE）；② `scripts\hmmsearch_win.py` 是否存在；③ `python -m pip show pyhmmer` 是否装了。🟢 新人路线不存在此问题（UGENE/在线）。**不要去找"官方 hmmsearch.exe"——Windows 没有现代官方二进制（2.6 勘误）**。
**Q5：blastp 报错 DLL 缺失？** 装 Microsoft Visual C++ Redistributable（NCBI BLAST 安装包一般自带提示）。

## 6.2 数据/格式类
**Q6：蛋白组 grep 到只有几百条？** 下错文件（可能是单基因）。NCBI 找 protein.faa。
**Q7：domtbl 在 Excel 里全挤一列？** 分隔符没选 Tab。数据→从文本/CSV→分隔符勾 Tab。
**Q8：候选 ID 在 GFF 里搜不到？** 带版本后缀（.1/.2）或前缀。统一去后缀：Excel 分列按 "."。
**Q9：.hmm 文件记事本打开是 HTML？** 下错链接。回 Pfam/InterPro 页面找 HMM 下载按钮。

## 6.3 运行类
**Q10：hmmsearch 报格式错误？** FASTA 有非法字符/空行/CR。用 tbtools statFasta 检查；TXT 文件用记事本「另存为 UTF-8/ANSI」清洗。
**Q11：genestructure 输出空白图？** GFF 里 ID 格式与名单不一致（可能带 mRNA 后缀）。看 GFF 实际 ID 写法，调整名单。
**Q12：Gtf/Gff3 Sequences Extractor 输出为空？** Feature 选错或没点 initialize。Feature 选 CDS，上下游填 0，再 Start。
**Q13：recipBlast 报 blastp 找不到？** BLAST+ 没装/没 PATH。回 2.7。
**Q14：OneStepBuildATree 卡住？** Windows 下其 IQ-TREE 阶段存在上游管道 stderr 阻塞问题（可能长时间挂起，非数据错误）；优先切 TBtools GUI 建树，或先小数据（20 条）试跑。

## 6.4 逻辑判断类
**Q15：核心域齐全 60 个，太多？** 数量异常仅作 QC 触发信号，不要据此删成员。先查 [域1] 阈值（[核心域1] 在众多同超家族蛋白里都有，必须同时看 [核心域2]）；抽 3-5 条比拟南芥 [家族名] 看保守性；仍存疑则复核输入/ID/模型/注释。
**Q16：查漏挖出"只有[核心域1]"的一批？** 大概率 [超家族近缘成员]，不是 [家族名]。记入补充表（[超家族近缘成员] 鉴定是另一个课题）。
**Q17：某成员 CDS 翻译不对？** 检查：① GFF 里选的 feature 是否 CDS；② ID 是否带 mRNA 后缀；③ 该区域基因组是否有 N 堆积。都正常还失败 → 走边界/排除决策。
**Q18：全 0 表达的成员删不删？** 0 表达只是支持证据 J 阴性 → **触发复核，不足以单独定 boundary**（正文原则：不靠单一证据判定）；保留并记 review（油茶 378.17 先例是多项证据综合的边界判定）。
**Q19：[目标物种]基因组小，能跑得动吗？** 完全能。约 275 Mb（GCF_000512975.1）比油茶 2.9 Gb 小一个量级，普通笔记本无压力。
**Q20：tbtools 命令在 Windows 上绘图报错？** 数据类工具全可用；**绘图引擎在 Windows 无 xvfb 部分受限**——绘图统一用 **TBtools GUI 点选**（Windows 原生有屏幕），这是本教程的既定策略。

## 6.5 提速技巧
- 多线程：**兼容层单线程**（无需 --cpu）；真实 HMMER 多线程版才用 `--cpu 4`；BLAST+ `-num_threads 4` 真实多线程；
- 先小试：先拿 1000 条蛋白子集（Excel 从蛋白组 ID 抽前 1000）跑通全链，再全量；
- 后台/记录：PowerShell 里 `命令 > logs\step.log 2>&1` 把输出存文件，出错看 log。

---

# 第 7 章 术语表与附录

> 📌 **本章只需记住 3 件事**：① 术语完整定义见第 12 章；② GUI 菜单按关键词搜（窗口右上角有搜索框）；③ 7.3 油茶数字只是数量级参考，不是你的预期值。

## 7.1 术语速查（完整术语表见第 12 章，此处不重复）

常用词即查：[家族名]、结构域、HMM/HMMER、E 值、边界成员、RBH、OG、Ka/Ks、MEME、GFF/FASTA/TSV、tbtools-cli、TBtools——定义与上下文见第 12 章「术语表（完整版）」。

## 7.2 GUI 菜单速查表（TBtools 点哪里）

| 功能 | 菜单路径（✅=官方确认 ⚠️=以版本为准） | 对应 CLI |
|:--|:--|:--|
| 按 ID 提取序列 | Sequence Toolkits → Fasta Tools → **Amazing Fasta Extractor** ✅ | `tbtools tool extractFasta` |
| 序列统计 | Sequence Toolkits → Fasta Tools → **Fasta Stats** ✅ | `tbtools tool statFasta` |
| 按 GFF 提取 CDS/蛋白/启动子 | Sequence Toolkits → Gff3/GTF Manipulator → **Gtf/Gff3 Sequences Extractor** ✅ | RPC `GxfToGenePos.process`（gene 位要显式 featurePattern=gene） |
| 多序列比对 | Sequence Toolkits → **Multiple Sequence Alignment** ⚠️ | `tbtools muscle` / RPC OneStep |
| BLAST 搜索 | **Blast → Blast Wrapper → Several Sequences To a Big File** ✅ | `tbtools recipBlast` / `twoSeqBlast` |
| 基因结构图 | Graphics → BioSequence Structure Illustrator → **Gene Structure View** ⚠️ | `tbtools genestructure` |
| 树+基序+结构三联图 | Graphics → BioSequence Structure Illustrator → **Amazing Optional Gene Viewer** ✅（输入 Newick+MEME XML+GFF） | `tbtools motif` + `tbtools tree` |
| 基因染色体定位图 | Graphics → BioSequence Structure Illustrator → **Gene Location (from GXF)** ⚠️ | `tbtools genelocgff` |
| 热图 | Graphics → **Amazing Heatmap → The Amazing Simple Heatmap** ✅ | `tbtools heatmap` |
| Venn | Graphics → Venn and Upset Plot → **Wonderful Venn** ✅ | `tbtools venn2/venn3` |
| GO/KEGG 富集 | **GO and KEGG → GO/KEGG Enrichment** ✅ | `tbtools goEnrich/keggEnrich` |
| 一键建树 | **Tree → One Step Build a ML Tree** ⚠️ | `tbtools rpc call OneStepBuildATree.process` |
| Ka/Ks | Sequence Toolkits → **Simple Ka/Ks Calculator** ⚠️ | `tbtools dnDsCalculate` |

## 7.3 油茶真实结果对照表（[目标物种]结果跟它对）

| 指标 | 油茶（参考） | [目标物种]（待填） | 合理区间 |
|:--|:--|:--|:--|
| 蛋白组规模 | 46,612 | ____ | — |
| 初筛候选（E<1e-3） | 83 | ____ | 观察明显异常 |
| 核心域齐全 | 20 | ____ | 0 或异常大量才回查 |
| 仅[核心域1]（[超家族近缘成员]候选） | 27 | ____ | 仅记录 |
| 查漏新增 | 1（378.17） | ____ | 异常多才回查 |
| 最终成员 | 21（20 标准 + 1 边界） | ____ | 仅 sanity check（不设范围） |
| 蛋白长度（油茶实例） | 427-733 aa | ____ | 异常短蛋白才回查 |
| 重复类型 | 片段5/分散16/串联0 | ____ | 串联通常极少 |

> ⚠️ 本表是**油茶实测数字 vs 你的预期**（数量合理性参考），不是要求你把[目标物种]拿去跟油茶/茶树比对序列；序列比对的对照物种用拟南芥 + [目标物种]近缘（3.6.1）。

## 7.4 常用命令速查（PowerShell）

```powershell
# 看文件
Get-Content file.txt -TotalCount 5      # 前 5 行
Get-Content file.txt | Measure-Object -Line   # 行数
Select-String -Path file.txt -Pattern "关键词"  # 搜关键词
(Get-ChildItem -Recurse).Count             # 文件/目录数（Measure-Object 统计的是对象数不是行数）

# 处理
Get-Content a.txt,b.txt | Set-Content all.txt   # 合并文本
# Excel 处理表格最省事：数据→从文本/CSV→Tab 分隔

# 运行并记录
hmmsearch ... 2>&1 | Tee-Object -FilePath logs\step.log
```

## 7.5 资源链接汇总

| 资源 | 网址 |
|:--|:--|
| TBtools-II（jar + Windows GUI） | github.com/CJ-Chen/TBtools/releases |
| tbtools-cli（命令行封装） | github.com/qby1613527176-cmd/tbtools-cli |
| HMMER（pyhmmer 内核） | `python -m pip install pyhmmer`（见 2.6） |
| NCBI BLAST+ Windows | ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ |
| NCBI 基因组（[目标物种]三件套） | ncbi.nlm.nih.gov/datasets/genome |
| PlantTFDB（参考序列） | planttfdb.gao-lab.org |
| Pfam/InterPro（结构域模型） | ebi.ac.uk/interpro |
| TAIR（拟南芥蛋白组） | arabidopsis.org |
| MEME Suite（基序） | meme-suite.org |
| OrthoVenn3（聚类） | orthovenn3.bioinfotoolkits.net |
| iTOL（树美化） | itol.embl.de |
| EMBL-EBI HMMER（在线） | ebi.ac.uk/Tools/hmmer |

## 7.6 结语

按本教程走完，你将得到一份**经得起推敲的[目标物种] [家族名] 成员集合**——每个成员有证据、每个决策有记录、每个命令可复现。这就是把基因家族鉴定做成"结论扎实"而不是"跑个流程"的区别。

需要下一步（成员确定后的系统发育深化、基因结构图、染色体定位、共线性、表达分析）——随时可以再出配套教程。

---

# 第 8 章 tbtools 命令全解（照着查，不用背）

> 📌 **本章只需记住 3 件事**：① 找命令先 `tbtools search`；② 看参数先 `tbtools tool-describe --json`；③ 绘图类命令在 Windows 受限 → 用 TBtools GUI。

> 来源：tbtools-cli 仓库 `docs/COMMAND_REFERENCE.md`（自动生成；**命令契约一律以你本机 `tbtools tool-describe <命令> --json` 为准**）。任何时刻想找命令：`tbtools search <任务词>` 先搜。这里列本流程相关的高频命令。

## 8.1 blast 组（6 个）

| 命令 | 作用 | 用法要点 |
|:--|:--|:--|
| `recipBlast` | **双向最优比对（RBH），一步出互指对** | `recipBlast <query.fa> <subject.fa> <outPrefix> [--thread N]`（v1.4.23 为位置参数形态；不同版本可能不同，**一律以 `tbtools tool-describe recipBlast --json` 为准**；两个方向都应在完整蛋白组上跑，成员只作结果筛选） |
| `twoSeqBlast` | 两条序列/两组序列比对 | `twoSeqBlast <query> <subject> <out> [--prog blastp]` |
| `quickFamily` | 基因家族快速同源鉴定 | `quickFamily <refPep.fa> <familyIds.txt> <queryPep.fa> <outPrefix>` |
| `findhomolog` | 找最优同源 | 37 FindBestHomology 引擎 |
| `filterCScore` | 过滤 blast tab6 结果 | `filterCScore <in.tab6> <out.tab6> [--cscore 0.5]` |
| `blat` | BLAT 比对（Java 内嵌） | `blat ...`（42 BlatExecutor） |

## 8.2 序列/表格工具（engine 组高频）

| 命令 | 作用 |
|:--|:--|
| `extractFasta` | 按 ID 列表提取 FASTA 序列 |
| `extractFastaSub` | 按区域/子序列提取 |
| `extractFeatureFromGTF` | 从 GTF/GFF 提取特征序列 |
| `extractGff3Region` | 按坐标取 GFF 区域 |
| `statFasta` | FASTA 统计（条数/长度/GC） |
| `CdsToProtein.process`（RPC） | CDS 翻译成蛋白（'cds2protein' 非顶层 CLI 命令） |
| `GXFOverlaper` | GFF 操作 |
| `FastaLongestRepresentater` | 多转录本取最长代表 |
| `FastaIDRenamer` / `FastaIDSimplifier` | ID 改名/简化 |
| `TableColSelector` / `TableMelt` / `TableCast` | 表格选列/透视 |
| `autoMakeBlastDb` | 自动建 BLAST 库 |
| `dnDsCalculate` | Ka/Ks 计算 |
| `fpkmToTpm` / `rpkmCal` | 表达量换算 |
| `GoCompareBar` | GO 比较柱状图 |

## 8.3 RPC 常用方法（数据工具，188 个——截至本文测试版本，以 `tbtools methods` 实际输出为准）

```powershell
tbtools methods                     # 列出全部方法（JSON）
tbtools rpc call <Method.process> '<json>'   # 调用
```

| 方法 | 功能 |
|:--|:--|
| `FastaStat.process` | 序列统计 |
| `FastaExtract.process` | 按 ID 提取 |
| `FastaMerge.process` / `FastaSplit` | 合并/拆分 FASTA |
| `CdsToProtein.process` | CDS→蛋白 |
| `OneStepBuildATree.process` | 一键建树（MUSCLE+trimAl+IQ-TREE） |
| `FetchATimeTree.process` | TimeTree |
| `AmazingHeatMap.process` | 热图 |
| `ExpressionCorrMatrix.process` | 表达相关矩阵 |
| `GxfToGenePos.process` | GFF→基因位置表 |
| `GxfRepresentativeIds.process` | gene→代表性转录本 mRNA ID 映射（4.5 用） |
| `GxfGeneDensityProfiler.process` | 基因密度 |
| `QuickGeneFamilyIdentification.process` | 基因家族快速鉴定 |
| `TableTools.*` | 17 个表格工具（melt/transpose/sort…） |

## 8.4 tbtools 全局用法清单

```powershell
tbtools --help                # 全部子命令
tbtools version --json        # 版本与能力计数
tbtools doctor                # 环境自检（jar/java/依赖）
tbtools search "词"           # 按任务找命令（不规划）
tbtools tool-describe <命令> --json   # 看某命令参数契约
tbtools tool-validate <命令> <输入...> --json  # 执行前预检
tbtools tool-run <命令> <输入...> --json      # 执行（建议先 tool-describe / tool-validate 再运行）
tbtools tool-submit / job-status / job-result # 长任务异步
tbtools artifact inspect <文件>    # 产物语义校验
tbtools tool-provenance <文件>     # 溯源
tbtools mcp                     # MCP server（给 Claude 等 AI 用）
```

## 8.5 绘图命令一览（TBtools GUI 或 tbtools 绘图）

| 图 | tbtools 命令 | GUI 路径 |
|:--|:--|:--|
| 基因结构图 | `genestructure <gff> <ids> <out>` | Gene Structure View |
| 基序分布图 | `motif <meme.xml> <ids> <out>` | Amazing Optional Gene Viewer |
| 基因染色体定位图 | `genelocgff <gff3> <ids> <out>` | Gene Location (from GXF) |
| 热图 | `heatmap <matrix> <out> [group]`；`heatmap2`（聚类/分组） | Amazing Heatmap |
| Venn | `venn2/venn3 --List1.. --label1..` | Wonderful Venn |
| 火山图 | `volcano <deg.txt> <out>` | — |
| 共线性点图 | `dotplot --inGff --genePair --chrLayout` | Dual Synteny Plot |
| 共线性双图 | `dualsyn <gff> <collinearity> <out>` / `msy` | Dual Synteny / Microsynteny |
| 树+注释轨道 | `tree <treeMeta.cfg> <out>` | TreeTreeTree |
| MSA 比对图 | `msa <aln.fa> <out>` | — |
| Circos | `circos <chrLen> <links> <genePos> <out>` | — |
| 条形图/柱状图 | `barplot / groupedbar` | — |
| PCA | `pca` | — |

---

# 第 9 章 【实例】完整走查示例（ARR-B·油茶 数据演练；泛化后此章仅作参考）

> 📌 **本章只需记住 3 件事**：① 油茶数字（83/20/21）只是流程演示，不是你的预期；② 命令与第 4 章完全一致，物种换成你的；③ 378.17 是"边界成员"判定的完整范本。

> 这一章用**油茶真实数据**走一遍第 4 章主链，让你在看芝麻数据执行前，先对"每一步会看到什么"有具体画面。命令和 §4 完全一致，只是物种换成油茶（Camellia oleifera，文件路径是本地示例）。
> ⚠️ **本章所有油茶数字（83/20/21 等）仅为流程演示，不构成芝麻的预期值**——芝麻该是多少就是多少，只拿它当"数量级合理性"的 sanity check 参考（7.3/13.5）。

## 9.0 示例数据（油茶，本地已有）

| 用途 | 文件 |
|:--|:--|
| 蛋白组 | `生物信息学/油茶/解压后/Chrall.proteins.fasta`（46,612 条） |
| GFF | `生物信息学/油茶/解压后/Chrall.genes.gff` |
| ARR-B 参考 | PlantTFDB 2354 条（示例：放 `refs/arrb_refs_raw.fa`） |
| 结构域模型 | `PF00072.hmm` / `PF00249.hmm` |
| 对照物种 | **拟南芥** TAIR 全蛋白组（`control/athaliana.protein.fa`）；芝麻近缘物种（胡麻科/唇形目）如有再加（见 3.6.1） |

## 9.1 走查：第 1-3 步（建模→初筛→双域）

```powershell
# Step 1 建模（油茶实测输出）
cd D:\arrb_sesame\results
# cd-hit 后 421 条代表序列 → MAFFT 比对 → hmmbuild：
#  HMM file:    arrb_refs.hmm
#  Model length: 342
# ☑ 检查：HMMER3/f 开头，342 列

# Step 2 初筛
hmmsearch -E 1e-3 --domtblout 02_search\arrb.domtbl -o 02_search\arrb.out D:\arrb_sesame\data\refs\arrb_refs.hmm 油茶\Chrall.proteins.fasta   # 兼容层单线程，--cpu 会被忽略（真实 HMMER 才用）
# 实测：83 个候选（油茶历史案例初筛 E=1e-3；本案例参数仅作演示，不作为芝麻主流程参数——主流程见参数表）

# Step 3 双域验证
hmmsearch -E 1e-3 --tblout 03_domains\rec.tblout D:\arrb_sesame\data\refs\PF00072.hmm 03_domains\arrb_candidates.fa
hmmsearch -E 1e-3 --tblout 03_domains\myb.tblout D:\arrb_sesame\data\refs\PF00249.hmm 03_domains\arrb_candidates.fa
# 实测判定：双域齐全 20 ｜ 仅 REC 27 ｜ 无 REC 36
```

## 9.2 走查：第 6 步查漏（油茶实测：挖出 378.17）

```powershell
# 宽松重扫 E=1e-3 → 103 命中 → 83 基因；新候选双域复验：
# 发现 maker-HiC_scaffold_12-snap-gene-378.17：
#   ARR-B.hmm E=4.3e-61 | REC E=4.9e-12 ✅ | MYB E=1.1e-6 ⚠️退化
# 证据链（油茶判定表）：
#   1 家族模型 4.3e-61 ✅  2b MYB 1.1e-6 ⚠️存在
#   3 结构核对：350 aa 全长、7 外显子 5 内含子、翻译无终止 ✅
#   4 RBH：best hit = AtARR1 (AT3G16857)，E=7.6e-29 ✅
#   5 功能注释：eggNOG → ko04075 细胞分裂素通路 ✅
#   表达：5 套转录组 0 表达
# 决策：纳入第 21 个成员，标注 boundary（HMM_dual_domain_boundary）
```

## 9.3 走查：RBH 与建树（油茶实测输出形态）

```powershell
# recipBlast 输出（示意两行）：
# query                subject              pident  evalue
# Co1g12345   AT1G19050(ARR1)  87.3    2e-120   ← 互指成立
# Co2g67890   AT2G25180(ARR12) 90.1    3e-130   ← 互指成立

# 建树：36 taxa（20 油茶 + 15 拟南芥 + 茶树补充）· 这是油茶案例自己的对照（同科，合理）
# 你跑芝麻时对照 = 拟南芥 + 芝麻近缘（胡麻科/唇形目），见 3.6.1
# IQ-TREE 最佳模型 JTT+F+I+R3；bootstrap 1000
# 树文件 arrb_tree.treefile → iTOL/FigTree 打开
```

## 9.4 走查：冻结表（油茶实例，当年命名 final_set.tsv；通用命名见 4.12：preliminary/final_gene_set.tsv）

```
gene    chr    start    end    strand   status   source
maker-HiC_scaffold_10-snap-gene-775.6    HiC_scaffold_10    12345    23456    +   standard   hmm_dual_domain
maker-HiC_scaffold_14-snap-gene-954.31   HiC_scaffold_14    98765    102345   -   standard   hmm_dual_domain
maker-HiC_scaffold_12-snap-gene-378.17   HiC_scaffold_12    37825743 37829416 -   boundary   myb_degenerate_zero_expr
```

> 📌 本实跑的 RBH 采用 RefSeq（48,265 条，历史验证数据源变体）；通用教程当前默认 TAIR（3.6）。**两者不混用计数**。
> 📌 芝麻执行时，把上面所有"油茶数字"替换成你自己的（候选数/双域数/成员数），**数字异常（候选 0 或几千、双域 0 或 60+）是最快的排错信号**。

---


# 第 10 章 TBtools GUI 手把手（每个功能怎么点，逐步操作）

> 📌 **本章只需记住 3 件事**：① 菜单按关键词搜（不同版本位置会变）；② 每个功能四步：输入 → Initialize → Start → 检查输出；③ 卡住先查 4.0.1 / 第 11 章。

> 本章把第 4 章用到的主要 TBtools 图形界面功能，按「打开对话框 → 每一步填什么 → 点哪个按钮」写全。**界面以你实际获取的 TBtools-II 版本为准；不同版本菜单位置可能略有差异，按功能关键词搜索（窗口右上角有搜索框）。**

## 10.1 准备工作：打开 TBtools + 设置工作目录

1. 双击 TBtools 图标打开主面板（主菜单栏 + 常用功能按钮）；
2. 建议：菜单 **Preferences → Set Memory**（内存）给 4G+（大矩阵/热图需要）；
3. 每个功能对话框都有输入框：可以**直接把文件拖进输入框**（Windows 支持），或点 `...` 按钮浏览选择。

## 10.2 Amazing Fasta Extractor（按 ID 列表提取序列）—— 4.3/4.4/4.8/4.12 用

官方确认路径：`Main menubar -> Sequence Toolkits -> Fasta Tools -> Amazing Fasta Extractor`（✅）

1. 打开该功能，对话框分四块：
   - **Input Fasta**：把全蛋白组文件（如 `[Species].protein.fa`）拖进去（或点 `...`）；
   - 点 **Initialize** 按钮（建立索引，大数据要等几秒；会提示 index 已建）；
   - **Output Fasta**：填输出文件名（如 `candidates.fa`）；
   - **ID list**：把候选 ID 列表粘贴进去（或点右边图标加载 txt 文件）——支持三种格式：
     - 单列 ID：`Si01g12345` 一行一个；
     - 区域：`Chr1 100000 102000`（染色体+起+止，空格分隔）；
     - 自定义名 + 区域：`名字 Chr1 100000 102000`；
2. 点 **Start**（或勾 **Just Show Dialog** 则直接在弹窗里看结果不落盘）；
3. 完成后输出文件里就是按你名单抽出的序列——**序列条数应 = ID 个数**（少了说明有 ID 没匹配上，见 6.2 Q8）。

> 这个功能同时也是「查 ID 是否在文件里」的利器：抽出来的条数不对 = 有 ID 对不上，立刻知道。

## 10.2.1 Fasta Stats（序列统计/条数检查）—— 3.8/4.4 用

路径：`Main menubar -> Sequence Toolkits -> Fasta Tools -> Fasta Stats`（✅）

1. **Input Fasta**：拖入要统计的 FASTA（蛋白组 / 成员 / 参考集都行）；
2. 点 **Start**（或 Refresh）；
3. 输出：**Sequences 条数**、长度分布、GC 含量、是否含异常字符（`*`/`X`）——3.8 数据自检、4.4 完整性初检都看这里。

> ☑️ 用法：`statFasta` 命令的 GUI 等价物；条数对不上 = 文件下错/名单缺 ID（见 3.8 处理表）。

## 10.3 Gtf/Gff3 Sequences Extractor（按注释提取 CDS/蛋白/上游）—— 4.5 结构核对用

官方确认路径：`Main menubar -> Sequence Toolkits -> Gff3/GTF Manipulator -> Gtf/Gff3 Sequences Extractor`（✅）

1. **Gff3/Gtf file**：拖入[目标物种] GFF → 点 **Initialize**（解析后下方会列出可用 feature 类型）；
2. 关键两步（新手常错）：
   - **Feature type to extract**：选 `CDS`（要翻译成蛋白时选这个；要基因区 DNA 选 `gene`；要启动子选上游 bp 数）；
   - **ID to group by**：选 `Parent`（按转录本（mRNA）聚合 CDS 片段）或 `mRNA`；
3. **Genome file**：拖入基因组 FASTA；
4. **Output file**：填输出（如 `members.cds.fa`）；
5. **Upstream/Downstream**：默认 0（提取启动子就在 Upstream 填 2000 之类）；
6. 点 **Start** → 输出每个转录本的 CDS 序列。

**☑️ 用完后**：拿这个 CDS 文件 → Fasta Tools → **Translate**（翻译成蛋白）→ 与注释蛋白对比长度/一致性 = 4.5 的结构核对实证。

## 10.4 Blast Wrapper（BLAST 搜索）—— 4.8 备用 / 表达比对

官方确认路径：`Main menubar -> Blast -> Blast Wrapper -> Several Sequences To a Big File [Commonly Used]`（✅）

1. **Query**：把 query 序列粘贴进文本框或拖入 FASTA（多条也可以）；
2. **Target**：拖入选定的目标文件（拟南芥蛋白组）；
3. **Output**：填输出文件路径；格式选 **Table**（制表符表格，Excel 可直接开）或 XML（可点 Visualize 可视化）；
4. 右上参数面板：程序选 blastp、E 值 1e-5、线程数；
5. 点 **Start**；
6. 完成后点 **Visualize**（仅 XML 格式）可以图形化看比对。

> ⚠️ 如果报错找不到 blast：确认已装 NCBI BLAST+（2.7）且其 bin 目录在 PATH，重启 TBtools 再试。
> 💡 同一个对话框把程序改成 **tblastn**、Target 换成[目标物种]**基因组**（DNA）——就是 4.6 查漏的 GUI 做法（蛋白→基因组扫描）。

## 10.5 Gene Structure View（基因结构图）—— 4.5/4.9 用

路径：`Main menubar -> Graphics -> BioSequence Structure Illustrator -> Gene Structure View (From GFF3/GTF)`（⚠️ 版本差异）

1. 输入：GFF 文件 + 成员 ID 列表文件（或直接粘 ID）；
2. 可配：外显子颜色、显示 CDS/UTR、输出尺寸；
3. **Start** → 弹窗显示基因结构图 → 窗口里点保存（PNG/SVG/PDF）；
4. 同一菜单下 **Amazing Optional Gene Viewer**（✅ 官方确认）：它能一次输入 **Newick 树 + MEME XML + GFF**，输出「树 + 基序 + 基因结构」三联图——4.9 建完树后强烈推荐用它出论文级总览图（油茶 Fig1 同款风格）。

## 10.6 Amazing Heatmap（热图）—— 下游

官方确认路径：`Main menubar -> Graphics -> Amazing Heatmap -> The Amazing Simple Heatmap`（✅）

1. 输入：表达矩阵/数值矩阵文件（第一行表头、第一列行名，Tab 分隔）；
2. 可选：分组信息文件（行/列分组）、行/列树文件；
3. 选配色、log2 转换、归一化（勾选 Row scale/Column scale）；
4. **Start** → 交互式热图窗口 → 导出 PNG/SVG。

## 10.7 Wonderful Venn（Venn 图）—— 核心域交集/集合比较

官方确认路径：`Main menubar -> Graphics -> Venn and Upset Plot -> Wonderful Venn (Up to Six Sets)`（✅）

1. 点 Add 添加集合（2-6 个）；
2. 每个集合：粘贴 ID 列表或拖入 txt（一个文件 = 一个集合）；
3. 改集合标签（label）；
4. **Start** → Venn 图窗口 → 导出；**图中的交集 ID 也可导出**（右键/输出选项）——4.3 用 Venn2 求"核心域交集"就是用它。

## 10.8 GO/KEGG 富集（下游）

路径：`Main menubar -> GO and KEGG -> GO Enrichment`（✅）/ `KEGG Enrichment`（✅）

1. GO：需三样输入——`go-basic.obo`（对话框里可直接点 **Download go-basic.obo**）、GO 注释背景文件（基因\GO 两列）、目标基因集；
2. KEGG：点 **Make One Backend File From Web** 准备通路文件 + 注释背景 + 目标集；
3. 输出：`*.final.xls` 直接用（已按 p≤0.05 过滤）。

## 10.9 One Step Build a ML Tree（一键建树）

路径：`Main menubar -> Tree -> One Step Build a ML Tree`（⚠️ 老版本在 Preferences/Other，搜 "One Step"）

1. 输入 FASTA（多序列）；
2. 选快速 Bootstrap（1000）、线程数；
3. **Start** → 输出目录得到 aligned fasta、修剪后 fasta、treefile、iqtree 报告；
4. treefile 用 iTOL 或 FigTree 打开美化。

---

## 10.10 Reciprocal Blast（双向最优比对/RBH）—— 4.8 用

路径：`Main menubar -> Blast -> Reciprocal Blast`（✅）

1. **Query（A）**：拖入[目标物种]**全蛋白组**（`data\genome\[Species].protein.fa`）；
2. **Target（B）**：拖入拟南芥**全蛋白组**（`data\control\athaliana.protein.fa`）；
3. 其余参数默认（E 值、线程数可按需调）；点 **Start**——**TBtools 内部自动建 BLAST 库**，不需要先 makeblastdb；
4. 结果 = 双向各一份 BLAST 表 + 互指对（A→B 最优与 B→A 最优互相指向 = RBH）。
> ⚠️ **两个方向都要用完整蛋白组**（成员只用于最后筛选互指对，不作为反向库）——这是 RBH 的正确口径（见 4.8）。

**☑️ 看结果**：正反两表里各取 **bitscore 最优**（并列/近似并列 → 人工复核）；反向表查这个拟南芥命中是否反指向同一成员 → 互指 = RBH。
> ⚠️ 依赖 blastp（2.7 必装）；RBH 是直系同源**支持证据**，不单独证明严格一对一直系同源（多倍体严格互指率低属正常）。

## 10.11 Gff3 To Gene Pos（GFF→基因坐标表）—— 4.12 冻结用

路径：`Main menubar -> Sequence Toolkits -> Gff3/GTF Manipulator -> Gff3 To Gene Pos`（⚠️ 版本差异，搜 "Gff3 To Gene"）

1. **Gff3 file**：拖入[目标物种] GFF → 点 **Initialize**；
2. 输出设置：填输出路径；**默认按 CDS 特征**——要 gene 位置必须**把 feature 改成 gene**（对应正文 4.12 的 `featurePattern:"gene"`）；
3. **Start** → 输出 `all_genes_pos.tsv`（染色体/起/止/链向，供 Excel VLOOKUP 拼冻结表）。

> 同菜单 **Gff3 Statistics**：GFF 里 gene/mRNA/CDS 行数统计——3.8 数据自检的 GUI 做法。

## 10.12 Simple Ka/Ks Calculator（Ka/Ks，ω）—— 4.13.1 用

路径：`Main menubar -> Sequence Toolkits -> Simple Ka/Ks Calculator (NG)`（⚠️ NG = 串行版，参数简单）

1. 输入：两组 CDS 文件（成员 CDS + 近缘物种 CDS，先各自密码子比对，见 4.13.1）；
2. 选配对方式/物种标签；点 **Start**；
3. 输出各对 ω（<1 净化选择）。**Ka/Ks 是辅助证据，不单独判断成员真假**（无近缘 CDS 就跳过）。

---

# 第 11 章 QA 大全（按现象查，含 Windows 特有问题）

> 📌 **本章用法**：按现象查表；11.4 是判断类问题（最容易答错，重点看）。

## 11.1 安装/环境（Windows 特有）

| 问题 | 原因与解决 |
|:--|:--|
| `java` 找不到 | 装 JDK 并勾 Add to PATH；重开 PowerShell |
| TBtools GUI 打不开/闪退 | 缺 Java 或内存不足：右键以管理员运行；Preferences 调内存；重装 latest 版 |
| TBtools 中文乱码 | 系统区域设置：勾选「Beta: 使用 Unicode UTF-8 提供全球语言支持」后重启 |
| tbtools pip 安装慢 | 用清华 pip 镜像：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -e .` |
| tbtools doctor 报缺依赖 | 缺哪个补哪个（见 2.8），不影响其他功能 |
| hmmsearch 双击闪退 | HMMER 是命令行程序，要在 PowerShell 里跑，不是双击 |
| BLAST installer 卡住 | 换免安装版：下载后解压，把 bin 目录加 PATH 即可 |

## 11.2 数据/格式

| 问题 | 原因与解决 |
|:--|:--|
| 蛋白组只有几条 | 下错文件，重下 protein.faa |
| FASTA 一行超长 | 正常，别手动改；用工具处理 |
| GFF 打不开 | gz 未解压 → 右键全部解压 |
| Excel 打开 .hmm 乱码 | .hmm 用记事本看，别用 Excel |
| 中文路径报错 | 全文唯一路径规则：**纯英文、无空格**；把文件放 D:\[family]_sesame |

## 11.3 运行报错

| 问题 | 原因与解决 |
|:--|:--|
| hmmsearch 一堆 `----` | 正常（表格分隔线），看 E 值列 |
| 结果全 0 命中 | 蛋白组是 DNA 或模型空 → 回 4.1/4.2 检查点 |
| genestructure 出空白 | ID 与 GFF 命名不符（去后缀/加 mRNA 后缀） |
| CDS 提取空 | Feature 没选 CDS 或没 Initialize |
| recipBlast 报参数错 | `tbtools tool-describe recipBlast --json` 看准确参数 |
| OneStepBuildATree 挂起 | Windows 下 IQ-TREE 管道 stderr 阻塞（上游缺陷）；切 TBtools GUI 建树，或改用分步直链 muscle→trimal→iqtree 重试 |
| Excel 太卡 | 大数据用 tbtools 表格工具代替 Excel |

## 11.4 逻辑/判断（最容易答错，重点看）

| 问题 | 正确做法 |
|:--|:--|
| 核心域成员异常多 | 先当 QC 信号：复核 [域1] 判定（[核心域1] 非 [家族名] 专属）、抽几条与拟南芥 [家族名] 比对、检查输入/模型；不据此删成员 |
| "仅 [核心域1]"候选一堆 | 正常（通常多于核心域齐全的），记入补充表，不算本课题 |
| 成员不表达 | 0 表达只是支持证据 J 阴性 → **触发复核，不自动定 boundary**（不靠单一证据判定；油茶 378.17 先例是多项证据综合后的边界判定，非"0 表达即边界"） |
| 数量明显偏少 | 对照文献/近缘物种/其他注释版本/组装完整性解释差异（参考序列太少太偏、阈值过严、注释不完整都可能）；**不补数** |
| 边界成员怎么向导师解释 | 摆证据链（模型E值/各域/结构/比对/注释），说清"退化≠假基因" |
| 后面想改成员集合 | 禁止！冻结后一切分析以此为基线，要改就重跑全部下游+说明理由 |

## 11.5 提速与技巧

- `hmmsearch`（兼容层**单线程**，无需 --cpu；只有真实 HMMER 多线程版才用 `--cpu 8`）；
- 大文件操作先建索引（Amazing Fasta Extractor 的 Initialize 只做一次）；
- 重活放晚上跑，输出 `> log.txt 2>&1` 落盘；
- 所有命令存 scripts，结果存 results，命名带步骤号——**这是给未来的自己省时间**。

---

# 第 12 章 术语表（完整版）

> 📌 **本章用法**：遇到不懂的术语回来查；`[家族名]`/`[核心域1]` 等占位符含义见 0.1.1。

| 术语 | 解释 |
|:--|:--|
| [家族名]（示例：ARR-B） | 你要鉴定的基因家族（示例：B 型响应调节因子） |
| 标志结构域 | 家族区别于其他家族的核心结构域组合（[核心域1] + [核心域2]） |
| [核心域1] | 家族第一个核心结构域（Pfam [域1]） |
| [核心域2] | 家族第二个核心结构域（Pfam [域2]） |
| 同超家族蛋白 | 与家族共有一个核心域但缺特有域的其他家族成员（通常应排除） |
| 结构域 | 蛋白中进化保守的功能模块（Pfam 编号） |
| HMM / HMMER | 家族概率模型 / 搜索软件套件 |
| hmmbuild | 由多序列比对建 HMM |
| hmmsearch | 用 HMM 扫序列库 |
| E 值 | 命中巧合概率期望（越小越可信） |
| score/bitscore | 比对得分（越大越强） |
| 候选(candidate) | 初筛命中、待验证的基因 |
| 真成员 | 通过核心硬条件 + 支持证据的基因 |
| 边界成员 | 基因座真实但局部证据弱（纳入+标注） |
| 排除项 | 不满足判定、被剔的基因（记录原因） |
| FASTA | 序列文本格式 |
| GFF/GFF3 | 基因注释表（9 列） |
| TSV/CSV | Tab/逗号分隔表格 |
| MSA | 多序列比对 |
| MAFFT/MUSCLE | 比对软件 |
| cd-hit | 去冗余（相似度聚类） |
| blastp | 蛋白↔蛋白相似搜索 |
| tblastn | 蛋白↔核酸（翻译后）搜索 |
| makeblastdb | 建 BLAST 库 |
| RBH | 双向最优比对（互为最佳命中；直系同源**支持证据**，不单独证明严格一对一） |
| best hit | 最优命中 |
| 直系同源(ortholog) | 物种分化形成的一对基因 |
| 旁系同源(paralog) | 种内复制形成的一对基因 |
| OG | 直系同源组（聚类产物） |
| OrthoFinder / OrthoVenn3 | 聚类软件 / 在线聚类 |
| MEME | 从头找保守基序 |
| motif | 保守基序（短功能肽段） |
| Ka/Ks（ω） | 非同义/同义替换比 |
| 净化选择 | ω<1，功能被保留 |
| 正选择 | ω>1，适应性进化 |
| Exonerate | 蛋白回拼基因组（本教程用结构核对替代） |
| CDS | 编码序列（翻译区） |
| 外显子/内含子 | 保留/剪掉的基因区段 |
| 启动子 | 基因上游调控区 |
| 假基因 | 功能被破坏的基因拷贝 |
| 转录组/RNA-seq | mRNA 测序（表达证据） |
| TPM/FPKM | 表达量单位 |
| 系统发育树 | 进化关系树（Newick 格式） |
| bootstrap | 树分支支持率（重抽样） |
| TBtools | CJ-Chen 的图形工具盒（Windows 原生） |
| tbtools-cli | TBtools-II 的命令行封装（能力数量以 `tbtools version --json` 为准） |
| RPC | 进程间调用（tbtools 数据工具的 JSON 接口） |
| GUI | 图形界面 |


# 第 13 章 附录：文件样例 + 打印版执行清单

> 📌 **本章只需记住 3 件事**：① 13.4 打印版清单动手前过一遍；② 13.10 芝麻真实数字是"终点长什么样"的参考；③ 13.11 避坑清单动手前扫一眼（避开 90% 的坑）；13.12 是兼容层代码（🟡 自动化才需要）。

> 本章三样东西：① 你会在各步骤遇到的真实文件长什么样（对照用）；② 全程打印版勾选清单（照着打勾，防漏步）；③ 交付检查表。

## 13.1 hmmsearch 输出样例（知道自己在看什么）

### 人读版 `[family].hmmsearch.out`（-o 输出）片段：

```
Query:       [family]_refs  [M=342]

Scores for complete sequences (score includes all domains):
   --- full sequence ---   --- best 1 domain ---    -#dom-
   E-value  score  bias    E-value  score  bias    exp  N  Sequence
   ------- ------ -----    ------- ------ -----    ---- -- -------- ---------
   1.3e-92  306.4   0.6      2e-47  163.9   0.2    1.1  2  Si02g12345
   2.1e-85  282.9   1.1      3e-45  155.0   0.4    1.0  1  Si05g06789
   ...
```

- 第 1 列 = 该序列全长的 E 值（**越小越好**）；
- 最后一列 = 命中序列名（基因 ID）。

### 机器读版 `[family].domtbl`（--domtblout 输出）片段：

```
# target name         accession        tlen query name           accession   qlen   E-value  score  bias ...
Si02g12345            -                512 [family]_refs             -           342    1.3e-92  306.4  0.6 ...
Si02g12345            -                512 [family]_refs             -           342    2e-47    163.9  0.2 ...
```

**你要用的列**（ ⚠️ 不靠固定列号：HMMER 版本/输出类型不同列可能变化，按表头识别）：
| 表头名 | 内容 | 用途 |
|:--|:--|:--|
| `target name`（第 1 列） | 目标序列名（基因 ID） | 提取名单 |
| `full sequence E-value` | 全序列 E 值 | 过滤阈值（Excel 按表头筛这列） |

## 13.2 GFF3 样例行（对照你的[目标物种] GFF）

```
Chr1  maker  gene      100000  105000  .  +  .  ID=Si01g12345;Name=Si01g12345
Chr1  maker  mRNA      100000  105000  .  +  .  ID=Si01g12345.1;Parent=Si01g12345
Chr1  maker  exon      100000  100400  .  +  0  Parent=Si01g12345.1
Chr1  maker  CDS       100000  100400  .  +  0  Parent=Si01g12345.1
Chr1  maker  exon      100900  101800  .  +  0  Parent=Si01g12345.1
Chr1  maker  CDS       100900  101800  .  +  0  Parent=Si01g12345.1
```

> 注意：**GFF 里 gene 的 ID 通常不带 `.1` 后缀，mRNA/CDS 带**。做 4.5 的 CDS 提取时，输出序列名是 mRNA 名（如 `Si01g12345.1`），和你的成员名（`Si01g12345`）差一个后缀——**这是新手最容易卡住的点**：要么名单加后缀，要么提取后把 `.1` 去掉再比对。

## 13.3 blast 表格输出（-outfmt 6）样例

```
Si01g12345    AT1G19050.1    87.3    512    32    1    1    512    1    512    2e-120    890
Si02g67890    AT3G16857.1    90.1    480    21    0    1    480    1    480    3e-130    960
```

12 列含义（写报告会引用）：`query | subject | %identity | 长度 | 错配 | 缺口 | q起 | q止 | s起 | s止 | E值 | bitscore`。

## 13.4 打印版执行清单（[目标物种] [家族名] 鉴定）

### 13.4.1 新手 1.5-2 天最小可行路线（一页版，🟢 Level 1；第一次完整学习建议预留 2-4 天）

> **怎么用**：只做下面 10 步；每步「命令或 GUI → 检查点 → 报错去哪查」。核心规则：**HMM/BLAST 只捞人，命中 ≠ 成员**；硬条件 A（家族 HMM）+ B（核心域）必须成立。

| # | 步骤 | 命令或 GUI▶ | ☑️ 检查点 | 报错→ |
|:-:|:--|:--|:--|:--|
| 1 | 填参数表 + 替换占位符 | 0.9 表 → 编辑器全局替换 | 全文无 `[目标物种]` 残留 | — |
| 2 | 装环境（5 必需组件 + HMMER 按路线） | 2.1 表；HMMER 走 🟢 UGENE/在线（不用装命令行） | 2.9 自检全过（🟢 新人可跳过 `hmmsearch -h` 那行） | 6 章 Q1-5 |
| 3 | 数据就位 | 3.3-3.7 三件套+参考+域模型+拟南芥 | 3.8 自检全过 | 3.8 处理表 |
| 4 | 家族模型 | 4.1（有官方 HMM 直接跳 4.2） | `[family]_refs.hmm` 首行 HMMER3/f | 4.1 错误表 |
| 5 | 初筛 | 4.2 `hmmsearch -E 1e-3` | 候选几十~几百 | 4.2 排查表 |
| 6 | 并集召回 | 4.2b blastp + 并集 | `candidates_union.txt` | 4.0.1 |
| 7 | 核心域验证 | 4.3 hmmsearch ×2 + 交集 | 核心域齐全名单 | 4.3 错误表 |
| 8 | 提取 + 完整性 | 4.4 extractFasta + statFasta | 无内部 `*`；条数 = 名单数 | 4.4 排查表 |
| 9 | 注释一致性 | 4.5 CDS→翻译→比对（GUI：10.3+10.5） | 4 指标通过 | 4.5 错误表 |
| 10 | 查漏→矩阵→阶段冻结 | 4.6 + 4.11 + 4.12 | `preliminary_gene_set.tsv` 行数 = 成员数（Level 1 输出；`final_gene_set.tsv` 属 🟡 Level 2） | 4.6/4.11/4.12 |

> 每步命令存 `scripts\stepN.txt`；输出存 `results\`；先拿 1000 条蛋白子集试跑全链再全量；报错先查 4.0.1 → 第 6 章 → 第 11 章。

**A. 环境（第 2 章）**
- [ ] Java 装好（`java -version` 有输出）
- [ ] Python 装好（`python --version` 有输出）
- [ ] TBtools jar 就位（`java -jar TBtools_JRE1.6.jar version` 输出版本）
- [ ] tbtools-cli 装好（`tbtools version --json` 有输出）
- [ ] TBTOOLS_JAR 环境变量生效
- [ ]（🟡 自动化路线）HMMER 兼容层可用（`hmmsearch -h`）；🟢 新人路线改为「UGENE 能打开 / EBI HMMER 页面能提交」即可
- [ ] BLAST+ 可用（`blastp -version`）
- [ ] TBtools GUI 能打开

**B. 数据（第 3 章）**
- [ ] [目标物种]蛋白组（数量级 sanity，无固定值；0 条或几条 = 下错文件）→ `data/genome/`
- [ ] [目标物种]基因组（几百 MB）→ `data/genome/`
- [ ] [目标物种] GFF（gene 行数量级与蛋白组相当）→ `data/genome/`
- [ ] [家族名] 参考（多物种覆盖即可，无固定条数；有官方 HMM 可省）→ `data/refs/[family]_refs_raw.fa`
- [ ] [域1].hmm + [域2].hmm（第一行 HMMER3）→ `data/refs/`
- [ ] 拟南芥蛋白组（~2.7 万）→ `data/control/`

**C. 鉴定（第 4 章）**
- [ ] 4.1 建模型：hmmbuild 出 `[family]_refs.hmm`（HMMER3/f 开头）
- [ ] 4.2 初筛：得到候选名单（**数量不设固定范围**，异常多/0 才回查）
- [ ] 4.3 核心域：记录核心域齐全数（异常才回查，不作成员标准）
- [ ] 4.4 完整性：成员序列无内部终止（允许末端 stop）
- [ ] 4.5 结构核对：CDS 翻译全长一致、结构图正常
- [ ] 4.6 查漏：宽松重扫 → 新候选证据链 → 边界决策
- [ ] 4.7 OG 聚类（🟡 Level 2 才勾）：优先与家族参考形成合理 OG；物种特异 OG **不自动排除**，转其他支持证据复核
- [ ] 4.8 RBH（🟡 Level 2 才勾）：逐成员记录 best hit 与互指（**不设固定通过率**）
- [ ] 4.9 MEME（🟡 Level 2 才勾）：成员集合呈现一致家族保守模式
- [ ] 4.10 建树（🟡 Level 2 才勾）：树文件生成、成员位于家族预期分支
- [ ] 4.11 证据矩阵：核心硬条件全过 + 支持证据记录完整
- [ ] 4.12 冻结（按层级，三件套）：🟢 preliminary_gene_set.tsv + representative_transcript + representative_protein；🟡 final_gene_set.tsv + 对应三件套

**D. 交付（第 5 章）**
- [ ] 交付（三件套命名，见 3.0）：preliminary/final_gene_set.tsv + representative_transcript.tsv + representative_protein.fa · verification_matrix.tsv · identification_report.md · scripts · logs
- [ ] results 整目录备份
- [ ] 数量 sanity check（仅发现明显异常用）

## 13.5 关键数字速查（油茶实测 → [目标物种]预期）

| 节点 | 油茶实测 | [目标物种]预期 | 异常信号 |
|:--|:--|:--|:--|
| 初筛候选 | 83 | 无固定预期（sanity） | 0 或异常巨大才回查 |
| 核心域齐全 | 20 | 无固定预期（sanity） | 0 才回查 |
| 仅 [核心域1]（[超家族近缘成员]候选） | 27 | 仅记录 | — |
| 查漏新增 | 1 | 仅记录 | 异常多才回查 |
| 最终成员 | 21 | 无固定预期（sanity） | 明显偏离才复核流程 |
| 蛋白长度（油茶实例，非通用） | 427-733 aa | 仅记录 | 大量异常短蛋白才回查 |
| 外显子数（油茶实例，非通用） | 5-11 | 类似 | 全是单外显子需查注释 |

## 13.6 新手最容易翻车的 6 个点（考前重点）

1. **ID 后缀**：GFF 里 gene 与 mRNA/CDS 的 ID 差 `.1`——4.5 提取和 4.12 冻结最容易在这错位。**统一规则：成员名单用不带后缀的基因 ID；GFF 提取时把输出名去后缀再比对。**
2. **[域1] 太宽**：很多同超家族蛋白都带共享域——**多域家族判定必须"核心域齐全"**（单域家族见 4.3b 竞争排除），别把"有共享域"当结果。
3. **蛋白组下成 DNA**：hmmsearch 全 0 命中时先看序列字母（有 T/U = 下错）。
4. **Excel 打开 domtbl 全挤一列**：导入时分隔符要选 **Tab**。
5. **成员数少 ≠ 家族小**：跨组装/跨组合对比时数量差异大，**先排除组装/注释不完整再下结论**——"少"往往是注释问题，不是家族真小（油茶 LOG 实例 2026-10-09 修正：CON 注释层面只有 3 条，曾被误判为"缺 LOG5/LOG8 整组拷贝"；S9 六框直扫 + S10 剪接重建双轨道证明 **CON 实为 3 注释 + 5 基因组恢复 = 8 座位**，与同属茶树 13 条对齐（3+5+5 残迹）——注释漏检为主，不是家族真小也不是组装碎）。**口诀：数量异常先走 4.6b 双轨道排除注释/组装，再谈生物学**。
6. **冻结后改成员**：一切下游分析以冻结表为准；要改 = 重跑下游 + 说明理由，不是悄悄改表。

## 13.6.1 三种典型异常结果（对号入座，别慌）

| 你的现象 | 原因 | 处理 | 回哪查 |
|:--|:--|:--|:--|
| **案例 A：HMM 候选 500 个以上** | 模型是超家族级过宽 / 误用域模型当家族模型 / 蛋白组含大量异构体 | ① 确认用的是家族 HMM 不是 Pfam 超家族条目；② 先看核心域验证（4.3）能砍多少——候选多本身不是错误，真伪靠域判定 | 4.2 排查表 / 4.3 |
| **案例 B：BLAST 第二召回 0 命中** | 参考集与目标物种亲缘很远 / blastp 库建错 / query 是 DNA | ① `makeblastdb` 生成的库文件在不在；② 抽一条参考蛋白去 NCBI BLAST 网页验证有同源；③ 若参考太远，换近缘参考或只靠 HMM 召回（并集 = HMM 单源也合法） | 4.2b / 3.4 |
| **案例 C：核心域验证 0 条或全缺 [核心域2]** | .hmm 下成 HTML / 候选序列为空 / 你的家族判定模板选错域 | ① 检查两个 .hmm 首行 HMMER3/f；② 用 1.2 的判定模板核对你家族到底该看哪两个域；③ 单域家族看 4.3b（域即家族） | 3.5 / 1.2 / 4.3 错误表 |
| **案例 D：成员数远低于近缘物种（二倍体只有 2-3 条，近缘普遍 7-13）** | **不一定是家族真小/组装碎——先怀疑注释漏检**（自动注释器对"跨外显子基序、短、低表达、无同源 hints"的家族必漏，见 4.6b） | 走 **4.6b 双轨道**：S9 六框直扫 + S10 剪接重建排除注释/组装因素，再谈生物学（油茶 LOG：CON 注释仅 3 条曾被误判"缺整组拷贝"，双轨道找回 5 个 → 8 座位，与同属茶树 13 对齐） | 4.6b / 13.6 第 5 点 |

> 四个案例共同原则：**异常数量是 QC 触发信号，不是成员标准**——先排查数据/模型/ID，数量少时先走 4.6b 双轨道排除注释/组装，别急着删成员或改阈值或下"家族真小"结论。

## 13.7 下一步（成员确定后，如需）

| 分析 | 工具（TBtools/tbtools） | 产出 |
|:--|:--|:--|
| 亚家族分类 | 树 + iTOL 着色 | 亚家族划分（按系统发育；实例：ARR-B 分 I/II/III） |
| 基因结构图 | genestructure / Gene Structure View | 论文 Fig |
| 染色体定位图 | genelocgff / Gene Location | 论文 Fig |
| 基序分布图 | motif / Amazing Optional Gene Viewer | 论文 Fig |
| 启动子顺式元件 | 在线 PlantCARE / TBtools 提取上游 | cis 分析 |
| 共线性 | mcscanx / dualsyn / dotplot / MCScanX GUI | 重复类型 |
| 表达 | extractFasta + heatmap / 在线转录组 | 表达热图 |
| 富集 | goEnrich / keggEnrich / GO and KEGG GUI | 功能富集 |

## 13.8 中英对照速查（写论文/与国外合作者沟通用）

| 中文 | English | 上下文 |
|:--|:--|:--|
| 基因家族鉴定 | gene family identification | 全文 |
| 候选基因 | candidate gene | Step 2 |
| 结构域验证 | domain verification | Step 3 |
| 双结构域 | dual-domain / two conserved domains | Step 3 |
| 核心域 1（示例：接收域） | receiver domain ([核心域1], [域1]) | Step 3 |
| DNA 结合域 | DNA-binding domain ([核心域2], [域2]) | Step 3 |
| 家族 HMM 模型 | family HMM profile | Step 1 |
| 全蛋白组搜索 | whole-proteome search | Step 2 |
| E 值阈值 | E-value cutoff | Step 2/3 |
| 蛋白完整性 | protein integrity (no internal stop codon) | Step 4 |
| 基因结构核对 | gene structure verification | Step 5 |
| 查漏 | exhaustive re-scan / salvage search | Step 6 |
| 边界成员 | boundary member | Step 6 |
| 直系同源组 | orthogroup (OG) | Step 7 |
| 双向最优比对 | reciprocal best hit (RBH) | Step 8 |
| 保守基序 | conserved motif | Step 9 |
| 系统发育树 | phylogenetic tree | Step 10 |
| 支持率 | bootstrap support | Step 10 |
| 集合冻结 | final gene set | Step 12 |
| 证据矩阵 | evidence matrix (core criteria + supporting evidence) | 全文 |
| 净化选择 | purifying selection (ω<1) | Ka/Ks |
| 标志结构域验证 | core-domain verification | Step 3 |

## 13.9 与旧版（WSL 版）文档的关系

如果你之前拿到过 `[目标物种][家族名]鉴定手把手教程_完整版.md`（v2，主推 WSL2）——**本版（v3.3-Win）与之的区别**（13.9 为历史版本关系说明，当前环境以 13.9.1 为准）：

| 维度 | v2（WSL 版） | 本版 v3.3-Win |
|:--|:--|:--|
| 运行环境 | WSL2 + Bioconda | 纯 Windows（Java+Python+TBtools） |
| 主工具 | Linux 命令行全套 | TBtools GUI + tbtools-cli |
| HMMER | conda 装 | HMMER（pyhmmer 内核，见 2.6） |
| Exonerate | protein-to-genome 独立验证 | GFF 注释一致性核对（**二者不等价**，见 4.5） |
| 建树 | iqtree 命令 | tbtools one-step / TBtools 一键建树 |
| 绘图 | 命令行 | TBtools GUI 点选 |
| 适用 | 想完整复刻油茶服务器流程 | 全程 Windows、零 Linux |

两版**方法论一致**（多源召回 + 证据验证 + 边界决策），只是实现工具不同；结果应互相可比。

---

### 13.9.1 当前环境基线（v3.3-Win，2026-10-02 封版）

- **Current validated baseline（v3.3 当前基线）**：Windows 11 + Java 17 + Python 3.12 + TBtools-II（以 `fetch-jar` 实取为准）+ **tbtools-cli 1.4.23** + HMMER（pyhmmer 内核 0.12.3 兼容层）+ NCBI BLAST+ 2.x。命令契约一律以本机 `tool-describe --json` 为准。
- **Historical validation（历史实测）**：tbtools-cli v1.3.0→v1.4.x 区间（缺陷已修）；TBtools-II 教程验证环境曾观测到 2.475（**Historical observed baseline**）；当前官方最新 release 为 **2.515**——一律以 fetch-jar 实取 + `tbtools doctor` 为准。
- 本文为单一线性教材：第 0-13 章；方法学 = 多源召回（HMM ∪ BLAST ∪ tblastn）+ 核心归属条件（A 家族 HMM、B 核心域）+ 数据质量 QC（C 注释一致性）+ 支持证据综合（standard/boundary/unresolved/exclude）+ 边界成员决策。


## 13.10 【实例】芝麻 ARR-B 实跑验证（2026-09-24，Windows 11 实跑——对通用流程的完整验证）

> ⚠️ **本节所有数字（172/18/14/3 等）= 芝麻实例，不是你的目标值**；跑自己的物种时以 13.4.1 检查点为准。

> 对本文档主链 4.1-4.12 的完整实跑（配套：《ARR-B_鉴定实跑_完整文档.md》环境/Bug/复现手册；《ARR-B_完整鉴定过程.md》《ARR-B_总集文档.md》方法/结果权威记录）。**本节的数字就是芝麻真实预期**。

| 环节 | 实跑结果 |
|:--|:--|
| 芝麻蛋白组（GCF_000512975.1_S_indicum_v1.0） | 35,410 条 |
| ARR-B 参考集 | 148 条（7 物种 PlantTFDB） |
| 家族 HMM 初筛（E<1e-3，14 秒） | 172 候选；blastp 并集后仍 172（本次 blast 为 HMM 子集） |
| 双域（REC 65 ∩ MYB 124） | **18 条**；仅 REC 47 排除（A 型/超家族成员）、仅 MYB 106、无域 1 |
| 完整性 | 无内部终止、无 X；287-707 aa |
| tblastn 全基因组查漏（E<1e-5） | 18/18 回命中自身位点；**无独立新位点** |
| RBH（vs 拟南芥 RefSeq 48,265 条） | 严格互指 3/18（**历史实跑口径 = 成员 vs 拟南芥全蛋白组；通用教程 4.8 已改为完整蛋白组↔完整蛋白组 + 成员筛选**；不严格互指 ≠ 由 RBH 证明 orthology——RBH 始终是支持证据） |
| 系统发育（IQ-TREE） | 最佳模型 JTT+F+I+G4；18 成员单系、无超家族混入 |
| **最终集合** | **18 条蛋白 = 14 个基因座：17 standard + 1 boundary**（XP_020549869.1，287 aa 显著偏短 → boundary，待 CDS 完整性/表达核对） |

**配套结论**：家族规模表述建议 "14 个 SiARR-B 基因（18 条转录本/蛋白）"（3 个位点产多条异构体；LOC105172165/166 为串联重复对；1 个位点位于未挂载支架 NW_011628044.1）。

**实跑发现的教程勘误（已在本文档修正）**：① HMMER 官方无 Windows 64 位二进制 → 2.6 改 pyhmmer 内核方案；② jar 版本以 `tbtools fetch-jar` 实取为准（教程验证环境曾实测 2.475，属 historical；当前官方最新 2.515），不存在"必须某版本"；③ NCBI 目录名 `GCF_000512975.1_S_indicum_v1.0`（旧 ASM51297v1 404）；④ 部分引擎为 ArgsParser（--key value）风格，位置参数静默零输出 → 4.0.1 + 命令已改。

**实跑历史记录：tbtools-cli 缺陷（v1.3.0 时代，1.4.x 已修；仅作历史参考，非当前版本行为）**：① 桥编译缺 `-encoding UTF-8`（中文 Windows 全灭，P0）；② 错误通道 GBK 自崩；③ recipBlast 位置参数未绑定（静默空跑，手动 BLAST+ 退路参考 4.8 / 13.10）。


## 13.11 实战避坑清单（六项目实战沉淀，一条规则 = 一个踩过的坑）

> 本教程由六个真实项目的实跑迭代而成。下表把每个项目贡献的**规则级教训**汇总成一页——动手前扫一眼，能避开 90% 的坑。

| # | 规则（教训） | 来源项目 | 教程落点 |
|:-:|:--|:--|:--|
| 1 | 家族标志域编号必须用 UniProt 代表蛋白交叉注释反查，**不要背**（PF05691 曾张冠李戴为棉子糖合酶） | 油茶 LOG | 1.2 ④ |
| 2 | Pfam 无专属条目时看 InterPro 贡献成员库——**非 Pfam（如 NCBIFam）则 Pfam 多半只有超家族宽模型，须自建**（LOG：IPR005269→TIGR00730；PF03641 过宽） | LOG | 1.2 ⑤ |
| 3 | 超家族级 HMM 直接做家族鉴定 → **真假分数重叠、假阳性可高于真成员**（LOG 定量：157-171 vs 100-160，YvdD>OsLOG） | LOG-HMM 专项 | 1.2 ⑤ / 4.1 验证三步 |
| 4 | 自建 HMM 必须三验证：**自检回搜 + 负对照 + 与超家族模型并行对比区分度** | LOG-HMM 专项 | 4.1 🧪 |
| 5 | 单域家族（无多域硬条件兜底）：**邻近家族减法复核 = 必做**（WOX：2 条 HD-Zip IV 四域混入靠此剔除） | 紫苏 WOX | 4.3b-2 |
| 6 | 反筛要覆盖**超家族全部成员家族**，不是单诱饵/单官方模型——"第二模型复确认会放行的错误，竞争性归属能抓住"（scaffold_11 曾过 TIGR00730 仍被聚类归属移出） | LOG | 4.3b-3 |
| 7 | 反筛两层：**Pfam 全库面板**（30,134 HMM 批量，30 秒/组合）+ **自建聚类 HMM 面板**（35% 聚类→簇→竞争归属） | 油茶 LOG S3y | 4.3b-3 |
| 8 | 初筛先松后紧（E=1e-3 起步），不要一上来严格阈值漏掉歧化成员 | ARR-B / WOX / LOG | 1.8 参数表 |
| 9 | 注释一致性（CDS→翻译→比对）是**数据质量控制，不是独立基因座证据**（同源注释互证）；失败先查 ID/转录本/版本 | ARR-B 终审 | 1.5 C |
| 10 | tblastn/直扫命中 ≠ 新成员：**必须 ORF 验证**（E 值显著只证明"曾有过同源"；**完整 ORF + 家族典型长度/核心域覆盖 + 无明确破坏证据**才算候选——≥120 aa 是 LOG 实例经验值，非通用标准） | LOG | 4.6 / 4.6b |
| 11 | 全基因组直扫：numpy 向量化六框翻译 + 90 kb 分块（HMMER 10 万残基上限）+ 双模型 + 基因座聚类 + ORF 验证；**覆盖并集不能替代 ORF 验证**（伪基因座 116 ≥ 真基因 115） | LOG | 4.6b |
| 12 | "成员数少 ≠ 家族小"：数量异常先走 S9+S10 双轨道排除注释/组装再下结论（**2026-10-09 修正**：CON 注释 3 被误判"缺整组拷贝"，S10 恢复 5 → 8 座位，与茶树 13 对齐——注释漏检为主，非组装碎非家族真小） | 油茶 LOG S10 | 13.6 第 5 点 / 4.6b |
| 13 | 静默 0 结果先核对**输出解析与 outfmt 列定义**（8 列按 9 列解析全丢），解析前打印首行列数断言 | LOG | 4.0.1 |
| 14 | pyhmmer：无 hmmbuild 子命令（wheel 只含 7 个）→ plan7.Builder API（`build_msa(msa, Background)` 三元组、MSA 需 name、无 cpus）；**批量建模"建与写分离"**（build+write 后再读 MSA 静默 SIGTERM 硬崩）；`len(msa)`=列数 | LOG | 2.6 路 1 |
| 15 | InterPro wwwapi 的 .hmm 是 **gzip 流**（先看魔数 1f 8b）；pyhmmer 读 .gz 依赖系统 gzip 命令（Windows 无）→ 先解压 | LOG | 3.5 / C8 |
| 16 | Windows 保留设备名不能做目录（CON/PRN/AUX/NUL/COM1-9）——WinError 267 | LOG | 3.2 |
| 17 | 断点续传防并发写 + 流式 CRC 校验（gzip 自带 CRC32）；续传后大小 > 远端 = 重复投递，按字节定位损坏 | LOG | 3.x 下载 |
| 18 | EBI REST：结果端点以 `/resulttypes` 为准（ClustalO FASTA 在 `fa`，aln-fasta 400；`out` 是日志） | LOG | 4.1 |
| 19 | RBH 是直系同源**支持证据**不单独证明严格一对一（WGD/旁系扩张致严格互指率低，按基因级解读）；**且必须在两个完整蛋白组之间计算，成员只作结果筛选**（成员子集作反向库会制造假互指） | ARR-B 终审 / 封版审查 P0 | 1.5 F / 4.8 / 10.10 |
| 20 | 证据矩阵四分类 standard/boundary/unresolved/exclude + 边界成员单独标注（不静默删除） | ARR-B/WOX/LOG 全部 | 1.5 / 4.11 |
| 21 | 下载后检查字节数>0 + 魔数/哈希校验（3xx 重定向目标不可达会静默 0 字节） | LOG | 3.x |
| 22 | 国内网络：GitHub release 直链常被阻断 → 镜像/TUNA/fetch-jar/在线服务；figshare 公开 vs 私链可达性不同 | LOG | 2.4 / 3.x |
| 23 | 支持证据**案例级替代实验**（LOG 5.10d，**不等价于正式直系同源聚类，不得替代 OG 结果**）：G FastTree+外群距离判据；E pident≥40%+覆盖≥70% 是**相似性近似、不是 orthogroup**；H 保守列替代 MEME；I NG86 | LOG | 4.9/4.10 |
| 24 | 重建树/批量分析前删比对缓存（缓存不感知序列集变化 → `target not in this tree`） | LOG | 4.10 |
| 25 | **家族基序可能跨剪接边界**（分居两外显子）——六框翻译搜基序对剪接基因**系统性失效**：真伪判据必须在 HSP 链重建后的拼接 CDS 上验（或参考基序区段的基因组比对），不能看六框残基 | 油茶 LOG D8 | 4.6b S10c |
| 26 | HSP 剪接重建必须**逐外显子用自身读码框**（各外显子相位随坐标变化，frames 常混合 1/2/3）；相邻不同 frame 的 HSP 不得合并（间隔 ≤60 bp 且同 frame 才并）——否则重建蛋白整体报废 | 油茶 LOG S10 | 4.6b S10b |
| 27 | 草图组装的**同序列重复要折叠**：同 scaffold 上 ORF 100% 相同、HMM E 值一字不差 = 组装重复，不是独立基因座位（GWHERBT 7 条按此折叠） | 油茶 LOG S10 | 4.6b S10a |
| 28 | **提取窗口 ±1kb 会截 5′ 外显子**："候选但模型缺陷（core 命中、基序在位、0 终止子、len<120）"可能是提取伪影而非真缺陷——先换**宽窗口（±6kb）**重提取：ORF 恢复增长 = 伪影按真基因重建；**仍不增长 = 组装层面 5′ 外显子真实缺失**，维持截短定性（±6kb 复验找回 7 个被误杀真座位） | 油茶 LOG S11x/S11y | 4.6b S10b |
| 29 | **跨组装交叉验证必须统一坐标命名空间**：扫作者组装（chr1-15）得座位表，却拿另一套组装（NCBI CM*）提取序列 → 35 个座位全部"序列缺失"、从未被重建（A 层硬伤）——提取前先核对 seqid 归属哪套组装；多套组装共存时（如作者 + NCBI）严格分开，或做坐标 lift-over | 油茶 LOG S12 | 4.6b / 3.3 |

---


## 13.12 HMMER 兼容层脚本全文（🟡 自动化路线用；基于 pyhmmer 的 HMMER-compatible tutorial wrapper，教程专用，≠ 官方 HMMER）

> 两个脚本存到 `scripts\`；注册与自检命令见 2.6。**参数与真实 HMMER 一致，但为教程专用子集**：只实现 `-h`/`-E`/`-o`/`--tblout`/`--domtblout`/`--cpu`(忽略)；未实现参数直接报错。

```python
# hmmsearch_win.py —— 教程专用 hmmsearch 兼容层（官方 pyhmmer API：SequenceFile；只实现 -h/-E/-o/--tblout/--domtblout/--cpu-忽略）
# 用法（与 HMMER 一致）：python hmmsearch_win.py [选项] <model.hmm> <seqs.fa>
import sys, pyhmmer
from pyhmmer.easel import SequenceFile, Alphabet
from pyhmmer.plan7 import HMMFile, Pipeline

def usage():
    print("用法: python hmmsearch_win.py [-E 阈值] [-o out.txt] [--tblout f] [--domtblout f] <model.hmm> <seqs.fa>")
    sys.exit(0)

def main():
    argv = sys.argv[1:]
    if "-h" in argv or "--help" in argv: usage()
    E, out_o, tblout, domtblout = 1e-3, None, None, None
    pos, i = [], 0
    while i < len(argv):
        a = argv[i]
        if a == "-E": E = float(argv[i+1]); i += 2   # 只实现 -E；-T 未实现
        elif a == "-o": out_o = argv[i+1]; i += 2
        elif a == "--tblout": tblout = argv[i+1]; i += 2
        elif a == "--domtblout": domtblout = argv[i+1]; i += 2
        elif a == "--cpu": i += 2   # pyhmmer 单线程，明确忽略
        elif a.startswith("-"):
            raise SystemExit(f"[hmmsearch_win] 不支持的参数: {a} —— 教程专用兼容层只实现 -h/-E/-o/--tblout/--domtblout/--cpu(忽略)，未实现参数直接报错，绝不静默跳过")
        else:
            pos.append(a); i += 1
    if len(pos) < 2: usage()
    model, target = pos[0], pos[1]
    A = Alphabet.amino()
    hmm = next(HMMFile(model))
    with SequenceFile(target, digital=True, alphabet=A) as seq_file:
        hits = Pipeline(A, E=E).search_hmm(hmm, seq_file)
    if domtblout:
        with open(domtblout, "wb") as f: hits.write(f, format="domains")
    if tblout:
        with open(tblout, "w") as f:
            f.write("#target_name\tfull_sequence_E-value\tscore\n")
            for h in hits: f.write(h.name.decode() + "\t" + f"{h.evalue:.2e}" + "\t" + f"{h.score:.1f}" + "\n")
    if out_o:
        with open(out_o, "w") as f:
            f.write("Query: " + model + "  (pyhmmer 兼容层)   target: " + target + "   E<=" + f"{E:.0e}" + "\n")
            f.write("Scores for complete sequences:\ntarget name          full sequence E-value    score\n")
            for h in hits: f.write(f"{h.name.decode():<20} {h.evalue:.2e}    {h.score:.1f}" + "\n")
    print(f"# hits: {len(hits)}  (E<={E:.0e})")
if __name__ == "__main__": main()
```

```python
# hmmbuild_win.py —— pyhmmer plan7.Builder 建 HMM 兼容层（官方 pyhmmer API：MSAFile）
# 用法（与 HMMER 一致）：python hmmbuild_win.py <out.hmm> <alignment.aln>
import sys, pyhmmer
from pyhmmer.easel import MSAFile, Alphabet
from pyhmmer.plan7 import Builder, Background

def main():
    if "-h" in sys.argv or "--help" in sys.argv or len(sys.argv) < 3:
        print("用法: python hmmbuild_win.py <out.hmm> <alignment.aln>")
        sys.exit(0 if "-h" in sys.argv else 1)
    out_hmm, aln = sys.argv[1], sys.argv[2]
    A = Alphabet.amino()
    # 官方 0.12.x 形态：MSAFile(digital=True) → build_msa
    with MSAFile(aln, digital=True, alphabet=A) as msa_file:
        msa = msa_file.read()
    if not msa.name: msa.name = b"family"
    hmm, _, _ = Builder(A).build_msa(msa, Background(A))
    with open(out_hmm, "wb") as f: hmm.write(f)
    print("HMM written:", out_hmm)
if __name__ == "__main__": main()
```
## 13.13 pyhmmer API 开发者说明（🔴 普通读者跳过）

**🔴 开发者说明（pyhmmer API 细节，普通读者跳过）**：建 HMM 需要 `pyhmmer.plan7.Builder`——`Builder(alphabet).build_msa(msa, background)` 第二参数是 `pyhmmer.plan7.Background(alphabet)`（不是参考序列），返回 `(hmm, profile, stats)` 三元组；MSA 必须先设 `msa.name = b"<fam>_family"`（否则报 Unable to name the HMM）；`Pipeline(alphabet, E=...)` 与 `search_hmm` 不接受 `cpus`（单线程）；批量建模坑：同进程多次 build + `hmm.write()` 后再读 MSA 会静默 SIGTERM 硬崩（先全部内存建完 → 内存扫描 → 写盘放最后）；个别簇模型 `hmm.write()` 会无限挂起（内存构建直接使用）；`len(msa)` 是列数不是序列数（用 `msa.sequences`）；Pfam 全库批量反扫用 `pyhmmer.hmmer.hmmsearch(hmms, seqs, cpus=8)` 批量接口。

*第 13 章完。全套 14 章（0-13）+ 六项目实跑沉淀，可独立交付。跑的过程中任何一步卡住，对照第 6/11 章找答案；找不到就带着报错原文和上一步的检查点结果来问。祝顺利！*

---
