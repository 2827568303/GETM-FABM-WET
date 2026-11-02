import re, struct
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(p,'rb').read(); base=0x400000
for s in ('are inappropriate','You will no longer','Please contact DS-INTL','Warning!'):
    u=s.encode('utf-16le')
    idx=[m.start() for m in re.finditer(re.escape(u), d)]
    print(repr(s), [hex(base+i) for i in idx])
    for i in idx[:2]:
        va=base+i
        pat=struct.pack('<I', va)
        refs=[m.start() for m in re.finditer(re.escape(pat), d)]
        print('   ptr refs:', [hex(base+r) for r in refs][:6])
        # also the address of the enclosing descriptor
