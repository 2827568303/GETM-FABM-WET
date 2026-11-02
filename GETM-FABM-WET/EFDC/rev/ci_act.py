import struct
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(p,'rb').read(); base=0x400000
def rd(va,n=4):
    o=va-base
    return d[o:o+n] if 0<=o and o+n<=len(d) else None
def dump(va,n=0x28):
    print('=== ',hex(va))
    for i in range(0,n,4):
        v=struct.unpack('<I', rd(va+i,4))[0]
        extra=''
        if 0x400000<=v<0x1660000:
            b=rd(v,40); t=b.split(b'\x00')[0]
            if len(t)>=4 and all(32<=c<127 for c in t): extra='-> '+t.decode('latin1')
        print(f'  +{i:02x}: {v:#010x} {extra}')
dump(0x4DD92C)
dump(0x4DD8A0,0x10)
print('title form classinfo 0x4D5204 for comparison:')
dump(0x4D5204,0x28)
