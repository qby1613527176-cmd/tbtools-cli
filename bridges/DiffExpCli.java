import biocjava.bioDoer.JIGplotToolkit.RNAseqViz.DiffExpDualHistPlot;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;

/**
 * tbplot dehist — TBtools 差异表达双直方图 CLI（08/29 新增，第 27 引擎）
 *
 * 用法: DiffExpCli <deg.txt> <out> [width] [height]
 *   deg.txt: 每行至少 3 列（tab 分隔）：任意ID\t值1\t值2
 *     值1/值2: 两个样本/条件的数值（如表达量、Log2FC 对）
 *     # 开头行跳过；第 2 列必须是数字
 *     引擎按 值1 vs 值2 大小分左右两个直方图
 *
 * 引擎: DiffExpDualHistPlot.process(File) 返回 JIGSubPanel[]（双直方图）
 */
public class DiffExpCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: DiffExpCli <deg.txt> <out> [width] [height]");
            System.exit(1);
        }
        String inFile = args[0];
        String outFile = args[1];
        int width = args.length > 2 ? Integer.parseInt(args[2]) : 1000;
        int height = args.length > 3 ? Integer.parseInt(args[3]) : 700;

        DiffExpDualHistPlot plot = new DiffExpDualHistPlot();
        JIGSubPanel[] panels = plot.process(new File(inFile));
        if (panels == null || panels.length == 0) {
            System.err.println("错误: process 返回空");
            System.exit(1);
        }
        JIGBasePanel base = new JIGBasePanel(width, height);
        for (JIGSubPanel p : panels) base.addSubPanel(p);
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) base.save2PDF(new File(outFile));
        else base.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile + " (" + panels.length + " 面板)");
        System.exit(0);
    }
}