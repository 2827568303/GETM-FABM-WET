import struct
for p in (r"C:\Windows\SysWOW64\MSVBVM60.DLL", r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\MSVBVM60.DLL"):
    d=open(p,'rb').read()
    lf=struct.unpack_from('<I',d,0x3C)[0]
    nsec=struct.unpack_from('<H',d,lf+6)[0]
    sizeimg=struct.unpack_from('<I',d,lf+0x18+0x38)[0]
    print(p.split('\\')[-1], 'e_lfanew',hex(lf),'nsec',nsec,'sizeimg',hex(sizeimg),'filelen',len(d))
    for i in range(nsec):
        o=lf+0x18+i*0x28
        name=d[o:o+8].rstrip(b'\x00')
        va,vs,raw,rs=struct.unpack_from('<IIII',d,o+8)
        print('   ',name,hex(va),hex(vs),hex(raw),hex(rs), hex(struct.unpack_from('<I',d,o+36)[0]))
