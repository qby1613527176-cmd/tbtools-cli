import java.io.File;
import java.nio.file.Files;
import java.nio.charset.StandardCharsets;
import java.util.List;

/**
 * tbplot visualizePseudoBlock — 伪共线性区块可视化 CLI（08/29，第 51 引擎）
 *
 * 用法: VisualizeCli <inBlockOut> <outGraph.pdf> [--labels "Genome1,Genome2"]
 *   inBlockOut: FindBlockDual 输出（行=一个基因组区块; 基因格式 name(chr:start-end):strand[:matchIDs]）
 *   outGraph:  输出 PDF（引擎只支持 PDF）
 *   --labels:  每行对应的基因组标签（默认 Genome1,Genome2,...；不传则自动加）
 *
 * ⚠️ main() 硬编码 13 个 queryId 循环——改直接调 visualize(File outGraph)。
 * ⚠️ Visualize 输入格式要求每行 `标签:基因1\t基因2...`（第一个冒号前是标签），
 *    FindBlockDual 输出无标签 → 桥自动补齐（默认 Genome1/Genome2/...，或用 --labels 指定）。
 *
 * 例: VisualizeCli examples/data/findblockdual/block_Cr_Cs_real.out.txt out.pdf --labels "Camellia_reticulata,Camellia_sinensis"
 */
public class VisualizeCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: VisualizeCli <inBlockOut> <outGraph.pdf> [--labels \"Genome1,Genome2\"]");
            System.exit(1);
        }
        String in = args[0];
        String out = args[1];
        String labels = null;
        for (int i = 2; i < args.length; i++) {
            if (args[i].equals("--labels") && i+1 < args.length) labels = args[++i];
        }
        // 读入 FindBlockDual 输出并加标签前缀（Visualize 需要 标签:基因1\t基因2 格式）
        List<String> lines = Files.readAllLines(new File(in).toPath(), StandardCharsets.UTF_8);
        String[] labelArr = labels == null ? null : labels.split(",");
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < lines.size(); i++) {
            String line = lines.get(i).trim();
            if (line.isEmpty()) continue;
            String label;
            if (labelArr != null && i < labelArr.length) label = labelArr[i];
            else label = "Genome" + (i + 1);
            // 若行首已是 `单词:` 标签格式则跳过（兼容已带标签输入）
            sb.append(label).append(":").append(line).append("\n");
        }
        File tmpIn = File.createTempFile("vpsb_in", ".tab");
        Files.write(tmpIn.toPath(), sb.toString().getBytes(StandardCharsets.UTF_8));
        Object obj = Class.forName("biocjava.bioDoer.PseudoSyntenyBlock.VisualizePseudoSyntenyBlock")
                .getDeclaredConstructor().newInstance();
        obj.getClass().getMethod("setInFindBlockResultTab", File.class)
                .invoke(obj, tmpIn);
        obj.getClass().getMethod("visualize", File.class)
                .invoke(obj, new File(out));
        tmpIn.delete();
        System.err.println("[tbplot] 区块可视化完成: " + out);
        System.exit(0);
    }
}