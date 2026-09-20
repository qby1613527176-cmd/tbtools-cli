import biocjava.bioDoer.Fasta.FastaMergerAndSpliter;

import java.io.File;
import java.util.ArrayList;

/**
 * tbplot famerge — 多 FASTA 合并 CLI（GUI 逆向 #33，09/20）
 *
 * 用法: FastaMergerCli <out.fa> <in1.fa> <in2.fa> [in3.fa ...]
 *   out: 合并输出
 *   inN: 输入 FASTA 列表（≥1 个）
 *
 * 引擎: FastaMergerAndSpliter.Merge(ArrayList, String)（GUI 逆向：
 *   FastaMergeAndSplitGUIPanel $3 mergedStartButton 回调；
 *   面板还有 QuickSpiltFasta 拆分 → 已由 fasplit direct 覆盖）
 */
public class FastaMergerCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: FastaMergerCli <out.fa> <in1.fa> <in2.fa> [in3.fa ...]");
            System.exit(1);
        }
        String outFile = args[0];
        ArrayList<String> inList = new ArrayList<String>();
        for (int i = 1; i < args.length; i++) {
            if (!new File(args[i]).exists()) {
                System.err.println("错误: 输入文件不存在: " + args[i]);
                System.exit(2);
            }
            inList.add(args[i]);
        }
        FastaMergerAndSpliter.Merge(inList, outFile);
        System.err.println("[tbplot] 合并完成: " + inList.size() + " 个文件 → " + outFile);
        System.exit(0);
    }
}
