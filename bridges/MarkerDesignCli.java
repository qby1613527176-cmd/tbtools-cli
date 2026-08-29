import java.io.File;
import java.io.PrintStream;
import java.io.ByteArrayOutputStream;
import java.lang.reflect.Method;

/**
 * tbplot marker — TBtools 标记设计工具 CLI（08/29，第 46-48 引擎）
 *
 * 用法: MarkerDesignCli <engineClass> <inMarker> <out.txt> [--maxPoint N]
 *   engineClass: MarkerDist|MarkerFilter|SampleDist（biocjava.bioDoer.markerDesign 下）
 *   inMarker: 标记 0-1 矩阵（tab 分隔）
 *   --maxPoint: MarkerDist 专用（最大点数）
 *
 * ⚠️ 引擎输出模式差异（08/29 反编译确认，统一兼容）：
 *   - MarkerDist:   process() 返回结果字符串（result 非空）→ 直接写文件
 *   - MarkerFilter: process() 返回 null，结果走 System.err.println
 *   - SampleDist:   process() 返回 ""，结果走 System.err.println
 *   桥在 process() 期间重定向 System.err 到缓冲，若返回字符串为空则把捕获的 stderr 写入文件。
 */
public class MarkerDesignCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: MarkerDesignCli <MarkerDist|MarkerFilter|SampleDist> <inMarker> <out.txt> [--maxPoint N]");
            System.exit(1);
        }
        String engine = args[0];
        String inMarker = args[1];
        String out = args[2];
        String clsName = "biocjava.bioDoer.markerDesign." + engine;
        int maxPoint = -1;
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--maxPoint") && i+1 < args.length) maxPoint = Integer.parseInt(args[++i]);
        }
        Object obj = Class.forName(clsName).getDeclaredConstructor().newInstance();
        obj.getClass().getMethod("setInMarker", File.class).invoke(obj, new File(inMarker));
        if (maxPoint >= 0) {
            try { obj.getClass().getMethod("setMaxPoint", int.class).invoke(obj, maxPoint); }
            catch (NoSuchMethodException e) { /* engine doesn't have setMaxPoint */ }
        }
        Method process = obj.getClass().getMethod("process");

        // 重定向 System.err 捕获引擎结果输出
        PrintStream origErr = System.err;
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        PrintStream capture = new PrintStream(buf, true);
        String result;
        try {
            System.setErr(capture);
            result = (String) process.invoke(obj);
        } finally {
            System.setErr(origErr);
            capture.flush();
        }
        // 返回字符串为空 → 用捕获的 stderr 内容
        String content = (result == null || result.trim().isEmpty()) ? buf.toString() : result;
        java.io.FileWriter fw = new java.io.FileWriter(out);
        fw.write(content == null ? "" : content);
        fw.close();
        System.err.println("[tbplot] 已保存: " + out);
        System.exit(0);
    }
}
