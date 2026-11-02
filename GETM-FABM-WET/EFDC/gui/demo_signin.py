# -*- coding: utf-8 -*-
"""Drive the Activation Wizard's Demo path and dump the sign-in form's controls.

python -X utf8 gui/demo_signin.py <exe> [--fill email|password] [--click caption]
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
u32.GetDlgCtrlID.argtypes = [wt.HWND]
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

exe = sys.argv[1]
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(outdir, exist_ok=True)
fill_email = "test@example.com"
fill_pwd = "Test1234!"


def txt(h):
    b = ctypes.create_unicode_buffer(512); u32.GetWindowTextW(h, b, 512); return b.value


def cls(h):
    b = ctypes.create_unicode_buffer(128); u32.GetClassNameW(h, b, 128); return b.value


def rect(h):
    r = wt.RECT(); u32.GetWindowRect(h, ctypes.byref(r)); return (r.left, r.top, r.right, r.bottom)


def tops(pid):
    out = []

    def cb(h, l):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            out.append(h)
        return True

    u32.EnumWindows(CB(cb), 0)
    return out


def kids(h):
    out = []

    def cb(c, l):
        out.append(c)
        return True

    u32.EnumChildWindows(h, CB(cb), 0)
    return out


p = subprocess.Popen([exe], cwd=os.path.dirname(exe), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pid = p.pid
print("pid=%d" % pid, flush=True)
t0 = time.time()
clicked_demo = False
dumped_signin = False
filled = False
signed = False

while time.time() - t0 < 40:
    t = time.time() - t0
    for h in tops(pid):
        title, c = txt(h), cls(h)
        if not u32.IsWindowVisible(h):
            continue
        kids_list = kids(h)
        if "Activation Wizard" in title and not clicked_demo:
            print("[%5.2f] wizard up; buttons:" % t, flush=True)
            for k in kids_list:
                kc, kt = cls(k), txt(k)
                if kc in ("ThunderRT6CommandButton", "Button") and kt:
                    print("     %-24r id=%d" % (kt, u32.GetDlgCtrlID(k)), flush=True)
                    if "Demo Version" in kt:
                        u32.SendMessageW(k, 0x00F5, 0, 0)  # BM_CLICK
                        print("[%5.2f] clicked %r" % (t, kt), flush=True)
                        clicked_demo = True
        elif clicked_demo and not dumped_signin and ("Sign in" in title or "Demo" in title):
            print("[%5.2f] new form %r (%s)" % (t, title, c), flush=True)
            for k in kids_list:
                kc, kt = cls(k), txt(k)
                if kc in ("ThunderRT6TextBox", "Edit", "ThunderRT6CommandButton", "Button", "Static", "ThunderRT6Label"):
                    print("     %-22s %-28r id=%d" % (kc, kt, u32.GetDlgCtrlID(k)), flush=True)
            dumped_signin = True
            try:
                sz = capture(h, os.path.join(outdir, "signin_%s.png" % title.replace(" ", "_")))
                print("     capture %s" % (sz,), flush=True)
            except Exception:
                pass
    if p.poll() is not None:
        print("[%5.2f] EXITED code=%s" % (time.time() - t0, p.returncode), flush=True)
        break
    time.sleep(0.3)
print("alive=%s" % (p.poll() is None), flush=True)

