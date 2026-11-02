import ctypes, ctypes.wintypes as wt, subprocess, sys, time, os

EXE = None
for root, dirs, files in os.walk(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"):
    if "EFDC_Explorer8.4.exe" in files and "_orig" not in root:
        EXE = os.path.join(root, "EFDC_Explorer8.4.exe")
        break
if EXE is None:
    raise SystemExit("exe not found")

dur = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
u32 = ctypes.WinDLL("user32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.IsWindowVisible.argtypes = [wt.HWND]
u32.GetParent.argtypes = [wt.HWND]
u32.GetParent.restype = wt.HWND
ENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

proc = subprocess.Popen([EXE], cwd=os.path.dirname(EXE))
pid = proc.pid
print("pid", pid, "exe", EXE, flush=True)

t0 = time.time()
seen = set()
while time.time() - t0 < dur:
    def cb(h, lp):
        p = wt.DWORD(0)
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid and u32.GetParent(h) == 0:
            c = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, c, 256)
            t = ctypes.create_unicode_buffer(512); u32.GetWindowTextW(h, t, 512)
            key = (c.value, t.value, u32.IsWindowVisible(h))
            if key not in seen:
                seen.add(key)
                print("[%6.2f] WIN cls=%r title=%r vis=%s hwnd=%#x" % (time.time() - t0, c.value, t.value, u32.IsWindowVisible(h), h), flush=True)
        return True
    u32.EnumWindows(ENUMPROC(cb), 0)
    if proc.poll() is not None:
        print("[%6.2f] process exited code=%s" % (time.time() - t0, proc.returncode), flush=True)
        break
    time.sleep(0.4)

print("alive=", proc.poll() is None, flush=True)
if proc.poll() is None:
    try:
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
    except Exception:
        pass
