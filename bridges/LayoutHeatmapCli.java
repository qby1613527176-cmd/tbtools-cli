import biocjava.bioDoer.JIGplotToolkit.HeatMap.LayoutHeatmap;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.awt.Color;
import java.io.File;

/**
 * tbplot layoutheatmap — TBtools 布局热图 CLI（08/29 重建）
 *
 * 用法: LayoutHeatmapCli <layout.tsv> <expr.tsv> <out> [--options]
 *   layout.tsv: 样本名矩阵（TSV，定义样本在热图中的布局位置；空位用 NA）
 *   expr.tsv: 表达矩阵（首列基因名 + 样本名表头 + 数值）
 *   --options: --cellWidth --cellHeight --yGap --log2 --log10 --rowScale --minColor r,g,b
 *              --midColor r,g,b --maxColor r,g,b --nanColor r,g,b --noLegend --noValue --rename f --topLeft
 *
 * 引擎: LayoutHeatmap.plot() 返回 JIGSubPanel[]（3×3 布局+5 基因验证 SVG 67KB，08/28）
 */
public class LayoutHeatmapCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: LayoutHeatmapCli <layout.tsv> <expr.tsv> <out> [--options]");
            System.exit(1);
        }
        String layoutFile = args[0];
        String exprFile = args[1];
        String outFile = args[2];
        int cellWidth = 50, cellHeight = 50, yGap = 30;
        boolean log2 = false, log10 = false, rowScale = false, showLegend = true, showValue = true;
        Color minC = Color.BLUE, midC = Color.WHITE, maxC = Color.RED, nanC = Color.GRAY;
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--cellWidth") && i+1<args.length) cellWidth = Integer.parseInt(args[++i]);
            else if (args[i].equals("--cellHeight") && i+1<args.length) cellHeight = Integer.parseInt(args[++i]);
            else if (args[i].equals("--yGap") && i+1<args.length) yGap = Integer.parseInt(args[++i]);
            else if (args[i].equals("--log2")) log2 = true;
            else if (args[i].equals("--log10")) log10 = true;
            else if (args[i].equals("--rowScale")) rowScale = true;
            else if (args[i].equals("--noLegend")) showLegend = false;
            else if (args[i].equals("--noValue")) showValue = false;
            else if (args[i].equals("--minColor") && i+1<args.length) minC = parseColor(args[++i]);
            else if (args[i].equals("--midColor") && i+1<args.length) midC = parseColor(args[++i]);
            else if (args[i].equals("--maxColor") && i+1<args.length) maxC = parseColor(args[++i]);
            else if (args[i].equals("--nanColor") && i+1<args.length) nanC = parseColor(args[++i]);
        }

        LayoutHeatmap hm = new LayoutHeatmap();
        hm.setLayoutFile(new File(layoutFile));
        hm.setInExpFile(new File(exprFile));
        // 绕过引擎硬编码的 Windows 测试路径 I:\\TBtools用户测试数据\\...\\renamingInfo.txt
        // （构造函数默认指向该不存在路径，plot() 读取时 FileNotFoundException）
        File renamingFile = File.createTempFile("tbplot_renaming", ".txt");
        renamingFile.deleteOnExit();
        hm.setRenamingInfo(renamingFile);
        hm.setCellWidth(cellWidth);
        hm.setCellHeight(cellHeight);
        hm.setyGap(yGap);
        if (log2) { hm.setLogScale(true); hm.setLogBase(2.0); }
        else if (log10) { hm.setLogScale(true); hm.setLogBase(10.0); }
        hm.setRowScale(rowScale);
        hm.setMinValueColor(minC);
        hm.setMidColor(midC);
        hm.setMaxValueColor(maxC);
        hm.setNaNColor(nanC);
        hm.setShowLegend(showLegend);
        // 数值显示（若 setter 存在）
        try { hm.getClass().getMethod("setShowValue", boolean.class).invoke(hm, showValue); } catch (Exception e) {}

        JIGSubPanel[] panels = hm.plot();
        if (panels == null || panels.length == 0) {
            System.err.println("错误: plot() 返回空");
            System.exit(1);
        }
        JIGBasePanel base = new JIGBasePanel(1200, 800);
        for (JIGSubPanel p : panels) base.addSubPanel(p);
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) base.save2PDF(new File(outFile));
        else base.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile + " (" + panels.length + " 面板)");
        System.exit(0);
    }

    static Color parseColor(String s) {
        try {
            String[] rgb = s.split(",");
            if (rgb.length == 3) return new Color(Integer.parseInt(rgb[0].trim()), Integer.parseInt(rgb[1].trim()), Integer.parseInt(rgb[2].trim()));
        } catch (Exception e) {}
        return Color.WHITE;
    }
}