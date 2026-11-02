import ctypes, ctypes.wintypes as wt, time, os, sys, json
import frida

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
EXE = os.path.join(BASE, "EFDC 商业版8.4", "EFDC_Explorer8.4.exe")
REV = os.path.join(BASE, "rev")

js_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REV, "diag1.js")
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 40.0
JS = open(js_file, encoding="utf-8").read()

u32 = ctypes.WinDLL("user32", use_last_error=True)
ENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
WM_GETTEXT = 0x000D
SMTO_ABORTIFHUNG = 0x0002


def text_of(hwnd, n=400):
    buf = ctypes.create_unicode_buffer(n)
    res = ctypes.c_size_t(0)
    ok = u32.SendMessageTimeoutW(hwnd, WM_GETTEXT, n, buf, SMTO_ABORTIFHUNG, 300, ctypes.byref(res))
    if not ok:
        return "<unresponsive>"
    return buf.value


pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
session = frida.attach(pid)
script = session.create_script(JS)


def on_message(msg, data):
    if msg.get("type") == "send":
        print("[js]", msg.get("payload"), flush=True)
    elif msg.get("type") == "error":
        print("[js-err]", msg.get("description"), flush=True)


script.on("message", on_message)
script.load()
frida.resume(pid)
print("pid", pid, flush=True)

t0 = time.time()
seen = set()
while time.time() - t0 < dur:
    def cb(h, lp):
        p = wt.DWORD(0)
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            c = ctypes.create_unicode_buffer(120)
            u32.GetClassNameW(c, 120)
            key = (c.value, text_of(h, 80))
            if key not in seen:
                seen.add(key)
                print(f"[{time.time()-t0:5.2f}] WIN {c.value!r} hwnd={h:#x} vis={u32.IsWindowVisible(h)} title={text_of(h,120)!r}", flush=True)
        return True
    u32.EnumWindows(ENUMPROC(cb), 0)
    time.sleep(0.5)

try:
    print("---- RIP SAMPLE ----", flush=True)
    for k, v in script.exports_sync.dump():
        print(f"  {v:5d}  {k}", flush=True)
except Exception as e:
    print("dump err", e, flush=True)

alive = True
try:
    os.kill(pid, 9)
except Exception:
    pass
print("done", flush=True)
