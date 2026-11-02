import pefile
from capstone import *
p=r"C:\EFDC84_LIC\mscomctl.ocx"
pe=pefile.PE(p)
base=pe.OPTIONAL_HEADER.ImageBase
exps={e.name.decode():e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
print('ImageBase',hex(base),'exports',list(exps)[:8])
rva=exps['DllGetClassObject']
print('DllGetClassObject RVA', hex(rva))
def off(r):
    for s in pe.sections:
        if s.VirtualAddress<=r<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(r-s.VirtualAddress)
d=open(p,'rb').read(); o=off(rva)
md=Cs(CS_ARCH_X86,CS_MODE_32)
for i in md.disasm(d[o:o+0x180], base+rva):
    print(f"{i.address-base:06x}: {i.bytes.hex():<20} {i.mnemonic} {i.op_str}")
