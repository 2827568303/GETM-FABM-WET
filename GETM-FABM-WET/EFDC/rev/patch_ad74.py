exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=bytearray(open(exe,'rb').read())
o=0x156AD74-0x400000
print('before:', d[o:o+6].hex())
assert d[o:o+6]==bytes.fromhex('ff9050020000'), d[o:o+6].hex()
d[o:o+6]=bytes.fromhex('31c0668945c4')   # xor eax,eax ; mov [ebp-0x3c],ax
open(exe,'wb').write(bytes(d))
print('patched 0x156AD74: skip the blocking property call')
