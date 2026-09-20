import biocjava.bioIO.ORF.SixFrameTranlater;

import java.io.File;

/**
 * tbplot sixframe — TBtools 六框翻译 CLI（GUI 逆向 #16，09/20）
 *
 * 用法: SixFrameTranlaterCli <in.fa> <out.fa>
 *   in:  核酸 FASTA
 *   out: 六框翻译蛋白 FASTA（+1/+2/+3/-1/-2/-3 六条序列）
 *
 * 引擎: SixFrameTranlater（GUI 逆向：SixFrameTranslatorGUIPanel StartButton 回调
 *   → setInFile/setOutFile/process 三连，main() 是硬编码路径演示无 ArgsParser）
 * 注意引擎类名拼写是 SixFrameTranlater（少一个 s），不要按英文习惯拼对。
 */
public class SixFrameTranlaterCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: SixFrameTranlaterCli <in.fa> <out.fa>");
            System.exit(1);
        }
        File inFa = new File(args[0]);
        File outFa = new File(args[1]);
        if (!inFa.exists()) {
            System.err.println("错误: 输入文件不存在: " + inFa.getAbsolutePath());
            System.exit(2);
        }
        SixFrameTranlater sft = new SixFrameTranlater();
        sft.setInFile(inFa);
        sft.setOutFile(outFa);
        sft.process();
        System.err.println("[tbplot] 六框翻译完成: " + outFa.getAbsolutePath());
        System.exit(0);
    }
}
