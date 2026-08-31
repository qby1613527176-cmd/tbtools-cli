import biocjava.bioDoer.MEME.DrawMotifPattern.DrawAmazingMetaPlot;
import jigplot.engine.JIGBasePanel;

import java.awt.Component;
import java.awt.Window;
import java.io.File;

/**
 * tbcli amazmeta — Amazing Meta Plot CLI（08/31 第七十八波，引擎 120）
 *
 * 用法: AmazingMetaCli <meme.xml> <newick.treefile> <out.svg|png|pdf> [seqLen.txt] [geneRename.txt]
 *   meme.xml:      MEME 结果（必选）
 *   newick.treefile: 进化树（必选，控制基因顺序）
 *   seqLen.txt:    可选序列长度文件（gene\tlen）
 *   geneRename.txt: 可选基因重命名
 *
 * 引擎: DrawAmazingMetaPlot.plot() —— 组合 进化树+Motif模式+基因结构+蛋白域 到一张图
 *   （论文级组合图；plot() 内部 JFrame 显示 → Window 反射取 JIGBasePanel → save2SVG/PNG/PDF）
 */
public class AmazingMetaCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: AmazingMetaCli <meme.xml> <newick.treefile> <out.svg|png|pdf> [seqLen.txt] [geneRename.txt]");
            System.exit(1);
        }
        File memeFile = new File(args[0]);
        File treeFile = new File(args[1]);
        String out = args[2];
        File seqLenFile = args.length > 3 ? new File(args[3]) : null;
        File renameFile = args.length > 4 ? new File(args[4]) : null;

        String newick = new String(java.nio.file.Files.readAllBytes(treeFile.toPath()), "UTF-8").trim();

        DrawAmazingMetaPlot damp = new DrawAmazingMetaPlot();
        damp.setMemeXmlFile(memeFile);
        damp.setNewickTreeString(newick);
        damp.setGradient(true);
        damp.setTotalGraphWidth(2000);
        damp.setTotalGraphHeight(2800);
        damp.setTreeLayOut(biocjava.bioDoer.JIGplotToolkit.newickParser.PhyloTreeMan.TreeBranchTranForm.Cladogram);
        if (seqLenFile != null && seqLenFile.exists()) damp.setInCoverMEMESeqLenFile(seqLenFile);
        if (renameFile != null && renameFile.exists()) damp.setGeneRenameFile(renameFile);

        damp.plot();

        // plot() 内部 JFrame 显示 → Window.getWindows() 反射取 JIGBasePanel
        JIGBasePanel panel = null;
        for (int i = 0; i < 20 && panel == null; i++) {
            for (Window w : Window.getWindows()) {
                if (w == null || !w.isVisible()) continue;
                JIGBasePanel p = findPanel(w);
                if (p != null) { panel = p; break; }
            }
            if (panel == null) Thread.sleep(200);
        }
        if (panel == null) {
            System.err.println("错误: 无法从 JFrame 提取 JIGBasePanel");
            System.exit(1);
        }
        String low = out.toLowerCase();
        if (low.endsWith(".png")) panel.save2PNG(new File(out));
        else if (low.endsWith(".pdf")) panel.save2PDF(new File(out));
        else panel.save2SVG(new File(out));
        System.err.println("[tbplot] 已保存: " + out);
        System.exit(0);
    }

    private static JIGBasePanel findPanel(Component c) {
        if (c instanceof JIGBasePanel) return (JIGBasePanel) c;
        if (c instanceof java.awt.Container) {
            for (Component child : ((java.awt.Container) c).getComponents()) {
                JIGBasePanel p = findPanel(child);
                if (p != null) return p;
            }
        }
        return null;
    }
}
