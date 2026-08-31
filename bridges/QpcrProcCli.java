import biocjava.bioDoer.LinuxPipe.SimpleQPCRProcessser;

import java.io.File;

/**
 * tbcli qpcrproc — qPCR 相对表达分析 CLI（08/31 第八十七波，工具 97）
 *
 * 用法: QpcrProcCli <in.qpcr.tab> <out.xls>
 *   in.qpcr.tab: Sample\tRefCt\tExpCt（列1=内参基因 Ct，列2=目标基因 Ct；同样本多行求均值）
 *   out.xls: Sample\tMean\tStdev（2^-ΔΔCt 相对表达）
 *
 * 引擎: SimpleQPCRProcessser.setInqPCRTabFile/setOutProcessedFile + process()
 *   （main 硬编码演示 → setter+process；qPCR 数据分析，与绘图类 qpcr 互补）
 */
public class QpcrProcCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: QpcrProcCli <in.qpcr.tab> <out.xls>");
            System.exit(1);
        }
        SimpleQPCRProcessser sqp = new SimpleQPCRProcessser();
        sqp.setInqPCRTabFile(new File(args[0]));
        sqp.setOutProcessedFile(new File(args[1]));
        sqp.process();
        System.err.println("[tbplot] 已保存: " + args[1]);
        System.exit(0);
    }
}
