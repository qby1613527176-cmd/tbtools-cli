import JJpolt2.Example.DualSyntenyPlotterAdvance;
import jigplot.engine.JIGBasePanel;

import java.awt.Component;
import java.awt.Container;
import java.awt.Window;
import java.io.File;
import java.io.FileWriter;

/**
 * tbplot dualsyn — TBtools 双基因组共线性图 CLI（08/29 新增，第 32 引擎）
 *
 * 用法: DualSynCli <simplifiedGff> <collinearity> <out> [--chr1 "1,2,3"] [--chr2 "4,5,6"] [--rows N] [--gap N]
 *   simplifiedGff: Chr\tGeneName\tStart\tEnd（染色体名必须是数字！如 1/2/3，或 "1-1" 片段名）
 *   collinearity: MCScanX 输出（*.collinearity，染色体名含 "-" 取数字部分）
 *   --chr1/--chr2: ctl 里要显示的染色体名列表（逗号分隔，须在 GFF 中）
 *   --rows: ctl 第1行 int（默认 3）
 *   --gap: ctl 第2行 int（默认 3）
 *
 * 引擎: DualSyntenyPlotterAdvance（plot() 弹窗 → 窗口遍历保存）
 * ctl 格式（逆向）：第1行 int / 第2行 int / 第3行 染色体列表, / 第4行 染色体列表,
 */
public class DualSynCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: DualSynCli <simplifiedGff> <collinearity> <out> [--chr1 \"1,2\"] [--chr2 \"3,4\"] [--rows N] [--gap N]");
            System.exit(1);
        }
        String gffFile = args[0];
        String collinearFile = args[1];
        String outFile = args[2];
        String chr1 = null, chr2 = null;
        int rows = 3, gap = 3;
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--chr1") && i+1<args.length) chr1 = args[++i];
            else if (args[i].equals("--chr2") && i+1<args.length) chr2 = args[++i];
            else if (args[i].equals("--rows") && i+1<args.length) rows = Integer.parseInt(args[++i]);
            else if (args[i].equals("--gap") && i+1<args.length) gap = Integer.parseInt(args[++i]);
        }
        if (chr1 == null || chr2 == null) {
            System.err.println("错误: 必须提供 --chr1 和 --chr2（染色体名列表，逗号分隔，须在 GFF 中）");
            System.exit(1);
        }

        // 生成 ctl 文件
        File ctlFile = File.createTempFile("dualsyn", ".ctl");
        ctlFile.deleteOnExit();
        FileWriter fw = new FileWriter(ctlFile);
        fw.write(rows + "\n");
        fw.write(gap + "\n");
        fw.write(chr1 + "\n");
        fw.write(chr2 + "\n");
        fw.close();

        DualSyntenyPlotterAdvance dsp = new DualSyntenyPlotterAdvance();
        dsp.setCtlFile(ctlFile.getAbsolutePath());
        dsp.setCollinerFile(collinearFile);
        dsp.setInSimplifiedGff(gffFile);
        dsp.setGeneColorFile("");
        dsp.plot(); // 弹窗

        // 窗口遍历
        JIGBasePanel panel = null;
        Window[] windows = Window.getWindows();
        System.err.println("[tbplot] 窗口数: " + windows.length);
        for (Window w : windows) {
            JIGBasePanel found = findBasePanel(w);
            if (found != null) { panel = found; break; }
        }
        if (panel == null) {
            System.err.println("错误: 未找到 JIGBasePanel");
            System.exit(1);
        }
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) panel.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) panel.save2PDF(new File(outFile));
        else panel.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }

    static JIGBasePanel findBasePanel(Component c) {
        if (c instanceof JIGBasePanel) return (JIGBasePanel) c;
        if (c instanceof Container) {
            Component[] comps = ((Container) c).getComponents();
            for (Component comp : comps) {
                JIGBasePanel found = findBasePanel(comp);
                if (found != null) return found;
            }
        }
        return null;
    }
}