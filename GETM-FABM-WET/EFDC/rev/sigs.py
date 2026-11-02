for f in ('eems1183_setup.exe','vb6rtlib.exe'):
    d=open(f,'rb').read()
    print('=====',f,len(d))
    for pat in (b'Inno Setup',b'Nullsoft',b'7z\xbc\xaf\x27\x1c',b'MSCF',b'Wise Installation',b'Setup Factory',b'InstallShield',b'MSI'):
        i=d.find(pat)
        if i>=0: print('  ',pat[:16],'at',hex(i))
    print('  head',d[:32].hex())
