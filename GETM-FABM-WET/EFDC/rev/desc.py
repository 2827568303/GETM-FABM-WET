import struct
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read(); base=0x400000
def rd(va,n=4):
    o=va-base
    return d[o:o+n] if 0<=o and o+n<=len(d) else None
def s_at(va,n=40):
    b=rd(va,n)
    if not b: return None
    a=b.split(b'\x00')[0]
    if len(a)>=4 and all(32<=c<127 for c in a): return a.decode('latin1')
    return None
for va in (0x507080,0x507D08):
    print('=== ',hex(va))
    for i in range(0,0x40,4):
        v=struct.unpack('<I', rd(va+i,4))[0]
        s=s_at(v)
        print(f'  +{i:02x}: {v:#010x} {s or ""}')
