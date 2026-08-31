import biocjava.bioDoer.GXFUtils.GSAssess.GsaQuickDiagnosis;

import java.io.File;

/**
 * tbcli gsadiag — 基因结构快速诊断 CLI（08/31 第八十四波，工具 94）
 *
 * 用法: GsaDiagCli <in.fixed.gff3> <out.stat.xls> [genome.fasta] [relax] [--checkUTR]
 *   in.fixed.gff3: 注释 GFF3（建议已相位校正）
 *   out.stat.xls: 诊断统计输出
 *   genome.fasta: 可选基因组（编码潜能检查）
 *   relax: 长度异常 relax 参数（默认 0.5）
 *   --checkUTR: 检查 UTR 比例异常
 *
 * 引擎: GsaQuickDiagnosis.setInFixedGXF/setOutStat/setOptionalGenomeSequence/setRelax + process()
 *   （main 硬编码演示 → setter+process；Gff3PhaseValidator + LengthAnomalyChecker 内部检查）
 */
public class GsaDiagCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: GsaDiagCli <in.fixed.gff3> <out.stat.xls> [genome.fasta] [relax] [--checkUTR]");
            System.exit(1);
        }
        GsaQuickDiagnosis gqd = new GsaQuickDiagnosis();
        gqd.setInFixedGXF(new File(args[0]));
        gqd.setOutStat(new File(args[1]));
        boolean checkUtr = false;
        double relax = 0.5;
        for (String a : args) {
            if (a.equals("--checkUTR")) checkUtr = true;
        }
        if (args.length > 2 && !args[2].equals("--checkUTR")) {
            File g = new File(args[2]);
            if (g.exists()) gqd.setOptionalGenomeSequence(g);
        }
        if (args.length > 3 && !args[3].equals("--checkUTR")) {
            try { relax = Double.parseDouble(args[3]); } catch (Exception e) {}
        }
        gqd.setRelax(relax);
        gqd.setCheckUTR(checkUtr);
        gqd.process();
        System.err.println("[tbplot] 已保存: " + args[1]);
        System.exit(0);
    }
}