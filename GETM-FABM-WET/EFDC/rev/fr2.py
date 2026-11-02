import sys, time, os, ctypes, ctypes.wintypes as wt
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import frida

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
u32 = ctypes.WinDLL('user32', use_last_error=True)
WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

EXE = sys.argv[1]
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 22.0
SCRIPT = sys.argv[3] if len(sys.argv) > 3 else 'hook2.js'
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), SCRIPT), encoding='utf-8').read()

dev = frida.get_local_device()
pid = dev.spawn([EXE], cwd=os.path.dirname(EXE))
print('pid', pid, flush=True)
sess = dev.attach(pid)
script = sess.create_script(src)


def on_message(msg, data):
    if msg['type'] == 'send':
        print(msg['payload'], flush=True)
    else:
        print('ERR', msg, flush=True)


script.on('message', on_message)
script.load()

# auto-dismiss message boxes
def dismiss():
    hits = []
    def cb(h, lp):
        p = wt.DWORD(0)
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            b = ctypes.create_unicode_buffer(64)
            u32.GetClassNameW(h, b, 64)
            if b.value == '#32770':
                def cb2(h2, lp2):
                    cb2_ = ctypes.create_unicode_buffer(64)
                    u32.GetClassNameW(h2, cb2_, 64)
                    if cb2_.value == 'Button':
                        u32.PostMessageW(h2, 0x00F5, 0, 0)   # BM_CLICK
                    return True
                u32.EnumChildWindows(h, WNDENUMPROC(cb2), 0)
                hits.append(h)
        return True
    u32.EnumWindows(WNDENUMPROC(cb), 0)
    return hits

dev.resume(pid)
t0 = time.time()
n = 0
try:
    while time.time() - t0 < DUR:
        time.sleep(0.25)
        for h in dismiss():
            n += 1
            print(f'[{time.time()-t0:6.2f}] dismissed dialog {h}', flush=True)
finally:
    try:
        dev.kill(pid)
    except Exception as e:
        pass
    print('done, dialogs dismissed:', n, flush=True)
