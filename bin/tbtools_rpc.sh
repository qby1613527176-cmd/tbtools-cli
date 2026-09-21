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

# ---------- N34/N35 自愈：pid 文件 + 崩溃转储（与 tbtools rpc 命令一致）----------
RPC_DIR="${TBTOOLS_RPC_DIR:-$HOME/.config/tbtools-cli}"
mkdir -p "$RPC_DIR"
PID_FILE="$RPC_DIR/rpc-$RPC_PORT.pid"
LOG_FILE="$RPC_DIR/rpc-$RPC_PORT.log"

pid_alive() {
    # 读 pid 文件并确认是 RPC server 进程；不是则清 stale 返回 1
    [ -f "$PID_FILE" ] || return 1
    local pid
    pid=$(cat "$PID_FILE" 2>/dev/null) || return 1
    if kill -0 "$pid" 2>/dev/null; then
        if [ -r "/proc/$pid/cmdline" ] && ! grep -aq "biocjava.rpc.RpcServer" "/proc/$pid/cmdline"; then
            rm -f "$PID_FILE"; return 1
        fi
        echo "$pid"; return 0
    fi
    rm -f "$PID_FILE"; return 1
}

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
    # 健康检查失败但 pid 还在 → 引擎假死/僵尸（N35 502 伪装场景），杀掉重拉
    local old_pid
    if old_pid=$(pid_alive); then
        echo "⚠️ 旧 RPC 进程 (PID $old_pid) 无响应，终止后重拉..." >&2
        kill "$old_pid" 2>/dev/null || true
        rm -f "$PID_FILE"
        sleep 1
    fi
    echo "🚀 启动 TBtools RPC 服务器 (端口 $RPC_PORT)..." >&2
    # N35: OOM 宁可崩溃（可自愈）也不僵尸悬挂；留堆转储供排查
    nohup java -Xmx4g \
        -XX:+CrashOnOutOfMemoryError \
        -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath="$RPC_DIR" \
        -cp "$TBTOOLS_JAR" biocjava.rpc.RpcServer \
        > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    # 等待健康检查
    for _ in $(seq 1 30); do   # SC2034: i 未使用
        sleep 1
        if curl -s --max-time 2 "$HEALTH_URL" | grep -q "OK"; then
            echo "✅ RPC 服务器就绪 (PID $pid): $HEALTH_URL" >&2
            return 0
        fi
        # 进程已死（启动即崩）→ 不必等满
        if ! kill -0 "$pid" 2>/dev/null; then
            echo "❌ RPC 服务器启动后退出，日志: $LOG_FILE" >&2
            rm -f "$PID_FILE"
            return 1
        fi
    done
    echo "❌ RPC 服务器启动超时，日志: $LOG_FILE" >&2
    return 1
}

stop_server() {
    local pid
    if pid=$(pid_alive); then
        kill "$pid" && echo "✅ 已停止 RPC 服务器 (PID $pid)" >&2
    else
        echo "RPC 服务器未在运行（端口 $RPC_PORT）" >&2
    fi
    rm -f "$PID_FILE"
}

usage() {
    echo "TBtools-II RPC CLI — 用法:"
    echo "  tbtools_rpc.sh start                 # 启动 RPC 服务器"
    echo "  tbtools_rpc.sh stop                  # 停止 RPC 服务器"
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
    stop)
        stop_server
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