import biocjava.bioDoer.JIGplotToolkit.GeneLocation.GeneLocation;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.TreeMap;

/**
 * tbplot genelocgff — TBtools 基因染色体定位图（GFF+ID 输入）CLI（08/29 重建）
 *
 * 用法: GeneLocGffCli <gff3> <idList> <out> [--chrLen len.tsv] [--rename r.tsv] [--pairs p.tsv] [--color c.tsv]
 *                     [--rankedChr list] [--onlyMapped true|false] [--showLabel true|false]
 *
 * 方案: 绕开 GeneLocationControlFromGff3AndIdList.process() 的 JFrame
 *   复制核心逻辑: 解析 GFF（mRNA/gene 行）→ 生成 genePos 文件（featureName\tchrName\tstartPos\tendPos）
 *               + genomeLen 文件（chr\tlength）→ GeneLocation.plot() → save2Graph
 *   参考 08/28 原 GeneLocGffCli（GRAS 75 基因/15 染色体验证 SVG 108KB）
 */
public class GeneLocGffCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: GeneLocGffCli <gff3> <idList> <out> [--chrLen len.tsv] [--rename r.tsv] [--pairs p.tsv] [--color c.tsv] [--rankedChr list] [--onlyMapped bool] [--showLabel bool]");
            System.exit(1);
        }
        String gffFile = args[0];
        String idFile = args[1];
        String outFile = args[2];

        File chrLenFile = null, renameFile = null, pairsFile = null, colorFile = null, rankedChrFile = null;
        boolean onlyMapped = false, showLabel = true;
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--chrLen") && i+1<args.length) chrLenFile = new File(args[++i]);
            else if (args[i].equals("--rename") && i+1<args.length) renameFile = new File(args[++i]);
            else if (args[i].equals("--pairs") && i+1<args.length) pairsFile = new File(args[++i]);
            else if (args[i].equals("--color") && i+1<args.length) colorFile = new File(args[++i]);
            else if (args[i].equals("--rankedChr") && i+1<args.length) rankedChrFile = new File(args[++i]);
            else if (args[i].equals("--onlyMapped") && i+1<args.length) onlyMapped = Boolean.parseBoolean(args[++i]);
            else if (args[i].equals("--showLabel") && i+1<args.length) showLabel = Boolean.parseBoolean(args[++i]);
        }

        // 读 ID 列表
        HashSet<String> retainIds = new HashSet<String>();
        BufferedReader br = new BufferedReader(new FileReader(idFile));
        String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (!line.isEmpty() && !line.startsWith("#")) retainIds.add(line);
        }
        br.close();
        System.err.println("[tbplot] 目标 ID 数: " + retainIds.size());

        // 解析 GFF：收集 mRNA/transcript 行 (chr, start, end, id)
        ArrayList<String[]> genes = new ArrayList<String[]>(); // {id, chr, start, end}
        HashMap<String, Long> chrMax = new HashMap<String, Long>();
        br = new BufferedReader(new FileReader(gffFile));
        while ((line = br.readLine()) != null) {
            if (line.startsWith("#")) continue;
            String[] f = line.split("\t");
            if (f.length < 9) continue;
            String type = f[2];
            if (!type.equals("mRNA") && !type.equals("transcript") && !type.equals("gene")) continue;
            String chr = f[0];
            long start = Long.parseLong(f[3]);
            long end = Long.parseLong(f[4]);
            // 提取 ID
            String attrs = f[8];
            String id = extractAttr(attrs, "ID");
            if (id == null) continue;
            if (!retainIds.isEmpty() && !retainIds.contains(id)) continue;
            genes.add(new String[]{id, chr, String.valueOf(start), String.valueOf(end)});
            Long cm = chrMax.get(chr);
            if (cm == null || end > cm) chrMax.put(chr, end);
        }
        br.close();
        if (genes.isEmpty()) {
            System.err.println("错误: 没有匹配到任何基因（检查 ID 是否与 GFF 的 mRNA ID 一致）");
            System.exit(1);
        }
        System.err.println("[tbplot] 匹配基因: " + genes.size() + ", 染色体: " + chrMax.size());

        // 生成临时 genePos 文件
        File genePosFile = File.createTempFile("tbplot_genePos", ".txt");
        genePosFile.deleteOnExit();
        BufferedWriter bw = new BufferedWriter(new FileWriter(genePosFile));
        for (String[] g : genes) {
            bw.write(g[0] + "\t" + g[1] + "\t" + g[2] + "\t" + g[3]);
            bw.newLine();
        }
        bw.close();

        // 生成 genomeLen 文件（未提供则从 GFF 推）
        File genomeLenFile;
        if (chrLenFile != null && chrLenFile.exists()) {
            genomeLenFile = chrLenFile;
        } else {
            genomeLenFile = File.createTempFile("tbplot_genomeLen", ".txt");
            genomeLenFile.deleteOnExit();
            bw = new BufferedWriter(new FileWriter(genomeLenFile));
            for (String chr : chrMax.keySet()) {
                bw.write(chr + "\t" + chrMax.get(chr));
                bw.newLine();
            }
            bw.close();
        }

        // GeneLocation.plot()
        GeneLocation gl = new GeneLocation();
        gl.setInGenePosFile(genePosFile);
        gl.setInGenomeLen(genomeLenFile);
        if (pairsFile != null && pairsFile.exists()) gl.setGenePairinfo(pairsFile);
        if (colorFile != null && colorFile.exists()) gl.setGeneColorMapInfo(colorFile);
        gl.setShowGeneLabel(showLabel);

        JIGSubPanel panel = gl.plot();
        JIGBasePanel base = new JIGBasePanel(1000, 800);
        base.addSubPanel(panel);
        String low = outFile.toLowerCase();
        if (low.endsWith(".png")) base.save2PNG(new File(outFile));
        else if (low.endsWith(".pdf")) base.save2PDF(new File(outFile));
        else base.save2SVG(new File(outFile));
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }

    static String extractAttr(String attrs, String key) {
        // 解析 GFF9 属性列: key=value;key2=value2
        for (String part : attrs.split(";")) {
            String[] kv = part.trim().split("=", 2);
            if (kv.length == 2 && kv[0].equals(key)) return kv[1].trim();
        }
        return null;
    }
}
