import ctypes, ctypes.wintypes as wt, time, os, sys
import frida

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
EXE = os.path.join(BASE, "EFDC 商业版8.4", "EFDC_Explorer8.4.exe")
REV = os.path.join(BASE, "rev")
js_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REV, "xpix5.js")
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0

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
            t = ctypes.create_unicode_buffer(400); u32.GetWindowTextW(h, t, 400)
            k = (c.value, t.value)
            if k not in seen:
                seen.add(k)
                print(f'[{time.time()-t0:5.2f}] WIN {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)}', flush=True)
            if c.value == '#32770':
                def cb2(ch, lp2):
                    cc = ctypes.create_unicode_buffer(80); u32.GetClassNameW(ch, cc, 80)
                    tt = ctypes.create_unicode_buffer(2000); u32.GetWindowTextW(ch, tt, 2000)
                    if tt.value.strip():
                        print(f'      [{cc.value}] {tt.value}', flush=True)
                    return True
                u32.EnumChildWindows(h, ENUMPROC(cb2), 0)
        return True
    u32.EnumWindows(ENUMPROC(cb), 0)
    time.sleep(0.35)
print('done', flush=True)
