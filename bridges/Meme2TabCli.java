/**
 * tbplot meme2tab — MEME/MAST XML → 表格 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: Meme2TabCli <meme.xml|mast.xml> <out.tab>
 *
 * 接口来源：反编译 MemeOrMastXmlToTabGUIPanel（GUI 真实调用链）：
 *   MEMESuiteXMLtoTab mxt = new MEMESuiteXMLtoTab();
 *   mxt.setInMastXML(inXML); mxt.setOutTab(outTab); mxt.process();
 * 纯逻辑无 GUI。产物：motif 域注释表（序列 × motif 位置/pvalue）。
 */
public class Meme2TabCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: Meme2TabCli <meme.xml|mast.xml> <out.tab>");
            System.exit(1);
        }
        Object mxt = Class.forName("biocjava.bioIO.BioSoftPipeServer.MEMEsuiteWrapper.MEMESuiteXMLtoTab")
                .getDeclaredConstructor().newInstance();
        Class<?> c = mxt.getClass();
        c.getMethod("setInMastXML", java.io.File.class).invoke(mxt, new java.io.File(args[0]));
        c.getMethod("setOutTab", java.io.File.class).invoke(mxt, new java.io.File(args[1]));
        c.getMethod("process").invoke(mxt);
        System.err.println("[tbplot] 已保存: " + args[1]);
        System.exit(0);
    }
}