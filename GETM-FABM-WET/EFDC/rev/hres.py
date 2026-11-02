import pefile
from capstone import *
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe=pefile.PE(p); data=open(p,'rb').read(); base=pe.OPTIONAL_HEADER.ImageBase
def off(va):
    rva=va-base
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.Misc_VirtualSize:
            return s.PointerToRawData+(rva-s.VirtualAddress)
va=base+0x427c2
o=off(va); md=Cs(CS_ARCH_X86,CS_MODE_32)
for i in md.disasm(data[o:o+0x60], va):
    print(f"{i.address:08x}: {i.bytes.hex():<20} {i.mnemonic} {i.op_str}")
print('...')
for i in md.disasm(data[o:o+0x200], va):
    if i.mnemonic=='ret': print('RET at', hex(i.address), i.bytes.hex())
