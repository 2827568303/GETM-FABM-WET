import ctypes, ctypes.wintypes as wt, subprocess, sys, os, time
import frida

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
EXE = os.path.join(BASE, "EFDC 商业版8.4", "EFDC_Explorer8.4.exe")
PICFIX = os.path.join(BASE, "rev", "picfix2.js")

dur = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
JS = open(PICFIX, encoding="utf-8").read()

u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.IsWindowVisible.argtypes = [wt.HWND]
u32.GetParent.argtypes = [wt.HWND]
u32.GetParent.restype = wt.HWND
u32.SendMessageTimeoutW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM, wt.UINT, wt.UINT, ctypes.POINTER(ctypes.c_size_t)]
ENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
WM_GETTEXT = 0x000D
BM_CLICK = 0x00F5


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
clicked = set()
while time.time() - t0 < dur:
    def cb(h, lp):
        p = wt.DWORD(0)
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value != pid:
            return True
        c = cls(h)
        t = text(h)
        key = (h, c, t)
        if key not in seen:
            seen.add(key)
            print("[%6.2f] WIN cls=%-24r title=%r vis=%s hwnd=%#x" % (time.time() - t0, c, t, u32.IsWindowVisible(h), h), flush=True)
        if c == "#32770" and h not in clicked:
            clicked.add(h)
            found = []

            def cb2(ch, l2):
                if cls(ch) in ("Button", "Static"):
                    found.append((cls(ch), text(ch), ch))
                return True
            u32.EnumChildWindows(h, ENUMPROC(cb2), 0)
            btn = None
            for cname, tname, ch in found:
                if cname == "Button":
                    btn = ch
            msg = " / ".join(f"{cname}:{tname!r}" for cname, tname, _ in found)
            print("      DIALOG children:", msg, flush=True)
            if btn:
                u32.PostMessageW(btn, BM_CLICK, 0, 0)
                print("      -> clicked OK on", hex(h), flush=True)
        return True
    u32.EnumWindows(ENUMPROC(cb), 0)
    if not k32.GetProcessId and False:
        pass
    time.sleep(0.35)

print("done", flush=True)
try:
    os.kill(pid, 9)
except Exception:
    pass
