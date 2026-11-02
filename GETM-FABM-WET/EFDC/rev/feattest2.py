import ctypes, ctypes.wintypes as wt, time, os, re, shutil
k32 = ctypes.WinDLL("kernel32"); u32 = ctypes.WinDLL("user32")
WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


class SI(ctypes.Structure):
    _fields_ = [('cb', wt.DWORD), ('a', wt.LPSTR), ('b', wt.LPSTR), ('c', wt.LPSTR), ('x', wt.DWORD), ('y', wt.DWORD),
                ('xs', wt.DWORD), ('ys', wt.DWORD), ('xc', wt.DWORD), ('yc', wt.DWORD), ('fill', wt.DWORD),
                ('flags', wt.DWORD), ('show', wt.WORD), ('r2', wt.WORD), ('r', ctypes.c_void_p),
                ('h1', wt.HANDLE), ('h2', wt.HANDLE), ('h3', wt.HANDLE)]


class PI(ctypes.Structure):
    _fields_ = [('h', wt.HANDLE), ('t', wt.HANDLE), ('pid', wt.DWORD), ('tid', wt.DWORD)]


exe = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
ini = r"C:\Users\Public\DSI\EEMS8.3\EEMS.ini"
orig = open(ini, encoding='utf-8', errors='replace').read()

FEATURES = ['EE_MULTI_TRIAL_8_0', 'EE_MULTI_TRIAL_8_4', 'EE_TRIAL_8_0', 'EEMS_VERSIONDATE']

for feat in FEATURES:
    text = re.sub(r'^FeatureName=.*$', 'FeatureName=' + feat, orig, flags=re.M)
    open(ini, 'w', encoding='utf-8').write(text)
    si = SI(); si.cb = ctypes.sizeof(si); pi = PI()
    k32.CreateProcessW(None, ctypes.c_wchar_p('"' + exe + '"'), None, None, False, 0, None,
                       os.path.dirname(exe), ctypes.byref(si), ctypes.byref(pi))
    t0 = time.time(); seen = set(); exited = None
    while time.time() - t0 < 14:
        def cb(h, lp):
            p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
            if p.value == pi.pid:
                c = ctypes.create_unicode_buffer(64); u32.GetClassNameW(h, c, 64)
                t = ctypes.create_unicode_buffer(200); u32.GetWindowTextW(h, t, 200)
                seen.add((c.value, t.value, u32.IsWindowVisible(h)))
            return True
        u32.EnumWindows(WNDENUMPROC(cb), 0)
        ec = wt.DWORD(0); k32.GetExitCodeProcess(ctypes.c_void_p(pi.h), ctypes.byref(ec))
        if ec.value != 259:
            exited = ec.value; break
        time.sleep(0.3)
    if exited is None:
        k32.TerminateProcess(ctypes.c_void_p(pi.h), 0)
    print(f'--- {feat}: ' + ('exited ' + hex(exited) if exited is not None else 'STILL RUNNING'))
    for c, t, v in sorted(seen):
        print(f'      {c!r} {t!r} vis={v}')

open(ini, 'w', encoding='utf-8').write(orig)
print('INI restored')

