import pefile
from capstone import *
p=r"C:\EFDC84_LIC\vb6\MSCOMCTL.OCX"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
md=Cs(CS_ARCH_X86,CS_MODE_32)
for rva,n in ((0x453CE,'CreateInstanceLic'),(0x812F3,'GetLicInfo')):
    print('=====',n,hex(rva))
    o=off(rva)
    for i in md.disasm(d[o:o+0x70], base+rva):
        print(f"{i.address-base:06x}: {i.bytes.hex():<20} {i.mnemonic} {i.op_str}")
