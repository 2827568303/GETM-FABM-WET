import pefile, struct, uuid
p=r"C:\EFDC84_LIC\mscomctl.ocx"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase
d=open(p,'rb').read()
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
rva=0xAEB38
o=off(rva)
print('at 0xAEB38:', d[o:o+64].hex())
for i in range(0,8):
    ent=rva+i*8
    oo=off(ent)
    ptr=struct.unpack_from('<I',d,oo)[0]
    w=struct.unpack_from('<H',d,oo+4)[0]
    print(f'entry {i}: rva {ent:#x} ptr={ptr:#x} w={w:#x}')
    if ptr and 0x27580000<=ptr<0x27580000+0x100000:
        pr=ptr-base
        po=off(pr)
        if po: print('    guid bytes', d[po:po+16].hex())
