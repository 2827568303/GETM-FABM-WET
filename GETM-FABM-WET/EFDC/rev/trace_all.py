import ctypes, ctypes.wintypes as wt, time, os, sys, collections
import frida

EXE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
JS = open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\trace_all.js", encoding='utf-8').read()
DUR = float(sys.argv[1]) if len(sys.argv)>1 else 40.0

u32 = ctypes.WinDLL("user32")
WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
session = frida.attach(pid)
script = session.create_script(JS)
logs = []
def on_message(msg, data):
    if msg.get('type') == 'send':
        line = str(msg.get('payload'))
        logs.append(line)
        print('[js]', line, flush=True)
    elif msg.get('type') == 'error':
        print('[js-err]', msg.get('stack') or msg.get('description'), flush=True)
script.on('message', on_message)
script.load()
frida.resume(pid)
print('spawned pid', pid, flush=True)

t0 = time.time()
seen = set()
last_snap = 0
samples = collections.Counter()
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
                print(f'[{time.time()-t0:5.2f}] WIN {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)} rect=({rr.l},{rr.t},{rr.r},{rr.b}) hwnd={h:#x}', flush=True)
        return True
    u32.EnumWindows(WNDENUMPROC(cb), 0)
    if time.time() - last_snap > 1.0 and time.time()-t0 > 6:
        last_snap = time.time()
        try:
            snap = script.exports_sync.snapshot()
            for th in snap:
                if 'pc' in th:
                    samples[(th['id'], th['pc'])] += 1
        except Exception as e:
            print('snaperr', e, flush=True)
    time.sleep(0.1)

print('=== TOP sampled PCs ===', flush=True)
for (tid, pc), n in samples.most_common(25):
    print(f'  th{tid} {pc} x{n}', flush=True)
print('=== final snapshot ===', flush=True)
try:
    for th in script.exports_sync.snapshot():
        print(' th', th.get('id'), th.get('pc'), ' :: ', ' <- '.join(th.get('bt',[])[:8]), flush=True)
except Exception as e:
    print('snap err', e)
print('LEAVE RUNNING pid', pid, flush=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'trace_all_out.txt'),'w',encoding='utf-8') as f:
    f.write('\n'.join(logs))
