import biocjava.bioDoer.MEME.DrawMotifPattern.DrawMotifPatternFromMEMEResult;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;

/**
 * tbplot motif — TBtools Motif 分布图 CLI（08/29 重建）
 *
 * 用法: MotifCli <meme.xml> <idList.txt> <out.svg/png> [width] [height]
 *   meme.xml: MEME suite 输出（含 motif 定义）
 *   idList.txt: 序列 ID 列表（每行一个，指定画哪些序列）
 *   outFile: 输出 SVG/PNG
 *   width/height: 画布尺寸（默认 1200x600）
 *
 * 引擎: DrawMotifPatternFromMEMEResult
 *   关键: setMaxMotif 设大避免 isTooMuchMotif 弹窗（headless 卡死）
 *   postGraph(null, basePanel) 返回 JIGSubPanel（第一参数 Newick 传 null）
 */
public class MotifCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: MotifCli <meme.xml> <idList.txt> <outFile> [width] [height]");
            System.exit(1);
        }
        String memeFile = args[0];
        String idFile = args[1];
        String outFile = args[2];
        int width = args.length > 3 ? Integer.parseInt(args[3]) : 1200;
        int height = args.length > 4 ? Integer.parseInt(args[4]) : 600;

        // 读取 ID 列表
        ArrayList<String> idList = new ArrayList<String>();
        BufferedReader br = new BufferedReader(new FileReader(idFile));
        String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (!line.isEmpty() && !line.startsWith("#")) idList.add(line);
        }
        br.close();
        if (idList.isEmpty()) {
            System.err.println("警告: idList 为空，将绘制全部序列");
        }
        System.err.println("[tbplot] 目标序列数: " + idList.size());

        DrawMotifPatternFromMEMEResult drawer = new DrawMotifPatternFromMEMEResult();
        drawer.setInFile(new File(memeFile));
        drawer.setMaxMotif(10000); // 关键：设大避免 isTooMuchMotif → JOptionPane → headless 卡死
        if (!idList.isEmpty()) {
            drawer.setDefinedRankOrSubSet(idList);
        }

        JIGBasePanel base = new JIGBasePanel(width, height);
        JIGSubPanel panel = drawer.postGraph(null, base);
        if (panel == null) {
            System.err.println("错误: postGraph 返回 null");
            System.exit(1);
        }
        base.addSubPanel(panel);

        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) {
            base.save2PNG(new File(outFile));
        } else if (low.endsWith(".pdf")) {
            base.save2PDF(new File(outFile));
        } else {
            base.save2SVG(new File(outFile));
        }
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }
}
