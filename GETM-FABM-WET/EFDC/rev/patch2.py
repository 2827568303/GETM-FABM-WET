p='dbg.py'; s=open(p,encoding='utf-8').read()
s=s.replace("""                    else:
                        self.w(f'EXC code={exc_code:#010x} addr={site:#010x} first={first}')
                        if exc_code == 0xC0000005:
                            status = DBG_EXCEPTION_NOT_HANDLED""","""                    else:
                        self.w(f'EXC code={exc_code:#010x} addr={site:#010x} first={first}')
                        status = DBG_EXCEPTION_NOT_HANDLED   # let the app's own SEH see it""")
open(p,'w',encoding='utf-8').write(s)
print('ok')
