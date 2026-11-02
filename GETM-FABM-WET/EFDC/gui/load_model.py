# -*- coding: utf-8 -*-
"""Load a model in the running EFDC Demo UI through Browse + OK (focus-safe).

python -X utf8 gui/load_model.py
"""
import ctypes
import ctypes.wintypes as wt
import sys
import time

sys.path.insert(0, __file__.rsplit("\\", 1)[0])
import typegui as tg

u = ctypes.WinDLL("user32", use_last_error=True)
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


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


def main():
    forms = [h for h in tops() if "EFDC_Explorer8.4 Demo" in txt(h) and u.IsWindowVisible(h)]
    if not forms:
        print("no demo UI")
        return 1
    form = forms[0]
    tg.focus(form)
    time.sleep(0.5)
    btn = [k for k in kids(form) if cls(k).startswith("ThunderRT6CommandButton")
           and txt(k).strip() == "Browse" and u.IsWindowVisible(k)]
    if not btn:
        print("no Browse button")
        return 2
    r = rect(btn[0])
    tg.click_screen((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
    time.sleep(2.5)
    dlg = [h for h in tops() if "Select Directory" in txt(h) and u.IsWindowVisible(h)]
    if not dlg:
        print("no picker")
        return 3
    d = dlg[0]
    ok = [k for k in kids(d) if cls(k) == "ThunderRT6CommandButton"
          and txt(k).strip().upper() == "OK" and u.IsWindowVisible(k)]
    if not ok:
        print("no OK")
        return 4
    r = rect(ok[0])
    tg.click_screen((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
    time.sleep(12)
    for h in tops():
        if cls(h) == "#32770" and u.IsWindowVisible(h):
            for k in kids(h):
                if cls(k) == "Button":
                    r = rect(k)
                    tg.click_screen((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
                    break
            time.sleep(0.6)
    print("loaded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
