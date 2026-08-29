import java.io.File;

/**
 * tbplot ctgGroup — miniprot 等位基因 contig 分组 CLI（08/29，第 72 引擎）
 *
 * 用法: CtgGroupCli <in.miniprot.gff> <polyPoid> <outContigGrpMap>
 *   in.miniprot.gff: miniprot --gff 输出（蛋白→contigs）
 *   polyPoid: 目标倍性；outContigGrpMap: contig → 同源组
 *
 * 组装辅助链: miniprot → CtgGroupCli → HomoConflictBasedPartition(自带CLI) → SeperateChrByAlleles
 * ⚠️ main() 硬编码路径——改走 setInMiniprotGff/setPloyPoid/setOutContigGrpMap + process()。
 */
public class CtgGroupCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: CtgGroupCli <in.miniprot.gff> <polyPoid> <outContigGrpMap>");
            System.exit(1);
        }
        Object o = Class.forName("biocjava.bioDoer.GenomeAssembly.ContigGroupByAlleleMap")
                .getDeclaredConstructor().newInstance();
        Class<?> c = o.getClass();
        c.getMethod("setInMiniprotGff", File.class).invoke(o, new File(args[0]));
        c.getMethod("setPloyPoid", int.class).invoke(o, Integer.parseInt(args[1]));
        c.getMethod("setOutContigGrpMap", File.class).invoke(o, new File(args[2]));
        c.getMethod("process").invoke(o);
        System.err.println("[tbplot] contig 等位分组完成: " + args[2]);
        System.exit(0);
    }
}