import biocjava.bioDoer.JJplot2Toolkit.BuildDegramdomFromTable;

import java.io.File;

/**
 * tbcli degramdom — 亲子表构建 Newick 树 CLI（08/31 第七十波）
 *
 * 用法: DegramdomCli <in.tsv> [out.nwk]
 *   in.tsv: 子节点\t父节点\t枝长（每行一个父子关系；表头/空行自动跳过）
 *   out.nwk: 输出 Newick（可选，默认打印到 stdout）
 *
 * 引擎: BuildDegramdomFromTable.process() 返回 Newick 字符串（main 硬编码演示 → setter+process）
 */
public class DegramdomCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("用法: DegramdomCli <in.tsv> [out.nwk]");
            System.exit(1);
        }
        BuildDegramdomFromTable bdf = new BuildDegramdomFromTable();
        bdf.setInTable(new File(args[0]));
        String tree = bdf.process();
        if (args.length > 1) {
            java.io.FileWriter fw = new java.io.FileWriter(new File(args[1]));
            fw.write(tree);
            fw.close();
            System.err.println("[tbplot] 已保存: " + args[1]);
        } else {
            System.out.println(tree);
        }
        System.exit(0);
    }
}
