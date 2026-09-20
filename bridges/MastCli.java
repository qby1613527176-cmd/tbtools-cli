/**
 * tbplot mast — MAST motif 搜索 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: MastCli <sequence.fa> <motifs.meme|meme.xml> <workingDir> [--motif-to-use N] [--max-motif-pvalue 1e-4] [--max-seq-evalue 10] [--extra "..."]
 *
 * 接口来源：反编译 MASTGUIPanel（GUI 真实调用链）：
 *   QuickRunMAST qrm = new QuickRunMAST();
 *   qrm.setSequenceFile/setMotifFile/setWorkingDir/setMaxMotifPvalue/
 *      setMaxSequenceEvalue/setMotifToUse;
 *   qrm.process();   // 内部 `mast <seq> -d <motifs> -ev <p> -mev <e> [--motif N]`
 *
 * 依赖系统 mast 二进制（meme-suite）；产物 mast.txt/mast.xml 在 workingDir。
 * MEME 管线闭环：meme(发现) → fimo(扫描) / mast(搜索) → memeViz(可视化)。
 */
public class MastCli {
    public static void main(String[] args) throws Exception {
        String motifToUse = "";
        double maxMotifP = 1e-4, maxSeqE = 10.0;
        String extra = "";
        java.util.ArrayList<String> pos = new java.util.ArrayList<String>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--motif-to-use") && i+1 < args.length) motifToUse = args[++i];
            else if (args[i].equals("--max-motif-pvalue") && i+1 < args.length) maxMotifP = Double.parseDouble(args[++i]);
            else if (args[i].equals("--max-seq-evalue") && i+1 < args.length) maxSeqE = Double.parseDouble(args[++i]);
            else if (args[i].equals("--extra") && i+1 < args.length) extra = args[++i];
            else pos.add(args[i]);
        }
        if (pos.size() < 3) {
            System.err.println("用法: MastCli <sequence.fa> <motifs.meme|meme.xml> <workingDir> [--motif-to-use N] [--max-motif-pvalue 1e-4] [--max-seq-evalue 10]");
            System.exit(1);
        }
        java.io.File wd = new java.io.File(pos.get(2));
        if (!wd.isDirectory() && !wd.mkdirs()) {
            System.err.println("❌ 无法创建 workingDir: " + pos.get(2));
            System.exit(1);
        }
        Object qrm = Class.forName("biocjava.bioIO.BioSoftPipeServer.MEMEsuiteWrapper.QuickRunMAST")
                .getDeclaredConstructor().newInstance();
        Class<?> c = qrm.getClass();
        c.getMethod("setSequenceFile", java.io.File.class).invoke(qrm, new java.io.File(pos.get(0)));
        c.getMethod("setMotifFile", java.io.File.class).invoke(qrm, new java.io.File(pos.get(1)));
        c.getMethod("setWorkingDir", java.io.File.class).invoke(qrm, wd);
        c.getMethod("setMaxMotifPvalue", double.class).invoke(qrm, maxMotifP);
        c.getMethod("setMaxSequenceEvalue", double.class).invoke(qrm, maxSeqE);
        if (!motifToUse.isEmpty()) c.getMethod("setMotifToUse", String.class).invoke(qrm, motifToUse);
        if (!extra.isEmpty()) {
            try { c.getMethod("setOtherParas", String.class).invoke(qrm, extra); }
            catch (Exception ignore) {}
        }
        c.getMethod("process").invoke(qrm);
        System.err.println("[tbplot] MAST 完成，结果在: " + wd.getAbsolutePath());
        System.exit(0);
    }
}