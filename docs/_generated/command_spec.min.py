'command_spec.py — 统一命令模型(CommandSpec, 第八轮评审核心建议骨架)。\n\n目标: 所有命令产物(metadata/docs/help/search/统计)从单一 CommandSpec 模型派生,\n不再各自从 ENGINE_REGISTRY / CLI_TOOLS / cli.py / CATEGORY_MAP 分散读取。\n\n当前为兼容层骨架: 从现有注册源构建统一 specs(不改运行时行为),\ngen_metadata 与后续工具以 specs 为唯一输入。\n'
import os
from dataclasses import dataclass, field
from tbtools_cli import auto_commands as _ac
from tbtools_cli.cli_tools_registry import CLI_TOOLS
from tbtools_cli.cli_load import CATEGORY_MAP
class ParamSpec():
    """命令参数定义(评审 #31 Tool Contract: 类型/默认值/是否必填)"""

class InputSpec():
    """命令输入定义(二期 schema: 类型/格式/必填)"""

class InvocationSpec():
    """
    调用契约(评审 #70 P0-1 Contract Compiler):
把 CommandSpec 的 inputs/outputs/parameters 编译成精确 argv 布局——
消灭 {input}/$step.output/args[-1] 的三层猜测。

布局约定(与现有引擎一致): [flag 参数对...] [输入(按声明序)] [输出路径]
    """

def build_argv(self, inputs: list, parameters: dict, output: str):
        """
        编译精确 argv:
inputs: 按 InputSpec 声明序的路径列表
parameters: {contract 名: 值}(自动翻译 cli_name + 类型验证 + bool flag 形式)
output: 输出路径(末位)
        """
    ...
class CommandSpec():
    """单一命令定义(第八轮评审 CommandSpec 模型)"""

@property
def output_formats(self):
        """唯一 output truth 访问口(评审 #94 P0-1): output_slots 优先,outputs 兜底。"""
    ...
@property
def invocation(self):
        """调用契约投影(评审 #70): inputs+parameters → 可编译 argv 的 InvocationSpec。"""
    ...
KNOWN_NAMED_FLAGS = {'venn2': {'inputs': {'list1': '--List1', 'list2': '--List2'}, 'output': '--graph'}, 'venn3': {'inputs': {'list1': '--List1', 'list2': '--List2', 'list3': '--List3'}, 'output': '--graph'}, 'recipBlast': {'inputs': {'query': '--querySeqFile', 'subject': '--subjectSeqFile'}, 'output': '--outDirAndPrefix'}, 'tpmCalc': {'inputs': {'counts': '--countsTable', 'lenInfo': '--lenInfo'}, 'output': '--outTable'}, 'autoMakeBlastDb': {'inputs': {'fasta': '--inFasta'}, 'output': '--outBase'}}
_CONTRACTS_CACHE: dict = {}
_CONTRACTS_MTIME: tuple = ()
def load_contracts():
    """
    加载 contracts/tools/*.yaml(评审 #110 建议③: YAML 是 gen_metadata 导出的**生成快照/覆盖层**,
代码真源(KNOWN_*/ENGINE_REGISTRY/CLI_TOOLS)优先——不再声称 YAML 声明优先, 防双向覆盖复发)。
返回 {name: {inputs/outputs/parameters/capabilities/layout/...}}。
    """

    ...
_CONTRACTS_ERRORS: list = []
def contract_load_errors():
    """YAML 契约加载错误(评审 #90 P1-1): doctor/validate 可报告。"""

    ...
def _apply_contract_overlay(spec):
    """
    YAML 快照校验层(评审 #111 P0-1: Contract Integrity Freeze)。

实测: 0 个工具依赖 YAML 兜底(全部 inputs/outputs/parameters/layout 均为代码声明+
快照双有)——overlay 从此**不再覆盖 runtime truth**, 只做一致性校验:
  - YAML 与代码一致 → 忽略(快照是导出物, 代码为准)
  - 不一致 → warn(快照过期, 提示重跑 gen_metadata; runtime 用代码真源)
防止"开发者改代码未重跑 gen_metadata → 旧 YAML 静默回退 runtime"。
    """

    ...
class OutputSpec():
    """输出槽位定义(评审 #86 P1-5): semantic matching 需要 output-slot → input-slot。"""

