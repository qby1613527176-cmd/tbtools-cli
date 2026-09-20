/**
 * tbplot golevel — GO 层级统计 + 层级柱状图 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: GoLevelCli <go.obo> <gene2go.tsv> <outPrefix> [--level N] [--graph] [--width W] [--height H]
 *   go.obo:     GO 本体数据库
 *   gene2go.tsv: 基因→GO 注释（geneID\tGO:x,GO:y）
 *   outPrefix:   输出前缀
 *   --level:     GO 层级（默认 2，1-23）
 *   --graph:     同时画层级柱状图（默认只出统计表）
 *
 * 接口来源：反编译 LevelGounterGUIPanel（GUI 真实调用链）：
 *   LevelCounter llg = new LevelCounter();
 *   llg.setGOdb(oboFilePath).setGene2GoFile(query2GoFilePath).init();
 *   llg.writeGo2GenesFileAtLevel(level, outTable);      // 统计表 .Level2.count.xls
 *   LevelGrapher lg = new LevelGrapher(outTable, outSVG); // 直接写 SVG（无 GUI 弹窗）
 *   lg.setGraphWidth(W); lg.setGraphHeight(H); lg.makeLevelGraph();
 */
public class GoLevelCli {
    public static void main(String[] args) throws Exception {
        int level = 2;
        boolean graph = false;
        String width = "800", height = "600";
        java.util.ArrayList<String> pos = new java.util.ArrayList<String>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--level") && i+1 < args.length) level = Integer.parseInt(args[++i]);
            else if (args[i].equals("--graph")) graph = true;
            else if (args[i].equals("--width") && i+1 < args.length) width = args[++i];
            else if (args[i].equals("--height") && i+1 < args.length) height = args[++i];
            else pos.add(args[i]);
        }
        if (pos.size() < 3) {
            System.err.println("用法: GoLevelCli <go.obo> <gene2go.tsv> <outPrefix> [--level N] [--graph] [--width W] [--height H]");
            System.exit(1);
        }
        String obo = pos.get(0), gene2go = pos.get(1), outPrefix = pos.get(2);
        String outTable = outPrefix + ".Level" + level + ".count.xls";

        Object lc = Class.forName("biocjava.bioDoer.GeneOntology.Grapher.LevelCounter")
                .getDeclaredConstructor().newInstance();
        Class<?> c = lc.getClass();
        c.getMethod("setGOdb", java.io.File.class).invoke(lc, new java.io.File(obo));
        c.getMethod("setGene2GoFile", java.io.File.class).invoke(lc, new java.io.File(gene2go));
        c.getMethod("init").invoke(lc);
        c.getMethod("writeGo2GenesFileAtLevel", int.class, String.class).invoke(lc, level, outTable);
        System.err.println("[tbplot] GO 层级统计表: " + outTable);

        if (graph) {
            String outSVG = outTable + ".svg";
            Object lg = Class.forName("biocjava.bioDoer.GeneOntology.Grapher.LevelGrapher")
                    .getConstructor(String.class, String.class).newInstance(outTable, outSVG);
            Class<?> gl = lg.getClass();
            gl.getMethod("setGraphWidth", String.class).invoke(lg, width);
            gl.getMethod("setGraphHeight", String.class).invoke(lg, height);
            gl.getMethod("makeLevelGraph").invoke(lg);
            System.err.println("[tbplot] GO 层级图: " + outSVG);
        }
        System.exit(0);
    }
}