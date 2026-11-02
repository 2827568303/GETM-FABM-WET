import sys
SRC=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
DST=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\MSVBVM60.DLL"
d=bytearray(open(SRC,'rb').read())
# patch: force picture-load success (EAX=0), keep ret 0x20
off=0x1d761
assert d[off:off+8]==bytes.fromhex('85c00f8ce7830600'), d[off:off+8].hex()
d[off:off+8]=bytes.fromhex('31c09090909090 90'.replace(' ',''))
open(DST,'wb').write(bytes(d))
print('patched and written', len(d))
