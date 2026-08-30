import biocjava.bioIO.TrimMSA.trimMSA;

import java.io.File;

/**
 * tbcli trimMSA 桥 — MSA 修剪 CLI（08/31）
 *
 * 用法: TrimMSACli <in.aln.fa> <out.aln.fa> [ratio]
 *   in.aln.fa: 多序列比对 (Fasta)
 *   out.aln.fa: 修剪后比对
 *   ratio: 每列保留阈值 (默认 0.5)
 *
 * ⚠️ trimMSA.main 是硬编码演示路径（不走 ArgsParser）→ 桥直接用 setter + process()
 */
public class TrimMSACli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: TrimMSACli <in.aln.fa> <out.aln.fa> [ratio]");
            System.exit(1);
        }
        String inFile = args[0];
        String outFile = args[1];
        float ratio = args.length > 2 ? Float.parseFloat(args[2]) : 0.5f;

        trimMSA tm = new trimMSA();
        tm.setInMSAfa(new File(inFile));
        tm.setOutMSAfa(new File(outFile));
        tm.setRatio(ratio);
        tm.process();
        System.err.println("[tbcli] 已保存: " + outFile + " (ratio=" + ratio + ")");
        System.exit(0);
    }
}
