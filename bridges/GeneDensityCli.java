/**
 * tbplot gdensity — 基因密度分析 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: GeneDensityCli <in.gff3> <out.geneRecords.bed> <binSize> [--feature <tag>] [--chrlen <file>]
 *
 * 接口来源：反编译 GeneDensityProfilerGUIPanel（GUI 真实调用链）：
 *   GeneDensityProfiler gdpf = new GeneDensityProfiler();
 *   gdpf.setBinSize(N); setInGXF(gff); [setDefinedFeatureTag] [setChrLengthFile]
 *   gdpf.setOutGeneRecordFile(out); gdpf.process();
 * 纯逻辑无 GUI。产物：基因记录（按 bin 划分），供染色体基因密度分布图。
 */
public class GeneDensityCli {
    public static void main(String[] args) throws Exception {
        String feature = "";
        String chrlen = "";
        java.util.ArrayList<String> pos = new java.util.ArrayList<String>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--feature") && i+1 < args.length) feature = args[++i];
            else if (args[i].equals("--chrlen") && i+1 < args.length) chrlen = args[++i];
            else pos.add(args[i]);
        }
        if (pos.size() < 3) {
            System.err.println("用法: GeneDensityCli <in.gff3> <out.geneRecords> <binSize> [--feature <tag>] [--chrlen <file>]");
            System.exit(1);
        }
        Object gd = Class.forName("biocjava.bioDoer.GXFUtils.GeneDensityProfiler")
                .getDeclaredConstructor().newInstance();
        Class<?> c = gd.getClass();
        c.getMethod("setInGXF", java.io.File.class).invoke(gd, new java.io.File(pos.get(0)));
        c.getMethod("setOutGeneRecordFile", java.io.File.class).invoke(gd, new java.io.File(pos.get(1)));
        c.getMethod("setBinSize", int.class).invoke(gd, Integer.parseInt(pos.get(2)));
        if (!feature.isEmpty()) c.getMethod("setDefinedFeatureTag", String.class).invoke(gd, feature);
        if (!chrlen.isEmpty()) c.getMethod("setChrLengthFile", java.io.File.class).invoke(gd, new java.io.File(chrlen));
        c.getMethod("process").invoke(gd);
        System.err.println("[tbplot] 已保存: " + pos.get(1));
        System.exit(0);
    }
}