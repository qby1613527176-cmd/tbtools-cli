#!/usr/bin/env python
"""RPC 回归统一 runner(收敛 34 个同构 run_p*.py, 2026-09-23)。

用法:
  TBREGRESSION_TEST=<数据根> python3 scripts/run_rpc_regression.py [--only p1,p2] [--list]

- 每个 run_p*.py 是原 Windows 交付脚本的 Linux 化版本(第一阶段收敛: 保留脚本, 统一入口/汇总)
- 数据根存在才执行(无数据=跳过, 不产生误报); 汇总 PASS/FAIL 表 + 失败脚本尾部日志
"""
import argparse
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = sorted(glob.glob(os.path.join(HERE, "tests", "rpc_regression_linux", "run_p*.py")))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", default="", help="逗号分隔的 phase 子集, 如 p1,p4")
    ap.add_argument("--list", action="store_true", help="列出可用 phase 脚本")
    args = ap.parse_args()

    if args.list:
        for s in SCRIPTS:
            print(os.path.basename(s))
        return 0

    data = os.environ.get("TBREGRESSION_TEST", "")
    if not data or not os.path.isdir(data):
        print(f"⚠️  TBREGRESSION_TEST 未设置或不存在({data!r})——跳过全部 {len(SCRIPTS)} 个回归脚本")
        print("    设置: TBREGRESSION_TEST=<交付包数据根> python3 scripts/run_rpc_regression.py")
        return 0

    only = {x.strip().lower() for x in args.only.split(",") if x.strip()}
    results = []
    for s in SCRIPTS:
        base = os.path.basename(s)
        phase = base.replace("run_", "").replace(".py", "")
        if only and phase not in only:
            continue
        env = dict(os.environ, TBROOT=HERE)
        r = subprocess.run([sys.executable, s], capture_output=True, text=True, env=env, timeout=3600)
        ok = r.returncode == 0
        results.append((base, ok))
        tail = "\n".join(r.stdout.splitlines()[-4:]) if not ok else ""
        print(f"{'✅' if ok else '❌'} {base}" + (f"\n{tail}" if tail else ""))

    passed = sum(1 for _, ok in results if ok)
    print(f"\n═══ RPC 回归汇总: {passed}/{len(results)} PASS ═══")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
