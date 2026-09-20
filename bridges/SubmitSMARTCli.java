/**
 * tbplot smart — SMART 域注释 CLI（插件 P00060 CLI 化）
 *
 * 用法: SubmitSMARTCli <in.fa> <out.txt> [--pfam] [--signalp] [--disembl] [--schnipsel] [--rep]
 *   开关默认全开；关闭传 --no-xxx 不需要（默认全 true）
 *
 * ⚠️ 联网：POST 到 EMBL ismart.embl.de/smart/show_motifs.pl（约 10-60s）。
 * 输出: 每行 query + 域位置 + 域类型（Pfam:XXX / low_complexity_region 等）。
 */
public class SubmitSMARTCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: SubmitSMARTCli <in.fa> <out.txt>");
            System.exit(1);
        }
        Object s = Class.forName("BatchSMART.submitSMART").getDeclaredConstructor().newInstance();
        Class<?> c = s.getClass();
        c.getMethod("setInFa", java.io.File.class).invoke(s, new java.io.File(args[0]));
        c.getMethod("setOutTab", java.io.File.class).invoke(s, new java.io.File(args[1]));
        c.getMethod("setDo_pfam", boolean.class).invoke(s, true);
        c.getMethod("setDo_signalp", boolean.class).invoke(s, true);
        c.getMethod("setDo_disembl", boolean.class).invoke(s, true);
        c.getMethod("setDo_schnipsel", boolean.class).invoke(s, true);
        c.getMethod("setDo_rep", boolean.class).invoke(s, true);
        c.getMethod("setFinished", boolean.class).invoke(s, false);
        c.getMethod("process").invoke(s);
        System.err.println("[tbplot] SMART 注释完成: " + args[1]);
        System.exit(0);
    }
}