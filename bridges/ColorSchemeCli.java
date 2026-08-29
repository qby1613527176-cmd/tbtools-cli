import biocjava.bioDoer.JIGplotToolkit.ColorSchemeGenerator.ColorSchemeGenerator;
import java.io.File;

/**
 * tbplot colorscheme — TBtools 配色生成 CLI（08/29，第 41 引擎）
 *
 * 用法: ColorSchemeCli <inTab> <outTab> <refColIndex>
 *   inTab: tab 分隔表；refColIndex: 从 0 开始，取该列做配色 key（去重）
 *   outTab: 输出颜色代码表
 */
public class ColorSchemeCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: ColorSchemeCli <inTab> <outTab> <refColIndex>");
            System.exit(1);
        }
        ColorSchemeGenerator csg = new ColorSchemeGenerator();
        csg.setInTab(new File(args[0]));
        csg.setOutTab(new File(args[1]));
        csg.setRefColIndex(Integer.parseInt(args[2]));
        csg.process();
        System.err.println("[tbplot] 已保存: " + args[1]);
        System.exit(0);
    }
}
