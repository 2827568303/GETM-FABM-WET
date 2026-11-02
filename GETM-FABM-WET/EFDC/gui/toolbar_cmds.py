# -*- coding: utf-8 -*-
"""Replay toolbar commands with the toolbar handle as lParam, watching for dialogs/writes.

python -X utf8 gui/toolbar_cmds.py [id ...]
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

IDS = [int(a) for a in sys.argv[1:]] or [6, 5, 3]


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
    form = [h for h in tops() if "EFDC_Explorer8.4 Demo" in txt(h) and u.IsWindowVisible(h)][0]
    tg.focus(form)
    time.sleep(0.4)
    l, t, _, _ = rect(form)

    toolbar = None
    for k in kids(form):
        kr = rect(k)
        c = cls(k)
        if kr[2] - kr[0] > 600 and 10 <= kr[1] - t <= 80 and kr[3] - kr[1] < 90:
            print("candidate toolbar: %s %s %s" % (hex(k), c, kr))
            if toolbar is None or kr[1] < rect(toolbar)[1]:
                toolbar = k
    print("toolbar =", hex(toolbar) if toolbar else None)

    for cid in IDS:
        u.PostMessageW(form, 0x0111, cid, toolbar or 0)
        time.sleep(1.2)
        opened = [txt(h) for h in tops()
                  if h != form and u.IsWindowVisible(h) and cls(h) in ("#32770", "ThunderRT6FormDC")]
        print("id=%-3d lparam=%s -> %s" % (cid, hex(toolbar or 0), opened[:3]), flush=True)
        for h in tops():
            if h != form and u.IsWindowVisible(h) and cls(h) == "#32770":
                for k in kids(h):
                    if cls(k) == "Button":
                        r = rect(k)
                        tg.click_screen((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
                        break
                time.sleep(0.4)
    return 0


if __name__ == "__main__":
    sys.exit(main())
