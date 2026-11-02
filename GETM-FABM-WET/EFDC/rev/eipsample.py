import ctypes, ctypes.wintypes as wt, subprocess, os, sys, time, collections
import frida

EXE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
REV = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev"

k32 = ctypes.WinDLL("kernel32", use_last_error=True)

TH32CS_SNAPTHREAD = 0x00000004
THREAD_SUSPEND_RESUME = 0x0002
THREAD_GET_CONTEXT = 0x0008
THREAD_QUERY_INFORMATION = 0x0040
CONTEXT_CONTROL = 0x00010001


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


JS = open(os.path.join(REV, "diag51.js"), encoding="utf-8").read() + "\n" + open(os.path.join(REV, sys.argv[1] if len(sys.argv)>1 else "diag74.js"), encoding="utf-8").read()
pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
sess = frida.attach(pid)
sc = sess.create_script(JS)
sc.load()
frida.resume(pid)
print("pid", pid)

time.sleep(4.0)

snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
te = THREADENTRY32()
te.dwSize = ctypes.sizeof(THREADENTRY32)
hist = collections.Counter()
t0 = time.time()
while time.time() - t0 < 6:
    k32.Thread32First(snap, ctypes.byref(te))
    while True:
        if te.th32OwnerProcessID == pid:
            h = k32.OpenThread(THREAD_GET_CONTEXT | THREAD_SUSPEND_RESUME | THREAD_QUERY_INFORMATION, False, te.th32ThreadID)
            if h:
                k32.SuspendThread(h)
                ctx = WOW64_CONTEXT()
                ctx.ContextFlags = CONTEXT_CONTROL
                if k32.Wow64GetThreadContext(h, ctypes.byref(ctx)):
                    hist[ctx.Eip] += 1
                k32.ResumeThread(h)
                k32.CloseHandle(h)
        if not k32.Thread32Next(snap, ctypes.byref(te)):
            break
    time.sleep(0.1)

k32.CloseHandle(snap)
for eip, n in hist.most_common(15):
    print("%5d  0x%08X" % (n, eip))
try:
    os.kill(pid, 9)
except Exception:
    pass

