import java.io.File;

/**
 * tbplot qpcrDdct — qPCR 相对定量（ΔΔCt）CLI（08/29，第 58 引擎）
 *
 * 用法: QpcrDdctCli <in.qpcr.tab> <out.xls>
 *   in.qpcr.tab: tab 分隔 3 列（基因名\t对照Ct\t实验Ct），同名多行取平均
 *   out.xls: 相对表达量（2^-ΔΔCt 等）
 *
 * ⚠️ main() 硬编码路径——改走 setInqPCRTabFile/setOutProcessedFile + process()。
 *    多基因重复样本自动平均。TBtools 官方用于 qPCR 相对定量。
 */
public class QpcrDdctCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: QpcrDdctCli <in.qpcr.tab> <out.xls>");
            System.exit(1);
        }
        Object o = Class.forName("biocjava.bioDoer.LinuxPipe.SimpleQPCRProcessser")
                .getDeclaredConstructor().newInstance();
        Class<?> c = o.getClass();
        c.getMethod("setInqPCRTabFile", File.class).invoke(o, new File(args[0]));
        c.getMethod("setOutProcessedFile", File.class).invoke(o, new File(args[1]));
        c.getMethod("process").invoke(o);
        System.err.println("[tbplot] qPCR 相对定量完成: " + args[1]);
        System.exit(0);
    }
}