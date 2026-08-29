import java.io.File;
import java.lang.reflect.Method;
import java.util.ArrayList;

/**
 * tbplot findBlockMultiple — 多基因组伪共线性区块搜索 CLI（08/29，第 52 引擎）
 *
 * 用法: FindBlockMultipleCli <queryGenome.fa> <query.gff> <queryId> <out.txt> <sub1Genome.fa> <sub1.gff> [<sub2Genome.fa> <sub2.gff> ...] [--leftEdge N --rightEdge N --expand N --threads N]
 *   queryGenome.fa / query.gff : 查询物种基因组 + 注释
 *   queryId                    : 查询基因 ID（基因组中部，避开首个基因 get(-1) 边界 bug）
 *   out.txt                    : 区块结果（含 query + 各 subject 行）
 *   subNGenome.fa / subN.gff   : 1 或多个比对物种（成对给出）
 *
 * ⚠️ main1() 硬编码路径——改走完整 setter + processMultipleGenome()。
 * ⚠️ 大数据引擎：必须 -Djava.io.tmpdir=<磁盘>（/tmp=tmpfs 16G 会被 3GB 基因组 init 撑爆）。
 *
 * 例: FindBlockMultipleCli Cr.fa Cr.gff evm.model.Chr06.1064 out.txt Cs.fa Cs.gff Ni.fa Ni.gff
 */
public class FindBlockMultipleCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 7 || (args.length - 4) % 2 != 0) {
            System.err.println("用法: FindBlockMultipleCli <queryGenome.fa> <query.gff> <queryId> <out.txt> <sub1Genome.fa> <sub1.gff> [<sub2Genome.fa> <sub2.gff> ...] [--leftEdge N --rightEdge N --expand N --threads N]");
            System.exit(1);
        }
        File qGenome = new File(args[0]);
        File qGxf = new File(args[1]);
        String queryId = args[2];
        File out = new File(args[3]);
        ArrayList<File> subGenomes = new ArrayList<>();
        ArrayList<File> subGxfs = new ArrayList<>();
        int i = 4;
        int left = 10, right = 10, expand = 15, threads = 8;
        // 顺序解析：-- 开头=选项，否则是 subject 基因组/gff 对
        while (i < args.length) {
            String a = args[i];
            if (a.equals("--leftEdge") && i+1 < args.length) { left = Integer.parseInt(args[++i]); i++; }
            else if (a.equals("--rightEdge") && i+1 < args.length) { right = Integer.parseInt(args[++i]); i++; }
            else if (a.equals("--expand") && i+1 < args.length) { expand = Integer.parseInt(args[++i]); i++; }
            else if (a.equals("--threads") && i+1 < args.length) { threads = Integer.parseInt(args[++i]); i++; }
            else if (a.startsWith("--")) { System.err.println("未知选项: " + a); System.exit(1); }
            else {
                if (i+1 >= args.length) { System.err.println("subject gff 缺失: " + a); System.exit(1); }
                subGenomes.add(new File(a));
                subGxfs.add(new File(args[i+1]));
                i += 2;
            }
        }
        if (subGenomes.isEmpty()) { System.err.println("至少需要一个 subject 基因组"); System.exit(1); }
        Object obj = Class.forName("biocjava.bioDoer.PseudoSyntenyBlock.FindBlockMultiple")
                .getDeclaredConstructor().newInstance();
        Class<?> cls = obj.getClass();
        cls.getMethod("setInGenomeSequence_Query", File.class).invoke(obj, qGenome);
        cls.getMethod("setInGxf_Query", File.class).invoke(obj, qGxf);
        cls.getMethod("setQueryId", String.class).invoke(obj, queryId);
        cls.getMethod("setInSubjectGenomeFileArr", ArrayList.class).invoke(obj, subGenomes);
        cls.getMethod("setInSubjectGxfFileArr", ArrayList.class).invoke(obj, subGxfs);
        cls.getMethod("setOutResultFile", File.class).invoke(obj, out);
        cls.getMethod("setLeftEdgeCount", int.class).invoke(obj, left);
        cls.getMethod("setRightEdgeCount", int.class).invoke(obj, right);
        cls.getMethod("setTargetEdgeExpandCount", int.class).invoke(obj, expand);
        try { cls.getMethod("setNumOfThread", int.class).invoke(obj, threads); } catch (NoSuchMethodException e) {}
        Method pm = cls.getMethod("processMultipleGenome");
        pm.invoke(obj);
        System.err.println("[tbplot] findBlockMultiple 完成: " + out);
        System.exit(0);
    }
}
