p='probe.py'; s=open(p,encoding='utf-8').read()
s=s.replace("""            if AUTOCLOSE:
                u32.PostMessageW(h, WM_COMMAND, IDOK, 0)
                print(f'          -> sent IDOK (auto-dismiss)')""","""            if AUTOCLOSE:
                def cb3(h2, lp2):
                    c = ctypes.create_unicode_buffer(64)
                    u32.GetClassNameW(h2, c, 64)
                    if c.value == 'Button':
                        u32.PostMessageW(h2, BM_CLICK, 0, 0)
                    return True
                u32.EnumChildWindows(h, WNDENUMPROC(cb3), 0)
                print(f'          -> clicked OK (auto-dismiss)')""")
open(p,'w',encoding='utf-8').write(s)
print('ok')
