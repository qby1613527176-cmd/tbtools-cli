import biocjava.bioIO.HTSData.SAMBAM.Utils.BAMIndexCreater;

import java.io.File;

/**
 * tbcli bamindex — BAM 索引创建 CLI（08/31 第七十二波）
 *
 * 用法: BamIndexCli <in.sorted.bam> [out.bai]
 *   in.sorted.bam: 已排序 BAM
 *   out.bai:       输出 .bai（默认 <in>.bai）
 *
 * 引擎: BAMIndexCreater.setInSortedBamFile/setOutBaiFile + process()
 *   （main 硬编码演示 → setter+process）
 */
public class BamIndexCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("用法: BamIndexCli <in.sorted.bam> [out.bai]");
            System.exit(1);
        }
        String inBam = args[0];
        String outBai = args.length > 1 ? args[1] : inBam + ".bai";

        BAMIndexCreater bic = new BAMIndexCreater();
        bic.setInSortedBamFile(new File(inBam));
        bic.setOutBaiFile(new File(outBai));
        bic.process();
        System.err.println("[tbplot] 已保存: " + outBai);
        System.exit(0);
    }
}
