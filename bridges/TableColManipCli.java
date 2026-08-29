import java.io.File;
import java.lang.reflect.Method;
import java.util.ArrayList;

/**
 * TableColManipulator CLI bridge (engine 84)
 * 表格列选择/筛选：根据列名从表中选择列输出
 * Usage: TableColManipCli <inTable> <outTable> <colName1> [colName2 ...] [--sep tab|comma|space] [--header true|false] [--caseSensitive true|false]
 *   inTable: 输入表格（支持 .gz）；colNames: 要保留的列名（表头）
 */
public class TableColManipCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("Usage: TableColManipCli <inTable> <outTable> <colName1> [colName2...] [--sep tab|comma|space] [--header true|false] [--caseSensitive true|false]");
            System.exit(1);
        }
        String inTable = args[0];
        String outTable = args[1];
        String sep = "tab";
        boolean header = true;
        boolean caseSensitive = false;
        ArrayList<String> selCols = new ArrayList<>();
        // 解析参数: colNames 直到 -- 前缀
        int i = 2;
        while (i < args.length) {
            switch (args[i]) {
                case "--sep": sep = args[++i]; break;
                case "--header": header = Boolean.parseBoolean(args[++i]); break;
                case "--caseSensitive": caseSensitive = Boolean.parseBoolean(args[++i]); break;
                default: selCols.add(args[i]);
            }
            i++;
        }
        if (selCols.isEmpty()) {
            System.err.println("至少需要一个列名");
            System.exit(1);
        }

        Class<?> c = Class.forName("biocjava.bioDoer.Table.TableColManipulator");
        Object o = c.getDeclaredConstructor().newInstance();
        // ColSepType 枚举
        Class<?> sepEnum = Class.forName("biocjava.bioDoer.Table.TableColManipulator$ColSepType");
        String sepVal = sep.equals("comma") ? "comma" : sep.equals("space") ? "space" : "tab";
        Object sepEnumVal = Enum.valueOf((Class) sepEnum, sepVal);
        c.getMethod("setColumnSepType", sepEnum).invoke(o, sepEnumVal);
        c.getMethod("setInFile", File.class).invoke(o, new File(inTable));
        c.getMethod("setOutFile", File.class).invoke(o, new File(outTable));
        c.getMethod("setContainHeader", boolean.class).invoke(o, header);
        c.getMethod("setCaseSensitive", boolean.class).invoke(o, caseSensitive);
        // setIdList 需要 ArrayList —— 传空列表
        c.getMethod("setIdList", ArrayList.class).invoke(o, new ArrayList<String>());
        c.getMethod("setSelectedCols", ArrayList.class).invoke(o, selCols);
        c.getMethod("selectedLines").invoke(o);
        System.out.println("[tbcli] TableColManipulator done: " + outTable);
    }
}