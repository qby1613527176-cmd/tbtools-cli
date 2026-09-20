import biocjava.bioIO.BioSoftPipeServer.QuickTrimAL;
import biocjava.bioIO.BioSoftPipeServer.QuickTrimAL.AUTOMOD;
import biocjava.bioIO.BioSoftPipeServer.QuickTrimAL.OUTFORMAT;

import java.io.File;

/**
 * tbplot trimal — trimAl 比对修剪 CLI（GUI 逆向 #29，09/20）
 *
 * 用法: QuickTrimALCli <in.aln> <out.aln> [--mode gappyout|strict|strictplus|automated1]
 *                       [--format fasta|clustal|phylip|nexus|mega|nbrf] [--keepheader]
 *   in:   比对后 FASTA（muscle 产物）
 *   out:  修剪后比对
 *   --mode:       自动修剪模式（默认 automated1；gappyout=按 gap 分布/strict=严格/strictplus=更严格）
 *   --format:     输出格式（默认 fasta）
 *   --keepheader: 保留完整序列头
 *
 * 引擎: QuickTrimAL（GUI 逆向：TrimalGUIPanel $3 StartButton 回调
 *   → setInFile/setOutFile/setOutfmt/setTrimMode/setKeepallheader/trim；
 *   引擎调系统 trimal 二进制，v1.5 语法兼容）
 * 依赖: 系统 trimal
 */
public class QuickTrimALCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: QuickTrimALCli <in.aln> <out.aln> [--mode gappyout|strict|strictplus|automated1] [--format fasta|clustal|phylip|nexus|mega|nbrf] [--keepheader]");
            System.exit(1);
        }
        File inFile = new File(args[0]);
        File outFile = new File(args[1]);
        QuickTrimAL qta = new QuickTrimAL();
        qta.setInFile(inFile);
        qta.setOutFile(outFile);
        qta.setTrimMode(AUTOMOD.ML_AUTOMATED1);
        qta.setOutfmt(OUTFORMAT.FASTA);
        for (int i = 2; i < args.length; i++) {
            switch (args[i]) {
                case "--mode":
                    String m = args[++i].toLowerCase();
                    if (m.equals("gappyout")) qta.setTrimMode(AUTOMOD.GAPPYOUT);
                    else if (m.equals("strict")) qta.setTrimMode(AUTOMOD.STRICT);
                    else if (m.equals("strictplus")) qta.setTrimMode(AUTOMOD.NJ_STRICTPLUS);
                    else qta.setTrimMode(AUTOMOD.ML_AUTOMATED1);
                    break;
                case "--format":
                    String f = args[++i].toLowerCase();
                    if (f.equals("clustal")) qta.setOutfmt(OUTFORMAT.CLUSTAL);
                    else if (f.equals("phylip")) qta.setOutfmt(OUTFORMAT.PHYLIP);
                    else if (f.equals("nexus")) qta.setOutfmt(OUTFORMAT.NEXUS);
                    else if (f.equals("mega")) qta.setOutfmt(OUTFORMAT.MEGA);
                    else if (f.equals("nbrf")) qta.setOutfmt(OUTFORMAT.NBRF);
                    else qta.setOutfmt(OUTFORMAT.FASTA);
                    break;
                case "--keepheader": qta.setKeepallheader(true); break;
                default:
                    System.err.println("警告: 忽略未知参数 " + args[i]);
            }
        }
        if (!inFile.exists()) {
            System.err.println("错误: 输入文件不存在: " + inFile.getAbsolutePath());
            System.exit(2);
        }
        qta.trim();
        System.err.println("[tbplot] trimAl 修剪完成: " + outFile.getAbsolutePath());
        System.exit(0);
    }
}
