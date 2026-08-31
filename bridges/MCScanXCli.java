import org.mcscanx.api.MCScanXAPI;

import java.io.File;

/**
 * tbcli mcscanx — 纯 Java MCScanX 共线性检测 + 重复基因分类 CLI（08/31 第六十八波）
 *
 * 用法:
 *   MCScanXCli <gff> <blast> <outPrefix> [--html]              # 共线性检测
 *   MCScanXCli classify <gff> <blast> <outPrefix>              # 重复基因分类（WGD/tandem 等）
 *
 *   gff:      简化 GFF（MCScanX 格式）
 *   blast:    BLAST tab 结果（12 列，蛋白互相比对）
 *   outPrefix: 输出前缀（生成 <prefix>.collinearity / .duptype）
 *   --html:   可选生成 HTML 可视化
 *
 * 引擎: org.mcscanx.api.MCScanXAPI — 纯 Java 实现，无需外部 MCScanX 二进制
 *   （GRAS WGD/共线性分析刚需；与外部 MCScanX 输出 100% 一致验证）
 */
public class MCScanXCli {
    public static void main(String[] args) throws Exception {
        // 模式 1: classify 子命令 → 重复基因分类
        if (args.length >= 1 && args[0].equals("classify")) {
            if (args.length < 4) {
                System.err.println("用法: MCScanXCli classify <gff> <blast> <outPrefix>");
                System.exit(1);
            }
            String gff = args[1];
            String blast = args[2];
            String outPrefix = args[3];
            File gffFile = new File(gff);
            File blastFile = new File(blast);
            if (!gffFile.exists() || !blastFile.exists()) {
                System.err.println("错误: 文件不存在: " + gff + " / " + blast);
                System.exit(1);
            }
            // ⚠️ classifyDuplicateGenes(String) 的 String API 只设 geneTypeFile，但 validate 要求 collinearityFile → 必须用完整 InputFiles/OutputOptions API
            org.mcscanx.config.InputFiles inputFiles = org.mcscanx.config.InputFiles.builder()
                .gffFile(gffFile.getAbsolutePath())
                .blastFile(blastFile.getAbsolutePath())
                .build();
            org.mcscanx.config.OutputOptions outputOptions = org.mcscanx.config.OutputOptions.builder()
                .collinearityFile(outPrefix + ".collinearity")
                .geneTypeFile(outPrefix + ".gene_type")
                .build();
            MCScanXAPI api = new MCScanXAPI();
            MCScanXAPI.ClassificationResult cl = api.classifyDuplicateGenes(inputFiles, outputOptions);
            File outGeneType = new File(outPrefix + ".gene_type");
            System.err.println("[tbplot] 重复基因分类: " + (outGeneType.exists() ? outGeneType.getAbsolutePath() : "(未生成)"));
            System.err.println("[tbplot] 分类结果文件: " + cl.getOutputFile());
            System.exit(0);
        }

        // 模式 2: 共线性检测
        if (args.length < 3) {
            System.err.println("用法: MCScanXCli <gff> <blast> <outPrefix> [--html] | MCScanXCli classify <gff> <blast> <outPrefix>");
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