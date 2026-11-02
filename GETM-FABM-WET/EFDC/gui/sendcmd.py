# -*- coding: utf-8 -*-
"""Post WM_COMMAND ids to the EFDC main form and report what each one does.

python -X utf8 gui/sendcmd.py <id0> <id1> [--lparam N]
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

ID0 = int(sys.argv[1])
ID1 = int(sys.argv[2])
LPARAM = 0
if "--lparam" in sys.argv:
    LPARAM = int(sys.argv[sys.argv.index("--lparam") + 1], 0)


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
            if cls(k) in ("Button", "ThunderRT6CommandButton") and t in ("确定", "取消", "Cancel", "Close", "OK"):
                r = rect(k)
                tg.click_screen((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
                return txt(h)
    return None


def main():
    form = [h for h in tops() if "EFDC_Explorer8.4 Demo" in txt(h) and u.IsWindowVisible(h)][0]
    for cid in range(ID0, ID1 + 1):
        u.PostMessageW(form, 0x0111, cid, LPARAM)
        time.sleep(0.55)
        opened = [txt(h) for h in tops()
                  if h != form and u.IsWindowVisible(h) and cls(h) in ("#32770", "ThunderRT6FormDC")]
        print("id=%-3d %s" % (cid, opened[:2]), flush=True)
        d = dismiss()
        if d:
            print("     dismissed %r" % d, flush=True)
            time.sleep(0.3)
    return 0


if __name__ == "__main__":
    sys.exit(main())
