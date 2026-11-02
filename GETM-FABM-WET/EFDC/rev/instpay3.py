d=open('eems1183_setup.exe','rb').read()
def hx(off,n=64):
    b=d[off:off+n]
    return ' '.join(f'{x:02x}' for x in b)
print('before names (0x3AEE60..0x3AEF20):')
for o in range(0x3AEE60,0x3AEF20,16):
    print(f'{o:08x}  {hx(o,16)}')
print()
print('names start region:')
i=d.find(b'Triangle.dll')
print('Triangle.dll at', hex(i))
print('ctx before:', d[i-64:i].hex())
print('after names block:')
# find end of the names block (first null)
j=i
while j<len(d) and d[j]!=0: j+=1
print('names end at', hex(j), 'next 128 bytes:', d[j:j+128].hex())
