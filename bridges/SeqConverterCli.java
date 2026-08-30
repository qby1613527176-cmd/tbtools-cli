import biocjava.bioIO.SeqFormatConvert.seqFactory.SeqConverter;

/**
 * tbcli seqConverter 桥 — 序列格式转换 CLI（08/31）
 *
 * 用法: SeqConverterCli -i <in> -o <out> -iF <fmt> -oF <fmt>
 *   fmt: fasta|clustal|MEGA|nexus|PAML|phylip
 *
 * ⚠️ SeqConverter.main 是硬编码演示 → 真实 CLI 入口是 main1(public static)
 *   （main1 ≠ main 规律：PafGenomeComp/SeqConverter 同型）
 */
public class SeqConverterCli {
    public static void main(String[] args) throws Exception {
        SeqConverter.main1(args);
        System.exit(0);
    }
}
