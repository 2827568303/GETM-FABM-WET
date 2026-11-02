import pefile
p=r"C:\EFDC84_LIC\vb6\MSCOMCTL.OCX"
d=bytearray(open(p,'rb').read())
pe=pefile.PE(data=bytes(d))
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
o=off(0x45400)
d[o:o+6]=bytes.fromhex('0f844cd50000')
o=off(0x45437)
d[o:o+8]=bytes.fromhex('b801000000c20400')
open(p,'wb').write(bytes(d))
print('restored branch; validator -> always 1')
print('check:', bytes(d[off(0x45400):off(0x45400)+6]).hex(), bytes(d[off(0x45437):off(0x45437)+8]).hex())
