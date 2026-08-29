import java.io.File;
import java.util.ArrayList;
import java.util.List;

/**
 * tbplot bamstate — BAM 覆盖状态评估 CLI（08/29，第 57 引擎）
 *
 * 用法: BamStateCli <gff3> <out.tsv> <bam1> [bam2 ...] [--coverageThr X] [--depthThr X]
 *   gff3: 标准 GFF3（gene/mRNA/exon 特征）
 *   out.tsv: 每 BAM 的 coverage 比例 / depth / 总基因数 / 表达基因数
 *   bamN: 比对 BAM（需 samtools index 建立 .bai）
 *
 * ⚠️ BAM 参考染色体名必须与 GFF3 seqid 匹配（HiC_scaffold_* 等）
 *    实测：GRAS RNA-seq bam_subset + arrb21 GFF3（HiC_scaffold）验证通过
 */
public class BamStateCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: BamStateCli <gff3> <out.tsv> <bam1> [bam2 ...] [--coverageThr X] [--depthThr X]");
            System.exit(1);
        }
        // 解析选项（-- 开头），其余为 bam
        ArrayList<String> bams = new ArrayList<>();
        double covThr = 0.5, depthThr = 3.0;
        boolean gffDone = false;
        String gff = args[0];
        String out = args[1];
        for (int i = 2; i < args.length; i++) {
            if (args[i].equals("--coverageThr") && i+1 < args.length) covThr = Double.parseDouble(args[++i]);
            else if (args[i].equals("--depthThr") && i+1 < args.length) depthThr = Double.parseDouble(args[++i]);
            else bams.add(args[i]);
        }
        if (bams.isEmpty()) { System.err.println("至少需要一个 BAM"); System.exit(1); }
        ArrayList<File> bamFiles = new ArrayList<>();
        for (String b : bams) bamFiles.add(new File(b));
        Object o = Class.forName("biocjava.bioDoer.GenomeAnnotation.BAMStateAssessor")
                .getDeclaredConstructor().newInstance();
        Class<?> c = o.getClass();
        c.getMethod("setBamFiles", List.class).invoke(o, bamFiles);
        c.getMethod("setGffFile", File.class).invoke(o, new File(gff));
        c.getMethod("setCoverageThreshold", double.class).invoke(o, covThr);
        c.getMethod("setDepthThreshold", double.class).invoke(o, depthThr);
        c.getMethod("setOutputFile", File.class).invoke(o, new File(out));
        c.getMethod("setThreads", int.class).invoke(o, 4);
        c.getMethod("process").invoke(o);
        System.err.println("[tbplot] BAM 状态评估完成: " + out);
        System.exit(0);
    }
}