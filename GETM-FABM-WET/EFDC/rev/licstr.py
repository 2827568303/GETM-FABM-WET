import re
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read()
for pat in (b'license.bmp', b'.bmp', b'license', b'License', b'.lic', b'Rijndael', b'CRijndael'):
    idxs=[m.start() for m in re.finditer(re.escape(pat), d)]
    print(f'{pat!r:16} count={len(idxs)} first5={[hex(i) for i in idxs[:5]]}')
