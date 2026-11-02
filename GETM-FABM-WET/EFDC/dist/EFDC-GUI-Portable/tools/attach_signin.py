# -*- coding: utf-8 -*-
"""Fill the EFDC Demo sign-in form that appears on a fresh machine.

Used by 启动EFDC.bat: the launcher starts the app itself, then this script fills the
"Sign in EEMS Demo Version" form, ticks "Remember Password" and submits it.

Field mapping is decided by GEOMETRY (the upper box is Email, the lower one is
Password) and every write is read back; if the two boxes turn out to be swapped,
the values are exchanged and rewritten. Any "Invalid Email format" style dialog is
dismissed and the submission retried.

python -X utf8 attach_signin.py [timeout_sec]
"""
import ctypes
import ctypes.wintypes as wt
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import typegui as tg

u = ctypes.WinDLL("user32", use_last_error=True)
u.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u.SendMessageW.restype = ctypes.c_long
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

TIMEOUT = float(sys.argv[1]) if len(sys.argv) > 1 else 45.0
EMAIL = "zhang.san8888@gmail.com"
PWD = "Efdc2026!"
MAX_ATTEMPTS = 3


def log(*a):
    print(*a, flush=True)


def load_credentials():
    global EMAIL, PWD
    ini = os.path.join(os.environ.get("PUBLIC", r"C:\Users\Public"), "DSI", "EEMS8.3", "EEMS.ini")
    try:
        for line in open(ini, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if line.startswith("demo_email=") and line.split("=", 1)[1].strip():
                EMAIL = line.split("=", 1)[1].strip()
            if line.startswith("demo_password=") and line.split("=", 1)[1].strip():
                PWD = line.split("=", 1)[1].strip()
    except Exception:
        pass


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


def gettext(h):
    b = ctypes.create_unicode_buffer(512)
    u.SendMessageW(h, 0x000D, 512, ctypes.cast(b, ctypes.c_void_p).value)
    return b.value


def settext(h, s):
    b = ctypes.create_unicode_buffer(s, len(s) + 1)
    return u.SendMessageW(h, 0x000C, 0, ctypes.cast(b, ctypes.c_void_p).value)


def find_efdc_pid():
    for h in tops():
        if "EFDC_Explorer" in txt(h) and u.IsWindowVisible(h):
            p = wt.DWORD(0)
            u.GetWindowThreadProcessId(h, ctypes.byref(p))
            return p.value
    return 0


def visible_windows(pid):
    out = []
    for h in tops():
        p = wt.DWORD(0)
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid and u.IsWindowVisible(h):
            out.append((cls(h), txt(h), h))
    return out


def dialog_text(h):
    """Collect the text of a message box (title + all static children)."""
    parts = [txt(h)]
    for k in kids(h):
        if cls(k) == "Static":
            t = txt(k)
            if t:
                parts.append(t)
    return " | ".join(p for p in parts if p)


FATAL_MARKERS = ("will stop now", "licenseWrapper is not valid", "LicenseWrapper Is Nothing",
                 "could not get the host id", "problems with your license")


def scan_dialogs(pid):
    """Return (fatal_text, dismissable_handle).  A fatal licence error must NOT be clicked away."""
    fatal = ""
    dismiss = None
    for c, s, h in visible_windows(pid):
        if c != "#32770":
            continue
        text = dialog_text(h)
        low = text.lower()
        if any(m.lower() in low for m in FATAL_MARKERS):
            fatal = text
        else:
            dismiss = h
    return fatal, dismiss


def dismiss_error_dialog(pid):
    """Close message boxes such as 'Invalid Email format, please correct it.'"""
    fatal, h = scan_dialogs(pid)
    if fatal or h is None:
        return False
    log("   dialog seen: %r" % dialog_text(h)[:80])
    for k in kids(h):
        if cls(k) in ("Button", "ThunderRT6CommandButton") and txt(k):
            u.SendMessageW(k, 0x00F5, 0, 0)   # BM_CLICK
            time.sleep(0.6)
            return True
    return False


def text_boxes(form):
    boxes = [k for k in kids(form) if cls(k) == "ThunderRT6TextBox" and u.IsWindowVisible(k)]
    boxes.sort(key=lambda k: rect(k)[1])          # upper box first
    return boxes


def fill_and_submit(form):
    boxes = text_boxes(form)
    if len(boxes) < 2:
        log("   expected 2 text boxes, found %d" % len(boxes))
        return False
    email_box, pwd_box = boxes[0], boxes[1]

    settext(email_box, EMAIL)
    settext(pwd_box, PWD)
    time.sleep(0.3)

    got_email, got_pwd = gettext(email_box), gettext(pwd_box)
    # self-correct if the app laid the two boxes out the other way round
    if "@" not in got_email or got_pwd == PWD and got_email == PWD:
        if "@" in got_pwd:
            email_box, pwd_box = pwd_box, email_box
            settext(email_box, EMAIL)
            settext(pwd_box, PWD)
            time.sleep(0.3)
            got_email, got_pwd = gettext(email_box), gettext(pwd_box)
    log("   email=%r  pwd_len=%d" % (got_email, len(got_pwd)))

    if "@" not in got_email:
        log("   email field still does not hold an address, trying the keyboard path")
        try:
            email_box, pwd_box = boxes[0], boxes[1]
            tg.click_and_focus(form, email_box)
            tg.press(0x23)
            for _ in range(len(gettext(email_box)) + 2):
                tg.press(0x08)
            tg.type_unicode(EMAIL, 0.03)
            tg.click_and_focus(form, pwd_box)
            tg.press(0x23)
            for _ in range(len(gettext(pwd_box)) + 2):
                tg.press(0x08)
            tg.type_unicode(PWD, 0.03)
            got_email = gettext(email_box)
            log("   after keyboard path: email=%r" % got_email)
        except Exception as e:
            log("   keyboard path failed: %s" % e)

    # tick "Remember Password" so the next start signs in silently
    for k in kids(form):
        if cls(k).startswith("ThunderRT6CheckBox") and "Remember" in txt(k):
            try:
                state = u.SendMessageW(k, 0x00F0, 0, 0)   # BM_GETCHECK
                if state == 0:
                    u.SendMessageW(k, 0x00F5, 0, 0)       # BM_CLICK
                    log("   ticked Remember Password")
            except Exception:
                pass
            break

    btn = None
    for k in kids(form):
        if cls(k).startswith("ThunderRT6CommandButton") and "Sign" in txt(k):
            btn = k
    if not btn:
        log("   Sign In button not found")
        return False
    u.SendMessageW(btn, 0x00F5, 0, 0)                      # BM_CLICK
    log("   submitted sign-in")
    return True


def main():
    load_credentials()
    log("   sign-in helper: email=%r" % EMAIL)
    t0 = time.time()
    attempts = 0
    while time.time() - t0 < TIMEOUT:
        pid = find_efdc_pid()
        if not pid:
            time.sleep(0.4)
            continue
        fatal, _ = scan_dialogs(pid)
        if fatal:
            log("")
            log("  ===============================================================")
            log("   FATAL: %s" % fatal)
            log("   许可组件没有加载成功，程序会自己退出（所以窗口一闪就没）。")
            log("   处理：确认启动器第 [2/8] 步出现 unblocked ...、第 [6/8] 步出现")
            log("         ok license wrapper registered；然后重跑 启动EFDC.bat。")
            log("  ===============================================================")
            return 3
        forms = visible_windows(pid)
        if any("Demo Version" in s and "Sign in" not in s for c, s, h in forms) and attempts > 0:
            log("OK: EFDC_Explorer8.4 main window is up")
            return 0
        if dismiss_error_dialog(pid):
            time.sleep(0.5)
            continue
        wizard = [h for c, s, h in forms if "Activation Wizard" in s]
        if wizard:
            for k in kids(wizard[0]):
                if cls(k).startswith("ThunderRT6CommandButton") and "Demo Version" in txt(k):
                    u.SendMessageW(k, 0x00F5, 0, 0)
                    log("   clicked Demo Version in the Activation Wizard")
                    break
            time.sleep(1.0)
            continue
        sign = [h for c, s, h in forms if "Sign in" in s]
        if sign and attempts < MAX_ATTEMPTS:
            attempts += 1
            log("filling sign-in form (attempt %d)" % attempts)
            try:
                fill_and_submit(sign[0])
            except Exception as e:
                log("   fill failed: %s" % e)
            # give the app time to validate and react
            for _ in range(20):
                time.sleep(0.5)
                if dismiss_error_dialog(pid):
                    break
                forms2 = visible_windows(pid)
                if any("Sign in" not in s and "Demo Version" in s for c, s, h in forms2):
                    log("OK: signed in, main window is up")
                    return 0
            continue
        time.sleep(0.4)

    log("")
    log("  ===============================================================")
    log("   登录框还在：请在 Email 里填 zhang.san8888@gmail.com")
    log("   Password 里填 Efdc2026!  然后点 Sign In")
    log("   （勾上 Remember Password，下次就不用再输）")
    log("  ===============================================================")
    return 1


if __name__ == "__main__":
    sys.exit(main())
