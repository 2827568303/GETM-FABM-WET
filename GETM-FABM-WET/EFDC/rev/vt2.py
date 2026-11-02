import struct
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read(); base=0x400000
def rd(va,n=4):
    o=va-base
    return d[o:o+n] if 0<=o and o+n<=len(d) else None
vt=0x4F43F0
print('title form vtable @', hex(vt))
for i in range(0,72):
    v=struct.unpack('<I', rd(vt+i*4,4))[0]
    mark=' <-- code' if 0x401000<=v<0x1620000 else ''
    print(f'  [{i:02d}] {v:#010x}{mark}')
