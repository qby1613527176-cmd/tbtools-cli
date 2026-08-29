import java.io.File;
import java.lang.reflect.Method;

/**
 * tbplot findBlockDual — 双基因组伪共线性区块搜索 CLI（08/29，第 50 引擎）
 *
 * 用法: FindBlockDualCli <queryGenome.fa> <query.gff> <subjectGenome.fa> <subject.gff> <queryId> <out.txt>
 *   queryGenome.fa / subjectGenome.fa : 两物种基因组 FASTA
 *   query.gff / subject.gff            : 两物种 GFF/GXF 注释（含 mRNA 行）
 *   queryId                            : 查询基因 ID（mRNA ID，如 AT1G70000.2）
 *   out.txt                            : 伪共线性区块匹配结果
 *
 * 可选参数（默认值）:
 *   --leftEdge N(5) --rightEdge N(5) --expand N(10) --threads N(2) --evalue 1e-5 --minIdentity 0.33 --bestHit N(10)
 *
 * ⚠️ FindBlockDual.main() 硬编码路径——改走完整 setter + process()。
 *    内部用 blastp 找 query 侧边缘基因在 subject 侧的同源，推断共线性区块。
 *    ⚠️ 需真实双基因组数据验证（本地无拟南芥 TAIR10 对照数据）。
 */
public class FindBlockDualCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 6) {
            System.err.println("用法: FindBlockDualCli <queryGenome.fa> <query.gff> <subjectGenome.fa> <subject.gff> <queryId> <out.txt> [--leftEdge N] [--rightEdge N] [--expand N] [--threads N] [--evalue X] [--minIdentity X] [--bestHit N]");
            System.exit(1);
        }
        File qGenome = new File(args[0]);
        File qGxf = new File(args[1]);
        File sGenome = new File(args[2]);
        File sGxf = new File(args[3]);
        String queryId = args[4];
        File out = new File(args[5]);
        // 默认值（与引擎默认一致）
        int left = 5, right = 5, expand = 10, threads = 2, bestHit = 10;
        double evalue = 1.0e-5, minIdentity = 0.33;
        for (int i = 6; i < args.length; i++) {
            String a = args[i];
            if (a.equals("--leftEdge") && i+1 < args.length) left = Integer.parseInt(args[++i]);
            else if (a.equals("--rightEdge") && i+1 < args.length) right = Integer.parseInt(args[++i]);
            else if (a.equals("--expand") && i+1 < args.length) expand = Integer.parseInt(args[++i]);
            else if (a.equals("--threads") && i+1 < args.length) threads = Integer.parseInt(args[++i]);
            else if (a.equals("--evalue") && i+1 < args.length) evalue = Double.parseDouble(args[++i]);
            else if (a.equals("--minIdentity") && i+1 < args.length) minIdentity = Double.parseDouble(args[++i]);
            else if (a.equals("--bestHit") && i+1 < args.length) bestHit = Integer.parseInt(args[++i]);
        }
        Object obj = Class.forName("biocjava.bioDoer.PseudoSyntenyBlock.FindBlockDual").getDeclaredConstructor().newInstance();
        Class<?> cls = obj.getClass();
        cls.getMethod("setInGenomeSequence_Query", File.class).invoke(obj, qGenome);
        cls.getMethod("setInGxf_Query", File.class).invoke(obj, qGxf);
        cls.getMethod("setInGenomeSequence_Subject", File.class).invoke(obj, sGenome);
        cls.getMethod("setInGxf_Subject", File.class).invoke(obj, sGxf);
        cls.getMethod("setQueryId", String.class).invoke(obj, queryId);
        cls.getMethod("setOutMatchInfo", File.class).invoke(obj, out);
        cls.getMethod("setLeftEdgeCount", int.class).invoke(obj, left);
        cls.getMethod("setRightEdgeCount", int.class).invoke(obj, right);
        cls.getMethod("setTargetEdgeExpandCount", int.class).invoke(obj, expand);
        // numOfThread / evalue / minIdentity / retainBestHitNum 无公开 setter，用反射
        try { cls.getMethod("setNumOfThread", int.class).invoke(obj, threads); } catch (NoSuchMethodException e) {}
        try { cls.getMethod("setEvalue", double.class).invoke(obj, evalue); } catch (NoSuchMethodException e) {}
        try { cls.getMethod("setSpecifiedMinIdentity", double.class).invoke(obj, minIdentity); } catch (NoSuchMethodException e) {}
        try { cls.getMethod("setRetainBestHitNum", int.class).invoke(obj, bestHit); } catch (NoSuchMethodException e) {}
        Method process = cls.getMethod("process");
        String result = (String) process.invoke(obj);
        if (result != null && !result.trim().isEmpty()) {
            java.io.FileWriter fw = new java.io.FileWriter(out);
            fw.write(result);
            fw.close();
        }
        System.err.println("[tbplot] findBlockDual 完成: " + out);
        System.exit(0);
    }
}
