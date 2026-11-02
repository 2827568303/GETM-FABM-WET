import struct
d=open('vb6cc.exe','rb').read()
idx=0; n=0
while True:
    i=d.find(b'MSCF', idx)
    if i<0: break
    idx=i+1
    if i+4+8<=len(d):
        cb=struct.unpack_from('<I', d, i+8)[0]
        ok = (i+cb)<=len(d)
        print(hex(i), 'cb', cb, 'ok' if ok else 'TRUNC')
        if ok:
            open(f'payload_{n}.cab','wb').write(d[i:i+cb]); n+=1
print('valid cabs', n)
# also look for IExpress payload signature / file list
for pat in (b'MSCOMCTL', b'mscomctl', b'MSCOMCTL.OCX'):
    print(pat, d.find(pat))
