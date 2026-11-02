import ctypes, ctypes.wintypes as wt, subprocess, os, time, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import typegui as tg
u=ctypes.WinDLL("user32"); u.GetWindowTextW.argtypes=[wt.HWND,wt.LPWSTR,ctypes.c_int]
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
t0=time.time(); done=False; clicked=False
while time.time()-t0<30:
    for h in tops(p.pid):
        if not u.IsWindowVisible(h): continue
        t=txt(h)
        if 'Demo Version' in t and 'Sign in' not in t:
            print('[%.2f] SUCCESS %r' % (time.time()-t0,t)); done=True; break
        if 'Sign in EEMS Demo' in t and not clicked:
            tg.focus(h)
            for k in kids(h):
                if cls(k).startswith('ThunderRT6CommandButton') and 'Sign' in txt(k) and '&In' in txt(k):
                    tg.click_window(k); clicked=True; print('clicked Sign In without typing'); break
    if done or p.poll() is not None: break
    time.sleep(0.3)
print('done=',done,'alive=',p.poll() is None)
