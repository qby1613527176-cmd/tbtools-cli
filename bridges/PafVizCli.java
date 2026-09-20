import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;
import java.lang.reflect.Method;

/**
 * tbplot pafviz — PAF 基因组比对可视化 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: PafVizCli <in.paf> <out.svg> [--graph-size N] [--color Target|Query|None]
 *        [--seed N] [--min-len N] [--switch-qnt] [--rc-color] [--width N] [--height N]
 *
 * 接口来源：反编译 PAFVizGUIPanel（GUI 真实调用链）：
 *   PafViz pv = new PafViz();
 *   pv.setInPaf/setGraphSize/setCurColorMode/setColorRandSeed/setMinAlnLen/
 *      setSwitchQnT/setRcColor;
 *   pv.viz_process();          // 尾部 quickShow GUI 弹窗（headless 崩）
 * 规避：viz_process = process()（public，返回 JIGSubPanel）+ quickShow。
 *   直调 process() 拿 panel → JIGBasePanel.save2* 保存（同 qdot/DeHist 模式）。
 */
public class PafVizCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: PafVizCli <in.paf> <out.svg> [--graph-size N] [--color Target|Query|None] [--seed N] [--min-len N] [--switch-qnt] [--rc-color] [--width N] [--height N]");
            System.exit(1);
        }
        int graphSize = 600, seed = 1, minLen = 0, width = 1200, height = 800;
        String color = "Target";
        boolean switchQnT = false, rcColor = false;
        for (int i = 2; i < args.length; i++) {
            if (args[i].equals("--graph-size") && i+1 < args.length) graphSize = Integer.parseInt(args[++i]);
            else if (args[i].equals("--color") && i+1 < args.length) color = args[++i];
            else if (args[i].equals("--seed") && i+1 < args.length) seed = Integer.parseInt(args[++i]);
            else if (args[i].equals("--min-len") && i+1 < args.length) minLen = Integer.parseInt(args[++i]);
            else if (args[i].equals("--width") && i+1 < args.length) width = Integer.parseInt(args[++i]);
            else if (args[i].equals("--height") && i+1 < args.length) height = Integer.parseInt(args[++i]);
            else if (args[i].equals("--switch-qnt")) switchQnT = true;
            else if (args[i].equals("--rc-color")) rcColor = true;
        }
        Object pv = Class.forName("biocjava.bioDoer.JIGplotToolkit.Paf.PafViz").getDeclaredConstructor().newInstance();
        Class<?> c = pv.getClass();
        c.getMethod("setInPaf", File.class).invoke(pv, new File(args[0]));
        c.getMethod("setGraphSize", int.class).invoke(pv, graphSize);
        Class<?> cm = Class.forName("biocjava.bioDoer.JIGplotToolkit.Paf.PafViz$ColorMode");
        Object cmEnum = Enum.valueOf((Class)cm, color);
        c.getMethod("setCurColorMode", cm).invoke(pv, cmEnum);
        c.getMethod("setColorRandSeed", int.class).invoke(pv, seed);
        c.getMethod("setMinAlnLen", int.class).invoke(pv, minLen);
        c.getMethod("setSwitchQnT", boolean.class).invoke(pv, switchQnT);
        c.getMethod("setRcColor", boolean.class).invoke(pv, rcColor);
        Method process = c.getMethod("process");
        Object result = process.invoke(pv);
        if (!(result instanceof JIGSubPanel)) {
            System.err.println("❌ process 未返回 JIGSubPanel");
            System.exit(1);
        }
        JIGBasePanel base = new JIGBasePanel(width, height);
        base.addSubPanel((JIGSubPanel) result);
        File outf = new File(args[1]);
        String low = args[1].toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(outf);
        else if (low.endsWith(".pdf")) base.save2PDF(outf);
        else base.save2SVG(outf);
        System.err.println("[tbplot] 已保存: " + args[1]);
        System.exit(0);
    }
}
