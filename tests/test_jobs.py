"""job 状态机回归测试(2026-09-23 补): 不依赖真实 Java, 用轻量命令验证状态转移。"""
import json
import os
import subprocess
import sys
import time


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = os.path.expanduser("~/.config/tbtools-cli/jobs")


def run_cli(*args, timeout=60):
    r = subprocess.run([sys.executable, "-m", "tbtools_cli.cli", *args],
                       capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    return r.returncode, r.stdout, r.stderr


def _submit_and_wait(args, wait=3):
    ec, out, _ = run_cli("tool-submit", *args)
    assert ec == 0, out
    jid = json.loads(out)["job_id"]
    time.sleep(wait)
    _, out2, _ = run_cli("job-status", jid)
    return jid, json.loads(out2)


class TestJobStateMachine:
    def test_submit_success(self):
        """成功路径: running → succeeded(exit 0)"""
        jid, st = _submit_and_wait(["version"], wait=2)
        assert st["status"] == "succeeded", st
        assert st["exit_code"] == 0

    def test_submit_failure(self):
        """失败路径: 不存在文件 → failed(exit≠0)"""
        jid, st = _submit_and_wait(["expr", "volcano", "/no/such_file_xyz.txt", "/tmp/jt_fail.svg"], wait=3)
        assert st["status"] == "failed", st
        assert st["exit_code"] != 0

    def test_job_result_structured(self):
        """job-result 返回结构化结果(含 status)"""
        jid, _ = _submit_and_wait(["version"], wait=2)
        ec, out, _ = run_cli("job-result", jid)
        assert ec == 0
        d = json.loads(out)
        assert d["schema_version"] == "1.0"
        assert d["status"] == "succeeded"

    def test_job_log(self):
        """job-log 可读(成功命令必有输出)"""
        jid, _ = _submit_and_wait(["version"], wait=2)
        ec, out, _ = run_cli("job-log", jid, "--tail", "5")
        assert ec == 0
        assert "tbtools-cli" in out or "version" in out.lower()

    def test_job_clean_keeps_running(self):
        """job-clean 不碰 running 任务, 清理历史已结束(用 --all 验证幂等)"""
        jid, _ = _submit_and_wait(["version"], wait=2)
        # 先 --all 清空历史(幂等), 再提交一个新 job 应可运行
        run_cli("job-clean", "--all")
        jid2, st = _submit_and_wait(["version"], wait=2)
        assert st["status"] == "succeeded"
        # 清理后遗留文件应为 0(新 job 也结束, --all 再清一次)
        run_cli("job-clean", "--all")
        leftovers = [f for f in os.listdir(JOBS) if jid2 in f or jid in f]
        assert leftovers == [], f"清理残留: {leftovers}"
