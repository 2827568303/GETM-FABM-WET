# -*- coding: utf-8 -*-
"""Launch the app, wait for the Activation Wizard, close it, then report what the UI does.

python -X utf8 gui/close_wizard.py <exe> [seconds]
"""
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import time

from win_shot import capture

u32 = ctypes.WinDLL("user32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
u32.SendMessageTimeoutW.restype = ctypes.c_ulong
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

exe = sys.argv[1]
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 18.0
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(outdir, exist_ok=True)


def txt(h):
    b = ctypes.create_unicode_buffer(256); u32.GetWindowTextW(h, b, 256); return b.value


def cls(h):
    b = ctypes.create_unicode_buffer(128); u32.GetClassNameW(h, b, 128); return b.value


def rect(h):
    r = wt.RECT(); u32.GetWindowRect(h, ctypes.byref(r)); return (r.left, r.top, r.right, r.bottom)


def wins(pid):
    out = []

    def cb(h, l):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            out.append(h)
        return True

    u32.EnumWindows(CB(cb), 0)
    return out


p = subprocess.Popen([exe], cwd=os.path.dirname(exe), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pid = p.pid
print("pid=%d" % pid, flush=True)
t0 = time.time()
closed_at = None
reported = set()
while time.time() - t0 < dur:
    t = time.time() - t0
    for h in wins(pid):
        title, c = txt(h), cls(h)
        key = (c, title, bool(u32.IsWindowVisible(h)))
        if key not in reported and (c.startswith("ThunderRT6") or "Activation" in title):
            reported.add(key)
            print("[%5.2f] %-18s %-22r vis=%s rect=%s" % (t, c, title, key[2], rect(h)), flush=True)
        if "Activation Wizard" in title and closed_at is None and t > 6:
            print("[%5.2f] sending WM_CLOSE to wizard" % t, flush=True)
            u32.PostMessageW(h, 0x0010, 0, 0)
            closed_at = t
        if closed_at is not None and t > closed_at + 1.5 and title and c.startswith("ThunderRT6FormDC") and u32.IsWindowVisible(h) and rect(h)[2] > rect(h)[0]:
            try:
                path = os.path.join(outdir, "after_close_%s.png" % title.replace(" ", "_").replace(".", ""))
                sz = capture(h, path)
                print("[%5.2f] capture %r %s" % (t, title, sz), flush=True)
            except Exception:
                pass
    if p.poll() is not None:
        print("[%5.2f] EXITED code=%s" % (time.time() - t0, p.returncode), flush=True)
        break
    time.sleep(0.25)
print("alive=%s" % (p.poll() is None), flush=True)
if p.poll() is None:
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
