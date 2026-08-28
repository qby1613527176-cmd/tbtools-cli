import biocjava.bioDoer.JIGplotToolkit.newickParser.TreeTreeTree.TreeTreeTree;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;
import java.util.ArrayList;

/**
 * tbplot tree — TBtools 树+注释图 CLI（08/29 重建）
 *
 * 用法: TreeCli <treeMeta.config> <out> [pad] [width] [height]
 *   treeMeta.config: 行导向配置（# 注释）:
 *     [TYPE]:Tree                # 树类型（必须）
 *     [NEWICK]:<newick 同行>      # Newick 树（与 [NEWICK]: 同行，允许含冒号）
 *     [setting]                  # 设置节（可选）
 *     [TYPE]:TextAnno/HeatMap/BarPlot/Tile/StackBar/Domain/GeneStructure/Motifs/ManualAssigned <file> ...
 *   pad: 面板间距（默认 20）
 *
 * 引擎: TreeTreeTree.showMeYourPower() 返回 ArrayList<JIGSubPanel>（各轨道）
 *       （GRAS 12sp 树 926 叶 + TextAnno + HeatMap 轨道验证 SVG 1.19MB，08/28）
 */
public class TreeCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: TreeCli <treeMeta.config> <out> [pad] [width] [height]");
            System.exit(1);
        }
        String configFile = args[0];
        String outFile = args[1];
        int pad = args.length > 2 ? Integer.parseInt(args[2]) : 20;
        int width = args.length > 3 ? Integer.parseInt(args[3]) : 1200;
        int height = args.length > 4 ? Integer.parseInt(args[4]) : 800;

        TreeTreeTree ttt = new TreeTreeTree();
        ttt.setInConfig(new File(configFile));
        ttt.setScaleFactor(1.0);

        ArrayList<JIGSubPanel> panels = ttt.showMeYourPower();
        if (panels == null || panels.isEmpty()) {
            System.err.println("错误: showMeYourPower 返回空");
            System.exit(1);
        }
        System.err.println("[tbplot] 轨道面板数: " + panels.size());

        JIGBasePanel base = new JIGBasePanel(width, height);
        for (JIGSubPanel p : panels) base.addSubPanel(p);
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) base.save2PDF(new File(outFile));
        else base.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile + " (" + panels.size() + " 轨道)");
        System.exit(0);
    }
}