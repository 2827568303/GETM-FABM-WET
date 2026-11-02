exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=bytearray(open(exe,'rb').read())
o=0x81D3E0-0x400000
print('before:', d[o:o+8].hex())
assert d[o:o+3]==bytes.fromhex('558bec'), d[o:o+3].hex()
d[o:o+5]=bytes.fromhex('66b80100c3')   # mov ax,1 ; ret
open(exe,'wb').write(bytes(d))
print('patched 0x81D3E0 -> return 1')