KNOWN_OUTPUT_SLOTS = {'muscle': [OutputSpec('aln', format='fasta', content_type='alignment')], 'trimal': [OutputSpec('aln', format='fasta', content_type='alignment')], 'sixframe': [OutputSpec('pep', format='fasta', content_type='protein')], 'pep2codon': [OutputSpec('cds', format='fasta', content_type='dna')], 'iqtree': [OutputSpec('tree', format='nwk', content_type='tree')], 'mcscanx': [OutputSpec('collinearity', format='tsv', content_type='table')], 'recipBlast': [OutputSpec('result', format='tsv', content_type='table')], 'volcano': [OutputSpec('plot', format='svg', content_type='plot')]}
KNOWN_INPUT_CONTENT_TYPES = {'pep2codon': {'cds': 'dna', 'pep_aln': 'protein'}, 'sixframe': {'inFa': 'dna', 'dna': 'dna', 'pep': 'dna'}, 'recipBlast': {'query': 'protein', 'subject': 'protein'}, 'autoMakeBlastDb': {'fasta': 'protein'}, 'dualsyn': {'gff': 'annotation', 'collinearity': 'table'}, 'mcscanx': {'gff': 'annotation', 'blast': 'table'}}
KNOWN_OUTPUT_CONTENT_TYPES = {'muscle': 'alignment', 'trimal': 'alignment', 'sixframe': 'protein', 'pep2codon': 'dna', 'blastp': 'table', 'blastn': 'table', 'diamond': 'table', 'recipBlast': 'table', 'mcscanx': 'table', 'hmmsearch': 'table', 'iqtree': 'tree', 'phylotree': 'tree', 'fasttree': 'tree'}
KNOWN_CONTENT_TYPES = {'muscle': 'sequence', 'trimal': 'alignment', 'iqtree': 'alignment', 'phylotree': 'alignment', 'blastp': 'protein', 'blastn': 'dna', 'diamond': 'protein', 'recipBlast': 'protein', 'hmmsearch': 'protein', 'simpleHmmscan': 'protein', 'pep2codon': 'protein', 'sixframe': 'dna', 'longestorf': 'dna', 'cpg': 'dna', 'seqlogo': 'alignment', 'msa': 'alignment', 'genestructure': 'annotation', 'gxfSplit': 'annotation', 'volcano': 'table', 'dehist': 'table', 'hclust': 'table', 'barplot': 'table', 'heatmap': 'table', 'goEnrich': 'table', 'keggEnrich': 'table', 'gsea': 'table', 'mcscanx': 'table', 'dualsyn': 'table', 'fasta2phy': 'dna'}
KNOWN_SCHEMAS = {'volcano': ([InputSpec('deg', format='tsv', note='GeneID\tLog2FC\tpvalue', columns=['GeneID', 'Log2FC', 'pvalue'])], ['svg']), 'heatmap': ([InputSpec('matrix', format='tsv', note='首列 gene ID', columns=['gene_id'])], ['svg']), 'hclust': ([InputSpec('distance', format='tsv', note='三列距离', columns=['GeneA', 'GeneB', 'distance'])], ['svg']), 'venn2': ([InputSpec('list1', format='txt'), InputSpec('list2', format='txt')], ['svg']), 'msy': ([InputSpec('pos', format='tsv', note='Chr\tGene\tStart\tEnd'), InputSpec('links', format='tsv'), InputSpec('layout', format='txt')], ['svg']), 'genestructure': ([InputSpec('gff', format='gff3'), InputSpec('ids', format='txt')], ['svg']), 'motif': ([InputSpec('meme_xml', format='xml'), InputSpec('ids', format='txt')], ['svg']), 'peaktss': ([InputSpec('gxf', format='gff3'), InputSpec('peaks', format='tsv', note='MACS2, 坐标须百万级(bin 0 边界避让)')], ['svg']), 'tableMerge': ([InputSpec('tables', format='tsv', note='多个输入表')], ['tsv']), 'qdot': ([InputSpec('gff', format='tsv', note='4 列简化: Chr\tGene\tStart\tEnd')], ['svg']), 'dehist': ([InputSpec('deg', format='tsv', note='DEG 表', columns=['GeneID', 'Log2FC', 'pvalue'])], ['svg']), 'pca': ([InputSpec('matrix', format='tsv', note='首列 gene ID', columns=['gene_id'])], ['svg']), 'barplot': ([InputSpec('enrichment', format='tsv', note='富集表', columns=['Term', 'Pvalue'])], ['svg']), 'circos': ([InputSpec('chrLen', format='tsv'), InputSpec('link', format='tsv'), InputSpec('genePos', format='tsv')], ['svg']), 'dotplot': ([InputSpec('gff', format='tsv', note='4 列简化'), InputSpec('pairs', format='tsv')], ['svg']), 'dualsyn': ([InputSpec('gff', format='tsv', note='简化 GFF'), InputSpec('pairs', format='tsv')], ['svg']), 'mcscanx': ([InputSpec('gff', format='tsv', note='chr\tgene\tstart\tend'), InputSpec('blast', format='tsv', note='tab6')], ['tsv']), 'iqtree': ([InputSpec('aln', format='fasta')], ['nwk', 'treefile']), 'muscle': ([InputSpec('fasta', format='fasta')], ['aln']), 'trimal': ([InputSpec('aln', format='fasta')], ['aln']), 'blastp': ([InputSpec('query', format='fasta'), InputSpec('db', format='fasta')], ['out']), 'sixframe': ([InputSpec('dna', format='fasta', note='DNA 序列输入(6-frame 翻译为蛋白)')], ['fasta']), 'longestorf': ([InputSpec('seq', format='fasta', note='核酸输入')], ['fa']), 'seqlogo': ([InputSpec('seqs', format='fasta')], ['svg']), 'stat-fasta': ([InputSpec('fasta', format='fasta')], ['xls']), 'venn3': ([InputSpec('list1', format='txt'), InputSpec('list2', format='txt'), InputSpec('list3', format='txt')], ['svg']), 'venn4': ([InputSpec('list1', format='txt'), InputSpec('list2', format='txt'), InputSpec('list3', format='txt'), InputSpec('list4', format='txt')], ['svg']), 'upset': ([InputSpec('sets', format='txt', note='多个集合文件, 末参为输出')], ['svg']), 'tpmCalc': ([InputSpec('counts', format='tsv', note='counts 表', cli_name='--countsTable'), InputSpec('lenInfo', format='tsv', columns=['GeneID', 'Length'], cli_name='--lenInfo')], ['tsv']), 'gxfSplit': ([InputSpec('gff', format='gff3')], ['tsv']), 'gxfAttr': ([InputSpec('gff', format='gff3')], ['tsv']), 'gxfIdAppender': ([InputSpec('gff', format='gff3')], ['gff3']), 'recipBlast': ([InputSpec('query', format='fasta'), InputSpec('subject', format='fasta')], ['tsv']), 'autoMakeBlastDb': ([InputSpec('fasta', format='fasta')], ['db']), 'genelocgff': ([InputSpec('gff', format='gff3'), InputSpec('ids', format='txt')], ['svg']), 'treeRooting': ([InputSpec('nwk', format='newick', note='需枝长')], ['nwk']), 'memerun': ([InputSpec('fasta', format='fasta')], ['meme']), 'mastrun': ([InputSpec('meme', format='meme')], ['xml']), 'goEnrich': ([InputSpec('background', format='tsv'), InputSpec('target', format='tsv')], ['tsv']), 'keggEnrich': ([InputSpec('ref_keg', format='tsv', note='扁平 5 列 .keg: Knum/Desc/Pathway/SubClass/MainClass'), InputSpec('annotation', format='tsv', note='gene→K 对应表'), InputSpec('select_ids', format='txt', note='目标基因集每行一个')], ['xls']), 'gsea': ([InputSpec('expr', format='tsv'), InputSpec('cls', format='txt')], ['xls']), 'efpHeat': ([InputSpec('tga', format='tga', note='TrueColor type2'), InputSpec('expMat', format='tsv')], ['svg']), 'multiEfp': ([InputSpec('tga', format='tga'), InputSpec('expMat', format='tsv')], ['svg']), 'layoutheatmap': ([InputSpec('expr', format='tsv'), InputSpec('layout', format='tsv')], ['svg']), 'microsyn': ([InputSpec('gff', format='tsv', note='简化 GFF'), InputSpec('links', format='tsv')], ['svg']), 'multisyn': ([InputSpec('gff', format='tsv'), InputSpec('gxf_lst', format='txt')], ['svg']), 'pafviz': ([InputSpec('paf', format='tsv', note='PAF alignment table; 标准 12 核心列 + 可选附加列')], ['svg']), 'pafref': ([InputSpec('paf', format='tsv', note='含 cg:Z CIGAR')], ['svg']), 'peakanno': ([InputSpec('gxf', format='gff3', note='peaks 注释用 GXF'), InputSpec('peaks', format='tsv', note='MACS2, 坐标须百万级(bin 0 边界避让)')], ['tsv']), 'supercircos': ([InputSpec('config', format='txt', note='[chrLen] 等节')], ['svg']), 'gel': ([InputSpec('lanes', format='tsv', note='LaneLabels 逗号分隔')], ['svg']), 'plotrna': ([InputSpec('genome', format='fasta', note='基因组 fasta'), InputSpec('sam', format='tsv', note='SAM 比对文件')], ['pdf']), 'pep2codon': ([InputSpec('cds', format='fasta'), InputSpec('pep_aln', format='fasta')], ['fa']), 'mcscanxd': ([InputSpec('gff', format='tsv'), InputSpec('blast', format='tsv')], ['collinearity']), 'notung': ([InputSpec('tree', format='newick'), InputSpec('gene_tree', format='newick')], ['nwk']), 'newickRename': ([InputSpec('nwk', format='newick')], ['nwk']), 'hmmerSearch': ([InputSpec('hmm', format='hmm'), InputSpec('seq', format='fasta')], ['tsv']), 'memeViz': ([InputSpec('meme', format='meme')], ['svg']), 'kallisto': ([InputSpec('fastq', format='fastq', note='RNA-seq')], ['tsv']), 'tfbsShift': ([InputSpec('motif', format='meme')], ['tsv']), 'smart': ([InputSpec('seq', format='fasta')], ['tsv']), 'barplotter': ([InputSpec('gff', format='gff3', note='简化 GFF: chr\tgene\tend'), InputSpec('synteny', format='tsv', note='MCScanX collinearity 格式'), InputSpec('ctl', format='txt', note='4 行: xdim/ydim/xchr逗号分隔/ychr逗号分隔')], ['png']), 'calcRepeat': ([InputSpec('fasta', format='fasta')], ['tsv']), 'rnaplot': ([InputSpec('seq', format='fasta')], ['svg']), 'preparespecies': ([InputSpec('genome', format='fasta', cli_name='--inGenomeFa'), InputSpec('gff', format='gff3', cli_name='--inGXF')], ['fasta'])}
KNOWN_PARAMS = {'volcano': [ParamSpec('pval_cutoff', 'float', 0.05, cli_name='--pval-cutoff'), ParamSpec('fc_cutoff', 'float', 1.0, cli_name='--fc-cutoff'), ParamSpec('w', 'int', 1000), ParamSpec('h', 'int', 800)], 'heatmap': [ParamSpec('w', 'int', 1000), ParamSpec('h', 'int', 800), ParamSpec('log2', 'bool', False), ParamSpec('row_scale', 'bool', False)], 'hclust': [ParamSpec('w', 'int', 1000), ParamSpec('h', 'int', 800), ParamSpec('t', 'int', 4, note='线程')], 'genestructure': [ParamSpec('w', 'int', 1000), ParamSpec('h', 'int', 800), ParamSpec('genome', 'string', None, note='可选基因组 FASTA')], 'dehist': [ParamSpec('w', 'int', 1000), ParamSpec('h', 'int', 800)], 'mcscanx': [ParamSpec('t', 'int', 4), ParamSpec('w', 'int', 1000), ParamSpec('h', 'int', 800)], 'dualsyn': [ParamSpec('chr1', 'string', None, note='逗号分隔染色体'), ParamSpec('chr2', 'string', None)], 'iqtree': [ParamSpec('bb', 'int', 1000, note='UFBoot ≥1000'), ParamSpec('t', 'int', 4)]}
KNOWN_DEPENDENCIES_STRUCT = {'hmmsearch': [{'name': 'hmmer', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'hmmsearch', 'version_args': ['-h']}], 'simplehmmscan': [{'name': 'hmmer', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'hmmscan', 'version_args': ['-h']}], 'calcRepeat': [{'name': 'jellyfish', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'jellyfish', 'version_args': ['--version']}], 'rnaplot': [{'name': 'rnafold', 'type': 'binary', 'required': True, 'platforms': ['linux'], 'executable': 'RNAfold', 'version_args': ['--version']}], 'plotrna': [{'name': 'rnafold', 'type': 'binary', 'required': True, 'platforms': ['linux'], 'executable': 'RNAfold', 'version_args': ['--version']}], 'kallisto': [{'name': 'kallisto', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'kallisto', 'version_args': ['version']}], 'diamond': [{'name': 'diamond', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'diamond', 'version_args': ['--version']}], 'mcscanxd': [{'name': 'mcscanx', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'MCScanX', 'version_args': []}], 'blastp': [{'name': 'blast+', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'blastp', 'version_args': ['-version']}], 'blastn': [{'name': 'blast+', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'blastn', 'version_args': ['-version']}], 'muscle': [{'name': 'muscle', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'muscle', 'version_args': ['-version']}], 'mafft': [{'name': 'mafft', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'mafft', 'version_args': ['--version']}], 'iqtree': [{'name': 'iqtree2', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'iqtree2', 'version_args': ['--version']}], 'onesteptree': [{'name': 'iqtree2', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'iqtree2', 'version_args': ['--version']}], 'trimal': [{'name': 'trimal', 'type': 'binary', 'required': True, 'platforms': ['linux', 'macos'], 'executable': 'trimal', 'version_args': ['-version']}], 'taxparse': [{'name': 'internet', 'type': 'capability', 'required': True, 'platforms': ['linux', 'macos', 'windows']}], 'sraxml2tab': [{'name': 'internet', 'type': 'capability', 'required': False, 'platforms': ['linux', 'macos', 'windows']}]}
KNOWN_DEPENDENCIES: dict = {cmd: [str(d['name']) for d in deps] for cmd, deps in KNOWN_DEPENDENCIES_STRUCT.items()}
ONTOLOGY = {'alignment': 'sequence.alignment', 'expression_matrix': 'expression.matrix', 'gene_structure': 'annotation.gene_structure', 'translation': 'sequence.translation', 'extraction': 'sequence.extraction', 'conversion': 'sequence.conversion', 'sequence': 'sequence', 'homology': 'sequence.homology', 'hmm_scan': 'sequence.homology.hmm_scan', 'filtering': 'sequence.homology.filtering', 'reciprocal_best_hit': 'sequence.homology.reciprocal_best_hit', 'phylogeny': 'phylogeny', 'rooting': 'phylogeny.rooting', 'reconciliation': 'phylogeny.reconciliation', 'tree_building': 'phylogeny.tree-building', 'tree_editing': 'phylogeny.editing', 'synteny': 'genomics.synteny', 'collinearity': 'genomics.synteny', 'collinearity_detection': 'genomics.synteny.detection', 'microsynteny': 'genomics.synteny.microsynteny', 'annotation': 'genomics.annotation', 'gff_fixing': 'genomics.annotation.fixing', 'gff_ops': 'genomics.annotation.ops', 'genome_analysis': 'genomics', 'genome_circos': 'genomics.circos', 'expression': 'expression', 'differential_expression': 'expression.differential', 'normalization': 'expression.normalization', 'rna_seq': 'expression.rna-seq', 'quantification': 'expression.rna-seq.quantification', 'enrichment': 'expression.enrichment', 'gene_ontology': 'expression.enrichment.go', 'pathway': 'expression.enrichment.pathway', 'clustering': 'expression.clustering', 'distance': 'expression.clustering.distance', 'dimension_reduction': 'expression.dimension-reduction', 'statistics': 'expression.statistics', 'visualization': 'visualization', 'motif': 'sequence.motif', 'scanning': 'sequence.motif.scanning', 'discovery': 'sequence.motif.discovery', 'genome_scan': 'sequence.motif.genome-scan', 'domain': 'sequence.domain', 'orf_prediction': 'sequence.orf-prediction', 'chip_seq': 'chip-seq', 'peak_calling': 'chip-seq.peak-calling', 'peak_annotation': 'chip-seq.peak-annotation', 'assembly': 'genomics.assembly', 'ngs': 'sequence.ngs', 'preprocessing': 'sequence.ngs.preprocessing', 'set_operations': 'sets', 'table_operations': 'table', 'viral_analysis': 'virus'}
def expand_ontology(tags: list[str]):
    """
    平标签 → 含分层父链的全集(如 alignment → [sequence.alignment, sequence])。

Agent 用 'phylogeny' 查询时, 'phylogeny.tree-building' 也命中(父链展开)。
    """

    ...
