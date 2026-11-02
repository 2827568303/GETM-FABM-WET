import ctypes, ctypes.wintypes as wt, time, os, sys
import frida

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
EXE = os.path.join(BASE, "EFDC 商业版8.4", "EFDC_Explorer8.4.exe")
REV = os.path.join(BASE, "rev")

js_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REV, "probe2.js")
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0
JS = open(js_file, encoding='utf-8').read()

u32 = ctypes.WinDLL("user32")
ENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
WM_GETTEXT = 0x000D
SMTO_ABORTIFHUNG = 0x0002
BM_CLICK = 0x00F5
WM_COMMAND = 0x0111

def text_of(hwnd, n=2000):
    buf = ctypes.create_unicode_buffer(n)
    res = ctypes.c_size_t(0)
    ok = u32.SendMessageTimeoutW(hwnd, WM_GETTEXT, n, buf, SMTO_ABORTIFHUNG, 300, ctypes.byref(res))
    if not ok:
        return '<unresponsive>'
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

t0 = time.time(); seen = set(); dumped = set(); clicked = set()
while time.time() - t0 < dur:
    def cb(h, lp):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            c = ctypes.create_unicode_buffer(80); u32.GetClassNameW(h, c, 80)
            k = c.value
            if k not in seen:
                seen.add(k)
                print(f'[{time.time()-t0:5.2f}] WIN {c.value!r} hwnd={h:#x} vis={u32.IsWindowVisible(h)} title={text_of(h,300)!r}', flush=True)
            if c.value == '#32770':
                if h not in dumped:
                    dumped.add(h)
                    def cb2(ch, lp2):
                        cc = ctypes.create_unicode_buffer(80); u32.GetClassNameW(ch, cc, 80)
                        t = text_of(ch)
                        if t.strip():
                            print(f'      [{cc.value}] {t!r}', flush=True)
                        return True
                    u32.EnumChildWindows(h, ENUMPROC(cb2), 0)
                if h not in clicked and time.time() - t0 > 1.5:
                    clicked.add(h)
                    btn = u32.GetDlgItem(h, 1)  # IDOK
                    if not btn:
                        # enumerate children, click the Button
                        found = []
                        def cb3(ch, lp3):
                            cc = ctypes.create_unicode_buffer(80); u32.GetClassNameW(ch, cc, 80)
                            if cc.value == 'Button':
                                found.append(ch)
                            return True
                        u32.EnumChildWindows(h, ENUMPROC(cb3), 0)
                        if found:
                            btn = found[0]
                    if btn:
                        print(f'[{time.time()-t0:5.2f}] AUTO-CLICK OK on {h:#x} btn={btn:#x}', flush=True)
                        u32.SendMessageW(btn, BM_CLICK, 0, 0)
        return True
    u32.EnumWindows(ENUMPROC(cb), 0)
    time.sleep(0.4)
print('done', flush=True)
