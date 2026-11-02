# -*- coding: utf-8 -*-
"""Click every toolbar slot in the EFDC window, dismissing any dialogs, and report what opened.

python -X utf8 gui/scan_toolbar.py [x0] [x1] [step] [y]
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

X0 = int(sys.argv[1]) if len(sys.argv) > 1 else 30
X1 = int(sys.argv[2]) if len(sys.argv) > 2 else 660
STEP = int(sys.argv[3]) if len(sys.argv) > 3 else 34
Y = int(sys.argv[4]) if len(sys.argv) > 4 else 44


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


def dismiss():
    for h in tops():
        if not u.IsWindowVisible(h) or cls(h) not in ("#32770", "ThunderRT6FormDC"):
            continue
        for k in kids(h):
            t = txt(k).strip()
            if cls(k) in ("Button", "ThunderRT6CommandButton") and t in ("确定", "取消", "Cancel", "OK", "Close"):
                r = rect(k)
                tg.click_screen((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
                return txt(h)
    return None


def main():
    form = [h for h in tops() if "EFDC_Explorer8.4 Demo" in txt(h) and u.IsWindowVisible(h)][0]
    tg.focus(form)          # restore from -48000 and raise above leftovers
    time.sleep(0.5)
    l, t, _, _ = rect(form)
    for x in range(X0, X1, STEP):
        u.SetForegroundWindow(form)
        time.sleep(0.12)
        tg.click_screen(l + x, t + Y)
        time.sleep(0.9)
        opened = [txt(h) for h in tops()
                  if h != form and u.IsWindowVisible(h) and cls(h) in ("#32770", "ThunderRT6FormDC")]
        print("x=%-3d %s" % (x, opened[:2]), flush=True)
        d = dismiss()
        if d:
            print("    dismissed %r" % d, flush=True)
            time.sleep(0.4)
    return 0


if __name__ == "__main__":
    sys.exit(main())
