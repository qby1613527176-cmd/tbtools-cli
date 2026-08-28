import biocjava.bioDoer.JIGplotToolkit.Paf.PafGenomeComp;

/**
 * tbplot pafcomp — TBtools PAF 基因组比较图 CLI（08/29，第 38 引擎）
 *
 * 用法: PafGC <--inPaf paf> <--outGraph out> [--colorMode Target|Query|None] [--size N] [--colorSeed N] [--switchQnT] [--minLen N]
 *
 * ⚠️ 入口是 main1（不是 main）——main 不 setInPaf 用默认路径；main1 完整 ArgsParser + quickSave
 */
public class PafGC {
    public static void main(String[] args) throws Exception {
        java.lang.reflect.Method m = PafGenomeComp.class.getMethod("main1", String[].class);
        m.invoke(null, (Object) args);
    }
}
