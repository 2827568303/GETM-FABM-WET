import ctypes, ctypes.wintypes as wt, time, os
import frida
EXE=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
import glob
c=glob.glob(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC *8.4\EFDC_Explorer8.4.exe")
EXE=c[0]
JS=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\picfix2.js",encoding='utf-8').read()
u32=ctypes.WinDLL("user32")
ENUMPROC=ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
pid=frida.spawn(EXE, cwd=os.path.dirname(EXE))
s=frida.attach(pid); sc=s.create_script(JS); sc.on('message',lambda m,d:None); sc.load(); frida.resume(pid)
t0=time.time(); shown=False
while time.time()-t0<20:
    def cb(h,lp):
        global shown
        p=wt.DWORD(0); u32.GetWindowThreadProcessId(h,ctypes.byref(p))
        if p.value==pid:
            cc=ctypes.create_unicode_buffer(80); u32.GetClassNameW(h,cc,80)
            tt=ctypes.create_unicode_buffer(300); u32.GetWindowTextW(h,tt,300)
            if cc.value=='ThunderRT6FormDC' and tt.value:
                vis=u32.IsWindowVisible(h)
                if not shown:
                    r=u32.ShowWindow(h,5)
                    print(f'ShowWindow({tt.value!r}) -> {r}, visible now={u32.IsWindowVisible(h)}')
                    u32.SetForegroundWindow(h)
                    shown=True
        return True
    u32.EnumWindows(ENUMPROC(cb),0)
    time.sleep(0.4)
    if shown and time.time()-t0>14: break
try: frida.kill(pid)
except: pass
