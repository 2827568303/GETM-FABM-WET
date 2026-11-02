import ctypes, ctypes.wintypes as wt, time, os
k32=ctypes.WinDLL("kernel32"); u32=ctypes.WinDLL("user32")
ENUMPROC=ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
class SI(ctypes.Structure):
    _fields_=[('cb',wt.DWORD),('a',wt.LPSTR),('b',wt.LPSTR),('c',wt.LPSTR),('x',wt.DWORD),('y',wt.DWORD),('xs',wt.DWORD),('ys',wt.DWORD),('xc',wt.DWORD),('yc',wt.DWORD),('fill',wt.DWORD),('flags',wt.DWORD),('show',wt.WORD),('r2',wt.WORD),('r',ctypes.c_void_p),('h1',wt.HANDLE),('h2',wt.HANDLE),('h3',wt.HANDLE)]
class PI(ctypes.Structure):
    _fields_=[('h',wt.HANDLE),('t',wt.HANDLE),('pid',wt.DWORD),('tid',wt.DWORD)]
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
os.chdir(os.path.dirname(exe)); si=SI(); si.cb=ctypes.sizeof(si); pi=PI()
k32.CreateProcessW(None, ctypes.c_wchar_p('"'+exe+'"'), None,None,False,0,None,None,ctypes.byref(si),ctypes.byref(pi))
t0=time.time(); fired=False; seen=set()
while time.time()-t0<26:
    top=[]
    def cb(h,lp):
        p=wt.DWORD(0); u32.GetWindowThreadProcessId(h,ctypes.byref(p))
        if p.value==pi.pid:
            c=ctypes.create_unicode_buffer(64); u32.GetClassNameW(h,c,64)
            t=ctypes.create_unicode_buffer(128); u32.GetWindowTextW(h,t,128)
            top.append((h,c.value,t.value))
            key=(c.value,t.value)
            if key not in seen:
                seen.add(key); print(f'[{time.time()-t0:5.2f}] {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)}')
        return True
    u32.EnumWindows(ENUMPROC(cb),0)
    if not fired and time.time()-t0>6.0:
        fired=True
        for h,c,t in top:
            if c=='ThunderRT6FormDC':
                timers=[]
                def cb2(ch,lp):
                    cc=ctypes.create_unicode_buffer(64); u32.GetClassNameW(ch,cc,64)
                    if cc.value=='ThunderRT6Timer': timers.append(ch)
                    return True
                u32.EnumChildWindows(h, ENUMPROC(cb2), 0)
                print(f'[{time.time()-t0:5.2f}] splash {t!r}: {len(timers)} timers -> SetTimer+WM_TIMER')
                for th in timers:
                    tid=u32.SetTimer(th, 1, 300, None)
                    u32.PostMessageW(th, 0x0113, 1, 0)
                    print(f'    timer hwnd={th:#x} SetTimerId={tid}')
    ec=wt.DWORD(0); k32.GetExitCodeProcess(ctypes.c_void_p(pi.h),ctypes.byref(ec))
    if ec.value!=259:
        print(f'[{time.time()-t0:5.2f}] exited 0x{ec.value:x}'); break
    time.sleep(0.5)
else:
    print('still running -> kill'); k32.TerminateProcess(ctypes.c_void_p(pi.h),0)
