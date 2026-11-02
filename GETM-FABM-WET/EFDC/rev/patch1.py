import re
p='dbg.py'; s=open(p,encoding='utf-8').read()
s=s.replace("""    def arm_all(self):
        mods = self.enum_modules()""","""    def arm_all(self):
        if self.mode == 'none':
            self.w('mode=none: no breakpoints armed')
            return
        mods = self.enum_modules()""")
s=s.replace("""        table = {""","""        if self.mode == 'api_only':
            table = {k: v for k, v in table.items()}
        table = {""")
s=s.replace("""                    self.bp('exe_entry', base + 0x51954)
                    self.bp('CheckLicensing', base + 0x41C4C0)
                    self.bp('ShowExpiredForm?', base + 0x41F020)""","""                    if self.mode != 'none':
                        self.bp('exe_entry', base + 0x51954)
                        if self.mode == 'all':
                            self.bp('CheckLicensing', base + 0x41C4C0)
                            self.bp('ShowExpiredForm?', base + 0x41F020)""")
s=s.replace("""    def __init__(self, exe, logpath, timeout=60):""","""    def __init__(self, exe, logpath, timeout=60, mode='all'):""")
s=s.replace("""        self.base = None""","""        self.base = None
        self.mode = mode""")
s=s.replace("""    d = Dbg(exe, logp, timeout=float(sys.argv[2]) if len(sys.argv) > 2 else 50)""","""    mode = sys.argv[3] if len(sys.argv) > 3 else 'all'
    d = Dbg(exe, logp, timeout=float(sys.argv[2]) if len(sys.argv) > 2 else 50, mode=mode)""")
open(p,'w',encoding='utf-8').write(s)
print("ok")
