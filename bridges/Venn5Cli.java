import biocjava.bioDoer.JJplot2Toolkit.WonderfulVenn.venn5.Venn5;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashSet;

/**
 * tbplot venn5 — TBtools 五集合韦恩图 CLI（08/29 新增，第 29 引擎）
 *
 * 用法: Venn5Cli <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> [labelA] [labelB] [labelC] [labelD] [labelE]
 *   每个 setN.txt: 每行一个成员 ID
 *
 * 引擎: Venn5（setInArrA~E + setTitleA~E + setOutGraph + getVennGraph）
 */
public class Venn5Cli {
    public static void main(String[] args) throws Exception {
        if (args.length < 6) {
            System.err.println("用法: Venn5Cli <out> <setA.txt> <setB.txt> <setC.txt> <setD.txt> <setE.txt> [labelA-E]");
            System.exit(1);
        }
        String outFile = args[0];
        ArrayList<HashSet<String>> sets = new ArrayList<HashSet<String>>();
        for (int i = 1; i <= 5; i++) {
            sets.add(readSet(args[i]));
        }
        String[] labels = args.length > 6 ? new String[]{args[6], args.length>7?args[7]:"B", args.length>8?args[8]:"C", args.length>9?args[9]:"D", args.length>10?args[10]:"E"} : new String[]{"A","B","C","D","E"};

        Venn5 v = new Venn5();
        v.setInArrA(sets.get(0));
        v.setInArrB(sets.get(1));
        v.setInArrC(sets.get(2));
        v.setInArrD(sets.get(3));
        v.setInArrE(sets.get(4));
        v.setTitleA(labels[0]);
        v.setTitleB(labels[1]);
        v.setTitleC(labels[2]);
        v.setTitleD(labels[3]);
        v.setTitleE(labels[4]);
        v.setOutGraph(new File(outFile));
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