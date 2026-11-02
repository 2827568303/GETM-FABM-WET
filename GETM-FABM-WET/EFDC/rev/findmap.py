import re, struct
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
d=open(p,'rb').read(); base=0x400000
for s in ('does not map with the license file','does not map','The feature'):
    u=s.encode('utf-16le')
    idx=[m.start() for m in re.finditer(re.escape(u), d)]
    print(repr(s), [hex(base+i) for i in idx])
    for i in idx[:3]:
        va=base+i
        pat=struct.pack('<I',va)
        refs=[m.start() for m in re.finditer(re.escape(pat), d)]
        print('   refs:', [hex(base+r) for r in refs][:6])
