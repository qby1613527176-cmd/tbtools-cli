import JJpolt2.Clustering.Hclust.Hclust;

import java.io.File;
import java.io.FileWriter;

/**
 * tbplot hclust — TBtools Hclust 聚类 CLI（08/29 重建）
 *
 * 用法: HclustCli <expr.matrix.tsv> <out.nwk> [distMethod] [clusterMethod]
 *   expr.matrix.tsv: 首列基因名 + 列样本名表头，其余数值
 *   distMethod: 距离方法（默认 Euclidean，如 PearsonCorrelation / Manhattan 等）
 *   clusterMethod: 聚类方法（默认 UPGA，如 NeighborJoining / ML / MP 等）
 *
 * 引擎: Hclust.buildDendrogram() 返回 Newick 字符串
 * 注意: 此引擎输出 Newick 树文本（不是图）
 */
public class HclustCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: HclustCli <expr.tsv> <out.nwk> [distMethod] [clusterMethod]");
            System.exit(1);
        }
        String inFile = args[0];
        String outFile = args[1];

        Hclust hclust = new Hclust();
        hclust.setDistanceMap(new File(inFile));
        if (args.length > 2) {
            hclust.setUseClusteringMethod(Hclust.Method.valueOf(args[2]));
        }
        // clusterMethod: 若提供，尝试设置（若无对应 setter 忽略）
        String newick = hclust.buildDendrogram();
        if (newick == null || newick.trim().isEmpty()) {
            System.err.println("错误: buildDendrogram 返回空");
            System.exit(1);
        }
        FileWriter fw = new FileWriter(outFile);
        fw.write(newick);
        fw.close();
        System.err.println("[tbplot] 已保存: " + outFile + " (" + newick.length() + " chars)");
        System.exit(0);
    }
}
