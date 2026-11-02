exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=bytearray(open(exe,'rb').read())
o=(0x4528C4+0x2C)-0x400000
d[o:o+4]=(0x1568180).to_bytes(4,'little')
open(exe,'wb').write(bytes(d))
print('lpSubMain restored ->', hex(int.from_bytes(d[o:o+4],'little')))
