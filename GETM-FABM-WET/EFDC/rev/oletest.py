import ctypes, ctypes.wintypes as wt, uuid, struct
k32=ctypes.WinDLL('kernel32'); ole32=ctypes.WinDLL('ole32'); oleaut=ctypes.WinDLL('oleaut32')
ole32.OleInitialize(None)

class GUID(ctypes.Structure):
    _fields_=[('Data1',wt.DWORD),('Data2',wt.WORD),('Data3',wt.WORD),('Data4',ctypes.c_ubyte*8)]
IID_IPictureDisp_GUID = GUID(0x7BF80981,0xBF32,0x101A,(ctypes.c_ubyte*8)(0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB))

ole32.CreateStreamOnHGlobal.argtypes=[ctypes.c_void_p, wt.BOOL, ctypes.POINTER(ctypes.c_void_p)]
ole32.CreateStreamOnHGlobal.restype=ctypes.HRESULT
oleaut.OleLoadPictureEx.argtypes=[ctypes.c_void_p, wt.LONG, wt.DWORD, ctypes.POINTER(GUID), wt.DWORD, wt.DWORD, wt.DWORD, ctypes.POINTER(ctypes.c_void_p)]
oleaut.OleLoadPictureEx.restype=ctypes.HRESULT
oleaut.OleLoadPicture.argtypes=[ctypes.c_void_p, wt.LONG, wt.BOOL, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p)]
oleaut.OleLoadPicture.restype=ctypes.HRESULT

def make_stream(data):
    p=ctypes.c_void_p()
    hr=ole32.CreateStreamOnHGlobal(None, True, ctypes.byref(p))
    assert hr==0, hex(hr & 0xffffffff)
    vt=ctypes.cast(p, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    Write=ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p, wt.ULONG, ctypes.POINTER(wt.ULONG))(vt[4])
    Seek=ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_longlong, wt.DWORD, ctypes.POINTER(ctypes.c_longlong))(vt[5])
    buf=ctypes.create_string_buffer(data)
    n=wt.ULONG(0)
    Write(p, buf, len(data), ctypes.byref(n))
    Seek(p, 0, 0, None)
    return p

def try_load(label, data, ex=True):
    p=make_stream(data)
    pp=ctypes.c_void_p()
    if ex:
        hr=oleaut.OleLoadPictureEx(p, len(data), 0, ctypes.byref(IID_IPictureDisp_GUID), 0,0,0, ctypes.byref(pp))
    else:
        hr=oleaut.OleLoadPicture(p, len(data), False, ctypes.byref(IID_IPictureDisp_GUID), ctypes.byref(pp))
    print(f"{label:28s} len={len(data):5d} hr={hr & 0xffffffff:#010x} pic={pp.value}")

blob=open('dump_1.bin','rb').read()
try_load('whole lt blob', blob)
try_load('payload after 8 bytes', blob[8:])
try_load('payload after 6 bytes', blob[6:])
try_load('whole lt blob (OleLoadPicture)', blob, ex=False)
bmp=open(r'C:\Users\Public\DSI\EEMS8.3\license.bmp','rb').read()
try_load('license.bmp', bmp)
# also save payload as .ico and check GDI+
open('payload.ico','wb').write(blob[8:])

