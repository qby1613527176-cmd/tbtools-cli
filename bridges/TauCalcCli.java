import java.io.File;

/**
 * tbplot tauIndex — 组织特异性 τ 指数 CLI（08/29，第 59 引擎）
 *
 * 用法: TauCalcCli <inExpTab> <outTAU>
 *   inExpTab: 表达矩阵（首列基因名 + 样本列）
 *   outTAU: 每基因 Preferred Sample + TAU Index（0=均匀, 1=完全组织特异）
 *
 * ⚠️ main() 硬编码路径——改走 setInExpTab/setOutTAU + process()。
 *    τ 指数：1 - Σ(1-x̂)/(n-1)，组织表达分析的通用特异性指标。
 */
public class TauCalcCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: TauCalcCli <inExpTab> <outTAU>");
            System.exit(1);
        }
        Object o = Class.forName("biocjava.bioDoer.Table.TAUCalc")
                .getDeclaredConstructor().newInstance();
        Class<?> c = o.getClass();
        c.getMethod("setInExpTab", File.class).invoke(o, new File(args[0]));
        c.getMethod("setOutTAU", File.class).invoke(o, new File(args[1]));
        c.getMethod("process").invoke(o);
        System.err.println("[tbplot] τ 指数计算完成: " + args[1]);
        System.exit(0);
    }
}