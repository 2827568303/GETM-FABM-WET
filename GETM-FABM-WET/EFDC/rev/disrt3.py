import pefile
from capstone import *
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
md=Cs(CS_ARCH_X86,CS_MODE_32)
for start in (0xF7C50,0x86515):
    print('=====',hex(start))
    o=start
    for i in md.disasm(d[o:o+0x60], base+start):
        print(f"{i.address-base:06x}: {i.bytes.hex():<22} {i.mnemonic} {i.op_str}")
