# -*- coding: utf-8 -*-
"""SendInput helpers: real mouse click + unicode typing (so VB6 fires Change events)."""
import ctypes
import ctypes.wintypes as wt
import time

u = ctypes.WinDLL("user32", use_last_error=True)

# The EFDC forms are often created minimized / off-screen; without DPI awareness the
# coordinates reported by GetWindowRect do not match physical pixels, so every click
# lands somewhere else. Declare awareness before any window is created.
try:
    u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

u.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
u.mouse_event.argtypes = [wt.DWORD, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_void_p]
u.SetForegroundWindow.argtypes = [wt.HWND]
u.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wt.WORD), ("wScan", wt.WORD), ("dwFlags", wt.DWORD),
                ("time", wt.DWORD), ("dwExtraInfo", ctypes.c_void_p)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", wt.DWORD),
                ("dwFlags", wt.DWORD), ("time", wt.DWORD), ("dwExtraInfo", ctypes.c_void_p)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wt.DWORD), ("wParamL", wt.WORD), ("wParamH", wt.WORD)]


class _INPUTunion(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wt.DWORD), ("u", _INPUTunion)]


u.SendInput.argtypes = [wt.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
u.SendInput.restype = wt.UINT

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
INPUT_KEYBOARD = 1
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


def rect(h):
    r = wt.RECT()
    u.GetWindowRect(h, ctypes.byref(r))
    return (r.left, r.top, r.right, r.bottom)


def click_screen(x, y):
    u.SetCursorPos(int(x), int(y))
    time.sleep(0.05)
    u.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, None)
    u.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, None)
    time.sleep(0.08)


def click_window(h, fx=0.5, fy=0.5):
    l, t, r, b = rect(h)
    click_screen(l + (r - l) * fx, t + (b - t) * fy)


def focus(h):
    """Reliably bring a window to the foreground (Windows blocks plain SetForegroundWindow)."""
    try:
        u.ShowWindow(h, 9)  # SW_RESTORE
        # VB6 commonly creates forms minimized at (-48000,-48000); move it on-screen first.
        # HWND_TOPMOST keeps it above leftover EFDC windows from earlier runs.
        u.SetWindowPos(h, -1, 120, 120, 0, 0, 0x0001 | 0x0040)  # TOPMOST | NOSIZE | SHOWWINDOW
        try:
            u.SwitchToThisWindow(h, True)
        except Exception:
            pass
        if u.GetForegroundWindow() != h:
            fg = u.GetForegroundWindow()
            tid_fg = u.GetWindowThreadProcessId(fg, None) if fg else 0
            tid_us = ctypes.windll.kernel32.GetCurrentThreadId()
            if tid_fg:
                u.AttachThreadInput(tid_us, tid_fg, True)
            u.BringWindowToTop(h)
            u.SetForegroundWindow(h)
            if tid_fg:
                u.AttachThreadInput(tid_us, tid_fg, False)
    except Exception:
        pass
    time.sleep(0.3)


def is_foreground(h):
    return u.GetForegroundWindow() == h


class GUITHREADINFO(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("flags", wt.DWORD), ("hwndActive", wt.HWND),
                ("hwndFocus", wt.HWND), ("hwndCapture", wt.HWND), ("hwndMenuOwner", wt.HWND),
                ("hwndMoveSize", wt.HWND), ("hwndCaret", wt.HWND), ("rcCaret", wt.RECT)]


def focused_window(hwnd_any):
    """Which control of that window's thread currently has keyboard focus."""
    tid = u.GetWindowThreadProcessId(hwnd_any, None)
    gti = GUITHREADINFO()
    gti.cbSize = ctypes.sizeof(GUITHREADINFO)
    if u.GetGUIThreadInfo(tid, ctypes.byref(gti)):
        return gti.hwndFocus
    return None


def click_and_focus(h_form, control, tries=4):
    """Click a control until it really owns the keyboard focus. Returns True on success."""
    tg_focus = focus
    for i in range(tries):
        tg_focus(h_form)
        click_window(control)
        time.sleep(0.15)
        if focused_window(h_form) == control:
            return True
        time.sleep(0.2)
    return False


def type_unicode(text, delay=0.02):
    for ch in text:
        code = ord(ch)
        for flags in (KEYEVENTF_UNICODE, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP):
            inp = INPUT(type=INPUT_KEYBOARD)
            inp.u.ki = KEYBDINPUT(wVk=0, wScan=code, dwFlags=flags, time=0, dwExtraInfo=None)
            u.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
            time.sleep(delay)
        time.sleep(delay)


def press(vk):
    for flags in (0, KEYEVENTF_KEYUP):
        inp = INPUT(type=INPUT_KEYBOARD)
        inp.u.ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=None)
        u.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        time.sleep(0.02)


def key_down(vk):
    inp = INPUT(type=INPUT_KEYBOARD)
    inp.u.ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=0, time=0, dwExtraInfo=None)
    u.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    time.sleep(0.02)


def key_up(vk):
    inp = INPUT(type=INPUT_KEYBOARD)
    inp.u.ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=None)
    u.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    time.sleep(0.02)


def select_all():
    key_down(0x11)      # Ctrl
    press(0x41)         # A
    key_up(0x11)


def backspace(n=1):
    for _ in range(n):
        press(0x08)


