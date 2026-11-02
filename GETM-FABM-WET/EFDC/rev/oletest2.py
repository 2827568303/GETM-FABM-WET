import ctypes, ctypes.wintypes as wt, uuid, struct
k32=ctypes.WinDLL('kernel32'); ole32=ctypes.WinDLL('ole32'); oleaut=ctypes.WinDLL('oleaut32')
ole32.OleInitialize(None)
class GUID(ctypes.Structure):
    _fields_=[('Data1',wt.DWORD),('Data2',wt.WORD),('Data3',wt.WORD),('Data4',ctypes.c_ubyte*8)]
def guid(s):
    b=uuid.UUID(s).bytes_le
    g=GUID(); ctypes.memmove(ctypes.byref(g), b, 16); return g
IID_IPicture=guid('{7BF80980-BF32-101A-8BBB-00AA00300CAB}')
IID_IPictureDisp=guid('{7BF80981-BF32-101A-8BBB-00AA00300CAB}')
ole32.CreateStreamOnHGlobal.argtypes=[ctypes.c_void_p, wt.BOOL, ctypes.POINTER(ctypes.c_void_p)]
oleaut.OleLoadPictureEx.argtypes=[ctypes.c_void_p, wt.LONG, wt.DWORD, ctypes.POINTER(GUID), wt.DWORD, wt.DWORD, wt.DWORD, ctypes.POINTER(ctypes.c_void_p)]
oleaut.OleLoadPictureEx.restype=ctypes.c_long
def stream(data):
    p=ctypes.c_void_p(); hr=ole32.CreateStreamOnHGlobal(None, True, ctypes.byref(p))
    vt=ctypes.cast(p, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    Write=ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p, wt.ULONG, ctypes.POINTER(wt.ULONG))(vt[4])
    Seek=ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_longlong, wt.DWORD, ctypes.POINTER(ctypes.c_longlong))(vt[5])
    b=ctypes.create_string_buffer(data); n=wt.ULONG(0); Write(p,b,len(data),ctypes.byref(n)); Seek(p,0,0,None)
    return p
def run(label,data,g,size=None):
    p=stream(data); pp=ctypes.c_void_p()
    hr=oleaut.OleLoadPictureEx(p, size if size else len(data), 0, ctypes.byref(g), 0,0,0, ctypes.byref(pp))
    print(f"{label:34s} len={len(data):5d} size={(size if size else len(data)):5d} hr={hr & 0xffffffff:#010x} pic={pp.value}")
blob=open('dump_1.bin','rb').read()
run('blob IID_IPictureDisp', blob, IID_IPictureDisp)
run('blob IID_IPicture', blob, IID_IPicture)
run('blob IID_IPicture size=21070', blob, IID_IPicture, 21070)
run('payload8 IID_IPicture', blob[8:], IID_IPicture)
