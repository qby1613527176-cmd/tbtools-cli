/**
 * tbplot hmmerSearch — Advanced HMMer Search CLI（插件 P00680 CLI 化）
 *
 * 用法: HmmerSuiteCli <target.fa> <hmmDb> <out.tsv>
 *   target.fa: 待扫描序列（蛋白）
 *   hmmDb:     HMM 数据库（.hmm，需 hmmpress 过或单 HMM 文件）
 *   out.tsv:   解析后的 domtblout 结果表
 *
 * 引擎: HmmerSuite.HMMSearchWrapper（插件 jar），setIn* + process()。
 *
 * ⚠️ 已知插件缺陷 + 桥层规避：
 *   插件对 inHMMDb 的跨目录 hard link（Files.createLink）**没有异常兜底**，
 *   输入输出不同目录且跨文件系统时抛 FileSystemException 崩溃
 *   （实测: /home vs /tmp 即触发）。规避: 把输入复制到输出目录，
 *   使其与 outFile 同目录 → 插件跳过 link 分支。
 *   二进制: 优先 plugins/lib/bin（随包/environment）；缺失回退系统 PATH。
 */
public class HmmerSuiteCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: HmmerSuiteCli <target.fa> <hmmDb> <out.tsv>");
            System.exit(1);
        }
        java.io.File inSeq = new java.io.File(args[0]);
        java.io.File inDb = new java.io.File(args[1]);
        java.io.File out = new java.io.File(args[2]);
        java.io.File outDir = out.getAbsoluteFile().getParentFile();
        if (outDir == null) outDir = new java.io.File(".");
        java.io.File tmpSeq = new java.io.File(outDir, inSeq.getName());
        java.io.File tmpDb = new java.io.File(outDir, inDb.getName());
        java.nio.file.Files.copy(inSeq.toPath(), tmpSeq.toPath(),
                java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        java.nio.file.Files.copy(inDb.toPath(), tmpDb.toPath(),
                java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        tmpSeq.deleteOnExit();
        tmpDb.deleteOnExit();

        Object w = Class.forName("HmmerSuite.HMMSearchWrapper").getDeclaredConstructor().newInstance();
        Class<?> c = w.getClass();
        c.getMethod("setInSequence", java.io.File.class).invoke(w, tmpSeq);
        c.getMethod("setInHMMDb", java.io.File.class).invoke(w, tmpDb);
        c.getMethod("setOutFile", java.io.File.class).invoke(w, out);
        c.getMethod("process").invoke(w);
        System.err.println("[tbplot] 已保存: " + args[2]);
        System.exit(0);
    }
}