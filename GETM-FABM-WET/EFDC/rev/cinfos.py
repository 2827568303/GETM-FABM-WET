import struct
d=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
base=0x400000
pat=struct.pack('<I',0x004DD8A0)
offs=[]; i=d.find(pat)
while i>=0:
    offs.append(i); i=d.find(pat,i+1)
infos=[]
for o in offs:
    va=base+o
    ci=va-4
    if 0x4A0000 < ci < 0x510000:
        infos.append(ci)
print('class info candidates:', len(infos))
print([hex(x) for x in infos[:60]])