GROUP_CAPABILITIES = {'expr': ['expression'], 'syn': ['synteny'], 'gxf': ['annotation'], 'table': ['table_operations'], 'fastq': ['ngs', 'sequence'], 'blast': ['homology'], 'asm': ['assembly'], 'chipseq': ['chip_seq'], 'tree': ['phylogeny'], 'seq': ['sequence'], 'efp': ['expression'], 'sets': ['set_operations'], 'enrich': ['enrichment'], 'virus': ['viral_analysis'], 'genome': ['genome_analysis'], 'assembly': ['assembly']}
KNOWN_RELATIONS = {'volcano': {'accepts': ['DEG_TABLE'], 'produces': ['VOLCANO_PLOT'], 'next_step': ['goEnrich', 'keggEnrich'], 'related_to': ['dehist', 'heatmap']}, 'dehist': {'accepts': ['DEG_TABLE'], 'produces': ['DEG_HISTOGRAM'], 'related_to': ['volcano']}, 'heatmap': {'accepts': ['EXPRESSION_MATRIX'], 'produces': ['HEATMAP'], 'next_step': ['hclust'], 'related_to': ['pca']}, 'pca': {'accepts': ['EXPRESSION_MATRIX'], 'produces': ['PCA_PLOT']}, 'hclust': {'accepts': ['DISTANCE_TABLE'], 'produces': ['DENDROGRAM'], 'related_to': ['heatmap']}, 'mcscanx': {'accepts': ['GFF', 'BLAST_TAB6'], 'produces': ['COLLINEARITY'], 'next_step': ['dualsyn', 'dotplot']}, 'dualsyn': {'accepts': ['SIMPLIFIED_GFF', 'COLLINEARITY'], 'produces': ['SYNTENY_PLOT']}, 'dotplot': {'accepts': ['SIMPLIFIED_GFF', 'COLLINEARITY'], 'produces': ['DOTPLOT']}, 'pafviz': {'accepts': ['PAF'], 'produces': ['SYNTENY_PLOT'], 'related_to': ['dualsyn', 'dotplot']}, 'pafref': {'accepts': ['PAF'], 'produces': ['PAF_REF_COVERAGE']}, 'muscle': {'accepts': ['FASTA'], 'produces': ['ALIGNMENT'], 'next_step': ['trimal', 'iqtree']}, 'trimal': {'accepts': ['ALIGNMENT'], 'produces': ['TRIMMED_ALIGNMENT'], 'next_step': ['iqtree']}, 'iqtree': {'accepts': ['ALIGNMENT'], 'produces': ['PHYLOGENY_NWK'], 'next_step': ['tree']}, 'tpmCalc': {'accepts': ['COUNTS_TABLE', 'GENE_LENGTH'], 'produces': ['TPM_TABLE'], 'next_step': ['pca', 'heatmap', 'volcano']}, 'gsea': {'accepts': ['EXPRESSION_TABLE', 'PHENOTYPE_CLS'], 'produces': ['GSEA_REPORT']}, 'genestructure': {'accepts': ['GFF3', 'GENE_ID_LIST'], 'produces': ['GENE_STRUCTURE_PLOT']}, 'kallisto': {'accepts': ['FASTQ'], 'produces': ['QUANT_TABLE'], 'next_step': ['tpmCalc']}, 'recipBlast': {'accepts': ['FASTA'], 'produces': ['BLAST_HITS', 'RBH_TABLE'], 'next_step': ['filterCScore'], 'related_to': ['twoSeqBlast']}, 'twoSeqBlast': {'accepts': ['FASTA'], 'produces': ['BLAST_HITS'], 'related_to': ['recipBlast']}, 'extractFasta': {'accepts': ['FASTA', 'GENE_ID_LIST'], 'produces': ['SEQUENCE_SUBSET', 'FASTA'], 'related_to': ['extractFastaSub']}, 'statFasta': {'accepts': ['FASTA'], 'produces': ['FASTA_STATS', 'TSV'], 'related_to': ['fastaExtract']}, 'dnDsCalculate': {'accepts': ['ALIGNMENT'], 'produces': ['KAKS_TABLE'], 'related_to': ['muscle']}, 'hmmsearch': {'accepts': ['FASTA', 'HMM_PROFILE'], 'produces': ['HMM_HITS', 'TSV']}, 'sixframe': {'accepts': ['DNA_FASTA'], 'produces': ['PROTEIN_FASTA'], 'related_to': ['longestorf']}, 'longestorf': {'accepts': ['DNA_FASTA'], 'produces': ['PROTEIN_FASTA'], 'related_to': ['sixframe']}, 'memerun': {'accepts': ['PROTEIN_FASTA'], 'produces': ['MEME_XML'], 'next_step': ['motif']}, 'tfbsShift': {'accepts': ['MEME_XML'], 'produces': ['TFBS_TABLE'], 'related_to': ['motif']}, 'pep2codon': {'accepts': ['PROTEIN_ALIGNMENT'], 'produces': ['CODON_ALIGNMENT'], 'related_to': ['muscle']}, 'structure': {'accepts': ['GFF3'], 'produces': ['GENE_STRUCTURE_PLOT'], 'related_to': ['genestructure']}, 'mastExtract': {'accepts': ['MEME_XML', 'HMM_HITS'], 'produces': ['SEQUENCE_SUBSET'], 'related_to': ['memerun']}, 'hmmerSearch': {'accepts': ['FASTA', 'HMM_PROFILE'], 'produces': ['HMM_HITS'], 'related_to': ['hmmsearch']}, 'calcRepeat': {'accepts': ['DNA_FASTA'], 'produces': ['REPEAT_SCAN'], 'related_to': ['careclassify']}, 'smart': {'accepts': ['PROTEIN_FASTA'], 'produces': ['DOMAIN_ANNOTATION'], 'related_to': ['cddmotif']}, 'memeViz': {'accepts': ['MEME_XML'], 'produces': ['MOTIF_PLOT'], 'related_to': ['memerun']}}
GROUP_RELATIONS = {'syn': {'accepts': ['SIMPLIFIED_GFF', 'COLLINEARITY'], 'produces': ['SYNTENY_PLOT'], 'next_step': ['dualsyn', 'dotplot'], 'related_to': ['mcscanx']}, 'expr': {'accepts': ['EXPRESSION_TABLE'], 'produces': ['PLOT'], 'related_to': ['volcano', 'heatmap']}, 'tree': {'accepts': ['ALIGNMENT', 'NEWICK'], 'produces': ['PHYLOGENY_NWK'], 'next_step': ['tree']}, 'seq': {'accepts': ['FASTA', 'GFF3'], 'produces': ['SEQUENCE_ARTIFACT'], 'related_to': ['muscle', 'trimal']}, 'gxf': {'accepts': ['GFF3'], 'produces': ['ANNOTATION_OUT']}, 'table': {'accepts': ['TABLE'], 'produces': ['TABLE_OUT']}, 'blast': {'accepts': ['FASTA'], 'produces': ['BLAST_HITS'], 'next_step': ['filterCScore']}, 'chipseq': {'accepts': ['ALIGNMENT', 'PEAKS'], 'produces': ['PEAK_ANNOTATION']}, 'fastq': {'accepts': ['FASTQ'], 'produces': ['SEQUENCE_ARTIFACT'], 'next_step': ['kallisto', 'tpmCalc']}, 'asm': {'accepts': ['GENOME', 'GFF'], 'produces': ['ASSEMBLY_OUT']}, 'virus': {'accepts': ['FASTA', 'REF_DB'], 'produces': ['VIRUS_ANNOTATION']}, 'efp': {'accepts': ['TGA', 'EXP_MATRIX'], 'produces': ['EFP_HEATMAP']}, 'sets': {'accepts': ['GENE_LISTS'], 'produces': ['SET_DIAGRAM'], 'related_to': ['venn2', 'venn3', 'upset']}, 'enrich': {'accepts': ['GENE_LISTS'], 'produces': ['ENRICHMENT_REPORT'], 'next_step': ['barplot']}, 'genome': {'accepts': ['GENOME'], 'produces': ['GENOME_OUT']}}
KNOWN_CAPABILITIES = {'volcano': ['differential_expression', 'visualization'], 'heatmap': ['expression_matrix', 'clustering', 'visualization'], 'dehist': ['differential_expression', 'visualization'], 'pca': ['dimension_reduction', 'expression_matrix'], 'hclust': ['clustering', 'distance'], 'genestructure': ['gene_structure', 'annotation', 'visualization'], 'seqlogo': ['motif', 'visualization'], 'msa': ['alignment', 'visualization'], 'motif': ['motif', 'visualization'], 'sixframe': ['translation', 'sequence'], 'longestorf': ['orf_prediction', 'sequence'], 'blastp': ['homology', 'alignment'], 'mcscanx': ['synteny', 'collinearity'], 'dualsyn': ['synteny', 'visualization'], 'dotplot': ['synteny', 'visualization'], 'msy': ['microsynteny', 'visualization'], 'iqtree': ['phylogeny'], 'muscle': ['alignment'], 'trimal': ['alignment', 'filtering'], 'kallisto': ['rna_seq', 'quantification'], 'gsea': ['enrichment'], 'goEnrich': ['enrichment'], 'keggEnrich': ['enrichment'], 'tpmCalc': ['rna_seq', 'normalization'], 'peaktss': ['chip_seq'], 'dnDsCalculate': ['ka_ks', 'evolutionary_analysis'], 'extractFasta': ['sequence', 'extraction'], 'statFasta': ['sequence', 'statistics'], 'hmmerSearch': ['homology', 'hmm_scan'], 'pep2codon': ['translation', 'codon'], 'mastExtract': ['motif', 'sequence_extraction'], 'preparespecies': ['genome_preparation', 'annotation'], 'fastaExtract': ['sequence', 'extraction'], 'mastrun': ['motif', 'scanning'], 'structure': ['sequence']}
KNOWN_CAPABILITIES.update({'mcscanx': ['synteny', 'collinearity_detection'], 'dualsyn': ['synteny', 'visualization'], 'dotplot': ['synteny', 'visualization'], 'circos': ['visualization', 'genome_circos'], 'collinearRegion': ['synteny', 'visualization'], 'pafviz': ['synteny', 'visualization'], 'pafref': ['synteny', 'visualization'], 'microsyn': ['synteny', 'visualization'], 'multisyn': ['synteny', 'visualization'], 'qdot': ['synteny', 'visualization'], 'fimo': ['motif', 'scanning'], 'mastrun': ['motif', 'scanning'], 'memerun': ['motif', 'discovery'], 'memeViz': ['motif', 'visualization'], 'seqlogo': ['motif', 'visualization'], 'tfbsShift': ['motif', 'genome_scan'], 'smart': ['domain', 'annotation'], 'hmmsearch': ['homology', 'hmm_scan'], 'diamond': ['homology', 'alignment'], 'blastp': ['homology', 'alignment'], 'blastn': ['homology', 'alignment'], 'recipBlast': ['homology', 'reciprocal_best_hit', 'blast'], 'filterCScore': ['homology', 'filtering'], 'kallisto': ['rna_seq', 'quantification'], 'fqTrim': ['ngs', 'preprocessing'], 'fqfaConv': ['sequence', 'conversion'], 'fastaExtract': ['sequence', 'extraction'], 'fastaSubseq': ['sequence', 'extraction'], 'gffFix': ['annotation', 'gff_fixing'], 'gxfAppend': ['annotation', 'gff_ops'], 'genelocation': ['annotation', 'visualization'], 'peaktss': ['chip_seq', 'peak_calling'], 'peakanno': ['chip_seq', 'peak_annotation'], 'tpmCalc': ['rna_seq', 'normalization'], 'efpHeat': ['expression', 'visualization'], 'layoutheatmap': ['expression', 'visualization'], 'gsea': ['enrichment'], 'goEnrich': ['enrichment', 'gene_ontology'], 'keggEnrich': ['enrichment', 'pathway'], 'multiEfp': ['expression', 'visualization'], 'treeRooting': ['phylogeny', 'rooting'], 'onesteptree': ['phylogeny', 'tree_building'], 'notung': ['phylogeny', 'reconciliation'], 'newickRename': ['phylogeny', 'tree_editing']})
KNOWN_ALIASES = {'treeRooting': 'rooting', 'TableCast': 'tableCast', 'gbar': 'groupedbar', 'gdensity': 'genedensity', 'getLongestCompleteORF': 'longestorf', 'one-step': 'onesteptree', 'genestructure': 'structure', 'tree': 'draw', 'onesteptree': 'one-step'}
KNOWN_STATUS = {'srr2ena': 'network-required', 'pubmed': 'network-required', 'seqfetch': 'network-required', 'rnaplot': 'platform-limited', 'calcRepeat': 'platform-limited', 'hmmsearch': 'platform-limited', 'simplehmmscan': 'platform-limited', 'cubeheatmap': 'beta', 'groupedbar': 'beta', 'nwAlign': 'beta'}
_SPECS_CACHE: dict | None = None
def build_command_specs(force: bool=False, _skip_overlay: bool=False):
    """
    构建统一命令模型(单一源, 兼容层: 不改变现运行行为)。

force=True 强制重建(测试/热更新用); 否则命中 SpecRegistry 缓存(评审 #110 P1,
294 spec 一次性构建, Agent 高频链不再重复重建)。
_skip_overlay=True: 跳过 YAML 快照校验/兑底(评审 #111 P1-1 独立真源比较用——
拿纯代码 CommandSpec 与快照对比, 防"overlay 后 spec 比 YAML"自我验证)。

来源:
  1. ENGINE_REGISTRY 表驱动(组 CATEGORY_MAP 归属)
  2. CLI_TOOLS 工具注册表
  3. 手动命令(经 cli_load 分组注册的 manual 命令, 从分组命令集补)
    """

    ...
