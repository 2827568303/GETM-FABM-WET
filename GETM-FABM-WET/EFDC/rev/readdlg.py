import ctypes, ctypes.wintypes as wt
u32=ctypes.WinDLL("user32")
ENUMPROC=ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
found=[]
def cb(h,lp):
    c=ctypes.create_unicode_buffer(80); u32.GetClassNameW(h,c,80)
    t=ctypes.create_unicode_buffer(400); u32.GetWindowTextW(h,t,400)
    if c.value=='#32770':
        found.append((h,t.value))
        def cb2(ch,lp2):
            cc=ctypes.create_unicode_buffer(80); u32.GetClassNameW(ch,cc,80)
            tt=ctypes.create_unicode_buffer(1000); u32.GetWindowTextW(ch,tt,1000)
            if tt.value.strip(): print(f'   child {cc.value!r}: {tt.value!r}')
            return True
        u32.EnumChildWindows(h, ENUMPROC(cb2), 0)
    return True
u32.EnumWindows(ENUMPROC(cb),0)
print('dialogs:', [(hex(h),t) for h,t in found])
