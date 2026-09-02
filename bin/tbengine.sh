#!/usr/bin/env bash
# ============================================================
# TbEngine — TBtools 任意引擎类通用 CLI 启动器（反射包装）
# 用法: tbengine.sh <引擎类> [key=value]... [--call <方法名>]
# 逻辑: 实例化引擎类 → 参数名匹配 setXxx() → 调用 process/show
# 例:   tbengine.sh biocjava.bioDoer.Fasta.ExtractFasta --help
# ============================================================
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
# shellcheck disable=SC1091
source "$ROOT/config/config.sh"
JAR="${TBTOOLS_JAR}"
JAVA_BIN="${TBTOOLS_JAVA:-${JAVA_HOME:+$JAVA_HOME/bin/}java}"
TBCLI_BUILD="$ROOT/build"
mkdir -p "$TBCLI_BUILD"
tbtools_check_jar || exit 1

if [ $# -lt 1 ]; then
  echo "用法: tbengine.sh <引擎类> [key=value]... [--call <方法>]"
  echo "例:   tbengine.sh biocjava.bioDoer.JIGplotToolkit.HeatMap.HeatmapControl inFile=/tmp/m.txt"
  exit 1
fi

ENGINE_CLASS="$1"; shift

# 编译动态包装器
cat > "$TBCLI_BUILD/TbEngineInvoke.java" << 'JAVA'
import java.lang.reflect.*;
import java.io.File;
import java.util.*;

public class TbEngineInvoke {
    public static void main(String[] args) throws Exception {
        String clsName = args[0];
        String callMethod = null;
        Map<String,String> params = new LinkedHashMap<>();
        for (int i = 1; i < args.length; i++) {
            if (args[i].equals("--call") && i+1 < args.length) { callMethod = args[i+1]; i++; continue; }
            if (args[i].startsWith("--")) continue;
            String[] kv = args[i].split("=", 2);
            if (kv.length == 2) params.put(kv[0], kv[1]);
        }
        Class<?> cls = Class.forName(clsName);
        Object obj = cls.getDeclaredConstructor().newInstance();

        int invoked = 0;
        for (Method m : cls.getMethods()) {
            if (!m.getName().startsWith("set") || m.getParameterCount() != 1) continue;
            String key = m.getName().substring(3);
            String val = null;
            for (String pk : params.keySet()) {
                if (pk.equalsIgnoreCase(key) || pk.equalsIgnoreCase(pk.replace("_",""))) { val = params.get(pk); break; }
            }
            if (val == null) continue;
            try {
                m.invoke(obj, convert(m.getParameterTypes()[0], val));
                System.out.println("  ▶ " + m.getName() + "(" + val + ")");
                invoked++;
            } catch (Exception e) {
                System.out.println("  ⚠ " + m.getName() + " 失败: " + (e.getCause()!=null?e.getCause().getMessage():e));
            }
        }
        System.out.println("  [设置 " + invoked + " 个参数]");

        // 默认调用链
        String[] chain = callMethod!=null ? new String[]{callMethod}
                        : new String[]{"process","showMeTheHeatMap","conductBlast","run","execute","start","doWork"};
        boolean done = false;
        for (String name : chain) {
            try {
                Method m = null;
                for (Method mm : cls.getMethods()) {
                    if (mm.getName().equals(name) && mm.getParameterCount()==0) { m = mm; break; }
                    if (mm.getName().equals(name) && mm.getParameterCount()==1 && mm.getParameterTypes()[0]==boolean.class) { m = mm; break; }
                }
                if (m == null) continue;
                Object r = m.getParameterCount()==0 ? m.invoke(obj) : m.invoke(obj, false);
                System.out.println("  ✓ 调用 " + name + "() 成功" + (r!=null?" => "+r:""));
                done = true;
                break;
            } catch (InvocationTargetException e) {
                System.out.println("  ✗ " + name + "() 异常: " + (e.getCause()!=null?e.getCause().toString():e));
                done = true;
                break;
            } catch (Exception e) {
                // 继续找下一个方法
            }
        }
        if (!done) {
            System.out.println("  [未找到零参调用方法。可用方法:]");
            for (Method m : cls.getMethods()) {
                if (m.getDeclaringClass() != Object.class && m.getName().matches("(process|show|draw|run|plot|write|save).*") )
                    System.out.println("    " + m);
            }
        }
    }
    static Object convert(Class<?> pt, String val) {
        if (pt == String.class) return val;
        if (pt == int.class || pt == Integer.class) return Integer.parseInt(val);
        if (pt == double.class || pt == Double.class) return Double.parseDouble(val);
        if (pt == float.class || pt == Float.class) return Float.parseFloat(val);
        if (pt == boolean.class || pt == Boolean.class) return Boolean.parseBoolean(val);
        if (pt == File.class) return new File(val);
        if (pt == File[].class) return new File[]{new File(val)};
        if (pt == List.class || pt == ArrayList.class) return new ArrayList<>(Arrays.asList(val.split(",")));
        return val;
    }
}
JAVA

javac -cp "$JAR" -d "$TBCLI_BUILD" "$TBCLI_BUILD/TbEngineInvoke.java" 2>&1 | head -5
# ---- 友好错误处理 ----
_run_engine() {
  local _err_file
  _err_file=$(mktemp /tmp/tbtools_err.XXXXXX)
  "$JAVA_BIN" -Xmx4g -cp "$TBCLI_BUILD:$JAR" TbEngineInvoke "$ENGINE_CLASS" "$@" 2>"$_err_file"
  local _ec=$?
  if [ $_ec -ne 0 ]; then
    echo "" >&2
    echo "❌ 执行失败（退出码 $_ec）" >&2
    grep -E "^Exception in thread|^Caused by:|^Error:" "$_err_file" | head -3 | while IFS= read -r _line; do
      echo "   $_line" >&2
    done
    echo "" >&2
    echo "   💡 常见原因: 参数缺失/格式不对/文件路径错误/数据不匹配" >&2
    echo "   📖 查看帮助: docs/COMMAND_REFERENCE.md" >&2
    echo "   🔍 完整堆栈: $_err_file" >&2
    echo "" >&2
  else
    cat "$_err_file" >&2
  fi
  rm -f "$_err_file"
  return $_ec
}

_run_engine "$@"