def clear_specs_cache():
    """SpecRegistry 失效(评审 #110 P1): KNOWN_* / 注册表变更后强制下次重建。"""

    ...
def specs_from_scans(reg, tools, manual, infer_group=None):
    """
    扫描结果 → CommandSpec → metadata 投影(单一组装逻辑, gen_metadata 与工具共用)。

reg/tools/manual: scan_* 输出的条目 dict(含 name/kind/class/runner/xmx/help/group)。
infer_group: 可选分组推断函数(name, kind, src) -> str(manual 命令分组)。
    """

    ...
def to_metadata_entry(spec: CommandSpec):
    """CommandSpec → metadata 条目(与现有 command_metadata.json 结构兼容)"""

    ...
def agent_readiness(spec):
    """
    工具 Agent-ready 分级(评审 #66 P1-5 修正):
FULL = inputs+outputs+capabilities 有标注 + status=stable(parameters 声明存在即可,
       无参数工具不扣分——区分"声明无参数"和"未定义参数")
PARTIAL = 部分契约(capabilities 有但 schema 不全, 或 status 非 stable)
LEGACY = 基础(仅注册;或无 capability 标注)
    """

    ...
def readiness_census():
    """全量工具 Agent-ready 统计(readiness matrix 的数值口径)。"""

    ...
