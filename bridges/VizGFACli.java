import biocjava.bioDoer.JIGplotToolkit.Network.GFAGraphLayout;
import biocjava.bioDoer.JIGplotToolkit.Network.NetworkInfo;
import biocjava.bioDoer.JIGplotToolkit.Network.VizGFA;
import jigplot.engine.JIGSubPanel;
import jigplot.OtherTools.JIGUtils;

import java.io.File;

/**
 * VizGFACli — TBtools GFA 网络图 CLI（子任务 A 新增）
 *
 * 引擎链: GFAGraphLayout.process(gfa, w, h) → NetworkInfo → VizGFA.visualize(info, w, h) → JIGSubPanel
 * GFA 格式（tab 分隔）:
 *   S\t<nodeName>\t<sequence>          # 节点
 *   L\t<from>\t<strand1>\t<to>\t<strand2>\t<overlap>   # 边
 *
 * 用法: VizGFACli <in.gfa> <out.svg|png> [width] [height]
 */
public class VizGFACli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: VizGFACli <in.gfa> <out> [width] [height]");
            System.err.println("GFA: S 行=节点, L 行=边（tab 分隔）");
            System.exit(1);
        }
        String gfa = args[0];
        String outFile = args[1];
        int w = args.length > 2 ? Integer.parseInt(args[2]) : 1200;
        int h = args.length > 3 ? Integer.parseInt(args[3]) : 900;

        NetworkInfo info = GFAGraphLayout.process(gfa, w, h);
        JIGSubPanel panel = VizGFA.visualize(info, w, h);

        File outf = new File(outFile);
        JIGUtils.quickSave(outf, new JIGSubPanel[]{panel});
        System.err.println("[tbplot] 已保存: " + outf + " (节点 " + info.node2Pos.size() + ", 边 " + info.nodeLinks.size() + ")");
        System.exit(0);
    }
}
