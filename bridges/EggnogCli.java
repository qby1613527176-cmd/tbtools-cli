/**
 * tbplot eggnog — eggNOG-mapper 直系同源注释 CLI（GUI 面板逆向接口，09/20）
 *
 * 用法: EggnogCli <in.fa> -o <prefix> --output_dir <outDir> --data_dir <eggNOGdb> [--dmnd_db <db>] [--cpu N] [--evalue 0.001] [--override] [其他官方参数...]
 *
 * 接口来源：反编译 EggnogMapperGUIPanel.onStart()（GUI 真实调用链）——
 *   CliArgs cli = CliParser.parse(args);
 *   EmapperPipeline pipeline = new EmapperPipeline(cli);
 *   pipeline.run();
 * GUI 传参（11 项）：-m diamond -i <in.fa> -o <prefix> --output_dir <outDir>
 *   --data_dir <dataDir> --dmnd_db <dmndPath> --cpu <n> --evalue <e> --override
 *
 * ⚠️ 前置：eggNOG 数据库需先就位（TBtools GUI 的 EggnogDbProvider 走飞纪盘
 *   分片下载且依赖 Swing 确认框——headless 不可用）。数据库目录结构：
 *   <data_dir>/<taxScope>/eggnog.db + <taxScope>.dmnd + taxa 文件
 *   （也可用官方 eggNOG-mapper 的 eggNOG_db 目录，经 --eggnog_db/--tax_db 指定）
 */
public class EggnogCli {
    public static void main(String[] args) throws Exception {
        if (args.length == 0) {
            System.err.println("用法: EggnogCli <in.fa> -o <prefix> --output_dir <outDir> --data_dir <eggNOGdb> [--dmnd_db <db>] [--cpu N] [--evalue 0.001] [--override]");
            System.err.println("     传参方式与 GUI 完全一致（-m diamond 为默认模式）");
            System.exit(1);
        }
        eggnogmapper.cli.CliArgs cli = eggnogmapper.cli.CliParser.parse(args);
        if (cli.help) {
            eggnogmapper.cli.CliParser.printHelp();
            System.exit(0);
        }
        if (cli.inputPath == null) {
            System.err.println("❌ 缺少输入文件（-i <in.fa>）");
            System.exit(1);
        }
        eggnogmapper.emapper.EmapperPipeline pipeline = new eggnogmapper.emapper.EmapperPipeline(cli);
        pipeline.run();
        System.err.println("[tbplot] eggNOG-mapper 完成");
        System.exit(0);
    }
}