def contract_coverage():
    """
    契约覆盖三层(评审 #82 P1-7): declared(声明)/compileable(可编译)/verified(执行验证)。
保留六维明细(向后兼容)。
    """

    ...
def _load_verification_report():
    """
    从测试产物读 verification 名单(评审 #82 P1-6 + #86 P1-6 + #90 P0-2:
名单由测试生成;报告不存在时**不回退过时内置名单**——假的 EXECUTION_VERIFIED 比 DECLARED 更危险)。
返回 (conformance_verified, execution_verified, compile_verified)。
    """

    ...
def _bcs_for_verify():
    """verification 加载时构建 spec(模块内直接调用, 避免自 import 循环)。"""

    ...
_CONFORMANCE_VERIFIED, _EXEC_VERIFIED, _COMPILE_VERIFIED = _load_verification_report()
CONFORMANCE_VERIFIED_TOOLS = _CONFORMANCE_VERIFIED
EXECUTION_VERIFIED_TOOLS = _EXEC_VERIFIED
def verification_level(spec):
    """
    执行验证分级(评审 #80 + #110 建议① 再分层):
CONFORMANCE_VERIFIED = 金链 conformance 全断言通过(Tier2+; 评审 #110: 真跑+expected argv+产物语义+provenance)
EXECUTION_VERIFIED = 真实执行通过(Tier2; 产物非空+sha256 完整)
COMPILEABLE = InvocationSpec 可编译(有 inputs 契约)
DECLARED = 仅注册声明
    """

    ...
def verification_census():
    """
    评审 #98 P1-3: COMPILE_VERIFIED(测试产物名单)入 census——
与 COMPILEABLE(声明可编译)区分,API 统一(不再只在 coverage 里有)。
    """

    ...
