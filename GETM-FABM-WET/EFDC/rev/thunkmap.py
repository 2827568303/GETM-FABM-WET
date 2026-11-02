import ctypes, ctypes.wintypes as wt, time, sys, os, struct, subprocess, pefile
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
k32 = ctypes.WinDLL('kernel32', use_last_error=True)
psapi = ctypes.WinDLL('psapi', use_last_error=True)

class STARTUPINFOA(ctypes.Structure):
    _fields_ = [('cb', wt.DWORD), ('lpReserved', wt.LPSTR), ('lpDesktop', wt.LPSTR),
                ('lpTitle', wt.LPSTR), ('dwX', wt.DWORD), ('dwY', wt.DWORD),
                ('dwXSize', wt.DWORD), ('dwYSize', wt.DWORD), ('dwXCountChars', wt.DWORD),
                ('dwYCountChars', wt.DWORD), ('dwFillAttribute', wt.DWORD), ('dwFlags', wt.DWORD),
                ('wShowWindow', wt.WORD), ('cbReserved2', wt.WORD), ('lpReserved2', ctypes.c_void_p),
                ('hStdInput', wt.HANDLE), ('hStdOutput', wt.HANDLE), ('hStdError', wt.HANDLE)]

class PI(ctypes.Structure):
    _fields_ = [('hProcess', wt.HANDLE), ('hThread', wt.HANDLE), ('pid', wt.DWORD), ('tid', wt.DWORD)]

exe = sys.argv[1]
os.chdir(os.path.dirname(exe))
si = STARTUPINFOA(); si.cb = ctypes.sizeof(si)
pi = PI()
if not k32.CreateProcessW(None, ctypes.c_wchar_p(f'"{exe}"'), None, None, False, 0, None, None,
                          ctypes.byref(si), ctypes.byref(pi)):
    print('CreateProcess failed', ctypes.get_last_error()); sys.exit(1)
print('pid', pi.pid)
time.sleep(4)

h = k32.OpenProcess(0x1F0FFF, False, pi.pid)
def rp(hp, addr, size):
    b = ctypes.create_string_buffer(size); n = ctypes.c_size_t(0)
    if not k32.ReadProcessMemory(ctypes.c_void_p(hp), ctypes.c_void_p(addr), b, size, ctypes.byref(n)):
        return None
    return b.raw[:n.value]
def u32(hp, addr):
    d = rp(hp, addr, 4); return struct.unpack('<I', d)[0] if d and len(d)==4 else None

arr = (ctypes.c_void_p*1024)(); need = ctypes.c_size_t(0)
psapi.EnumProcessModulesEx(ctypes.c_void_p(h), ctypes.byref(arr), ctypes.sizeof(arr), ctypes.byref(need), 3)
mods = {}
for i in range(need.value//ctypes.sizeof(ctypes.c_void_p)):
    buf = ctypes.create_unicode_buffer(520)
    if psapi.GetModuleFileNameExW(ctypes.c_void_p(h), ctypes.c_void_p(arr[i]), buf, 520):
        mods[buf.value.lower().split('\\')[-1]] = arr[i]
print({k: hex(v) for k, v in mods.items()})

vm = mods.get('msvbvm60.dll')
app = mods.get('efdc_explorer8.4.exe')
# export map of msvbvm60 from disk
pe = pefile.PE(r'C:\Windows\SysWOW64\MSVBVM60.DLL', fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
name_by_rva = {}
for e in pe.DIRECTORY_ENTRY_EXPORT.symbols:
    if e.name:
        name_by_rva.setdefault(e.address, e.name.decode())
    else:
        name_by_rva.setdefault(e.address, f'ord{e.ordinal}')
vm_size = pe.OPTIONAL_HEADER.SizeOfImage
print('msvbvm60 base', hex(vm), 'size', hex(vm_size), 'app base', hex(app))

# app thunk table: first 0x900 bytes of .text
th = rp(h, app + 0x1000, 0x900)
out = []
for i in range(0, len(th) - 3, 4):
    val = struct.unpack_from('<I', th, i)[0]
    va = app + 0x1000 + i
    tag = '?'
    if vm <= val < vm + vm_size:
        rva = val - vm
        nm = name_by_rva.get(rva)
        tag = f'msvbvm60+{rva:#07x} {nm or ""}'
    else:
        # other module?
        for k, b in mods.items():
            if b <= val < b + 0x800000:
                tag = k
                break
    out.append((va, val, tag))
with open('thunks.txt', 'w', encoding='utf-8') as f:
    for va, val, tag in out:
        f.write(f'{va:#010x} -> {val:#010x}  {tag}\n')
print('wrote thunks.txt', len(out))
k32.TerminateProcess(ctypes.c_void_p(h), 0)
