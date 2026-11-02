#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EFDC 模型前端（本地 Web UI）
- 列出模型、显示网格（按湖底高程着色）
- 一键运行破解版求解器（PERPETUAL），实时抓取进度
- 实时曲线：水位 / 流速 / 浓度（从求解器 stdout 解析）
- 仅监听 127.0.0.1，仅用 Python 标准库
用法:  python server.py [port]
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
import uuid
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

WORK = os.path.dirname(os.path.abspath(__file__))
# 模型根目录：默认是 web 的上一级；可用环境变量 EFDC_MODELS_ROOT 覆盖
ROOT = os.environ.get("EFDC_MODELS_ROOT") or os.path.dirname(WORK)

# 求解器：按优先级找，可用环境变量 EFDC_SOLVER 覆盖
_SOLVER_NAMES = ["EFDCPlus_084_OMP_180718.PERPETUAL.exe",
                 "EFDCPlus_084_OMP_180718.patched2.exe",
                 "EFDCPlus_084_OMP_180718.exe"]
_SOLVER_DIRS = [os.environ.get("EFDC_SOLVER_DIR") or "",
                os.path.join(os.path.dirname(WORK), "solver"),
                os.path.join(os.path.dirname(WORK), "EFDC 商业版8.4"),
                os.path.dirname(WORK), WORK]

def _find_solver():
    envp = os.environ.get("EFDC_SOLVER")
    if envp and os.path.exists(envp):
        return envp
    for d in _SOLVER_DIRS:
        if not d:
            continue
        for n in _SOLVER_NAMES:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    return os.path.join(os.path.dirname(WORK), "solver", _SOLVER_NAMES[0])

SOLVER = _find_solver()
RUNS = os.path.join(WORK, "runs")
os.makedirs(RUNS, exist_ok=True)

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8787

# --------------------------------------------------------------------------- #
#  模型解析
# --------------------------------------------------------------------------- #

def _scan_dir(base):
    """返回 base 下含 EFDC.INP 的子目录"""
    out = []
    try:
        names = sorted(os.listdir(base))
    except Exception:
        return out
    for name in names:
        p = os.path.join(base, name)
        if not os.path.isdir(p):
            continue
        inp = None
        try:
            for f in os.listdir(p):
                if f.lower() == "efdc.inp":
                    inp = os.path.join(p, f)
                    break
        except Exception:
            continue
        if inp:
            out.append((name, p, inp))
    return out


def list_models():
    out = []
    seen = set()
    bases = [ROOT, os.path.join(ROOT, "models")]
    for base in bases:
        for name, p, inp in _scan_dir(base):
            if p in seen:
                continue
            seen.add(p)
            out.append({
                "name": name,
                "path": p,
                "mtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(inp))),
                "cells": count_active_cells(p),
            })
    return out


def count_active_cells(mdir):
    """优先用 corners.inp 的格数（与实际可绘图格数一致）"""
    try:
        n = len(read_corners(mdir))
        if n:
            return n
    except Exception:
        pass
    f = os.path.join(mdir, "cell.inp")
    if not os.path.exists(f):
        return None
    n = 0
    try:
        with open(f, encoding="latin-1") as fh:
            for line in fh:
                s = line.strip()
                if not s or s[0] in "C*":
                    continue
                body = s[4:] if len(s) > 4 else ""
                n += sum(1 for ch in body if ch not in "0 ")
    except Exception:
        return None
    return n or None


def read_corners(mdir):
    """corners.inp -> [{i,j,pts:[[x,y]*4]}]"""
    f = os.path.join(mdir, "corners.inp")
    if not os.path.exists(f):
        return []
    cells = []
    with open(f, encoding="latin-1") as fh:
        for line in fh:
            s = line.strip()
            if not s or s[0] in "*C":
                continue
            parts = s.split()
            if len(parts) < 10:
                continue
            try:
                i, j = int(parts[0]), int(parts[1])
                nums = [float(x) for x in parts[2:10]]
            except ValueError:
                continue
            pts = [[nums[k], nums[k + 1]] for k in range(0, 8, 2)]
            cells.append({"i": i, "j": j, "pts": pts})
    return cells


