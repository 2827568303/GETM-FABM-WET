import ctypes, ctypes.wintypes as wt, time, os
k32=ctypes.WinDLL("kernel32"); u32=ctypes.WinDLL("user32")
ENUMPROC=ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
class SI(ctypes.Structure):
    _fields_=[('cb',wt.DWORD),('a',wt.LPSTR),('b',wt.LPSTR),('c',wt.LPSTR),('x',wt.DWORD),('y',wt.DWORD),('xs',wt.DWORD),('ys',wt.DWORD),('xc',wt.DWORD),('yc',wt.DWORD),('fill',wt.DWORD),('flags',wt.DWORD),('show',wt.WORD),('r2',wt.WORD),('r',ctypes.c_void_p),('h1',wt.HANDLE),('h2',wt.HANDLE),('h3',wt.HANDLE)]
class PI(ctypes.Structure):
    _fields_=[('h',wt.HANDLE),('t',wt.HANDLE),('pid',wt.DWORD),('tid',wt.DWORD)]
class RECT(ctypes.Structure):
    _fields_=[('l',wt.LONG),('t',wt.LONG),('r',wt.LONG),('b',wt.LONG)]
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
os.chdir(os.path.dirname(exe)); si=SI(); si.cb=ctypes.sizeof(si); pi=PI()
k32.CreateProcessW(None, ctypes.c_wchar_p('"'+exe+'"'), None,None,False,0,None,None,ctypes.byref(si),ctypes.byref(pi))
time.sleep(8)
def describe(h, depth):
    c=ctypes.create_unicode_buffer(64); u32.GetClassNameW(h,c,64)
    t=ctypes.create_unicode_buffer(128); u32.GetWindowTextW(h,t,128)
    r=RECT(); u32.GetWindowRect(h,ctypes.byref(r))
    p=wt.DWORD(0); u32.GetWindowThreadProcessId(h,ctypes.byref(p))
    if p.value!=pi.pid: return
    print('  '*depth + f'{c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)} rect=({r.l},{r.t},{r.r},{r.b})')
    def cb(ch,lp):
        describe(ch, depth+1); return True
    u32.EnumChildWindows(h, ENUMPROC(cb), 0)
def top(h,lp):
    p=wt.DWORD(0); u32.GetWindowThreadProcessId(h,ctypes.byref(p))
    if p.value==pi.pid: describe(h,0)
    return True
u32.EnumWindows(ENUMPROC(top),0)
k32.TerminateProcess(ctypes.c_void_p(pi.h),0)
