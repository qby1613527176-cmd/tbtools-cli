/**
 * tbplot hmmerSearch — Advanced HMMer Search CLI（插件 P00680 CLI 化）
 *
 * 用法: HmmerSuiteCli <target.fa> <hmmDb> <out.tsv>
 *   target.fa: 待扫描序列（蛋白）
 *   hmmDb:     HMM 数据库（.hmm，需 hmmpress 过或单 HMM 文件）
 *   out.tsv:   解析后的 domtblout 结果表
 *
 * 引擎: HmmerSuite.HMMSearchWrapper（插件 jar），setIn* + process()。
 *   二进制发现: 优先插件自带 plugins/lib/bin/（Linux hmmsearch 已随包发行），
 *   缺失时回退系统 PATH 的 hmmsearch。
 *   与 base CLI 的 simpleHmmscan 差异: 无需 Pfam idList，直接全库扫描 +
 *   domtblout 解析（HMMSearchDomParser）。
 */
public class HmmerSuiteCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: HmmerSuiteCli <target.fa> <hmmDb> <out.tsv>");
            System.exit(1);
        }
        Object w = Class.forName("HmmerSuite.HMMSearchWrapper").getDeclaredConstructor().newInstance();
        Class<?> c = w.getClass();
        c.getMethod("setInSequence", java.io.File.class).invoke(w, new java.io.File(args[0]));
        c.getMethod("setInHMMDb", java.io.File.class).invoke(w, new java.io.File(args[1]));
        c.getMethod("setOutFile", java.io.File.class).invoke(w, new java.io.File(args[2]));
        c.getMethod("process").invoke(w);
        System.err.println("[tbplot] 已保存: " + args[2]);
        System.exit(0);
    }
}
