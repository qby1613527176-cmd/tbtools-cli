import biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.venn6.Venn6;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashSet;

/**
 * tbplot venn6 — TBtools 六集合韦恩图 CLI（08/29 新增，第 30 引擎）
 *
 * 用法: Venn6Cli <out> <setA.txt> ... <setF.txt> [labelA-F]
 *   每个 setN.txt: 每行一个成员 ID
 *
 * 引擎: Venn6（setInArrA~F + setTitleA~F + setOutGraph + getVennGraph）
 */
public class Venn6Cli {
    public static void main(String[] args) throws Exception {
        if (args.length < 7) {
            System.err.println("用法: Venn6Cli <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> <setF.txt> [labelA-F]");
            System.exit(1);
        }
        String outFile = args[0];
        ArrayList<HashSet<String>> sets = new ArrayList<HashSet<String>>();
        for (int i = 1; i <= 6; i++) {
            sets.add(readSet(args[i]));
        }
        String[] labels = new String[6];
        for (int i = 0; i < 6; i++) {
            labels[i] = args.length > 7 + i ? args[7 + i] : String.valueOf((char)('A' + i));
        }

        Venn6 v = new Venn6();
        v.setInArrA(sets.get(0));
        v.setInArrB(sets.get(1));
        v.setInArrC(sets.get(2));
        v.setInArrD(sets.get(3));
        v.setInArrE(sets.get(4));
        v.setInArrF(sets.get(5));
        v.setTitleA(labels[0]);
        v.setTitleB(labels[1]);
        v.setTitleC(labels[2]);
        v.setTitleD(labels[3]);
        v.setTitleE(labels[4]);
        v.setTitleF(labels[5]);
        v.setOutGraph(new File(outFile));
        v.getOverlap(); // 必须先计算交集，否则 maskToSet 为空 → 全部计数 0（08/31 盲测 P0 bug）
        v.getVennGraph();
        System.err.println("[tbplot] 已保存: " + outFile);
        System.exit(0);
    }

    static HashSet<String> readSet(String path) throws Exception {
        HashSet<String> set = new HashSet<String>();
        BufferedReader br = new BufferedReader(new FileReader(path));
        String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (!line.isEmpty() && !line.startsWith("#")) set.add(line);
        }
        br.close();
        System.err.println("[tbplot] " + path + ": " + set.size() + " 成员");
        return set;
    }
}