# -*- coding: utf-8 -*-
"""Sign in to the already running EFDC Demo sign-in form (no process spawn).

python -X utf8 gui/signin_only.py [email] [password]
"""
import ctypes
import ctypes.wintypes as wt
import sys
import time

sys.path.insert(0, __file__.rsplit("\\", 1)[0])
import typegui as tg
import signin_fill

u = ctypes.WinDLL("user32", use_last_error=True)
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

EMAIL = sys.argv[1] if len(sys.argv) > 1 else "zhang.san8888@gmail.com"
PWD = sys.argv[2] if len(sys.argv) > 2 else "Efdc2026!"


def txt(h):
    b = ctypes.create_unicode_buffer(512)
    u.GetWindowTextW(h, b, 512)
    return b.value


def tops():
    o = []

    def cb(h, l):
        o.append(h)
        return True

    u.EnumWindows(CB(cb), 0)
    return o


def main():
    deadline = time.time() + 40
    while time.time() < deadline:
        sign = [h for h in tops() if "Sign in EEMS Demo" in txt(h) and u.IsWindowVisible(h)]
        if sign:
            print("sign-in form", hex(sign[0]))
            ok = signin_fill.fill_signin(sign[0], EMAIL, PWD, log=print)
            print("filled:", ok)
            return 0 if ok else 1
        time.sleep(0.5)
    print("no sign-in form")
    return 2


if __name__ == "__main__":
    sys.exit(main())
