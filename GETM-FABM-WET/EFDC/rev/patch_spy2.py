p='run_spy_fast.py'; s=open(p,encoding='utf-8').read()
s=s.replace("""                print(f'[{time.time()-t0:5.2f}] WIN {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)}')""","""                import ctypes as _c
                class R(ctypes.Structure):
                    _fields_=[('l',wt.LONG),('t',wt.LONG),('r',wt.LONG),('b',wt.LONG)]
                rr=R(); u32.GetWindowRect(h, ctypes.byref(rr))
                print(f'[{time.time()-t0:5.2f}] WIN {c.value!r} {t.value!r} vis={u32.IsWindowVisible(h)} rect=({rr.l},{rr.t},{rr.r},{rr.b}) hwnd={h:#x} pid_owner={u32.GetWindow(h,4)}')""")
open(p,'w',encoding='utf-8').write(s)
print('ok')
