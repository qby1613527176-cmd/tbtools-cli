import biocjava.bioDoer.JIGplotToolkit.Synteny.MultipleGffViewer.FormatTranformerForMultipleGffViewer;

import java.io.File;

/**
 * tbcli mggxf — 多 GFF 视图格式转换 CLI（08/31 第九十波，工具 103）
 *
 * 用法: MgGxfCli <inGenePair|blastTab6> <in.simplified.gff> <out.LinkedRegion> [GenePair|BlastTab6]
 *   inGenePair: 基因对文件（GenePair 模式）
 *   in.simplified.gff: 简化 GFF（chr\tgene\tstart\tend）
 *   out.LinkedRegion: 输出共线性区域
 *
 * 引擎: FormatTranformerForMultipleGffViewer.setInFile/setInGffFile/setOutFile/setInputFormat + transform()
 *   （main 硬编码演示 → setter+process；多物种共线性可视化的格式转换）
 */
public class MgGxfCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: MgGxfCli <inGenePair|blastTab6> <in.simplified.gff> <out.LinkedRegion> [GenePair|BlastTab6]");
            System.exit(1);
        }
        FormatTranformerForMultipleGffViewer.InputFormat fmt =
            (args.length > 3 && args[3].equals("BlastTab6"))
                ? FormatTranformerForMultipleGffViewer.InputFormat.BlastTab6
                : FormatTranformerForMultipleGffViewer.InputFormat.GenePair;
        FormatTranformerForMultipleGffViewer ftfmg = new FormatTranformerForMultipleGffViewer();
        ftfmg.setInFile(new File(args[0]));
        ftfmg.setInGffFile(new File(args[1]));
        ftfmg.setOutFile(new File(args[2]));
        ftfmg.setInputFormat(fmt);
        ftfmg.transform();
        System.err.println("[tbplot] 已保存: " + args[2]);
        System.exit(0);
    }
}