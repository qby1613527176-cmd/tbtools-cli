/**
 * tbplot mcscanxd — OneStep MCScanX-SuperFast CLI（插件 P00370 CLI 化）
 *
 * 用法: MCScanXFastCli <wkDir> <genome1.fa> <genome2.fa> <gxf1> <gxf2> [threads] [blastHits] [evalue]
 *   wkDir:    工作目录（中间文件+结果，须可写）
 *   genome1/2: 两个物种的蛋白 FASTA（diamond 比对）
 *   gxf1/2:    对应 GXF 注释（GFF/GTF）
 *   threads:   线程（默认 4）；blastHits: 每基因 hits（默认 5）；evalue: 阈值（默认 1e-5）
 *
 * 引擎: OneStepMCSCanXDiamond.OneStepMCScanXSuperFast（插件 jar），
 *   diamond 二进制 plugins/lib/bin/diamond（Linux 随包）。
 */
public class MCScanXFastCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 5) {
            System.err.println("用法: MCScanXFastCli <wkDir> <genome1.fa> <genome2.fa> <gxf1> <gxf2> [threads] [blastHits] [evalue]");
            System.exit(1);
        }
        int threads = args.length > 5 ? Integer.parseInt(args[5]) : 4;
        int hits = args.length > 6 ? Integer.parseInt(args[6]) : 5;
        double evalue = args.length > 7 ? Double.parseDouble(args[7]) : 1e-5;
        java.io.File wk = new java.io.File(args[0]);
        if (!wk.isDirectory() && !wk.mkdirs()) {
            System.err.println("❌ 无法创建工作目录: " + args[0]);
            System.exit(1);
        }
        Object w = Class.forName("OneStepMCSCanXDiamond.OneStepMCScanXSuperFast").getDeclaredConstructor().newInstance();
        Class<?> c = w.getClass();
        c.getMethod("setWkDirectory", java.io.File.class).invoke(w, wk);
        c.getMethod("setInGenome_1", java.io.File.class).invoke(w, new java.io.File(args[1]));
        c.getMethod("setInGenome_2", java.io.File.class).invoke(w, new java.io.File(args[2]));
        c.getMethod("setInGxf_1", java.io.File.class).invoke(w, new java.io.File(args[3]));
        c.getMethod("setInGxf_2", java.io.File.class).invoke(w, new java.io.File(args[4]));
        c.getMethod("setNumberOfThread", int.class).invoke(w, threads);
        c.getMethod("setNumberOfBlastHit", int.class).invoke(w, hits);
        c.getMethod("setEvalue", double.class).invoke(w, evalue);
        c.getMethod("process").invoke(w);
        System.err.println("[tbplot] MCScanX-SuperFast 完成: " + args[0]);
        System.exit(0);
    }
}
