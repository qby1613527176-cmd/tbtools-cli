#!/usr/bin/env python3
"""
tbcli — TBtools-II 2.535 全功能 CLI 统一入口（完整版）
======================================================
覆盖三层：
  1. RPC 层（188 方法）→ 127.0.0.1:8765 JSON-RPC（主干，全部可调用）
  2. 命令行注册工具（54 个）→ java -jar jar <工具名> 或映射类名
  3. JIGplot 绘图引擎（26+ 枚举 + 任意类 tbengine 反射）

用法：
  tbcli list rpc              # 188 个 RPC 方法
  tbcli list tools            # 命令行工具
  tbcli list plots            # 绘图功能
  tbcli rpc <method> '<json>' # 调用任意 RPC（全功能主干）
  tbcli tool <名称> [参数...]   # 命令行工具
  tbcli plot <图名> [参数...]   # 绘图引擎
  tbcli engine <类名> [k=v...] # 任意引擎反射调用（tbengine.sh）
  tbcli server start|stop     # RPC 服务器管理
"""

VERSION = "1.0.0"

import subprocess, sys, json, os, re, urllib.request

JAR = os.environ.get("TBTOOLS_JAR", "")
RPC = "http://127.0.0.1:8765/rpc"
HOME = os.path.expanduser("~")
# 项目根目录：脚本在 <root>/bin/，向上两级
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
SCRIPTS = os.path.join(ROOT, "bin")

# 若环境变量未设置，尝试从 config.sh 读取默认值（bash source 解析，兼容 $cand 变量）
if not JAR:
    try:
        import subprocess as _sp
        out = _sp.check_output(
            ["bash", "-c", f"source {os.path.join(ROOT, 'config', 'config.sh')} 2>/dev/null; echo \"$TBTOOLS_JAR\""],
            text=True, timeout=10)
        v = out.strip().splitlines()[-1] if out.strip() else ""
        if v and os.path.exists(v):
            JAR = v
    except Exception:
        pass

if not JAR:
    try:
        with open(os.path.join(ROOT, "config", "config.sh")) as f:
            for line in f:
                if line.startswith("TBTOOLS_JAR=") and '"$HOME' not in line:
                    v = line.split("=", 1)[1].strip().strip('"')
                    if os.path.exists(v):
                        JAR = v
    except Exception:
        pass

if not JAR or not os.path.exists(JAR):
    print("❌ 未找到 TBtools jar。请设置环境变量 TBTOOLS_JAR 指向 TBtools_JRE1.6.jar", file=sys.stderr)
    sys.exit(1)

