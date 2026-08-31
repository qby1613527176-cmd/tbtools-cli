import biocjava.bioIO.BioSoftPipeServer.MEMEsuiteWrapper.QuickRunMAST;

import java.io.File;

/**
 * tbcli mastrun — 一步法 MAST motif 扫描 CLI（08/31 第八十九波，工具 101）
 *
 * 用法: MastRunCli <meme.xml> <seq.fasta> <workingDir> [--motifs M] [--seqEvalue X] [--motifPvalue X] [--other "..."]
 *   meme.xml:  MEME 输出（motif 定义）
 *   seq.fasta: 待扫描序列
 *   workingDir: 输出目录
 *
 * 引擎: QuickRunMAST.setMotifFile/setSequenceFile/setWorkingDir/... + process()
 *   （调系统 mast；与 memerun 配套——memerun 发现 motif → mastrun 扫描）
 */
public class MastRunCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: MastRunCli <meme.xml> <seq.fasta> <workingDir> [--motifs M] [--seqEvalue X] [--motifPvalue X] [--other \"...\"]");
            System.exit(1);
        }
        QuickRunMAST qrm = new QuickRunMAST();
        qrm.setMotifFile(new File(args[0]));
        qrm.setSequenceFile(new File(args[1]));
        qrm.setWorkingDir(new File(args[2]));
        for (int i = 3; i < args.length; i++) {
            switch (args[i]) {
                case "--motifs": qrm.setMotifToUse(args[++i]); break;
                case "--seqEvalue": qrm.setMaxSequenceEvalue(Double.parseDouble(args[++i])); break;
                case "--motifPvalue": qrm.setMaxMotifPvalue(Double.parseDouble(args[++i])); break;
                case "--other": qrm.setOtherParas(args[++i]); break;
                default: System.err.println("未知参数: " + args[i]); break;
            }
        }
        qrm.process();
        System.err.println("[tbplot] MAST 完成，输出目录: " + args[2]);
        System.exit(0);
    }
}