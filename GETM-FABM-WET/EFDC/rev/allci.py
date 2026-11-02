import struct
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
d=open(p,'rb').read(); base=0x400000
cands=[]
# scan for class-info pattern: +0x04 == 0x4DD8A0, +0x10 == 0xFFFFFFFF
pat=struct.pack('<I',0x004DD8A0)
i=d.find(pat)
while i>=0:
    ci=base+(i-4)
    if 0x400000 < ci < 0x1700000:
        flags,shared,zero,ti,ff,zero2,ptr,gl=struct.unpack_from('<8I', d, i-4)
        if ff==0xFFFFFFFF and shared==0x004DD8A0 and ptr>0x400000 and gl>0x1600000:
            cands.append((ci,flags,ti,gl))
    i=d.find(pat,i+1)
print('total class infos:', len(cands))
forms=[c for c in cands if (c[1] & 0x00A00000)==0x00A00000 or (c[1] & 0x00B00000)==0x00B00000]
print('form-like:', len(forms))
for ci,flags,ti,gl in forms:
    print(f'  {ci:#08x} flags={flags:#010x} ti={ti:#010x} global={gl:#010x}')
