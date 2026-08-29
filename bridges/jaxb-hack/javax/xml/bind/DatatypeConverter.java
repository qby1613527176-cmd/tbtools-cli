package javax.xml.bind;
import java.util.Base64;
public class DatatypeConverter {
    public static String printBase64Binary(byte[] data) { return Base64.getEncoder().encodeToString(data); }
    public static String printHexBinary(byte[] data) {
        StringBuilder sb = new StringBuilder();
        for (byte b : data) sb.append(String.format("%02x", b));
        return sb.toString();
    }
    public static byte[] parseBase64Binary(String s) { return Base64.getDecoder().decode(s); }
}
