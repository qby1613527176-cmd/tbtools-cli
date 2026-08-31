import biocjava.bioIO.HTSData.SAMBAM.SamBamBINCov;

import java.io.File;

/**
 * tbcli sambamcov — BAM bin 覆盖统计 CLI（08/31 第七十一波）
 *
 * 用法: SamBamCovCli <in.bam> <out.tsv> [binSize] [countMode]
 *   binSize:   窗口大小 bp（默认 1000）
 *   countMode: Overlap|StartPos|EndPos（默认 Overlap）
 *
 * 引擎: SamBamBINCov.setInXamFile/setOutBINCovFile/setBINsize/setCountMode + process()
 *   （main 硬编码演示 → setter+process）
 */
public class SamBamCovCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: SamBamCovCli <in.bam> <out.tsv> [binSize] [countMode]");
            System.exit(1);
        }
        int binSize = args.length > 2 ? Integer.parseInt(args[2]) : 1000;
        String cm = args.length > 3 ? args[3] : "Overlap";

        SamBamBINCov sbbc = new SamBamBINCov();
        sbbc.setInXamFile(new File(args[0]));
        sbbc.setOutBINCovFile(new File(args[1]));
        sbbc.setBINsize(binSize);
        sbbc.setCountMode(SamBamBINCov.CountMode.valueOf(cm));
        sbbc.process();
        System.err.println("[tbplot] 已保存: " + args[1] + " (binSize=" + binSize + ", mode=" + cm + ")");
        System.exit(0);
    }
}
