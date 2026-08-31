import biocjava.bioIO.BioSoftPipeServer.pepAln2CodonAln;

import java.io.File;

/**
 * tbcli pep2codon — 蛋白比对回译密码子比对 CLI（08/31 第八十二波，工具 91）
 *
 * 用法: Pep2CodonCli <cds.fa> <pep.aln.fa> <codon.aln.out>
 *   cds.fa:       CDS 序列（ID 与 pep.aln 一致）
 *   pep.aln.fa:   蛋白比对（含 gap 的比对结果）
 *   codon.aln.out: 输出密码子比对（Ka/Ks 分析输入）
 *
 * 引擎: pepAln2CodonAln.transformat(File, File, File) —— 静态方法直接调用（main 硬编码演示）
 *   （PairWiseKaKsCalculator 内部回译逻辑的独立版——Ka/Ks 分析刚需）
 */
public class Pep2CodonCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: Pep2CodonCli <cds.fa> <pep.aln.fa> <codon.aln.out>");
            System.exit(1);
        }
        pepAln2CodonAln.transformat(new File(args[0]), new File(args[1]), new File(args[2]));
        System.err.println("[tbplot] 已保存: " + args[2]);
        System.exit(0);
    }
}
