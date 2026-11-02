import ctypes, ctypes.wintypes as wt, subprocess, sys, os, time
import frida

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
EXE = os.path.join(BASE, "EFDC 商业版8.4", "EFDC_Explorer8.4.exe")
REV = os.path.join(BASE, "rev")
dur = float(sys.argv[1]) if len(sys.argv) > 1 else 40.0
scripts = sys.argv[2:] if len(sys.argv) > 2 else ["diag22.js"]
JS = "\n".join(open(os.path.join(REV, s), encoding="utf-8").read() for s in scripts)

u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.IsWindowVisible.argtypes = [wt.HWND]
u32.GetParent.argtypes = [wt.HWND]
u32.GetParent.restype = wt.HWND
E = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def cls(h):
    b = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, b, 256); return b.value


def txt(h):
    b = ctypes.create_unicode_buffer(1024); u32.GetWindowTextW(h, b, 1024); return b.value


pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
sess = frida.attach(pid)
sc = sess.create_script(JS)
sc.on("message", lambda m, d: print("[js]", m.get("payload") or m.get("description"), flush=True))
sc.load()
frida.resume(pid)
print("pid", pid, flush=True)

t0 = time.time(); seen = set(); exited = None
while time.time() - t0 < dur:
    def cb(h, l):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid and u32.GetParent(h) == 0:
            k = (cls(h), txt(h), u32.IsWindowVisible(h))
            if k not in seen:
                seen.add(k)
                print("[%6.2f] WIN cls=%-20r title=%-42r vis=%s" % (time.time() - t0, k[0], k[1], k[2]), flush=True)
        return True
    u32.EnumWindows(E(cb), 0)
    h = k32.OpenProcess(0x1000, False, pid)
    if h:
        code = wt.DWORD(0)
        k32.GetExitCodeProcess(h, ctypes.byref(code))
        k32.CloseHandle(h)
        if code.value != 259:
            exited = time.time() - t0
            print('PROCESS EXITED code=%d at %.1fs' % (code.value, exited), flush=True)
            break
    time.sleep(0.4)

print("elapsed=%.1f" % (time.time() - t0), flush=True)
try:
    os.kill(pid, 9)
except Exception:
    pass