CLI_TOOLS = {
    "DecodeIlluminaFqPool": "biocjava.bioDoer.Fastq.DecodeIlluminaFqPool",
    "fastaIDAppender": "biocjava.bioIO.FastX.FastaIndex.FastaIDAppender",
    "rpkmCal": "biocjava.bioDoer.ExpressionLevelCalculator.RPKMcalculator",
    "fpkmToTpm": "biocjava.bioDoer.ExpressionLevelCalculator.FPKMtoTPM",
    "tpmCalc": "biocjava.bioDoer.ExpressionLevelCalculator.TPMcalculator",
    "mimicVqsr": "biocjava.bioDoer.GWAS.MimicVqsrCutoffFind",
    "autoMakeBlastDb": "biocjava.bioDoer.BLAST.makeblastdb",
    "autoRemoteBlast": "biocjava.bioDoer.BLAST.remoteblast",
    "GoCompareBar": "biocjava.bioDoer.GeneOntology.Grapher.GoCompare",
    "plotRNAfoldloci": "biocjava.bioDoer.JIGplotToolkit.miRCoverage.PlotRNAfold",
    "getLongestCompleteORF": "biocjava.bioIO.ORF.ORF",
    "ExtractFeaturefromGFF3andGenome": "biocjava.bioIO.GFF.ExtractFeaturefromGFF3andGenome",
    "Fasta36m10toTable": "biocjava.bioIO.FastaAligner.Fasta36m10toTable",
    "FastaIDRenamer": "biocjava.bioIO.FastX.FastaIndex.FastaIDRenamer",
    "FastaIDSimplifier": "biocjava.bioIO.FastX.FastaIndex.FastaIDSimplifier",
    "FastaLongestRepresentater": "biocjava.bioIO.FastX.FastaIndex.FastaLongestRepresentater",
    "FoldStructureStater": "biocjava.bioIO.RNAfold.FoldStructureStater",
    "GXFOverlaper": "biocjava.bioDoer.GXFUtils.GXFOverlaper",
    "NCBITaxonomy": "biocjava.bioWeb.NCBITaxonomy.NCBITaxonomy",
    "OneStepMirGraph": "biocjava.bioIO.RNAfold.OneStepMirGraph",
    "OverlapGeneModels": "biocjava.bioIO.GXF.gxfTree.OverlapGeneModels",
    "PredictMirSTAR": "biocjava.bioIO.RNAfold.PredictMirSTAR",
    "RNAplotAdvance": "biocjava.bioDoer.JIGplotToolkit.miRCoverage.RNAplotAdvance",
    "MIRPrediionResultStat": "biocjava.bioDoer.miRNA.MIRPrediionResultStat",
    "ReciprocalBlast": "biocjava.bioDoer.BLAST.ReciprocalBlast.ReciprocalBlast",
    "RegionGXFOverlapAnnotation": "biocjava.bioDoer.GXFUtils.RegionGXFOverlapAnnotation",
    "TableCast": "biocjava.bioDoer.Table.TableCast",
    "TableColSelector": "biocjava.bioDoer.Table.TableColSelector",
    "TableMelt": "biocjava.bioDoer.Table.TableMelt",
    "downLoadNCBIFasta": "biocjava.bioWeb.DownLoadNCBIFasta",
    "extractFasta": "biocjava.bioDoer.Fasta.ExtractFasta",
    "extractFastaSub": "biocjava.bioDoer.Fasta.ExtractFastaSubseq",
    "keggEnrichment": "biocjava.bioDoer.Kegg.AdvancedForEnrichment.KeggEnrichment",
    "goAnnoPipe": "biocjava.bioDoer.GeneOntology.Annotation.GoAnnoPipe",
    "dnDsCalculate": "biocjava.bioIO.KaKs.DnDsCalculate",
    "ssrMiner": "biocjava.bioIO.FastX.FastaIndex.SSRminer",
    "checkPrimer": "biocjava.bioIO.Primer.CheckPrimer",
    "quickLocateSeqPattern": "biocjava.bioIO.FastX.QuickLocateSeqPattern",
    "blastXmlSummaryTable": "biocjava.bioIO.BlastXml.BlastXMLSummaryTable",
    "emblToFasta": "biocjava.bioIO.Embl.emblToFasta",
    "gbff2gff": "biocjava.bioIO.GBff.gbff2gff",
    "extractGff3Region": "biocjava.bioIO.GFF.ExtractGff3Region",
    "vcfBinCount": "biocjava.bioIO.HTSData.VCF.VCFBINCount",
    "getLongestORF": "biocjava.bioIO.ORF.GetLongestORF",
    "translater": "biocjava.bioIO.ORF.Translater",
    "makeFastaIndex": "biocjava.bioIO.FastX.FastaIndex.MakeFastaIndex",
    "quickSplitFasta": "biocjava.bioIO.FastX.FastaIndex.QuickSpiltFasta",
    "fastaFragmenter": "biocjava.bioIO.FastX.FastaIndex.Fragment.FastaFragmenter",
    "eggNogMapperResult": "biocjava.bioIO.BioSoftPipeServer.eggNogMapperResult",
    "tandemDupFinder": "biocjava.bioIO.BioSoftPipeServer.TandemDupFinder",
    "genePairExpCorr": "biocjava.bioIO.BioSoftPipeServer.GenePairExpCorr",
    "slurmScriptPrepare": "biocjava.bioIO.BioSoftPipeServer.SlurmScriptPrepare",
    "geneExpFilter": "biocjava.bioIO.BioSoftPipeServer.GeneExpFilter",
    "prepareFileFromMCScanXtoTBtools": "biocjava.bioDoer.JIGplotToolkit.Synteny.PrepareFileFromMCScanXtoTBtools",
    "blastXmlToTable": "biocjava.bioIO.BlastXml.BlastXmlToSelfDefinedTable",
    "targetSoPipe": "biocjava.bioDoer.miRNA.TargetSoPipe",
    "target2TablePipe": "biocjava.bioDoer.miRNA.Target2TablePipe",
    "mirIdentifierBasedOnTargetSo": "biocjava.bioDoer.miRNA.MIRidentifierBasedOnTargetSoResult",
    "regionBlast": "biocjava.bioDoer.BLAST.wholeGenomeBlastN.regionBlast",
    "findBestHomologyBatch": "biocjava.bioIO.BioSoftPipeServer.FindBestHomologyBatch",
    "collinearityToRegion": "biocjava.bioDoer.ComparativeGenomics.MCScanX.CollinearityToRegion",
    "pairWiseKaKsCalculator": "biocjava.bioIO.BioSoftPipeServer.PairWiseKaKsCalculator",
    "simpleBatchProcess": "biocjava.bioDoer.Aligner.NeedleMan.SimpleBatchProcess",
    "quickGeneFamilyIdentification": "biocjava.bioDoer.BLAST.ReciprocalBlast.QuickGeneFamilyIdentification",
    "gffCdsPhaseCorrector": "biocjava.bioDoer.GXFUtils.GffCdsPhase.GffCdsPhaseCorrector",
    "parallelMD5Check": "biocjava.bioDoer.FileUtils.ParallelMD5Check",
    "pafRefBaseCoverCalc": "biocjava.bioDoer.JIGplotToolkit.Paf.PafRefBaseCoverCalc",
    "sRNAseqReadLenStat": "biocjava.sRNA.Tools.sRNAseqReadLenStat",
    "sRNAReadTrimmer": "biocjava.sRNA.Tools.sRNAReadTrimmer",
    "sRNAseqAdaperRemover": "biocjava.sRNA.Tools.sRNAseqAdaperRemover",
    "fastqParallelTrimmer": "biocjava.bioDoer.Fastq.FastqParallelTrimmer",
    "fastqParallelSubBest": "biocjava.bioDoer.Fastq.FastqParallelSubBest",
    "fastqAndFasta": "biocjava.bioDoer.LinuxPipe.FastqAndFasta",
    "extractFeatureFromGTF": "biocjava.bioIO.GTF.ExtractFeaturefromGTFandGenome",
    "sRNAseqCollasper": "biocjava.sRNA.Tools.sRNAseqCollasper",
    "generateMotifFromSequences": "biocjava.bioIO.BioSoftPipeServer.MEMEsuiteWrapper.GenerateMotifFromSequences",
    "sRNAseqDeCollasper": "biocjava.sRNA.Tools.sRNAseqDeCollasper",
    "findBestForkerRootTree": "biocjava.bioDoer.JIGplotToolkit.newickParser.FindBestForkerRootTree",
    "statFasta": "biocjava.bioIO.FastX.FastaIndex.QuickStatFasta",
    "goEnrichMerge": "biocjava.bioDoer.JIGplotToolkit.EnrichmentAnalysisGraph.GOEnrichmentMergeBubble",
    "vcfAddID": "biocjava.bioDoer.GWAS.VCFAddID",
    "bigMarkerRandomDesign": "biocjava.bioDoer.markerDesign.BigMarkerRandomDesign"
}


