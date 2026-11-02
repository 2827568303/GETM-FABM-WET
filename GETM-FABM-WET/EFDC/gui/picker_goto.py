# -*- coding: utf-8 -*-
"""Navigate the EFDC 'Select Directory' picker to a sub-folder and confirm with OK.

python -X utf8 gui/picker_goto.py "<subfolder name>" [--ok]

Assumes the picker is already open and the target folder is a child of the folder
the picker currently shows (it opens in the app's working directory).
"""
import ctypes
import ctypes.wintypes as wt
import sys
import time

sys.path.insert(0, __file__.rsplit("\\", 1)[0])
import typegui as tg

u = ctypes.WinDLL("user32", use_last_error=True)
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
u.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u.SendMessageW.restype = ctypes.c_long
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

NAME = sys.argv[1]
DO_OK = "--ok" in sys.argv


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


def lb_text(h, i):
    b = ctypes.create_unicode_buffer(512)
    u.SendMessageW(h, 0x0189, i, ctypes.cast(b, ctypes.c_void_p).value)
    return b.value


def lb_count(h):
    return u.SendMessageW(h, 0x018B, 0, 0)


def lb_cur(h):
    return u.SendMessageW(h, 0x0188, 0, 0)


def lb_setcur(h, i):
    u.SendMessageW(h, 0x0186, i, 0)  # LB_SETCURSEL


def main():
    dlg = [h for h in tops() if "Select Directory" in txt(h) and u.IsWindowVisible(h)]
    if not dlg:
        print("picker not open")
        return 1
    d = dlg[0]
    u.SetForegroundWindow(d)
    time.sleep(0.3)
    dl = [k for k in kids(d) if cls(k) == "ThunderRT6DirListBox" and u.IsWindowVisible(k)][0]
    items = [lb_text(dl, i) for i in range(lb_count(dl))]
    print("current dirlist:", items)
    idx = None
    for i, s in enumerate(items):
        if NAME.lower() in s.lower():
            idx = i
            break
    if idx is None:
        print("target %r not in list" % NAME)
        return 2

    l, t, r, b = rect(dl)
    item_h = max(10, (b - t) // max(1, lb_count(dl)))
    y = t + int(item_h * (idx + 0.5))
    x = l + 30
    print("click item %d (%r) at %s" % (idx, items[idx], (x, y)))
    tg.click_screen(x, y)
    time.sleep(0.8)
    after = [lb_text(dl, i) for i in range(lb_count(dl))]
    print("dirlist after click:", after)

    if DO_OK:
        ok = [k for k in kids(d) if cls(k) == "ThunderRT6CommandButton"
              and txt(k).strip().upper() == "OK" and u.IsWindowVisible(k)][0]
        rr = rect(ok)
        tg.click_screen((rr[0] + rr[2]) / 2, (rr[1] + rr[3]) / 2)
        print("clicked OK")
        time.sleep(2)
        print("picker open:", bool(u.IsWindowVisible(d)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
