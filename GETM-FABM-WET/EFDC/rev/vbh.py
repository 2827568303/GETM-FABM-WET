import struct
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read(); base=0x400000
def rd(va,n=4):
    o=va-base
    return d[o:o+n] if 0<=o and o+n<=len(d) else None
def s_at(va,n=64):
    b=rd(va,n)
    if not b: return None
    a=b.split(b'\x00')[0]
    if len(a)>=3 and all(32<=c<127 for c in a): return a.decode('latin1')
    try:
        s=b.decode('utf-16le','ignore').split('\x00')[0]
        if len(s)>=3 and all(32<=ord(c)<127 for c in s): return 'U:'+s
    except: pass
    return None
# entry point: find push <VBHeader> at 0x451954
print('entry bytes:', rd(0x451954,12).hex())
vbh=struct.unpack('<I', rd(0x451955,4))[0]
print('VBHeader VA:', hex(vbh), 'sig:', rd(vbh,4))
for off in range(0,0x60,4):
    v=struct.unpack('<I', rd(vbh+off,4))[0]
    print(f'  VBHeader+{off:02x} = {v:#010x}')
