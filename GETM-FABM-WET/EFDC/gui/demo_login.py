# -*- coding: utf-8 -*-
"""Drive the Demo sign-in form: fill email/password, click Sign In, watch results.

python -X utf8 gui/demo_login.py <exe> [email] [password]
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
u32.SendMessageW.restype = ctypes.c_ulong
u32.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u32.PostMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

exe = sys.argv[1]
EMAIL = sys.argv[2] if len(sys.argv) > 2 else "test@example.com"
PWD = sys.argv[3] if len(sys.argv) > 3 else "Test1234!"
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(outdir, exist_ok=True)
SRVLOG = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\fake_dsi_requests.txt"


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


def settext(h, s):
    buf = ctypes.create_unicode_buffer(s)
    u32.SendMessageW(h, 0x000C, 0, ctypes.cast(buf, ctypes.c_void_p).value)  # WM_SETTEXT


p = subprocess.Popen([exe], cwd=os.path.dirname(exe), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pid = p.pid
print("pid=%d email=%s" % (pid, EMAIL), flush=True)
t0 = time.time()
stage = "wizard"
seen = set()
while time.time() - t0 < 45:
    t = time.time() - t0
    for h in tops(pid):
        if not u32.IsWindowVisible(h):
            continue
        title, c = txt(h), cls(h)
        if stage == "wizard" and "Activation Wizard" in title:
            for k in kids(h):
                if cls(k) in ("ThunderRT6CommandButton", "Button") and "Demo Version" in txt(k):
                    u32.SendMessageW(k, 0x00F5, 0, 0)
                    print("[%5.2f] clicked Demo Version" % t, flush=True)
                    stage = "signin"
                    break
        elif stage == "signin" and "Sign in" in title:
            edits = [k for k in kids(h) if cls(k) == "ThunderRT6TextBox"]
            print("[%5.2f] sign-in form: %d text boxes" % (t, len(edits)), flush=True)
            if len(edits) >= 2:
                settext(edits[0], EMAIL)
                settext(edits[1], PWD)
                print("     filled email/password", flush=True)
                for k in kids(h):
                    if cls(k) == "ThunderRT6CommandButton" and "Sign &In" in txt(k):
                        u32.SendMessageW(k, 0x00F5, 0, 0)
                        print("[%5.2f] clicked Sign In" % t, flush=True)
                        stage = "waiting"
                        break
        elif stage in ("waiting", "signin") and title and "Sign in" not in title and "Activation" not in title:
            key = (c, title)
            if key not in seen:
                seen.add(key)
                print("[%5.2f] form %-18s %-34r vis=%s rect=%s" % (t, c, title, bool(u32.IsWindowVisible(h)), rect(h)), flush=True)
    if p.poll() is not None:
        print("[%5.2f] EXITED code=%s" % (time.time() - t0, p.returncode), flush=True)
        break
    time.sleep(0.3)

print("--- server log ---", flush=True)
try:
    for line in open(SRVLOG, encoding="utf-8", errors="replace").read().splitlines()[-20:]:
        print("  " + line, flush=True)
except Exception as e:
    print("  (no log: %s)" % e, flush=True)

if p.poll() is None:
    for h in tops(pid):
        if u32.IsWindowVisible(h) and rect(h)[2] > rect(h)[0]:
            try:
                capture(h, os.path.join(outdir, "demo_%s.png" % txt(h).replace(" ", "_")[:30]))
            except Exception:
                pass
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)


