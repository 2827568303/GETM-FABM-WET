import ctypes, ctypes.wintypes as wt, time, os, sys
import frida

EXE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
JS = open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\prof.js", encoding='utf-8').read()

u32 = ctypes.WinDLL("user32")
WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
session = frida.attach(pid)
script = session.create_script(JS)

def on_message(msg, data):
    if msg.get('type') == 'send':
        print('[js]', msg.get('payload'), flush=True)
    elif msg.get('type') == 'error':
        print('[js-err]', msg.get('stack') or msg.get('description'), flush=True)

script.on('message', on_message)
script.load()
frida.resume(pid)
print('spawned pid', pid, flush=True)

t0 = time.time()
seen = set()
while time.time() - t0 < 30:
    def cb(h, lp):
        p = wt.DWORD(0)
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            c = ctypes.create_unicode_buffer(80); u32.GetClassNameW(h, c, 80)
            t = ctypes.create_unicode_buffer(256); u32.GetWindowTextW(h, t, 256)
            k = (c.value, t.value)
            if k not in seen:
                seen.add(k)
                class R(ctypes.Structure):
                    _fields_=[('l',wt.LONG),('t',wt.LONG),('r',wt.LONG),('b',wt.LONG)]
                rr=R(); u32.GetWindowRect(h, ctypes.byref(rr))
                print(f'[{time.time()-t0:5.2f}] WIN {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)} rect=({rr.l},{rr.t},{rr.r},{rr.b}) hwnd={h:#x}', flush=True)
        return True
    u32.EnumWindows(WNDENUMPROC(cb), 0)
    time.sleep(0.03)
print('enum done', flush=True)
time.sleep(8)
print('alive?', flush=True)
try:
    print(frida.get_process(pid).parameters if False else '', end='')
except Exception:
    pass
# leave process running for manual inspection
print('pid left running:', pid, flush=True)
