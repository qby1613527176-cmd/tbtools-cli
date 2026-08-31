import biocjava.bioDoer.FileUtils.FileLineSplit;
import java.io.File;
/**
 * tbcli filesplit — 文件按份数分割 CLI（工具 99）
 * 用法: FileSplitCli <inFile> <numParts>
 * 引擎: FileLineSplit.Split(File, int) 静态方法
 */
public class FileSplitCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) { System.err.println("用法: FileSplitCli <inFile> <numParts>"); System.exit(1); }
        File[] parts = FileLineSplit.Split(new File(args[0]), Integer.parseInt(args[1]));
        for (File p : parts) System.err.println("[tbplot] 生成: " + p.getAbsolutePath());
        System.exit(0);
    }
}
