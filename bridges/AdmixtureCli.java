import biocjava.bioDoer.JIGplotToolkit.PopulationGenetics.AdmixtureQmatViz;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;

/**
 * tbplot admixture — TBtools ADMIXTURE Q 矩阵堆叠图 CLI（08/29 重建）
 *
 * 用法: AdmixtureCli <qFiles.lst> <out> [sampleIDFile] [groupFile] [sortMode] [width] [height] [panelInterval]
 *   qFiles.lst: 每行一个 Q 矩阵文件路径（ADMIXTURE 输出 *.Q，如 K=2、K=3）
 *   sampleIDFile: 样本 ID 文件（每行一个，与 Q 矩阵行对应）
 *   groupFile: 分组文件（可选）
 *   sortMode: Qraito|Lexical|None（默认 None）
 *
 * 引擎: AdmixtureQmatViz
 *   process(File[]) 返回 JIGSubPanel[]（每个 Q 文件一个面板）→ save2Graph
 */
public class AdmixtureCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: AdmixtureCli <qFiles.lst> <out> [sampleIDFile] [groupFile] [sortMode] [width] [height] [panelInterval]");
            System.exit(1);
        }
        String lstFile = args[0];
        String outFile = args[1];
        File sampleIDFile = args.length > 2 && !args[2].equals("-") ? new File(args[2]) : null;
        File groupFile = args.length > 3 && !args[3].equals("-") ? new File(args[3]) : null;
        String sortMode = args.length > 4 ? args[4] : "None";
        int width = args.length > 5 ? Integer.parseInt(args[5]) : 1200;
        int height = args.length > 6 ? Integer.parseInt(args[6]) : 600;
        int interval = args.length > 7 ? Integer.parseInt(args[7]) : 120;

        // 读 qFiles.lst
        ArrayList<String> qFiles = new ArrayList<String>();
        BufferedReader br = new BufferedReader(new FileReader(lstFile));
        String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (!line.isEmpty() && !line.startsWith("#")) qFiles.add(line);
        }
        br.close();
        if (qFiles.isEmpty()) {
            System.err.println("错误: qFiles.lst 为空");
            System.exit(1);
        }
        File[] qFileArr = new File[qFiles.size()];
        for (int i = 0; i < qFiles.size(); i++) qFileArr[i] = new File(qFiles.get(i));
        System.err.println("[tbplot] Q 文件数: " + qFiles.size());

        AdmixtureQmatViz viz = new AdmixtureQmatViz();
        viz.setSortMode(AdmixtureQmatViz.SortMode.valueOf(sortMode));
        viz.setWidth(width);
        viz.setHeight(height);
        viz.setPanelInterval(interval);
        if (sampleIDFile != null && sampleIDFile.exists()) viz.setSampleIDFile(sampleIDFile);
        if (groupFile != null && groupFile.exists()) viz.setInGroupFile(groupFile);

        JIGSubPanel[] panels = viz.process(qFileArr);
        JIGBasePanel base = new JIGBasePanel(width, height * panels.length + interval * (panels.length - 1));
        for (JIGSubPanel p : panels) base.addSubPanel(p);
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) base.save2PDF(new File(outFile));
        else base.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile + " (" + panels.length + " 面板)");
        System.exit(0);
    }
}