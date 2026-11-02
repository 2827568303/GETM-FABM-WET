# -*- coding: utf-8 -*-
"""Launch the app, list the Activation Wizard's child controls, click a button by caption,
then capture the main window. Proves whether the wizard is the only blocker.

python -X utf8 gui/click_wiz.py <exe> <caption-substring> [seconds]
"""
import ctypes, ctypes.wintypes as wt, os, subprocess, sys, time
from win_shot import capture

u32 = ctypes.WinDLL("user32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
CB = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

exe = sys.argv[1]
want = sys.argv[2] if len(sys.argv) > 2 else "Demo"
dur = float(sys.argv[3]) if len(sys.argv) > 3 else 12.0
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(outdir, exist_ok=True)


def cls(h):
    b = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, b, 256); return b.value


def txt(h):
    b = ctypes.create_unicode_buffer(512); u32.GetWindowTextW(h, b, 512); return b.value


def rect(h):
    r = wt.RECT(); u32.GetWindowRect(h, ctypes.byref(r)); return (r.left, r.top, r.right, r.bottom)


def tops(pid):
    out = []
    def cb(h, l):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            out.append(h)
        return True
    u32.EnumWindows(CB(cb), 0)
    return out


def children(h):
    out = []
    def cb(c, l):
        out.append(c)
        return True
    u32.EnumChildWindows(h, CB(cb), 0)
    return out


p = subprocess.Popen([exe], cwd=os.path.dirname(exe), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pid = p.pid
print("pid=%d" % pid, flush=True)
t0 = time.time()
clicked = False
while time.time() - t0 < dur:
    t = time.time() - t0
    for h in tops(pid):
        title = txt(h)
        if "Activation Wizard" in title and not clicked:
            print("[%5.2f] wizard hwnd=0x%X rect=%s" % (t, h, rect(h)), flush=True)
            kids = children(h)
            for c in kids:
                ct, cc = txt(c), cls(c)
                if cc in ("ThunderRT6CommandButton", "Button") and ct:
                    print("    btn 0x%X %-20r %s" % (c, ct, rect(c)), flush=True)
            for c in kids:
                ct, cc = txt(c), cls(c)
                if cc in ("ThunderRT6CommandButton", "Button") and want.lower() in ct.lower():
                    print("[%5.2f] clicking %r" % (t, ct), flush=True)
                    u32.SendMessageW(c, 0x00F5, 0, 0)  # BM_CLICK
                    clicked = True
                    break
        if u32.IsWindowVisible(h) and rect(h)[2] > rect(h)[0]:
            try:
                sz = capture(h, os.path.join(outdir, "click_%03d_%s.png" % (int(t * 10), cls(h).replace(' ', ''))))
                if sz and clicked:
                    print("[%5.2f] shot %s %r %s" % (t, cls(h), title[:26], sz), flush=True)
            except Exception as e:
                pass
    if p.poll() is not None:
        print("[%5.2f] EXITED code=%s" % (t, p.returncode), flush=True)
        break
    time.sleep(0.3)
if p.poll() is None:
    print("alive at end", flush=True)
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
