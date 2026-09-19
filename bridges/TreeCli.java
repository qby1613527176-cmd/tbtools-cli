import biocjava.bioDoer.JIGplotToolkit.newickParser.TreeTreeTree.TreeTreeTree;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;
import java.util.ArrayList;

/**
 * tbplot tree — TBtools 树+注释图 CLI（08/29 重建）
 *
 * 用法: TreeCli <treeMeta.config> <out> [pad] [width] [height]
 *   treeMeta.config: 行导向配置（# 注释）:
 *     [TYPE]:Tree                # 树类型（必须）
 *     [NEWICK]:<newick 同行>      # Newick 树（与 [NEWICK]: 同行，允许含冒号）
 *     [setting]                  # 设置节（可选）
 *     [TYPE]:TextAnno/HeatMap/BarPlot/Tile/StackBar/Domain/GeneStructure/Motifs/ManualAssigned <file> ...
 *   pad: 面板间距（默认 20）
 *
 * 引擎: TreeTreeTree.showMeYourPower() 返回 ArrayList<JIGSubPanel>（各轨道）
 *       （GRAS 12sp 树 926 叶 + TextAnno + HeatMap 轨道验证 SVG 1.19MB，08/28）
 */
public class TreeCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: TreeCli <treeMeta.config> <out> [pad] [width] [height]");
            System.exit(1);
        }
        String configFile = args[0];
        String outFile = args[1];
        int pad = args.length > 2 ? Integer.parseInt(args[2]) : 20;
        int width = args.length > 3 ? Integer.parseInt(args[3]) : 1200;
        int height = args.length > 4 ? Integer.parseInt(args[4]) : 800;

        // FIX(G2): TreeTreeTree 在配置解析失败时会从 System.in 读入（挂起元凶，
        // WorkBuddy 报告「tree draw 挂起无响应」；本地复现：喂 .nwk 挂 30s+，
        // stdin 关死即立即返回）。两道防线：
        // ① 预检配置必须含 [TYPE]: 行，否则快速报错并指路 phylotree
        // ② System.in 置空流，引擎任何 stdin 读立即 EOF
        try {
            String content = new String(java.nio.file.Files.readAllBytes(new File(configFile).toPath()));
            if (!content.contains("[TYPE]:")) {
                System.err.println("❌ 输入不是 TreeTab 配置（缺 [TYPE]: 行）: " + configFile);
                System.err.println("   配置文件示例:");
                System.err.println("     [TYPE]:Tree");
                System.err.println("     [NEWICK]:((A:0.1,B:0.2):0.3,C:0.4);");
                System.err.println("   💡 如果只想直接画 newick 树: tbtools tree phylotree <in.nwk> <out.svg>");
                System.exit(2);
            }
        } catch (java.io.IOException ioe) {
            System.err.println("❌ 无法读取配置文件: " + configFile + " (" + ioe.getMessage() + ")");
            System.exit(2);
        }
        System.setIn(new java.io.ByteArrayInputStream(new byte[0]));

        TreeTreeTree ttt = new TreeTreeTree();
        ttt.setInConfig(new File(configFile));
        ttt.setScaleFactor(1.0);

        ArrayList<JIGSubPanel> panels = ttt.showMeYourPower();
        if (panels == null || panels.isEmpty()) {
            System.err.println("错误: showMeYourPower 返回空");
            System.exit(1);
        }
        System.err.println("[tbplot] 轨道面板数: " + panels.size());

        JIGBasePanel base = new JIGBasePanel(width, height);
        for (JIGSubPanel p : panels) base.addSubPanel(p);
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) base.save2PDF(new File(outFile));
        else base.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile + " (" + panels.size() + " 轨道)");
        System.exit(0);
    }
}