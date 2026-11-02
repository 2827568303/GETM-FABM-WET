import ctypes, ctypes.wintypes as wt, subprocess, time
u=ctypes.WinDLL('user32', use_last_error=True)
u.GetClassNameW.argtypes=[wt.HWND,wt.LPWSTR,ctypes.c_int]; u.GetWindowTextW.argtypes=[wt.HWND,wt.LPWSTR,ctypes.c_int]
u.SendMessageW.argtypes=[wt.HWND,wt.UINT,wt.WPARAM,wt.LPARAM]; u.SendMessageW.restype=ctypes.c_ulong
CB=ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def txt(h):
    b=ctypes.create_unicode_buffer(512); u.GetWindowTextW(h,b,512); return b.value
def cls(h):
    b=ctypes.create_unicode_buffer(128); u.GetClassNameW(h,b,128); return b.value
def tops(pid):
    out=[]
    def cb(h,l):
        p=wt.DWORD(0); u.GetWindowThreadProcessId(h,ctypes.byref(p))
        if p.value==pid: out.append(h)
        return True
    u.EnumWindows(CB(cb),0); return out
def kids(h):
    out=[]
    def cb(c,l): out.append(c); return True
    u.EnumChildWindows(h,CB(cb),0); return out
exe=r'C:\Users\23801\AppData\Local\EFDC84\app\EFDC_Explorer8.4.exe'
p=subprocess.Popen([exe], cwd=exe.rsplit('\\',1)[0])
t0=time.time(); stage=0
while time.time()-t0 < 25:
    for h in tops(p.pid):
        if not u.IsWindowVisible(h): continue
        t=txt(h)
        if stage==0 and 'Activation Wizard' in t:
            for k in kids(h):
                if cls(k).startswith('ThunderRT6CommandButton') and 'Demo Version' in txt(k):
                    u.SendMessageW(k,0x00F5,0,0); stage=1
        elif stage==1 and 'Sign in' in t:
            boxes=[k for k in kids(h) if cls(k)=='ThunderRT6TextBox']
            print('boxes:', len(boxes))
            allkids=[(cls(c), txt(c), c) for c in kids(h)]
            print('classes seen:', sorted(set(c for c,_,_ in allkids))[:12])
            edits=[c for c,tt,c in allkids if c=='Edit']
            print('native edits:', len(edits))
            if len(edits)>=2:
                for hh,val in ((edits[0],'user@example.com'),(edits[1],'Passw0rd!')):
                    buf=ctypes.create_unicode_buffer(val)
                    u.SendMessageW(hh,0x000C,0,ctypes.cast(buf,ctypes.c_void_p).value)
                print(' readback email=', repr(txt(edits[0])), 'pass=', repr(txt(edits[1])))
                stage=2
    if p.poll() is not None:
        print('exit', p.returncode); break
    time.sleep(0.3)
subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True)
