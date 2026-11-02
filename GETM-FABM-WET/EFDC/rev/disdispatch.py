import pefile
from capstone import *
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
md=Cs(CS_ARCH_X86,CS_MODE_32)
o=off(0x108BD9)
for i in md.disasm(d[o:o+0x70], base+0x108BD9):
    print(f"{i.address-base:06x}: {i.bytes.hex():<22} {i.mnemonic} {i.op_str}")
