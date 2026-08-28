import JJpolt2.Example.DualSyntenyPlotterAdvance;
import jjplot2.JJplot2GUI;

import java.awt.Component;
import java.awt.Container;
import java.awt.Window;
import java.io.File;
import java.io.FileWriter;

/**
 * tbplot dualsyn — TBtools 双基因组共线性图 CLI v2（08/29，旧框架保存修复）
 *
 * 用法: DualSynCli <simplifiedGff> <collinearity> <out> [--chr1 "1,2"] [--chr2 "3,4"] [--rows N] [--gap N]
 *   simplifiedGff: Chr\tGeneName\tStart\tEnd（染色体名必须数字！如 1/2/3 或 "1-1"）
 *   collinearity: MCScanX 输出（*.collinearity）
 *
 * 引擎: DualSyntenyPlotterAdvance（旧 JJplot2 框架）
 *   plot() 内部 JustShowIt 创建窗口 + 返回 JJplot2GUI
 * 保存: 遍历窗口找 jjplot2.JJplot2GUI 实例 → 调 saveImageAsPNG/PDF
 */
public class DualSynCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: DualSynCli <simplifiedGff> <collinearity> <out> [--chr1 \"1,2\"] [--chr2 \"3,4\"] [--rows N] [--gap N]");
            System.exit(1);
        }
        String gffFile = args[0];
        String collinearFile = args[1];
        String outFile = args[2];
        String chr1 = null, chr2 = null;
        int rows = 3, gap = 3;
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--chr1") && i+1<args.length) chr1 = args[++i];
            else if (args[i].equals("--chr2") && i+1<args.length) chr2 = args[++i];
            else if (args[i].equals("--rows") && i+1<args.length) rows = Integer.parseInt(args[++i]);
            else if (args[i].equals("--gap") && i+1<args.length) gap = Integer.parseInt(args[++i]);
        }
        if (chr1 == null || chr2 == null) {
            System.err.println("错误: 必须提供 --chr1 和 --chr2");
            System.exit(1);
        }

        File ctlFile = File.createTempFile("dualsyn", ".ctl");
        ctlFile.deleteOnExit();
        FileWriter fw = new FileWriter(ctlFile);
        fw.write(rows + "\n");
        fw.write(gap + "\n");
        fw.write(chr1 + "\n");
        fw.write(chr2 + "\n");
        fw.close();

        DualSyntenyPlotterAdvance dsp = new DualSyntenyPlotterAdvance();
        dsp.setCtlFile(ctlFile.getAbsolutePath());
        dsp.setCollinerFile(collinearFile);
        dsp.setInSimplifiedGff(gffFile);
        dsp.setGeneColorFile("");
        dsp.plot(); // 内部 JustShowIt 创建窗口

        // 遍历窗口找 JJplot2GUI
        JJplot2GUI gui = null;
        Window[] windows = Window.getWindows();
        System.err.println("[tbplot] 窗口数: " + windows.length);
        for (Window w : windows) {
            gui = findGUI(w);
            if (gui != null) break;
        }
        if (gui == null) {
            System.err.println("错误: 未找到 JJplot2GUI");
            System.exit(1);
        }

        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) {
            gui.saveImageAsPNG(outFile);
        } else if (low.endsWith(".pdf")) {
            gui.saveImageAsPDF(outFile);
        } else {
            // SVG: 用 svgGenerator
            Object svg = gui.getSvgGenerator();
            if (svg != null) {
                java.lang.reflect.Method m = svg.getClass().getMethod("saveAs", java.io.File.class, boolean.class);
                m.invoke(svg, new File(outFile), true);
            } else {
                gui.saveImageAsPNG(outFile + ".png");
            }
        }
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }

    static JJplot2GUI findGUI(Component c) {
        if (c instanceof JJplot2GUI) return (JJplot2GUI) c;
        if (c instanceof Container) {
            Component[] comps = ((Container) c).getComponents();
            for (Component comp : comps) {
                JJplot2GUI found = findGUI(comp);
                if (found != null) return found;
            }
        }
        return null;
    }
}