def rpc_call(method, params=None):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())

def server_running():
    try:
        with urllib.request.urlopen("http://127.0.0.1:8765/health", timeout=2) as r:
            return b"OK" in r.read()
    except Exception:
        return False

def start_server():
    if server_running():
        print("✅ RPC 服务器已在运行"); return
    print("🚀 启动 RPC 服务器...")
    subprocess.Popen(["java", "-Xmx4g", "-cp", JAR, "biocjava.rpc.RpcServer"],
                     stdout=open("/tmp/tbtools_rpc_server.log", "w"), stderr=subprocess.STDOUT)
    import time
    for _ in range(25):
        time.sleep(1)
        if server_running(): print("✅ 就绪: 127.0.0.1:8765"); return
    print("❌ 启动超时")

def stop_server():
    os.system("ps aux | grep '[R]pcServer' | awk '{print $2}' | xargs -r kill")
    print("✅ 已停止")

def cmd_list(kind):
    if kind == "rpc":
        if not server_running(): start_server()
        m = rpc_call("system.listMethods").get("result", {}).get("methods", [])
        print(f"RPC 方法: {len(m)}"); [print(f"  {x}") for x in m]
    elif kind == "tools":
        print(f"命令行工具: {len(CLI_TOOLS)}"); [print(f"  {k} -> {v}") for k, v in sorted(CLI_TOOLS.items())]
    elif kind == "plots":
        # 绘图命令列表来自 tbplot.sh（真实可用入口）
        try:
            cmds = []
            for line in open(os.path.join(SCRIPTS, "tbplot.sh")):
                mo = re.match(r"^  ([a-zA-Z][a-zA-Z0-9]+)\)", line)
                if mo: cmds.append(mo.group(1))
            print(f"绘图: {len(cmds)} 个（tbplot.sh）"); [print(f"  {x}") for x in sorted(cmds)]
        except Exception as e:
            print(f"⚠️ 无法读取 tbplot.sh: {e}")
    elif kind == "all":
        cmd_list("rpc"); cmd_list("tools"); cmd_list("plots")

