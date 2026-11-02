p='probe.py'; s=open(p,encoding='utf-8').read()
s=s.replace("""WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)""","""WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
AUTOCLOSE = ('--noclose' not in sys.argv)
BM_CLICK = 0x00F5
WM_COMMAND = 0x0111
IDOK = 1""")
s=s.replace("""    for h, c, t, kids in w:
        key = (c, t, tuple(kids))""","""    for h, c, t, kids in w:
        key = (c, t, tuple(kids))
        if AUTOCLOSE and c == '#32770':
            clicked = False
            for kh, kc, kt in kids2:
                pass""")
s=s.replace("""            for kc, kt in kids:
                print(f'          child {kc!r}: {kt!r}')""","""            for kc, kt in kids:
                print(f'          child {kc!r}: {kt!r}')
            if AUTOCLOSE:
                u32.PostMessageW(h, WM_COMMAND, IDOK, 0)
                print(f'          -> sent IDOK (auto-dismiss)')""")
open(p,'w',encoding='utf-8').write(s)
print('ok')
