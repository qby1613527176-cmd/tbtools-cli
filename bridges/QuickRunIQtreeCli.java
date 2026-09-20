import biocjava.bioIO.BioSoftPipeServer.QuickRunIQtree;

import java.io.File;

/**
 * tbplot iqtree — IQ-TREE 最大似然建树 CLI（GUI 逆向 #28，09/20）
 *
 * 用法: QuickRunIQtreeCli <aln.fa> <outPrefix> [--model MFP] [--ufboot N] [--boot N]
 *                         [--freerate] [--asc] [--threads N] [--redo]
 *   aln.fa:    比对后 FASTA（可用 tbplot muscle 产物）
 *   outPrefix: 输出前缀（产物 outPrefix.treefile/.iqtree/.log 等）
 *   --model:    替换模型（默认 MFP=自动选模；如 GTR+G、JTT+G）
 *   --ufboot N: 超快 bootstrap 次数（如 1000；推荐）
 *   --boot N:   标准 bootstrap 次数（与 ufboot 二选一）
 *   --freerate: +R 自由速率模型
 *   --asc:      +ASC  ascertainment bias 校正
 *   --threads:  线程数（默认 0=AUTO）
 *   --redo:     覆盖已有输出
 *
 * 引擎: QuickRunIQtree（GUI 逆向：IQtreeGUIPanel $5 StartButton 回调；
 *   引擎拼 iqtree -s -pre -bb/-b -m -nt 调系统二进制，v2 语法兼容）
 * 依赖: 系统 iqtree/iqtree2
 */
public class QuickRunIQtreeCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: QuickRunIQtreeCli <aln.fa> <outPrefix> [--model MFP] [--ufboot N] [--boot N] [--freerate] [--asc] [--threads N] [--redo]");
            System.exit(1);
        }
        File inFile = new File(args[0]);
        File outPrefix = new File(args[1]);
        QuickRunIQtree qta = new QuickRunIQtree();
        qta.setInFile(inFile);
        qta.setOutPrefix(outPrefix);
        qta.setModel("MFP");
        qta.setNumberOfThread(0);
        for (int i = 2; i < args.length; i++) {
            switch (args[i]) {
                case "--model": qta.setModel(args[++i]); break;
                case "--ufboot":
                    int ub = Integer.parseInt(args[++i]);
                    if (ub > 0 && ub < 1000) {
                        System.err.println("错误: IQ-TREE 2 要求 UFBoot ≥ 1000（传了 " + ub + "，引擎会静默失败）");
                        System.exit(1);
                    }
                    qta.setUltraFastBS(true); qta.setBootStrapNum(ub); break;
                case "--boot": qta.setUltraFastBS(false); qta.setBootStrapNum(Integer.parseInt(args[++i])); break;
                case "--freerate": qta.setFreeRate(true); break;
                case "--asc": qta.setAscertainmentBias(true); break;
                case "--threads": qta.setNumberOfThread(Integer.parseInt(args[++i])); break;
                case "--redo": qta.setRedo(true); break;
                default:
                    System.err.println("警告: 忽略未知参数 " + args[i]);
            }
        }
        if (!inFile.exists()) {
            System.err.println("错误: 输入文件不存在: " + inFile.getAbsolutePath());
            System.exit(2);
        }
        qta.build();
        File treefile = new File(outPrefix.getAbsolutePath() + ".treefile");
        if (treefile.exists()) {
            System.err.println("[tbplot] IQ-TREE 建树完成: " + treefile.getAbsolutePath());
        } else {
            System.err.println("[tbplot] IQ-TREE 完成但未找到 .treefile（查 " + outPrefix.getAbsolutePath() + ".log）");
        }
        System.exit(0);
    }
}
