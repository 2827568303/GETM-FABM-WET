exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=bytearray(open(exe,'rb').read())
o=0x81CA1F-0x400000
print('current 0x81CA1F:', d[o:o+5].hex())
d[o:o+5]=bytes.fromhex('e8bc090000')   # call 0x81D3E0 (FNO check)
open(exe,'wb').write(bytes(d))
print('restored FNO call at 0x81CA1F')
