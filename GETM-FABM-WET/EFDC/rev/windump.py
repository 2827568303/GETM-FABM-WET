import ctypes, ctypes.wintypes as wt, subprocess, os, time, sys

EXE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
OUT = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\win_dump.txt"

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
time.sleep(9)
lines = ["pid=%d alive=%s" % (proc.pid, proc.poll() is None)]

def dump():
    for h in []:
        pass
    rows = []

    def cb(h, l):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == proc.pid:
            r = RECT(); u32.GetWindowRect(h, ctypes.byref(r))
            rows.append("cls=%-22r title=%-36r vis=%d rect=(%d,%d %dx%d) parent=%#x hwnd=%#x" % (
                cls(h), txt(h), u32.IsWindowVisible(h), r.l, r.t, r.r - r.l, r.b - r.t, (u32.GetParent(h) or 0), (h or 0)))
        return True
    u32.EnumWindows(E(cb), 0)
    return rows


lines += dump()
# 读取所有 #32770 的子控件文本
dlgs=[]
def __cb(h,l):
    p=wt.DWORD(0); u32.GetWindowThreadProcessId(h,ctypes.byref(p))
    if p.value==proc.pid and cls(h)=="#32770": dlgs.append(h)
    return True
u32.EnumWindows(E(__cb),0)
for d in dlgs:
    kids=[]
    def __cb2(ch,l2):
        t2=txt(ch)
        if t2: kids.append("%s:%r"%(cls(ch),t2))
        return True
    u32.EnumChildWindows(d,E(__cb2),0)
    lines.append("DIALOG %#x -> %s" % (d, " | ".join(kids)))
lines.append("--- 3s later ---")
time.sleep(3)
lines += dump()

h = k32.OpenProcess(0x1000, False, proc.pid)
if h:
    code = wt.DWORD(0); k32.GetExitCodeProcess(h, ctypes.byref(code)); k32.CloseHandle(h)
    lines.append("exitcode=%d" % code.value)

open(OUT, "w", encoding="utf-8").write("\n".join(lines))
subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)], capture_output=True)
print("\n".join(lines))



