import biocjava.bioDoer.BLAT.BlatExecutor;
import org.ucsc.blat.api.BlatRunResult;

import java.io.File;

/**
 * tbplot blat — BLAT 序列比对 CLI（GUI 逆向 #42，09/21）
 *
 * 用法: BlatExecutorCli <db.fa> <query.fa> <out> [--format blast9|psl|pslx|axt|maf|sim4|wublast|blast|blast8]
 *       [--minScore N] [--minIdentity 0.x] [--noHead] [--mode auto|dnadna|dnarna]
 *       [--tileSize N] [--stepSize N] [--maxGap N] [--maxIntron N] [--extra "opts"]
 *
 * 引擎: BlatExecutor（GUI 逆向：BlatGUIPanel runBlatInBackground；
 *   **org.ucsc.blat 纯 Java BLAT 实现内嵌 jar，无需外部二进制**；
 *   main() 无 ArgsParser → 桥）
 */
public class BlatExecutorCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: BlatExecutorCli <db.fa> <query.fa> <out> [--format blast9] [--minScore N] [--minIdentity 0.x] [--noHead] [--mode auto|dnadna|dnarna] [--tileSize N] [--stepSize N] [--maxGap N] [--maxIntron N] [--extra \"opts\"]");
            System.exit(1);
        }
        File dbFile = new File(args[0]);
        File queryFile = new File(args[1]);
        File outFile = new File(args[2]);
        BlatExecutor executor = new BlatExecutor();
        executor.setDatabaseFile(dbFile);
        executor.setQueryFile(queryFile);
        executor.setOutputFile(outFile);
        executor.setOutFormat("blast9");
        executor.setAutoDetectMode(true);
        StringBuilder extra = new StringBuilder();
        for (int i = 3; i < args.length; i++) {
            switch (args[i]) {
                case "--format": executor.setOutFormat(args[++i]); break;
                case "--minScore": executor.setMinScore(Integer.parseInt(args[++i])); break;
                case "--minIdentity": executor.setMinIdentity(Double.parseDouble(args[++i])); break;
                case "--noHead": executor.setNoHead(true); break;
                case "--mode":
                    String m = args[++i].toLowerCase();
                    if (m.equals("dnadna")) { executor.setAutoDetectMode(false); extra.append("-t=dna -q=dna "); }
                    else if (m.equals("dnarna")) { executor.setAutoDetectMode(false); extra.append("-t=dna -q=rna "); }
                    else executor.setAutoDetectMode(true);
                    break;
                case "--tileSize": executor.setTileSize(Integer.parseInt(args[++i])); break;
                case "--stepSize": executor.setStepSize(Integer.parseInt(args[++i])); break;
                case "--maxGap": executor.setMaxGap(Integer.parseInt(args[++i])); break;
                case "--maxIntron": executor.setMaxIntron(Integer.parseInt(args[++i])); break;
                case "--extra": extra.append(args[++i]); break;
                default:
                    System.err.println("警告: 忽略未知参数 " + args[i]);
            }
        }
        if (!dbFile.exists() || !queryFile.exists()) {
            System.err.println("错误: 输入文件不存在");
            System.exit(2);
        }
        if (extra.length() > 0) {
            executor.setExtraOptionsRaw(extra.toString().trim());
        }
        BlatRunResult result = executor.run();
        System.err.println("[tbplot] BLAT 比对完成: " + outFile.getAbsolutePath()
                + (result != null ? "（" + result + "）" : ""));
        System.exit(0);
    }
}
