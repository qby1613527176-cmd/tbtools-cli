import biocjava.bioDoer.JIGplotToolkit.Synteny.SeveralSpeciesMicroSyntenicAnalysisAdvance;
import jigplot.engine.JIGBasePanel;

import java.awt.Component;
import java.awt.Container;
import java.awt.Window;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.LinkedHashSet;

/**
 * tbplot multisyn — TBtools 多物种微共线性分析图 CLI（08/29 新增，第 33 引擎）
 *
 * 用法: SeveralSpeciesCli <gxf.lst> <collinear.lst> <out> [--genes idlist.txt]
 *   gxf.lst: 每行一个 GXF/GFF 注释文件路径
 *   collinear.lst: 每行一个 MCScanX collinearity 文件路径（与 GXF 对应配对）
 *   --genes: 高亮基因 ID 列表（可选）
 *
 * 引擎: SeveralSpeciesMicroSyntenicAnalysisAdvance
 *   setGxfArr(ArrayList<File>) + setCollinearFileArr + setSpecificGenesList
 *   process() 内部用 JIG 引擎（JIGBasePanel）→ 窗口遍历保存
 */
public class SeveralSpeciesCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: SeveralSpeciesCli <gxf.lst> <collinear.lst> <out> [--genes idlist.txt]");
            System.exit(1);
        }
        String gxfLst = args[0];
        String collinearLst = args[1];
        String outFile = args[2];
        String genesFile = null;
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--genes") && i+1<args.length) genesFile = args[++i];
        }

        // 读 GXF 列表
        ArrayList<File> gxfArr = new ArrayList<File>();
        BufferedReader br = new BufferedReader(new FileReader(gxfLst));
        String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (!line.isEmpty() && !line.startsWith("#")) gxfArr.add(new File(line));
        }
        br.close();
        System.err.println("[tbplot] GXF 数: " + gxfArr.size());

        // 读 collinearity 列表
        ArrayList<File> collinearArr = new ArrayList<File>();
        br = new BufferedReader(new FileReader(collinearLst));
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (!line.isEmpty() && !line.startsWith("#")) collinearArr.add(new File(line));
        }
        br.close();
        System.err.println("[tbplot] collinearity 数: " + collinearArr.size());

        SeveralSpeciesMicroSyntenicAnalysisAdvance engine = new SeveralSpeciesMicroSyntenicAnalysisAdvance();
        engine.setGxfArr(gxfArr);
        engine.setCollinearFileArr(collinearArr);
        // specificGenesList 是必需（process() 检查 isEmpty）——无 --genes 时从第一个 GXF 提取所有基因
        LinkedHashSet<String> genes = new LinkedHashSet<String>();
        if (genesFile != null) {
            br = new BufferedReader(new FileReader(genesFile));
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (!line.isEmpty() && !line.startsWith("#")) genes.add(line);
            }
            br.close();
        } else {
            // 自动从第一个 GXF 提取所有 mRNA 基因名
            BufferedReader gxfr = new BufferedReader(new FileReader(gxfArr.get(0)));
            while ((line = gxfr.readLine()) != null) {
                if (line.startsWith("#")) continue;
                String[] f = line.split("\t");
                if (f.length >= 9 && (f[2].equals("mRNA") || f[2].equals("transcript"))) {
                    String id = extractAttr(f[8], "ID");
                    if (id != null) genes.add(id);
                }
            }
            gxfr.close();
            System.err.println("[tbplot] 自动提取基因数: " + genes.size());
        }
        engine.setSpecificGenesList(genes);
        System.err.println("[tbplot] 高亮基因: " + genes.size());
        engine.process(); // 内部 JIGBasePanel 弹窗

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
        // 多物种引擎内部 panel 可能未设置尺寸 → 保存前显式设置（避免 BufferedImage 0 尺寸崩溃）
        panel.setSize(new java.awt.Dimension(1600, 1200));
        panel.setPreferredSize(new java.awt.Dimension(1600, 1200));
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

    static String extractAttr(String attrs, String key) {
        for (String part : attrs.split(";")) {
            String[] kv = part.trim().split("=", 2);
            if (kv.length == 2 && kv[0].equals(key)) return kv[1].trim();
        }
        return null;
    }
}