def read_dxdy(mdir):
    """dxdy.inp -> {(i,j): {dx,dy,depth,bottom,zrough}}"""
    f = os.path.join(mdir, "dxdy.inp")
    d = {}
    if not os.path.exists(f):
        return d
    with open(f, encoding="latin-1") as fh:
        for line in fh:
            s = line.strip()
            if not s or s[0] in "C*":
                continue
            parts = s.split()
            if len(parts) < 7:
                continue
            try:
                i, j = int(parts[0]), int(parts[1])
                d[(i, j)] = {
                    "dx": float(parts[2]), "dy": float(parts[3]),
                    "depth": float(parts[4]), "bottom": float(parts[5]),
                    "zrough": float(parts[6]),
                }
            except ValueError:
                continue
    return d


def read_inp_head(mdir):
    """从 EFDC.INP 抓标题与几个关键卡片"""
    f = os.path.join(mdir, "efdc.inp")
    info = {"title": "", "header": []}
    if not os.path.exists(f):
        return info
    lines = open(f, encoding="latin-1").read().splitlines()
    for idx, line in enumerate(lines):
        if line.strip().upper().startswith("C1 TITLE"):
            for k in range(idx + 1, min(idx + 4, len(lines))):
                if lines[k].strip():
                    info["title"] = lines[k].strip()
                    break
            break
    # 收集前 60 行作为原始头（UI 里可展开查看）
    info["header"] = [l[:120] for l in lines[:60]]
    return info


def model_detail(path):
    md = {"path": path, "name": os.path.basename(path)}
    md.update(read_inp_head(path))
    cells = read_corners(path)
    dxdy = read_dxdy(path)
    for c in cells:
        info = dxdy.get((c["i"], c["j"]), {})
        c["bottom"] = info.get("bottom")
        c["depth"] = info.get("depth")
        c["dx"] = info.get("dx")
    md["cells"] = cells
    if cells:
        xs = [p[0] for c in cells for p in c["pts"]]
        ys = [p[1] for c in cells for p in c["pts"]]
        md["bbox"] = [min(xs), min(ys), max(xs), max(ys)]
    else:
        md["bbox"] = None
    return md


# --------------------------------------------------------------------------- #
#  求解器运行 + 实时解析
# --------------------------------------------------------------------------- #

