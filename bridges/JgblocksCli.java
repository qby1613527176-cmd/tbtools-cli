import biocjava.bioIO.TrimMSA.Jgblocks;
import biocjava.bioIO.TrimMSA.Jgblocks.GapTreatment;

import java.io.File;

/**
 * tbplot gblocks — Gblocks 保守区修剪 CLI（GUI 逆向 #30，09/20）
 *
 * 用法: JgblocksCli <in.aln.fa> <out.aln.fa> [--is 0.5] [--fs 0.85] [--cp 8]
 *                   [--bl1 15] [--bl2 10] [--nongap 0.5] [--gaptreat none|half|all]
 *   in:   比对后 FASTA
 *   out:  修剪后比对（保守 block）
 *   --is:      保守位点最小一致度（默认 0.5）
 *   --fs:      高保守位点最小一致度（默认 0.85）
 *   --cp:      非保守区最大连续长度（默认 8）
 *   --bl1:     block 最小初始长度（默认 15）
 *   --bl2:     block 最小最终长度（默认 10， flank 处理后）
 *   --nongap:  定义 gap 的最大比例（默认 0.5）
 *   --gaptreat: gap 处理（默认 half）
 *
 * 引擎: Jgblocks（纯 Java Gblocks 实现，非外部二进制；GUI 逆向：
 *   JGblocksGUIPanel $3 StartButton 回调 → 6 setter + process()；
 *   main() 仅 --inMSAfa/--outMSAfa 暴露，全参数须走 setter）
 */
public class JgblocksCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: JgblocksCli <in.aln.fa> <out.aln.fa> [--is 0.5] [--fs 0.85] [--cp 8] [--bl1 15] [--bl2 10] [--nongap 0.5] [--gaptreat none|half|all]");
            System.exit(1);
        }
        File inFile = new File(args[0]);
        File outFile = new File(args[1]);
        Jgblocks jgb = new Jgblocks();
        jgb.setIS(0.5); jgb.setFS(0.85); jgb.setCP(8);
        jgb.setBL1(15); jgb.setBL2(10); jgb.setNonGapRatio(0.5);
        jgb.setGapTreatment(GapTreatment.HALF);
        for (int i = 2; i < args.length; i++) {
            switch (args[i]) {
                case "--is": jgb.setIS(Double.parseDouble(args[++i])); break;
                case "--fs": jgb.setFS(Double.parseDouble(args[++i])); break;
                case "--cp": jgb.setCP(Integer.parseInt(args[++i])); break;
                case "--bl1": jgb.setBL1(Integer.parseInt(args[++i])); break;
                case "--bl2": jgb.setBL2(Integer.parseInt(args[++i])); break;
                case "--nongap": jgb.setNonGapRatio(Double.parseDouble(args[++i])); break;
                case "--gaptreat":
                    String g = args[++i].toLowerCase();
                    if (g.equals("none")) jgb.setGapTreatment(GapTreatment.NONE);
                    else if (g.equals("all")) jgb.setGapTreatment(GapTreatment.ALL);
                    else jgb.setGapTreatment(GapTreatment.HALF);
                    break;
                default:
                    System.err.println("警告: 忽略未知参数 " + args[i]);
            }
        }
        if (!inFile.exists()) {
            System.err.println("错误: 输入文件不存在: " + inFile.getAbsolutePath());
            System.exit(2);
        }
        jgb.setInMSAfa(inFile);
        jgb.setOutMSAfa(outFile);
        jgb.process();
        System.err.println("[tbplot] Gblocks 修剪完成: " + outFile.getAbsolutePath());
        System.exit(0);
    }
}
