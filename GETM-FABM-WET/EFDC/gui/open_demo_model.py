# -*- coding: utf-8 -*-
"""Open a model from the EFDC Demo UI via its Browse button (DPI-aware).

python -X utf8 gui/open_demo_model.py "<model folder>" [--shot name]
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
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

MODEL = sys.argv[1]
SHOT = sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else "model"
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


def center(h):
    l, t, r, b = rect(h)
    return (l + r) / 2, (t + b) / 2


def main():
    form = None
    for h in tops():
        t = txt(h)
        if "EFDC_Explorer8.4 Demo Version" in t:
            form = h
            break
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
    print("form %r rect=%s" % (txt(form), rect(form)))

    btn = None
    for k in kids(form):
        if cls(k).startswith("ThunderRT6CommandButton") and txt(k).strip() == "Browse" and u.IsWindowVisible(k):
            btn = k
    if not btn:
        print("no visible Browse button")
        return 2
    x, y = center(btn)
    print("click Browse at %s" % ((x, y),))
    tg.click_screen(x, y)
    time.sleep(2.0)

    dlg = None
    for h in tops():
        t = txt(h)
        if "Select Directory" in t and u.IsWindowVisible(h):
            dlg = h
    if not dlg:
        print("picker dialog not found")
        return 3
    print("dialog %r %s rect=%s" % (txt(dlg), cls(dlg), rect(dlg)))

    combo = None
    for k in kids(dlg):
        if cls(k) == "ThunderRT6ComboBox" and u.IsWindowVisible(k):
            combo = k
    if not combo:
        print("no file-name combo")
        return 4
    u.SetForegroundWindow(dlg)
    time.sleep(0.2)
    x, y = center(combo)
    tg.click_screen(x, y)
    time.sleep(0.4)
    print("  combo focus now %s (target %s)" % (hex(tg.focused_window(dlg) or 0), hex(combo)))
    tg.type_unicode(MODEL, delay=0.015)
    time.sleep(0.4)
    ok = None
    for k in kids(dlg):
        if cls(k) == "ThunderRT6CommandButton" and txt(k).strip().upper() == "OK" and u.IsWindowVisible(k):
            ok = k
    if not ok:
        print("no OK button")
        return 5
    x, y = center(ok)
    tg.click_screen(x, y)
    time.sleep(8)
    print("picker still visible:", bool(u.IsWindowVisible(dlg)))
    print("capture:", capture(form, os.path.join(OUT, SHOT + ".png")))
    for h in tops():
        if u.IsWindowVisible(h) and h != form:
            t = txt(h)
            if t and cls(h) in ("#32770", "ThunderRT6FormDC"):
                print("popup: %r %s" % (t, cls(h)))
                try:
                    print("   shot:", capture(h, os.path.join(OUT, SHOT + "_popup.png")))
                except Exception as e:
                    print("   shot fail", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
