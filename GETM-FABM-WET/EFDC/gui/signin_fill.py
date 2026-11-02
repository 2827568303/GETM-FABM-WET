# -*- coding: utf-8 -*-
"""Fill the EFDC Demo sign-in form: focus-verified click, backspace-clear, verified typing."""
import ctypes
import ctypes.wintypes as wt
import time

import typegui as tg

u = ctypes.WinDLL("user32", use_last_error=True)
u.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u.SendMessageW.restype = ctypes.c_ulong
u.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def txt(h):
    b = ctypes.create_unicode_buffer(512); u.GetWindowTextW(h, b, 512); return b.value


def cls(h):
    b = ctypes.create_unicode_buffer(128); u.GetClassNameW(h, b, 128); return b.value


def gettext(h):
    b = ctypes.create_unicode_buffer(512)
    u.SendMessageW(h, 0x000D, 512, ctypes.cast(b, ctypes.c_void_p).value)
    return b.value


def kids(h):
    out = []

    def cb(c, l):
        out.append(c)
        return True

    u.EnumChildWindows(h, CB(cb), 0)
    return out


def put_text(h_form, box, text, log=print, tries=3):
    """Focus the box (verified), clear with Backspace only, type, verify."""
    for attempt in range(1, tries + 1):
        if not tg.click_and_focus(h_form, box):
            log("   could not focus the field (attempt %d)" % attempt)
            continue
        cur = gettext(box)
        tg.press(0x23)  # End
        for _ in range(len(cur) + 2):
            tg.press(0x08)          # Backspace
        tg.type_unicode(text, delay=0.03)
        time.sleep(0.2)
        got = gettext(box)
        log("   attempt %d: got %r" % (attempt, got))
        if got == text:
            return True
    return False


def fill_signin(h, email, pwd, log=print):
    boxes = [k for k in kids(h) if cls(k) == "ThunderRT6TextBox"]
    if len(boxes) < 2:
        log("   expected 2 text boxes, found %d" % len(boxes))
        return False
    # geometry decides: the upper box is Email (id 6 on this build), the lower one is Password
    boxes.sort(key=lambda x: tg.rect(x)[1])
    email_box, pwd_box = boxes[0], boxes[1]
    if email_box == pwd_box:
        log("   email/password map to the same control")
        return False

    if not put_text(h, email_box, email, log=log):
        log("   email field failed")
        return False
    if not put_text(h, pwd_box, pwd, log=log):
        log("   password field failed")
        return False

    btn = None
    for k in kids(h):
        if cls(k).startswith("ThunderRT6CommandButton") and "Sign" in txt(k) and "&In" in txt(k):
            btn = k
    if not btn:
        log("   Sign In button not found")
        return False
    tg.focus(h)
    tg.click_window(btn)
    log("   submitted")
    return True


