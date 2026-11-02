src=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
d=bytearray(open(src,'rb').read())
o=0x1D761
assert d[o:o+8]==bytes.fromhex('85c00f8ce7830600')
d[o:o+8]=bytes.fromhex('8b4d1883210031c0')
open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\MSVBVM60_nullpic.dll","wb").write(bytes(d))
print('written rev\\MSVBVM60_nullpic.dll')
