/**
 * tbplot makemotif — 从序列生成 MEME motif 文件 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: MakeMotifCli <in.seqs.txt> <out.meme> [--mol DNA|RNA|Protein]
 *
 * 接口来源：反编译 MakeMotifGUIPanel（GUI 真实调用链）：
 *   GenerateMotifFromSequences gmfs = new GenerateMotifFromSequences();
 *   gmfs.setInSeqLines(File); gmfs.setOutMotifMatrix(File);
 *   gmfs.setMoleculeType(MotifMolType); gmfs.process();
 * 输入：每行一条待对齐的等长序列（GUI 粘贴框逐行 = 等长片段）；
 * 输出：MEME 格式 letter-probability matrix motif 文件（可直接喂 fimo/mast）。
 */
public class MakeMotifCli {
    public static void main(String[] args) throws Exception {
        String mol = "DNA";
        java.util.ArrayList<String> pos = new java.util.ArrayList<String>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--mol") && i+1 < args.length) mol = args[++i];
            else pos.add(args[i]);
        }
        if (pos.size() < 2) {
            System.err.println("用法: MakeMotifCli <in.seqs.txt> <out.meme> [--mol DNA|RNA|Protein]");
            System.exit(1);
        }
        Object gmfs = Class.forName("biocjava.bioIO.BioSoftPipeServer.MEMEsuiteWrapper.GenerateMotifFromSequences")
                .getDeclaredConstructor().newInstance();
        Class<?> c = gmfs.getClass();
        c.getMethod("setInSeqLines", java.io.File.class).invoke(gmfs, new java.io.File(pos.get(0)));
        c.getMethod("setOutMotifMatrix", java.io.File.class).invoke(gmfs, new java.io.File(pos.get(1)));
        Class<?> mm = Class.forName("biocjava.bioIO.BioSoftPipeServer.MEMEsuiteWrapper.GenerateMotifFromSequences$MotifMolType");
        Object mt = mol.equalsIgnoreCase("RNA") ? Enum.valueOf((Class)mm, "RNA")
                  : mol.equalsIgnoreCase("Protein") ? Enum.valueOf((Class)mm, "Protein")
                  : Enum.valueOf((Class)mm, "DNA");
        c.getMethod("setMoleculeType", mm).invoke(gmfs, mt);
        c.getMethod("process").invoke(gmfs);
        System.err.println("[tbplot] 已保存: " + pos.get(1));
        System.exit(0);
    }
}