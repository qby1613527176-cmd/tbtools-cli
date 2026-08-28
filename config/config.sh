#!/usr/bin/env bash
# ============================================================
# tbtools-cli 统一配置
# 所有脚本通过 source 此文件获取路径配置
#
# 优先级：环境变量 > 本文件默认值
#   1. 命令行/环境变量（TBTOOLS_JAR / TBTOOLS_JAVA / TBTOOLS_RPC_PORT ...）
#   2. 用户配置文件 ~/.tbtools-cli/config.sh
#   3. 本文件默认值
# ============================================================

# ---------- 项目根目录（自动检测，支持软链）----------
TBTOOLS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ---------- 用户配置文件（最高优先级，install.sh 写入）----------
if [ -f "$HOME/.config/tbtools-cli/config.sh" ]; then
    # shellcheck disable=SC1090
    source "$HOME/.config/tbtools-cli/config.sh"
fi

# ---------- TBtools jar（核心依赖）----------
# 优先级：环境变量 TBTOOLS_JAR > 用户配置 > 常见位置查找
# 获取方式：https://github.com/CJ-Chen/TBtools 或 TBtools 官网下载 TBtools_JRE1.6.jar
if [ -z "${TBTOOLS_JAR:-}" ]; then
    for cand in \
        "$HOME/tbtools-cli/lib/TBtools_JRE1.6.jar" \
        "$HOME/TBtools/TBtools_JRE1.6.jar" \
        "/mnt/d/shengwu/TBtools/TBtools_JRE1.6.jar" \
        "/opt/TBtools/TBtools_JRE1.6.jar" \
        ; do
        if [ -f "$cand" ]; then TBTOOLS_JAR="$cand"; break; fi
    done
fi
export TBTOOLS_JAR

# ---------- Java 可执行 ----------
if [ -z "${TBTOOLS_JAVA:-}" ]; then
    if [ -n "${JAVA_HOME:-}" ]; then
        TBTOOLS_JAVA="$JAVA_HOME/bin/java"
    else
        TBTOOLS_JAVA="java"
    fi
fi
export TBTOOLS_JAVA

# ---------- Java 内存 ----------
export TBTOOLS_JAVA_MEM="${TBTOOLS_JAVA_MEM:--Xmx4g}"

# ---------- RPC 服务器 ----------
export TBTOOLS_RPC_PORT="${TBTOOLS_RPC_PORT:-8765}"
export TBTOOLS_RPC_URL="http://127.0.0.1:${TBTOOLS_RPC_PORT}/rpc"

# ---------- 桥源码目录 ----------
TBTOOLS_BRIDGES="${TBTOOLS_ROOT}/bridges"

# ---------- 构建目录（编译产物，可清）----------
TBTOOLS_BUILD="${TBTOOLS_ROOT}/build"

# ---------- 工具函数：检查 jar ----------
tbtools_check_jar() {
    if [ ! -f "${TBTOOLS_JAR:-}" ]; then
        echo "❌ 未找到 TBtools jar: ${TBTOOLS_JAR:-}" >&2
        echo "   请设置 TBTOOLS_JAR 环境变量，或下载后放到 lib/ 目录" >&2
        echo "   下载: https://github.com/CJ-Chen/TBtools/releases" >&2
        return 1
    fi
    return 0
}

# ---------- 工具函数：编译桥（源 → build/）----------
tbtools_build_bridge() {
    local src="$1"
    local name
    name="$(basename "${src%.java}")"
    mkdir -p "$TBTOOLS_BUILD"
    # 只在源码更新时重新编译
    if [ ! -f "$TBTOOLS_BUILD/$name.class" ] || [ "$src" -nt "$TBTOOLS_BUILD/$name.class" ]; then
        "${TBTOOLS_JAVA:-java}" -version >/dev/null 2>&1 || true
        javac -cp "$TBTOOLS_JAR" -d "$TBTOOLS_BUILD" "$src" 2>/dev/null || {
            echo "⚠️ 编译 $name 失败，尝试 javac 完整路径..." >&2
            # 尝试从 JDK 找 javac
            local jdk_javac
            for jdk_javac in "$JAVA_HOME/bin/javac" /usr/lib/jvm/*/bin/javac; do
                [ -x "$jdk_javac" ] && { "$jdk_javac" -cp "$TBTOOLS_JAR" -d "$TBTOOLS_BUILD" "$src" 2>/dev/null && break; }
            done
        }
    fi
}
