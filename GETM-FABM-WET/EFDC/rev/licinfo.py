import pefile
from capstone import *
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\vb6cab2\mscomctl.ocx"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
md=Cs(CS_ARCH_X86,CS_MODE_32)
for rva,n in ((0x82131,'GetLicInfo'),(0x82177,'RequestLicKey')):
    print('=====',n,hex(rva))
    o=off(rva)
    for i in md.disasm(d[o:o+0x60], base+rva):
        print(f"{i.address-base:06x}: {i.bytes.hex():<20} {i.mnemonic} {i.op_str}")
