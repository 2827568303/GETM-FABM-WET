import sys, time, os, ctypes, ctypes.wintypes as wt
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import frida
k32=ctypes.WinDLL("kernel32"); u32=ctypes.WinDLL("user32")
WNDENUMPROC=ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
EXE=sys.argv[1]; DUR=float(sys.argv[2]); SCRIPT=sys.argv[3]
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),SCRIPT),encoding="utf-8").read()
dev=frida.get_local_device(); pid=dev.spawn([EXE], cwd=os.path.dirname(EXE)); print("pid",pid)
sess=dev.attach(pid); script=sess.create_script(src)
ndump=[0]
def on_message(msg,data):
    if msg["type"]=="send":
        print(msg["payload"], flush=True)
        if data:
            ndump[0]+=1
            p=f"dump_{ndump[0]}.bin"
            open(p,"wb").write(data)
            print("  saved",p,len(data),"bytes", flush=True)
    else: print("ERR",msg,flush=True)
script.on("message",on_message); script.load()
def dismiss():
    hits=[]
    def cb(h,lp):
        p=wt.DWORD(0); u32.GetWindowThreadProcessId(h,ctypes.byref(p))
        if p.value==pid:
            b=ctypes.create_unicode_buffer(64); u32.GetClassNameW(h,b,64)
            if b.value=="#32770":
                def cb2(h2,lp2):
                    c=ctypes.create_unicode_buffer(64); u32.GetClassNameW(h2,c,64)
                    if c.value=="Button": u32.PostMessageW(h2,0x00F5,0,0)
                    return True
                u32.EnumChildWindows(h,WNDENUMPROC(cb2),0); hits.append(h)
        return True
    u32.EnumWindows(WNDENUMPROC(cb),0); return hits
dev.resume(pid); t0=time.time()
try:
    while time.time()-t0<DUR:
        time.sleep(0.25)
        for h in dismiss(): print(f"[{time.time()-t0:6.2f}] dismissed {h}", flush=True)
finally:
    try: dev.kill(pid)
    except Exception: pass
    print("done", flush=True)
