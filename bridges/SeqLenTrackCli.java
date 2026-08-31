import biocjava.bioDoer.MEME.DrawMotifPattern.DrawSequenceFromSeqLenInfo;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;

/**
 * tbcli seqlentrack — 序列长度骨架图 CLI（08/31 第八十波，引擎 122）
 *
 * 用法: SeqLenTrackCli <seqlen.txt> <out.svg|png|pdf> [newick.treefile]
 *   seqlen.txt: gene\tlength（每行一个基因；# 开头跳过）
 *   newick.treefile: 可选进化树（排序基因）
 *
 * 引擎: DrawSequenceFromSeqLenInfo（继承 DrawMotifPatternFromMEMEResult.postGraph(newick, panel)）
 *   （AmazingMetaPlot 的 CDD 面板底层——基因长度骨架图）
 */
public class SeqLenTrackCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: SeqLenTrackCli <seqlen.txt> <out.svg|png|pdf> [newick.treefile]");
            System.exit(1);
        }
        String newick = "";
        if (args.length > 2) {
            File tf = new File(args[2]);
            if (tf.exists()) newick = new String(java.nio.file.Files.readAllBytes(tf.toPath()), "UTF-8").trim();
        }
        DrawSequenceFromSeqLenInfo dmp = new DrawSequenceFromSeqLenInfo();
        dmp.setInFile(new File(args[0]));
        JIGBasePanel jigPanel = new JIGBasePanel(1200, 800);
        JIGSubPanel sp = dmp.postGraph(newick, jigPanel);
        jigPanel.addSubPanel(sp);
        String out = args[1];
        String low = out.toLowerCase();
        if (low.endsWith(".png")) jigPanel.save2PNG(new File(out));
        else if (low.endsWith(".pdf")) jigPanel.save2PDF(new File(out));
        else jigPanel.save2SVG(new File(out));
        System.err.println("[tbplot] 已保存: " + out);
        System.exit(0);
    }
}
