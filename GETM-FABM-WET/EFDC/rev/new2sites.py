import re, struct
d=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
base=0x400000
pat=bytes([0xFF,0x15,0x14,0x15,0x40,0x00])   # call [0x401514] __vbaNew2
sites=[m.start() for m in re.finditer(re.escape(pat),d)]
print('New2 call sites:', len(sites))
for o in sites[:40]:
    va=base+o
    # look back for push imm32 (info) and push addr
    back=d[max(0,o-24):o]
    imms=[]
    for i in range(len(back)-5):
        if back[i]==0x68:
            v=struct.unpack_from('<I',back,i+1)[0]
            if 0x400000<=v<0x1700000: imms.append(hex(v))
    print(' ', hex(va), 'pushes:', imms)
