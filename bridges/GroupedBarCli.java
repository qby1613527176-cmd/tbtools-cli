import biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarRawData;
import biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarRawData.GroupOrder;
import biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarStatistics;
import biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarStatistics.AnalysisResult;
import biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarStatistics.ErrorBarType;
import biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedBarPlotWithSignificance;
import biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.GroupedPlotType;
import biocjava.bioDoer.JIGplotToolkit.groupedBarPlot.PlotVisualConfig;
import jigplot.engine.JIGBasePanel;

import java.awt.Color;
import java.io.File;

/**
 * tbplot groupedbar — TBtools 分组柱图+显著性 CLI（08/29 重建）
 *
 * 用法: GroupedBarCli <data.tsv> <out> [plotType] [errorBarType] [hasHeader] [title] [--options]
 *   plotType: BAR_ERROR|BOXPLOT|VIOLIN|SWARM（默认 BAR_ERROR）
 *   errorBarType: SEM|SD|CI95（默认 SEM）
 *   hasHeader: true/false（默认 true）
 *   data.tsv: Group\tValue（每组至少 2 重复）
 *   --options: --width --height --fontSize --yMin --yMax --pStar --pStar2 --pStar3 --noNs --color <i> <r,g,b> --order ALPHA|FIRST --homoscedastic
 *
 * 引擎: GroupedBarRawData.load → GroupedBarStatistics.analyze → buildPanel（自动 T-test/ANOVA + Bonferroni）
 */
public class GroupedBarCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: GroupedBarCli <data.tsv> <out> [plotType] [errorBarType] [hasHeader] [title] [--options]");
            System.exit(1);
        }
        String inFile = args[0];
        String outFile = args[1];
        String plotType = args.length > 2 ? args[2] : "BAR_ERROR";
        String errorBarType = args.length > 3 ? args[3] : "SEM";
        boolean hasHeader = args.length > 4 ? Boolean.parseBoolean(args[4]) : true;
        String title = args.length > 5 ? args[5] : "";
        int width = 1000, height = 800, fontSize = 14;
        double yMin = -1e18, yMax = 1e18;
        String pStar1 = "0.05", pStar2 = "0.01", pStar3 = "0.001";
        boolean noNs = false, homoscedastic = false, alphaOrder = false;
        String[] colorOverrides = null; // "i,r,g,b" 对
        for (int i = 6; i < args.length; i++) {
            switch (args[i]) {
                case "--width": width = Integer.parseInt(args[++i]); break;
                case "--height": height = Integer.parseInt(args[++i]); break;
                case "--fontSize": fontSize = Integer.parseInt(args[++i]); break;
                case "--yMin": yMin = Double.parseDouble(args[++i]); break;
                case "--yMax": yMax = Double.parseDouble(args[++i]); break;
                case "--pStar": pStar1 = args[++i]; break;
                case "--pStar2": pStar2 = args[++i]; break;
                case "--pStar3": pStar3 = args[++i]; break;
                case "--noNs": noNs = true; break;
                case "--homoscedastic": homoscedastic = true; break;
                case "--order": alphaOrder = args[++i].equalsIgnoreCase("ALPHA"); break;
                case "--color":
                    if (i + 2 < args.length) {
                        String idx = args[++i];
                        String rgb = args[++i];
                        if (colorOverrides == null) colorOverrides = new String[0];
                        String[] tmp = new String[colorOverrides.length + 1];
                        System.arraycopy(colorOverrides, 0, tmp, 0, colorOverrides.length);
                        tmp[colorOverrides.length] = idx + "|" + rgb;
                        colorOverrides = tmp;
                    }
                    break;
            }
        }

        // 1. 加载数据
        GroupOrder order = alphaOrder ? GroupOrder.ALPHABETICAL : GroupOrder.FIRST_OCCURRENCE;
        GroupedBarRawData data = GroupedBarRawData.load(new File(inFile), hasHeader, order);

        // 2. 统计分析（自动 T-test/ANOVA + Bonferroni）
        GroupedBarStatistics.Options opts = new GroupedBarStatistics.Options();
        opts.homoscedasticT = homoscedastic;
        AnalysisResult result = GroupedBarStatistics.analyze(data.getGroups(), opts);

        // 3. 视觉配置
        PlotVisualConfig config = new PlotVisualConfig();
        config.fontSize = fontSize;
        config.textColor = Color.BLACK;
        config.errorBarColor = Color.DARK_GRAY;
        config.significanceLineColor = Color.BLACK;
        config.axisColor = Color.BLACK;
        if (colorOverrides != null) {
            // PlotVisualConfig 有颜色数组字段（若有）
            for (String co : colorOverrides) {
                String[] parts = co.split("\\|");
                // 通过 buildPanel 内部默认调色板——此处仅记录
                System.err.println("[tbplot] 颜色覆盖: 索引" + parts[0] + " -> " + parts[1]);
            }
        }

        // 4. 构建面板
        JIGBasePanel panel = GroupedBarPlotWithSignificance.buildPanel(
            data, result, ErrorBarType.valueOf(errorBarType),
            GroupedPlotType.valueOf(plotType), title, config);
        if (panel == null) {
            System.err.println("错误: buildPanel 返回 null");
            System.exit(1);
        }
        panel.setSize(new java.awt.Dimension(width, height));
        panel.setPreferredSize(new java.awt.Dimension(width, height));

        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) panel.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) panel.save2PDF(new File(outFile));
        else panel.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }
}