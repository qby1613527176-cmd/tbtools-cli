import biocjava.bioIO.BioSoftPipeServer.PlantCAREResult.PlantCAREResultClassify;

import java.io.File;

/**
 * tbplot careclassify — PlantCARE 顺式元件结果分类 CLI（GUI 逆向 #22，09/20）
 *
 * 用法: PlantCAREResultClassifyCli <plantcare.tab> <out.xls>
 *   in:  PlantCARE 网站输出 .tab（第 8 列 = motif/site 名）
 *   out: 原行 + 追加「大类\t亚类」两列（如 TF\tMYB Binding Site）
 *
 * 引擎: PlantCAREResultClassify（GUI 逆向：PlantCAREResultClassifyGUIPanel $1
 *   → setInPlantCAREResultFile/setOutClassifyFile/process，main() 硬编码路径）
 * 原理: jar 内置 97 类分类表（Phytohormone/Environment/Tissue/TF/Common），
 *   按第 8 列 motif 名查表追加；查不到填 NA\tNA
 */
public class PlantCAREResultClassifyCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: PlantCAREResultClassifyCli <plantcare.tab> <out.xls>");
            System.exit(1);
        }
        File inFile = new File(args[0]);
        File outFile = new File(args[1]);
        if (!inFile.exists()) {
            System.err.println("错误: 输入文件不存在: " + inFile.getAbsolutePath());
            System.exit(2);
        }
        PlantCAREResultClassify pcrc = new PlantCAREResultClassify();
        pcrc.setInPlantCAREResultFile(inFile);
        pcrc.setOutClassifyFile(outFile);
        pcrc.process();
        System.err.println("[tbplot] PlantCARE 分类完成: " + outFile.getAbsolutePath());
        System.exit(0);
    }
}
