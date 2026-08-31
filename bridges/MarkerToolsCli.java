import biocjava.bioDoer.markerDesign.MarkerDist;
import biocjava.bioDoer.markerDesign.MarkerFilter;
import biocjava.bioDoer.markerDesign.SampleDist;

import java.io.File;

/**
 * tbcli markertools — 分子标记分析 CLI（08/31 第七十七波）
 *
 * 用法:
 *   MarkerToolsCli filter <in.marker.tab>            # 标记过滤(minor allele 统计,输出 stderr)
 *   MarkerToolsCli dist <in.marker.tab> <maxPoint>   # 标记距离计算
 *   MarkerToolsCli sampledist <in.marker.tab>        # 样本距离计算
 *
 * in.marker.tab: 0/1 标记矩阵,行=样本/个体,列=标记,首行列名+首列行名
 *
 * 引擎: MarkerFilter/MarkerDist/SampleDist 的 setInMarker + process()（main 均硬编码演示）
 */
public class MarkerToolsCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: MarkerToolsCli <filter|dist|sampledist> <in.marker.tab> [maxPoint]");
            System.exit(1);
        }
        String mode = args[0];
        File inFile = new File(args[1]);
        if (!inFile.exists()) {
            System.err.println("错误: 文件不存在: " + args[1]);
            System.exit(1);
        }
        switch (mode) {
            case "filter": {
                MarkerFilter mf = new MarkerFilter();
                mf.setInMarker(inFile);
                mf.process();
                break;
            }
            case "dist": {
                MarkerDist md = new MarkerDist();
                md.setInMarker(inFile);
                if (args.length > 2) md.setMaxPoint(Integer.parseInt(args[2]));
                md.process();
                break;
            }
            case "sampledist": {
                SampleDist sd = new SampleDist();
                sd.setInMarker(inFile);
                sd.process();
                break;
            }
            default:
                System.err.println("未知模式: " + mode + " (支持 filter|dist|sampledist)");
                System.exit(1);
        }
        System.exit(0);
    }
}