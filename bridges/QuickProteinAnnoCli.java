/**
 * tbplot quickAnno — Quick Protein Anno CLI（插件 P00480 CLI 化）
 *
 * 用法: QuickProteinAnnoCli <query.pep> <swissprotDb> <out.txt> [threads] [maxHits]
 *   query.pep:    待注释蛋白 FASTA
 *   swissprotDb:  Swiss-Prot 库（FASTA 即可，diamond 自动 makedb 到工作区；
 *                 推荐用完整 UniProt Swiss-Prot 或自建库）
 *   out.txt:      注释汇总表（diamond 比对 + BlastXMLSummaryTable 取 Top N hits）
 *   threads:      线程（默认 4）；maxHits: 每蛋白保留命中数（默认 10）
 *
 * 引擎: QuickGenomeDot.QuickProteinAnno（插件 jar）——diamond 二进制
 *   plugins/lib/bin/diamond（Linux ELF）。⚠️ 无 swissprot 库时不建议跑
 *   （几 GB 级），本桥允许用户自带库文件。
 */
public class QuickProteinAnnoCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: QuickProteinAnnoCli <query.pep> <swissprotDb> <out.txt> [threads] [maxHits]");
            System.exit(1);
        }
        int threads = args.length > 3 ? Integer.parseInt(args[3]) : 4;
        int hits = args.length > 4 ? Integer.parseInt(args[4]) : 10;
        Object w = Class.forName("QuickGenomeDot.QuickProteinAnno").getDeclaredConstructor().newInstance();
        Class<?> c = w.getClass();
        c.getMethod("setInFile", java.io.File.class).invoke(w, new java.io.File(args[0]));
        c.getMethod("setInSwissprotDb", java.io.File.class).invoke(w, new java.io.File(args[1]));
        c.getMethod("setOutFile", java.io.File.class).invoke(w, new java.io.File(args[2]));
        c.getMethod("setNumberOfTreads", int.class).invoke(w, threads);
        c.getMethod("setNumberOfhit", int.class).invoke(w, hits);
        c.getMethod("process").invoke(w);
        System.err.println("[tbplot] 蛋白注释完成: " + args[2]);
        System.exit(0);
    }
}