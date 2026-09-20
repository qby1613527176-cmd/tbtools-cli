import biocjava.bioWeb.Pubmed.PubmedSearch;

import java.io.File;

/**
 * tbplot pubmed — PubMed 文献检索汇总 CLI（GUI 逆向 #45，09/21）
 *
 * 用法: PubmedSearchCli <query> <out.xls>
 *   query: PubMed 检索式（如 "GRAS transcription factor plant"）
 *   out:   文献汇总表（期刊/标题/年份/影响因子/DOI 等）
 *
 * 引擎: PubmedSearch.process(query, file)（GUI 逆向：PubmedSummaryGUIPanel $2；
 *   ⚠️ 联网 NCBI PubMed eutils；main() 硬编码演示查询）
 */
public class PubmedSearchCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: PubmedSearchCli <query> <out.xls>");
            System.exit(1);
        }
        new PubmedSearch().process(args[0], new File(args[1]));
        System.err.println("[tbplot] PubMed 检索完成: " + args[1]);
        System.exit(0);
    }
}
