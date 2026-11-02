import ctypes, ctypes.wintypes as wt, subprocess, os, time, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
u=ctypes.WinDLL("user32"); u.GetWindowTextW.argtypes=[wt.HWND,wt.LPWSTR,ctypes.c_int]
u.GetWindowRect.argtypes=[wt.HWND, ctypes.POINTER(wt.RECT)]
u.SendMessageW.argtypes=[wt.HWND,wt.UINT,wt.WPARAM,wt.LPARAM]; u.SendMessageW.restype=ctypes.c_ulong
E=ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def txt(h):
    b=ctypes.create_unicode_buffer(256); u.GetWindowTextW(h,b,256); return b.value
def cls(h):
    b=ctypes.create_unicode_buffer(128); u.GetClassNameW(h,b,128); return b.value
def tops(pid):
    o=[]
    def cb(h,l):
        p=wt.DWORD(0); u.GetWindowThreadProcessId(h,ctypes.byref(p))
        if p.value==pid: o.append(h)
        return True
    u.EnumWindows(E(cb),0); return o
def kids(h):
    o=[]
    def cb(c,l): o.append(c); return True
    u.EnumChildWindows(h,E(cb),0); return o
exe=os.path.join(os.environ['LOCALAPPDATA'],'EFDC84','app','EFDC_Explorer8.4.exe')
p=subprocess.Popen([exe], cwd=os.path.dirname(exe))
t0=time.time()
while time.time()-t0<30:
    for h in tops(p.pid):
        if u.IsWindowVisible(h) and 'Sign in EEMS Demo' in txt(h):
            for k in kids(h):
                if cls(k)=='ThunderRT6TextBox':
                    r=wt.RECT(); u.GetWindowRect(k, ctypes.byref(r))
                    print('id=%-3d  top=%-5d left=%-5d size=%dx%d' % (u.GetDlgCtrlID(k), r.top, r.left, r.right-r.left, r.bottom-r.top))
            raise SystemExit
    time.sleep(0.3)
