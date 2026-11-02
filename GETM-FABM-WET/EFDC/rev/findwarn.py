import re, struct
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(p,'rb').read(); base=0x400000
for s in (b'are inappropriate', b'You will no longer be able', b'Please contact DS-INTL'):
    idx=[m.start() for m in re.finditer(re.escape(s), d)]
    print(s.decode(), [hex(base+i) for i in idx])
    for i in idx[:2]:
        va=base+i
        pat=struct.pack('<I', va)
        refs=[m.start() for m in re.finditer(re.escape(pat), d)]
        print('   refs:', [hex(base+r) for r in refs][:6])
