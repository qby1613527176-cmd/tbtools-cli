import biocjava.bioIO.HTSData.SAMBAM.Utils.SAMBAMSorter;
import htsjdk.samtools.SAMFileHeader;

import java.io.File;

/**
 * tbcli bamsort — BAM 排序 CLI（08/31 第七十二波）
 *
 * 用法: BamSortCli <in.bam> <out.bam> [sortOrder] [tmpDir]
 *   sortOrder: coordinate|queryname|unsorted|duplicate（默认 coordinate）
 *   tmpDir:    临时目录（默认系统临时）
 *
 * 引擎: SAMBAMSorter.setInFile/setOutFile/setSo/setTmpDir + process()
 *   （main 硬编码演示 → setter+process）
 */
public class BamSortCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: BamSortCli <in.bam> <out.bam> [sortOrder] [tmpDir]");
            System.exit(1);
        }
        String soStr = args.length > 2 ? args[2] : "coordinate";
        String tmpDir = args.length > 3 ? args[3] : null;

        SAMFileHeader.SortOrder so;
        switch (soStr.toLowerCase()) {
            case "coordinate": so = SAMFileHeader.SortOrder.coordinate; break;
            case "queryname": so = SAMFileHeader.SortOrder.queryname; break;
            case "unsorted": so = SAMFileHeader.SortOrder.unsorted; break;
            case "duplicate": so = SAMFileHeader.SortOrder.duplicate; break;
            default: so = SAMFileHeader.SortOrder.coordinate; break;
        }

        SAMBAMSorter sbs = new SAMBAMSorter();
        sbs.setInFile(new File(args[0]));
        sbs.setOutFile(new File(args[1]));
        sbs.setSo(so);
        if (tmpDir != null) sbs.setTmpDir(new File(tmpDir));
        sbs.process();
        System.err.println("[tbplot] 已保存: " + args[1] + " (sort=" + soStr + ")");
        System.exit(0);
    }
}
