#!/usr/bin/env bash
# RPC 交付包回归脚本 Linux 化（RPC 交付包 N 系列修复后回归用）
#
# 交付包 02_回归脚本/run_p*.py（36 份）硬编码 Windows 路径（C:/Users/16135/...）
# 与 taskkill 杀树。本脚本把它们转换到 tests/rpc_regression_linux/：
#   - 测试目录 T 与仓库目录改为环境变量（保留 Windows 默认值，双平台可用）
#   - python 调用改为 sys.executable（不再指向 WorkBuddy venv）
#   - taskkill 分支保留（Windows 仍可用），Linux 走 killpg
# 用法: bash scripts/rpc_regression_linux.sh <交付包脚本目录>
# 默认: /tmp/tbtools_rpc_pkg/TBtools_RPC测试交付包/02_回归脚本
set -euo pipefail
SRC="${1:-/tmp/tbtools_rpc_pkg/TBtools_RPC测试交付包/02_回归脚本}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/tests/rpc_regression_linux"
mkdir -p "$DEST"
n=0
for f in "$SRC"/run_p*.py "$SRC"/prep_inputs.py "$SRC"/run_cmdtests.py; do
  [ -f "$f" ] || continue
  out="$DEST/$(basename "$f")"
  python3 - "$f" > "$out" << 'PYEOF'
import re, sys
src = open(sys.argv[1], encoding='utf-8', errors='replace').read()

# 1) 测试目录/仓库目录 → 环境变量（Windows 默认保留）
src = src.replace(
    'T = r"C:\\Users\\16135\\WorkBuddy\\2026-09-20-10-24-01\\tbtools-test"',
    'T = os.environ.get("TBREGRESSION_TEST", r"C:\\Users\\16135\\WorkBuddy\\2026-09-20-10-24-01\\tbtools-test")')
src = src.replace(
    'os.chdir(r"C:\\Users\\16135\\WorkBuddy\\2026-09-20-10-24-01\\tbtools-cli")',
    'os.chdir(os.environ.get("TBREGRESSION_CLI", r"C:\\Users\\16135\\WorkBuddy\\2026-09-20-10-24-01\\tbtools-cli"))')

# 2) python 调用 → sys.executable（跨平台）
src = re.sub(
    r'CLI = \[r"C:\\Users\\16135\\.workbuddy\\binaries\\python\\envs\\default\\Scripts\\python\.exe",\s*"-m", "tbtools_cli\.cli"\]',
    'CLI = [sys.executable, "-m", "tbtools_cli.cli"]', src)
src = re.sub(
    r'PY = r"C:\\Users\\16135\\.workbuddy\\binaries\\python\\envs\\default\\Scripts\\python\.exe"',
    'PY = sys.executable', src)
src = src.replace('import sys\n', 'import sys\n', 1)
if 'import sys' not in src.split('\n')[0:20].__str__():
    src = 'import sys\n' + src if not src.startswith('import sys') else src

# 3) taskkill 杀树 → 跨平台（Windows 保留 taskkill，Linux killpg）
src = src.replace(
    'subprocess.run(["taskkill", "/F", "/T", "/PID", str(r.pid)], capture_output=True)',
    'subprocess.run(["taskkill", "/F", "/T", "/PID", str(r.pid)], capture_output=True) if os.name == "nt" else (lambda p: (os.killpg(os.getpgid(p.pid), 9) if os.getpgid(p.pid) else os.kill(p.pid, 9)))(r)')

print(src)
PYEOF
  n=$((n+1))
done
echo "✅ 已转换 $n 份脚本 → $DEST"
echo "使用: TBREGRESSION_TEST=<测试目录> TBREGRESSION_CLI=<仓库目录> python3 tests/rpc_regression_linux/run_p13.py"
