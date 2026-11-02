# -*- coding: utf-8 -*-
"""Load a model through the Demo UI's Browse picker using WM_SETTEXT (no typing).

python -X utf8 gui/open_model3.py "<model folder>"
"""
import ctypes
import ctypes.wintypes as wt
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import typegui as tg
from win_shot import capture

u = ctypes.WinDLL("user32", use_last_error=True)
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
u.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u.SendMessageW.restype = ctypes.c_long
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

MODEL = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(OUT, exist_ok=True)


def txt(h):
    b = ctypes.create_unicode_buffer(512)
    u.GetWindowTextW(h, b, 512)
    return b.value


def cls(h):
    b = ctypes.create_unicode_buffer(128)
    u.GetClassNameW(h, b, 128)
    return b.value


def rect(h):
    r = wt.RECT()
    u.GetWindowRect(h, ctypes.byref(r))
    return (r.left, r.top, r.right, r.bottom)


def tops():
    o = []

    def cb(h, l):
        o.append(h)
        return True

    u.EnumWindows(CB(cb), 0)
    return o


def kids(h):
    o = []

    def cb(c, l):
        o.append(c)
        return True

    u.EnumChildWindows(h, CB(cb), 0)
    return o


def settext(h, s):
    buf = ctypes.create_unicode_buffer(s, len(s) + 1)
    return u.SendMessageW(h, 0x000C, 0, ctypes.cast(buf, ctypes.c_void_p).value)


def click(h):
    r = rect(h)
    tg.click_screen((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)


def main():
    form = None
    for h in tops():
        if "EFDC_Explorer8.4 Demo Version" in txt(h) and u.IsWindowVisible(h):
            form = h
    if not form:
        print("demo UI not running")
        return 1
    if u.IsIconic(form):
        u.ShowWindow(form, 9)
    u.SetWindowPos(form, -1, 60, 60, 1000, 740, 0x0040 | 0x0004)
    time.sleep(0.4)
    u.BringWindowToTop(form)
    u.SetForegroundWindow(form)
    time.sleep(0.3)

    btn = [k for k in kids(form) if cls(k).startswith("ThunderRT6CommandButton")
           and txt(k).strip() == "Browse" and u.IsWindowVisible(k)]
    if not btn:
        print("no Browse button")
        return 2
    click(btn[0])
    time.sleep(2.0)

    dlg = [h for h in tops() if "Select Directory" in txt(h) and u.IsWindowVisible(h)]
    if not dlg:
        print("picker not found")
        return 3
    d = dlg[0]
    print("picker %r" % txt(d))
    combo = [k for k in kids(d) if cls(k) == "ThunderRT6ComboBox" and u.IsWindowVisible(k)]
    if not combo:
        print("no combo")
        return 4
    print("set text ->", settext(combo[0], MODEL))
    time.sleep(0.4)
    ok = [k for k in kids(d) if cls(k) == "ThunderRT6CommandButton"
          and txt(k).strip().upper() == "OK" and u.IsWindowVisible(k)]
    if not ok:
        print("no OK")
        return 5
    click(ok[0])
    time.sleep(6)
    print("picker still open:", bool(u.IsWindowVisible(d)))
    print("capture:", capture(form, os.path.join(OUT, "loaded.png")))
    caps = [k for k in kids(form) if cls(k).startswith("ThunderRT6") and txt(k)]
    print("form texts:", [txt(k)[:40] for k in caps][:20])
    for h in tops():
        if u.IsWindowVisible(h) and cls(h) in ("#32770",):
            print("popup:", repr(txt(h)))
            print("  shot:", capture(h, os.path.join(OUT, "loaded_popup.png")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
