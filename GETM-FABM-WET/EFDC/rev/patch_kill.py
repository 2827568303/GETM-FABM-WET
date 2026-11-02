exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=bytearray(open(exe,'rb').read())
o=0x81D991-0x400000
print('before:', d[o:o+6].hex())
assert d[o:o+6]==bytes.fromhex('ff1574134000'), d[o:o+6].hex()
d[o:o+6]=bytes.fromhex('909090909090')
open(exe,'wb').write(bytes(d))
print('patched: Kill at 0x81D991 -> NOP')
