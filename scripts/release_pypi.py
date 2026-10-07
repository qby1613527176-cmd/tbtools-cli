#!/usr/bin/env python3
"""release_pypi.py — PyPI 发布一键脚本(2026-10-07 沉淀, 基于 1.4.90/91 实测流程).

流程: 门禁预检(--check/ruff/mypy) → cp verification_report 包内快照 → build(wheel+sdist)
     → twine check → 干净 venv 冒烟(version/exec_verified) → twine upload
     → PyPI 拉取验证(simple 索引传播延迟自动重试).

用法:
  python3 scripts/release_pypi.py               # 全流程(上传)
  python3 scripts/release_pypi.py --dry-run     # 只 build+check+冒烟, 不上传

前置: ~/.pypirc 已配 token(600 权限); pyproject 版本已 bump(git tag 已打);
     本机有 JAR 环境产出的 tests/verification_report.json(发布时点验证证据)。
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sh(cmd, cwd=ROOT, timeout=600, check=True):
    """run shell; 失败即抛(发布流程无静默继续)."""
    print(f'>> {" ".join(cmd) if isinstance(cmd, list) else cmd}')
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        print(r.stdout[-1500:])
        print(r.stderr[-1500:])
        raise SystemExit(f'[发布中止] 命令失败: {" ".join(cmd) if isinstance(cmd, list) else cmd}')
    return r


def version() -> str:
    m = re.search(r'version = "([\d.]+)"',
                  open(os.path.join(ROOT, 'pyproject.toml'), encoding='utf-8').read())
    if not m:
        raise SystemExit('pyproject.toml 无 version')
    return m.group(1)


def main():
    ap = argparse.ArgumentParser(description='tbtools-cli PyPI 一键发布')
    ap.add_argument('--dry-run', action='store_true', help='只 build+check+冒烟, 不上传')
    a = ap.parse_args()
    ver = version()
    print(f'== tbtools-cli {ver} → PyPI ==')

    # 0) 门禁预检(发布前必须绿)
    sh(['python3', 'scripts/gen_metadata.py', '--check'])
    sh(['ruff', 'check', '.'])
    sh(['/home/elysia/.venvs/mypy_tbtools/bin/mypy', 'tbtools_cli/', 'scripts/gen_metadata.py'])

    # 1) 包内验证证据快照(安装态 census/describe 可见; 真源 tests/)
    sh(['cp', 'tests/verification_report.json', 'tbtools_cli/verification_report.json'])

    # 2) build(wheel + sdist; 清掉旧 dist)
    dist = os.path.join(ROOT, 'dist')
    for f in os.listdir(dist):
        if f.startswith(f'tbtools_cli-{ver}'):
            os.remove(os.path.join(dist, f))
    sh(['pip', 'wheel', '.', '-w', 'dist/', '--no-deps'], timeout=900)
    sh([sys.executable, '-c', 'from setuptools import build_meta; build_meta.build_sdist("dist")'],
       timeout=900)
    whl = f'dist/tbtools_cli-{ver}-py3-none-any.whl'
    sdist = f'dist/tbtools_cli-{ver}.tar.gz'
    print(f'    build OK: {whl} / {sdist}')

    # 3) twine check(临时 venv 装 twine, 不依赖系统 pip)
    tv = tempfile.mkdtemp(prefix='twine_venv_')
    sh([sys.executable, '-m', 'venv', tv], check=False)
    sh([os.path.join(tv, 'bin', 'pip'), 'install', '-q', 'twine'], timeout=300)
    tw = os.path.join(tv, 'bin', 'twine')
    sh([tw, 'check', whl, sdist])

    # 4) 干净 venv 冒烟(wheel 安装 + 核心功能 + 安装态验证证据)
    pv = tempfile.mkdtemp(prefix='pypi_venv_')
    sh([sys.executable, '-m', 'venv', pv])
    sh([os.path.join(pv, 'bin', 'pip'), 'install', '-q', whl], timeout=300)
    r = sh([os.path.join(pv, 'bin', 'tbtools'), 'version', '--json'])
    d = json.loads(r.stdout)
    assert d['version'] == ver, f'冒烟: 版本不符 {d}'
    assert d.get('execution_verified', 0) > 0, f'冒烟: 安装态 exec_verified=0(证据快照未生效) {d}'
    print(f'    冒烟 OK: v{d["version"]} / meta_cmds={d.get("metadata_commands")} / exec_verified={d.get("execution_verified")}')

    if a.dry_run:
        print('--dry-run: build+check+冒烟 全过, 未上传。')
        return

    # 5) upload(~/.pypirc token, 不打印)
    sh([tw, 'upload', whl, sdist], timeout=600)

    # 6) PyPI 拉取验证(simple 索引传播延迟, 重试最多 ~2min)
    last_err = None
    for i in range(8):
        time.sleep(15)
        pv2 = tempfile.mkdtemp(prefix='pypi_pull_')
        sh([sys.executable, '-m', 'venv', pv2], check=False)
        r = subprocess.run([os.path.join(pv2, 'bin', 'pip'), 'install', '-q', '--no-cache-dir',
                            f'tbtools-cli=={ver}'], capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            last_err = r.stderr[-150:]
            print(f'    [重试 {i+1}] simple 索引未同步: {last_err[:60]}')
            continue
        rr = subprocess.run([os.path.join(pv2, 'bin', 'tbtools'), 'version', '--json'],
                            capture_output=True, text=True, timeout=60)
        try:
            d = json.loads(rr.stdout)
            assert d['version'] == ver
            print(f'    PyPI 拉取验证 OK: v{d["version"]} / exec_verified={d.get("execution_verified")}')
            return
        except Exception:
            last_err = 'version 校验失败'
    raise SystemExit(f'[发布中止] PyPI 拉取验证超时(索引传播慢): {last_err}')


if __name__ == '__main__':
    main()
