import unrootedtree.engine.UnrootedTreePanelNew;
import jigplot.engine.JIGBasePanel;

import java.io.File;

/**
 * tbplot unrooted — 无根树可视化 CLI（08/31 第六十四波）
 *
 * 用法: UnrootedTreeCli <in.nwk> <out> [layout] [width] [height] [iterations]
 *   in.nwk: Newick 树文件
 *   out:    .svg / .png / .pdf
 *   layout: Circular|Radial|Force-Directed|Equal Angle|N-Body|Equal-Daylight（默认 Circular）
 *   iterations: Force-Directed/N-Body 迭代次数（默认 200）
 *
 * 引擎: UnrootedTreePanelNew.loadNewickFile() → getJIGPanel() 返回 JIGBasePanel
 *       （独立引擎，与已判死局的 UnrootedTreeViz 无关；08/31 攻下）
 */
public class UnrootedTreeCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: UnrootedTreeCli <in.nwk> <out> [layout] [width] [height] [iterations]");
            System.exit(1);
        }
        String nwk = args[0];
        String out = args[1];
        String layout = args.length > 2 ? args[2] : "Circular";
        int width = args.length > 3 ? Integer.parseInt(args[3]) : 1000;
        int height = args.length > 4 ? Integer.parseInt(args[4]) : 900;
        int iterations = args.length > 5 ? Integer.parseInt(args[5]) : 200;

        UnrootedTreePanelNew ut = new UnrootedTreePanelNew();
        ut.setLayoutType(layout);
        ut.setIterations(iterations);
        ut.loadNewickFile(new File(nwk));

        JIGBasePanel panel = ut.getJIGPanel();
        String low = out.toLowerCase();
        if (low.endsWith(".png")) panel.save2PNG(new File(out));
        else if (low.endsWith(".pdf")) panel.save2PDF(new File(out));
        else panel.save2SVG(new File(out));
        System.err.println("[tbplot] 已保存: " + out + " (layout=" + layout + ")");
        System.exit(0);
    }
}
