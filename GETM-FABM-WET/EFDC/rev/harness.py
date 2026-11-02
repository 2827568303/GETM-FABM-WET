import ctypes, ctypes.wintypes as wt, time, os, sys, glob
import frida

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
EXE = os.path.join(BASE, "EFDC 商业版8.4", "EFDC_Explorer8.4.exe")
REV = os.path.join(BASE, "rev")

js_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REV, "logspy.js")
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0
patch_file = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '-' else None

patches = []
if patch_file:
    p = patch_file if os.path.isabs(patch_file) else os.path.join(REV, patch_file)
    if os.path.exists(p):
        for line in open(p, encoding='utf-8'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            va, hexs = line.split()[:2]
            patches.append((int(va, 16), hexs))
print('patches:', [(hex(v), h) for v, h in patches], flush=True)

prelude = ''
if patches:
    prelude = 'var PATCHES = %s;\n(function(){var base=Process.getModuleByName("EFDC_Explorer8.4.exe").base;' \
              'PATCHES.forEach(function(p){var a=base.add(p[0]-0x400000);Memory.protect(a,p[1].length/2+16,"rwx");' \
              'var u=new Uint8Array(p[1].length/2);for(var i=0;i<u.length;i++)u[i]=parseInt(p[1].substr(i*2,2),16);' \
              'a.writeByteArray(u);});send("patches applied: "+PATCHES.length);})();\n' % (
                  '[' + ','.join('[%d,"%s"]' % (v, h) for v, h in patches) + ']')

JS = prelude + open(js_file, encoding='utf-8').read()

out_lines = []
pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
session = frida.attach(pid)
script = session.create_script(JS)

def on_message(msg, data):
    if msg.get('type') == 'send':
        line = str(msg.get('payload'))
        out_lines.append(line)
        print('[js]', line, flush=True)
    elif msg.get('type') == 'error':
        print('[js-err]', msg.get('stack') or msg.get('description'), flush=True)
script.on('message', on_message)
script.load()
frida.resume(pid)
print('pid', pid, flush=True)

u32 = ctypes.WinDLL("user32")
WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
t0 = time.time(); seen = set()
while time.time() - t0 < dur:
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
                line = f'[{time.time()-t0:5.2f}] WIN {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)} rect=({rr.l},{rr.t},{rr.r},{rr.b})'
                out_lines.append(line); print(line, flush=True)
        return True
    u32.EnumWindows(WNDENUMPROC(cb), 0)
    time.sleep(0.15)

print('=== files under Public\\DSI (non-stale) ===', flush=True)
for f in glob.glob(r'C:\Users\Public\DSI\**\*', recursive=True):
    if os.path.isfile(f) and 'stale' not in f:
        print('  ', f, os.path.getsize(f), flush=True)
with open(os.path.join(REV, 'harness_out.txt'), 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out_lines))
print('done', flush=True)
