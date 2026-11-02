import ctypes, ctypes.wintypes as wt, subprocess, os, sys, time

EXE = sys.argv[1] if len(sys.argv) > 1 else r"C:\EFDC84_RUN\EFDC_Explorer8.4.exe"
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 45.0

u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetParent.argtypes = [wt.HWND]
u32.GetParent.restype = wt.HWND
E = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


class RECT(ctypes.Structure):
    _fields_ = [("l", ctypes.c_long), ("t", ctypes.c_long), ("r", ctypes.c_long), ("b", ctypes.c_long)]


u32.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(RECT)]


def cls(h):
    b = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, b, 256); return b.value


def txt(h):
    b = ctypes.create_unicode_buffer(1024); u32.GetWindowTextW(h, b, 1024); return b.value


proc = subprocess.Popen([EXE], cwd=os.path.dirname(EXE))
t0 = time.time()
print("pid=%d exe=%s" % (proc.pid, EXE), flush=True)
seen = {}

while time.time() - t0 < DUR:
    cur = {}

    def cb(h, l):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == proc.pid:
            r = RECT(); u32.GetWindowRect(h, ctypes.byref(r))
            key = (cls(h), txt(h))
            cur[key] = (u32.IsWindowVisible(h), r.l, r.t, r.r - r.l, r.b - r.t, h)
        return True
    u32.EnumWindows(E(cb), 0)

    for k, v in cur.items():
        if k not in seen:
            seen[k] = v
            print("[%5.2f] NEW  cls=%-20r title=%-30r vis=%d rect=(%d,%d %dx%d) hwnd=%#x" % (time.time() - t0, k[0], k[1], v[0], v[1], v[2], v[3], v[4], v[5]), flush=True)
        elif seen[k][0] != v[0] or seen[k][3:5] != v[3:5]:
            print("[%5.2f] CHG  cls=%-20r title=%-30r vis=%d rect=(%d,%d %dx%d)" % (time.time() - t0, k[0], k[1], v[0], v[1], v[2], v[3], v[4]), flush=True)
            seen[k] = v

    h = k32.OpenProcess(0x1000, False, proc.pid)
    if h:
        code = wt.DWORD(0); k32.GetExitCodeProcess(h, ctypes.byref(code)); k32.CloseHandle(h)
        if code.value != 259:
            print("[%5.2f] EXITED code=%d" % (time.time() - t0, code.value), flush=True)
            break
    time.sleep(0.25)

alive = proc.poll() is None
print("done alive=%s" % alive, flush=True)
if alive:
    subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)], capture_output=True)
