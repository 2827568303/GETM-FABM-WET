import glob, os, pefile
from capstone import *
cands=glob.glob(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\*.exe")
print('backup candidates:', cands)
p=cands[0] if cands else None
if p:
    pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
    print('file',p,'size',len(d))
    md=Cs(CS_ARCH_X86,CS_MODE_32)
    start=0x822430
    o=start-base
    for i in md.disasm(d[o:o+0x60], start):
        print(f"{i.address-base:06x}: {i.bytes.hex():<22} {i.mnemonic} {i.op_str}")
    print('bytes at 0x822450:', d[0x822450-base:0x822450-base+8].hex())
    print('bytes at 0x81CA1F:', d[0x81CA1F-base:0x81CA1F-base+8].hex())
