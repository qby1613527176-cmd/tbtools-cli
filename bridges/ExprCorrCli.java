import java.io.File;

/**
 * tbplot exprCorr — 表达相关矩阵 CLI（08/29，第 60 引擎）
 *
 * 用法: ExprCorrCli <inFPKM> <outCorrMat>
 *   inFPKM: 表达矩阵（首列基因名 + 样本列）
 *   outCorrMat: 样本间 Pearson 相关矩阵（共表达/聚类分析输入）
 *
 * ⚠️ main() 硬编码路径——改走 setInFPKM/setOutCorrMat + process()。
 */
public class ExprCorrCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: ExprCorrCli <inFPKM> <outCorrMat>");
            System.exit(1);
        }
        Object o = Class.forName("biocjava.bioDoer.Table.ExpressionCorr")
                .getDeclaredConstructor().newInstance();
        Class<?> c = o.getClass();
        c.getMethod("setInFPKM", File.class).invoke(o, new File(args[0]));
        c.getMethod("setOutCorrMat", File.class).invoke(o, new File(args[1]));
        c.getMethod("process").invoke(o);
        System.err.println("[tbplot] 表达相关矩阵完成: " + args[1]);
        System.exit(0);
    }
}