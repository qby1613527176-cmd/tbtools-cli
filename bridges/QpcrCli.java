import biocjava.bioDoer.JIGplotToolkit.qPCRBarPlot.barPlotWithErrorBar;
import jigplot.engine.JIGBasePanel;

import java.awt.Window;
import java.io.File;

/**
 * tbplot qpcr — TBtools qPCR 柱状图（带误差棒）CLI（08/29 重建）
 *
 * 用法: QpcrCli <data.txt> <out.svg/png> [width] [height]
 *   data.txt: name\tmean\tsd（每行一个样本/处理）
 *
 * 引擎: barPlotWithErrorBar（plot() 只弹窗不返回 panel）
 * 方案: 窗口遍历 —— plot() 后遍历所有 java.awt.Window 找到 JIGBasePanel 再保存
 *       （参考 08/28 原 QpcrCli 的窗口遍历方案）
 */
public class QpcrCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: QpcrCli <data.txt> <outFile> [width] [height]");
            System.exit(1);
        }
        String inFile = args[0];
        String outFile = args[1];

        barPlotWithErrorBar plotter = new barPlotWithErrorBar();
        plotter.setInFile(new File(inFile));
        plotter.plot(); // 内部 setVisible 弹窗（xvfb 下无显示但仍创建 Window）

        // 窗口遍历：找 JIGBasePanel
        JIGBasePanel panel = null;
        Window[] windows = Window.getWindows();
        System.err.println("[tbplot] 窗口数: " + windows.length);
        for (Window w : windows) {
            JIGBasePanel found = findBasePanel(w);
            if (found != null) {
                panel = found;
                break;
            }
        }
        if (panel == null) {
            System.err.println("错误: 未找到 JIGBasePanel（可能绘图失败）");
            System.exit(1);
        }

        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) {
            panel.save2PNG(new File(outFile));
        } else if (low.endsWith(".pdf")) {
            panel.save2PDF(new File(outFile));
        } else {
            panel.save2SVG(new File(outFile));
        }
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }

    static JIGBasePanel findBasePanel(java.awt.Component c) {
        if (c instanceof JIGBasePanel) return (JIGBasePanel) c;
        if (c instanceof java.awt.Container) {
            java.awt.Component[] comps = ((java.awt.Container) c).getComponents();
            for (java.awt.Component comp : comps) {
                JIGBasePanel found = findBasePanel(comp);
                if (found != null) return found;
            }
        }
        return null;
    }
}
