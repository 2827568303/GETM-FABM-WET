# -*- coding: utf-8 -*-
"""Uninstrumented GUI watcher: launch exe, log windows, capture screen shots.

Usage: python -X utf8 gui/watch.py <exe> <seconds> <tag>
No frida, no hooks: this is what a user actually sees.
"""
import ctypes, ctypes.wintypes as wt, os, subprocess, sys, time
from PIL import ImageGrab

u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
u32.IsWindowVisible.argtypes = [wt.HWND]
u32.IsWindowEnabled.argtypes = [wt.HWND]
u32.IsHungAppWindow.argtypes = [wt.HWND]
u32.SendMessageTimeoutW.restype = ctypes.c_ulong
u32.GetParent.argtypes = [wt.HWND]
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

exe = sys.argv[1]
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 15.0
tag = sys.argv[3] if len(sys.argv) > 3 else "run"
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(outdir, exist_ok=True)


def cls(h):
    b = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, b, 256); return b.value


def txt(h):
    b = ctypes.create_unicode_buffer(512); u32.GetWindowTextW(h, b, 512); return b.value


def rect(h):
    r = wt.RECT(); u32.GetWindowRect(h, ctypes.byref(r))
    return (r.left, r.top, r.right, r.bottom)


def windows(pid):
    out = []
    def cb(h, l):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            out.append(h)
        return True
    u32.EnumWindows(CB(cb), 0)
    return out


p = subprocess.Popen([exe], cwd=os.path.dirname(exe),
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
pid = p.pid
print("pid=%d exe=%s" % (pid, exe), flush=True)

t0 = time.time()
seen = set()
next_shot = 1.0
while time.time() - t0 < dur:
    t = time.time() - t0
    for h in windows(pid):
        key = (h, cls(h))
        r = rect(h)
        vis = bool(u32.IsWindowVisible(h))
        en = bool(u32.IsWindowEnabled(h))
        hung = bool(u32.IsHungAppWindow(h))
        if key not in seen:
            seen.add(key)
            print("[%5.2f] WIN hwnd=0x%X cls=%-20s title=%-32r vis=%d en=%d rect=%s parent=0x%X"
                  % (t, h, cls(h), txt(h), vis, en, r, u32.GetParent(h).__or__(0)), flush=True)
        elif hung:
            print("[%5.2f]   hung hwnd=0x%X %s" % (t, h, txt(h)), flush=True)
    if p.poll() is not None:
        print("[%5.2f] EXITED code=%s" % (t, p.returncode), flush=True)
        break
    if t >= next_shot:
        try:
            ImageGrab.grab().save(os.path.join(outdir, "%s_%03d.png" % (tag, int(t * 10))))
            print("[%5.2f] shot %s_%03d.png" % (t, tag, int(t * 10)), flush=True)
        except Exception as e:
            print("shot fail %s" % e, flush=True)
        next_shot += 1.0
    time.sleep(0.15)

if p.poll() is None:
    print("still running -> killing", flush=True)
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
else:
    print("final exit=%s" % p.returncode, flush=True)
