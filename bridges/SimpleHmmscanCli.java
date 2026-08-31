import biocjava.bioDoer.LinuxPipe.simpleHmmscan;

import java.io.File;

/**
 * tbcli simpleHmmscan — Pfam 域快速扫描 CLI（08/31 第七十三波）
 *
 * 用法: SimpleHmmscanCli <pfamA.hmm> <target.pep> <idList.txt> <out.txt>
 *   pfamA.hmm: Pfam-A.hmm 数据库（需已 hmmindex）
 *   target.pep: 待扫描蛋白
 *   idList.txt: 感兴趣 Pfam ID 列表（每行一个，如 GRAS）
 *   out.txt: 输出
 *
 * 引擎: simpleHmmscan.setPfamHmmA/setTargetPep/setPfamIdList/setFinalOutFile + process()
 *   （main 硬编码演示 → setter+process；调系统 hmmsearch）
 */
public class SimpleHmmscanCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("用法: SimpleHmmscanCli <pfamA.hmm> <target.pep> <idList.txt> <out.txt>");
            System.exit(1);
        }
        simpleHmmscan sh = new simpleHmmscan();
        sh.setPfamHmmA(new File(args[0]));
        sh.setTargetPep(new File(args[1]));
        sh.setPfamIdList(new File(args[2]));
        sh.setFinalOutFile(new File(args[3]));
        sh.process();
        System.err.println("[tbplot] 已保存: " + args[3]);
        System.exit(0);
    }
}