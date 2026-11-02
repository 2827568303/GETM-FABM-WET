import ctypes, ctypes.wintypes as wt, subprocess, os, time

EXE = r"C:\EFDC84_RUN\EFDC_Explorer8.4.exe"
u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.IsWindowVisible.argtypes = [wt.HWND]
u32.ShowWindow.argtypes = [wt.HWND, ctypes.c_int]
u32.SetWindowLongW.argtypes = [wt.HWND, ctypes.c_int, ctypes.c_long]
u32.SetWindowLongW.restype = ctypes.c_long
E = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def cls(h):
    b = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, b, 256); return b.value


def txt(h):
    b = ctypes.create_unicode_buffer(512); u32.GetWindowTextW(h, b, 512); return b.value


proc = subprocess.Popen([EXE], cwd=os.path.dirname(EXE))
pid = proc.pid
t0 = time.time()
time.sleep(1.5)

found = []

def cb(h, l):
    p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
    if p.value == pid and cls(h).startswith("ThunderRT6Form"):
        found.append(h)
    return True
u32.EnumWindows(E(cb), 0)

print("[%5.2f] found=%s" % (time.time() - t0, [(hex(h), cls(h), txt(h)) for h in found]), flush=True)
for h in found:
    st = u32.SetWindowLongW(h, -16, 0)
    u32.SetWindowLongW(h, -16, (st | 0x10000000) & 0xFFFFFFFF)
    r = u32.ShowWindow(h, 5)
    print("  ShowWindow(%#x) prev=%d vis=%d" % (h, r, u32.IsWindowVisible(h)), flush=True)

while time.time() - t0 < 20:
    h2 = k32.OpenProcess(0x1000, False, pid)
    if h2:
        code = wt.DWORD(0); k32.GetExitCodeProcess(h2, ctypes.byref(code)); k32.CloseHandle(h2)
        if code.value != 259:
            print("[%5.2f] EXITED code=%d" % (time.time() - t0, code.value), flush=True)
            break
    st = [(hex(h), u32.IsWindowVisible(h)) for h in found if u32.IsWindow(h)]
    time.sleep(1.0)

print("alive=%s" % (proc.poll() is None), flush=True)
if proc.poll() is None:
    subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
