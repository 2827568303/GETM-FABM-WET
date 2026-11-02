# -*- coding: utf-8 -*-
"""Load a model into the EFDC Explorer Demo UI by typing its folder into the Directory box.

python -X utf8 gui/open_model.py "<model folder>" [--shot name]
Assumes the app is already running in the Demo UI (see autologin.py).
"""
import ctypes
import ctypes.wintypes as wt
import os
import sys
import time

import typegui as tg
from win_shot import capture

u = ctypes.WinDLL("user32", use_last_error=True)
u.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
u.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u.SendMessageW.restype = ctypes.c_ulong
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

MODEL = sys.argv[1]
SHOT = sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else "model_loaded"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(OUT, exist_ok=True)


def txt(h):
    b = ctypes.create_unicode_buffer(512); u.GetWindowTextW(h, b, 512); return b.value


def cls(h):
    b = ctypes.create_unicode_buffer(128); u.GetClassNameW(h, b, 128); return b.value


def gettext(h):
    b = ctypes.create_unicode_buffer(512)
    u.SendMessageW(h, 0x000D, 512, ctypes.cast(b, ctypes.c_void_p).value)
    return b.value


def tops(pid=None):
    out = []

    def cb(h, l):
        if pid is None or (lambda: (lambda p: p.value == pid)(wt.DWORD(0)))():
            out.append(h)
        return True

    u.EnumWindows(CB(cb), 0)
    return out


def find_demo_form():
    for h in tops():
        t = txt(h)
        if "Demo Version" in t and "Sign in" not in t and u.IsWindowVisible(h):
            return h
    return None


def kids(h):
    out = []

    def cb(c, l):
        out.append(c)
        return True

    u.EnumChildWindows(h, CB(cb), 0)
    return out


def main():
    form = find_demo_form()
    if not form:
        print("Demo UI not found - run gui/autologin.py first")
        return 1
    fl, ft, fr, fb = tg.rect(form)
    print("form %r rect=%s" % (txt(form), (fl, ft, fr, fb)))

    # the Directory field: widest text-ish control in the top ~160 px of the client area
    cands = []
    for k in kids(form):
        c = cls(k)
        r = tg.rect(k)
        w, hgt = r[2] - r[0], r[3] - r[1]
        if c == 'ThunderRT6TextBox' and w >= 400 and hgt <= 40 and r[1] - ft < 200:
            cands.append((w, k, r, c))
    cands.sort(reverse=True)
    for w, k, r, c in cands[:5]:
        print("  candidate %-22s w=%-5d rect=%s text=%r" % (c, w, r, gettext(k)))
    if not cands:
        print("no candidate field found")
        return 2

    w, box, r, c = cands[0]
    print("using %s at %s" % (c, r))
    if not tg.click_and_focus(form, box):
        print("could not focus the directory field")
        return 3
    tg.press(0x23)  # End
    for _ in range(len(gettext(box)) + 4):
        tg.press(0x08)
    tg.type_unicode(MODEL, delay=0.03)
    time.sleep(0.3)
    print("typed: %r" % gettext(box))
    tg.press(0x0D)  # Enter
    time.sleep(6)
    try:
        print("capture:", capture(form, os.path.join(OUT, SHOT + ".png")))
    except Exception as e:
        print("capture failed:", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())

