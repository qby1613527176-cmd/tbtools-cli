/**
 * tbplot keggEnrich — KEGG 富集分析 CLI（G4 缺口补齐，WorkBuddy 2026-09-19 报告 §8）
 *
 * 用法: KeggEnrichCli <reference.keg> <annotation.tsv> <selectIds.txt> <out.xls>
 *   reference.keg:  KEGG 参考通路层次文件（.keg，KEGG FTP 获取）
 *   annotation.tsv: 背景注释（gene ↔ K number 对应表）
 *   selectIds.txt:  目标基因集（每行一个 ID）
 *   out.xls:        富集结果输出
 *
 * ⚠️ main() 硬编码路径——改走 4 setter + initializedBackground + conductEnrichment。
 *    注意: 需要真实 .keg 参考文件才能完整验证（合成数据仅验证到参数接线）。
 */
public class KeggEnrichCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("用法: KeggEnrichCli <reference.keg> <annotation.tsv> <selectIds.txt> <out.xls>");
            System.exit(1);
        }
        Object k = Class.forName("biocjava.bioDoer.Kegg.AdvancedForEnrichment.KeggEnrichment")
                .getDeclaredConstructor().newInstance();
        Class<?> c = k.getClass();
        c.getMethod("setInRefenceKeg", String.class).invoke(k, args[0]);
        c.getMethod("setAnnotation", String.class).invoke(k, args[1]);
        c.getMethod("setSelectIdsFile", String.class).invoke(k, args[2]);
        c.getMethod("setOutFile", String.class).invoke(k, args[3]);
        c.getMethod("initializedBackground").invoke(k);
        c.getMethod("conductEnrichment").invoke(k);
        System.err.println("[tbplot] KEGG 富集完成: " + args[3]);
        System.exit(0);
    }
}
