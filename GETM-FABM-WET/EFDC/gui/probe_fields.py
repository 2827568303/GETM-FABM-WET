import ctypes, ctypes.wintypes as wt, subprocess, time, os
u=ctypes.WinDLL("user32", use_last_error=True)
u.GetClassNameW.argtypes=[wt.HWND,wt.LPWSTR,ctypes.c_int]; u.GetWindowTextW.argtypes=[wt.HWND,wt.LPWSTR,ctypes.c_int]
u.SendMessageW.argtypes=[wt.HWND,wt.UINT,wt.WPARAM,wt.LPARAM]; u.SendMessageW.restype=ctypes.c_ulong
E=ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def txt(h):
    b=ctypes.create_unicode_buffer(512); u.GetWindowTextW(h,b,512); return b.value
def cls(h):
    b=ctypes.create_unicode_buffer(128); u.GetClassNameW(h,b,128); return b.value
def gt(h):
    b=ctypes.create_unicode_buffer(512); u.SendMessageW(h,0x000D,512,ctypes.cast(b,ctypes.c_void_p).value); return b.value
def st(h,s):
    b=ctypes.create_unicode_buffer(s); u.SendMessageW(h,0x000C,0,ctypes.cast(b,ctypes.c_void_p).value)
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
t0=time.time(); did=False
while time.time()-t0<30:
    for h in tops(p.pid):
        if not u.IsWindowVisible(h): continue
        t=txt(h)
        if 'Activation Wizard' in t:
            for k in kids(h):
                if cls(k).startswith('ThunderRT6CommandButton') and 'Demo Version' in txt(k):
                    u.SendMessageW(k,0x00F5,0,0)
        elif 'Sign in EEMS Demo' in t and not did:
            did=True
            boxes=[k for k in kids(h) if cls(k)=='ThunderRT6TextBox']
            print('boxes:', [(hex(x), u.GetDlgCtrlID(x)) for x in boxes])
            if len(boxes)>=2:
                st(boxes[0],'zhang.san8888@gmail.com'); st(boxes[1],'Efdc2026!')
                print(' after set -> box0=%r box1=%r' % (gt(boxes[0]), gt(boxes[1])))
                time.sleep(0.4)
                print(' after sleep -> box0=%r box1=%r' % (gt(boxes[0]), gt(boxes[1])))
            break
    if p.poll() is not None:
        print('exit', p.returncode); break
    time.sleep(0.3)
subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True)
