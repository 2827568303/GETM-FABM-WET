import ctypes, ctypes.wintypes as wt, os, sys, time
import frida

EXE = sys.argv[3] if len(sys.argv) > 3 else r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
REV = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev"
JS_FILE = sys.argv[1] if len(sys.argv) > 1 else "diag51.js"
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0

u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.IsWindowVisible.argtypes = [wt.HWND]
E = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def cls(h):
    b = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, b, 256); return b.value


def txt(h):
    b = ctypes.create_unicode_buffer(512); u32.GetWindowTextW(h, b, 512); return b.value


JS = open(os.path.join(REV, JS_FILE), encoding="utf-8").read()
pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
sess = frida.attach(pid)
sc = sess.create_script(JS)
sc.on("message", lambda m, d: print("[js]", m.get("payload") or m.get("description"), flush=True))
sc.load()
frida.resume(pid)
print("pid", pid, flush=True)

t0 = time.time()
seen = set()
while time.time() - t0 < DUR:
    def cb(h, l):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            k = (cls(h), txt(h), u32.IsWindowVisible(h))
            if k not in seen:
                seen.add(k)
                print("[%5.2f] WIN %-22s %-30r vis=%d" % (time.time() - t0, k[0], k[1], k[2]), flush=True)
        return True
    u32.EnumWindows(E(cb), 0)
    h2 = k32.OpenProcess(0x1000, False, pid)
    if h2:
        code = wt.DWORD(0); k32.GetExitCodeProcess(h2, ctypes.byref(code)); k32.CloseHandle(h2)
        if code.value != 259:
            print("[%5.2f] EXITED code=%d" % (time.time() - t0, code.value), flush=True)
            break
    time.sleep(0.2)
print("done", flush=True)
try:
    os.kill(pid, 9)
except Exception:
    pass

