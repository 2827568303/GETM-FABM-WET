import os
exe=os.path.join(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC", "EFDC \u5546\u4e1a\u72488.4".encode().decode(), "EFDC_Explorer8.4.exe")
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC \u5546\u4e1a\u72488.4\EFDC_Explorer8.4.exe"
p=p.encode('utf-8').decode('unicode_escape')
print('exists', os.path.exists(p))
d=bytearray(open(p,'rb').read())
o=0x81F80D-0x400000
print('current:', d[o:o+2].hex())
if d[o:o+2]==bytes.fromhex('7567'):
    d[o:o+2]=bytes.fromhex('eb67')
    open(p,'wb').write(bytes(d))
    print('patched ->', bytes(d[o:o+2]).hex())
else:
    print('already patched or different')
