import struct
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read(); base=0x400000
def rd(va,n=4):
    o=va-base
    return d[o:o+n] if 0<=o and o+n<=len(d) else None
def show(va,n=0x28):
    print('=== ',hex(va))
    for i in range(0,n,4):
        v=struct.unpack('<I', rd(va+i,4))[0]
        print(f'  +{i:02x}: {v:#010x}')
show(0x48FE70,0x30)
ti=struct.unpack('<I', rd(0x48FE70+0x0C,4))[0]
print('typeinfo guess:',hex(ti))
if 0x401000<=ti<0x1620000:
    show(ti,0x20)
    # search for a name pointer nearby
    for k in range(0,0x40,4):
        v=struct.unpack('<I', rd(ti+k,4))[0]
        if 0x4E0000<=v<0x520000:
            b=rd(v,64)
            s=b.split(b'\x00')[0]
            print('   ptr at +%02x ->'%k, v, s[:40])
