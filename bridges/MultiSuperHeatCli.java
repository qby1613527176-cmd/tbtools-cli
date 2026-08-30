import biocjava.bioDoer.SimpleEfpBrowser.generateMultipleSuperHeatMap;
import jigplot.engine.JIGBasePanel;

import java.io.File;
import java.util.ArrayList;

/**
 * tbplot multiEfp — TBtools 多矩阵组织表达热图 CLI（engine 110，08/31 攻克）
 *
 * 用法: MultiSuperHeatCli <inTGA> <sample2cc> <expMat1.tsv[,expMat2.tsv,...]> <geneId> <out> [--imageWidth N] [--imageHeight N]
 *   inTGA: 底图（植物/组织示意图，必须 TrueColor RGB 非灰度）
 *   sample2cc: SampleName\tRGB 映射
 *   expMat(逗号分隔): 首列基因名 + 样本列，可多个矩阵叠加
 *   geneId: 要可视化的基因
 *   out: .svg/.pdf/.png
 *
 * 引擎: generateMultipleSuperHeatMap
 *   main() 硬编码了第二个矩阵路径（ExpressData1.txt）→ 不能直接用 main
 *   核心 API 完好：setter + private initExp()（反射）+ showHeatMapOf(geneId) → JIGBasePanel → save2SVG/PNG/PDF
 *   ⚠️ 需 fake DatatypeConverter（build/javax/xml/bind/，JDK9+ jaxb hack）
 */
public class MultiSuperHeatCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 5) {
            System.err.println("用法: MultiSuperHeatCli <inTGA> <sample2cc> <expMat1[,expMat2,...]> <geneId> <out> [--imageWidth N] [--imageHeight N]");
            System.exit(1);
        }
        String inTGA = args[0], sample2cc = args[1], expMats = args[2], geneId = args[3], outFile = args[4];
        int W = 0, H = 0;
        for (int i = 5; i < args.length; i++) {
            if (args[i].equals("--imageWidth") && i+1<args.length) W = Integer.parseInt(args[++i]);
            else if (args[i].equals("--imageHeight") && i+1<args.length) H = Integer.parseInt(args[++i]);
        }

        generateMultipleSuperHeatMap g = new generateMultipleSuperHeatMap();
        g.setInTGAFile(new File(inTGA));
        g.setSampleName2CodeFile(new File(sample2cc));
        ArrayList<File> mats = new ArrayList<>();
        for (String m : expMats.split(",")) {
            if (!m.trim().isEmpty()) mats.add(new File(m.trim()));
        }
        g.setExpressMatrixFileArr(mats);
        g.setOutImageFile(new File(outFile));
        if (W > 0) g.setImageWidth(W);
        if (H > 0) g.setImageHeight(H);

        // private initExp() → 反射
        java.lang.reflect.Method init = generateMultipleSuperHeatMap.class.getDeclaredMethod("initExp");
        init.setAccessible(true);
        init.invoke(g);

        JIGBasePanel panel = g.showHeatMapOf(geneId);
        if (panel == null) {
            System.err.println("错误: showHeatMapOf 返回 null（基因 " + geneId + " 是否在矩阵中？）");
            System.exit(1);
        }
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) panel.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) panel.save2PDF(new File(outFile));
        else panel.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }
}