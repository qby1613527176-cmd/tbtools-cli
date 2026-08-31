import org.mcscanx.api.MCScanXAPI;

import java.io.File;

/**
 * tbcli mcscanx — 纯 Java MCScanX 共线性检测 CLI（08/31 第六十八波）
 *
 * 用法: MCScanXCli <gff> <blast> <outPrefix> [--html]
 *   gff:      简化 GFF（MCScanX 格式）
 *   blast:    BLAST tab 结果（12 列，蛋白互相比对）
 *   outPrefix: 输出前缀（生成 <prefix>.collinearity）
 *   --html:   可选生成 HTML 可视化
 *
 * 引擎: org.mcscanx.api.MCScanXAPI.detectSynteny() — 纯 Java 实现，无需外部 MCScanX 二进制
 *   （GRAS WGD/共线性分析刚需；2026-08-31 攻下）
 */
public class MCScanXCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: MCScanXCli <gff> <blast> <outPrefix> [--html]");
            System.exit(1);
        }
        String gff = args[0];
        String blast = args[1];
        String outPrefix = args[2];
        boolean html = false;
        for (String a : args) if (a.equals("--html")) html = true;

        File gffFile = new File(gff);
        File blastFile = new File(blast);
        if (!gffFile.exists() || !blastFile.exists()) {
            System.err.println("错误: 文件不存在: " + gff + " / " + blast);
            System.exit(1);
        }

        MCScanXAPI api = new MCScanXAPI();
        MCScanXAPI.SyntenyResult result = api.detectSynteny(gffFile.getAbsolutePath(), blastFile.getAbsolutePath(), outPrefix, html);

        File outCollinearity = new File(outPrefix + ".collinearity");
        System.err.println("[tbplot] 共线性结果: " + (outCollinearity.exists() ? outCollinearity.getAbsolutePath() : "(未生成)"));
        System.err.println("[tbplot] blocks: " + result.getSegmentCount() + " segments");
        System.exit(0);
    }
}