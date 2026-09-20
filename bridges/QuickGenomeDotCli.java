import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;
import java.lang.reflect.Method;

/**
 * tbplot qdot — Quick Genome Dot Plot CLI（插件 P00380 CLI 化）
 *
 * 用法: QuickGenomeDotCli <blast.tab> <in.gff> <chrLayout.txt> <out.svg> [--point-size N] [--high N] [--mid N] [--low N] [--highlight genes.txt]
 *   blast.tab:    基因对比对结果（diamond 输出，mcscanxd 已产 <g1>vs<g2>.blast）
 *   in.gff:       合并 GFF（mcscanxd 产出 <g1>vs<g2>.gff）
 *   chrLayout.txt: 染色体布局（mcscanxd 产出 *.ChrLayout.tab.xls）
 *   out:          输出 SVG/PNG/PDF
 *
 * 背景: 插件 QuickGenomeDotPlot.process() 尾部调用 JIGUtils.quickShow（GUI 弹窗），
 *   headless 下抛 HeadlessException（实测）。其上游 diamond blast + MCScanX 已由
 *   mcscanxd 完成——本桥直接驱动 dotdotdot 引擎（setChrLayoutFile/setGenePair/setInGff
 *   + process()→JIGSubPanel→JIGBasePanel 保存），绕开 quickShow。
 */
public class QuickGenomeDotCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("用法: QuickGenomeDotCli <blast.tab> <in.gff> <chrLayout.txt> <out.svg> [--point-size N] [--high N] [--mid N] [--low N] [--highlight genes.txt]");
            System.exit(1);
        }
        double pointSize = 2.0, high = 0.8, mid = 0.5, low = 0.1;
        String highlight = null;
        for (int i = 4; i < args.length; i++) {
            if (args[i].equals("--point-size") && i+1 < args.length) pointSize = Double.parseDouble(args[++i]);
            else if (args[i].equals("--high") && i+1 < args.length) high = Double.parseDouble(args[++i]);
            else if (args[i].equals("--mid") && i+1 < args.length) mid = Double.parseDouble(args[++i]);
            else if (args[i].equals("--low") && i+1 < args.length) low = Double.parseDouble(args[++i]);
            else if (args[i].equals("--highlight") && i+1 < args.length) highlight = args[++i];
        }
        Object e = Class.forName("biocjava.bioDoer.JIGplotToolkit.DotPlot.dotdotdot").getDeclaredConstructor().newInstance();
        Class<?> c = e.getClass();
        c.getMethod("setGenePair", File.class).invoke(e, new File(args[0]));
        c.getMethod("setInGff", File.class).invoke(e, new File(args[1]));
        c.getMethod("setChrLayoutFile", File.class).invoke(e, new File(args[2]));
        c.getMethod("setPointSize", double.class).invoke(e, pointSize);
        c.getMethod("setHighConfValue", double.class).invoke(e, high);
        c.getMethod("setMidConfValue", double.class).invoke(e, mid);
        c.getMethod("setLowConfValue", double.class).invoke(e, low);
        c.getMethod("setColorIndex", int.class).invoke(e, 10);
        c.getMethod("setHighColor", java.awt.Color.class).invoke(e, java.awt.Color.RED);
        c.getMethod("setMidColor", java.awt.Color.class).invoke(e, java.awt.Color.ORANGE);
        c.getMethod("setLowColor", java.awt.Color.class).invoke(e, java.awt.Color.WHITE);
        if (highlight != null) c.getMethod("setHighlightGeneFile", File.class).invoke(e, new File(highlight));
        Method process = c.getMethod("process");
        Object result = process.invoke(e);
        if (!(result instanceof JIGSubPanel)) {
            System.err.println("❌ process 未返回 JIGSubPanel");
            System.exit(1);
        }
        JIGBasePanel base = new JIGBasePanel(1200, 800);
        base.addSubPanel((JIGSubPanel) result);
        File outf = new File(args[3]);
        String low2 = args[3].toLowerCase();
        if (low2.endsWith(".png")) base.save2PNG(outf);
        else if (low2.endsWith(".pdf")) base.save2PDF(outf);
        else base.save2SVG(outf);
        System.err.println("[tbplot] 已保存: " + args[3]);
        System.exit(0);
    }
}