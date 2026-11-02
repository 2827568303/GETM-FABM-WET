import re, struct
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDCPlus_084_OMP_180718.exe"
d=open(p,'rb').read()
print('size', len(d), 'head', d[:16])
for pat in (b'MSCOMCTL', b'mscomctl', b'MSCF', b'Inno', b'Nullsoft', b'InstallShield', b'7z\xbc\xaf\x27\x1c'):
    print(pat[:12], d.find(pat))
