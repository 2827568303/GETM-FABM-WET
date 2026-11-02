import ctypes, ctypes.wintypes as wt, os, sys, time
import frida
from PIL import ImageGrab

EXE = r"C:\EFDC84_RUN\EFDC_Explorer8.4.exe"
REV = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev"
OUT = os.path.join(REV, "app_shot.png")

u32 = ctypes.WinDLL("user32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.IsWindowVisible.argtypes = [wt.HWND]
u32.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
u32.SetForegroundWindow.argtypes = [wt.HWND]
E = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def cls(h):
    b = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, b, 256); return b.value


def txt(h):
    b = ctypes.create_unicode_buffer(512); u32.GetWindowTextW(h, b, 512); return b.value


JS = open(os.path.join(REV, "diag39.js"), encoding="utf-8").read()
pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
sess = frida.attach(pid)
sc = sess.create_script(JS)
sc.on("message", lambda m, d: print("[js]", m.get("payload") or m.get("description"), flush=True))
sc.load()
frida.resume(pid)
print("pid", pid, flush=True)

time.sleep(12)

target = None

def cb(h, l):
    global target
    p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
    if p.value == pid and cls(h).startswith("ThunderRT6Form"):
        r = wt.RECT(); u32.GetWindowRect(h, ctypes.byref(r))
        print("WIN %s %r vis=%d rect=(%d,%d %dx%d)" % (cls(h), txt(h), u32.IsWindowVisible(h), r.left, r.top, r.right - r.left, r.bottom - r.top), flush=True)
        if u32.IsWindowVisible(h) and target is None:
            target = (h, r)
    return True
u32.EnumWindows(E(cb), 0)

if target:
    h, r = target
    u32.SetForegroundWindow(h)
    time.sleep(1.0)
    box = (r.left, r.top, r.right, r.bottom)
    img = ImageGrab.grab(bbox=box)
    img.save(OUT)
    print("saved", OUT, img.size, flush=True)
else:
    print("no visible form window", flush=True)

try:
    os.kill(pid, 9)
except Exception:
    pass
