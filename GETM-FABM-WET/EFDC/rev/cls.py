import struct
d=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
base=0x400000
def rd(va,n=4):
    o=va-base
    if o<0 or o+n>len(d): return None
    return d[o:o+n]
def str_at(va, n=64):
    b=rd(va,n)
    if not b: return None
    # ascii
    a=b.split(b'\x00')[0]
    if len(a)>=3 and all(32<=c<127 for c in a): return a.decode('latin1')
    # utf16
    try:
        s=b.decode('utf-16le','ignore').split('\x00')[0]
        if len(s)>=3 and all(32<=ord(c)<127 for c in s): return 'U:'+s
    except: pass
    return None
for info in (0x4EB84C,0x4EA944,0x4F9F3C,0x4FACDC,0x4F3B90,0x4F3BC0,0x454C64,0x4D5204,0x4A7FA0):
    print(f'=== info {info:#x} ===')
    for i in range(0,0x20,4):
        v=struct.unpack('<I', rd(info+i,4))[0]
        s=str_at(v)
        print(f'   +{i:02x}: {v:#010x} {s or ""}')
