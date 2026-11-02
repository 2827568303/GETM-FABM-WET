# -*- coding: utf-8 -*-
"""DPI-aware model loader: restore the EFDC window, click the Directory box, type the path.

python -X utf8 gui/open_model2.py "<model folder>" [--shot name]
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
try:
    u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

u.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u.SendMessageW.restype = ctypes.c_ulong
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

MODEL = sys.argv[1]
SHOT = sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else "model2"
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


def gettext(h):
    b = ctypes.create_unicode_buffer(1024)
    u.SendMessageW(h, 0x000D, 1024, ctypes.cast(b, ctypes.c_void_p).value)
    return b.value


def tops():
    out = []

    def cb(h, l):
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


def find_demo_form():
    for h in tops():
        t = txt(h)
        if "EFDC_Explorer" in t and "Sign in" not in t and "Activation" not in t and u.IsWindowVisible(h):
            return h
    return None


def main():
    form = find_demo_form()
    if not form:
        print("EFDC main window not found")
        return 1
    print("form %r" % txt(form))

    # the app likes to start minimized; restore + give it a real place on screen
    if u.IsIconic(form):
        u.ShowWindow(form, 9)
    u.SetWindowPos(form, -1, 80, 80, 900, 700, 0x0040 | 0x0004)
    time.sleep(0.4)
    u.BringWindowToTop(form)
    u.SetForegroundWindow(form)
    time.sleep(0.3)
    r = wt.RECT()
    u.GetWindowRect(form, ctypes.byref(r))
    print("rect=%s focus=%s" % ((r.left, r.top, r.right, r.bottom), hex(tg.focused_window(form) or 0)))

    cands = []
    for k in kids(form):
        c = cls(k)
        kr = wt.RECT()
        u.GetWindowRect(k, ctypes.byref(kr))
        w, hgt = kr.right - kr.left, kr.bottom - kr.top
        if c == "ThunderRT6TextBox" and w >= 400 and hgt <= 40 and kr.top - r.top < 220:
            cands.append((w, k, (kr.left, kr.top, kr.right, kr.bottom)))
    cands.sort(reverse=True)
    for w, k, kr in cands[:6]:
        print("  candidate w=%-5d rect=%s text=%r" % (w, kr, gettext(k)))
    if not cands:
        print("no directory textbox found")
        return 2

    w, box, kr = cands[0]
    ok = False
    for attempt in range(3):
        u.BringWindowToTop(form)
        u.SetForegroundWindow(form)
        time.sleep(0.25)
        tg.click_screen((kr[0] + kr[2]) / 2, (kr[1] + kr[3]) / 2)
        time.sleep(0.35)
        foc = tg.focused_window(form)
        print("  click attempt %d -> focus=%s" % (attempt + 1, hex(foc or 0)))
        if foc == box:
            ok = True
            break
    if not ok:
        print("could not focus the directory field")
        capture(form, os.path.join(OUT, SHOT + "_nofocus.png"))
        return 3

    tg.press(0x23)  # End
    for _ in range(len(gettext(box)) + 4):
        tg.press(0x08)
    tg.type_unicode(MODEL, delay=0.02)
    time.sleep(0.3)
    print("typed: %r" % gettext(box))
    tg.press(0x0D)  # Enter
    time.sleep(7)
    print("capture:", capture(form, os.path.join(OUT, SHOT + ".png")))
    # report any dialog that appeared
    for h in tops():
        if h == form:
            continue
        t = txt(h)
        if t and cls(h) in ("#32770", "ThunderRT6FormDC") and u.IsWindowVisible(h):
            print("dialog: %r %s" % (t, cls(h)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
