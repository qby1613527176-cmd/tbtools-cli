import biocjava.bioDoer.JIGplotToolkit.Dist.Distance;
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;

/**
 * tbplot distance — TBtools 距离计算 CLI（08/29，第 42 引擎）
 *
 * 用法: DistanceCli <in.tsv> <col1> <col2> <method>
 *   in.tsv: tab 分隔表；col1/col2: 列索引（从 0 开始，取两列数值）
 *   method: euclidean|pearson|pearsonDist
 *   输出: 两列数值的距离/相关系数（所有行合并计算）
 *
 * 引擎: Distance 静态方法（getEuclideanDistance/getPearsonCorrelationCoefficient/getPearsonDistance）
 */
public class DistanceCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("用法: DistanceCli <in.tsv> <col1> <col2> <euclidean|pearson|pearsonDist>");
            System.exit(1);
        }
        String inFile = args[0];
        int c1 = Integer.parseInt(args[1]);
        int c2 = Integer.parseInt(args[2]);
        String method = args[3];
        ArrayList<Double> v1 = new ArrayList<>(), v2 = new ArrayList<>();
        BufferedReader br = new BufferedReader(new FileReader(inFile));
        String line;
        while ((line = br.readLine()) != null) {
            if (line.startsWith("#")) continue;
            String[] cols = line.split("\t");
            if (cols.length <= Math.max(c1, c2)) continue;
            try {
                v1.add(Double.parseDouble(cols[c1]));
                v2.add(Double.parseDouble(cols[c2]));
            } catch (NumberFormatException e) { /* skip non-numeric */ }
        }
        br.close();
        if (v1.size() != v2.size() || v1.isEmpty()) {
            System.err.println("错误: 两列数值数量不一致或为空 (" + v1.size() + " vs " + v2.size() + ")");
            System.exit(1);
        }
        double result;
        switch (method) {
            case "euclidean": result = Distance.getEuclideanDistance(v1, v2); break;
            case "pearson": result = Distance.getPearsonCorrelationCoefficient(v1, v2); break;
            case "pearsonDist": result = Distance.getPearsonDistance(v1, v2); break;
            default: System.err.println("未知方法: " + method); System.exit(1); return;
        }
        System.out.println(method + "\t" + result);
        System.exit(0);
    }
}
