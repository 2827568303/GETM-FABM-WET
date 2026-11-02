p='fr2.py'; s=open(p,encoding='utf-8').read()
s=s.replace("""            if b.value == '#32770':
                u32.PostMessageW(h, 0x0111, 1, 0)
                hits.append(h)""","""            if b.value == '#32770':
                def cb2(h2, lp2):
                    cb2_ = ctypes.create_unicode_buffer(64)
                    u32.GetClassNameW(h2, cb2_, 64)
                    if cb2_.value == 'Button':
                        u32.PostMessageW(h2, 0x00F5, 0, 0)   # BM_CLICK
                    return True
                u32.EnumChildWindows(h, WNDENUMPROC(cb2), 0)
                hits.append(h)""")
open(p,'w',encoding='utf-8').write(s)
print('ok')
