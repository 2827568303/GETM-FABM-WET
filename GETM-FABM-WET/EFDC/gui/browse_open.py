# -*- coding: utf-8 -*-
"""Load a model via the Browse button in the EFDC Demo UI.

python -X utf8 gui/browse_open.py "<model folder>" [--shot name]
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
u.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u.SendMessageW.restype = ctypes.c_ulong
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

MODEL = sys.argv[1]
SHOT = sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else "after_browse"
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


def all_windows():
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


def demo_form():
    for h in all_windows():
        t = txt(h)
        if "Demo Version" in t and "Sign in" not in t and u.IsWindowVisible(h):
            return h
    return None


def click_browse(form):
    for k in kids(form):
        if cls(k).startswith("ThunderRT6CommandButton") and "Browse" in txt(k):
            tg.focus(form)
            tg.click_window(k)
            return True
    return False


def fill_browse_dialog(path, before):
    """Find the newly appeared dialog and put the folder path into its edit box."""
    deadline = time.time() + 6
    while time.time() < deadline:
        for h in all_windows():
            if h in before or not u.IsWindowVisible(h):
                continue
            c = cls(h)
            if c == "#32770" or "ThunderRT6FormDC" in c:
                print("dialog %r (%s)" % (txt(h), c))
                edits = [k for k in kids(h) if cls(k) in ("Edit", "ThunderRT6TextBox")]
                if not edits:
                    continue
                box = edits[0]
                if not tg.click_and_focus(h, box):
                    # try every edit until one takes focus
                    for e in edits:
                        if tg.click_and_focus(h, e):
                            box = e
                            break
                tg.press(0x23)
                for _ in range(len(gettext(box)) + 2):
                    tg.press(0x08)
                tg.type_unicode(path, delay=0.03)
                print("typed: %r" % gettext(box))
                tg.press(0x0D)
                return h
        time.sleep(0.25)
    return None


def main():
    form = demo_form()
    if not form:
        print("Demo UI not found")
        return 1
    before = set(all_windows())
    if not click_browse(form):
        print("Browse button not found")
        return 2
    print("clicked Browse")
    dlg = fill_browse_dialog(MODEL, before)
    if dlg:
        time.sleep(1.0)
        # some dialogs need an explicit OK
        for k in kids(dlg):
            if cls(k) in ("Button", "ThunderRT6CommandButton") and txt(k).strip() in ("OK", "确定"):
                tg.click_window(k)
                print("clicked OK")
                break
    time.sleep(6)
    try:
        print("capture:", capture(form, os.path.join(OUT, SHOT + ".png")))
    except Exception as e:
        print("capture failed:", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
