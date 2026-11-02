src=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
s=open(src,'rb').read(); d=bytearray(open(exe,'rb').read())
o=0x81D3E0-0x400000
orig=s[o:o+8]
print('orig bytes:', orig.hex())
print('current   :', d[o:o+8].hex())
d[o:o+8]=orig
open(exe,'wb').write(bytes(d))
print('restored   :', bytes(d[o:o+8]).hex())
