import pefile
p=r"C:\EFDC84_LIC\mscomctl.ocx"
d=bytearray(open(p,'rb').read())
pe=pefile.PE(data=bytes(d))
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
o=off(0x34E35)
print('Load prologue:', d[o:o+16].hex())
assert d[o]==0x55 and d[o+1]==0x8b and d[o+2]==0xec, 'unexpected prologue'
d[o:o+5]=bytes.fromhex('31c0c20400')
open(p,'wb').write(bytes(d))
print('patched IPersistStreamInit::Load @RVA 0x34E35 -> xor eax,eax; ret 4')
