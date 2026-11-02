import ctypes, ctypes.wintypes as wt, subprocess, os, time, sys

EXE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
OUT = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\dialogs.txt"

u32 = ctypes.WinDLL("user32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
E = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
BM_CLICK = 0x00F5


def cls(h):
    b = ctypes.create_unicode_buffer(256)
    u32.GetClassNameW(h, b, 256)
    return b.value


def txt(h):
    b = ctypes.create_unicode_buffer(2048)
    u32.GetWindowTextW(h, b, 2048)
    return b.value


proc = subprocess.Popen([EXE], cwd=os.path.dirname(EXE))
time.sleep(8)
logs = []
for rnd in range(8):
    found = []
    def cb(h, l):
        p = wt.DWORD(0)
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == proc.pid and cls(h) == "#32770":
            found.append(h)
        return True
    u32.EnumWindows(E(cb), 0)
    if not found:
        logs.append("round %d: no dialog (alive=%s)" % (rnd, proc.poll() is None))
        break
    for h in found:
        kids = []
        def cb2(ch, l):
            c, t = cls(ch), txt(ch)
            if t:
                kids.append("%s:%r" % (c, t))
            return True
        u32.EnumChildWindows(h, E(cb2), 0)
        logs.append("round %d dialog %#x -> %s" % (rnd, h, " | ".join(kids)))
        btns = []
        def cb3(ch, l):
            if cls(ch) == "Button":
                btns.append(ch)
            return True
        u32.EnumChildWindows(h, E(cb3), 0)
        if btns:
            u32.PostMessageW(btns[0], BM_CLICK, 0, 0)
    time.sleep(1.5)

logs.append("final alive=%s" % (proc.poll() is None))
open(OUT, "w", encoding="utf-8").write("\n".join(logs))
subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)], capture_output=True)
print("ok")
