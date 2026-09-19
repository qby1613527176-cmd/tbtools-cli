/**
 * tbplot gsea — GO 预排序 GSEA 富集 CLI（插件 P00342 CLI 化）
 *
 * 用法: GSEAWrapperCli <go.obo> <query2go.tsv> <rank.rnk> <outDir>
 *   go.obo:       GO OBO 数据库
 *   query2go.tsv: 基因→GO 注释（geneID\tGO:x,GO:y）
 *   rank.rnk:     预排序列表（geneID\tscore，按 score 排）
 *   outDir:       输出目录
 *
 * 引擎: GSEAWrapper.PreRankGSEA（插件 jar），setter + process()。
 */
public class GSEAWrapperCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("用法: GSEAWrapperCli <go.obo> <query2go.tsv> <rank.rnk> <outDir>");
            System.exit(1);
        }
        java.io.File outDir = new java.io.File(args[3]);
        if (!outDir.isDirectory() && !outDir.mkdirs()) {
            System.err.println("❌ 无法创建输出目录: " + args[3]);
            System.exit(1);
        }
        Object e = Class.forName("GSEAWrapper.PreRankGSEA").getDeclaredConstructor().newInstance();
        Class<?> c = e.getClass();
        c.getMethod("setInOboFile", java.io.File.class).invoke(e, new java.io.File(args[0]));
        c.getMethod("setInQuery2GoFile", java.io.File.class).invoke(e, new java.io.File(args[1]));
        c.getMethod("setInRankFile", java.io.File.class).invoke(e, new java.io.File(args[2]));
        c.getMethod("setOutDir", java.io.File.class).invoke(e, outDir);
        c.getMethod("process").invoke(e);
        System.err.println("[tbplot] GSEA 完成: " + args[3]);
        System.exit(0);
    }
}
