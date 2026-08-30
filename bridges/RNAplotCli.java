import biocjava.bioDoer.JIGplotToolkit.miRCoverage.RNAplotAdvance;
import biocjava.bioIO.RNAfold.FoldInfo;
import biocjava.bioIO.RNAfold.RNAfoldInvoker;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.awt.geom.Point2D;
import java.io.File;
import java.io.FileWriter;
import java.util.ArrayList;

/**
 * tbplot rnaplot — TBtools RNA 二级结构绘图 CLI（engine 111，08/31 攻克）
 *
 * 用法: RNAplotCli <seq.fa|rawSeq> <out> [--colorMap "seq1=R,G,B;seq2=R,G,B"] [--interactive false]
 *   seq: FASTA 或单行序列
 *   out: .svg/.pdf/.png
 *
 * 引擎: RNAplotAdvance（需要 RNAfold/RNAplot 可执行）
 *   main() 用 RNAplotInvoker.generatePlotPsFile 管道调 RNAplot → 本机 RNAplot 2.7 不读 stdin 管道，
 *   导致 temp PS 文件不生成 → FileNotFoundException
 * 破解: 绕开 generatePlotPsFile——
 *   1) RNAfoldInvoker.fold(seq) 拿 FoldInfo（seq+structure+mfe）
 *   2) 写 temp.fa（>seq + seq + structure(mfe)）→ 本机 RNAplot -i 生成 EPS（含 /sequence /coor /pairs）
 *   3) RNAplotAdvance.transform(EPS, interactive) → JIGSubPanel
 *   4) JIGBasePanel + addSubPanel + save2SVG/PNG/PDF
 */
public class RNAplotCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: RNAplotCli <seq.fa|rawSeq> <out> [--colorMap \"seq1=R,G,B;...\"] [--interactive false]");
            System.exit(1);
        }
        String inSeq = args[0];
        String outFile = args[1];
        String colorMap = null;
        boolean interactive = false;
        for (int i = 2; i < args.length; i++) {
            if (args[i].equals("--colorMap") && i+1<args.length) colorMap = args[++i];
            else if (args[i].equals("--interactive") && i+1<args.length) interactive = Boolean.parseBoolean(args[++i]);
        }

        // 1. 读序列
        String seq = inSeq;
        if (new File(inSeq).exists()) {
            StringBuilder sb = new StringBuilder();
            for (String l : java.nio.file.Files.readAllLines(new File(inSeq).toPath())) {
                if (l.startsWith(">")) continue;
                sb.append(l.trim());
            }
            seq = sb.toString();
        }
        seq = seq.replaceAll("[^ACGUacguTt]", "").toUpperCase().replace('T','U');
        if (seq.isEmpty()) {
            System.err.println("错误: 序列为空");
            System.exit(1);
        }

        // 2. RNAfold 折叠
        FoldInfo fi = RNAfoldInvoker.fold(seq);
        System.err.println("[tbplot] 折叠完成: mfe=" + fi.getMfe() + " len=" + fi.getInpuSeq().length());

        // 3. 写 temp.fa → RNAplot -i 生成 EPS
        File fa = File.createTempFile("rnaplot", ".fa");
        FileWriter fw = new FileWriter(fa);
        fw.write(">seq\n" + fi.getInpuSeq() + "\n" + fi.getFoldStructure() + " (" + String.format("%.1f", fi.getMfe()) + ")\n");
        fw.close();
        String workDir = fa.getParent();
        String epsPrefix = workDir + File.separator + "seq_ss";
        ProcessBuilder pb = new ProcessBuilder("RNAplot", "-i", fa.getAbsolutePath());
        pb.directory(new File(workDir));
        pb.redirectErrorStream(true);
        Process p = pb.start();
        p.waitFor();
        // RNAplot 输出 <name>_ss.eps
        File eps = new File(epsPrefix + ".eps");
        if (!eps.exists()) {
            // 兜底：找目录里任何 *_ss.eps
            File dir = new File(workDir);
            for (File f : dir.listFiles()) {
                if (f.getName().endsWith("_ss.eps") || f.getName().endsWith("_ss.ps")) { eps = f; break; }
            }
        }
        if (!eps.exists()) {
            System.err.println("错误: RNAplot 未生成 EPS（工作目录=" + workDir + "）");
            System.exit(1);
        }
        System.err.println("[tbplot] RNAplot EPS: " + eps.getAbsolutePath());

        // 4. transformat 解析
        RNAplotAdvance ra = new RNAplotAdvance();
        ra.setIsInteractive(interactive);
        JIGSubPanel sub = ra.transformat(eps, interactive);

        // 5. JIGBasePanel + addSubPanel
        Point2D[] pts = sub.getPoints();
        double minX = Double.MAX_VALUE, minY = Double.MAX_VALUE, maxX = -Double.MAX_VALUE, maxY = -Double.MAX_VALUE;
        if (pts != null) {
            for (Point2D pt : pts) {
                minX = Math.min(minX, pt.getX()); minY = Math.min(minY, pt.getY());
                maxX = Math.max(maxX, pt.getX()); maxY = Math.max(maxY, pt.getY());
            }
        }
        int w = (int)(maxX - minX) + 200, h = (int)(maxY - minY) + 200;
        if (w < 600) w = 600;
        if (h < 400) h = 400;
        JIGBasePanel base = new JIGBasePanel(w, h);
        base.addSubPanel(sub);

        // 6. colorMap 高亮（元素引用 subpanel 内部，直接改色即可）
        if (colorMap != null && !colorMap.isEmpty()) {
            ArrayList<jigplot.engine.JIGElement> els = ra.selectEle(colorMap);
            if (els != null) {
                for (jigplot.engine.JIGElement el : els) {
                    // 用 colorMap 解析颜色：引擎内部 selectEle 已按 colorMap 上色，这里仅确保刷新
                }
            }
            base.repaint();
        }

        // 7. 保存
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) base.save2PDF(new File(outFile));
        else base.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }
}