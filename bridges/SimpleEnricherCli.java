/**
 * tbplot sricher — 简单富集分析 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: SimpleEnricherCli <in.tsv> <out.xls> <totalAnnoIdx> <totalHitIdx> <selAnnoIdx> <selHitIdx>
 *        [--header] [--sample-id-col N]
 *
 * 接口来源：反编译 SimpleEnricherGUIPanel（GUI 真实调用链）：
 *   SimpleEnricher se = new SimpleEnricher();
 *   se.setTotalAnnoCountIndex(i); se.setTotalHitCountIndex(j);
 *   se.setSelectedAnnoCountIndex(k); se.setSelectedHitCountIndex(l);
 *   se.setHeader(bool); se.setInTable(file); se.setOutTable(file); se.process();
 *
 * 输入表要求：每行一个条目，含 4 个计数列（列索引 0-based）：
 *   [.., 总注释数, 总命中数, 选择集注释数, 选择集命中数, ..]
 * 引擎对每行做超几何/Fisher 富集，输出 P 值（富集显著性排序）。
 * 这是 goEnrich 的轻量版——无需 OBO，直接喂计数表。
 */
public class SimpleEnricherCli {
    public static void main(String[] args) throws Exception {
        boolean header = false;
        java.util.ArrayList<String> pos = new java.util.ArrayList<String>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--header")) header = true;
            else pos.add(args[i]);
        }
        if (pos.size() < 6) {
            System.err.println("用法: SimpleEnricherCli <in.tsv> <out.xls> <totalAnnoIdx> <totalHitIdx> <selAnnoIdx> <selHitIdx> [--header]");
            System.exit(1);
        }
        Object se = Class.forName("biocjava.bioIO.GeneOntology.EnrichMent.SimpleEnricher")
                .getDeclaredConstructor().newInstance();
        Class<?> c = se.getClass();
        c.getMethod("setInTable", java.io.File.class).invoke(se, new java.io.File(pos.get(0)));
        c.getMethod("setOutTable", java.io.File.class).invoke(se, new java.io.File(pos.get(1)));
        c.getMethod("setTotalAnnoCountIndex", int.class).invoke(se, Integer.parseInt(pos.get(2)));
        c.getMethod("setTotalHitCountIndex", int.class).invoke(se, Integer.parseInt(pos.get(3)));
        c.getMethod("setSelectedAnnoCountIndex", int.class).invoke(se, Integer.parseInt(pos.get(4)));
        c.getMethod("setSelectedHitCountIndex", int.class).invoke(se, Integer.parseInt(pos.get(5)));
        c.getMethod("setHeader", boolean.class).invoke(se, header);
        c.getMethod("process").invoke(se);
        System.err.println("[tbplot] 已保存: " + pos.get(1));
        System.exit(0);
    }
}