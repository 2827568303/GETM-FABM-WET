# -*- coding: utf-8 -*-
"""EFDC Explorer autologin to the Demo UI using real input (SendInput).

python -X utf8 gui/autologin.py <exe> [email] [password] [--verbose]
"""
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import typegui as tg
import signin_fill

u = ctypes.WinDLL("user32", use_last_error=True)
u.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
u.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u.SendMessageW.restype = ctypes.c_ulong
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

raw = sys.argv[1:]
RUN_CWD = None
if "--cwd" in raw:
    i = raw.index("--cwd")
    if i + 1 < len(raw):
        RUN_CWD = raw[i + 1]
    del raw[i:i + 2]
ARGS = [a for a in raw if not a.startswith("--")]
FLAGS = [a for a in raw if a.startswith("--")]
EXE = ARGS[0]
EMAIL = ARGS[1] if len(ARGS) > 1 else "zhang.san8888@gmail.com"
PWD = ARGS[2] if len(ARGS) > 2 else "Efdc2026!"
VERBOSE = "--verbose" in FLAGS


def log(*a):
    print(*a, flush=True)


def txt(h):
    b = ctypes.create_unicode_buffer(512); u.GetWindowTextW(h, b, 512); return b.value


def cls(h):
    b = ctypes.create_unicode_buffer(128); u.GetClassNameW(h, b, 128); return b.value


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


def visible(pid):
    return [(cls(h), txt(h), h) for h in tops(pid) if u.IsWindowVisible(h)]


def fill_and_submit(pid):
    forms = visible(pid)
    signin = [h for c, s, h in forms if "Sign in EEMS Demo" in s]
    if not signin:
        return False
    return signin_fill.fill_signin(signin[0], EMAIL, PWD, log=log)


def typegui_ctrl_a():
    tg.press(0x11)  # Ctrl down
    tg.press(0x41)  # A
    tg.press(0x11)  # Ctrl up (press sends down+up; approximate)
    time.sleep(0.05)


def dismiss_dialogs(pid):
    for c, s, h in visible(pid):
        if c == "#32770":
            body = [txt(k) for k in kids(h) if txt(k) and cls(k) in ("Static", "ThunderRT6Label")]
            log("   dialog %r: %s" % (s, " | ".join(body)))
            for k in kids(h):
                if cls(k) in ("Button", "ThunderRT6CommandButton") and txt(k):
                    u.SendMessageW(k, 0x00F5, 0, 0)
                    break
            time.sleep(0.5)
            return True
    return False


def hide_other_efdc(pid):
    """Leftover EFDC windows from earlier runs sit on top of ours and swallow the clicks."""
    n = 0

    def cb(h, l):
        nonlocal n
        p = wt.DWORD(0)
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid or not u.IsWindowVisible(h):
            return True
        t = txt(h)
        c = cls(h)
        if "EFDC" in t or c.startswith("ThunderRT6Form"):
            u.ShowWindow(h, 0)  # SW_HIDE
            n += 1
        return True

    u.EnumWindows(CB(cb), 0)
    if n:
        log("   hid %d window(s) of earlier EFDC runs" % n)


def start_license_stub():
    """Start tools/fakedemo.py invisibly if port 8080 is free (no extra console window)."""
    here = os.path.dirname(os.path.abspath(__file__))
    stub = os.path.join(here, "fakedemo.py")
    if not os.path.isfile(stub):
        return
    import socket
    s = socket.socket()
    try:
        s.settimeout(0.3)
        if s.connect_ex(("127.0.0.1", 8080)) == 0:
            log("   license stub already running on 8080")
            return
    finally:
        s.close()
    CREATE_NO_WINDOW = 0x08000000
    try:
        subprocess.Popen([sys.executable, "-X", "utf8", stub, "8080"],
                         cwd=here, creationflags=CREATE_NO_WINDOW,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3.0)
        log("   license stub started (127.0.0.1:8080)")
    except Exception as e:
        log("   license stub failed: %s" % e)


def main():
    start_license_stub()
    p = subprocess.Popen([EXE], cwd=RUN_CWD or os.path.dirname(EXE),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("pid=%d" % p.pid)
    time.sleep(1.0)
    hide_other_efdc(p.pid)
    t0 = time.time()
    clicked_demo = False
    attempts = 0
    while time.time() - t0 < 60:
        t = time.time() - t0
        if p.poll() is not None:
            log("[%5.2f] app exited code=%s" % (t, p.returncode))
            return 1
        forms = visible(p.pid)
        if VERBOSE:
            log("   %s" % [(c, s) for c, s, _ in forms])
        demo_ui = [h for c, s, h in forms if "Demo Version" in s and "Sign in" not in s]
        if demo_ui:
            h = demo_ui[0]
            log("[%5.2f] SUCCESS: %r rect=%s hwnd=0x%X" % (t, txt(h), tg.rect(h), h))
            return 0
        if dismiss_dialogs(p.pid):
            attempts = 0
            continue
        if not clicked_demo:
            wiz = [h for c, s, h in forms if "Activation Wizard" in s]
            if wiz:
                for k in kids(wiz[0]):
                    if cls(k).startswith("ThunderRT6CommandButton") and "Demo Version" in txt(k):
                        u.SendMessageW(k, 0x00F5, 0, 0)
                        clicked_demo = True
                        log("[%5.2f] clicked Demo Version" % t)
                        break
                continue
        if attempts < 3:
            if fill_and_submit(p.pid):
                attempts += 1
                log("[%5.2f] submitted sign-in (attempt %d)" % (t, attempts))
                time.sleep(1.5)
            continue
        time.sleep(0.2)

    log("timeout - closing the app so it is not left hanging")
    subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
    return 2


if __name__ == "__main__":
    sys.exit(main())



