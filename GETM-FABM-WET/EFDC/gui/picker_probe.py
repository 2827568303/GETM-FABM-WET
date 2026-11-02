# -*- coding: utf-8 -*-
"""Probe the EFDC 'Select Directory' picker and drive it to a target folder.

python -X utf8 gui/picker_probe.py "C:\\EFDC_M538"
"""
import ctypes
import ctypes.wintypes as wt
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import typegui as tg

u = ctypes.WinDLL("user32", use_last_error=True)
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
u.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u.SendMessageW.restype = ctypes.c_long
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

TARGET = sys.argv[1]


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
    u.SendMessageW(h, 0x0189, i, ctypes.cast(b, ctypes.c_void_p).value)  # LB_GETTEXT
    return b.value


def lb_count(h):
    return u.SendMessageW(h, 0x018B, 0, 0)  # LB_GETCOUNT


def lb_cur(h):
    return u.SendMessageW(h, 0x0188, 0, 0)  # LB_GETCURSEL


def settext(h, s):
    b = ctypes.create_unicode_buffer(s, len(s) + 1)
    return u.SendMessageW(h, 0x000C, 0, ctypes.cast(b, ctypes.c_void_p).value)


def click(h, fx=0.5, fy=0.5):
    r = rect(h)
    tg.click_screen(r[0] + (r[2] - r[0]) * fx, r[1] + (r[3] - r[1]) * fy)


def main():
    dlg = [h for h in tops() if "Select Directory" in txt(h) and u.IsWindowVisible(h)]
    if not dlg:
        print("picker not open")
        return 1
    d = dlg[0]
    u.SetForegroundWindow(d)
    time.sleep(0.2)
    for k in kids(d):
        c = cls(k)
        r = rect(k)
        if c.startswith("ThunderRT6") and u.IsWindowVisible(k):
            extra = ""
            if c in ("ThunderRT6DirListBox", "ThunderRT6FileListBox", "ThunderRT6DriveListBox"):
                extra = " count=%d cur=%d" % (lb_count(k), lb_cur(k))
                if c == "ThunderRT6DirListBox":
                    extra += " items=" + str([lb_text(k, i) for i in range(min(lb_count(k), 12))])
            print("%-26s %-22r %s%s" % (c, txt(k)[:22], r, extra))

    dirl = [k for k in kids(d) if cls(k) == "ThunderRT6DirListBox" and u.IsWindowVisible(k)]
    print("target:", TARGET)
    if not dirl:
        print("no dir listbox")
        return 2
    dl = dirl[0]
    n = lb_count(dl)
    print("dirlist entries:", [lb_text(dl, i) for i in range(n)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
