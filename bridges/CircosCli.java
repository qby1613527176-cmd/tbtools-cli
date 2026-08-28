import biocjava.bioDoer.JIGplotToolkit.Circos.AmazingSimpleCircos;
import jigplot.engine.JIGBasePanel;

import java.awt.Component;
import java.awt.Container;
import java.awt.Window;
import java.io.File;

/**
 * tbplot circos — TBtools Circos 共线性环形图 CLI（08/29 重建）
 *
 * 用法: CircosCli <chrLen.txt> <link.txt> <genePos.txt> <out> [width] [height]
 *   chrLen.txt: ChrID\tLength（每行一条染色体）
 *   link.txt:   chrA sA eA chrB sB eB [color]（共线性连线，可空文件）
 *   genePos.txt: Chr\tGene\tStart\tEnd [color]（基因位置，可空文件）
 *   out: 输出 SVG/PNG
 *
 * 引擎: AmazingSimpleCircos（process() 内部解析 3 文件 → JIGCircosAdvanced.plot() → JFrame）
 * 方案: 窗口遍历 —— process() 后遍历 Window 找 JIGBasePanel 再保存
 *       （08/28 原 CircosCli：JIGCircosAdvanced.plot，30 连线验证）
 */
public class CircosCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("用法: CircosCli <chrLen.txt> <link.txt> <genePos.txt> <out> [width] [height]");
            System.exit(1);
        }
        String chrLenFile = args[0];
        String linkFile = args[1];
        String genePosFile = args[2];
        String outFile = args[3];

        File linkF = new File(linkFile);
        File geneF = new File(genePosFile);
        if (!linkF.exists()) { linkF = File.createTempFile("empty_link", ".txt"); linkF.deleteOnExit(); }
        if (!geneF.exists()) { geneF = File.createTempFile("empty_gene", ".txt"); geneF.deleteOnExit(); }

        AmazingSimpleCircos circos = new AmazingSimpleCircos();
        circos.setInChrInfo(new File(chrLenFile));
        circos.setLinkInfo(linkF);
        circos.setGeneInfo(geneF);
        circos.setLeftUpSpace(30);
        circos.process(); // 内部 JFrame 弹窗 + JIGBasePanel

        // 窗口遍历
        JIGBasePanel panel = null;
        Window[] windows = Window.getWindows();
        System.err.println("[tbplot] 窗口数: " + windows.length);
        for (Window w : windows) {
            JIGBasePanel found = findBasePanel(w);
            if (found != null) { panel = found; break; }
        }
        if (panel == null) {
            System.err.println("错误: 未找到 JIGBasePanel（检查输入文件格式）");
            System.exit(1);
        }
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) panel.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) panel.save2PDF(new File(outFile));
        else panel.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }

    static JIGBasePanel findBasePanel(Component c) {
        if (c instanceof JIGBasePanel) return (JIGBasePanel) c;
        if (c instanceof Container) {
            Component[] comps = ((Container) c).getComponents();
            for (Component comp : comps) {
                JIGBasePanel found = findBasePanel(comp);
                if (found != null) return found;
            }
        }
        return null;
    }
}