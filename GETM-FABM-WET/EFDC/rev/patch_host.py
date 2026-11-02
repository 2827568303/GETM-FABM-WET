exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=bytearray(open(exe,'rb').read())
o=0x81F80D-0x400000
print('before:', d[o:o+2].hex())
assert d[o:o+2]==bytes.fromhex('7567'), d[o:o+2].hex()
d[o:o+2]=bytes.fromhex('eb67')
open(exe,'wb').write(bytes(d))
print('patched: 0x81F80D jne -> jmp (skip hostID check)')
