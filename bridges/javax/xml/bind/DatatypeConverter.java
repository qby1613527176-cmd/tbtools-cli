package javax.xml.bind;

/**
 * Fake DatatypeConverter — JDK9+ 移除 javax.xml.bind 后的兼容垫片（N27 修复）。
 *
 * 背景：TBtools 部分引擎（SimpleEfpBrowser.generateSuperHeatMap 等）直接引用
 * javax.xml.bind.DatatypeConverter（JDK8 内建）；JDK9+ 移除了 JAXB，引擎在
 * JDK9+ 上运行时 NoClassDefFoundError。08/29 起用本垫片（java.util.Base64 实现）
 * 解决，但源码未入库 → build/ 被 .gitignore 排除后，全新 checkout 无法重建，
 * 导致外部测试环境 multiEfp 报 NoClassDefFoundError。
 *
 * 本文件随仓库分发（bridges/javax/xml/bind/），ensure_bridge 自动编译到 build/。
 * 只实现 TBtools 引擎实际用到的静态方法（Base64/Hex/基础类型），按需扩展。
 */
public class DatatypeConverter {

    private DatatypeConverter() {
        throw new AssertionError("No instances");
    }

    // ---- Base64 ----
    public static String printBase64Binary(byte[] val) {
        return val == null ? null : java.util.Base64.getEncoder().encodeToString(val);
    }

    public static byte[] parseBase64Binary(String s) {
        return s == null ? null : java.util.Base64.getDecoder().decode(s);
    }

    // ---- Hex ----
    public static String printHexBinary(byte[] val) {
        if (val == null) return null;
        StringBuilder sb = new StringBuilder(val.length * 2);
        for (byte b : val) {
            sb.append(Character.forDigit((b >> 4) & 0xF, 16));
            sb.append(Character.forDigit(b & 0xF, 16));
        }
        return sb.toString();
    }

    public static byte[] parseHexBinary(String s) {
        if (s == null) return null;
        int len = s.length();
        byte[] out = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            out[i / 2] = (byte) Integer.parseInt(s.substring(i, i + 2), 16);
        }
        return out;
    }

    // ---- 基础类型 ----
    public static String printString(String val) { return val; }
    public static String parseString(String s) { return s; }
    public static int parseInt(String s) { return Integer.parseInt(s.trim()); }
    public static String printInt(int i) { return Integer.toString(i); }
    public static long parseLong(String s) { return Long.parseLong(s.trim()); }
    public static String printLong(long l) { return Long.toString(l); }
    public static short parseShort(String s) { return Short.parseShort(s.trim()); }
    public static String printShort(short v) { return Short.toString(v); }
    public static boolean parseBoolean(String s) { return Boolean.parseBoolean(s.trim()); }
    public static String printBoolean(boolean b) { return Boolean.toString(b); }
    public static float parseFloat(String s) { return Float.parseFloat(s.trim()); }
    public static String printFloat(float f) { return Float.toString(f); }
    public static double parseDouble(String s) { return Double.parseDouble(s.trim()); }
    public static String printDouble(double d) { return Double.toString(d); }
}