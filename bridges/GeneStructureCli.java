import biocjava.bioDoer.MEME.DrawMotifPattern.DrawGeneStructureFromGXFfile;
import biocjava.bioDoer.MEME.GeneStructure.ParseGeneStructureFromGXF;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.HashSet;

/**
 * tbplot genestructure — TBtools 基因结构图 CLI（08/29 重建）
 *
 * 用法: GeneStructureCli <input.gff> <idList.txt> <outFile> [genome.fa] [width] [height]
 *   input.gff: GFF/GXF 格式基因注释（含 mRNA 行）
 *   idList.txt: mRNA ID 列表（每行一个）
 *   genome.fa: 基因组序列（可选，用于显示 UTR 等）
 *   outFile: 输出 SVG/PNG
 *   width/height: 画布尺寸（默认 1200x600）
 *
 * 引擎: DrawGeneStructureFromGXFfile（继承 DrawMotifPatternFromMEMEResult）
 *   核心: ParseGeneStructureFromGXF.parse(GFF) + setRetainIDList + insertSeqFromGenome
 *   绘图: postGraph(null, basePanel) 返回 JIGSubPanel（第一参数 Newick 传 null 跳过）
 */
public class GeneStructureCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: GeneStructureCli <input.gff> <idList.txt> <outFile> [genome.fa] [width] [height]");
            System.exit(1);
        }
        String gffFile = args[0];
        String idFile = args[1];
        String outFile = args[2];
        File genomeFile = args.length > 3 ? new File(args[3]) : null;
        int width = args.length > 4 ? Integer.parseInt(args[4]) : 1200;
        int height = args.length > 5 ? Integer.parseInt(args[5]) : 600;

        // 读取 mRNA ID 列表
        HashSet<String> retainIds = new HashSet<String>();
        BufferedReader br = new BufferedReader(new FileReader(idFile));
        String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (!line.isEmpty() && !line.startsWith("#")) retainIds.add(line);
        }
        br.close();
        if (retainIds.isEmpty()) {
            System.err.println("错误: idList 为空");
            System.exit(1);
        }
        System.err.println("[tbplot] mRNA ID 数: " + retainIds.size());

        // 解析 GFF 构建基因结构
        DrawGeneStructureFromGXFfile drawer = new DrawGeneStructureFromGXFfile();
        ParseGeneStructureFromGXF parser = new ParseGeneStructureFromGXF();
        parser.setRetainIDList(retainIds);
        if (genomeFile != null && genomeFile.exists()) {
            parser.insertSeqFromGenome(genomeFile);
        }
        parser.parse(new File(gffFile));

        // 关键: 用 DrawGeneStructureFromGXFfile 的 field 来展示（通过继承的 postGraph）
        // DrawGeneStructureFromGXFfile 需要 setInFile(GFF) 供 metaParser 使用，
        // 但这里已直接用 ParseGeneStructureFromGXF；改用直接调用后者的数据结构
        drawer.setInFile(new File(gffFile));
        drawer.setMaxMotif(1000); // 避免 motif 过多弹窗
        if (genomeFile != null && genomeFile.exists()) drawer.setInGenomeSeqFile(genomeFile);

        // 用反射注入已解析的结构：DrawGeneStructureFromGXFfile 内部会重新 parse，
        // 因此直接使用其 metaParser + postGraph 流程
        JIGBasePanel base = new JIGBasePanel(width, height);
        JIGSubPanel panel = drawer.postGraph(null, base);
        if (panel == null) {
            System.err.println("错误: postGraph 返回 null");
            System.exit(1);
        }
        base.addSubPanel(panel);

        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) {
            base.save2PNG(new File(outFile));
        } else if (low.endsWith(".pdf")) {
            base.save2PDF(new File(outFile));
        } else {
            base.save2SVG(new File(outFile));
        }
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }
}