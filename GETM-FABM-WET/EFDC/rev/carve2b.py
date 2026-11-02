import struct
d=open('vb6rtlib.exe','rb').read()
print('size',len(d),'head',d[:2])
idx=0
while True:
    i=d.find(b'MSCF', idx)
    if i<0: break
    idx=i+1
    if i+12<=len(d):
        cb=struct.unpack_from('<I', d, i+8)[0]
        if i+cb<=len(d):
            fn=f'rtlib_{i:x}.cab'
            open(fn,'wb').write(d[i:i+cb]); print('cab at',hex(i),'size',cb,'->',fn)
