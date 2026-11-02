exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=bytearray(open(exe,'rb').read())
o=(0x4528C4+0x2C)-0x400000
print('lpSubMain bytes:', d[o:o+4].hex(), hex(int.from_bytes(d[o:o+4],'little')))
d[o:o+4]=b'\x00\x00\x00\x00'
open(exe,'wb').write(bytes(d))
print('lpSubMain -> 0 (try startup form)')
