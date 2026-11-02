exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=bytearray(open(exe,'rb').read())
o=0x81D3E0-0x400000
print('current:', d[o:o+8].hex())
d[o:o+5]=bytes.fromhex('558bec83ec')   # restore prologue bytes (push ebp; mov ebp,esp; sub esp,..)
d[o+3]=0x14                            # sub esp,0x14
open(exe,'wb').write(bytes(d))
print('restored:', d[o:o+8].hex())
