import biocjava.bioIO.BioSoftPipeServer.MEMEsuiteWrapper.QuickRunMEME;

import java.io.File;

/**
 * tbcli memerun — 一步法 MEME motif 发现 CLI（08/31 第八十八波，工具 100）
 *
 * 用法: MemeRunCli <in.fasta> <workingDir> [--motif N] [--minW N] [--maxW N] [--evalue X] [--mode ZeroOrOneOccurPerSeq|OneOccurPerSeq|AnyNumberOfOccurPerSeq]
 *   in.fasta:   未比对蛋白/核酸序列
 *   workingDir: 输出目录
 *
 * 引擎: QuickRunMEME.setInFile/setWorkingDir/... + process()（main 硬编码演示 → setter+process）
 *   （调系统 meme；GRAS motif 分析统一 CLI 入口）
 */
public class MemeRunCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: MemeRunCli <in.fasta> <workingDir> [--motif N] [--minW N] [--maxW N] [--evalue X] [--mode ...]");
            System.exit(1);
        }
        QuickRunMEME qrm = new QuickRunMEME();
        qrm.setInFile(new File(args[0]));
        qrm.setWorkingDir(new File(args[1]));
        for (int i = 2; i < args.length; i++) {
            switch (args[i]) {
                case "--motif": qrm.setNumberOfMotif(Integer.parseInt(args[++i])); break;
                case "--minW": qrm.setMinMotifWidth(Integer.parseInt(args[++i])); break;
                case "--maxW": qrm.setMaxMotifWidth(Integer.parseInt(args[++i])); break;
                case "--evalue": qrm.setMaxEvalue(Double.parseDouble(args[++i])); break;
                case "--mode":
                    qrm.setMiningMode(QuickRunMEME.SITEDISTRIBUTION.valueOf(args[++i]));
                    break;
                default: System.err.println("未知参数: " + args[i]); break;
            }
        }
        qrm.process();
        System.err.println("[tbplot] MEME 完成，输出目录: " + args[1]);
        System.exit(0);
    }
}