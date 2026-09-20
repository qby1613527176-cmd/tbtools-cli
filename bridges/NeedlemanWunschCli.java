/**
 * tbplot nwalign — Needleman-Wunsch 全局比对 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: NeedlemanWunschCli <seq1.fa> <seq2.fa> <out> [--protein|--dna] [--format EMBOSS|FASTA]
 *        [--gap-open 10] [--gap-extend 0.5] [--end-gap-open 10] [--end-gap-extend 0.5] [--end-weight]
 *
 * 接口来源：反编译 NeedlemanWunschGUIPanel（GUI 真实调用链）：
 *   NeedleManWunschAlign nmwa = new NeedleManWunschAlign(SeqType.Protein|DNA);
 *   nmwa.setxId/setyId/setxSeq/setySeq/setOutFormat/setGapOpen/setGapExtension/
 *        setEndGapOpen/setEndGapExtend/setEndWeight;
 *   FileUtils.stringToFile(nmwa.align().toString(), out);
 * 输入：两条单序列 FASTA（仅取每条的第一条序列）。
 * 输出：EMBOSS/FASTA 格式比对文本。
 */
public class NeedlemanWunschCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: NeedlemanWunschCli <seq1.fa> <seq2.fa> <out> [--protein|--dna] [--format EMBOSS|FASTA] [--gap-open N] [--gap-extend N] [--end-gap-open N] [--end-gap-extend N] [--end-weight]");
            System.exit(1);
        }
        boolean protein = false, dna = false, endWeight = false;
        String fmt = "EMBOSS";
        float gapOpen = 10f, gapExtend = 0.5f, endGapOpen = 10f, endGapExtend = 0.5f;
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--protein")) protein = true;
            else if (args[i].equals("--dna")) dna = true;
            else if (args[i].equals("--format") && i+1 < args.length) fmt = args[++i].toUpperCase();
            else if (args[i].equals("--gap-open") && i+1 < args.length) gapOpen = Float.parseFloat(args[++i]);
            else if (args[i].equals("--gap-extend") && i+1 < args.length) gapExtend = Float.parseFloat(args[++i]);
            else if (args[i].equals("--end-gap-open") && i+1 < args.length) endGapOpen = Float.parseFloat(args[++i]);
            else if (args[i].equals("--end-gap-extend") && i+1 < args.length) endGapExtend = Float.parseFloat(args[++i]);
            else if (args[i].equals("--end-weight")) endWeight = true;
        }
        Seq s1 = readFirst(args[0]), s2 = readFirst(args[1]);
        Class<?> seqType = Class.forName("biocjava.bioDoer.Aligner.NeedleMan.NeedleManWunschAlign$SeqType");
        Object tp = protein ? Enum.valueOf((Class)seqType, "Protein")
                  : dna ? Enum.valueOf((Class)seqType, "DNA")
                  : Enum.valueOf((Class)seqType, "Protein");
        Class<?> alnCls = Class.forName("biocjava.bioDoer.Aligner.NeedleMan.NeedleManWunschAlign");
        Object nmwa = alnCls.getConstructor(seqType).newInstance(tp);
        Class<?> fmtCls = Class.forName("biocjava.bioDoer.Aligner.NeedleMan.NeedleManWunschAlign$ALNFORMAT");
        Object fmtEnum = Enum.valueOf((Class)fmtCls, fmt);
        alnCls.getMethod("setxId", String.class).invoke(nmwa, s1.id);
        alnCls.getMethod("setyId", String.class).invoke(nmwa, s2.id);
        alnCls.getMethod("setxSeq", String.class).invoke(nmwa, s1.seq);
        alnCls.getMethod("setySeq", String.class).invoke(nmwa, s2.seq);
        alnCls.getMethod("setOutFormat", fmtCls).invoke(nmwa, fmtEnum);
        alnCls.getMethod("setGapOpen", float.class).invoke(nmwa, gapOpen);
        alnCls.getMethod("setGapExtension", float.class).invoke(nmwa, gapExtend);
        alnCls.getMethod("setEndGapOpen", float.class).invoke(nmwa, endGapOpen);
        alnCls.getMethod("setEndGapExtend", float.class).invoke(nmwa, endGapExtend);
        alnCls.getMethod("setEndWeight", boolean.class).invoke(nmwa, endWeight);
        Object result = alnCls.getMethod("align").invoke(nmwa);
        String text = result.toString();
        java.io.FileWriter fw = new java.io.FileWriter(args[2]);
        fw.write(text); fw.close();
        System.err.println("[tbplot] 已保存: " + args[2] + " (" + text.length() + " 字符)");
        System.exit(0);
    }

    static class Seq { String id, seq; }
    static Seq readFirst(String path) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.FileReader(path));
        String id = null; StringBuilder sb = new StringBuilder(); String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty()) continue;
            if (line.startsWith(">")) { if (id == null) id = line.substring(1).trim(); continue; }
            if (id != null) sb.append(line);
        }
        br.close();
        if (id == null) throw new Exception("输入不是 FASTA: " + path);
        Seq s = new Seq(); s.id = id; s.seq = sb.toString();
        return s;
    }
}
