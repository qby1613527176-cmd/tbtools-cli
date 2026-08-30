import biocjava.bioDoer.repeatScoreCompute.calcRepeatScore;

import java.io.File;

/**
 * tbplot calcRepeat — TBtools 重复序列得分计算 CLI（tool 39，08/31 攻克）
 *
 * 用法: CalcRepeatCli <genome.fa> <outRepeat.txt> [--kmerSize N] [--minFreq N] [--threads N]
 *   genome.fa: 基因组 FASTA
 *   outRepeat.txt: 输出重复得分（chr\tstart\tend\tscore）
 *
 * 引擎: calcRepeatScore（需 jellyfish 可执行）
 *   process() 内部用默认 numOfThreads=60 + -s 2000M 调 jellyfish count → 小数据/慢环境易挂
 * 破解: 预生成 <genome>.<kmer>.kmer.jf 文件（ProcessBuilder 用合理线程数，参数 -m -L -C 同引擎），
 *   process() 检测 .jf 已存在 → 跳过内部 jellyfish count → JellyfishServer 直接 query → 输出得分
 */
public class CalcRepeatCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: CalcRepeatCli <genome.fa> <outRepeat.txt> [--kmerSize N] [--minFreq N] [--threads N]");
            System.exit(1);
        }
        String inFa = args[0];
        String outFile = args[1];
        int kmerSize = 15, minFreq = 2, threads = 4;
        for (int i = 2; i < args.length; i++) {
            if (args[i].equals("--kmerSize") && i+1<args.length) kmerSize = Integer.parseInt(args[++i]);
            else if (args[i].equals("--minFreq") && i+1<args.length) minFreq = Integer.parseInt(args[++i]);
            else if (args[i].equals("--threads") && i+1<args.length) threads = Integer.parseInt(args[++i]);
        }

        // 预生成 .jf（引擎命名: <genome>.<kmer>.kmer.jf）
        File jf = new File(inFa + "." + kmerSize + ".kmer.jf");
        if (!jf.exists()) {
            System.err.println("[tbplot] 生成 jellyfish 计数: " + jf.getAbsolutePath());
            ProcessBuilder pb = new ProcessBuilder("jellyfish", "count",
                    "-m", String.valueOf(kmerSize),
                    "-s", "100M",
                    "-t", String.valueOf(threads),
                    "-L", String.valueOf(minFreq),
                    "-C",
                    inFa, "-o", jf.getAbsolutePath());
            pb.redirectErrorStream(true);
            Process p = pb.start();
            p.waitFor();
            if (!jf.exists()) {
                System.err.println("错误: jellyfish count 失败");
                System.exit(1);
            }
        }

        // 调引擎 process()
        calcRepeatScore c = new calcRepeatScore();
        c.setInGenomeSequence(new File(inFa));
        c.setOutRepeatFile(new File(outFile));
        c.setKmerSize(kmerSize);
        c.setMinFreq(minFreq);
        c.process();
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }
}