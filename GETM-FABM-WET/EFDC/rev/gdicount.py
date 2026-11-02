import ctypes, ctypes.wintypes as wt, time, os
k32=ctypes.WinDLL('kernel32'); user32=ctypes.WinDLL('user32')
def counts(h): return (user32.GetGuiResources(ctypes.c_void_p(h),0), user32.GetGuiResources(ctypes.c_void_p(h),1))
class SI(ctypes.Structure):
    _fields_=[('cb',wt.DWORD),('a',wt.LPSTR),('b',wt.LPSTR),('c',wt.LPSTR),('x',wt.DWORD),('y',wt.DWORD),('xs',wt.DWORD),('ys',wt.DWORD),('xc',wt.DWORD),('yc',wt.DWORD),('fill',wt.DWORD),('flags',wt.DWORD),('show',wt.WORD),('r2',wt.WORD),('r',ctypes.c_void_p),('h1',wt.HANDLE),('h2',wt.HANDLE),('h3',wt.HANDLE)]
class PI(ctypes.Structure):
    _fields_=[('h',wt.HANDLE),('t',wt.HANDLE),('pid',wt.DWORD),('tid',wt.DWORD)]
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
os.chdir(os.path.dirname(exe)); si=SI(); si.cb=ctypes.sizeof(si); pi=PI()
k32.CreateProcessW(None, ctypes.c_wchar_p('"'+exe+'"'), None,None,False,0,None,None,ctypes.byref(si),ctypes.byref(pi))
t0=time.time()
for w in (0.5,1.0,2.0,4.0,6.0):
    while time.time()-t0<w: time.sleep(0.05)
    print(f"t={w:.1f}s GDI/USER =", counts(pi.h))
k32.TerminateProcess(ctypes.c_void_p(pi.h),0)
