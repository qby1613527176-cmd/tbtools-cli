import java.io.File;
import java.nio.file.Files;
import java.nio.charset.StandardCharsets;

/**
 * tbplot treeRooting — MAD 系统发育定根 CLI（08/29，第 49 引擎）
 *
 * 用法: TreeRootingCli <in.nwk> <out.nwk>
 *   in.nwk: 未定根 NEWICK 树（单树）
 *   out.nwk: MAD 定根后的 NEWICK 树
 *
 * ⚠️ MAD.main() 硬编码输入路径（args 被覆盖）——不能直接调 main。
 *    改用公开静态入口 quickMadRoot(String)：NEWICK 字符串 → 定根后字符串。
 *    算法引用：Tria et al. 2017, Nat Ecol Evol (MAD rooting, DOI:10.1038/s41559-017-0193)
 */
public class TreeRootingCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: TreeRootingCli <in.nwk> <out.nwk>");
            System.exit(1);
        }
        String in = args[0];
        String out = args[1];
        String nwk = new String(Files.readAllBytes(new File(in).toPath()), StandardCharsets.UTF_8).trim();
        String rooted = biocjava.bioDoer.TreeRooting.MAD.quickMadRoot(nwk);
        Files.write(new File(out).toPath(), (rooted + "\n").getBytes(StandardCharsets.UTF_8));
        System.err.println("[tbplot] MAD 定根完成: " + out);
        System.exit(0);
    }
}
