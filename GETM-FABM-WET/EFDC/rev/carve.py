import struct
d=open('vb6cc.exe','rb').read()
i=d.find(b'MSCF')
print('MSCF at', hex(i))
if i>=0:
    cb=struct.unpack_from('<I', d, i+8)[0]
    print('cbCabinet', cb, 'file len', len(d))
    end=min(len(d), i+cb)
    open('payload.cab','wb').write(d[i:end])
    print('wrote payload.cab', end-i)
