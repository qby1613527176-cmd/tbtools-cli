import biocjava.bioWeb.NCBITaxonomy.NCBITaxonomy;
import biocjava.bioWeb.NCBITaxonomy.Taxon;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;

/**
 * tbplot taxparse — 物种名批量分类解析 CLI（GUI 逆向 #38，09/21）
 *
 * 用法: TaxonomyBatchCli <idList.txt> <out.xls>
 *   idList: 每行一个物种名（首列；其余列原样透传）
 *   out:    首列 + 9 级分类（superkingdom/kingdom/phylum/subphylum/order/
 *           family/subfamily/tribe/genus）+ 透传列
 *
 * 引擎: NCBITaxonomy.process（GUI 逆向：TaxonomyParserGUIPanel $3 批量循环逻辑；
 *   ⚠️ 联网 NCBI eutils esearch+efetch；注册表单次版为 tbtools tool NCBITaxonomy）
 */
public class TaxonomyBatchCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: TaxonomyBatchCli <idList.txt> <out.xls>");
            System.exit(1);
        }
        File idFile = new File(args[0]);
        File outFile = new File(args[1]);
        if (!idFile.exists()) {
            System.err.println("错误: 输入文件不存在: " + idFile.getAbsolutePath());
            System.exit(2);
        }
        NCBITaxonomy nt = new NCBITaxonomy();
        BufferedReader br = new BufferedReader(new FileReader(idFile));
        BufferedWriter bw = new BufferedWriter(new FileWriter(outFile));
        bw.write("Name\tSuperkingdom\tKingdom\tPhylum\tSubphylum\tOrder\tFamily\tSubfamily\tTribe\tGenus");
        bw.newLine();
        String inline;
        int ok = 0, skip = 0;
        while ((inline = br.readLine()) != null) {
            if (inline.trim().isEmpty()) continue;
            String[] columns = inline.split("\t");
            Taxon curTaxon = nt.process(columns[0]);
            if (!curTaxon.isExist()) {
                System.err.println("Skipping line " + inline + " which can't be processed");
                skip++;
                continue;
            }
            StringBuilder sb = new StringBuilder();
            sb.append(columns[0]).append("\t");
            sb.append(curTaxon.getSuperkingdom()).append("\t");
            sb.append(curTaxon.getKingdom()).append("\t");
            sb.append(curTaxon.getPhylum()).append("\t");
            sb.append(curTaxon.getSubphylum()).append("\t");
            sb.append(curTaxon.getOrder()).append("\t");
            sb.append(curTaxon.getFamily()).append("\t");
            sb.append(curTaxon.getSubfamily()).append("\t");
            sb.append(curTaxon.getTribe()).append("\t");
            sb.append(curTaxon.getGenus());
            for (int i = 1; i < columns.length; ++i) {
                sb.append("\t").append(columns[i]);
            }
            bw.write(sb.toString());
            bw.newLine();
            ok++;
        }
        br.close();
        bw.close();
        System.err.println("[tbplot] 分类解析完成: " + ok + " 条成功" + (skip > 0 ? "，" + skip + " 条跳过" : "") + " → " + outFile.getAbsolutePath());
        System.exit(0);
    }
}
