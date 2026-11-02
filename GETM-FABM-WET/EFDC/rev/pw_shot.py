import ctypes, ctypes.wintypes as wt, subprocess, os, time
from PIL import Image

EXE = r"C:\EFDC84_RUN\EFDC_Explorer8.4.pristine.exe"
OUT = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\pw_shot.png"

u32 = ctypes.WinDLL("user32", use_last_error=True)
g32 = ctypes.WinDLL("gdi32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
u32.PrintWindow.argtypes = [wt.HWND, wt.HDC, ctypes.c_uint]
E = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def cls(h):
    b = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, b, 256); return b.value


proc = subprocess.Popen([EXE], cwd=os.path.dirname(EXE))
t0 = time.time()
time.sleep(5.0)

target = []

def cb(h, l):
    p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
    if p.value == proc.pid and cls(h).startswith("ThunderRT6Form"):
        target.append(h)
    return True
u32.EnumWindows(E(cb), 0)
print("targets:", [hex(h) for h in target], flush=True)

if target:
    h = target[0]
    r = wt.RECT(); u32.GetWindowRect(h, ctypes.byref(r))
    w, hh = r.right - r.left, r.bottom - r.top
    print("rect", w, hh, flush=True)
    hdc = u32.GetWindowDC(h)
    mdc = g32.CreateCompatibleDC(hdc)
    bmp = g32.CreateCompatibleBitmap(hdc, w, hh)
    g32.SelectObject(mdc, bmp)
    ok = u32.PrintWindow(h, mdc, 2)
    print("PrintWindow ->", ok, flush=True)

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [("biSize", wt.DWORD), ("biWidth", ctypes.c_long), ("biHeight", ctypes.c_long),
                    ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
                    ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", ctypes.c_long), ("biYPelsPerMeter", ctypes.c_long),
                    ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD)]

    bi = BITMAPINFOHEADER()
    bi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bi.biWidth = w
    bi.biHeight = -hh
    bi.biPlanes = 1
    bi.biBitCount = 32
    bi.biCompression = 0
    buf = ctypes.create_string_buffer(w * hh * 4)
    g32.GetDIBits(mdc, bmp, 0, hh, buf, ctypes.byref(bi), 0)
    img = Image.frombuffer("RGBA", (w, hh), buf, "raw", "BGRA", 0, 1)
    img.convert("RGB").save(OUT)
    print("saved", OUT, img.size, flush=True)

subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)], capture_output=True)
