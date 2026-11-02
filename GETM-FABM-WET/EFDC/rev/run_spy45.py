import ctypes, ctypes.wintypes as wt, time, sys, os
import frida

EXE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
JS = open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\olp_diag2.js", encoding='utf-8').read()

u32 = ctypes.WinDLL("user32")
WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
session = frida.attach(pid)
script = session.create_script(JS)


def on_message(msg, data):
    if msg.get('type') == 'send':
        print('[js]', msg.get('payload'))
    elif msg.get('type') == 'error':
        print('[js-err]', msg.get('stack') or msg.get('description'))


script.on('message', on_message)
script.load()
frida.resume(pid)
print('spawned pid', pid)

t0 = time.time()
seen = set()
while time.time() - t0 < 45:
    def cb(h, lp):
        p = wt.DWORD(0)
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            c = ctypes.create_unicode_buffer(80); u32.GetClassNameW(h, c, 80)
            t = ctypes.create_unicode_buffer(256); u32.GetWindowTextW(h, t, 256)
            k = (c.value, t.value)
            if k not in seen:
                seen.add(k)
                print(f'[{time.time()-t0:5.2f}] WIN {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)}')
                if c.value == '#32770':
                    def cb2(ch, lp2):
                        cc = ctypes.create_unicode_buffer(80); u32.GetClassNameW(ch, cc, 80)
                        tt = ctypes.create_unicode_buffer(512); u32.GetWindowTextW(ch, tt, 512)
                        if tt.value.strip():
                            print(f'      child {cc.value!r}: {tt.value!r}')
                        return True
                    u32.EnumChildWindows(h, WNDENUMPROC(cb2), 0)
        return True
    u32.EnumWindows(WNDENUMPROC(cb), 0)
    time.sleep(0.3)
print('done')
try:
    frida.kill(pid)
except Exception:
    pass

