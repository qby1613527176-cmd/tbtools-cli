import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.File;
import java.lang.reflect.Method;

/**
 * tbplot admixtureViz — ADMIXTURE Q 矩阵可视化 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: AdmixtureCli <q1.txt> <q2.txt> [<q3.txt>...] <out.svg> [--id <samples.txt>]
 *        [--group <group.txt>] [--sort Qraito|Lexical|None] [--width N] [--height N] [--interval N]
 *
 * 接口来源：反编译 AdmixtureVizGUIPanel（GUI 真实调用链）：
 *   AdmixtureQmatViz aqv = new AdmixtureQmatViz();
 *   aqv.setSampleIDFile/setInGroupFile/setSortMode/setWidth/setHeight/setPanelInterval;
 *   JIGUtils.quickShow(aqv.process(fileArr));
 * 规避：直调 process(File[])（返回 JIGSubPanel）→ JIGBasePanel.save2*。
 *
 * 输入：ADMIIX 输出的 Q 矩阵（每行=样本，每列=群体占比）+ 可选样本 ID 文件
 *   （旧格式每行 sampleId+数值；新 Q 文件无 ID 列时用 --id）与群体分组文件。
 */
public class AdmixtureCli {
    public static void main(String[] args) throws Exception {
        java.util.ArrayList<String> pos = new java.util.ArrayList<String>();
        String idFile = null, groupFile = null, sort = "Qraito";
        int width = 800, height = 600, interval = 0;
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--id") && i+1 < args.length) idFile = args[++i];
            else if (args[i].equals("--group") && i+1 < args.length) groupFile = args[++i];
            else if (args[i].equals("--sort") && i+1 < args.length) sort = args[++i];
            else if (args[i].equals("--width") && i+1 < args.length) width = Integer.parseInt(args[++i]);
            else if (args[i].equals("--height") && i+1 < args.length) height = Integer.parseInt(args[++i]);
            else if (args[i].equals("--interval") && i+1 < args.length) interval = Integer.parseInt(args[++i]);
            else pos.add(args[i]);
        }
        if (pos.size() < 2) {
            System.err.println("用法: AdmixtureCli <q1.txt> <q2.txt> [<q3.txt>...] <out.svg> [--id samples.txt] [--group group.txt] [--sort Qraito|Lexical|None]");
            System.exit(1);
        }
        String outPath = pos.remove(pos.size() - 1);
        // 支持两种输入：直接 Q 文件 / *.lst 清单（每行一个 Q 文件路径，GUI 传统格式）
        java.util.ArrayList<File> qList = new java.util.ArrayList<File>();
        for (String fp : pos) {
            File f = new File(fp);
            if (f.getName().toLowerCase().endsWith(".lst")) {
                java.io.BufferedReader br = new java.io.BufferedReader(new java.io.FileReader(f));
                String line;
                while ((line = br.readLine()) != null) {
                    String t = line.trim();
                    if (!t.isEmpty()) qList.add(new File(t));
                }
                br.close();
            } else {
                qList.add(f);
            }
        }
        File[] qFiles = qList.toArray(new File[0]);

        Object aqv = Class.forName("biocjava.bioDoer.JIGplotToolkit.PopulationGenetics.AdmixtureQmatViz")
                .getDeclaredConstructor().newInstance();
        Class<?> c = aqv.getClass();
        if (idFile != null) c.getMethod("setSampleIDFile", File.class).invoke(aqv, new File(idFile));
        if (groupFile != null) c.getMethod("setInGroupFile", File.class).invoke(aqv, new File(groupFile));
        Class<?> sm = Class.forName("biocjava.bioDoer.JIGplotToolkit.PopulationGenetics.AdmixtureQmatViz$SortMode");
        c.getMethod("setSortMode", sm).invoke(aqv, Enum.valueOf((Class)sm, sort));
        c.getMethod("setWidth", int.class).invoke(aqv, width);
        c.getMethod("setHeight", int.class).invoke(aqv, height);
        c.getMethod("setPanelInterval", int.class).invoke(aqv, interval);
        Object result = c.getMethod("process", File[].class).invoke(aqv, (Object) qFiles);
        JIGSubPanel[] panels;
        if (result instanceof JIGSubPanel[]) {
            panels = (JIGSubPanel[]) result;
        } else if (result instanceof JIGSubPanel) {
            panels = new JIGSubPanel[]{ (JIGSubPanel) result };
        } else {
            System.err.println("❌ process 未返回 JIGSubPanel/JIGSubPanel[]");
            System.exit(1);
            panels = new JIGSubPanel[0];
        }
        JIGBasePanel base = new JIGBasePanel(width, height);
        for (JIGSubPanel p : panels) base.addSubPanel(p);
        System.err.println("[tbplot] " + panels.length + " 个 Q 面板");
        File outf = new File(outPath);
        String low = outPath.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(outf);
        else if (low.endsWith(".pdf")) base.save2PDF(outf);
        else base.save2SVG(outf);
        System.err.println("[tbplot] 已保存: " + outPath);
        System.exit(0);
    }
}