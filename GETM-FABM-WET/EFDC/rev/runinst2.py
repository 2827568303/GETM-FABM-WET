import ctypes, ctypes.wintypes as wt, time, os, subprocess
u32=ctypes.WinDLL("user32")
ENUMPROC=ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\eems1251_setup.exe"
p=subprocess.Popen([exe], cwd=os.path.dirname(exe))
print('pid', p.pid)
t0=time.time(); seen=set()
while time.time()-t0<30:
    def cb(h,lp):
        q=wt.DWORD(0); u32.GetWindowThreadProcessId(h,ctypes.byref(q))
        if q.value==p.pid:
            c=ctypes.create_unicode_buffer(80); u32.GetClassNameW(h,c,80)
            t=ctypes.create_unicode_buffer(300); u32.GetWindowTextW(h,t,300)
            k=(c.value,t.value)
            if k not in seen:
                seen.add(k); print(f'[{time.time()-t0:5.2f}] {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)}')
        return True
    u32.EnumWindows(ENUMPROC(cb),0)
    if p.poll() is not None:
        print(f'[{time.time()-t0:5.2f}] exited code={p.returncode}'); break
    time.sleep(0.4)
else:
    print('still running (installer UI up) -> leaving it')
