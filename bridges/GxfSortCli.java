import biocjava.bioDoer.GXFUtils.GXFfixer.GXFSort;

import java.io.File;

/**
 * tbcli gxfsort — GFF 按坐标排序 CLI（08/31 第八十五波，工具 95）
 *
 * 用法: GxfSortCli <in.gff3|gtf> <out.sorted>
 *   in/out: 注释文件（按染色体+坐标排序，注释预处理刚需）
 *
 * 引擎: GXFSort.sortByPretty(File, File)（main 硬编码演示 → 实例方法直接调）
 */
public class GxfSortCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: GxfSortCli <in.gff3|gtf> <out.sorted>");
            System.exit(1);
        }
        new GXFSort().sortByPretty(new File(args[0]), new File(args[1]));
        System.err.println("[tbplot] 已保存: " + args[1]);
        System.exit(0);
    }
}