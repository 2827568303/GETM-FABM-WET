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
for start,end in [(0x6601d700,0x6601d800),(0x66042380,0x66042440)]:
    print(f"===== {start:#x} =====")
    o=off(start); code=data[o:o+(end-start)]
    for i in md.disasm(code,start):
        print(f"{i.address:08x}: {i.bytes.hex():<20} {i.mnemonic} {i.op_str}")
