import java.io.File;

/**
 * tbplot targetScore — miRNA 靶标打分 CLI（08/29，第 55 引擎）
 *
 * 用法: TargetScoreCli <in.ssearch36.m10> <outTable> [--scoreCutOff N] [--maxMismatch N] [--recCom true|false] [--revTargetSo true|false]
 *   in.m10: ssearch36 官方参数输出（-w 100 -W 25 -E 1 -m 10 -i -U <mirna.fa> <target.fa>）
 *   outTable: 靶标表（miRNA  target  strand  beg  end  score  miRNAseq  targetseq  E  bits）
 *
 * ⚠️ 关键坑（08/29 实锤）：
 *   1. 必须 setCurAligner(Ssearch36)——默认 Fasta36 会 NPE（frame null）
 *   2. ssearch36 必须带 -i（reverse-complement）才有 sw_frame 行
 *   3. 完整管线：ssearch36 -i -m 10 → TargetScoreCli → 靶标表
 */
public class TargetScoreCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: TargetScoreCli <in.ssearch36.m10> <outTable> [--scoreCutOff N] [--maxMismatch N] [--recCom true|false] [--revTargetSo true|false]");
            System.exit(1);
        }
        String in = args[0];
        String out = args[1];
        double scoreCutOff = 5.0;
        int maxMisM = 6;
        boolean recCom = false, revTargetSo = false;
        for (int i = 2; i < args.length; i++) {
            if (args[i].equals("--scoreCutOff") && i+1 < args.length) scoreCutOff = Double.parseDouble(args[++i]);
            else if (args[i].equals("--maxMismatch") && i+1 < args.length) maxMisM = Integer.parseInt(args[++i]);
            else if (args[i].equals("--recCom") && i+1 < args.length) recCom = Boolean.parseBoolean(args[++i]);
            else if (args[i].equals("--revTargetSo") && i+1 < args.length) revTargetSo = Boolean.parseBoolean(args[++i]);
        }
        Object o = Class.forName("biocjava.bioDoer.miRNA.TargetSoEngine").getDeclaredConstructor().newInstance();
        Class<?> c = o.getClass();
        Class<?> alignerCls = Class.forName("biocjava.bioDoer.miRNA.TargetSoEngine$aligner");
        c.getMethod("setCurAligner", alignerCls)
                .invoke(o, Enum.valueOf((Class) alignerCls, "Ssearch36"));
        c.getMethod("setInFasta36m10File", File.class).invoke(o, new File(in));
        c.getMethod("setScoreCutOff", double.class).invoke(o, scoreCutOff);
        c.getMethod("setTotalMaxMisM", int.class).invoke(o, maxMisM);
        c.getMethod("setOutTable", File.class).invoke(o, new File(out));
        c.getMethod("setGenomeIsRecCom", boolean.class).invoke(o, recCom);
        c.getMethod("setRevTargetSo", boolean.class).invoke(o, revTargetSo);
        c.getMethod("process").invoke(o);
        System.err.println("[tbplot] miRNA 靶标打分完成: " + out);
        System.exit(0);
    }
}
