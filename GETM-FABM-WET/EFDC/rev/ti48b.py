import struct
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read(); base=0x400000
def rd(va,n=4):
    o=va-base
    return d[o:o+n] if 0<=o and o+n<=len(d) else None
for va in (0x7F5664,):
    print('=== ',hex(va))
    for i in range(0,0x20,4):
        v=struct.unpack('<I', rd(va+i,4))[0]
        b=rd(v,40) if 0x400000<=v<0x1620000 else None
        s=''
        if b:
            t=b.split(b'\x00')[0]
            if len(t)>=4 and all(32<=c<127 for c in t): s=t.decode('latin1')
            else:
                try:
                    u=b.decode('utf-16le','ignore').split('\x00')[0]
                    if len(u)>=3: s='U:'+u
                except: pass
        print(f'  +{i:02x}: {v:#010x} {s}')
