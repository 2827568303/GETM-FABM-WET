import struct
d=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
base=0x400000
new2=bytes([0xFF,0x15,0x14,0x15,0x40,0x00])
cands=[0x4a3088,0x4a49fc,0x4a6468,0x4a7fa0,0x4a9b28,0x4ab718,0x4ad328,0x4aefd0,0x4b0e20,0x4b2cb0,0x4b6bbc,0x4b8e44,0x4bb150,0x4bd5e8,0x4c24ac,0x4c7378,0x4cd0dc,0x4d5204]
for ci in cands:
    pat=b'\x68'+struct.pack('<I',ci)
    hits=[]
    i=d.find(pat)
    while i>=0:
        # check whether a New2 call follows within 16 bytes
        seg=d[i:i+24]
        if new2 in seg:
            hits.append(base+i)
        i=d.find(pat,i+1)
    print(hex(ci), 'New2 sites:', [hex(h) for h in hits][:6])
