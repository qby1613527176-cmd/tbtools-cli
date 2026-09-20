import biocjava.bioDoer.FileUtils.FileUtils;
import biocjava.bioDoer.JIGplotToolkit.newickParser.PhyloTreeMan;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.HashSet;

/**
 * tbplot subtree — Newick 子树提取 CLI（GUI 逆向 #23，09/20）
 *
 * 用法: GetSubNewickTreeCli <tree.nwk> <idList.txt> <out.nwk> [--contain]
 *   tree.nwk:  完整 Newick 树
 *   idList:    要保留的叶节点 ID（每行一个）
 *   out.nwk:   提取出的子树
 *   --contain: 模糊匹配（ID 为叶名子串即保留；默认精确匹配）
 *
 * 引擎: PhyloTreeMan.getSubTree + nodeToNwk（GUI 逆向：GetSubNewickTreeGUIPanel $1
 *   StartButton 回调；GUI 的 quickPlotTree 预览部分已跳过）
 */
public class GetSubNewickTreeCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: GetSubNewickTreeCli <tree.nwk> <idList.txt> <out.nwk> [--contain]");
            System.exit(1);
        }
        File inTree = new File(args[0]);
        File idFile = new File(args[1]);
        File outFile = new File(args[2]);
        boolean contain = args.length > 3 && args[3].equals("--contain");
        if (!inTree.exists() || !idFile.exists()) {
            System.err.println("错误: 输入文件不存在");
            System.exit(2);
        }
        String newickString = FileUtils.fileToString(inTree);
        HashSet<String> keptNode = new HashSet<String>();
        BufferedReader br = new BufferedReader(new FileReader(idFile));
        String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (!line.isEmpty()) keptNode.add(line);
        }
        br.close();
        PhyloTreeMan ptm = new PhyloTreeMan();
        String subNwk = ptm.nodeToNwk(ptm.getSubTree(newickString, keptNode, contain));
        FileUtils.stringToFile(subNwk, outFile);
        System.err.println("[tbplot] 子树提取完成: " + outFile.getAbsolutePath() + "（保留 " + keptNode.size() + " 个 ID）");
        System.exit(0);
    }
}
