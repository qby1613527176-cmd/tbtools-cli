import biocjava.bioIO.BlastXml.BlastXMLToPairwise;
import biocjava.bioIO.BlastXml.BlastXmlToBlastFoolTable;

import java.io.File;

/**
 * tbplot xml2blasttab / xml2pairwise — BLAST XML 转表 CLI（GUI 逆向 #25，09/20）
 *
 * 用法: BlastXmlConvertCli <mode> <in.xml> <out.txt>
 *   mode: blasttab  → BlastXmlToBlastFoolTable.xml2ShowerTable（BLAST 标准 m7 风格表）
 *         pairwise  → BlastXMLToPairwise.parse（BLAST 网页 pairwise 对齐文本）
 *
 * 引擎: GUI 逆向 BlastXML2TableGUIPanel $3 四模式单选：
 *   OutBlastTab→FoolTable / OutTBtoolsTab→SelfDefined（已有 blastXmlToTable）/
 *   Summary→SummaryTable（已有 blastXmlSummaryTable）/ 默认→Pairwise
 *   本桥补齐前两者缺的 FoolTable 和 Pairwise
 */
public class BlastXmlConvertCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: BlastXmlConvertCli <blasttab|pairwise> <in.xml> <out.txt>");
            System.exit(1);
        }
        String mode = args[0];
        File inXml = new File(args[1]);
        File outTxt = new File(args[2]);
        if (!inXml.exists()) {
            System.err.println("错误: 输入文件不存在: " + inXml.getAbsolutePath());
            System.exit(2);
        }
        switch (mode) {
            case "blasttab":
                BlastXmlToBlastFoolTable.xml2ShowerTable(inXml, outTxt);
                break;
            case "pairwise":
                BlastXMLToPairwise.parse(inXml, outTxt);
                break;
            default:
                System.err.println("错误: 未知模式 " + mode + "（可选 blasttab|pairwise）");
                System.exit(1);
        }
        System.err.println("[tbplot] BLAST XML 转换完成(" + mode + "): " + outTxt.getAbsolutePath());
        System.exit(0);
    }
}
