import pefile
from capstone import *
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
pe=pefile.PE(exe); base=pe.OPTIONAL_HEADER.ImageBase; d=open(exe,'rb').read()
def rd(rva,n):
    o=rva-base
    return d[o:o+n]
md=Cs(CS_ARCH_X86,CS_MODE_32)
start=0x42c9a0
o=start-base
for i in md.disasm(d[o:o+0xC0], start):
    print(f"{i.address-base:06x}: {i.bytes.hex():<22} {i.mnemonic} {i.op_str}")
