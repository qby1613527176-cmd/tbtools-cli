#!/usr/bin/env bash
# ============================================================
# tbtools_rpc.sh — TBtools-II 2.535 RPC CLI 封装
# 08/28 实测打通：TBtools RPC 服务 → jsonrpc 2.0 → 绘图/分析
# 服务器: java -cp TBtools_JRE1.6.jar biocjava.rpc.RpcServer (默认 127.0.0.1:8765)
# 端点: GET /health  POST /rpc  {"jsonrpc":"2.0","method":"...","params":{...}}
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
# shellcheck disable=SC1091
source "$ROOT/config/config.sh"
TBTOOLS_JAR="${TBTOOLS_JAR}"
RPC_URL="${TBTOOLS_RPC_URL:-http://127.0.0.1:8765/rpc}"
# ⚠️ HEALTH_URL 不能直接用 TBTOOLS_RPC_URL（config.sh 导出的是 .../rpc，兜底永不生效→健康检查打到 /rpc 永远失败，08/31 盲测 P0 bug）
# 正确：剥掉 /rpc 后缀拼 /health
HEALTH_URL="${RPC_URL%/rpc}/health"
RPC_PORT="${TBTOOLS_RPC_PORT:-8765}"

# ---------- 工具函数 ----------
rpc_call() {
    # 用法: rpc_call <method> <json-params>
    local method="$1"
    # ⚠️ 不能写 "${2:-{}}"：bash 会把参数值多加一个 }，导致 JSON 畸形（09/01 全量测试发现）；
    #    `${2:-}` 空默认无歧义，再显式补 {}
    local params="${2:-}"
    [ -z "$params" ] && params="{}"
    curl -s -X POST "$RPC_URL" \
        -H "Content-Type: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"method\":\"$method\",\"params\":$params}"
}

start_server() {
    if curl -s --max-time 2 "$HEALTH_URL" | grep -q "OK"; then
        echo "✅ RPC 服务器已在运行: $HEALTH_URL" >&2
        return 0
    fi
    echo "🚀 启动 TBtools RPC 服务器 (端口 $RPC_PORT)..." >&2
    nohup java -Xmx4g -cp "$TBTOOLS_JAR" biocjava.rpc.RpcServer \
        > /tmp/tbtools_rpc_server.log 2>&1 &
    local pid=$!
    # 等待健康检查
    for i in $(seq 1 15); do
        sleep 1
        if curl -s --max-time 2 "$HEALTH_URL" | grep -q "OK"; then
            echo "✅ RPC 服务器就绪 (PID $pid): $HEALTH_URL" >&2
            return 0
        fi
    done
    echo "❌ RPC 服务器启动超时，日志: /tmp/tbtools_rpc_server.log" >&2
    return 1
}

usage() {
    echo "TBtools-II RPC CLI — 用法:"
    echo "  tbtools_rpc.sh start                 # 启动 RPC 服务器"
    echo "  tbtools_rpc.sh methods               # 列出全部可用方法"
    echo "  tbtools_rpc.sh describe <方法名>      # 查看某方法参数"
    echo "  tbtools_rpc.sh call <方法名> '<json>' # 直接调用 (params JSON)"
    echo "  tbtools_rpc.sh heatmap <矩阵> <输出> [分组文件]  # 热图快捷"
    echo ""
    echo "示例:"
    echo "  tbtools_rpc.sh heatmap matrix.tsv out.png rowgroup.tsv"
    echo "  tbtools_rpc.sh call AmazingFastaExtract.process '{\"inputPath\":\"in.fa\",\"idListPath\":\"ids.txt\",\"outputPath\":\"out.fa\"}'"
    echo ""
    echo "环境变量: TBTOOLS_RPC_URL / TBTOOLS_RPC_PORT / TBTOOLS_JAR"
}

# ---------- 主命令 ----------
CMD="${1:-}"
case "$CMD" in
    start)
        start_server
        ;;
    methods|list)
        start_server
        rpc_call "system.listMethods" | python3 -m json.tool 2>/dev/null || rpc_call "system.listMethods"
        ;;
    describe)
        [ $# -ge 2 ] || { echo "需要方法名"; exit 1; }
        start_server
        rpc_call "system.describeMethod" "{\"method\":\"$2\"}" | python3 -m json.tool 2>/dev/null || rpc_call "system.describeMethod" "{\"method\":\"$2\"}"
        ;;
    call)
        [ $# -ge 3 ] || { echo "用法: tbtools_rpc.sh call <方法名> '<json>'"; exit 1; }
        start_server
        rpc_call "$2" "$3" | python3 -m json.tool 2>/dev/null || rpc_call "$2" "$3"
        ;;
    heatmap)
        [ $# -ge 3 ] || { echo "用法: tbtools_rpc.sh heatmap <矩阵> <输出.png> [分组文件]"; exit 1; }
        start_server
        matrix="$(realpath "$2")"; out="$(realpath "$3")"; group="${4:-}"
        # 用 Python 构造 JSON，避免 bash 引号转义问题
        params=$(python3 -c "
import json, sys
opts = {'showWindow': False}
if '$group':
    opts['rowGroupPath'] = '$group'
print(json.dumps({'matrixPath': '$matrix', 'outputPath': '$out', 'options': opts}))
")
        rpc_call "AmazingHeatMap.process" "$params"
        ;;
    *)
        usage
        ;;
esac