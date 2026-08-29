import biocjava.bioDoer.JIGplotToolkit.BlastVisulization.ncbiPileUpPlot;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;
import biocjava.bioIO.BlastXml.BlastXmlReader;
import biocjava.bioIO.BlastXml.Iteration;
import java.io.File;

/**
 * tbplot pileup — TBtools BLAST pile-up 可视化 CLI（08/29，第 44 引擎）
 *
 * 用法: PileUpCli <blast.xml> <out.svg> [--query NAME]
 *   blast.xml: BLAST XML 输出（BLAST+ -outfmt 5）
 *   --query: 指定 query（缺省自动选第一个）
 *
 * 引擎: ncbiPileUpPlot.showIteration(Iteration)（绕过 GUI 弹窗，自动选 query）
 */
public class PileUpCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: PileUpCli <blast.xml> <out.svg> [--query NAME]");
            System.exit(1);
        }
        String xmlFile = args[0], out = args[1];
        String queryName = null;
        for (int i = 2; i < args.length; i++) {
            if (args[i].equals("--query") && i+1 < args.length) queryName = args[++i];
        }
        // 读 BLAST XML，取指定/第一个 query
        BlastXmlReader bxr = new BlastXmlReader();
        bxr.setTargetFile(new File(xmlFile));
        Iteration target = null;
        while (bxr.hasNext()) {
            Iteration iter = bxr.getNextIteration();
            if (queryName == null || iter.getQueryDef().equals(queryName)) {
                target = iter;
                break;
            }
        }
        bxr.close();
        if (target == null) {
            System.err.println("错误: 未找到 query" + (queryName != null ? " " + queryName : ""));
            System.exit(1);
        }
        System.err.println("绘图 query: " + target.getQueryDef() + " len=" + target.getQueryLen());
        JIGSubPanel panel = ncbiPileUpPlot.showIteration(target);
        JIGBasePanel base = new JIGBasePanel(900, 600);
        base.addSubPanel(panel);
        String low = out.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(new File(out));
        else if (low.endsWith(".pdf")) base.save2PDF(new File(out));
        else base.save2SVG(new File(out));
        System.err.println("[tbplot] 已保存: " + out);
        System.exit(0);
    }
}
