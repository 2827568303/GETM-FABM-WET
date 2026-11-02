p='run_spy45.py'; s=open(p,encoding='utf-8').read()
s=s.replace("""                print(f'[{time.time()-t0:5.2f}] WIN {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)}')""","""                print(f'[{time.time()-t0:5.2f}] WIN {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)}')
                if c.value == '#32770':
                    def cb2(ch, lp2):
                        cc = ctypes.create_unicode_buffer(80); u32.GetClassNameW(ch, cc, 80)
                        tt = ctypes.create_unicode_buffer(512); u32.GetWindowTextW(ch, tt, 512)
                        if tt.value.strip():
                            print(f'      child {cc.value!r}: {tt.value!r}')
                        return True
                    u32.EnumChildWindows(h, WNDENUMPROC(cb2), 0)""")
open(p,'w',encoding='utf-8').write(s)
print('patched run_spy')
