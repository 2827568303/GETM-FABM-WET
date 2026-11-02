import ctypes, ctypes.wintypes as wt, time, sys, os, struct
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
k32 = ctypes.WinDLL('kernel32', use_last_error=True)

class STARTUPINFOA(ctypes.Structure):
    _fields_ = [('cb', wt.DWORD), ('lpReserved', wt.LPSTR), ('lpDesktop', wt.LPSTR),
                ('lpTitle', wt.LPSTR), ('dwX', wt.DWORD), ('dwY', wt.DWORD),
                ('dwXSize', wt.DWORD), ('dwYSize', wt.DWORD), ('dwXCountChars', wt.DWORD),
                ('dwYCountChars', wt.DWORD), ('dwFillAttribute', wt.DWORD), ('dwFlags', wt.DWORD),
                ('wShowWindow', wt.WORD), ('cbReserved2', wt.WORD), ('lpReserved2', ctypes.c_void_p),
                ('hStdInput', wt.HANDLE), ('hStdOutput', wt.HANDLE), ('hStdError', wt.HANDLE)]

class PI(ctypes.Structure):
    _fields_ = [('hProcess', wt.HANDLE), ('hThread', wt.HANDLE), ('pid', wt.DWORD), ('tid', wt.DWORD)]

def rp(h, addr, size):
    b = ctypes.create_string_buffer(size); n = ctypes.c_size_t(0)
    if not k32.ReadProcessMemory(ctypes.c_void_p(h), ctypes.c_void_p(addr), b, size, ctypes.byref(n)):
        return None
    return b.raw[:n.value]

def u32(h, addr):
    d = rp(h, addr, 4)
    return struct.unpack('<I', d)[0] if d and len(d) == 4 else None

def read_bstr(h, addr, maxlen=300):
    p = u32(h, addr)
    if not p or p < 0x10000:
        return None
    ln = u32(h, p - 4)
    if ln is None or ln > maxlen:
        return None
    d = rp(h, p, ln + 2)
    if not d:
        return None
    try:
        return d[:ln].decode('utf-16le', 'replace')
    except Exception:
        return None

GLOBALS = {
    '0x16202B8': 0x16202B8, '0x16202D4': 0x16202D4,
    '0x16203A0': 0x16203A0, '0x16203AC': 0x16203AC,
    '0x16203F4_IsActivated': 0x16203F4, '0x16203F6': 0x16203F6,
    '0x16203FC': 0x16203FC, '0x1620408_LicCode': 0x1620408,
    '0x162040C': 0x162040C, '0x1620410_Feature': 0x1620410,
    '0x1620444': 0x1620444, '0x1620448': 0x1620448,
    '0x1620458': 0x1620458, '0x162048C': 0x162048C,
    '0x1620498': 0x1620498, '0x1624xx': 0x1624F00,
}

exe = sys.argv[1]
waits = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [3, 8, 12]
os.chdir(os.path.dirname(exe))
si = STARTUPINFOA(); si.cb = ctypes.sizeof(si)
pi = PI()
if not k32.CreateProcessW(None, ctypes.c_wchar_p(f'"{exe}"'), None, None, False, 0, None, None,
                          ctypes.byref(si), ctypes.byref(pi)):
    print('CreateProcess failed', ctypes.get_last_error()); sys.exit(1)
h = k32.OpenProcess(0x1F0FFF, False, pi.pid)
print('pid', pi.pid)
t0 = time.time()
for w in waits:
    while time.time() - t0 < w:
        time.sleep(0.1)
    print(f'--- t={time.time()-t0:.1f}s ---')
    for name, addr in GLOBALS.items():
        if name == '0x1624xx':
            continue
        s = read_bstr(h, addr)
        v = u32(h, addr)
        if s is not None and s.strip('\x00'):
            print(f'  {name:24s} BSTR={s!r}')
        else:
            print(f'  {name:24s} dword={v:#x}   hi={u32(h, addr+2)}')
    # doubles for date fields
    for name, addr in [('d_1620428', 0x1620428), ('d_1620430', 0x1620430), ('d_1620438', 0x1620438)]:
        d = rp(h, addr, 8)
        if d:
            print(f'  {name:24s} f64={struct.unpack("<d", d)[0]!r}')
k32.TerminateProcess(ctypes.c_void_p(h), 0)
