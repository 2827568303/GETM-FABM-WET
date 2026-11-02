import struct
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
d=open(p,'rb').read(); base=0x400000
def rd(va,n=4):
    o=va-base
    return d[o:o+n] if 0<=o and o+n<=len(d) else None
def s_at(va,n=80):
    b=rd(va,n)
    if not b: return None
    t=b.split(b'\x00')[0]
    if len(t)>=4 and all(32<=c<127 for c in t): return t.decode('latin1')
    try:
        u=b.decode('utf-16le','ignore').split('\x00')[0]
        if len(u)>=4 and all(32<=ord(c)<127 for c in u): return 'U:'+u
    except: pass
    return None
for ci in (0x4a6468,0x4d5204):
    print('=== class info', hex(ci))
    for i in range(0,0x28,4):
        v=struct.unpack('<I',rd(ci+i,4))[0]
        extra=s_at(v) if 0x400000<=v<0x1660000 else ''
        print(f'   +{i:02x}: {v:#010x} {extra or ""}')
