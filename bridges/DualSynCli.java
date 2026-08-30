import JJpolt2.Example.DualSyntenyPlotterAdvance;

import java.awt.Component;
import java.awt.Container;
import java.awt.Window;
import java.io.File;
import java.io.FileWriter;
import java.lang.reflect.Field;
import java.lang.reflect.Method;

/**
 * tbplot dualsyn — TBtools 双基因组共线性图 CLI v3（08/31，旧 JJplot2 框架保存破解）
 *
 * 用法: DualSynCli <simplifiedGff> <collinearity> <out> [--chr1 "1,2"] [--chr2 "3,4"] [--rows N] [--gap N]
 *   simplifiedGff: Chr\tGeneName\tStart\tEnd（染色体名必须数字！如 1/2/3 或 "1-1"）
 *   collinearity: MCScanX 输出（*.collinearity）
 *
 * 引擎: DualSyntenyPlotterAdvance（旧 JJplot2 框架）
 *   plot() 内部用静态工厂 prepareBackgroundCoordinateWithoutAxis 建 GUI，
 *   GUI 实例被内部类（$5/$6/$7，含 Ljjplot2/JJplot2GUI 字段）以监听器形式挂在组件树上。
 * 保存: 调 plot() 后反射深度扫描所有窗口+组件+监听器对象，提取 JJplot2GUI 实例
 *       → saveImageAsPNG/PDF/SVG。
 */
public class DualSynCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: DualSynCli <simplifiedGff> <collinearity> <out> [--chr1 \"1,2\"] [--chr2 \"3,4\"] [--rows N] [--gap N]");
            System.exit(1);
        }
        String gffFile = args[0];
        String collinearFile = args[1];
        String outFile = args[2];
        String chr1 = null, chr2 = null;
        int rows = 3, gap = 3;
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--chr1") && i+1<args.length) chr1 = args[++i];
            else if (args[i].equals("--chr2") && i+1<args.length) chr2 = args[++i];
            else if (args[i].equals("--rows") && i+1<args.length) rows = Integer.parseInt(args[++i]);
            else if (args[i].equals("--gap") && i+1<args.length) gap = Integer.parseInt(args[++i]);
        }
        if (chr1 == null || chr2 == null) {
            System.err.println("错误: 必须提供 --chr1 和 --chr2");
            System.exit(1);
        }

        File ctlFile = File.createTempFile("dualsyn", ".ctl");
        ctlFile.deleteOnExit();
        FileWriter fw = new FileWriter(ctlFile);
        fw.write(rows + "\n");
        fw.write(gap + "\n");
        fw.write(chr1 + "\n");
        fw.write(chr2 + "\n");
        fw.close();

        DualSyntenyPlotterAdvance dsp = new DualSyntenyPlotterAdvance();
        dsp.setCtlFile(ctlFile.getAbsolutePath());
        dsp.setCollinerFile(collinearFile);
        dsp.setInSimplifiedGff(gffFile);
        dsp.setGeneColorFile("");
        dsp.plot(); // 内部 JustShowIt 创建窗口

        // 反射扫描窗口树 + 监听器对象，提取 JJplot2GUI 实例
        Object gui = null;
        java.util.Set<Object> visited = new java.util.HashSet<>();
        for (Window w : Window.getWindows()) {
            gui = scan(w, visited);
            if (gui != null) break;
        }
        if (gui == null) {
            System.err.println("错误: 未找到 JJplot2GUI 实例（窗口数=" + Window.getWindows().length + "）");
            System.exit(1);
        }
        System.err.println("[tbplot] 找到 JJplot2GUI 实例: " + gui.getClass().getName());

        // headless 下 GUI 未布局（offScreenImage=3x3）→ 保存前设置目标尺寸，确保图像不糊
        try {
            gui.getClass().getMethod("setWidth", int.class).invoke(gui, 2400);
            gui.getClass().getMethod("setHeight", int.class).invoke(gui, 900);
        } catch (Exception e) { /* 非关键 */ }

        String low = outFile.toLowerCase();
        Method mSave;
        // 正确 API: saveImageAsPNG/SVG/PDF（private，反射调用）——内部用 getAdjusteParamers 创建正确尺寸图像重绘
        if (low.endsWith(".svg")) {
            mSave = gui.getClass().getDeclaredMethod("saveImageAsSVG", String.class);
            mSave.setAccessible(true);
            mSave.invoke(gui, outFile);
        } else if (low.endsWith(".pdf")) {
            mSave = gui.getClass().getMethod("saveImageAsPDF", String.class);
            mSave.invoke(gui, outFile);
        } else {
            mSave = gui.getClass().getMethod("saveImageAsPNG", String.class);
            mSave.invoke(gui, outFile);
        }
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }

    /** 深度扫描：组件树 + 所有对象字段里的监听器，找 JJplot2GUI 类型字段的值 */
    static Object scan(Object obj, java.util.Set<Object> visited) {
        if (obj == null || visited.contains(obj)) return null;
        visited.add(obj);
        Class<?> cls = obj.getClass();
        // 本身是 JJplot2GUI？
        if (cls.getName().equals("jjplot2.JJplot2GUI")) return obj;
        // 遍历所有字段（含私有/继承）
        for (Class<?> c = cls; c != null && c != Object.class; c = c.getSuperclass()) {
            for (Field f : c.getDeclaredFields()) {
                try {
                    f.setAccessible(true);
                    Object v = f.get(obj);
                    if (v == null) continue;
                    if (v.getClass().getName().equals("jjplot2.JJplot2GUI")) return v;
                    // 递归：容器/监听器/集合里的对象
                    if (v instanceof Container || v instanceof java.awt.event.ActionListener
                        || v instanceof java.awt.event.MouseListener || v instanceof java.awt.event.MouseMotionListener
                        || v instanceof java.util.Collection || v instanceof java.util.Map
                        || v.getClass().getName().startsWith("JJpolt2.Example.DualSyntenyPlotterAdvance$")) {
                        Object found = scan(v, visited);
                        if (found != null) return found;
                    }
                } catch (Exception e) { /* ignore */ }
            }
        }
        // 递归子组件
        if (obj instanceof Container) {
            for (Component comp : ((Container) obj).getComponents()) {
                Object found = scan(comp, visited);
                if (found != null) return found;
            }
        }
        // 监听器数组（getListeners）
        if (obj instanceof Component) {
            try {
                Method gL = obj.getClass().getMethod("getListeners", Class.class);
                java.util.EventListener[] ls = (java.util.EventListener[]) gL.invoke(obj, java.util.EventListener.class);
                if (ls != null) {
                    for (java.util.EventListener l : ls) {
                        Object found = scan(l, visited);
                        if (found != null) return found;
                    }
                }
            } catch (Exception e) { /* ignore */ }
        }
        return null;
    }
}