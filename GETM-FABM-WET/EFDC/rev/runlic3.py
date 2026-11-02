import ctypes, ctypes.wintypes as wt, time, os, subprocess
u32=ctypes.WinDLL("user32")
ENUMPROC=ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
d=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EEMS125\x86"
exe=os.path.join(d,'EFDC_LIC.exe')
p=subprocess.Popen([exe], cwd=d)
print('pid',p.pid)
t0=time.time(); seen=set()
while time.time()-t0<20:
    def cb(h,lp):
        q=wt.DWORD(0); u32.GetWindowThreadProcessId(h,ctypes.byref(q))
        if q.value==p.pid:
            c=ctypes.create_unicode_buffer(80); u32.GetClassNameW(h,c,80)
            t=ctypes.create_unicode_buffer(400); u32.GetWindowTextW(h,t,400)
            k=(c.value,t.value)
            if k not in seen:
                seen.add(k); print(f'[{time.time()-t0:5.2f}] {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)}')
                def cb2(ch,lp2):
                    cc=ctypes.create_unicode_buffer(80); u32.GetClassNameW(ch,cc,80)
                    tt=ctypes.create_unicode_buffer(900); u32.GetWindowTextW(ch,tt,900)
                    if tt.value.strip(): print(f'      {cc.value!r}: {tt.value[:250]!r}')
                    return True
                u32.EnumChildWindows(h, ENUMPROC(cb2), 0)
        return True
    u32.EnumWindows(ENUMPROC(cb),0)
    if p.poll() is not None:
        print(f'[{time.time()-t0:5.2f}] exited code={p.returncode}'); break
    time.sleep(0.3)
else:
    print('still running')
