import biocjava.bioDoer.Aligner.SequenceSimilarityMatrix.CalculateSimilarity;

import java.io.File;

/**
 * tbplot protsim — 蛋白两两相似度矩阵 CLI（GUI 逆向 #24，09/20）
 *
 * 用法: CalculateSimilarityCli <pep.fa> <out.matrix>
 *   in:  蛋白 FASTA（多条序列）
 *   out: 两两相似度矩阵（百分比）
 *
 * 引擎: CalculateSimilarity（GUI 逆向：ProteinPairwiseSimilarityMatrixGUIPanel $1
 *   → setInFile/setOutSimMat/process，main() 硬编码路径无 ArgsParser）
 */
public class CalculateSimilarityCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: CalculateSimilarityCli <pep.fa> <out.matrix>");
            System.exit(1);
        }
        File inFile = new File(args[0]);
        File outFile = new File(args[1]);
        if (!inFile.exists()) {
            System.err.println("错误: 输入文件不存在: " + inFile.getAbsolutePath());
            System.exit(2);
        }
        CalculateSimilarity cs = new CalculateSimilarity();
        cs.setInFile(inFile);
        cs.setOutSimMat(outFile);
        cs.process();
        System.err.println("[tbplot] 相似度矩阵完成: " + outFile.getAbsolutePath());
        System.exit(0);
    }
}
