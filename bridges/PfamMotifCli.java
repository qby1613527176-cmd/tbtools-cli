import biocjava.bioDoer.MEME.DrawMotifPattern.DrawMotifPatternFromPfamResult;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;

/**
 * tbcli pfammotif — Pfam 保守域模式图 CLI（08/31 第八十一波，引擎 123）
 *
 * 用法: PfamMotifCli <pfamscan.txt> <in.fasta> <out.svg|png|pdf> [newick.treefile]
 *   pfamscan.txt: PfamScan/pfam_scan.pl 16 列输出（seqid alnStart alnEnd envStart envEnd hmmAcc hmmName type hmmStart hmmEnd hmmLen bitscore evalue ...）
 *   in.fasta:     蛋白序列（ID 与 pfamscan 一致）
 *   newick.treefile: 可选进化树
 *
 * 引擎: DrawMotifPatternFromPfamResult.setInFile/setInFasta + postGraph(newick, jigPanel) → JIGSubPanel
 *   （⚠️ 委托 PfamDomainHitsTableParser，期望 PfamScan 16/15 列；可用 hmmscan --domtblout 转换）
 */
public class PfamMotifCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: PfamMotifCli <pfamscan.txt> <in.fasta> <out.svg|png|pdf> [newick.treefile]");
            System.exit(1);
        }
        String newick = "";
        if (args.length > 3) {
            File tf = new File(args[3]);
            if (tf.exists()) newick = new String(java.nio.file.Files.readAllBytes(tf.toPath()), "UTF-8").trim();
        }
        DrawMotifPatternFromPfamResult dmp = new DrawMotifPatternFromPfamResult();
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
