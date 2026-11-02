exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=bytearray(open(exe,'rb').read())
for va in (0x81D4D7,0x81D51B,0x81D689,0x83CAB3):
    o=va-0x400000
    print(hex(va),'before:',d[o:o+5].hex())
    if d[o]==0xE8:
        d[o:o+5]=bytes.fromhex('9090909090')
open(exe,'wb').write(bytes(d))
print('NOPed 4 warning-building calls')
