import sys, time, os, ctypes, ctypes.wintypes as wt
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
k32=ctypes.WinDLL("kernel32"); u32=ctypes.WinDLL("user32")
WNDENUMPROC=ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
proj=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\滇池外海EFDC模型 538cells-99-17\EFDC.EE"
class SI(ctypes.Structure):
    _fields_=[('cb',wt.DWORD),('a',wt.LPSTR),('b',wt.LPSTR),('c',wt.LPSTR),('x',wt.DWORD),('y',wt.DWORD),('xs',wt.DWORD),('ys',wt.DWORD),('xc',wt.DWORD),('yc',wt.DWORD),('fill',wt.DWORD),('flags',wt.DWORD),('show',wt.WORD),('r2',wt.WORD),('r',ctypes.c_void_p),('h1',wt.HANDLE),('h2',wt.HANDLE),('h3',wt.HANDLE)]
class PI(ctypes.Structure):
    _fields_=[('h',wt.HANDLE),('t',wt.HANDLE),('pid',wt.DWORD),('tid',wt.DWORD)]
os.chdir(os.path.dirname(exe)); si=SI(); si.cb=ctypes.sizeof(si); pi=PI()
cmd='"'+exe+'" "'+proj+'"'
k32.CreateProcessW(None, ctypes.c_wchar_p(cmd), None,None,False,0,None,None,ctypes.byref(si),ctypes.byref(pi))
print('pid',pi.pid,'cmd',cmd)
seen=set(); t0=time.time()
while time.time()-t0<25:
    def cb(h,lp):
        p=wt.DWORD(0); u32.GetWindowThreadProcessId(h,ctypes.byref(p))
        if p.value==pi.pid:
            n=u32.GetWindowTextLengthW(h); b=ctypes.create_unicode_buffer(n+2); u32.GetWindowTextW(h,b,n+2)
            c=ctypes.create_unicode_buffer(64); u32.GetClassNameW(h,c,64)
            key=(c.value,b.value)
            if key not in seen:
                seen.add(key); print(f'[{time.time()-t0:6.2f}] {c.value!r} {b.value!r}')
        return True
    u32.EnumWindows(WNDENUMPROC(cb),0)
    ec=wt.DWORD(0); k32.GetExitCodeProcess(ctypes.c_void_p(pi.h),ctypes.byref(ec))
    if ec.value!=259:
        print(f'[{time.time()-t0:6.2f}] exited {ec.value:#x}'); break
    time.sleep(0.4)
else:
    print('still running -> kill'); k32.TerminateProcess(ctypes.c_void_p(pi.h),0)
