import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;
import jigplot.OtherTools.JIGUtils;

import java.awt.Color;
import java.io.File;
import java.lang.reflect.Method;
import java.util.ArrayList;

/**
 * GenericCli — TBtools 通用反射绘图桥（08/29 新增，根治 /tmp 清理导致桥丢失）
 *
 * 用反射驱动任意 TBtools 引擎，覆盖统一模式：
 *   setter(File/String/int/boolean/double/Color) → plot()/process()/makeGraph() → JIGSubPanel(JIGSubPanel[]) → save2Graph
 *
 * 用法:
 *   java -cp JAR:tbplot_cli GenericCli <engineClass> <method> <outFile> [--set field value ...] [--width N] [--height N]
 *
 *   engineClass: 完整类名（如 biocjava.bioDoer.JIGplotToolkit.Synteny.MultipleSpeciesSyteny）
 *   method:      绘图方法名，可用 + 连接按序调用（如 doPCA+postGraph => 先 doPCA 再 postGraph）
 *                plot / process / makeGraph / postGraph 等，返回 JIGSubPanel(JIGSubPanel[]) 的作为结果
 *   outFile:     输出 SVG/PNG
 *   --set:       调用 set<Field>(value)，类型自动推断:
 *                  File   -> new File(value)
 *                  String -> value
 *                  int    -> Integer.parseInt
 *                  double -> Double.parseDouble
 *                  float  -> Float.parseFloat
 *                  boolean-> Boolean.parseBoolean
 *                  Color  -> 解析 "r,g,b" 或 名字（RED/GREEN/...）
 *                  Enum   -> Enum.valueOf(type, value)
 *   --width/--height: JIGBasePanel 尺寸（默认 1000x800）
 */
