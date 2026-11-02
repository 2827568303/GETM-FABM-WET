# -*- coding: utf-8 -*-
"""Enumerate MSAA children of the EFDC toolbar (button names/tooltips -> find Save).

python -X utf8 gui/msaa_toolbar.py
"""
import ctypes
import ctypes.wintypes as wt

import comtypes
import comtypes.client
from comtypes import GUID, IUnknown
from comtypes.automation import IDispatch

u = ctypes.WinDLL("user32", use_last_error=True)
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

oleacc = ctypes.WinDLL("oleacc")
IID_IAccessible = GUID("{618736E0-3C3D-11CF-810C-00AA00389B71}")


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


def acc_from_window(h):
    p = ctypes.c_void_p()
    hr = oleacc.AccessibleObjectFromWindow(wt.HWND(h), 0xFFFFFFFC,  # OBJID_CLIENT
                                           ctypes.byref(IID_IAccessible), ctypes.byref(p))
    if hr != 0 or not p:
        return None
    return ctypes.cast(p, ctypes.POINTER(IDispatch))


def children(acc):
    """IAccessible::get_accChildCount + accParent walking via IDispatch is awkward;
    use IDispatch::Invoke for accChildCount and accChild(vt=VT_VARIANT)."""
    return []


def main():
    form = [h for h in tops() if "EFDC_Explorer8.4 Demo" in txt(h) and u.IsWindowVisible(h)][0]
    l, t, _, _ = rect(form)
    bars = []
    for k in kids(form):
        kr = rect(k)
        if kr[2] - kr[0] > 600 and 10 <= kr[1] - t <= 90 and kr[3] - kr[1] < 100:
            bars.append((k, cls(k), kr))
    for k, c, kr in bars:
        print("bar", hex(k), c, kr)
        acc = acc_from_window(k)
        print("   IAccessible:", acc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
