import ctypes, ctypes.wintypes as wt, os, time, struct
import frida

EXE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
REV = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev"

u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
u32.GetWindowThreadProcessId.restype = wt.DWORD
E = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

THREAD_SUSPEND_RESUME = 0x0002
THREAD_GET_CONTEXT = 0x0008
THREAD_QUERY_INFORMATION = 0x0040
CONTEXT_CONTROL = 0x00010001
PROCESS_ALL_ACCESS = 0x1F0FFF


class WOW64_CONTEXT(ctypes.Structure):
    _fields_ = [("ContextFlags", wt.DWORD),
                ("Dr0", wt.DWORD), ("Dr1", wt.DWORD), ("Dr2", wt.DWORD), ("Dr3", wt.DWORD), ("Dr6", wt.DWORD), ("Dr7", wt.DWORD),
                ("FloatSave", ctypes.c_byte * 112),
                ("SegGs", wt.DWORD), ("SegFs", wt.DWORD), ("SegEs", wt.DWORD), ("SegDs", wt.DWORD),
                ("Edi", wt.DWORD), ("Esi", wt.DWORD), ("Ebx", wt.DWORD), ("Edx", wt.DWORD), ("Ecx", wt.DWORD), ("Eax", wt.DWORD),
                ("Ebp", wt.DWORD), ("Eip", wt.DWORD), ("SegCs", wt.DWORD), ("EFlags", wt.DWORD), ("Esp", wt.DWORD), ("SegSs", wt.DWORD),
                ("ExtendedRegisters", ctypes.c_byte * 512)]


def cls(h):
    b = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, b, 256); return b.value


JS = open(os.path.join(REV, "diag51.js"), encoding="utf-8").read() + "\n" + open(os.path.join(REV, "diag86.js"), encoding="utf-8").read()
pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
sess = frida.attach(pid)
sc = sess.create_script(JS)
sc.on("message", lambda m, d: print("[js]", m.get("payload") or m.get("description"), flush=True))
sc.load()
frida.resume(pid)
print("pid", pid, flush=True)

time.sleep(10)

form = []

def cb(h, l):
    p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
    if p.value == pid and cls(h).startswith("ThunderRT6Form"):
        form.append(h)
    return True
u32.EnumWindows(E(cb), 0)
print("form hwnds", [hex(h) for h in form], flush=True)
if not form:
    os.kill(pid, 9)
    raise SystemExit("no form")

tid = wt.DWORD(0)
u32.GetWindowThreadProcessId(form[0], ctypes.byref(tid))
print("form thread id", tid.value, flush=True)

h = k32.OpenThread(THREAD_GET_CONTEXT | THREAD_SUSPEND_RESUME | THREAD_QUERY_INFORMATION, False, tid.value)
hproc = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
print("OpenThread ->", h, "err", ctypes.get_last_error())
if h:
    print("suspend ->", k32.SuspendThread(h), "err", ctypes.get_last_error())
    ctx = WOW64_CONTEXT(); ctx.ContextFlags = CONTEXT_CONTROL
    ok = k32.Wow64GetThreadContext(h, ctypes.byref(ctx))
    print("ctx ok=%s EIP=0x%08X ESP=0x%08X EBP=0x%08X" % (ok, ctx.Eip, ctx.Esp, ctx.Ebp), flush=True)
    buf = ctypes.create_string_buffer(0x2000)
    read = ctypes.c_size_t(0)
    k32.ReadProcessMemory(hproc, ctypes.c_void_p(ctx.Esp), buf, 0x2000, ctypes.byref(read))
    data = buf.raw[:read.value]
    hits = []
    for off in range(0, len(data) - 4, 4):
        v = struct.unpack_from("<I", data, off)[0]
        if 0x401000 <= v < 0x161F000 or 0x60000000 <= v < 0x64000000:
            hits.append((off, v))
    print("stack hits:", len(hits))
    for off, v in hits[:30]:
        print("  [esp+0x%04X] 0x%08X" % (off, v))
    k32.ResumeThread(h)
    k32.CloseHandle(h)

try:
    os.kill(pid, 9)
except Exception:
    pass

