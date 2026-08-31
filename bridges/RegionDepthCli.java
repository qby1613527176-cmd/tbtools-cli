import biocjava.bioDoer.JIGplotToolkit.miRCoverage.CalcRegionDepth;

import java.io.File;

/**
 * tbcli regiondepth — SAM 区域覆盖深度 CLI（08/31 第七十六波）
 *
 * 用法: RegionDepthCli <in.sam> <region> <out.depth> [scaleFactor]
 *   in.sam: 已排序或未排序 SAM（内部自动按位置排序+建索引）
 *   region: ChrID:Start-End 或 ChrID#Start#End（1-based）
 *   out.depth: 每碱基覆盖深度
 *   scaleFactor: 缩放因子（默认 1）
 *
 * 引擎: CalcRegionDepth.init() + processRegion()（main 硬编码演示 → setter+process）
 */
public class RegionDepthCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: RegionDepthCli <in.sam> <region> <out.depth> [scaleFactor]");
            System.exit(1);
        }
        int scale = args.length > 3 ? Integer.parseInt(args[3]) : 1;
        CalcRegionDepth crd = new CalcRegionDepth();
        crd.init(new File(args[0]));
        crd.processRegion(args[1], new File(args[2]), scale);
        System.err.println("[tbplot] 已保存: " + args[2] + " (region=" + args[1] + ")");
        System.exit(0);
    }
}
