import biocjava.bioDoer.JIGplotToolkit.newickParser.PhyloTreeMan;
import biocjava.bioDoer.JIGplotToolkit.newickParser.PhyloTreeNode;
import biocjava.bioDoer.JIGplotToolkit.newickParser.PhyloTreeView;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;

/**
 * tbplot phylotree — 系统发育树视图 CLI（08/31 第五十一波）
 *
 * 用法: PhyloTreeCli <in.nwk> <out> [vertical] [width] [height]
 *   in.nwk: Newick 树文件（支持枝长）
 *   out:    .svg / .png / .pdf
 *   vertical: true=纵向（默认 false 横向）
 *
 * 引擎: PhyloTreeMan.build() → calcForPlotEignine() 生成 TreeTab →
 *       PhyloTreeView.showTree() 返回 JIGSubPanel
 *       （08/29 误判「需 TreeTab 格式跳过」——实际 build 直接吃 newick，
 *         calcForPlotEignine 内部自动算坐标；08/31 复核攻下）
 */
public class PhyloTreeCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: PhyloTreeCli <in.nwk> <out> [vertical] [width] [height]");
            System.exit(1);
        }
        String nwkFile = args[0];
        String outFile = args[1];
        boolean vertical = args.length > 2 && Boolean.parseBoolean(args[2]);
        int width = args.length > 3 ? Integer.parseInt(args[3]) : 800;
        int height = args.length > 4 ? Integer.parseInt(args[4]) : 1400;

        // 读 newick（合并多行）
        StringBuilder sb = new StringBuilder();
        BufferedReader br = new BufferedReader(new FileReader(nwkFile));
        String line;
        while ((line = br.readLine()) != null) sb.append(line.trim());
        br.close();
        String nwk = sb.toString().trim();
        if (nwk.isEmpty()) {
            System.err.println("错误: newick 为空");
            System.exit(1);
        }

        PhyloTreeMan ptm = new PhyloTreeMan();
        PhyloTreeNode root = ptm.build(nwk);
        ptm.setTranFormType(PhyloTreeMan.TreeBranchTranForm.Origin);

        File tab = File.createTempFile("TBtools", ".tmpTreeTab");
        ptm.calcForPlotEignine(root, tab);

        // 枝长和为 0 → 自动降级 Cladogram（复刻 quickPlotTree 逻辑）
        double sumBranchLength = 0.0;
        BufferedReader br2 = new BufferedReader(new FileReader(tab));
        String l2;
        while ((l2 = br2.readLine()) != null) {
            String[] cols = l2.split("\t");
            if (cols.length > 2 && !"NaN".equals(cols[2])) {
                try { sumBranchLength += Double.parseDouble(cols[2]); } catch (Exception e) {}
            }
        }
        br2.close();
        if (sumBranchLength == 0.0) {
            System.err.println("[tbplot] 枝长和为 0，自动转 Cladogram");
            ptm.setTranFormType(PhyloTreeMan.TreeBranchTranForm.Cladogram);
            ptm.calcForPlotEignine(root, tab);
        }

        JIGBasePanel jigPanel = new JIGBasePanel(width, height);
        PhyloTreeView ptv = new PhyloTreeView();
        ptv.setShowBranchLabel(true);
        ptv.setPlotAxis(true);
        ptv.setShowNodeName(true);
        ptv.setShowHolderNodeName(false);
        ptv.setVertical(vertical);

        JIGSubPanel treePanel = ptv.showTree(tab, jigPanel);
        jigPanel.addSubPanel(treePanel);

        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) jigPanel.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) jigPanel.save2PDF(new File(outFile));
        else jigPanel.save2SVG(new File(outFile));

        tab.delete();
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }
}
