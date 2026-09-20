/**
 * tbplot meme — MEME motif 发现 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: MemeCli <in.fa> <workingDir> <outMemeXml> [--nmotifs N] [--minw N] [--maxw N]
 *        [--evt 0.05] [--mod zoops|oops|anr] [--extra "额外 meme 参数"]
 *
 * 接口来源：反编译 MEMEGUIPanel（GUI 真实调用链）：
 *   QuickRunMEME qrm = new QuickRunMEME();
 *   qrm.setInFile/setWorkingDir/setMaxEvalue/setNumberOfMotif/
 *      setMiningMode/setMinMotifWidth/setMaxMotifWidth;
 *   qrm.process();
 * 内部执行 `meme <in> -evt E -nmotifs N -minw W -maxw X -mod zoops|oops|anr`
 *   （cwd=workingDir，依赖系统 meme 二进制；产物 meme.xml 于 workingDir）
 *
 * 输出：workingDir/meme.xml 复制到 <outMemeXml>。
 */
public class MemeCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: MemeCli <in.fa> <workingDir> <outMemeXml> [--nmotifs N] [--minw N] [--maxw N] [--evt 0.05] [--mod zoops|oops|anr] [--extra \"...\"]");
            System.exit(1);
        }
        int nmotifs = 3, minw = 6, maxw = 50;
        double evt = 0.05;
        String mod = "zoops", extra = "";
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--nmotifs") && i+1 < args.length) nmotifs = Integer.parseInt(args[++i]);
            else if (args[i].equals("--minw") && i+1 < args.length) minw = Integer.parseInt(args[++i]);
            else if (args[i].equals("--maxw") && i+1 < args.length) maxw = Integer.parseInt(args[++i]);
            else if (args[i].equals("--evt") && i+1 < args.length) evt = Double.parseDouble(args[++i]);
            else if (args[i].equals("--mod") && i+1 < args.length) mod = args[++i];
            else if (args[i].equals("--extra") && i+1 < args.length) extra = args[++i];
        }
        java.io.File wd = new java.io.File(args[1]);
        if (!wd.isDirectory() && !wd.mkdirs()) {
            System.err.println("❌ 无法创建 workingDir: " + args[1]);
            System.exit(1);
        }
        Object qrm = Class.forName("biocjava.bioIO.BioSoftPipeServer.MEMEsuiteWrapper.QuickRunMEME")
                .getDeclaredConstructor().newInstance();
        Class<?> c = qrm.getClass();
        c.getMethod("setInFile", java.io.File.class).invoke(qrm, new java.io.File(args[0]));
        c.getMethod("setWorkingDir", java.io.File.class).invoke(qrm, wd);
        c.getMethod("setMaxEvalue", double.class).invoke(qrm, evt);
        c.getMethod("setNumberOfMotif", int.class).invoke(qrm, nmotifs);
        c.getMethod("setMinMotifWidth", int.class).invoke(qrm, minw);
        c.getMethod("setMaxMotifWidth", int.class).invoke(qrm, maxw);
        Class<?> sm = Class.forName("biocjava.bioIO.BioSoftPipeServer.MEMEsuiteWrapper.QuickRunMEME$SITEDISTRIBUTION");
        Object mode = mod.equalsIgnoreCase("oops") ? Enum.valueOf((Class)sm, "OneOccurPerSeq")
                    : mod.equalsIgnoreCase("anr") ? Enum.valueOf((Class)sm, "AnyNumberOfOccurPerSeq")
                    : Enum.valueOf((Class)sm, "ZeroOrOneOccurPerSeq");
        c.getMethod("setMiningMode", sm).invoke(qrm, mode);
        if (!extra.isEmpty()) {
            try { c.getMethod("setOtherParas", String.class).invoke(qrm, extra); }
            catch (Exception ignore) { /* otherParas 图层面不可见时忽略 */ }
        }
        c.getMethod("process").invoke(qrm);
        // meme 5.x 输出到 meme_out/ 子目录；旧版输出到 wd 根（GUI 面板是 wd 根）
        java.io.File xml = new java.io.File(new java.io.File(wd, "meme_out"), "meme.xml");
        if (!xml.isFile()) xml = new java.io.File(wd, "meme.xml");
        if (!xml.isFile()) {
            java.io.File[] anyXml = wd.listFiles((d, n) -> n.endsWith(".xml"));
            if (anyXml != null && anyXml.length > 0) xml = anyXml[0];
        }
        if (!xml.isFile()) {
            System.err.println("❌ 未找到 meme.xml（meme 运行失败？检查系统 meme 安装）");
            System.exit(1);
        }
        java.nio.file.Files.copy(xml.toPath(), new java.io.File(args[2]).toPath(),
                java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        System.err.println("[tbplot] meme.xml 已保存: " + args[2]);
        System.exit(0);
    }
}