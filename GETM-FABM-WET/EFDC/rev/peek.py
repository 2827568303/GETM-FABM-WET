import struct
EXE=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(EXE,'rb').read()
for va in (0x81CA1F,0x822450,0x81CA50,0x81CA55,0x81CA58,0x81CA5E,0x81CA62):
    o=va-0x400000
    print(f"{va:#08x}: {d[o:o+12].hex()}")
