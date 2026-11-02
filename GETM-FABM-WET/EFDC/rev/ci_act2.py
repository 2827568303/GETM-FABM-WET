import struct
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(p,'rb').read(); base=0x400000
def rd(va,n=4):
    o=va-base
    return d[o:o+n] if 0<=o and o+n<=len(d) else None
for va in (0x4EA348,0x4DFFA4):
    print('=== ',hex(va))
    for i in range(0,0x30,4):
        v=struct.unpack('<I', rd(va+i,4))[0]
        print(f'  +{i:02x}: {v:#010x}')
