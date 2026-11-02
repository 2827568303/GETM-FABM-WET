d=open('eems1251_setup.exe','rb').read()
base=0xD6200
print('payload head:', d[base:base+64].hex())
print('bytes  :', d[base:base+32])
# look for known signatures in first 2MB after payload start
sigs={'7z':b'7z\xbc\xaf\x27\x1c','lzma':b'\x5d\x00\x00','zstd':b'\x28\xb5\x2f\xfd','gzip':b'\x1f\x8b\x08','xz':b'\xfd7zXZ','cab':b'MSCF','zip':b'PK\x03\x04'}
for k,s in sigs.items():
    i=d.find(s, base, base+4*1024*1024)
    print(f'{k:5s}: {hex(i) if i>=0 else None}')
# strings in first 1MB of payload
import re
seg=d[base:base+1024*1024]
strs=re.findall(rb'[ -~]{6,}', seg)
print('sample strings:', [s.decode() for s in strs[:20]])
