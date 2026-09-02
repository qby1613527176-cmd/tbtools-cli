#!/usr/bin/env bash
# ============================================================
# tbtools-cli 安装脚本
# 用法: ./install.sh [--jar <TBtools.jar 路径>]
# ============================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$ROOT/bin"

echo "=============================================="
echo " tbtools-cli 安装"
echo "=============================================="

# ---------- 1. 查找/设置 TBtools jar ----------
JAR=""
# 解析 --jar 参数
while [ $# -gt 0 ]; do
    case "$1" in
        --jar) JAR="$2"; shift 2;;
        *) [ -z "$JAR" ] && [ -f "$1" ] && JAR="$1"; shift;;
    esac
done
if [ -z "$JAR" ]; then
    JAR="${TBTOOLS_JAR:-}"
fi
if [ -z "$JAR" ] || [ ! -f "$JAR" ]; then
    echo ""
    echo "⚠️  未找到 TBtools_JRE1.6.jar"
    echo ""
    echo "  需要下载 TBtools-II 2.535+ 主 jar："
    echo "    - GitHub:  https://github.com/CJ-Chen/TBtools/releases"
    echo "    - 官网:    https://www.tbtools.com"
    echo ""
    echo "  下载后请重新运行:"
    echo "    ./install.sh --jar /path/to/TBtools_JRE1.6.jar"
    echo "    或设置环境变量: export TBTOOLS_JAR=/path/to/TBtools_JRE1.6.jar"
    exit 1
fi

# 写入用户配置文件
mkdir -p "$HOME/.config/tbtools-cli"
cat > "$HOME/.config/tbtools-cli/config.sh" << EOF
export TBTOOLS_JAR="$JAR"
EOF
echo "✅ TBtools jar 配置写入: $HOME/.config/tbtools-cli/config.sh"
echo "   $JAR"

# ---------- 2. 创建 bin 软链 ----------
if [ -d "$HOME/.local/bin" ]; then
    ln -sf "$BIN/tbtools" "$HOME/.local/bin/tbtools"
    ln -sf "$BIN/tbplot.sh" "$HOME/.local/bin/tbplot.sh"
    echo "✅ 已创建软链: $HOME/.local/bin/tbtools"
else
    echo "ℹ️  未找到 ~/.local/bin，可手动软链:"
    echo "   ln -s $BIN/tbtools /usr/local/bin/tbtools"
fi

# ---------- 3. 检查 Java ----------
if command -v java >/dev/null 2>&1; then
    echo "✅ Java: $(java -version 2>&1 | head -1)"
else
    echo "⚠️  未找到 java，请安装 JDK 11+"
fi

# ---------- 2b. 检查 xvfb-run（绘图必需）----------
if ! command -v xvfb-run >/dev/null 2>&1; then
    echo "⚠️  未找到 xvfb-run（绘图引擎需要），安装: sudo apt install xvfb"
fi

# ---------- 2c. 检查可选依赖 ----------
for dep in samtools blastp muscle iqtree2 meme mast RNAfold minimap2; do
    command -v "$dep" >/dev/null 2>&1 && echo "  ✅ $dep ($(command -v $dep))" || true
done

# ---------- 4. 测试 ----------
echo ""
echo "=============================================="
echo " 测试: tbtools help"
echo "=============================================="
if "$BIN/tbtools" help >/dev/null 2>&1; then
    echo "✅ 安装成功！运行 'tbtools help' 查看用法"
else
    echo "❌ 测试失败，请检查依赖"
    exit 1
fi

echo ""
echo "完成。快速开始:"

echo "  bash run_examples.sh       # 一键验证（8项核心功能）"
echo "  tbtools help                # 查看全部命令"
echo "  tbtools seqlogo seqs.fa logo.svg   # 序列 LOGO 图"
echo "  tbtools server start        # 启动 RPC（数据工具）"
