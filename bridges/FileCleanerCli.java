import biocjava.bioDoer.FileCleaner;

import java.io.File;

/**
 * tbplot clearchar — 文件非法字符清理 CLI（GUI 逆向 #34，09/20）
 *
 * 用法: FileCleanerCli <in.txt> <out.txt>
 *   in:  任意文本文件
 *   out: 清理后文件（非可打印 ASCII/非 tab 字符替换为 _；空白行跳过）
 *
 * 引擎: FileCleaner.simplifyFile（GUI 逆向：InvalidCharCleanerGUIPanel $3；
 *   逐行扫描，保留 tab 与 0x20~0x7E，其余→_，非法字符逐行报告 stderr）
 */
public class FileCleanerCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: FileCleanerCli <in.txt> <out.txt>");
            System.exit(1);
        }
        File inFile = new File(args[0]);
        File outFile = new File(args[1]);
        if (!inFile.exists()) {
            System.err.println("错误: 输入文件不存在: " + inFile.getAbsolutePath());
            System.exit(2);
        }
        FileCleaner.simplifyFile(inFile, outFile);
        System.err.println("[tbplot] 清理完成: " + outFile.getAbsolutePath());
        System.exit(0);
    }
}
