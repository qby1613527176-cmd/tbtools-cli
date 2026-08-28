import biocjava.bioDoer.JIGplotToolkit.UpSetPloter.UpSetPlot;
import jigplot.engine.JIGBasePanel;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.HashSet;
import java.util.LinkedHashMap;

/**
 * tbplot upset — TBtools UpSetPlot 交集图 CLI（08/29 重建）
 *
 * 用法: UpSetCli <sets.txt> <out.svg/png> [width] [height]
 *   sets.txt: 每行 "集合名\t成员1\t成员2..."（tab 分隔，集合名后跟成员）
 *   out: 输出 SVG/PNG（按扩展名判断）
 *   width/height: 画布尺寸（默认 1000x800）
 *
 * 引擎: UpSetPlot.plot() 返回 JIGBasePanel（直接 save2Graph）
 */
public class UpSetCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: UpSetCli <sets.txt> <out> [width] [height]");
            System.exit(1);
        }
        String inFile = args[0];
        String outFile = args[1];
        int width = args.length > 2 ? Integer.parseInt(args[2]) : 1000;
        int height = args.length > 3 ? Integer.parseInt(args[3]) : 800;

        // 解析 sets.txt: "集合名\t成员1\t成员2..."
        LinkedHashMap<String, HashSet<String>> setMap = new LinkedHashMap<String, HashSet<String>>();
        BufferedReader br = new BufferedReader(new FileReader(inFile));
        String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] parts = line.split("\t");
            String setName = parts[0];
            HashSet<String> members = new HashSet<String>();
            for (int i = 1; i < parts.length; i++) {
                if (!parts[i].trim().isEmpty()) members.add(parts[i].trim());
            }
            setMap.put(setName, members);
        }
        br.close();
        if (setMap.isEmpty()) {
            System.err.println("错误: 没有解析到任何集合");
            System.exit(1);
        }
        System.err.println("[tbplot] 集合数: " + setMap.size());

        UpSetPlot plot = new UpSetPlot();
        plot.setInSetHashMap(setMap);
        plot.setWidth(width);
        plot.setHeight(height);

        JIGBasePanel panel = plot.plot();
        if (outFile.toLowerCase().endsWith(".png")) {
            panel.save2PNG(new File(outFile));
        } else if (outFile.toLowerCase().endsWith(".pdf")) {
            panel.save2PDF(new File(outFile));
        } else {
            panel.save2SVG(new File(outFile));
        }
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }
}
