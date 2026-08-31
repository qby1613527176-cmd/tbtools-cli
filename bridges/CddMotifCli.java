import biocjava.bioDoer.MEME.DrawMotifPattern.DrawMotifPatternFromCDDResult;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;

/**
 * tbcli cddmotif — CDD 保守域模式图 CLI（08/31 第七十九波，引擎 121）
 *
 * 用法: CddMotifCli <cdd.hitdata.txt> <in.fasta> <out.svg|png|pdf> [newick.treefile]
 *   cdd.hitdata.txt: NCBI Batch CD-search hitsConcise 结果（# 注释头 + Query/Hit type/PSSM-ID/From/To/... 表）
 *   in.fasta:       蛋白序列（ID 与 hitdata 的 Query 一致）
 *   newick.treefile: 可选进化树（排序基因）
 *
 * 引擎: DrawMotifPatternFromCDDResult.setInFile/setInFasta + postGraph(newick, jigPanel) → JIGSubPanel
 *   （论文级 CDD 保守域模式图；GRAS 真实 hitdata.txt 验证）
 */
public class CddMotifCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: CddMotifCli <cdd.hitdata.txt> <in.fasta> <out.svg|png|pdf> [newick.treefile]");
            System.exit(1);
        }
        String newick = "";
        if (args.length > 3) {
            File tf = new File(args[3]);
            if (tf.exists()) newick = new String(java.nio.file.Files.readAllBytes(tf.toPath()), "UTF-8").trim();
        }

        DrawMotifPatternFromCDDResult dmp = new DrawMotifPatternFromCDDResult();
        dmp.setInFile(new File(args[0]));
        dmp.setInFasta(new File(args[1]));

        JIGBasePanel jigPanel = new JIGBasePanel(1200, 1000);
        JIGSubPanel sp = dmp.postGraph(newick, jigPanel);
        jigPanel.addSubPanel(sp);

        String out = args[2];
        String low = out.toLowerCase();
        if (low.endsWith(".png")) jigPanel.save2PNG(new File(out));
        else if (low.endsWith(".pdf")) jigPanel.save2PDF(new File(out));
        else jigPanel.save2SVG(new File(out));
        System.err.println("[tbplot] 已保存: " + out);
        System.exit(0);
    }
}
