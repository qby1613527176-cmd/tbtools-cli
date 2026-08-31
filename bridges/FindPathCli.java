import biocjava.bioDoer.JIGplotToolkit.Synteny.BloomSynteny.FindPathBySynteny;

/**
 * tbcli findpath 桥 — 共线性基因块进化路径 CLI（08/31 第六十七波）
 *
 * 用法: FindPathCli --inGffArr <gff1,gff2,...> --inGenePairs <pairs> --inRegion <geneID> [--flankGeneNum N] [--highlightGene ID] --outGraph <out>
 *
 * ⚠️ FindPathBySynteny.main1 是完整 CLI，但 main 是硬编码演示 → 桥直接调 main1
 */
public class FindPathCli {
    public static void main(String[] args) throws Exception {
        FindPathBySynteny.main1(args);
        System.exit(0);
    }
}
