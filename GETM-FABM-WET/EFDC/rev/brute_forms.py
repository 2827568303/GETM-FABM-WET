import ctypes, ctypes.wintypes as wt, time, os, subprocess, struct
import frida

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
cand = [d for d in os.listdir(BASE) if d.startswith("EFDC ") and "8.4" in d]
EXE = os.path.join(BASE, cand[0], "EFDC_Explorer8.4.exe")
ORIG = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
JS = open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\picfix2.js", encoding="utf-8").read()

SITE = 0x156AD58
FORMS = [0x451aa0,0x451b80,0x451bf0,0x451d08,0x451d44,0x451dbc,0x451ef0,0x451f30,0x452000,
         0x452e10,0x45a650,0x45b590,0x45d68c,0x463218,0x463930,0x465f28,0x4690c8,0x46c81c,
         0x46d1b0,0x470c6c,0x47a514,0x47b0a4,0x482c3c,0x48470c,0x48dc78,0x4921fc,0x49605c,
         0x4a6468,0x4a9b28,0x4bd5e8,0x4c24ac,0x4d5204]

u32 = ctypes.WinDLL("user32")
ENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def patch(ci):
    for _ in range(30):
        try:
            subprocess.run(["taskkill","/F","/IM","EFDC_Explorer8.4.exe"], capture_output=True)
            time.sleep(0.3)
            d = bytearray(open(EXE, "rb").read())
            o = SITE - 0x400000
            d[o:o+5] = b"\x68" + ci.to_bytes(4, "little")
            open(EXE, "wb").write(bytes(d))
            return
        except PermissionError:
            time.sleep(0.5)
    raise RuntimeError("cannot write exe")


def run_once():
    titles = []
    pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
    session = frida.attach(pid)
    sc = session.create_script(JS)
    sc.on("message", lambda m, d: None)
    sc.load()
    frida.resume(pid)
    t0 = time.time()
    seen = set()
    while time.time() - t0 < 11:
        def cb(h, lp):
            p = wt.DWORD(0)
            u32.GetWindowThreadProcessId(h, ctypes.byref(p))
            if p.value == pid:
                c = ctypes.create_unicode_buffer(80); u32.GetClassNameW(h, c, 80)
                t = ctypes.create_unicode_buffer(300); u32.GetWindowTextW(h, t, 300)
                if c.value == "ThunderRT6FormDC" and t.value:
                    if t.value not in seen:
                        seen.add(t.value)
                        titles.append(t.value)
            return True
        u32.EnumWindows(ENUMPROC(cb), 0)
        time.sleep(0.25)
    try:
        frida.kill(pid)
    except Exception:
        pass
    return titles


orig = open(ORIG, "rb").read()
for ci in FORMS:
    patch(ci)
    try:
        ts = run_once()
    except Exception as e:
        ts = ["<err %s>" % e]
    print(f"{ci:#08x} -> {ts}", flush=True)

# restore the pristine bytes at that site
d = bytearray(open(EXE, "rb").read())
o = SITE - 0x400000
d[o:o+5] = orig[o:o+5]
open(EXE, "wb").write(bytes(d))
print("restored site to", orig[o:o+5].hex())
