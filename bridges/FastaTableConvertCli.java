import biocjava.bioDoer.Fasta.Tools.FastaTable;

import java.io.File;

/**
 * tbplot fa2tab / tab2fa — FASTA↔表格互转 CLI（GUI 逆向 #26，09/20）
 *
 * 用法: FastaTableConvertCli <fa2tab|tab2fa> <in> <out>
 *   fa2tab: FASTA → 表格（ID\t序列）
 *   tab2fa: 表格 → FASTA
 *
 * 引擎: FastaTable 双向静态方法（GUI 逆向：Fasta2TableGUIPanel $3
 *   fasta2tabRadioButton/tab2fastaRadioButton 单选，main() 无 ArgsParser）
 */
public class FastaTableConvertCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: FastaTableConvertCli <fa2tab|tab2fa> <in> <out>");
            System.exit(1);
        }
        String mode = args[0];
        File inFile = new File(args[1]);
        File outFile = new File(args[2]);
        if (!inFile.exists()) {
            System.err.println("错误: 输入文件不存在: " + inFile.getAbsolutePath());
            System.exit(2);
        }
        switch (mode) {
            case "fa2tab": FastaTable.fa2tab(inFile, outFile); break;
            case "tab2fa": FastaTable.tab2fa(inFile, outFile); break;
            default:
                System.err.println("错误: 未知模式 " + mode + "（可选 fa2tab|tab2fa）");
                System.exit(1);
        }
        System.err.println("[tbplot] FASTA↔表转换完成(" + mode + "): " + outFile.getAbsolutePath());
        System.exit(0);
    }
}
