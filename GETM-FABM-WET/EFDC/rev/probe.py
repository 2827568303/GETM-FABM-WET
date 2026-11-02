import ctypes, ctypes.wintypes as wt, time, sys, os, struct
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
k32 = ctypes.WinDLL('kernel32', use_last_error=True)
u32 = ctypes.WinDLL('user32', use_last_error=True)

class STARTUPINFOA(ctypes.Structure):
    _fields_ = [('cb', wt.DWORD), ('lpReserved', wt.LPSTR), ('lpDesktop', wt.LPSTR),
                ('lpTitle', wt.LPSTR), ('dwX', wt.DWORD), ('dwY', wt.DWORD),
                ('dwXSize', wt.DWORD), ('dwYSize', wt.DWORD), ('dwXCountChars', wt.DWORD),
                ('dwYCountChars', wt.DWORD), ('dwFillAttribute', wt.DWORD), ('dwFlags', wt.DWORD),
                ('wShowWindow', wt.WORD), ('cbReserved2', wt.WORD), ('lpReserved2', ctypes.c_void_p),
                ('hStdInput', wt.HANDLE), ('hStdOutput', wt.HANDLE), ('hStdError', wt.HANDLE)]

class PI(ctypes.Structure):
    _fields_ = [('hProcess', wt.HANDLE), ('hThread', wt.HANDLE), ('pid', wt.DWORD), ('tid', wt.DWORD)]

WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
AUTOCLOSE = ('--noclose' not in sys.argv)
BM_CLICK = 0x00F5
WM_COMMAND = 0x0111
IDOK = 1

def text(h):
    n = u32.GetWindowTextLengthW(h)
    b = ctypes.create_unicode_buffer(n + 2)
    u32.GetWindowTextW(h, b, n + 2)
    return b.value

def cls(h):
    b = ctypes.create_unicode_buffer(256)
    u32.GetClassNameW(h, b, 256)
    return b.value

def collect(pid):
    found = []
    def cb(h, lp):
        p = wt.DWORD(0)
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            kids = []
            def cb2(h2, lp2):
                t = text(h2)
                if t:
                    kids.append((cls(h2), t))
                return True
            u32.EnumChildWindows(h, WNDENUMPROC(cb2), 0)
            found.append((h, cls(h), text(h), kids))
        return True
    u32.EnumWindows(WNDENUMPROC(cb), 0)
    return found

exe = sys.argv[1]
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0
os.chdir(os.path.dirname(exe))
si = STARTUPINFOA(); si.cb = ctypes.sizeof(si)
pi = PI()
if not k32.CreateProcessW(None, ctypes.c_wchar_p(f'"{exe}"'), None, None, False, 0, None, None,
                          ctypes.byref(si), ctypes.byref(pi)):
    print('CreateProcess failed', ctypes.get_last_error()); sys.exit(1)
print('pid', pi.pid)
t0 = time.time()
seen = {}
alive = True
while time.time() - t0 < dur:
    w = collect(pi.pid)
    for h, c, t, kids in w:
        key = (c, t, tuple(kids))
        if key not in seen:
            seen[key] = time.time() - t0
            print(f'[{time.time()-t0:6.2f}] win={h} class={c!r} title={t!r}')
            for kc, kt in kids:
                print(f'          child {kc!r}: {kt!r}')
            if AUTOCLOSE:
                def cb3(h2, lp2):
                    c = ctypes.create_unicode_buffer(64)
                    u32.GetClassNameW(h2, c, 64)
                    if c.value == 'Button':
                        u32.PostMessageW(h2, BM_CLICK, 0, 0)
                    return True
                u32.EnumChildWindows(h, WNDENUMPROC(cb3), 0)
                print(f'          -> clicked OK (auto-dismiss)')
    ec = wt.DWORD(0)
    if k32.GetExitCodeProcess(ctypes.c_void_p(pi.hProcess), ctypes.byref(ec)) and ec.value != 259:
        print(f'[{time.time()-t0:6.2f}] process exited code={ec.value:#x}')
        alive = False
        break
    time.sleep(0.4)
if alive:
    print(f'[{time.time()-t0:6.2f}] still running -> terminating')
    k32.TerminateProcess(ctypes.c_void_p(pi.hProcess), 0)
