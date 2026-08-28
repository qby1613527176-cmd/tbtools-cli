import biocjava.bioDoer.JIGplotToolkit.HeatMap.CubeHeatMap;
import jigplot.engine.JIGBasePanel;

import java.awt.Component;
import java.awt.Container;
import java.awt.Window;
import java.io.File;

/**
 * tbplot cubeheatmap — TBtools 3D 立方体热图 CLI（08/29 重建）
 *
 * 用法: CubeHeatmapCli <expr.tsv> <group.tsv> <out> [--log10] [--minColor r,g,b] [--midColor r,g,b] [--maxColor r,g,b]
 *   expr.tsv: 表达矩阵（首列基因名 + 样本名表头 + 数值）
 *   group.tsv: Sample\tFirstDim\tSecondDim（定义 3D 三面维度）
 *
 * 引擎: CubeHeatMap（plot() 内部 JIGUtils.quickShow 创建窗口，不返回 panel）
 * 方案: 窗口遍历 —— plot() 后遍历 Window 找 JIGBasePanel 再保存
 *       （08/28 原 CubeHeatmapCli 同方案，需 -Xmx4g 避免 quickShow OOM）
 */
public class CubeHeatmapCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: CubeHeatmapCli <expr.tsv> <group.tsv> <out> [--log10] [--minColor r,g,b] [--midColor r,g,b] [--maxColor r,g,b]");
            System.exit(1);
        }
        String exprFile = args[0];
        String groupFile = args[1];
        String outFile = args[2];
        boolean log10 = false;
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--log10")) log10 = true;
        }

        CubeHeatMap cube = new CubeHeatMap();
        cube.setInExpFile(new File(exprFile));
        cube.setInGroupFile(new File(groupFile));
        cube.plot(); // 内部 quickShow 创建窗口

        // 窗口遍历
        JIGBasePanel panel = null;
        Window[] windows = Window.getWindows();
        System.err.println("[tbplot] 窗口数: " + windows.length);
        for (Window w : windows) {
            JIGBasePanel found = findBasePanel(w);
            if (found != null) { panel = found; break; }
        }
        if (panel == null) {
            System.err.println("错误: 未找到 JIGBasePanel");
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