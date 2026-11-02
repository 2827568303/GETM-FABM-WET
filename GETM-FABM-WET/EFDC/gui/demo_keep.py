# -*- coding: utf-8 -*-
"""Demo sign-in attempt #2: valid-looking email, then watch dialogs and server traffic."""
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import time

from win_shot import capture

u = ctypes.WinDLL("user32", use_last_error=True)
u.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u.SendMessageW.restype = ctypes.c_ulong
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

EXE = sys.argv[1]
EMAIL = sys.argv[2] if len(sys.argv) > 2 else "zhang.san8888@gmail.com"
PWD = sys.argv[3] if len(sys.argv) > 3 else "Efdc2026!"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
SRVLOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rev", "fake_dsi_requests.txt")
os.makedirs(OUT, exist_ok=True)


def txt(h):
    b = ctypes.create_unicode_buffer(512); u.GetWindowTextW(h, b, 512); return b.value


def cls(h):
    b = ctypes.create_unicode_buffer(128); u.GetClassNameW(h, b, 128); return b.value


def settext(h, s):
    b = ctypes.create_unicode_buffer(s)
    u.SendMessageW(h, 0x000C, 0, ctypes.cast(b, ctypes.c_void_p).value)


def tops(pid):
    out = []

    def cb(h, l):
        p = wt.DWORD(0); u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            out.append(h)
        return True

    u.EnumWindows(CB(cb), 0)
    return out


def kids(h):
    out = []

    def cb(c, l):
        out.append(c)
        return True

    u.EnumChildWindows(h, CB(cb), 0)
    return out


p = subprocess.Popen([EXE], cwd=os.path.dirname(EXE), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("pid=%d" % p.pid, flush=True)
t0 = time.time()
stage = 0
reported = set()

while time.time() - t0 < 30:
    t = time.time() - t0
    for h in tops(p.pid):
        if not u.IsWindowVisible(h):
            continue
        title = txt(h)
        if stage == 0 and "Activation Wizard" in title:
            for k in kids(h):
                if cls(k).startswith("ThunderRT6CommandButton") and "Demo Version" in txt(k):
                    u.SendMessageW(k, 0x00F5, 0, 0)
                    print("[%5.2f] Demo Version clicked" % t, flush=True)
                    stage = 1
        elif stage == 1 and "Sign in" in title:
            boxes = [k for k in kids(h) if cls(k) == "ThunderRT6TextBox"]
            if len(boxes) >= 2:
                settext(boxes[1], EMAIL)
                settext(boxes[0], PWD)
                for k in kids(h):
                    if cls(k) == "ThunderRT6CommandButton" and "Sign &In" in txt(k):
                        u.SendMessageW(k, 0x00F5, 0, 0)
                        print("[%5.2f] Sign In clicked (%s)" % (t, EMAIL), flush=True)
                        stage = 2
                        break
        elif stage >= 2:
            key = (cls(h), title)
            if key not in reported:
                reported.add(key)
                print("[%5.2f] window %-20s %r" % (t, cls(h), title), flush=True)
                try:
                    capture(h, os.path.join(OUT, "demo2_%s.png" % title.replace(" ", "_")[:28]))
                except Exception:
                    pass
    if p.poll() is not None:
        print("[%5.2f] EXITED %s" % (time.time() - t0, p.returncode), flush=True)
        break
    time.sleep(0.25)

print("--- server log tail ---", flush=True)
try:
    lines = open(SRVLOG, encoding="utf-8", errors="replace").read().splitlines()
    for line in lines[-15:]:
        print("   " + line, flush=True)
except Exception as e:
    print("   (%s)" % e, flush=True)
print("READY pid=%d" % p.pid, flush=True)


