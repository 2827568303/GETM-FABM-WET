import ctypes, ctypes.wintypes as wt, time, os, sys, glob
import frida

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
EXE = os.path.join(BASE, "EFDC 鍟嗕笟鐗?.4", "EFDC_Explorer8.4.exe")
REV = os.path.join(BASE, "rev")
js_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REV, "xmsg.js")
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 14.0
JS = open(js_file, encoding='utf-8').read()

u32 = ctypes.WinDLL("user32")
ENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
session = frida.attach(pid)
script = session.create_script(JS)
def on_message(msg, data):
    if msg.get('type') == 'send':
        print('[js]', msg.get('payload'), flush=True)
    elif msg.get('type') == 'error':
        print('[js-err]', msg.get('description'), flush=True)
script.on('message', on_message)
script.load()
frida.resume(pid)
print('pid', pid, flush=True)

t0 = time.time(); seen = set()
while time.time() - t0 < dur:
    def cb(h, lp):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            c = ctypes.create_unicode_buffer(80); u32.GetClassNameW(h, c, 80)
            k = (c.value, h)
            if c.value not in seen:
                seen.add(c.value)
                class R(ctypes.Structure):
                    _fields_=[('l',wt.LONG),('t',wt.LONG),('r',wt.LONG),('b',wt.LONG)]
                rr=R(); u32.GetWindowRect(h, ctypes.byref(rr))
                print(f'[{time.time()-t0:5.2f}] WIN class={c.value!r} hwnd={h:#x} vis={u32.IsWindowVisible(h)} rect=({rr.l},{rr.t},{rr.r},{rr.b})', flush=True)
        return True
    u32.EnumWindows(ENUMPROC(cb), 0)
    time.sleep(0.4)
print('done', flush=True)
os._exit(0)

