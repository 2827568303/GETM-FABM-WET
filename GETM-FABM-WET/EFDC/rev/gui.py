import struct
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read(); base=0x400000
def rd(va,n=4):
    o=va-base
    return d[o:o+n] if 0<=o and o+n<=len(d) else None
gui=0x4BFBBC
print('GUI table first 0x120 bytes:')
for i in range(0,0x120,4):
    v=struct.unpack('<I', rd(gui+i,4))[0]
    print(f'  +{i:03x}: {v:#010x}')
