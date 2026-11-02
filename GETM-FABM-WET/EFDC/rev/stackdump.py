import ctypes, ctypes.wintypes as wt, time, os, struct
k32=ctypes.WinDLL("kernel32"); u32=ctypes.WinDLL("user32")
class SI(ctypes.Structure):
    _fields_=[('cb',wt.DWORD),('a',wt.LPSTR),('b',wt.LPSTR),('c',wt.LPSTR),('x',wt.DWORD),('y',wt.DWORD),('xs',wt.DWORD),('ys',wt.DWORD),('xc',wt.DWORD),('yc',wt.DWORD),('fill',wt.DWORD),('flags',wt.DWORD),('show',wt.WORD),('r2',wt.WORD),('r',ctypes.c_void_p),('h1',wt.HANDLE),('h2',wt.HANDLE),('h3',wt.HANDLE)]
class PI(ctypes.Structure):
    _fields_=[('h',wt.HANDLE),('t',wt.HANDLE),('pid',wt.DWORD),('tid',wt.DWORD)]
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
os.chdir(os.path.dirname(exe)); si=SI(); si.cb=ctypes.sizeof(si); pi=PI()
k32.CreateProcessW(None, ctypes.c_wchar_p('"'+exe+'"'), None,None,False,0,None,None,ctypes.byref(si),ctypes.byref(pi))
print('pid',pi.pid,'tid',pi.tid)
time.sleep(7)
hThread=k32.OpenThread(0x1F03FF, False, pi.tid)
print('thread handle',hThread)
k32.SuspendThread(hThread)
ctx=(ctypes.c_ubyte*716)()
k32.Wow64GetThreadContext(hThread, ctx)
buf=bytes(ctx)
eip=struct.unpack_from('<I',buf,0xB8)[0]; esp=struct.unpack_from('<I',buf,0xC4)[0]; ebp=struct.unpack_from('<I',buf,0xB4)[0]
print(f'EIP={eip:#x} ESP={esp:#x} EBP={ebp:#x}')
mem=(ctypes.c_ubyte*0x20000)()
n=ctypes.c_size_t(0)
k32.ReadProcessMemory(ctypes.c_void_p(pi.h), ctypes.c_void_p(esp), mem, 0x20000, ctypes.byref(n))
data=bytes(mem[:n.value])
print('stack bytes read', n.value)
addrs=[]
for off in range(0, len(data)-4, 4):
    v=struct.unpack_from('<I',data,off)[0]
    if 0x401000<=v<0x1620000:
        addrs.append((esp+off, v))
print('code-like stack words:', len(addrs))
for a,v in addrs[:40]:
    print(f'  stack {a:#010x} -> {v:#010x}')
k32.ResumeThread(hThread); k32.CloseHandle(hThread)
time.sleep(0.2); k32.TerminateProcess(ctypes.c_void_p(pi.h),0)
