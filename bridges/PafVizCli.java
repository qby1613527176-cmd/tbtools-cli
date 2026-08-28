import biocjava.bioDoer.JIGplotToolkit.Paf.PafViz;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;

/**
 * tbplot pafviz — TBtools PAF 比对 Dot-plot CLI（08/29 重建）
 *
 * 用法: PafVizCli <in.paf> <out> [graphSize] [colorMode] [switchQT] [minAlnLen] [rcColor]
 *   colorMode: Target|Query|None（默认 Target）
 *   switchQT: true/false 交换 Query/Target 轴（默认 false）
 *   minAlnLen: 最小比对长度过滤（默认 0）
 *   rcColor: true/false 反向互补段反色（默认 false）
 *
 * 引擎: PafViz
 *   setInPaf + setCurColorMode(枚举) + process() 返回 JIGSubPanel
 */
public class PafVizCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: PafVizCli <in.paf> <out> [graphSize] [colorMode] [switchQT] [minAlnLen] [rcColor]");
            System.exit(1);
        }
        String inPaf = args[0];
        String outFile = args[1];
        int graphSize = args.length > 2 ? Integer.parseInt(args[2]) : 1000;
        String colorMode = args.length > 3 ? args[3] : "Target";
        boolean switchQT = args.length > 4 && Boolean.parseBoolean(args[4]);
        int minAlnLen = args.length > 5 ? Integer.parseInt(args[5]) : 0;
        boolean rcColor = args.length > 6 && Boolean.parseBoolean(args[6]);

        PafViz viz = new PafViz();
        viz.setInPaf(new File(inPaf));
        viz.setGraphSize(graphSize);
        viz.setCurColorMode(PafViz.ColorMode.valueOf(colorMode));
        viz.setSwitchQnT(switchQT);
        viz.setMinAlnLen(minAlnLen);
        viz.setRcColor(rcColor);

        JIGSubPanel panel = viz.process();
        JIGBasePanel base = new JIGBasePanel(graphSize, graphSize);
        base.addSubPanel(panel);
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) base.save2PDF(new File(outFile));
        else base.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }
}