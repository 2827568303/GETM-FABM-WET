import pefile
from capstone import *
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
md=Cs(CS_ARCH_X86,CS_MODE_32)
start=0x81C9C0
o=start-base
print('orig bytes 0x81CA1F:', d[0x81CA1F-base:0x81CA1F-base+8].hex())
for i in md.disasm(d[o:o+0xB0], start):
    print(f"{i.address-base:06x}: {i.bytes.hex():<22} {i.mnemonic} {i.op_str}")
