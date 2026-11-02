# -*- coding: utf-8 -*-
"""Launch the patched app, then prove the main window is live and capture it.

python -X utf8 gui/live_check.py <exe> <wait-seconds>
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
wait = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(outdir, exist_ok=True)


def cls(h):
    b = ctypes.create_unicode_buffer(128); u32.GetClassNameW(h, b, 128); return b.value


def txt(h):
    b = ctypes.create_unicode_buffer(256); u32.GetWindowTextW(h, b, 256); return b.value


def rect(h):
    r = wt.RECT(); u32.GetWindowRect(h, ctypes.byref(r)); return (r.left, r.top, r.right, r.bottom)


p = subprocess.Popen([exe], cwd=os.path.dirname(exe), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("pid=%d" % p.pid, flush=True)
time.sleep(wait)
if p.poll() is not None:
    print("EXITED early code=%s" % p.returncode)
    sys.exit(1)

found = []


def cb(h, l):
    pid = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(pid))
    if pid.value == p.pid:
        c, t = cls(h), txt(h)
        if c.startswith("ThunderRT6FormDC") and t:
            found.append(h)
    return True


u32.EnumWindows(CB(cb), 0)
for h in found:
    out = ctypes.c_ulong(0)
    ok = u32.SendMessageTimeoutW(h, 0, 0, 0, 2, 1500, ctypes.byref(out))
    hung = bool(u32.IsHungAppWindow(h))
    r = rect(h)
    print("window %-24r rect=%s responsive=%s hung=%s" % (txt(h), r, bool(ok), hung), flush=True)
    try:
        path = os.path.join(outdir, "live_%s.png" % txt(h).replace(" ", "_").replace(".", ""))
        sz = capture(h, path)
        print("   capture %s %s" % (path, sz), flush=True)
    except Exception as e:
        print("   capture failed %s" % e, flush=True)

# count child controls of the largest window
if found:
    h = max(found, key=lambda x: (rect(x)[2] - rect(x)[0]) * (rect(x)[3] - rect(x)[1]))
    kids = []

    def cb2(c, l):
        kids.append((cls(c), txt(c)))
        return True

    u32.EnumChildWindows(h, CB(cb2), 0)
    print("children of %r: %d" % (txt(h), len(kids)), flush=True)
    named = [k for k in kids if k[1]]
    print("  named controls: %s" % ", ".join("%s=%r" % k for k in named[:14]), flush=True)
print("done", flush=True)
