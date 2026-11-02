import re, struct
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(p,'rb').read(); base=0x400000
for name in (b'frmAct_License_Validation', b'frmAct_License_Bypass', b'frmAct_Demo_SignIn', b'frmAct_LicenseManager'):
    idx=[m.start() for m in re.finditer(re.escape(name), d)]
    print(name.decode(), 'at', [hex(base+i) for i in idx])
# find pointers to the first occurrence
if True:
    name=b'frmAct_License_Validation'
    i=d.find(name)
    va=base+i
    print('first VA', hex(va))
    pat=struct.pack('<I', va)
    refs=[m.start() for m in re.finditer(re.escape(pat), d)]
    print('pointers to it:', [hex(base+r) for r in refs][:10])
