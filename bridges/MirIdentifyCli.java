import java.io.File;

/**
 * tbplot mirIdentify — miRNA 前体鉴定 CLI（08/29，第 78 引擎）
 *
 * 用法: MirIdentifyCli <inGenome.fa> <inTargetSo.tsv> <outPredict> <outChecklog> [--checkARM BOTH|FIVE|THREE] [--maxAsy N] [--maxMatureAsy N] [--maxStarAsy N] [--maxBulge N]
 *   inGenome.fa : 参考基因组（HiC_scaffold 命名，如油茶 Co_chroms.fa）
 *   inTargetSo.tsv : TargetSo 引擎输出（mirnatarget 命令产物：miRNA target strand beg end score ...）
 *   outPredict : miRNA 前体预测表；outChecklog : 检查日志表
 *
 * ⚠️ 前体提取需要 RNAfold（检查 PATH）；基因组大（2.7GB 级）需 -Xmx>=8g + -Djava.io.tmpdir=<磁盘>
 * ⚠️ 靶标表 subject 染色体名必须与基因组 fasta 头匹配
 */
public class MirIdentifyCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("用法: MirIdentifyCli <inGenome.fa> <inTargetSo.tsv> <outPredict> <outChecklog> [--checkARM BOTH|FIVE|THREE] [--maxAsy N] [--maxMatureAsy N] [--maxStarAsy N] [--maxBulge N]");
            System.exit(1);
        }
        File genome = new File(args[0]);
        File target = new File(args[1]);
        File outPredict = new File(args[2]);
        File outChecklog = new File(args[3]);
        String checkARM = "BOTH";
        int maxAsy = 1, maxMatureAsy = 1, maxStarAsy = 0, maxBulge = 2;
        for (int i = 4; i < args.length; i++) {
            if (args[i].equals("--checkARM") && i+1 < args.length) checkARM = args[++i];
            else if (args[i].equals("--maxAsy") && i+1 < args.length) maxAsy = Integer.parseInt(args[++i]);
            else if (args[i].equals("--maxMatureAsy") && i+1 < args.length) maxMatureAsy = Integer.parseInt(args[++i]);
            else if (args[i].equals("--maxStarAsy") && i+1 < args.length) maxStarAsy = Integer.parseInt(args[++i]);
            else if (args[i].equals("--maxBulge") && i+1 < args.length) maxBulge = Integer.parseInt(args[++i]);
        }
        Object o = Class.forName("biocjava.bioDoer.miRNA.MIRidentifierBasedOnTargetSoResult")
                .getDeclaredConstructor().newInstance();
        Class<?> c = o.getClass();
        c.getMethod("setInGenomeFile", File.class).invoke(o, genome);
        c.getMethod("setInTargetSoResultFile", File.class).invoke(o, target);
        c.getMethod("setOutResult", File.class).invoke(o, outPredict);
        c.getMethod("setCheckLogResult", File.class).invoke(o, outChecklog);
        c.getMethod("setMaxAsy", int.class).invoke(o, maxAsy);
        c.getMethod("setMaxMatureAsy", int.class).invoke(o, maxMatureAsy);
        c.getMethod("setMaxStarAsy", int.class).invoke(o, maxStarAsy);
        c.getMethod("setMaxBulge", int.class).invoke(o, maxBulge);
        // ⚠️ ARM 枚举只写 Three/Five（驼峰），BOTH=不设置（null 默认）
        if (!checkARM.equalsIgnoreCase("BOTH")) {
            String armVal = checkARM.equalsIgnoreCase("THREE") ? "Three" : "Five";
            c.getMethod("setCheckARM", Class.forName("biocjava.bioIO.RNAfold.FoldStructureAnalyzer$ARM"))
                    .invoke(o, Enum.valueOf((Class) Class.forName("biocjava.bioIO.RNAfold.FoldStructureAnalyzer$ARM"), armVal));
        }
        // ⚠️ 引擎主流程方法名是 preict()（拼写错误），不是 process()！
        c.getMethod("preict").invoke(o);
        System.err.println("[tbplot] miRNA 前体鉴定完成: " + outPredict);
        System.exit(0);
    }
}