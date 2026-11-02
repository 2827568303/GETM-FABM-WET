import ctypes, ctypes.wintypes as wt, time, os
k32=ctypes.WinDLL("kernel32"); u32=ctypes.WinDLL("user32")
class SI(ctypes.Structure):
    _fields_=[('cb',wt.DWORD),('a',wt.LPSTR),('b',wt.LPSTR),('c',wt.LPSTR),('x',wt.DWORD),('y',wt.DWORD),('xs',wt.DWORD),('ys',wt.DWORD),('xc',wt.DWORD),('yc',wt.DWORD),('fill',wt.DWORD),('flags',wt.DWORD),('show',wt.WORD),('r2',wt.WORD),('r',ctypes.c_void_p),('h1',wt.HANDLE),('h2',wt.HANDLE),('h3',wt.HANDLE)]
class PI(ctypes.Structure):
    _fields_=[('h',wt.HANDLE),('t',wt.HANDLE),('pid',wt.DWORD),('tid',wt.DWORD)]
class FT(ctypes.Structure):
    _fields_=[('lo',wt.DWORD),('hi',wt.DWORD)]
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
os.chdir(os.path.dirname(exe)); si=SI(); si.cb=ctypes.sizeof(si); pi=PI()
k32.CreateProcessW(None, ctypes.c_wchar_p('"'+exe+'"'), None,None,False,0,None,None,ctypes.byref(si),ctypes.byref(pi))
h=ctypes.c_void_p(pi.h)
def cpu():
    c=FT(); e=FT(); k32.GetProcessTimes(h,ctypes.byref(c),ctypes.byref(e),ctypes.byref(FT()),ctypes.byref(FT()))
    return (c.hi*4294967296+c.lo)/1e7
t0=time.time(); prev=cpu(); prevt=t0
print('t(s)  cpu(s)  cpu%  threads  handles')
while time.time()-t0<16:
    time.sleep(1.0)
    ec=wt.DWORD(0); k32.GetExitCodeProcess(h,ctypes.byref(ec))
    if ec.value!=259:
        print(f'{time.time()-t0:5.1f}  exited 0x{ec.value:x}'); break
    now=cpu(); nowt=time.time()
    pct=(now-prev)/(nowt-prevt)*100
    cnt=wt.DWORD(0)
    k32.GetProcessHandleCount(h,ctypes.byref(cnt))
    print(f'{time.time()-t0:5.1f}  {now:6.2f}  {pct:5.1f}%')
    prev=now; prevt=nowt
try: k32.TerminateProcess(h,0)
except: pass