def cmd_rpc(method, params_json):
    if not server_running(): start_server()
    params = json.loads(params_json) if params_json else {}
    print(json.dumps(rpc_call(method, params), ensure_ascii=False, indent=2))

def _run_tool(java_cmd, tool_name):
    """执行 java 工具命令，失败时输出友好错误提示"""
    import subprocess, tempfile, os
    _err_file = tempfile.mktemp(prefix="tbtools_err.")
    r = subprocess.run(java_cmd, shell=True, stderr=open(_err_file, "w"))
    if r.returncode != 0:
        print("", file=sys.stderr)
        print(f"❌ 执行失败（退出码 {r.returncode}）", file=sys.stderr)
        # 提取异常关键行
        import re
        with open(_err_file) as f:
            lines = f.readlines()
        exc_lines = [l.rstrip() for l in lines if re.match(r'^(Exception in thread|Caused by:|Error:|\[Error\])', l)]
        if exc_lines:
            for l in exc_lines[:3]:
                print(f"   {l}", file=sys.stderr)
        else:
            # 取最后 3 行非空
            nonblank = [l.rstrip() for l in lines if l.strip()]
            for l in nonblank[-3:]:
                print(f"   {l}", file=sys.stderr)
        print("", file=sys.stderr)
        # 智能异常分类
        _hint = "参数缺失/格式不对/文件路径错误/数据不匹配"
        _err_text = open(_err_file).read()
        if "FileNotFoundException" in _err_text:
            _hint = "文件不存在或路径错误，检查输入文件路径"
        elif "NullPointerException" in _err_text:
            _hint = "可能缺少必需参数或数据格式不匹配"
        elif "NumberFormatException" in _err_text:
            _hint = "数据格式不匹配，检查输入文件列数/类型/分隔符"
        elif "ArrayIndexOutOfBoundsException" in _err_text:
            _hint = "可能缺少必需参数或输入数据行列数不足"
        print(f"   💡 {_hint}", file=sys.stderr)
        print(f"   📖 查看帮助: tbtools list tools 或 docs/COMMAND_REFERENCE.md", file=sys.stderr)
        print(f"   🔍 完整堆栈: {_err_file}", file=sys.stderr)
        print("", file=sys.stderr)
    else:
        # 成功时输出引擎进度信息到 stderr
        try:
            with open(_err_file) as f:
                import sys as _sys
                _sys.stderr.write(f.read())
        except: pass
    try: os.unlink(_err_file)
    except: pass
    return r.returncode

