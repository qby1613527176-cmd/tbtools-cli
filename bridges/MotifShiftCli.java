/**
 * tbplot tfbsShift — 植物 TF 结合 motif 偏移分析 CLI（插件 P00551 CLI 化）
 *
 * 用法: MotifShiftCli <query.pep> <outPrefix> [threads]
 *   query.pep:  待分析植物蛋白（TF 候选）
 *   outPrefix:  输出前缀（文件，非目录）
 *   threads:    线程数（默认 4）
 *
 * 引擎: motfiShift.MotifShift（插件 jar）。参考数据随插件发行：
 *   plugins/lib/plantTF/ath.pep（拟南芥 TF 蛋白集）
 *   plugins/lib/plantTF/binding.motifs（MEME 4.4 格式结合 motif 库）
 */
public class MotifShiftCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("用法: MotifShiftCli <ath.pep> <binding.motifs> <query.pep> <outPrefix> [threads]");
            System.exit(1);
        }
        Object e = Class.forName("motfiShift.MotifShift").getDeclaredConstructor().newInstance();
        Class<?> c = e.getClass();
        c.getMethod("setAthPep", java.io.File.class).invoke(e, new java.io.File(args[0]));
        c.getMethod("setBindingMotifInfo", java.io.File.class).invoke(e, new java.io.File(args[1]));
        c.getMethod("setQueryPep", java.io.File.class).invoke(e, new java.io.File(args[2]));
        c.getMethod("setOutDirAndPrefix", java.io.File.class).invoke(e, new java.io.File(args[3]));
        c.getMethod("setNumberOfThreads", String.class).invoke(e, args.length > 4 ? args[4] : "4");
        c.getMethod("process").invoke(e);
        System.err.println("[tbplot] TFBS motif shift 完成: " + args[3]);
        System.exit(0);
    }
}
