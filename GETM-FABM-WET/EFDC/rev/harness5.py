import ctypes, ctypes.wintypes as wt, time, os, sys
import frida

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
EXE = os.path.join(BASE, "EFDC 商业版8.4", "EFDC_Explorer8.4.exe")
REV = os.path.join(BASE, "rev")
js_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REV, "xpix5.js")
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 14.0
JS = open(js_file, encoding='utf-8').read()

u32 = ctypes.WinDLL("user32")
ENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
u32.SendMessageTimeoutW.restype = ctypes.c_size_t
u32.SendMessageTimeoutW.argtypes = [wt.HWND, wt.UINT, ctypes.c_void_p, ctypes.c_void_p, wt.UINT, wt.UINT, ctypes.POINTER(ctypes.c_size_t)]

WM_GETTEXT = 0x000D
SMTO_ABORTIFHUNG = 0x0002

def text_of(hwnd, n=3000):
    buf = ctypes.create_unicode_buffer(n)
    res = ctypes.c_size_t(0)
    ok = u32.SendMessageTimeoutW(hwnd, WM_GETTEXT, ctypes.c_void_p(n), ctypes.cast(buf, ctypes.c_void_p), SMTO_ABORTIFHUNG, 250, ctypes.byref(res))
    if not ok:
        return '<timeout>'
    return buf.value

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

t0 = time.time(); dumped = set()
while time.time() - t0 < dur:
    def cb(h, lp):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            c = ctypes.create_unicode_buffer(80); u32.GetClassNameW(h, c, 80)
            if c.value == '#32770' and h not in dumped:
                dumped.add(h)
                print('=== dialog %#x ===' % h, flush=True)
                print('   [caption] %r' % text_of(h), flush=True)
                def cb2(ch, lp2):
                    cc = ctypes.create_unicode_buffer(80); u32.GetClassNameW(ch, cc, 80)
                    t = text_of(ch)
                    if t.strip():
                        print('   [%s] %r' % (cc.value, t), flush=True)
                    return True
                u32.EnumChildWindows(h, ENUMPROC(cb2), 0)
        return True
    u32.EnumWindows(ENUMPROC(cb), 0)
    time.sleep(0.4)
print('done', flush=True)