def cmd_tool(name, args):
    cls = CLI_TOOLS.get(name)
    if cls:
        # 有映射: 直接 java -cp 调类
        print(f"▶ {name} -> {cls}")
        if not args:
            # 无参数时先尝试 --help（ArgsParser 工具有 Usage）
            r = subprocess.run(f"java -Xmx2g -cp {JAR} {cls} --help", 
                             shell=True, capture_output=True, text=True, timeout=10)
            if r.returncode != 0 or not r.stderr.strip():
                # --help 不行就试无参（有些引擎有 ArgsParser 会自动报 Usage）
                pass
            else:
                print(r.stderr, file=sys.stderr)
                print(f"\n💡 上面是 {name} 的参数说明，或查看: docs/COMMAND_REFERENCE.md", file=sys.stderr)
                sys.exit(1)
        sys.exit(_run_tool(f"java -Xmx4g -cp {JAR} {cls} {' '.join(args)}", name))
    else:
        # 无映射: 先校验类在 jar 中真实存在，避免拼错名直接启动官方 jar 倾倒配置挂死（08/31 盲测 P1）
        found = _class_in_jar(name)
        if not found:
            print(f"❌ 未知工具: {name}", file=sys.stderr)
            print(f"请用 tbtools list tools 查看可用工具（{len(CLI_TOOLS)} 个）", file=sys.stderr)
            sys.exit(1)
        print(f"▶ {name} -> 官方 Arg 模式 (java -jar jar {name})")
        sys.exit(_run_tool(f"java -Xmx4g -jar {JAR} {name} {' '.join(args)}", name))

def _class_in_jar(name):
    """校验工具名在 TBtools jar 中是否有对应类（避免拼错名启动官方 jar）"""
    import subprocess
    try:
        r = subprocess.run(["unzip", "-l", JAR], capture_output=True, text=True, timeout=10)
        return any(name.lower() in line.lower() for line in r.stdout.splitlines())
    except Exception:
        # unzip 不可用/异常时保守放行（保留原行为）
        return True

def cmd_plot(name, args):
    # 绘图引擎统一走 tbplot.sh 桥（绘图类无 main，必须经桥 headless 化）
    os.system(f"bash {SCRIPTS}/tbplot.sh {name} {' '.join(args)}")

def cmd_engine(cls, kvs):
    os.system(f"bash {SCRIPTS}/tbengine.sh {cls} {' '.join(kvs)}")

def cmd_version():
    print(f"tbtools-cli v{VERSION}")
    print(f"  140 绘图命令 + 82 CLI 工具 + 188 RPC 方法")
    print(f"  bridges: 80 | engines: 123 | 坑位: 35")
    import subprocess
    try:
        r = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=5)
        java_ver = r.stderr.split("\n")[0] if r.stderr else "unknown"
        print(f"  Java: {java_ver}")
    except: print("  Java: not found")
    jar = os.environ.get("TBTOOLS_JAR", "")
    if jar and os.path.isfile(jar):
        print(f"  JAR: {jar}")
    else:
        print(f"  JAR: ⚠️ 未配置（运行 tbtools doctor 排查）")

