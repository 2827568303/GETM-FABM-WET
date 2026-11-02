import ctypes, ctypes.wintypes as wt, time, os
k32=ctypes.WinDLL("kernel32"); u32=ctypes.WinDLL("user32")
WNDENUMPROC=ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
class SI(ctypes.Structure):
    _fields_=[('cb',wt.DWORD),('a',wt.LPSTR),('b',wt.LPSTR),('c',wt.LPSTR),('x',wt.DWORD),('y',wt.DWORD),('xs',wt.DWORD),('ys',wt.DWORD),('xc',wt.DWORD),('yc',wt.DWORD),('fill',wt.DWORD),('flags',wt.DWORD),('show',wt.WORD),('r2',wt.WORD),('r',ctypes.c_void_p),('h1',wt.HANDLE),('h2',wt.HANDLE),('h3',wt.HANDLE)]
class PI(ctypes.Structure):
    _fields_=[('h',wt.HANDLE),('t',wt.HANDLE),('pid',wt.DWORD),('tid',wt.DWORD)]
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_LIC.exe"
os.chdir(os.path.dirname(exe)); si=SI(); si.cb=ctypes.sizeof(si); pi=PI()
k32.CreateProcessW(None, ctypes.c_wchar_p('"'+exe+'"'), None,None,False,0,None,None,ctypes.byref(si),ctypes.byref(pi))
print('pid',pi.pid)
t0=time.time(); seen=set()
while time.time()-t0<20:
    def cb(h,lp):
        p=wt.DWORD(0); u32.GetWindowThreadProcessId(h,ctypes.byref(p))
        if p.value==pi.pid:
            c=ctypes.create_unicode_buffer(64); u32.GetClassNameW(h,c,64)
            t=ctypes.create_unicode_buffer(200); u32.GetWindowTextW(h,t,200)
            key=(c.value,t.value)
            if key not in seen:
                seen.add(key); print(f'[{time.time()-t0:5.2f}] {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)}')
        return True
    u32.EnumWindows(WNDENUMPROC(cb),0)
    ec=wt.DWORD(0); k32.GetExitCodeProcess(ctypes.c_void_p(pi.h),ctypes.byref(ec))
    if ec.value!=259:
        print(f'[{time.time()-t0:5.2f}] exited 0x{ec.value:x}'); break
    time.sleep(0.4)
else:
    print('still running -> kill'); k32.TerminateProcess(ctypes.c_void_p(pi.h),0)
