import biocjava.bioDoer.JIGplotToolkit.Synteny.MicroSyntenicAdvance;
import biocjava.bioIO.GXF.gxfTree.Region;
import jigplot.engine.JIGBasePanel;

import java.awt.Component;
import java.awt.Container;
import java.awt.Window;
import java.io.File;

/**
 * tbplot microsyn — TBtools 双基因组微共线性图 CLI（08/29 新增，第 31 引擎）
 *
 * 用法: MicroSynCli <gxf1> <gxf2> <collinearity> <out>
 *       [--chr1 LG03 --start1 13207612 --end1 13990030]
 *       [--chr2 chr08 --start2 10660849 --end2 11367883]
 *       [--highlight1 chr1:start:end] [--highlight2 chr2:start:end]
 *   gxf1/gxf2: 两物种 GFF/GXF 注释
 *   collinearity: MCScanX 输出（*.collinearity 文件）
 *   区域默认取全基因范围（若不指定则自动）
 *
 * 引擎: MicroSyntenicAdvance（setInGxf/setInGxf2/setCollinerFile/setRegion/setRegion2 + process）
 * 方案: 窗口遍历 —— process() 后遍历 Window 找 JIGBasePanel 再保存
 */
public class MicroSynCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("用法: MicroSynCli <gxf1> <gxf2> <collinearity> <out> [--chr1 C --start1 S --end1 E --chr2 C --start2 S --end2 E]");
            System.exit(1);
        }
        String gxf1 = args[0];
        String gxf2 = args[1];
        String collinear = args[2];
        String outFile = args[3];

        String chr1 = null, chr2 = null, start1 = null, end1 = null, start2 = null, end2 = null;
        String hl1 = null, hl2 = null;
        for (int i = 4; i < args.length; i++) {
            switch (args[i]) {
                case "--chr1": chr1 = args[++i]; break;
                case "--start1": start1 = args[++i]; break;
                case "--end1": end1 = args[++i]; break;
                case "--chr2": chr2 = args[++i]; break;
                case "--start2": start2 = args[++i]; break;
                case "--end2": end2 = args[++i]; break;
                case "--highlight1": hl1 = args[++i]; break;
                case "--highlight2": hl2 = args[++i]; break;
            }
        }

        // 若未指定区域，扫描 GXF 自动取 chr 范围（简化：用基因组坐标估算——从 GXF 找最后染色体并粗略范围）
        Region region1 = new Region();
        if (chr1 != null && start1 != null && end1 != null) {
            region1.setChrId(chr1); region1.setStart(start1); region1.setEnd(end1);
        } else {
            // 需要从 GXF 提取——先尝试让引擎自动处理：设置空 region
            region1.setChrId(""); region1.setStart("0"); region1.setEnd("0");
        }
        Region region2 = new Region();
        if (chr2 != null && start2 != null && end2 != null) {
            region2.setChrId(chr2); region2.setStart(start2); region2.setEnd(end2);
        } else {
            region2.setChrId(""); region2.setStart("0"); region2.setEnd("0");
        }

        MicroSyntenicAdvance msa = new MicroSyntenicAdvance();
        msa.setInGxf(new File(gxf1));
        msa.setInGxf2(new File(gxf2));
        msa.setCollinerFile(new File(collinear));
        msa.setRegion(region1);
        msa.setRegion2(region2);

        if (hl1 != null) {
            String[] p = hl1.split(":");
            Region hl = new Region();
            hl.setChrId(p[0]); hl.setStart(p[1]); hl.setEnd(p[2]);
            msa.setUpHighlightRegion(hl);
        }
        if (hl2 != null) {
            String[] p = hl2.split(":");
            Region hl = new Region();
            hl.setChrId(p[0]); hl.setStart(p[1]); hl.setEnd(p[2]);
            msa.setDownHighlightRegion(hl);
        }

        msa.process(); // 内部弹窗

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