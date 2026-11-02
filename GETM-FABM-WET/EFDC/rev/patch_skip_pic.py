import shutil, os
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=bytearray(open(exe,'rb').read())
def off(va): return va-0x400000
# 1) our previous P1 patches
o=off(0x81CA1F)
print('81CA1F before:', d[o:o+5].hex())
d[o:o+5]=bytes.fromhex('9090909090')
o=off(0x822450)
print('822450 before:', d[o:o+5].hex())
d[o:o+5]=bytes.fromhex('b001c21000')
# 2) NEW: skip form.Picture read at 0x156AD74 (call [eax+0x250])
o=off(0x156AD74)
print('156AD74 before:', d[o:o+6].hex())
assert d[o:o+6]==bytes.fromhex('ff9050020000'), d[o:o+6].hex()
d[o:o+6]=bytes.fromhex('31c0668945c4')
open(exe,'wb').write(bytes(d))
print('patched: skip Picture getter at 0x156AD74')
