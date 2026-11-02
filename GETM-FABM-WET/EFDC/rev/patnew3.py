import pefile
p=r"C:\EFDC84_LIC\vb6\MSCOMCTL.OCX"
d=bytearray(open(p,'rb').read())
pe=pefile.PE(data=bytes(d))
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
o=off(0x45B02)
print('before:', d[o:o+16].hex())
assert d[o]==0x55 and d[o+1]==0x8b and d[o+2]==0xec
d[o:o+5]=bytes.fromhex('31c0c20400')
open(p,'wb').write(bytes(d))
print('patched Load @RVA 0x45B02')
