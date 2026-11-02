import struct
d=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC_Explorer8.4.exe",'rb').read()
base=0x400000
def rd(va,n=4):
    o=va-base
    if o<0 or o+n>len(d): return None
    return d[o:o+n]
def s_at(va,n=48):
    b=rd(va,n)
    if not b: return None
    a=b.split(b'\x00')[0]
    if len(a)>=3 and all(32<=c<127 for c in a): return a.decode('latin1')
    try:
        s=b.decode('utf-16le','ignore').split('\x00')[0]
        if len(s)>=3: return 'U:'+s
    except: pass
    return None
for ti in (0x7F22A0,0x7F24E0,0x7F2920,0x7F3080):
    print('=== typeinfo?', hex(ti))
    for i in range(0,0x40,4):
        v=struct.unpack('<I', rd(ti+i))[0]
        s=s_at(v)
        print(f'  +{i:02x}: {v:#010x} {s or ""}')
