import java.io.File;

/**
 * tbplot goEnrich — GO 富集分析 CLI（G4 缺口补齐，WorkBuddy 2026-09-19 报告 §8）
 *
 * 用法: GoEnrichCli <go.obo> <gene2go.tsv> <selectGenes.txt> <outDir>
 *   go.obo:        GO 基本 OBO 数据库文件（go-basic.obo）
 *   gene2go.tsv:   背景注释，每行 geneID\tGO:0000001,GO:0000002（也兼容 ; 分隔、多列 GO）
 *   selectGenes.txt: 目标基因集（每行一个 geneID）
 *   outDir:        输出目录
 *
 * 输出: outDir/<selectName>.GO.Enrichment.final.xls（三本体合并显著结果表）
 *   列: Class / GO_Name / GO_ID / GO_Level / P_value / EnrichmentScore /
 *       HitsGenesCountsInSelectedSet / HitsGenesCountsInBackground / corrected p-value(BH)
 *   （cleanMode=true 会清掉 MF/CC/BP 三个中间表，只留合并终表）
 *
 * ⚠️ main() 硬编码路径——改走 prepareForEnrichMent + AutoEnrichMent 方法链。
 *    cleanMode=true 清中间文件（_ParsedAllGO.xls 等）。
 */
public class GoEnrichCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("用法: GoEnrichCli <go.obo> <gene2go.tsv> <selectGenes.txt> <outDir>");
            System.exit(1);
        }
        File outDir = new File(args[3]);
        if (!outDir.isDirectory() && !outDir.mkdirs()) {
            System.err.println("[GoEnrichCli] ❌ 无法创建输出目录: " + args[3]);
            System.exit(1);
        }
        Object e = Class.forName("biocjava.bioIO.GeneOntology.EnrichMent.GOTermEnrichment")
                .getDeclaredConstructor().newInstance();
        Class<?> c = e.getClass();
        c.getMethod("setCleanMode", boolean.class).invoke(e, true);
        c.getMethod("prepareForEnrichMent", File.class, File.class)
                .invoke(e, new File(args[0]), new File(args[1]));
        c.getMethod("AutoEnrichMent", File.class, String.class)
                .invoke(e, new File(args[2]), args[3]);
        System.err.println("[tbplot] GO 富集完成（MF/CC/BP 三表）: " + args[3]);
        System.exit(0);
    }
}
