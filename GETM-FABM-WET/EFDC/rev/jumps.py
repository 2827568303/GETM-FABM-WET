import struct
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
d=open(p,'rb').read(); base=0x400000
targets=[0x81CDD5,0x81CDE8,0x81CDBF,0x81CDF7]
for t in targets:
    hits=[]
    for i in range(len(d)-6):
        b=d[i]
        if b==0xE9:
            rel=struct.unpack_from('<i',d,i+1)[0]
            if (base+i+5+rel)&0xffffffff==t: hits.append(base+i)
        elif b==0xEB:
            rel=struct.unpack_from('<b',d,i+1)[0]
            if (base+i+2+rel)&0xffffffff==t: hits.append(base+i)
        elif b==0x0F and d[i+1] in (0x84,0x85):
            rel=struct.unpack_from('<i',d,i+2)[0]
            if (base+i+6+rel)&0xffffffff==t: hits.append(base+i)
    print(hex(t),'jumped from:',[hex(x) for x in hits][:10])