def cmd_doctor():
    import subprocess, shutil
    print("tbtools-cli 环境诊断")
    print("=" * 40)
    ok = 0; warn = 0; err = 0
    
    # Java
    if shutil.which("java"):
        r = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=5)
        ver = r.stderr.split("\n")[0] if r.stderr else "?"
        print(f"  ✅ Java: {ver}")
        ok += 1
    else:
        print("  ❌ Java: 未安装（需要 JDK 11+）")
        err += 1
    
    # javac
    if shutil.which("javac"):
        print("  ✅ javac: 可用")
        ok += 1
    else:
        print("  ⚠️ javac: 未安装（编译桥需要）")
        warn += 1
    
    # xvfb-run
    if shutil.which("xvfb-run"):
        print("  ✅ xvfb-run: 可用（绘图必需）")
        ok += 1
    else:
        print("  ❌ xvfb-run: 未安装（绘图引擎需要，apt install xvfb）")
        err += 1
    
    # JAR
    jar = os.environ.get("TBTOOLS_JAR", "")
    if jar and os.path.isfile(jar):
        size_mb = os.path.getsize(jar) / 1024 / 1024
        print(f"  ✅ JAR: {jar} ({size_mb:.0f}MB)")
        ok += 1
    else:
        # 尝试常见位置
        import os.path as op
        cands = [
            op.expanduser("~/tbtools-cli/lib/TBtools_JRE1.6.jar"),
            op.expanduser("~/Downloads/TBtools_JRE1.6.jar"),
            op.expanduser("~/下载/TBtools_JRE1.6.jar"),
            "/opt/TBtools/TBtools_JRE1.6.jar",
        ]
        found = [c for c in cands if op.isfile(c)]
        if found:
            print(f"  ✅ JAR: {found[0]}（建议设置 TBTOOLS_JAR）")
            ok += 1
        else:
            print("  ❌ JAR: 未找到（下载 TBtools_JRE1.6.jar）")
            err += 1
    
    # 可选依赖
    optional = {
        "samtools": "SAM/BAM 处理", "blastp": "BLAST 比对", "muscle": "多序列比对",
        "iqtree2": "系统发育建树", "meme": "Motif 发现", "mast": "Motif 扫描",
        "RNAfold": "RNA 二级结构", "minimap2": "基因组比对",
    }
    avail = []
    for dep, desc in optional.items():
        path = shutil.which(dep)
        if path:
            avail.append(f"{dep}({desc})")
    if avail:
        print(f"  ✅ 可选依赖: {', '.join(avail[:5])}")
        ok += 1
    else:
        print("  ℹ️ 可选依赖: 无（部分命令需要 samtools/blastp/muscle/iqtree2/meme 等）")
    
    print()
    print(f"  汇总: ✅ {ok}  ⚠️ {warn}  ❌ {err}")
    if err > 0:
        print("  ❌ 有致命问题，请按上述提示修复。")
        sys.exit(1)
    elif warn > 0:
        print("  ⚠️ 有警告，部分功能可能不可用。")
    else:
        print("  ✅ 环境完全就绪！")
    sys.exit(0)

def usage():
    print(__doc__.split("用法：")[1])

if __name__ == "__main__":
    if len(sys.argv) < 2: usage(); sys.exit(0)
    c = sys.argv[1]
    if c == "list" and len(sys.argv) >= 3: cmd_list(sys.argv[2])
    elif c == "rpc" and len(sys.argv) >= 3: cmd_rpc(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif c == "tool" and len(sys.argv) >= 3: cmd_tool(sys.argv[2], sys.argv[3:])
    elif c == "plot" and len(sys.argv) >= 3: cmd_plot(sys.argv[2], sys.argv[3:])
    elif c == "engine" and len(sys.argv) >= 3: cmd_engine(sys.argv[2], sys.argv[3:])
    elif c == "server" and len(sys.argv) >= 3: (start_server if sys.argv[2] == "start" else stop_server)()
    elif c == "version" or c == "--version" or c == "-v": cmd_version()
    elif c == "doctor": cmd_doctor()
    else: usage()
