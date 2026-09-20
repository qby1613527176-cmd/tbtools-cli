import jigplot.engine.JIGBasePanel;

import java.io.File;
import java.lang.reflect.Method;
import java.util.HashSet;
import java.util.LinkedHashMap;

/**
 * tbplot upset — UpSet 图 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: UpSetCli <set1.txt> <set2.txt> [<set3.txt>...] <out.svg> [--min-overlap N]
 *        [--rank1 Size|Count|Name] [--rank2 Size|Count|Name] [--rank3 Size|Count|Name]
 *        [--size-mode Increasing|Decreasing] [--count-mode ...] [--name-mode ...]
 *        [--width N] [--height N]
 *
 * 接口来源：反编译 QuickUpSetPlotGUIPanel（GUI 真实调用链）：
 *   每个文件读成 HashSet（文件名→ID 集合）：
 *   UpSetPlotControl usp = new UpSetPlotControl();
 *   usp.setInSetHashMap(map); usp.setMinOverlapSetSize(N);
 *   usp.setFristRank/setSecondRank/setThirdRank(rankKey);
 *   usp.setSetSizeRankMode/setSetCountRankMode/setSetNameRankMode(rankMode);
 *   usp.show();    // show() = plot() + JFrame 壳（headless 崩）
 * 规避：直调 plot()（public，返回 JIGBasePanel）→ save2* 保存。
 */
public class UpSetCli {
    public static void main(String[] args) throws Exception {
        int minOverlap = 0, width = 1200, height = 800;
        String rank1 = "Size", rank2 = "Count", rank3 = "Name";
        String sizeMode = "Decreasing", countMode = "Decreasing", nameMode = "Increasing";
        java.util.ArrayList<String> pos = new java.util.ArrayList<String>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--min-overlap") && i+1 < args.length) minOverlap = Integer.parseInt(args[++i]);
            else if (args[i].equals("--rank1") && i+1 < args.length) rank1 = args[++i];
            else if (args[i].equals("--rank2") && i+1 < args.length) rank2 = args[++i];
            else if (args[i].equals("--rank3") && i+1 < args.length) rank3 = args[++i];
            else if (args[i].equals("--size-mode") && i+1 < args.length) sizeMode = args[++i];
            else if (args[i].equals("--count-mode") && i+1 < args.length) countMode = args[++i];
            else if (args[i].equals("--name-mode") && i+1 < args.length) nameMode = args[++i];
            else if (args[i].equals("--width") && i+1 < args.length) width = Integer.parseInt(args[++i]);
            else if (args[i].equals("--height") && i+1 < args.length) height = Integer.parseInt(args[++i]);
            else pos.add(args[i]);
        }
        if (pos.size() < 3) {
            System.err.println("用法: UpSetCli <set1.txt> <set2.txt> [<set3.txt>...] <out.svg> [--min-overlap N] [--rank1 Size|Count|Name] ...");
            System.exit(1);
        }
        String outPath = pos.remove(pos.size() - 1);
        // 读集合（文件内容每行一个 ID，集合标题 = 文件名）
        LinkedHashMap<String, HashSet<String>> map = new LinkedHashMap<String, HashSet<String>>();
        for (String fp : pos) {
            File f = new File(fp);
            HashSet<String> ids = new HashSet<String>();
            java.io.BufferedReader br = new java.io.BufferedReader(new java.io.FileReader(f));
            String line;
            while ((line = br.readLine()) != null) {
                String t = line.trim();
                if (!t.isEmpty()) ids.add(t);
            }
            br.close();
            map.put(f.getName(), ids);
        }
        // show() 内部实际是 new UpSetPlot()（控件的 setter 会转投到它）——
        // 直接实例化 UpSetPlot：setInSetHashMap + plot() 返回 JIGBasePanel
        Object usp = Class.forName("biocjava.bioDoer.JIGplotToolkit.UpSetPloter.UpSetPlot")
                .getDeclaredConstructor().newInstance();
        Class<?> c = usp.getClass();
        c.getMethod("setInSetHashMap", LinkedHashMap.class).invoke(usp, map);
        c.getMethod("setMinOverlapSetSize", int.class).invoke(usp, minOverlap);
        Class<?> rk = Class.forName("biocjava.bioDoer.JIGplotToolkit.UpSetPloter.UpSetPlot$rankKey");
        c.getMethod("setFristRank", rk).invoke(usp, Enum.valueOf((Class)rk, rank1));
        c.getMethod("setSecondRank", rk).invoke(usp, Enum.valueOf((Class)rk, rank2));
        c.getMethod("setThirdRank", rk).invoke(usp, Enum.valueOf((Class)rk, rank3));
        Class<?> rm = Class.forName("biocjava.bioDoer.JIGplotToolkit.UpSetPloter.UpSetPlot$rankMode");
        c.getMethod("setSetSizeRankMode", rm).invoke(usp, Enum.valueOf((Class)rm, sizeMode));
        c.getMethod("setSetCountRankMode", rm).invoke(usp, Enum.valueOf((Class)rm, countMode));
        c.getMethod("setSetNameRankMode", rm).invoke(usp, Enum.valueOf((Class)rm, nameMode));
        Object panel = c.getMethod("plot").invoke(usp);
        if (!(panel instanceof JIGBasePanel)) {
            System.err.println("❌ plot 未返回 JIGBasePanel");
            System.exit(1);
        }
        File outf = new File(outPath);
        String low = outPath.toLowerCase();
        if (low.endsWith(".png")) ((JIGBasePanel) panel).save2PNG(outf);
        else if (low.endsWith(".pdf")) ((JIGBasePanel) panel).save2PDF(outf);
        else ((JIGBasePanel) panel).save2SVG(outf);
        System.err.println("[tbplot] 已保存: " + outPath);
        System.exit(0);
    }
}