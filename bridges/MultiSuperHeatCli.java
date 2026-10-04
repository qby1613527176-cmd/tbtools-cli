import java.io.File;
import java.lang.reflect.Method;
import java.util.ArrayList;

import biocjava.bioDoer.SimpleEfpBrowser.generateMultipleSuperHeatMap;
import jigplot.engine.JIGBasePanel;

/**
 * tbcli multiEfp 桥 — 多矩阵组织表达热图（08/31 第四十四波破解, 10/04 重建）
 *
 * 用法: MultiSuperHeatCli <inTGA> <sample2cc> <expMat1[,expMat2,...]> <geneId> <out>
 *   ⚠️ generateMultipleSuperHeatMap.main 是 ArgsParser 完整 CLI 但 main 里 setValue
 *   硬编码第二个矩阵路径(ExpressData1.txt) → 直接 main 会 FileNotFoundException。
 *   绕 main 走核心 API: setter 注入 + 反射 private initExp() + showHeatMapOf(geneId)
 *   → JIGBasePanel → save2SVG(同 HeatmapCli/GeneStructureCli 先例)。
 *   TGA 须 TrueColor(type2)；需 fake DatatypeConverter(build/javax/xml/bind/, JDK9+)。
 */
public class MultiSuperHeatCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 5) {
            System.err.println("用法: multiEfp <inTGA> <sample2cc> <expMat1[,expMat2,...]> <geneId> <out> [--imageWidth N]");
            System.exit(2);
        }
        generateMultipleSuperHeatMap eng = new generateMultipleSuperHeatMap();
        eng.setInTGAFile(new File(args[0]));
        eng.setSampleName2CodeFile(new File(args[1]));
        ArrayList<File> exps = new ArrayList<File>();
        for (String p : args[2].split(",")) {
            if (!p.trim().isEmpty()) exps.add(new File(p.trim()));
        }
        eng.setExpressMatrixFileArr(exps);
        File outFile = new File(args[4]);
        eng.setOutImageFile(outFile);
        // 反射调 private initExp()（main 内部调用的初始化）
        Method init = generateMultipleSuperHeatMap.class.getDeclaredMethod("initExp");
        init.setAccessible(true);
        init.invoke(eng);
        JIGBasePanel panel = eng.showHeatMapOf(args[3]);
        panel.save2SVG(outFile);
        System.err.println("[tbplot] 已保存: " + args[4]);
        System.exit(0);
    }
}