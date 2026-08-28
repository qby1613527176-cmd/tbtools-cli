import biocjava.bioDoer.JIGplotToolkit.Circos.CircleGeneViewer;
import jigplot.engine.JIGBasePanel;

import java.awt.Component;
import java.awt.Container;
import java.awt.Window;
import java.io.File;

/**
 * tbplot circlegene — TBtools 环形基因位置图 CLI（08/29 重建）
 *
 * 用法: CircleGeneViewerCli <gff> <geneID.txt> <out> [--rename f] [--link f] [--rankedChr f] [--onlyMapped true|false]
 *   gff: 基因注释 GFF（含 mRNA 行）
 *   geneID.txt: mRNA ID 列表（每行一个，可第二列 1/0 控制颜色）
 *   --rename: 基因重命名文件（可选）
 *   --link: 基因对文件 (GeneA\tGeneB\t[r,g,b]) 绘制共线性链接（可选）
 *   --rankedChr: 染色体排序列表（可选）
 *
 * 引擎: CircleGeneViewer（process() 内部 JFrame 弹窗；核心 JIGCircos.plot() 返回 JIGSubPanel）
 * 方案: 窗口遍历 —— process() 后遍历 Window 找 JIGBasePanel 再保存
 *       （GRAS 13 染色体+40 基因+6 同源 link 验证 SVG 25KB，08/28）
 */
public class CircleGeneViewerCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: CircleGeneViewerCli <gff> <geneID.txt> <out> [--rename f] [--link f] [--rankedChr f] [--onlyMapped true|false]");
            System.exit(1);
        }
        String gffFile = args[0];
        String idFile = args[1];
        String outFile = args[2];
        File renameFile = null, linkFile = null, rankedChrFile = null;
        boolean onlyMapped = false, showLabel = true;
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--rename") && i+1<args.length) renameFile = new File(args[++i]);
            else if (args[i].equals("--link") && i+1<args.length) linkFile = new File(args[++i]);
            else if (args[i].equals("--rankedChr") && i+1<args.length) rankedChrFile = new File(args[++i]);
            else if (args[i].equals("--onlyMapped") && i+1<args.length) onlyMapped = Boolean.parseBoolean(args[++i]);
        }

        CircleGeneViewer cgv = new CircleGeneViewer();
        cgv.setGffFile(new File(gffFile));
        cgv.setGeneIDFile(new File(idFile));
        if (renameFile != null && renameFile.exists()) cgv.setGeneRenameFile(renameFile);
        if (linkFile != null && linkFile.exists()) cgv.setDupGenePairInfoFile(linkFile);
        if (rankedChrFile != null && rankedChrFile.exists()) cgv.setRankedChrListFile(rankedChrFile);
        cgv.setOnlyShowChrContainGenes(onlyMapped);
        cgv.process(); // 内部 JFrame 弹窗 + JIGBasePanel

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