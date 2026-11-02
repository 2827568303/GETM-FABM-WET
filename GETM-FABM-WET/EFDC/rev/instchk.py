import struct,os
p='eems1183_setup.exe'
if os.path.exists(p):
    d=open(p,'rb').read()
    print('size',len(d))
    for pat in (b'Inno Setup',b'Nullsoft',b'InstallShield',b'Setup Factory',b'7z\xbc\xaf\x27\x1c',b'MSCF',b'Wise'):
        i=d.find(pat)
        print(f'  {pat[:16]!r}: {hex(i) if i>=0 else None}')
    print('head', d[:64].hex())
else:
    print('not present')
