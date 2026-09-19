import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;
import java.lang.reflect.Method;

/**
 * tbplot dehist — 差异表达双直方图 CLI（G5 死命令修复）
 *
 * 用法: DeHistCli <deg.tsv> <out.svg> [width] [height]
 *   deg.tsv: 差异表达统计表（gene + log2FC 等数值列）
 *
 * 背景: cli.py 原注册类 biocjava...DiffExp.DualHistPlot.DiffExpDualHistPlot
 *   在 2.535 jar 中不存在（tbtools doctor 死命令探测发现）；真实类为
 *   biocjava.bioDoer.JIGplotToolkit.RNAseqViz.DiffExpDualHistPlot，
 *   其 main() 硬编码作者机器路径 → 走 process(File)→JIGSubPanel[] 桥。
 */
public class DeHistCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: DeHistCli <deg.tsv> <out.svg> [width] [height]");
            System.exit(1);
        }
        int width = args.length > 2 ? Integer.parseInt(args[2]) : 1000;
        int height = args.length > 3 ? Integer.parseInt(args[3]) : 800;

        Object engine = Class.forName("biocjava.bioDoer.JIGplotToolkit.RNAseqViz.DiffExpDualHistPlot")
                .getDeclaredConstructor().newInstance();
        Method process = engine.getClass().getMethod("process", File.class);
        Object result = process.invoke(engine, new File(args[0]));
        if (!(result instanceof JIGSubPanel[])) {
            System.err.println("❌ process 未返回 JIGSubPanel[]");
            System.exit(1);
        }
        JIGSubPanel[] panels = (JIGSubPanel[]) result;
        JIGBasePanel base = new JIGBasePanel(width, height);
        for (JIGSubPanel p : panels) base.addSubPanel(p);
        File outf = new File(args[1]);
        String low = args[1].toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(outf);
        else if (low.endsWith(".pdf")) base.save2PDF(outf);
        else base.save2SVG(outf);
        System.err.println("[tbplot] 已保存: " + args[1] + " (" + panels.length + " 面板)");
        System.exit(0);
    }
}
