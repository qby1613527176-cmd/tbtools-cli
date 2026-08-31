import biocjava.bioDoer.GXFUtils.GXFfilter;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.HashSet;

/**
 * tbcli gxffilter — GFF 按 ID 列表过滤 CLI（08/31 第八十六波，工具 96）
 *
 * 用法: GxfFilterCli <in.gff3|gtf> <idList.txt> <out.gff3|gtf>
 *   idList.txt: 每行一个基因/转录本 ID
 *
 * 引擎: GXFfilter.setInGXF/setIDList/setOutGXF + process()（main 硬编码演示 → setter+process）
 *   （保留 ID 列表中基因/转录本及其子特征的子注释——基因家族子注释提取刚需）
 */
public class GxfFilterCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: GxfFilterCli <in.gff3|gtf> <idList.txt> <out.gff3|gtf>");
            System.exit(1);
        }
        HashSet<String> ids = new HashSet<String>();
        BufferedReader br = new BufferedReader(new FileReader(new File(args[1])));
        String line;
        while ((line = br.readLine()) != null) {
            String t = line.trim();
            if (!t.isEmpty()) ids.add(t);
        }
        br.close();
        GXFfilter gf = new GXFfilter();
        gf.setInGXF(new File(args[0]));
        gf.setIDList(ids);
        gf.setOutGXF(new File(args[2]));
        gf.process();
        System.err.println("[tbplot] 已保存: " + args[2] + " (过滤 ID " + ids.size() + " 个)");
        System.exit(0);
    }
}