import biocjava.bioDoer.bar_plotter;

/**
 * tbcli barplotter 桥 — 合成共线性柱状图 CLI（08/31 第六十六波）
 *
 * 用法: BarPlotterCli -g <gff> -s <synteny> -c <ctl> -o <out.png>
 *   gff: chr\tgene\tend（简化 GFF）
 *   synteny: MCScanX 式 collinearity（# Alignment 分段，行=基因1\t基因2\t...）
 *   ctl: 4 行 = xdim / ydim / xchr列表(逗号分隔) / ychr列表(逗号分隔)
 *
 * ⚠️ bar_plotter.main 是死代码（打印 -4）→ 真入口是 main1（main1≠main 规律）
 */
public class BarPlotterCli {
    public static void main(String[] args) {
        bar_plotter.main1(args);
        System.exit(0);
    }
}
