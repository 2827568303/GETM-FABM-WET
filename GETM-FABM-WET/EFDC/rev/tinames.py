import struct
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read(); base=0x400000
def rd(va,n=4):
    o=va-base
    return d[o:o+n] if 0<=o and o+n<=len(d) else None
def cstr(va,n=40):
    b=rd(va,n)
    if not b: return None
    t=b.split(b'\x00')[0]
    if len(t)>=4 and all(32<=c<127 for c in t): return t.decode('latin1')
    return None
# scan 0x7F0000-0x800000 for dwords pointing into name table 0x4E0000-0x520000
hits={}
for va in range(0x7F0000,0x800000,4):
    b=rd(va,4)
    if not b: continue
    v=struct.unpack('<I',b)[0]
    if 0x4E0000<=v<0x530000:
        s=cstr(v)
        if s and ('frm' in s or 'Form' in s or 'Explorer' in s):
            hits[va]=s
print('name-pointer hits:', len(hits))
for va,s in list(hits.items())[:40]:
    print(f'  {va:#08x} -> {s}')
