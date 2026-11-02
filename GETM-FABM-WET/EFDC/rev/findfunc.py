import pefile
from capstone import *
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe=pefile.PE(p); data=open(p,'rb').read(); base=pe.OPTIONAL_HEADER.ImageBase
def off(va):
    rva=va-base
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.Misc_VirtualSize:
            return s.PointerToRawData+(rva-s.VirtualAddress)
    return None
md=Cs(CS_ARCH_X86,CS_MODE_32)
start=0x6607ef80
o=off(start)
code=data[o:o+0x280]
for i in md.disasm(code,start):
    if i.address>0x6607f1d8: break
    print(f"{i.address:08x}: {i.bytes.hex():<20} {i.mnemonic} {i.op_str}")
