import jigplot.geom.violin.ViolinPlot;

import java.io.File;
import java.util.ArrayList;

/**
 * tbplot violin — 独立小提琴图 CLI（08/31 第六十五波）
 *
 * 用法: ViolinCli <in.tsv> <out> [width] [height]
 *   in.tsv: 组别\t值（每行一个观测；第一行可作表头）
 *   out:    .svg / .png / .pdf
 *
 * 引擎: ViolinPlot.generate() + saveToSVG/PNG/PDF（独立引擎，非 groupedbar VIOLIN 模式）
 */
public class ViolinCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: ViolinCli <in.tsv> <out> [width] [height]");
            System.exit(1);
        }
        String inFile = args[0];
        String out = args[1];
        int width = args.length > 2 ? Integer.parseInt(args[2]) : 800;
        int height = args.length > 3 ? Integer.parseInt(args[3]) : 500;

        // 读取 组别\t值（跳过表头）
        ArrayList<double[]> dataSets = new ArrayList<>();
        ArrayList<String> labels = new ArrayList<>();
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.FileReader(inFile));
        String line;
        java.util.LinkedHashMap<String, ArrayList<Double>> groups = new java.util.LinkedHashMap<>();
        while ((line = br.readLine()) != null) {
            String t = line.trim();
            if (t.isEmpty() || t.startsWith("#")) continue;
            String[] cols = t.split("\t");
            if (cols.length < 2) continue;
            String g = cols[0];
            // 跳过表头（组别非数字且第一行）
            try { Double.parseDouble(cols[1]); } catch (Exception e) { continue; }
            groups.computeIfAbsent(g, k -> new ArrayList<>()).add(Double.parseDouble(cols[1]));
        }
        br.close();
        for (String g : groups.keySet()) {
            ArrayList<Double> vals = groups.get(g);
            double[] arr = new double[vals.size()];
            for (int i = 0; i < vals.size(); i++) arr[i] = vals.get(i);
            dataSets.add(arr);
            labels.add(g);
        }
        if (dataSets.isEmpty()) {
            System.err.println("错误: 无数据（需 组别\t值 每行）");
            System.exit(1);
        }

        ViolinPlot vp = new ViolinPlot(dataSets, labels.toArray(new String[0]));
        vp.setTotalGraphWidth(width);
        vp.setTotalGraphHeight(height);
        vp.generate();

        String low = out.toLowerCase();
        if (low.endsWith(".pdf")) vp.saveToPDF(new File(out));
        else vp.saveToSVG(new File(out));
        System.err.println("[tbplot] 已保存: " + out + " (" + labels.size() + " 组)");
        System.exit(0);
    }
}
