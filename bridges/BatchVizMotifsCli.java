import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;
import java.lang.reflect.Method;

/**
 * tbplot memeViz — MEME motif 批量可视化 CLI（插件 P00700 CLI 化）
 *
 * 用法: BatchVizMotifsCli <meme.xml> <out.svg> [width] [height]
 *   meme.xml: MEME suite 输出（meme.xml 格式）
 *   out:      SVG/PNG/PDF 图
 *
 * 引擎: BatchVizMotifs.BatchVizMotifs（插件 jar），setInMEMEXml + process()
 *   → JIGSubPanel[]（每个 motif 一个面板）→ JIGBasePanel 保存。
 */
public class BatchVizMotifsCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: BatchVizMotifsCli <meme.xml> <out.svg> [width] [height]");
            System.exit(1);
        }
        int width = args.length > 2 ? Integer.parseInt(args[2]) : 1000;
        int height = args.length > 3 ? Integer.parseInt(args[3]) : 800;

        Object engine = Class.forName("BatchVizMotifs.BatchVizMotifs")
                .getDeclaredConstructor().newInstance();
        Class<?> c = engine.getClass();
        c.getMethod("setInMEMEXml", File.class).invoke(engine, new File(args[0]));
        Method process = c.getMethod("process");
        Object result = process.invoke(engine);
        if (!(result instanceof JIGSubPanel[])) {
            System.err.println("❌ process 未返回 JIGSubPanel[]");
            System.exit(1);
        }
        JIGSubPanel[] panels = (JIGSubPanel[]) result;
        JIGBasePanel base = new JIGBasePanel(width, height);
        for (JIGSubPanel p : panels) base.addSubPanel(p);
        File outf = new File(args[1]);
        String low = args[1].toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(outf);
        else if (low.endsWith(".pdf")) base.save2PDF(outf);
        else base.save2SVG(outf);
        System.err.println("[tbplot] 已保存: " + args[1] + " (" + panels.length + " motif 面板)");
        System.exit(0);
    }
}
