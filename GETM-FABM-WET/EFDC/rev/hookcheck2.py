import ctypes, ctypes.wintypes as wt, time, os, pefile
k32=ctypes.WinDLL('kernel32'); psapi=ctypes.WinDLL('psapi')
class SI(ctypes.Structure):
    _fields_=[('cb',wt.DWORD),('a',wt.LPSTR),('b',wt.LPSTR),('c',wt.LPSTR),('x',wt.DWORD),('y',wt.DWORD),('xs',wt.DWORD),('ys',wt.DWORD),('xc',wt.DWORD),('yc',wt.DWORD),('fill',wt.DWORD),('flags',wt.DWORD),('show',wt.WORD),('r2',wt.WORD),('r',ctypes.c_void_p),('h1',wt.HANDLE),('h2',wt.HANDLE),('h3',wt.HANDLE)]
class PI(ctypes.Structure):
    _fields_=[('h',wt.HANDLE),('t',wt.HANDLE),('pid',wt.DWORD),('tid',wt.DWORD)]
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
os.chdir(os.path.dirname(exe)); si=SI(); si.cb=ctypes.sizeof(si); pi=PI()
k32.CreateProcessW(None, ctypes.c_wchar_p('"'+exe+'"'), None,None,False,0,None,None,ctypes.byref(si),ctypes.byref(pi))
time.sleep(3); h=k32.OpenProcess(0x1F0FFF,False,pi.pid)
arr=(ctypes.c_void_p*512)(); need=ctypes.c_size_t(0)
psapi.EnumProcessModulesEx(ctypes.c_void_p(h), ctypes.byref(arr), ctypes.sizeof(arr), ctypes.byref(need), 3)
mods={}
for i in range(need.value//ctypes.sizeof(ctypes.c_void_p)):
    b=ctypes.create_unicode_buffer(520)
    if psapi.GetModuleFileNameExW(ctypes.c_void_p(h), ctypes.c_void_p(arr[i]), b, 520):
        p=b.value; mods[p.lower().split('\\')[-1]+'|'+p]=arr[i]
def rpm(addr,n):
    b=ctypes.create_string_buffer(n); c=ctypes.c_size_t(0)
    k32.ReadProcessMemory(ctypes.c_void_p(h), ctypes.c_void_p(addr), b, n, ctypes.byref(c)); return b.raw[:c.value]
for k,base in mods.items():
    name,path=k.split('|',1)
    if name in ('oleaut32.dll','ole32.dll','msvbvm60.dll','gdi32.dll'):
        print(name, hex(base), path)
        if 'wow64' in path.lower(): continue
        pe=pefile.PE(path, fast_load=True); pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
        exps={e.name.decode():e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
        data=open(path,'rb').read()
        for fn in ('OleLoadPictureEx','OleLoadPicture','CreateStreamOnHGlobal'):
            if fn not in exps: continue
            rva=exps[fn]
            for s in pe.sections:
                if s.VirtualAddress<=rva<s.VirtualAddress+s.Misc_VirtualSize:
                    o=s.PointerToRawData+(rva-s.VirtualAddress); break
            disk=data[o:o+16]; mem=rpm(base+rva,16)
            print(f"   {fn:22s} rva={rva:#08x} disk={disk.hex()} mem={mem.hex()} {'SAME' if disk==mem else 'PATCHED'}")
k32.TerminateProcess(ctypes.c_void_p(h),0)
