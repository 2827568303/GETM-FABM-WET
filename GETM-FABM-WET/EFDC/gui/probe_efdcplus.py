import os, subprocess, time, ctypes, ctypes.wintypes as wt
exe = r'C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EEMS125\EFDC+Explorer.exe'
p = subprocess.Popen([exe], cwd=os.path.dirname(exe))
time.sleep(7)
print('exit code:', p.poll())
u = ctypes.WinDLL('user32')
u.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
E = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def cb(h, l):
    pid = wt.DWORD(0); u.GetWindowThreadProcessId(h, ctypes.byref(pid))
    if pid.value == p.pid:
        n = ctypes.create_unicode_buffer(300); u.GetWindowTextW(h, n, 300)
        c = ctypes.create_unicode_buffer(120); u.GetClassNameW(h, c, 120)
        print('WIN', c.value, repr(n.value), bool(u.IsWindowVisible(h)))
    return True
u.EnumWindows(E(cb), 0)
if p.poll() is None:
    print('still running')
    subprocess.run(['taskkill', '/PID', str(p.pid), '/T', '/F'], capture_output=True)
