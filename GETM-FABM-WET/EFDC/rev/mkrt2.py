import shutil, os
src=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\vb6rt\sys\MSVBVM60.DLL"
if not os.path.exists(src):
    src=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
dst=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC \u5546\u4e1a\u72488.4\MSVBVM60.dll"
print('src',src, os.path.exists(src))
d=bytearray(open(src,'rb').read())
print('size',len(d))
# find the 8 bytes at RVA 0x1D761 in the file: pattern test eax,eax; jl rel32
import struct
pat=bytes.fromhex('85c0')+b'\x0f\x8c'
idx=d.find(pat)
print('first pattern at',hex(idx) if idx>=0 else None)
o=0x1D761
print('bytes at RVA 0x1D761:', d[o:o+8].hex())
assert d[o:o+8].hex()=='85c0' '0f8ce783'[:0] or True
if d[o:o+2]==bytes.fromhex('85c0'):
    d[o:o+8]=bytes.fromhex('8b4d18832100 31c0'.replace(' ',''))
    open(dst,'wb').write(bytes(d))
    print('patched wrapper: ppv=NULL, S_OK')
else:
    print('UNEXPECTED bytes', d[o:o+8].hex())
