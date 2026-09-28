import json, time, os
from datetime import datetime
import urllib.request

BASE = "http://127.0.0.1:8766"
CASE = r"C:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\case\Lake Dianchi"
LOG = os.path.join(CASE, "monitor_log.txt")

# 绕过沙箱代理，直连本地 Web 服务
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))


def get_status():
    req = urllib.request.Request(BASE + "/api/run/status")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    interval = 30
    max_iter = 420  # 最多约 3.5 小时（全年长任务留余量）
    with open(LOG, "w", encoding="utf-8") as f:
        f.write(f"[{now()}] 监督脚本启动，目标 {BASE}，案例 {CASE}\n")
        f.flush()
        for _ in range(max_iter):
            try:
                s = get_status()
            except Exception as e:
                f.write(f"[{now()}] [WARN] 状态获取失败: {e}\n")
                f.flush()
                time.sleep(interval)
                continue
            status = s.get("status", "?")
            prog = s.get("progress", 0) or 0
            cs = s.get("current_step", 0) or 0
            ts = s.get("total_steps", 0) or 0
            eta = s.get("eta_minutes", 0) or 0
            logs = s.get("logs", []) or []
            last = ""
            for ln in reversed(logs):
                if ln and ln.strip():
                    last = ln.strip()
                    break
            f.write(f"[{now()}] status={status} progress={prog:.1f}% "
                    f"step={cs}/{ts} eta={eta:.1f}min | {last[:140]}\n")
            f.flush()
            if status in ("completed", "failed", "stopped"):
                blob = "\n".join(logs)
                crash_kw = ("STOP 1", "collect_from_categories", "fatal_error",
                            "FATAL GETM ERROR", "FATAL ERROR", "out-of-bound",
                            "IEEE_INVALID", "IEEE_DIVIDE_BY_ZERO", "forrtl:", "NaN")
                crashed = any(k in blob for k in crash_kw)
                verdict = status
                if status == "completed" and crashed:
                    verdict = "completed-BUT-CRASH-IN-LOG"
                    f.write(f"[{now()}] [CRITICAL] 服务端标记 completed，但日志检出崩溃信号"
                            f"（{'/'.join(k for k in crash_kw if k in blob)}），判定为失败！\n")
                f.write(f"[{now()}] ===== 运行终态: {verdict} =====\n")
                for ln in logs[-50:]:
                    f.write("    " + ln + "\n")
                f.flush()
                break
            time.sleep(interval)
        else:
            f.write(f"[{now()}] [WARN] 已达最大监督时长，脚本退出"
                    f"（模型可能仍在运行，请手动查看 /api/run/status）\n")
            f.flush()


if __name__ == "__main__":
    main()
