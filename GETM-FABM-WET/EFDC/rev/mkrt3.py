import os
src=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
d=bytearray(open(src,'rb').read())
print('size',len(d))
o=0x1D761
print('bytes at RVA 0x1D761:', d[o:o+8].hex())
dst=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC \u5546\u4e1a\u72488.4\MSVBVM60.dll"
if d[o:o+8]==bytes.fromhex('85c00f8ce7830600'):
    d[o:o+8]=bytes.fromhex('8b4d1883210031c0')
    open(dst,'wb').write(bytes(d))
    print('OK patched and written')
else:
    # search the pattern
    pat=bytes.fromhex('85c00f8ce7830600')
    i=d.find(pat)
    print('pattern at',hex(i) if i>=0 else None)
    if i>=0:
        d[i:i+8]=bytes.fromhex('8b4d1883210031c0')
        open(dst,'wb').write(bytes(d))
        print('patched at',hex(i),'and written')
