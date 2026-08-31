import biocjava.bioDoer.JIGplotToolkit.ColorSchemeGenerator.ColorSchemeGenerator;

import java.io.File;

/**
 * tbcli colorscheme — 表格分组着色 CLI（08/31 第七十四波）
 *
 * 用法: ColorSchemeCli <in.tab> <out.tab> <refColIndex(1-based)>
 *   in.tab: 输入表（任意列，取第 refColIndex 列为分组键）
 *   out.tab: 输出 = 原表 + RGB 颜色列（如 255,0,0）
 *
 * 引擎: ColorSchemeGenerator.setInTab/setOutTab/setRefColIndex + process()
 *   （⚠️ isContinue/predifinedColorFile 无 setter——固定走随机色板分支）
 */
public class ColorSchemeCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: ColorSchemeCli <in.tab> <out.tab> <refColIndex(1-based)>");
            System.exit(1);
        }
        ColorSchemeGenerator csg = new ColorSchemeGenerator();
        csg.setInTab(new File(args[0]));
        csg.setOutTab(new File(args[1]));
        csg.setRefColIndex(Integer.parseInt(args[2]) - 1);
        csg.process();
        System.err.println("[tbplot] 已保存: " + args[1]);
        System.exit(0);
    }
}