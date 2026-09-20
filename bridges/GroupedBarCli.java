import jigplot.engine.JIGBasePanel;

import java.io.File;
import java.lang.reflect.Method;

/**
 * tbplot gbar — 分组柱状图 + 显著性标注 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: GroupedBarCli <data.tsv> <out.svg> [--header|--no-header] [--group-order FIRST_OCCURRENCE|ALPHABETICAL]
 *        [--errorbar SEM|SD|CI95] [--plot BAR_ERROR|BOXPLOT|VIOLIN|SWARM]
 *        [--title <t>] [--homoscedastic-t] [--width N] [--height N]
 *
 * 接口来源：反编译 GroupedBarSignificanceGUIPanel（GUI 真实调用链）：
 *   GroupedBarRawData raw = GroupedBarRawData.load(file, hasHeader, groupOrder, charset);
 *   GroupedBarStatistics.Options opt = new Options(); opt.homoscedasticT = ...;
 *   AnalysisResult ar = GroupedBarStatistics.analyze(raw.getGroups(), opt);
 *   GroupedBarPlotWithSignificance.showFrame(...);   // showFrame = buildPanel + JFrame 壳
 * 规避：直调 public static buildPanel(raw, ar, eb, pt, title, null) → JIGBasePanel
 *
 * 数据格式（行=样本，列=group value [optionalVariable]）：
 *   Group1 10.2
 *   Group1 12.1
 *   Group2 8.4
 *   ...（首行可选表头）
 */
public class GroupedBarCli {
    public static void main(String[] args) throws Exception {
        boolean hasHeader = true, homoscedastic = false;
        String groupOrder = "FIRST_OCCURRENCE", eb = "SEM", plot = "BAR_ERROR", title = "";
        int width = 1200, height = 800;
        java.util.ArrayList<String> pos = new java.util.ArrayList<String>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--header")) hasHeader = true;
            else if (args[i].equals("--no-header")) hasHeader = false;
            else if (args[i].equals("--group-order") && i+1 < args.length) groupOrder = args[++i];
            else if (args[i].equals("--errorbar") && i+1 < args.length) eb = args[++i];
            else if (args[i].equals("--plot") && i+1 < args.length) plot = args[++i];
            else if (args[i].equals("--title") && i+1 < args.length) title = args[++i];
            else if (args[i].equals("--homoscedastic-t")) homoscedastic = true;
            else if (args[i].equals("--width") && i+1 < args.length) width = Integer.parseInt(args[++i]);
            else if (args[i].equals("--height") && i+1 < args.length) height = Integer.parseInt(args[++i]);
            else pos.add(args[i]);
        }
        if (pos.size() < 2) {
            System.err.println("用法: GroupedBarCli <data.tsv> <out.svg> [--header|--no-header] [--errorbar SEM|SD|CI95] [--plot BAR_ERROR|BOXPLOT|VIOLIN|SWARM] [--homoscedastic-t]");
            System.exit(1);
        }
        File in = new File(pos.get(0));
        String outPath = pos.get(1);
        java.nio.charset.Charset utf8 = java.nio.charset.StandardCharsets.UTF_8;

        Class<?> rawCls = Class.forName("biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarRawData");
        Class<?> go = Class.forName("biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarRawData$GroupOrder");
        Object order = Enum.valueOf((Class)go, groupOrder);
        Object raw = rawCls.getMethod("load", File.class, boolean.class, go, java.nio.charset.Charset.class)
                .invoke(null, in, hasHeader, order, utf8);

        Class<?> statsCls = Class.forName("biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarStatistics");
        Object opt = Class.forName("biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarStatistics$Options")
                .getDeclaredConstructor().newInstance();
        opt.getClass().getField("homoscedasticT").setBoolean(opt, homoscedastic);
        Class<?> gsCls = Class.forName("biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarRawData$GroupSummary");
        Method analyze = statsCls.getMethod("analyze",
                java.util.List.class,
                Class.forName("biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarStatistics$Options"));
        Object ar = analyze.invoke(null, raw.getClass().getMethod("getGroups").invoke(raw), opt);

        Class<?> ebCls = Class.forName("biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarStatistics$ErrorBarType");
        Class<?> ptCls = Class.forName("biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedPlotType");
        Class<?> vcCls = Class.forName("biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.PlotVisualConfig");
        Object cfg = vcCls.getDeclaredConstructor().newInstance();
        java.lang.reflect.Field f;
        f = vcCls.getField("baseFontName"); f.set(cfg, "Arial");
        f = vcCls.getField("fontSize"); f.set(cfg, 14);
        f = vcCls.getField("xLabelAngle"); f.set(cfg, 45f);
        f = vcCls.getField("textColor"); f.set(cfg, java.awt.Color.BLACK);
        f = vcCls.getField("axisColor"); f.set(cfg, java.awt.Color.BLACK);
        f = vcCls.getField("errorBarColor"); f.set(cfg, java.awt.Color.BLACK);
        f = vcCls.getField("lineStroke"); f.set(cfg, 1.2f);
        f = vcCls.getField("significanceGapFactor"); f.set(cfg, 0.05);
        f = vcCls.getField("barHalfWidth"); f.set(cfg, 0.8);
        f = vcCls.getField("boxHalfWidth"); f.set(cfg, 0.8);
        Object panel = Class.forName("biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarPlotWithSignificance")
                .getMethod("buildPanel",
                        rawCls, ar.getClass(), ebCls, ptCls, String.class, vcCls)
                .invoke(null, raw, ar, Enum.valueOf((Class)ebCls, eb), Enum.valueOf((Class)ptCls, plot), title, cfg);
        File outf = new File(outPath);
        String low = outPath.toLowerCase();
        if (low.endsWith(".png")) ((JIGBasePanel) panel).save2PNG(outf);
        else if (low.endsWith(".pdf")) ((JIGBasePanel) panel).save2PDF(outf);
        else ((JIGBasePanel) panel).save2SVG(outf);
        System.err.println("[tbplot] 已保存: " + outPath);
        System.exit(0);
    }
}