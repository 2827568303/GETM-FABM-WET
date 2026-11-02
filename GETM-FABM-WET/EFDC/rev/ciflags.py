import struct
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
d=open(p,'rb').read(); base=0x400000
def rd(va,n=4):
    o=va-base
    return d[o:o+n] if 0<=o and o+n<=len(d) else None
cands=[0x4a3088,0x4a49fc,0x4a6468,0x4a7fa0,0x4a9b28,0x4ab718,0x4ad328,0x4aefd0,0x4b0e20,0x4b2cb0,0x4b6bbc,0x4b8e44,0x4bb150,0x4bd5e8,0x4c24ac,0x4c7378,0x4cd0dc,0x4d5204]
print('candidate  flags       +0x0c typeinfo  +0x1c global')
for ci in cands:
    flags=struct.unpack('<I',rd(ci,4))[0]
    ti=struct.unpack('<I',rd(ci+0x0c,4))[0]
    gl=struct.unpack('<I',rd(ci+0x1c,4))[0]
    tag='FORM' if (flags & 0x00A80000)==0x00A80000 else ''
    print(f'{ci:#08x}  {flags:#010x}  {ti:#010x}    {gl:#010x}  {tag}')
