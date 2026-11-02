import pefile
from capstone import *
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
pe=pefile.PE(exe); base=pe.OPTIONAL_HEADER.ImageBase; d=open(exe,'rb').read()
def off(va):
    r=va-base
    for s in pe.sections:
        if s.VirtualAddress<=r<s.VirtualAddress+s.SizeOfRawData:
            return s.PointerToRawData+(r-s.VirtualAddress)
    return None
md=Cs(CS_ARCH_X86,CS_MODE_32)
for start in (0x4D16A28,):
    o=off(start)
    print('=== ',hex(start), 'file off', hex(o) if o else None)
    if o is None: continue
    for i in md.disasm(d[o:o+0x60], start):
        print(f"{i.address-base:06x}: {i.bytes.hex():<22} {i.mnemonic} {i.op_str}")
