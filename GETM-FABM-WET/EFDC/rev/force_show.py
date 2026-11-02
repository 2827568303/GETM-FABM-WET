import ctypes, ctypes.wintypes as wt, subprocess, os, sys, time

EXE = r"C:\EFDC84_RUN\EFDC_Explorer8.4.exe"
u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.IsWindowVisible.argtypes = [wt.HWND]
u32.ShowWindow.argtypes = [wt.HWND, ctypes.c_int]
u32.SetForegroundWindow.argtypes = [wt.HWND]
E = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def cls(h):
    b = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, b, 256); return b.value


def txt(h):
    b = ctypes.create_unicode_buffer(512); u32.GetWindowTextW(h, b, 512); return b.value


proc = subprocess.Popen([EXE], cwd=os.path.dirname(EXE))
t0 = time.time()
shown = set()
while time.time() - t0 < 25:
    targets = []

    def cb(h, l):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == proc.pid and cls(h).startswith("ThunderRT6Form") and txt(h):
            targets.append(h)
        return True
    u32.EnumWindows(E(cb), 0)

    for h in targets:
        if h in shown:
            continue
        shown.add(h)
        u32.SetWindowLongW.argtypes=[wt.HWND,ctypes.c_int,ctypes.c_long]\n        u32.SetWindowLongW.restype=ctypes.c_long\n        st=u32.SetWindowLongW(h,-16,0)\n        u32.SetWindowLongW(h,-16,(st|0x10000000)&0xFFFFFFFF)\n        r = u32.ShowWindow(h, 5)
        u32.SetForegroundWindow(h)
        print("[%5.2f] ShowWindow(%#x, SW_SHOW) prev=%d vis_now=%d title=%r" % (time.time() - t0, h, r, u32.IsWindowVisible(h), txt(h)), flush=True)

    h2 = k32.OpenProcess(0x1000, False, proc.pid)
    if h2:
        code = wt.DWORD(0); k32.GetExitCodeProcess(h2, ctypes.byref(code)); k32.CloseHandle(h2)
        if code.value != 259:
            print("[%5.2f] EXITED code=%d" % (time.time() - t0, code.value), flush=True)
            break
    time.sleep(0.1)

print("alive=%s" % (proc.poll() is None))
if proc.poll() is None:
    subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)], capture_output=True)

