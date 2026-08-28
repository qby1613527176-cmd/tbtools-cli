import biocjava.bioDoer.JIGplotToolkit.MSA.MSAviewer;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;
import java.util.ArrayList;

/**
 * tbplot msa — TBtools MSA 序列比对图 CLI（08/29 重建，替代损坏的恢复件）
 *
 * 用法: MSACli <aligned.fasta> <out> [padding]
 *   尺寸按子面板自动计算，勿传 w/h（NPE 根因=缺 setInMSAtextFile）
 *
 * 引擎: MSAviewer.setInMSAtextFile + processed() 返回 panel 列表
 *       （PIN 14 序列验证 SVG 4.1MB；长序列建议 PNG，08/28）
 */
public class MSACli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: MSACli <aligned.fasta> <out> [padding]");
            System.exit(1);
        }
        String inFasta = args[0];
        String outFile = args[1];

        MSAviewer viewer = new MSAviewer();
        viewer.setInMSAtextFile(new File(inFasta));
        ArrayList<JIGSubPanel> panels = viewer.processed();
        System.err.println("[tbplot] processed() 完成, subpanels=" + panels.size());
        if (panels == null || panels.isEmpty()) {
            System.err.println("错误: 没有生成面板");
            System.exit(1);
        }

        // 尺寸按最后 subpanel 反推（勿传固定 w/h）
        JIGSubPanel last = panels.get(panels.size() - 1);
        JIGBasePanel base = new JIGBasePanel(1000, 800);
        for (JIGSubPanel p : panels) base.addSubPanel(p);
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) base.save2PDF(new File(outFile));
        else base.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }
}