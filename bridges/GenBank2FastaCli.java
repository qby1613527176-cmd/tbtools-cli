import biocjava.bioIO.GBff.genBank2Fasta;

import java.io.File;

/**
 * tbplot gb2fa — GenBank→FASTA 转换 CLI（GUI 逆向 #36，09/20）
 *
 * 用法: GenBank2FastaCli <in.gb> <out.fa>
 *
 * 引擎: genBank2Fasta（GUI 逆向：GenBank2FastaGUIPanel $3
 *   → setInGenBankFile/setOutFastaFile/process，main() 空实现）
 */
public class GenBank2FastaCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: GenBank2FastaCli <in.gb> <out.fa>");
            System.exit(1);
        }
        File inGb = new File(args[0]);
        File outFa = new File(args[1]);
        if (!inGb.exists()) {
            System.err.println("错误: 输入文件不存在: " + inGb.getAbsolutePath());
            System.exit(2);
        }
        genBank2Fasta gb2f = new genBank2Fasta();
        gb2f.setInGenBankFile(inGb);
        gb2f.setOutFastaFile(outFa);
        gb2f.process();
        System.err.println("[tbplot] GenBank→FASTA 完成: " + outFa.getAbsolutePath());
        System.exit(0);
    }
}
