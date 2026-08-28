import biocjava.bioDoer.JIGplotToolkit.newickParser.PhyloTreeView;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;

/**
 * tbplot phylotree — TBtools 系统发育树图 CLI（08/29 新增，第 31 引擎）
 *
 * 用法: PhyloTreeCli <newick.tree> <out> [width] [height] [--showNodeName true] [--showBranchLabel true]
 *   newick.tree: Newick 格式系统发育树文件
 *
 * 引擎: PhyloTreeView.showTree(File, JIGBasePanel) 返回 JIGSubPanel
 */
public class PhyloTreeCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: PhyloTreeCli <newick.tree> <out> [width] [height]");
            System.exit(1);
        }
        String treeFile = args[0];
        String outFile = args[1];
        int width = args.length > 2 ? Integer.parseInt(args[2]) : 1000;
        int height = args.length > 3 ? Integer.parseInt(args[3]) : 700;
        boolean showNodeName = true, showBranchLabel = true;
        for (int i = 4; i < args.length; i++) {
            if (args[i].equals("--showNodeName") && i+1<args.length) showNodeName = Boolean.parseBoolean(args[++i]);
            else if (args[i].equals("--showBranchLabel") && i+1<args.length) showBranchLabel = Boolean.parseBoolean(args[++i]);
        }

        PhyloTreeView view = new PhyloTreeView();
        view.setShowNodeName(showNodeName);
        view.setShowBranchLabel(showBranchLabel);

        JIGBasePanel base = new JIGBasePanel(width, height);
        JIGSubPanel panel = view.showTree(new File(treeFile), base);
        if (panel == null) {
            System.err.println("错误: showTree 返回 null");
            System.exit(1);
        }
        base.addSubPanel(panel);
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) base.save2PDF(new File(outFile));
        else base.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }
}