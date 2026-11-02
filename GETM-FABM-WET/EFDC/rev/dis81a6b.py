import pefile
from capstone import *
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
md=Cs(CS_ARCH_X86,CS_MODE_32)
start=0x81A63D
for i in md.disasm(d[start-base:start-base+0xA0], start):
    print(f"{i.address-base:06x}: {i.bytes.hex():<22} {i.mnemonic} {i.op_str}")
