import biocjava.bioDoer.JIGplotToolkit.MACS2viz.peakDistribution;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;
import java.lang.reflect.Method;

/**
 * tbplot peakdist — TBtools Peak 染色体分布图 CLI（08/29 新增，第 26 引擎）
 *
 * 用法: PeakDistCli <chrLen.tsv> <macs2_peak.xls> <out> [--chrHeight H] [--topLenRank N] [--width W] [--height H]
 *   chrLen.tsv: Chr\tLength（染色体长度）
 *   macs2_peak.xls: MACS2 peaks 表格（chr/start/end 列）
 *
 * 引擎: peakDistribution（process() 是 private，用反射 setAccessible 调用）
 *   setInChrLen + setInMACS2Peak + process() -> JIGSubPanel -> save2Graph
 */
public class PeakDistCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: PeakDistCli <chrLen.tsv> <macs2_peak.xls> <out> [--chrHeight H] [--topLenRank N] [--width W] [--height H]");
            System.exit(1);
        }
        String chrLenFile = args[0];
        String peakFile = args[1];
        String outFile = args[2];
        double chrHeight = 0.3;
        int topLenRank = 12;
        int width = 1000, height = 800;
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--chrHeight") && i+1<args.length) chrHeight = Double.parseDouble(args[++i]);
            else if (args[i].equals("--topLenRank") && i+1<args.length) topLenRank = Integer.parseInt(args[++i]);
            else if (args[i].equals("--width") && i+1<args.length) width = Integer.parseInt(args[++i]);
            else if (args[i].equals("--height") && i+1<args.length) height = Integer.parseInt(args[++i]);
        }

        peakDistribution pd = new peakDistribution();
        pd.setInChrLen(new File(chrLenFile));
        pd.setInMACS2Peak(new File(peakFile));
        // process() 是 private，反射调用
        Method m = peakDistribution.class.getDeclaredMethod("process");
        m.setAccessible(true);
        JIGSubPanel panel = (JIGSubPanel) m.invoke(pd);
        if (panel == null) {
            System.err.println("错误: process() 返回 null");
            System.exit(1);
        }

        JIGBasePanel base = new JIGBasePanel(width, height);
        base.addSubPanel(panel);
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) base.save2PDF(new File(outFile));
        else base.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }
}