class Runner:
    def __init__(self):
        self.lock = threading.Lock()
        self.proc = None
        self.thread = None
        self.state = {
            "running": False, "id": None, "model": None,
            "started": None, "finished": None, "exit": None,
            "lines": [], "series": {"t": [], "elev": [], "vele": [], "veln": [], "dye": []},
            "eta": None, "perpetual": False, "error": None, "progress": 0.0,
        }
        self.tail = deque(maxlen=300)

    # ---------------- 起停 ----------------
    def start(self, model_path):
        with self.lock:
            if self.proc and self.proc.poll() is None:
                return {"ok": False, "error": "已有任务在运行"}
            rid = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:4]
            logpath = os.path.join(RUNS, rid + ".log")
            stdin_path = os.path.join(RUNS, rid + ".stdin")
            with open(stdin_path, "w") as fh:
                fh.write("\n" * 20)
            self.tail.clear()
            self.state.update({
                "running": True, "id": rid, "model": model_path,
                "started": time.time(), "finished": None, "exit": None,
                "lines": [], "series": {"t": [], "elev": [], "vele": [], "veln": [], "dye": []},
                "eta": None, "perpetual": False, "error": None, "progress": 0.0,
            })
            sin = open(stdin_path, "rb")
            self.proc = subprocess.Popen(
                [SOLVER], cwd=model_path, stdin=sin,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            )
            self.thread = threading.Thread(target=self._pump, args=(rid, logpath, sin), daemon=True)
            self.thread.start()
            return {"ok": True, "id": rid}

    def stop(self):
        with self.lock:
            if not self.proc or self.proc.poll() is not None:
                return {"ok": False, "error": "没有在运行的任务"}
            try:
                self.proc.kill()
            except Exception as e:
                return {"ok": False, "error": str(e)}
            return {"ok": True}

    # ---------------- 读取输出 ----------------
    RX_STEP = re.compile(r"^\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)")
    RX_ETA = re.compile(r"ELAPSED TIME:\s*([\d.]+)\s*\(hr\)\s*ESTIMATED TIME TO COMPLETION:\s*([\d.]+)")

    def _pump(self, rid, logpath, sin):
        log = open(logpath, "w", encoding="utf-8", errors="replace")
        try:
            for raw in iter(self.proc.stdout.readline, b""):
                line = raw.decode("latin-1", "replace").rstrip("\r\n")
                log.write(line + "\n")
                log.flush()
                self.tail.append(line)
                if "PERPETUAL VERSION" in line:
                    self.state["perpetual"] = True
                m = self.RX_STEP.match(line)
                if m:
                    try:
                        t = float(m.group(1))
                        elev = float(m.group(3)) / 100.0      # cm -> m
                        s = self.state["series"]
                        s["t"].append(round(t, 3))
                        s["elev"].append(round(elev, 3))
                        s["vele"].append(float(m.group(4)))
                        s["veln"].append(float(m.group(5)))
                        s["dye"].append(float(m.group(6)))
                        if len(s["t"]) > 4000:
                            for k in s:
                                del s[k][:1000]
                    except Exception:
                        pass
                e = self.RX_ETA.search(line)
                if e:
                    try:
                        self.state["eta"] = float(e.group(2))
                    except Exception:
                        pass
        finally:
            rc = self.proc.wait()
            log.close()
            try:
                sin.close()
            except Exception:
                pass
            self.state["running"] = False
            self.state["exit"] = rc
            self.state["finished"] = time.time()
            self.state["lines"] = list(self.tail)

    def status(self):
        st = dict(self.state)
        st["lines"] = list(self.tail)[-200:]
        st["elapsed_min"] = round((time.time() - (st["started"] or time.time())) / 60.0, 2) if st["started"] else 0
        # 粗算进度：用第 1 个与最后一个时间(天) + ETA
        s = st["series"]
        if s["t"] and st["eta"]:
            done_hr = st["elapsed_min"] / 60.0
            if done_hr + st["eta"] > 0:
                st["progress"] = round(100.0 * done_hr / (done_hr + st["eta"]), 1)
        return st


RUNNER = Runner()


# --------------------------------------------------------------------------- #
#  HTTP
# --------------------------------------------------------------------------- #

class Handler(BaseHTTPRequestHandler):
    server_version = "EFDCFront/1.0"

    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path in ("/", "/index.html"):
            p = os.path.join(WORK, "index.html")
            if not os.path.exists(p):
                return self._send(404, "index.html missing", "text/plain; charset=utf-8")
            return self._send(200, open(p, encoding="utf-8").read(), "text/html; charset=utf-8")
        if u.path == "/api/models":
            return self._json({"solver": SOLVER, "solver_exists": os.path.exists(SOLVER),
                               "models": list_models()})
        if u.path == "/api/model":
            path = (q.get("path") or [""])[0]
            if not path or not os.path.isdir(path):
                return self._json({"error": "bad path"}, 400)
            return self._json(model_detail(path))
        if u.path == "/api/status":
            return self._json(RUNNER.status())
        return self._send(404, "not found", "text/plain; charset=utf-8")

    def do_POST(self):
        u = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        try:
            data = json.loads(body or b"{}")
        except Exception:
            data = {}
        if u.path == "/api/run":
            path = data.get("path") or ""
            if not os.path.isdir(path) or not os.path.exists(os.path.join(path, "EFDC.INP")) \
               and not os.path.exists(os.path.join(path, "efdc.inp")):
                return self._json({"ok": False, "error": "目录里没有 EFDC.INP"}, 400)
            if not os.path.exists(SOLVER):
                return self._json({"ok": False, "error": "找不到破解版求解器: " + SOLVER}, 400)
            return self._json(RUNNER.start(path))
        if u.path == "/api/stop":
            return self._json(RUNNER.stop())
        return self._send(404, "not found", "text/plain; charset=utf-8")


def main():
    print("EFDC 前端已启动: http://127.0.0.1:%d" % PORT)
    print("求解器: %s (%s)" % (SOLVER, "存在" if os.path.exists(SOLVER) else "缺失"))
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
