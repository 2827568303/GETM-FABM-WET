# -*- coding: utf-8 -*-
"""Launch exe uninstrumented, log windows, and PrintWindow-capture each one.

python -X utf8 gui/watch2.py <exe> <seconds> <tag>
"""
import ctypes, ctypes.wintypes as wt, os, subprocess, sys, time
from win_shot import capture

u32 = ctypes.WinDLL("user32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
u32.IsWindowVisible.argtypes = [wt.HWND]
u32.IsHungAppWindow.argtypes = [wt.HWND]
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
    r = wt.RECT(); u32.GetWindowRect(h, ctypes.byref(r)); return (r.left, r.top, r.right, r.bottom)


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
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pid = p.pid
print("pid=%d exe=%s" % (pid, exe), flush=True)

t0 = time.time()
seen = {}
next_shot = 1.0
hung_logged = False
while time.time() - t0 < dur:
    t = time.time() - t0
    hung_any = False
    for h in windows(pid):
        c = cls(h)
        if h not in seen:
            seen[h] = (c, txt(h), rect(h))
            print("[%5.2f] WIN hwnd=0x%X cls=%-20s title=%-28r vis=%d rect=%s" %
                  (t, h, c, txt(h), bool(u32.IsWindowVisible(h)), rect(h)), flush=True)
        if u32.IsHungAppWindow(h):
            hung_any = True
    if hung_any and not hung_logged:
        print("[%5.2f] *** thread hung (WER/exception) ***" % t, flush=True)
        hung_logged = True
    if p.poll() is not None:
        print("[%5.2f] EXITED code=%s" % (t, p.returncode), flush=True)
        break
    if t >= next_shot:
        for h, (c, title, r) in seen.items():
            if u32.IsWindowVisible(h) and r[2] > r[0]:
                try:
                    sz = capture(h, os.path.join(outdir, "%s_%03d_%s.png" % (tag, int(t * 10), c.replace(' ', ''))))
                    if sz:
                        print("[%5.2f] shot %s hwnd=0x%X %s %s" % (t, c, h, title[:24], sz), flush=True)
                except Exception as e:
                    print("shot fail %s" % e, flush=True)
        next_shot += 1.5
    time.sleep(0.12)

if p.poll() is None:
    print("still running -> kill", flush=True)
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
else:
    print("final exit=%s" % p.returncode, flush=True)
