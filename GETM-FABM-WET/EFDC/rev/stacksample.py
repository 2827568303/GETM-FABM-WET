import ctypes, ctypes.wintypes as wt, os, sys, time, collections
import frida

EXE = r"C:\EFDC84_RUN\EFDC_Explorer8.4.exe"
REV = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev"

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
TH32CS_SNAPTHREAD = 0x00000004
THREAD_SUSPEND_RESUME = 0x0002
THREAD_GET_CONTEXT = 0x0008
THREAD_QUERY_INFORMATION = 0x0040
CONTEXT_CONTROL = 0x00010001
PROCESS_ALL_ACCESS = 0x1F0FFF


class THREADENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ThreadID", wt.DWORD),
                ("th32OwnerProcessID", wt.DWORD), ("tpBasePri", ctypes.c_long), ("tpDeltaPri", ctypes.c_long),
                ("dwFlags", wt.DWORD)]


class WOW64_CONTEXT(ctypes.Structure):
    _fields_ = [("ContextFlags", wt.DWORD),
                ("Dr0", wt.DWORD), ("Dr1", wt.DWORD), ("Dr2", wt.DWORD), ("Dr3", wt.DWORD), ("Dr6", wt.DWORD), ("Dr7", wt.DWORD),
                ("FloatSave", ctypes.c_byte * 112),
                ("SegGs", wt.DWORD), ("SegFs", wt.DWORD), ("SegEs", wt.DWORD), ("SegDs", wt.DWORD),
                ("Edi", wt.DWORD), ("Esi", wt.DWORD), ("Ebx", wt.DWORD), ("Edx", wt.DWORD), ("Ecx", wt.DWORD), ("Eax", wt.DWORD),
                ("Ebp", wt.DWORD), ("Eip", wt.DWORD), ("SegCs", wt.DWORD), ("EFlags", wt.DWORD), ("Esp", wt.DWORD), ("SegSs", wt.DWORD),
                ("ExtendedRegisters", ctypes.c_byte * 512)]


JS = open(os.path.join(REV, "diag51.js"), encoding="utf-8").read()
pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
sess = frida.attach(pid)
sc = sess.create_script(JS)
sc.load()
frida.resume(pid)
print("pid", pid)
time.sleep(5.0)

hproc = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
te = THREADENTRY32(); te.dwSize = ctypes.sizeof(THREADENTRY32)

best = None
t0 = time.time()
while time.time() - t0 < 3:
    k32.Thread32First(snap, ctypes.byref(te))
    while True:
        if te.th32OwnerProcessID == pid:
            h = k32.OpenThread(THREAD_GET_CONTEXT | THREAD_SUSPEND_RESUME | THREAD_QUERY_INFORMATION, False, te.th32ThreadID)
            if h:
                k32.SuspendThread(h)
                ctx = WOW64_CONTEXT(); ctx.ContextFlags = CONTEXT_CONTROL
                if k32.Wow64GetThreadContext(h, ctypes.byref(ctx)):
                    if ctx.Esp and ctx.Eip > 0x70000000:
                        best = (ctx.Eip, ctx.Esp, ctx.Ebp, te.th32ThreadID)
                k32.ResumeThread(h); k32.CloseHandle(h)
        if not k32.Thread32Next(snap, ctypes.byref(te)):
            break
    if best:
        break
    time.sleep(0.1)

print("sample:", best)
if best and hproc:
    eip, esp, ebp, tid = best
    buf = ctypes.create_string_buffer(0x4000)
    read = ctypes.c_size_t(0)
    k32.ReadProcessMemory(hproc, ctypes.c_void_p(esp), buf, 0x4000, ctypes.byref(read))
    data = buf.raw[:read.value]
    import struct
    hits = []
    for off in range(0, len(data) - 4, 4):
        v = struct.unpack_from("<I", data, off)[0]
        if 0x401000 <= v < 0x161F000 or 0x60000000 <= v < 0x64000000:
            hits.append((off, v))
    print("stack hits:", len(hits))
    for off, v in hits[:40]:
        print("  [esp+0x%04X] 0x%08X" % (off, v))

k32.CloseHandle(snap)
try:
    os.kill(pid, 9)
except Exception:
    pass
