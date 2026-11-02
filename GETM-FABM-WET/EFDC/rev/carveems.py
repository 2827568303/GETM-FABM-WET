import struct
d=open('eems1183_setup.exe','rb').read()
print('size',len(d))
idx=0; found=[]
while True:
    i=d.find(b'MSCF', idx)
    if i<0: break
    idx=i+1
    if i+12<=len(d):
        cb=struct.unpack_from('<I', d, i+8)[0]
        ok = i+cb<=len(d)
        found.append((i,cb,ok))
print('MSCF hits:', [(hex(i),cb,ok) for i,cb,ok in found][:10])
n=0
for i,cb,ok in found:
    if ok and cb>1000:
        open(f'eems_{n}.cab','wb').write(d[i:i+cb]); n+=1
print('extracted cabs', n)
# also look for tabctl32 string
for pat in (b'TABCTL32', b'tabctl32', b'MSFLXGRD', b'RICHTX32', b'MSCOMCT2'):
    print(pat, d.find(pat))
