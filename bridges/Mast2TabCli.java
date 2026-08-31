import biocjava.bioIO.BioSoftPipeServer.MEMEsuiteWrapper.MEMESuiteXMLtoTab;

import java.io.File;

/**
 * tbcli mast2tab — MEME/Mast XML → tab CLI（08/31 第八十三波，工具 93）
 *
 * 用法: Mast2TabCli <mast|meme.xml> <out.tab>
 *   mast/meme.xml: MEME Suite XML 输出（mast.xml 或 meme.xml）
 *   out.tab: 表格化结果
 *
 * 引擎: MEMESuiteXMLtoTab.setInMastXML/setOutTab + process()（main 完全硬编码演示 → setter+process）
 */
public class Mast2TabCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: Mast2TabCli <mast|meme.xml> <out.tab>");
            System.exit(1);
        }
        MEMESuiteXMLtoTab mxt = new MEMESuiteXMLtoTab();
        mxt.setInMastXML(new File(args[0]));
        mxt.setOutTab(new File(args[1]));
        mxt.process();
        System.err.println("[tbplot] 已保存: " + args[1]);
        System.exit(0);
    }
}
