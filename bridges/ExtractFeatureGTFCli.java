import biocjava.bioIO.GTF.ExtractFeaturefromGTFandGenome;

/**
 * tbplot extractFeatureFromGTF — GTF 特征提取 CLI（RPC 交付包 N6 修复，09/21）
 *
 * 用法: ExtractFeatureGTFCli <in.gtf> <genome.fa> <out.gff|tsv> [--up N] [--down N] [--addUpDownN true|false] [--onlyUpOrDown true|false]
 *
 * 引擎: ExtractFeaturefromGTFandGenome（javap 实锤签名）
 *   setGtfFile(String)/setInGenome(String)/setOutFeatureFile(String)/process(String,String,boolean)
 *   main() 硬编码 Windows 路径 → 直通必崩；桥包装 setter 即可用（N6）。
 */
public class ExtractFeatureGTFCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: ExtractFeatureGTFCli <in.gtf> <genome.fa> <out.gff|tsv> [--up N] [--down N] [--addUpDownN true|false] [--onlyUpOrDown true|false]");
            System.exit(1);
        }
        String inGtf = args[0];
        String genome = args[1];
        String out = args[2];
        if (!new java.io.File(inGtf).exists()) { System.err.println("错误: 输入 GTF 不存在: " + inGtf); System.exit(2); }
        if (!new java.io.File(genome).exists()) { System.err.println("错误: 基因组 FASTA 不存在: " + genome); System.exit(2); }

        ExtractFeaturefromGTFandGenome eng = new ExtractFeaturefromGTFandGenome();
        eng.setGtfFile(inGtf);
        eng.setInGenome(genome);
        eng.setOutFeatureFile(out);
        // main() 流程: setGtfFile → preProcess() → setOutFeatureFile → setInGenome → process(gtf, outPrefix, only)
        eng.preProcess();
        int up = 0, down = 0;
        boolean addN = false, only = false;
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--up") && i + 1 < args.length) up = Integer.parseInt(args[++i]);
            else if (args[i].equals("--down") && i + 1 < args.length) down = Integer.parseInt(args[++i]);
            else if (args[i].equals("--addUpDownN") && i + 1 < args.length) addN = Boolean.parseBoolean(args[++i]);
            else if (args[i].equals("--onlyUpOrDown") && i + 1 < args.length) only = Boolean.parseBoolean(args[++i]);
        }
        eng.setUpStreamBases(up);
        eng.setDownStreamBases(down);
        eng.setAddUpDownN(addN);
        eng.setOnlyUpOrDownStreamBases(only);
        StringBuffer sb = eng.process(inGtf, out, only);        // 结果在 process() 返回值里，落盘（引擎 out 参数疑似前缀/未写文件）
        if (sb != null && sb.length() > 0) {
            java.io.FileWriter fw = new java.io.FileWriter(new java.io.File(out));
            fw.write(sb.toString());
            fw.close();
            System.err.println("[tbplot] 特征提取完成: " + out + " (" + sb.length() + " chars)");
        } else {
            System.err.println("[tbplot] 特征提取完成(空结果): " + out);
        }
        System.exit(0);
    }
}