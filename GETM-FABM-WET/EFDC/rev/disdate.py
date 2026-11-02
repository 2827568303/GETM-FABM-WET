import pefile
from capstone import *
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
md=Cs(CS_ARCH_X86,CS_MODE_32)
for start,n in ((0x82E240,0x80),(0x82E2C0,0x80)):
    print('=====',hex(start))
    for i in md.disasm(d[start-base:start-base+n], start):
        print(f"{i.address-base:06x}: {i.bytes.hex():<22} {i.mnemonic} {i.op_str}")
