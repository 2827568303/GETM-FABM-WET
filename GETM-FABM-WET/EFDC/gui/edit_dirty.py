# -*- coding: utf-8 -*-
"""Make the loaded model dirty through a panel edit, then trigger the save command.

python -X utf8 gui/edit_dirty.py
"""
import ctypes
import ctypes.wintypes as wt
import os
import sys
import time

sys.path.insert(0, __file__.rsplit("\\", 1)[0])
import typegui as tg

u = ctypes.WinDLL("user32", use_last_error=True)
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
u.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u.SendMessageW.restype = ctypes.c_long
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

MODEL = r"C:\EFDC_M538_SAVE"


def txt(h):
    b = ctypes.create_unicode_buffer(512)
    u.GetWindowTextW(h, b, 512)
    return b.value


def cls(h):
    b = ctypes.create_unicode_buffer(128)
    u.GetClassNameW(h, b, 128)
    return b.value


def gm(h):
    b = ctypes.create_unicode_buffer(512)
    u.SendMessageW(h, 0x000D, 512, ctypes.cast(b, ctypes.c_void_p).value)
    return b.value


def settext(h, s):
    b = ctypes.create_unicode_buffer(s, len(s) + 1)
    return u.SendMessageW(h, 0x000C, 0, ctypes.cast(b, ctypes.c_void_p).value)


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


def mtimes():
    out = {}
    for f in os.listdir(MODEL):
        p = os.path.join(MODEL, f)
        if os.path.isfile(p):
            out[f] = os.path.getmtime(p)
    return out


def main():
    form = [h for h in tops() if "EFDC_Explorer8.4 Demo" in txt(h) and u.IsWindowVisible(h)][0]
    boxes = [k for k in kids(form) if cls(k) == "ThunderRT6TextBox"]
    title = [k for k in boxes if gm(k) == "Title"]
    pid_box = [k for k in boxes if k not in title and gm(k) == ""]
    print("title box:", [hex(k) for k in title], "empty boxes:", [hex(k) for k in pid_box][:3])

    if title:
        settext(title[0], "EDITED_BY_AUTOMATION")
        print("title now:", repr(gm(title[0])))

    btns = [(txt(k), k) for k in kids(form) if cls(k) == "ThunderRT6CommandButton"]
    apply_like = [b for b in btns if b[0].strip() in ("Apply", "OK", "&OK", "Update", "Save")]
    print("apply-like buttons:", [(t, hex(k)) for t, k in apply_like][:6])

    for t, k in apply_like[:3]:
        u.SendMessageW(k, 0x00F5, 0, 0)   # BM_CLICK
        print("clicked", t)
        time.sleep(1.2)
        for h in tops():
            if h != form and u.IsWindowVisible(h) and cls(h) in ("#32770",):
                print("  dialog:", repr(txt(h)))
                for kk in kids(h):
                    if cls(kk) == "Button":
                        r = rect(kk)
                        tg.click_screen((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
                        break
                time.sleep(0.5)

    before = mtimes()
    u.PostMessageW(form, 0x0111, 3, 0)   # save command
    time.sleep(3)
    after = mtimes()
    changed = [k for k in after if before.get(k) != after[k]]
    print("files changed by id=3:", changed)
    for h in tops():
        if h != form and u.IsWindowVisible(h) and cls(h) in ("#32770",):
            print("dialog after save:", repr(txt(h)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
