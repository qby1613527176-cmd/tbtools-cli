import biocjava.bioDoer.StructAnnoCompare.StructAnnoCompareConfig;
import biocjava.bioDoer.StructAnnoCompare.StructAnnoCompareResult;
import biocjava.bioDoer.StructAnnoCompare.StructAnnoCompareService;

import java.io.File;
import java.nio.file.Path;

/**
 * tbplot annoCompare — 注释版本对比管线 CLI（08/31 第五十二波）
 *
 * 用法: StructAnnoCompareCli <before.gff3> <after.gff3> <outDir> [runName] [reciprocalOverlap] [boundaryTol] [cdsChangePct] [utrChangePct] [geneScope] [overlapMode]
 *   before/after.gff3: 同一基因组两个版本的注释
 *   outDir: 输出目录（自动建）
 *   runName: 运行名（默认 "annoCompare"）
 *   reciprocalOverlap: 双向重叠阈值（默认 0.5）
 *   boundaryTol: 边界容差（默认 100）
 *   cdsChangePct / utrChangePct: CDS/UTR 变化百分比阈值（默认 0.1 / 0.1）
 *   geneScope: all|mrna_only（默认 all）
 *   overlapMode: reciprocal|any（默认 reciprocal）
 *
 * 产物: <runName>_change_summary.csv / _change_log.csv / tracks/*_annotation_changes.bed /
 *       curation_summary_table.csv / curation_core_metrics.csv / figures/*_curation_summary_jigplot.{png,pdf,svg} /
 *       figures/*_ABCD_single_species_jigplot.{png,pdf,svg}
 *
 * 引擎: StructAnnoCompareService.run(StructAnnoCompareConfig)（纯 headless，无弹窗）
 */
public class StructAnnoCompareCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("用法: StructAnnoCompareCli <before.gff3> <after.gff3> <outDir> [runName] [reciprocalOverlap] [boundaryTol] [cdsChangePct] [utrChangePct] [geneScope] [overlapMode]");
            System.exit(1);
        }
        String before = args[0];
        String after = args[1];
        String outDir = args[2];
        String runName = args.length > 3 ? args[3] : "annoCompare";
        double recOverlap = args.length > 4 ? Double.parseDouble(args[4]) : 0.5;
        int boundaryTol = args.length > 5 ? Integer.parseInt(args[5]) : 100;
        double cdsPct = args.length > 6 ? Double.parseDouble(args[6]) : 0.1;
        double utrPct = args.length > 7 ? Double.parseDouble(args[7]) : 0.1;
        String geneScope = args.length > 8 ? args[8] : "all";
        String overlapMode = args.length > 9 ? args[9] : "reciprocal";

        StructAnnoCompareConfig cfg = new StructAnnoCompareConfig();
        cfg.setBeforeGff(Path.of(before));
        cfg.setAfterGff(Path.of(after));
        cfg.setOutputDir(Path.of(outDir));
        cfg.setRunName(runName);
        cfg.setReciprocalOverlap(recOverlap);
        cfg.setBoundaryTol(boundaryTol);
        cfg.setCdsChangePct(cdsPct);
        cfg.setUtrChangePct(utrPct);
        cfg.setGeneScope(geneScope);
        cfg.setOverlapMode(overlapMode);
        cfg.setGenerateVisualization(true);
        cfg.setLogConsumer(System.err::println);

        StructAnnoCompareResult r = new StructAnnoCompareService().run(cfg);
        System.err.println("[tbplot] summary: " + r.getSummaryPath());
        System.err.println("[tbplot] change log: " + r.getChangeLogPath() + " (" + r.getChangeLogEntries() + " 条)");
        System.err.println("[tbplot] curation core: " + r.getCurationCoreMetricsPath());
        if (r.getFigurePng() != null) System.err.println("[tbplot] curation figure: " + r.getFigurePng());
        if (r.getAbcdFigurePng() != null) System.err.println("[tbplot] ABCD figure: " + r.getAbcdFigurePng());
        System.exit(0);
    }
}
