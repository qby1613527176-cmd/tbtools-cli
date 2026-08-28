import biocjava.bioDoer.JIGplotToolkit.EnrichmentAnalysisGraph.Barplot;
import jigplot.engine.JIGBasePanel;

import java.awt.Window;
import java.io.File;
import java.lang.reflect.Field;

/**
 * Barplot CLI — 富集柱状图（-log10 P-value 横向柱状图）
 * 
 * 用法:
 *   java -cp JAR:tbplot BarplotCli <enrichment.xls> <outFile> <termCol> <pvalCol> [classCol] [maxTerms] [xlab] [ylab] [mode]
 * 
 * 参数:
 *   enrichment.xls  — 富集结果表（TSV 带表头）
 *   outFile         — 输出文件 (.svg/.png/.pdf)
 *   termCol         — Term 列名（如 GO_Name / Pathway）
 *   pvalCol         — P-value 列名（如 P_value）
 *   classCol        — 分 class 列名（可选，如 Class）
 *   maxTerms        — 最多显示 Term 数（默认 50）
 *   xlab            — X 轴标签（默认 "-log10(P-value)"）
 *   ylab            — Y 轴标签（默认 "GO Term"）
 *   mode            — 图模式: Normal|TextOnLeft|BarOnLeft（默认 Normal）
 * 
 * 数据格式（TSV，首行表头）:
 *   GO_Name\tP_value\tClass
 *   photosynthesis\t0.0001\tBP
 *   ...
 */
public class BarplotCli {
    
    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("用法: BarplotCli <enrichment.xls> <outFile> <termCol> <pvalCol> [classCol] [maxTerms] [xlab] [ylab] [mode]");
            System.exit(1);
        }
        
        String inFile = args[0];
        String outFile = args[1];
        String termCol = args[2];
        String pvalCol = args[3];
        String classCol = args.length > 4 ? args[4] : null;
        int maxTerms = args.length > 5 ? Integer.parseInt(args[5]) : 50;
        String xlab = args.length > 6 ? args[6] : "-log10(P-value)";
        String ylab = args.length > 7 ? args[7] : "GO Term";
        String modeStr = args.length > 8 ? args[8] : "Normal";
        
        Barplot.GraphMode mode;
        switch (modeStr.trim().toUpperCase()) {
            case "TEXTONLEFT": mode = Barplot.GraphMode.TextOnLeft; break;
            case "BARONLEFT": mode = Barplot.GraphMode.BarOnLeft; break;
            default: mode = Barplot.GraphMode.Normal; break;
        }
        
        // 记录当前窗口数
        int windowCountBefore = Window.getWindows().length;
        
        // 构建 Barplot
        Barplot bp = new Barplot();
        bp.setInTabFile(new File(inFile));
        bp.setTermColName(termCol);
        bp.setpValueColName(pvalCol);
        if (classCol != null && !classCol.equals("-")) {
            bp.setClassColName(classCol);
        }
        bp.setMaxTermToShow(maxTerms);
        bp.setXlab(xlab);
        bp.setYlab(ylab);
        bp.setGraphMode(mode);
        
        // 调用 generate()（会弹 JFrame，但 xvfb 下不阻塞）
        bp.generate();
        
        // 等待 Swing 完成渲染
        Thread.sleep(500);
        
        // 遍历所有窗口找 JIGBasePanel
        JIGBasePanel targetPanel = null;
        Window[] windows = Window.getWindows();
        for (Window w : windows) {
            // 搜索组件树找 JIGBasePanel
            targetPanel = findJIGBasePanel(w);
            if (targetPanel != null) break;
        }
        
        if (targetPanel == null) {
            // 反射从 Barplot 实例抓 jigPanel 字段（如果存在）
            System.err.println("窗口遍历未找到 JIGBasePanel，尝试反射...");
            // Barplot 内部 jigPanel 是局部变量，无法反射
            // 但 JScrollPane 包含 JIGBasePanel
            for (Window w : windows) {
                if (w instanceof javax.swing.JFrame) {
                    java.awt.Container content = ((javax.swing.JFrame) w).getContentPane();
                    targetPanel = findJIGBasePanelDeep(content);
                    if (targetPanel != null) break;
                }
            }
        }
        
        if (targetPanel != null) {
            // 保存
            if (outFile.toLowerCase().endsWith(".svg")) {
                targetPanel.save2SVG(new java.io.File(outFile));
            } else if (outFile.toLowerCase().endsWith(".png")) {
                targetPanel.save2PNG(new java.io.File(outFile));
            } else if (outFile.toLowerCase().endsWith(".pdf")) {
                targetPanel.save2PDF(new java.io.File(outFile));
            } else {
                targetPanel.save2SVG(new java.io.File(outFile + ".svg"));
            }
            System.err.println("Barplot saved: " + outFile);
            
            // 关闭窗口
            for (Window w : windows) {
                if (w instanceof java.awt.Frame) {
                    ((java.awt.Frame) w).dispose();
                }
            }
        } else {
            System.err.println("ERROR: 未找到 JIGBasePanel，无法保存。");
            System.err.println("Windows count: " + windows.length);
            for (Window w : windows) {
                System.err.println("  Window: " + w.getClass().getName() + " visible=" + w.isVisible());
            }
            System.exit(2);
        }
    }
    
    static JIGBasePanel findJIGBasePanel(java.awt.Container c) {
        for (int i = 0; i < c.getComponentCount(); i++) {
            java.awt.Component comp = c.getComponent(i);
            if (comp instanceof JIGBasePanel) {
                return (JIGBasePanel) comp;
            }
            if (comp instanceof java.awt.Container) {
                JIGBasePanel found = findJIGBasePanel((java.awt.Container) comp);
                if (found != null) return found;
            }
        }
        return null;
    }
    
    static JIGBasePanel findJIGBasePanelDeep(java.awt.Container c) {
        // 搜索 JScrollPane -> JViewport -> JIGBasePanel
        for (int i = 0; i < c.getComponentCount(); i++) {
            java.awt.Component comp = c.getComponent(i);
            if (comp instanceof JIGBasePanel) {
                return (JIGBasePanel) comp;
            }
            if (comp instanceof javax.swing.JScrollPane) {
                javax.swing.JScrollPane jsp = (javax.swing.JScrollPane) comp;
                java.awt.Component view = jsp.getViewport().getView();
                if (view instanceof JIGBasePanel) {
                    return (JIGBasePanel) view;
                }
                if (view instanceof java.awt.Container) {
                    JIGBasePanel found = findJIGBasePanelDeep((java.awt.Container) view);
                    if (found != null) return found;
                }
            }
            if (comp instanceof java.awt.Container) {
                JIGBasePanel found = findJIGBasePanelDeep((java.awt.Container) comp);
                if (found != null) return found;
            }
        }
        return null;
    }
}
