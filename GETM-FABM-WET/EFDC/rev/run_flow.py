import ctypes, ctypes.wintypes as wt, subprocess, sys, os, time
import frida

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
EXE = os.path.join(BASE, "EFDC 商业版8.4", "EFDC_Explorer8.4.exe")
REV = os.path.join(BASE, "rev")
dur = float(sys.argv[1]) if len(sys.argv) > 1 else 35.0

parts = [os.path.join(REV, "picfix2.js"), os.path.join(REV, "diag12.js")]
JS = "\n".join(open(p, encoding="utf-8").read() for p in parts)

u32 = ctypes.WinDLL("user32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.IsWindowVisible.argtypes = [wt.HWND]
u32.GetParent.argtypes = [wt.HWND]
u32.GetParent.restype = wt.HWND
ENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def cls(h):
    b = ctypes.create_unicode_buffer(256)
    u32.GetClassNameW(h, b, 256)
    return b.value


def text(h):
    b = ctypes.create_unicode_buffer(1024)
    u32.GetWindowTextW(h, b, 1024)
    return b.value


pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
session = frida.attach(pid)
script = session.create_script(JS)
script.on("message", lambda m, d: print("[js]", m.get("payload") or m.get("description"), flush=True))
script.load()
frida.resume(pid)
print("pid", pid, flush=True)

t0 = time.time()
seen = set()
while time.time() - t0 < dur:
    def cb(h, lp):
        p = wt.DWORD(0)
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value != pid or u32.GetParent(h) != 0:
            return True
        c, t = cls(h), text(h)
        k = (c, t, u32.IsWindowVisible(h))
        if k not in seen:
            seen.add(k)
            print("[%6.2f] WIN cls=%-22r title=%r vis=%s" % (time.time() - t0, c, t, u32.IsWindowVisible(h)), flush=True)
        return True
    u32.EnumWindows(ENUMPROC(cb), 0)
    time.sleep(0.4)

print("done alive check...", flush=True)
try:
    os.kill(pid, 9)
except Exception:
    pass
