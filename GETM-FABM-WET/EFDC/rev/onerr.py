import pefile
from capstone import *
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe=pefile.PE(p); data=open(p,'rb').read(); base=pe.OPTIONAL_HEADER.ImageBase
def off(va):
    rva=va-base
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.Misc_VirtualSize:
            return s.PointerToRawData+(rva-s.VirtualAddress)
md=Cs(CS_ARCH_X86,CS_MODE_32)
va=base+0x1d872
code=data[off(va):off(va)+0x90]
for i in md.disasm(code,va):
    print(f"{i.address:08x}: {i.bytes.hex():<20} {i.mnemonic} {i.op_str}")
