import biocjava.bioIO.SRAtools.GetENALinksOfSRR;

import java.io.File;

/**
 * tbplot srr2ena — SRR→ENA 下载链接解析 CLI（GUI 逆向 #39，09/21）
 *
 * 用法: GetENALinksCli <srrList.txt> <out.xls>
 *   srrList: 每行一个 SRR/ERR/DRR 号（# 开头注释跳过）
 *   out:     ENA filereport TSV（study/sample/run accession + tax_id +
 *            scientific_name + instrument + layout + fastq_ftp/aspera 等 17 字段）
 *
 * 引擎: GetENALinksOfSRR（GUI 逆向：SRR2ENALinksGUIPanel $1 StartButton 回调
 *   → setInSRRlistFile/setOutENAinfoFile/process；⚠️ 联网 ENA portal API，
 *   引擎自带 0~3s 随机限速）
 */
public class GetENALinksCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: GetENALinksCli <srrList.txt> <out.xls>");
            System.exit(1);
        }
        File inList = new File(args[0]);
        File outFile = new File(args[1]);
        if (!inList.exists()) {
            System.err.println("错误: 输入文件不存在: " + inList.getAbsolutePath());
            System.exit(2);
        }
        GetENALinksOfSRR gels = new GetENALinksOfSRR();
        gels.setInSRRlistFile(inList);
        gels.setOutENAinfoFile(outFile);
        gels.process();
        System.err.println("[tbplot] ENA 链接解析完成: " + outFile.getAbsolutePath());
        System.exit(0);
    }
}
