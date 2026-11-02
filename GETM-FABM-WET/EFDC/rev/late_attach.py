import ctypes, ctypes.wintypes as wt, subprocess, os, time
import frida

EXE = r"C:\EFDC84_RUN\EFDC_Explorer8.4.exe"
REV = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev"

u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
E = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def cls(h):
    b = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, b, 256); return b.value


def txt(h):
    b = ctypes.create_unicode_buffer(512); u32.GetWindowTextW(h, b, 512); return b.value


proc = subprocess.Popen([EXE], cwd=os.path.dirname(EXE))
pid = proc.pid
print("pid", pid, flush=True)
time.sleep(3.0)

JS = open(os.path.join(REV, "diag38.js"), encoding="utf-8").read()
try:
    sess = frida.attach(pid)
    sc = sess.create_script(JS)
    sc.on("message", lambda m, d: print("[js]", m.get("payload") or m.get("description"), flush=True))
    sc.load()
    print("frida attached at 3s", flush=True)
except Exception as e:
    print("attach failed:", e, flush=True)

t0 = time.time()
seen = set()
while time.time() - t0 < 20:
    def cb(h, l):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            c = cls(h)
            k = (c, txt(h), u32.IsWindowVisible(h))
            if c.startswith("ThunderRT6Form") and k not in seen:
                seen.add(k)
                print("[%5.2f] WIN cls=%s title=%r vis=%d" % (time.time() - t0, c, k[1], k[2]), flush=True)
        return True
    u32.EnumWindows(E(cb), 0)
    h2 = k32.OpenProcess(0x1000, False, pid)
    if h2:
        code = wt.DWORD(0); k32.GetExitCodeProcess(h2, ctypes.byref(code)); k32.CloseHandle(h2)
        if code.value != 259:
            print("[%5.2f] EXITED code=%d" % (time.time() - t0, code.value), flush=True)
            break
    time.sleep(0.15)

if proc.poll() is None:
    subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
