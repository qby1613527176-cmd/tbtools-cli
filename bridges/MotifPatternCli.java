import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;
import java.lang.reflect.Method;

/**
 * tbplot mpattern — MEME/MAST motif 图案标注图 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: MotifPatternCli <mast.xml> <out.svg> [--max-motif N] [--shape RoundRect|Rect|Oval]
 *        [--line Middle|Up|Down|Splice] [--gradient] [--show-num] [--width N] [--height N]
 *
 * 接口来源：反编译 MemeMastMotifPatternGUIPanel（GUI 真实调用链）：
 *   DrawMotifPatternFromMEMEResult dmp = new ...;
 *   dmp.setInFile(mastXml); setMaxMotif(N); setGradient/setShowMotifNum/
 *     setMotifShape(MotifShape)/setLineStyle(LineStyle); [setSeqNotationInfo...]
 *   dmp.postGraph();   // 无参版尾部 GUI 弹窗
 * 规避：postGraph(String, JIGBasePanel) 重载返回 JIGSubPanel → 自己保存
 *   （newickString 参数传空串即可，面板由调用方提供）。
 */
public class MotifPatternCli {
    public static void main(String[] args) throws Exception {
        int maxMotif = 20, width = 1200, height = 600;
        String shape = "RoundRect", line = "Middle";
        boolean gradient = false, showNum = false;
        java.util.ArrayList<String> pos = new java.util.ArrayList<String>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--max-motif") && i+1 < args.length) maxMotif = Integer.parseInt(args[++i]);
            else if (args[i].equals("--shape") && i+1 < args.length) shape = args[++i];
            else if (args[i].equals("--line") && i+1 < args.length) line = args[++i];
            else if (args[i].equals("--gradient")) gradient = true;
            else if (args[i].equals("--show-num")) showNum = true;
            else if (args[i].equals("--width") && i+1 < args.length) width = Integer.parseInt(args[++i]);
            else if (args[i].equals("--height") && i+1 < args.length) height = Integer.parseInt(args[++i]);
            else pos.add(args[i]);
        }
        if (pos.size() < 2) {
            System.err.println("用法: MotifPatternCli <mast.xml> <out.svg> [--max-motif N] [--shape RoundRect|Rect|Oval] [--line Middle|Up|Down|Splice] [--gradient] [--show-num]");
            System.exit(1);
        }
        Object dmp = Class.forName("biocjava.bioDoer.MEME.DrawMotifPattern.DrawMotifPatternFromMEMEResult")
                .getDeclaredConstructor().newInstance();
        Class<?> c = dmp.getClass();
        c.getMethod("setInFile", File.class).invoke(dmp, new File(pos.get(0)));
        c.getMethod("setMaxMotif", int.class).invoke(dmp, Math.min(maxMotif, 20));
        c.getMethod("setGradient", boolean.class).invoke(dmp, gradient);
        c.getMethod("setShowMotifNum", boolean.class).invoke(dmp, showNum);
        Class<?> ms = Class.forName("biocjava.bioDoer.MEME.DrawMotifPattern.DrawMotifPatternFromMEMEResult$MotifShape");
        c.getMethod("setMotifShape", ms).invoke(dmp, Enum.valueOf((Class)ms, shape));
        Class<?> ls = Class.forName("biocjava.bioDoer.MEME.DrawMotifPattern.DrawMotifPatternFromMEMEResult$LineStyle");
        c.getMethod("setLineStyle", ls).invoke(dmp, Enum.valueOf((Class)ls, line));
        JIGBasePanel base = new JIGBasePanel(width, height);
        Object result = c.getMethod("postGraph", String.class, JIGBasePanel.class).invoke(dmp, "", base);
        if (!(result instanceof JIGSubPanel)) {
            System.err.println("❌ postGraph 未返回 JIGSubPanel");
            System.exit(1);
        }
        base.addSubPanel((JIGSubPanel) result);
        File outf = new File(pos.get(1));
        String low = pos.get(1).toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(outf);
        else if (low.endsWith(".pdf")) base.save2PDF(outf);
        else base.save2SVG(outf);
        System.err.println("[tbplot] 已保存: " + pos.get(1));
        System.exit(0);
    }
}