import struct
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read(); base=0x400000
def calls_to(target):
    res=[]
    for i in range(len(d)-5):
        if d[i]==0xE8:
            rel=struct.unpack_from('<i', d, i+1)[0]
            va=base+i
            if (va+5+rel)&0xffffffff==target:
                res.append(va)
    return res
for t,name in ((0x156ab70,'0x156AB70 (creates 0x48FE70 obj)'),(0x156acc0,'0x156ACC0 (title form)'),(0x156b030,'0x156B030')):
    r=calls_to(t)
    print(name,'called from:', len(r), [hex(x) for x in r][:12])
