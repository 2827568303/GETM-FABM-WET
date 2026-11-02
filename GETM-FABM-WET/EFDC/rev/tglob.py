import re
d=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
base=0x400000
pat=bytes.fromhex('a1b0496201')
offs=[m.start() for m in re.finditer(re.escape(pat),d)]
print('mov eax,[0x16249b0] sites:', len(offs))
import struct
for o in offs[:40]:
    va=base+o
    seg=d[o:o+40]
    calls=re.findall(rb'\xff[\x90\x91\x92\x50\x51\x52\x53\x56\x57](..)', seg)
    offs2=[]
    for c in calls:
        offs2.append(hex(struct.unpack('<H',c)[0]))
    print(hex(va), seg[:24].hex(), 'calls+off:', offs2)
