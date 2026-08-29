import java.io.BufferedReader;
import java.io.FileReader;

/**
 * tbplot mountain — TBtools RNA 山峰图数据 CLI（08/29，第 43 引擎）
 *
 * 用法: MountainPlotCli <fold.txt> <out.tsv>
 *   fold.txt: RNA 二级结构折叠字符串（() 和 . 表示），如 ".((((..))))"
 *   out.tsv: 每碱基位置的山峰高度（位置\t高度）
 *
 * 引擎: MountainPlot.process() 逻辑（fold 字符串→堆积高度）
 */
public class MountainPlotCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: MountainPlotCli <fold.txt> <out.tsv>");
            System.exit(1);
        }
        // 读 fold 字符串（第一行非空）
        BufferedReader br = new BufferedReader(new FileReader(args[0]));
        String line;
        String fold = null;
        while ((line = br.readLine()) != null) {
            String t = line.trim();
            if (!t.isEmpty() && !t.startsWith(">")) { fold = t; break; }
        }
        br.close();
        if (fold == null) { System.err.println("错误: 未找到 fold 字符串"); System.exit(1); }
        // 计算山峰高度（模仿 MountainPlot.process）
        StringBuilder sb = new StringBuilder();
        int cummuHeight = 0;
        for (int i = 0; i < fold.length(); i++) {
            char c = fold.charAt(i);
            if (c == '(') cummuHeight++;
            else if (c == ')') cummuHeight--;
            sb.append(i + 1).append('\t').append(cummuHeight).append('\n');
        }
        java.io.FileWriter fw = new java.io.FileWriter(args[1]);
        fw.write(sb.toString());
        fw.close();
        System.err.println("[tbplot] 已保存: " + args[1]);
        System.exit(0);
    }
}