public class GenericCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: GenericCli <engineClass> <method> <outFile> [--set field value ...] [--width N] [--height N]");
            System.err.println("例: GenericCli biocjava.bioDoer.JIGplotToolkit.Synteny.MultipleSpeciesSyteny plot out.svg --set inSimplifiedGff genes.pos --set chrLayoutFile layout.txt --set genePairInfoFile links.txt");
            System.exit(1);
        }
        String engineClass = args[0];
        String methodName = args[1];
        String outFile = args[2];
        int width = 1000, height = 800;

        // 解析 --set / --width / --height
        ArrayList<String[]> setters = new ArrayList<String[]>();
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--set") && i + 2 < args.length) {
                setters.add(new String[]{args[i+1], args[i+2]});
                i += 2;
            } else if (args[i].equals("--width") && i + 1 < args.length) {
                width = Integer.parseInt(args[i+1]); i++;
            } else if (args[i].equals("--height") && i + 1 < args.length) {
                height = Integer.parseInt(args[i+1]); i++;
            }
        }

        Class<?> cls = Class.forName(engineClass);
        Object engine = cls.getDeclaredConstructor().newInstance();

        // 应用 setter
        for (String[] kv : setters) {
            String field = kv[0];
            String value = kv[1];
            String setterName = "set" + Character.toUpperCase(field.charAt(0)) + field.substring(1);
            Method setter = findSetter(cls, setterName);
            if (setter == null) {
                System.err.println("警告: 未找到 setter " + setterName + "，跳过");
                continue;
            }
            Class<?> ptype = setter.getParameterTypes()[0];
            Object pval = coerce(ptype, value);
            setter.invoke(engine, pval);
            System.err.println("set " + field + " = " + value);
        }

        // 调用绘图方法（支持 + 连接多方法）
        Object lastResult = null;
        for (String mn : methodName.split("\\+")) {
            Method method = findMethod(cls, mn.trim());
            if (method == null) {
                System.err.println("错误: 未找到方法 " + mn.trim() + " in " + engineClass);
                System.exit(1);
            }
            Object result = method.invoke(engine);
            if (result != null) lastResult = result;
        }

        // 收集返回的 JIGSubPanel（支持单面板 / 面板数组）
        ArrayList<JIGSubPanel> panels = new ArrayList<JIGSubPanel>();
        if (lastResult == null) {
            System.err.println("错误: 方法链未返回 JIGSubPanel，无法保存");
            System.exit(1);
        }
        if (lastResult instanceof JIGSubPanel) {
            panels.add((JIGSubPanel) lastResult);
        } else if (lastResult instanceof JIGSubPanel[]) {
            for (JIGSubPanel p : (JIGSubPanel[]) lastResult) panels.add(p);
        } else {
            System.err.println("警告: 返回类型 " + lastResult.getClass() + " 不是 JIGSubPanel");
        }

        if (panels.isEmpty()) {
            System.err.println("错误: 没有可保存的绘图面板");
            System.exit(1);
        }

        JIGSubPanel[] arr = panels.toArray(new JIGSubPanel[0]);
        // 固定尺寸 JIGBasePanel + addSubPanel + 直接保存（参照 SuperCircosCli 成功模式，
        // 不做 quickArrange/setSize——那些会对某些引擎产生异常尺寸）
        JIGBasePanel base = new JIGBasePanel(width, height);
        for (JIGSubPanel p : arr) base.addSubPanel(p);
        File outf = new File(outFile);
        String low = outFile.toLowerCase();
        if (low.endsWith(".svg")) base.save2SVG(outf);
        else if (low.endsWith(".png")) base.save2PNG(outf);
        else if (low.endsWith(".pdf")) base.save2PDF(outf);
        else { base.save2SVG(new File(outFile + ".svg")); }
        System.err.println("已保存: " + outFile + " (" + panels.size() + " 面板, " + width + "x" + height + ")");
        // 强制退出：某些引擎绘图后残留非 daemon 线程（如图例监听），
        // 不 exit 会导致 JVM 永不退出，命令悬挂到超时
        System.exit(0);
    }

    static Method findSetter(Class<?> cls, String name) {
        for (Method m : cls.getMethods()) {
            if (m.getName().equals(name) && m.getParameterCount() == 1) return m;
        }
        return null;
    }
    static Method findMethod(Class<?> cls, String name) {
        for (Method m : cls.getMethods()) {
            if (m.getName().equals(name)) return m;
        }
        return null;
    }

    static Object coerce(Class<?> type, String value) {
        if (type == File.class) return new File(value);
        if (type == String.class) return value;
        if (type == int.class || type == Integer.class) return Integer.parseInt(value);
        if (type == double.class || type == Double.class) return Double.parseDouble(value);
        if (type == float.class || type == Float.class) return Float.parseFloat(value);
        if (type == boolean.class || type == Boolean.class) return Boolean.parseBoolean(value);
        if (type == Color.class) return parseColor(value);
        if (type.isEnum()) return Enum.valueOf((Class<Enum>) type, value);
        if (type == long.class || type == Long.class) return Long.parseLong(value);
        if (type == byte.class || type == Byte.class) return Byte.parseByte(value);
        if (type == short.class || type == Short.class) return Short.parseShort(value);
        throw new RuntimeException("不支持的类型: " + type + " for value " + value);
    }

    static Color parseColor(String s) {
        String t = s.trim().toUpperCase();
        try {
            String[] rgb = s.split(",");
            if (rgb.length == 3) return new Color(Integer.parseInt(rgb[0].trim()), Integer.parseInt(rgb[1].trim()), Integer.parseInt(rgb[2].trim()));
        } catch (Exception e) { /* fall through */ }
        switch (t) {
            case "RED": return Color.RED;
            case "GREEN": return Color.GREEN;
            case "BLUE": return Color.BLUE;
            case "YELLOW": return Color.YELLOW;
            case "CYAN": return Color.CYAN;
            case "MAGENTA": return Color.MAGENTA;
            case "ORANGE": return Color.ORANGE;
            case "PINK": return Color.PINK;
            case "BLACK": return Color.BLACK;
            case "WHITE": return Color.WHITE;
            case "GRAY": case "GREY": return Color.GRAY;
            case "LIGHT_GRAY": case "LIGHTGREY": return Color.LIGHT_GRAY;
            case "DARK_GRAY": case "DARKGREY": return Color.DARK_GRAY;
        }
        throw new RuntimeException("无法解析颜色: " + s);
    }
}
