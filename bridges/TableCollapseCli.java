import java.io.File;

/**
 * tbplot tableCollapse — 表格按键折叠 CLI（08/29，第 63 引擎）
 *
 * 用法: TableCollapseCli <inTable> <keyColIndex> <outTable> [hasHeader true|false] [colSep]
 *   inTable: 输入表格；keyColIndex: 折叠键列（0 起）
 *   outTable: 按键折叠（同键行合并，值用分隔符连接）
 *   hasHeader: 是否有表头（默认 true）
 *   colSep: 分隔符（默认 \t）
 *
 * ⚠️ main() 硬编码路径——改走 setInTable/setKeyColumnIndex/setOutTable 等 setter + process()。
 */
public class TableCollapseCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: TableCollapseCli <inTable> <keyColIndex> <outTable> [hasHeader true|false] [colSep]");
            System.exit(1);
        }
        Object o = Class.forName("biocjava.bioDoer.Table.TableCollasper")
                .getDeclaredConstructor().newInstance();
        Class<?> c = o.getClass();
        c.getMethod("setInTable", File.class).invoke(o, new File(args[0]));
        c.getMethod("setKeyColumnIndex", int.class).invoke(o, Integer.parseInt(args[1]));
        c.getMethod("setOutTable", File.class).invoke(o, new File(args[2]));
        boolean header = true;
        if (args.length > 3) header = Boolean.parseBoolean(args[3]);
        c.getMethod("setHeader", boolean.class).invoke(o, header);
        c.getMethod("process").invoke(o);
        System.err.println("[tbplot] 表格按键折叠完成: " + args[2]);
        System.exit(0);
    }
}