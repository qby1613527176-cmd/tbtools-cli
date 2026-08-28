import biocjava.bioDoer.JIGplotToolkit.HeatMap.heatmap;
import jigplot.engine.JIGBasePanel;

import java.awt.Color;
import java.io.File;

/**
 * tbplot heatmap2 — TBtools 热图（引擎级，支持聚类/缩放/颜色映射）CLI（08/29 重建）
 *
 * 用法: HeatmapCli <expr.matrix.tsv> <out> [--options]
 *   expr.matrix.tsv: 首列基因名 + 列名表头 + 数值
 *   --options:
 *     --log2 / --log10         对数变换
 *     --rowScale               行归一化
 *     --clusterRow / --clusterCol  行列聚类
 *     --noRowNames / --noColNames  隐藏行列名
 *     --noLegend / --noValue   隐藏图例/数值
 *     --minColor r,g,b --midColor r,g,b --maxColor r,g,b
 *     --width px --height px
 *
 * 引擎: HeatMap.heatmap.show() 返回 JIGBasePanel（GRAS 70基因×81样本验证 SVG 2.08MB，08/28）
 */
public class HeatmapCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: HeatmapCli <expr.tsv> <out> [--log2 --rowScale --clusterRow --clusterCol --width px --height px ...]");
            System.exit(1);
        }
        String exprFile = args[0];
        String outFile = args[1];
        boolean log2 = false, log10 = false, rowScale = false, clusterRow = false, clusterCol = false;
        boolean showRowNames = true, showColNames = true, showLegend = true, showValue = false;
        int width = 1200, height = 1000;
        Color minC = Color.BLUE, midC = Color.WHITE, maxC = Color.RED;
        for (int i = 2; i < args.length; i++) {
            if (args[i].equals("--log2")) log2 = true;
            else if (args[i].equals("--log10")) log10 = true;
            else if (args[i].equals("--rowScale")) rowScale = true;
            else if (args[i].equals("--clusterRow")) clusterRow = true;
            else if (args[i].equals("--clusterCol")) clusterCol = true;
            else if (args[i].equals("--noRowNames")) showRowNames = false;
            else if (args[i].equals("--noColNames")) showColNames = false;
            else if (args[i].equals("--noLegend")) showLegend = false;
            else if (args[i].equals("--showValue")) showValue = true;
            else if (args[i].equals("--minColor") && i+1<args.length) minC = parseColor(args[++i]);
            else if (args[i].equals("--midColor") && i+1<args.length) midC = parseColor(args[++i]);
            else if (args[i].equals("--maxColor") && i+1<args.length) maxC = parseColor(args[++i]);
            else if (args[i].equals("--width") && i+1<args.length) width = Integer.parseInt(args[++i]);
            else if (args[i].equals("--height") && i+1<args.length) height = Integer.parseInt(args[++i]);
        }

        heatmap hm = new heatmap();
        hm.setInExpFile(new File(exprFile));
        if (log2) { hm.setLogScale(true); hm.setLogBase(2.0); }
        else if (log10) { hm.setLogScale(true); hm.setLogBase(10.0); }
        hm.setRowScale(rowScale);
        hm.setClusterRow(clusterRow);
        hm.setClusterCol(clusterCol);
        hm.setShowRowNames(showRowNames);
        hm.setShowColNames(showColNames);
        hm.setShowlegend(showLegend);
        hm.setShowValue(showValue);
        hm.setMinValueColor(minC);
        hm.setMidColor(midC);
        hm.setMaxValueColor(maxC);
        hm.setTotalGraphWidth(width);
        hm.setTotalGraphHeight(height);

        JIGBasePanel panel = hm.show();
        if (panel == null) {
            System.err.println("错误: show() 返回 null");
            System.exit(1);
        }
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) panel.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) panel.save2PDF(new File(outFile));
        else panel.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile);
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