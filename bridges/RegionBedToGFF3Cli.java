import biocjava.bioDoer.GXFUtils.RegionBedToGFF3;

import java.io.File;

/**
 * tbplot bed2gff3 — exon BED → GFF3 转换 CLI（GUI 逆向 #21，09/20）
 *
 * 用法: RegionBedToGFF3Cli <in.bed> <out.gff3> [genome.fa]
 *   in:    BED 文件（染色体 起始 结束 ID:链向:编码）
 *          ⚠️ 第 4 列必须是 ID:strand:coding 格式，如 G01:+:C（coding=C 编码/N 非编码；
 *          同 ID 多行会按坐标排序合并出 mRNA+exon 层级，start 自动 +1 转 1-based）
 *   out:   GFF3（自动补 .gff3 后缀）
 *   genome.fa: 可选基因组（存在则做 ORF 相关注释）
 *
 * 引擎: RegionBedToGFF3（GUI 逆向：ExonBedToGFF3GUIPanel $4 StartButton 回调
 *   → setInBedFile/setOutGff3/[setInGenomeFile]/process，main() 无 ArgsParser）
 */
public class RegionBedToGFF3Cli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: RegionBedToGFF3Cli <in.bed> <out.gff3> [genome.fa]");
            System.exit(1);
        }
        File inBed = new File(args[0]);
        File outGff3 = new File(args[1]);
        if (!outGff3.getName().toLowerCase().endsWith(".gff3")) {
            outGff3 = new File(outGff3.getAbsolutePath() + ".gff3");
        }
        if (!inBed.exists()) {
            System.err.println("错误: 输入 BED 不存在: " + inBed.getAbsolutePath());
            System.exit(2);
        }
        RegionBedToGFF3 rbtg = new RegionBedToGFF3();
        rbtg.setInBedFile(inBed);
        rbtg.setOutGff3(outGff3);
        if (args.length > 2 && new File(args[2]).exists()) {
            rbtg.setInGenomeFile(new File(args[2]));
        }
        rbtg.process();
        System.err.println("[tbplot] BED→GFF3 完成: " + outGff3.getAbsolutePath());
        System.exit(0);
    }
}
