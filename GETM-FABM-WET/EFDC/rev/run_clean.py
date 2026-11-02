import ctypes, ctypes.wintypes as wt, time, os, sys, glob
import frida

EXE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
JS = open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\picfix2.js", encoding='utf-8').read()
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 25.0

u32 = ctypes.WinDLL("user32")
WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
session = frida.attach(pid)
script = session.create_script(JS)
def on_message(msg, data):
    if msg.get('type') == 'send':
        print('[js]', msg.get('payload'), flush=True)
script.on('message', on_message)
script.load()
frida.resume(pid)
print('pid', pid, flush=True)

t0 = time.time(); seen = set(); last_log = None
while time.time() - t0 < DUR:
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
                print(f'[{time.time()-t0:5.2f}] WIN {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)} rect=({rr.l},{rr.t},{rr.r},{rr.b})', flush=True)
        return True
    u32.EnumWindows(WNDENUMPROC(cb), 0)
    for f in glob.glob(r'C:\Users\Public\DSI\**\*.log', recursive=True):
        sz = os.path.getsize(f)
        if sz != last_log:
            pass
    time.sleep(0.2)
print('=== logs ===', flush=True)
for f in glob.glob(r'C:\Users\Public\DSI\**\*', recursive=True):
    if os.path.isfile(f):
        print(' ', f, os.path.getsize(f), flush=True)
print('alive=', flush=True)
try:
    print(frida.get_process(pid) is not None)
except Exception as e:
    print('dead', e)
