import java.io.File;
import java.lang.reflect.Method;

/**
 * tbplot marker — TBtools 标记设计工具 CLI（08/29，第 46-48 引擎）
 *
 * 用法: MarkerDesignCli <engineClass> <inMarker> <out.txt> [--maxPoint N]
 *   engineClass: MarkerDist|MarkerFilter|SampleDist（biocjava.bioDoer.markerDesign 下）
 *   inMarker: 标记 0-1 矩阵（tab 分隔）
 *   --maxPoint: MarkerDist 专用（最大点数）
 *   引擎: setInMarker + process() 返回 String（分析结果）
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
        String result = (String) process.invoke(obj);
        java.io.FileWriter fw = new java.io.FileWriter(out);
        fw.write(result == null ? "" : result);
        fw.close();
        System.err.println("[tbplot] 已保存: " + out);
        System.exit(0);
    }
}
