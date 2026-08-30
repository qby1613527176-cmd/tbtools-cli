import biocjava.bioDoer.GXFUtils.GeneDensityProfiler;

import java.io.File;

/**
 * tbplot genedensity — 基因密度谱 CLI（08/31 第五十三波）
 *
 * 用法: GeneDensityCli <in.gff3> <out> [binSize]
 *   in.gff3: 基因组注释
 *   out:     基因密度表 (tsv)
 *   binSize: 窗口大小 bp（默认 100000）
 *
 * 引擎: GeneDensityProfiler.setBinSize/setInGXF/setOutGeneRecordFile/process()
 *       （窗口内基因计数 → 染色体密度谱，供基因组轨道/密度热图）
 */
public class GeneDensityCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: GeneDensityCli <in.gff3> <out> [binSize]");
            System.exit(1);
        }
        String inGff = args[0];
        String out = args[1];
        int binSize = args.length > 2 ? Integer.parseInt(args[2]) : 100000;

        GeneDensityProfiler gdp = new GeneDensityProfiler();
        gdp.setBinSize(binSize);
        gdp.setInGXF(new File(inGff));
        gdp.setOutGeneRecordFile(new File(out));
        gdp.process();
        System.err.println("[tbplot] 已保存: " + out + " (binSize=" + binSize + ")");
        System.exit(0);
    }
}
