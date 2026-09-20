import biocjava.bioDoer.NGSDataAnalysis.SequencingDataRecommand.AssemblyGenomeDataSizeRecommand;
import biocjava.bioDoer.NGSDataAnalysis.SequencingDataRecommand.AssemblyGenomeDataSizeRecommand.AssemblyObject;
import biocjava.bioDoer.NGSDataAnalysis.SequencingDataRecommand.RecommendSize;

/**
 * tbplot seqrecommend — 基因组组装测序量推荐 CLI（GUI 逆向 #43，09/21）
 *
 * 用法: AssemblyRecommandCli <genomeSize1n_bp> [--polyploid] [--het 0.01] [--level Minimum|Draft|Haplotyped_Resolved|Haplotyped_T2T]
 *   genomeSize1n_bp: 1n 基因组大小（bp，如 400000000）
 *   --polyploid: 多倍体
 *   --het:       杂合率（如 0.01 = 1%）
 *   --level:     组装目标（默认 Draft）
 *
 * 引擎: AssemblyGenomeDataSizeRecommand（GUI 逆向：AssemblyGenomeDataSizeRecommandGUIPanel $2
 *   → process(size, polyploid, het, object) → RecommendSize.getReportString()；纯计算离线）
 */
public class AssemblyRecommandCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("用法: AssemblyRecommandCli <genomeSize1n_bp> [--polyploid] [--het 0.01] [--level Minimum|Draft|Haplotyped_Resolved|Haplotyped_T2T]");
            System.exit(1);
        }
        double genomeSize1n = Double.parseDouble(args[0]);
        boolean isPolyPoid = false;
        double het = 0.01;
        AssemblyObject obj = AssemblyObject.Draft;
        for (int i = 1; i < args.length; i++) {
            switch (args[i]) {
                case "--polyploid": isPolyPoid = true; break;
                case "--het": het = Double.parseDouble(args[++i]); break;
                case "--level":
                    String lv = args[++i];
                    if (lv.equalsIgnoreCase("Minimum") || lv.equalsIgnoreCase("Mininum")) obj = AssemblyObject.Mininum;
                    else if (lv.equalsIgnoreCase("Haplotyped_Resolved")) obj = AssemblyObject.Haplotyped_Resolved;
                    else if (lv.equalsIgnoreCase("Haplotyped_T2T")) obj = AssemblyObject.Haplotyped_T2T;
                    else obj = AssemblyObject.Draft;
                    break;
                default:
                    System.err.println("警告: 忽略未知参数 " + args[i]);
            }
        }
        AssemblyGenomeDataSizeRecommand agdsr = new AssemblyGenomeDataSizeRecommand();
        RecommendSize rs = agdsr.process(genomeSize1n, isPolyPoid, het, obj);
        System.out.println(rs.getReportString());
        System.exit(0);
    }
}
