d=open('eems1183_setup.exe','rb').read()
sigs={
 '7z':b'7z\xbc\xaf\x27\x1c','zip':b'PK\x03\x04','cab':b'MSCF','gzip':b'\x1f\x8b\x08',
 'zstd':b'\x28\xb5\x2f\xfd','lzma':b'\x5d\x00\x00','rar':b'Rar!\x1a\x07','msi':b'\xd0\xcf\x11\xe0',
 'bzip2':b'BZh','xz':b'\xfd7zXZ','nsis':b'\xef\xbe\xad\xde'
}
for name,s in sigs.items():
    idx=[]; i=d.find(s)
    while i>=0 and len(idx)<5:
        idx.append(i); i=d.find(s,i+1)
    print(f'{name:6s}: {[hex(x) for x in idx]}')
print('--- region after PE (~0x3aba00) ---')
print(d[0x3aba00:0x3aba40].hex())
print('--- around 0x8579000 (first 7z) ---')
print(d[0x8579b80:0x8579bc0].hex())
