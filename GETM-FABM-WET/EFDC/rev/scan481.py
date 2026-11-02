import re
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(p,'rb').read()
base=0x400000
pats={b'\x68\xe1\x01\x00\x00':'push 0x1E1', b'\xb8\xe1\x01\x00\x00':'mov eax,0x1E1'}
for pat,name in pats.items():
    offs=[m.start() for m in re.finditer(re.escape(pat), d)]
    print(name, len(offs), [hex(base+o) for o in offs[:30]])
# mov dword ptr [ebp-x], 0x1E1  -> C7 45 xx E1 01 00 00
offs=[m.start() for m in re.finditer(rb'\xc7\x45.\xe1\x01\x00\x00', d, re.S)]
print('mov [ebp-x],0x1E1', len(offs), [hex(base+o) for o in offs[:30]])
