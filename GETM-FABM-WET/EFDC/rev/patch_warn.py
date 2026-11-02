exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=bytearray(open(exe,'rb').read())
for va,old,new in ((0x81D4D5,'7505','eb05'),):
    o=va-0x400000
    print(hex(va),'before:',d[o:o+2].hex())
    assert d[o:o+2]==bytes.fromhex(old), d[o:o+2].hex()
    d[o:o+2]=bytes.fromhex(new)
open(exe,'wb').write(bytes(d))
print('patched: always skip license warning at 0x81D4D5')
