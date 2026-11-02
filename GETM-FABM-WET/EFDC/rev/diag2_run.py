import ctypes, ctypes.wintypes as wt, time, os, sys
import frida

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
EXE = os.path.join(BASE, "EFDC 商业版8.4", "EFDC_Explorer8.4.exe")
REV = os.path.join(BASE, "rev")

js_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REV, "diag2.js")
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0
JS = open(js_file, encoding="utf-8").read()

u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetClassNameW.restype = ctypes.c_int
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.restype = ctypes.c_int
u32.IsWindowVisible.argtypes = [wt.HWND]
u32.GetParent.argtypes = [wt.HWND]
u32.GetParent.restype = wt.HWND
u32.GetWindowLongW.argtypes = [wt.HWND, ctypes.c_int]
ENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
WM_NULL = 0
SMTO_ABORTIFHUNG = 0x0002


def cls_of(h):
    b = ctypes.create_unicode_buffer(256)
    u32.GetClassNameW(h, b, 256)
    return b.value


def title_of(h):
    b = ctypes.create_unicode_buffer(512)
    u32.GetWindowTextW(h, b, 512)
    return b.value


def responsive(h):
    r = ctypes.c_size_t(0)
    ok = u32.SendMessageTimeoutW(h, WM_NULL, 0, 0, SMTO_ABORTIFHUNG, 200, ctypes.byref(r))
    return bool(ok)


pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
session = frida.attach(pid)
script = session.create_script(JS)


def on_message(msg, data):
    if msg.get("type") == "send":
        print("[js]", msg.get("payload"), flush=True)
    elif msg.get("type") == "error":
        print("[js-err]", msg.get("description"), flush=True)


script.on("message", on_message)
script.load()
frida.resume(pid)
proc = None
for _ in range(40):
    try:
        proc = ctypes.WinDLL("kernel32").OpenProcess(0x0400, False, pid)
        break
    except Exception:
        time.sleep(0.05)

print("pid", pid, flush=True)

t0 = time.time()
seen = {}
last_cpu = None
last_cpu_t = None
while time.time() - t0 < dur:
    cur = set()

    def cb(h, lp):
        p = wt.DWORD(0)
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value != pid:
            return True
        if u32.GetParent(h) != 0:
            return True
        c = cls_of(h)
        if not c:
            return True
        t = title_of(h)
        key = (h, c, t, u32.IsWindowVisible(h))
        cur.add(key)
        if key not in seen:
            seen[key] = time.time() - t0
            print(f"[{time.time()-t0:6.2f}] WIN cls={c!r} title={t!r} vis={u32.IsWindowVisible(h)} resp={responsive(h)} hwnd={h:#x}", flush=True)
        return True

    u32.EnumWindows(ENUMPROC(cb), 0)
    gone = [k for k in seen if k not in cur and isinstance(k, tuple)]
    for k in gone:
        print(f"[{time.time()-t0:6.2f}] GONE cls={k[1]!r} title={k[2]!r} hwnd={k[0]:#x}", flush=True)
        del seen[k]
    # CPU time of the process
    if proc:
        code = ctypes.wintypes.DWORD()
        ct, et, kt, ut = (ctypes.wintypes.FILETIME() for _ in range(4))
        if ctypes.windll.kernel32.GetProcessTimes(proc, ctypes.byref(ct), ctypes.byref(et), ctypes.byref(kt), ctypes.byref(ut)):
            cpu = (kt.dwHighDateTime << 32 | kt.dwLowDateTime) + (ut.dwHighDateTime << 32 | ut.dwLowDateTime)
            now = time.time()
            if last_cpu is not None and last_cpu_t is not None:
                pct = (cpu - last_cpu) / 1e7 / (now - last_cpu_t) * 100
                print(f"[{now-t0:6.2f}] CPU {pct:5.1f}%", flush=True)
            last_cpu, last_cpu_t = cpu, now
    time.sleep(1.0)

print("done; leaving process alive", flush=True)
