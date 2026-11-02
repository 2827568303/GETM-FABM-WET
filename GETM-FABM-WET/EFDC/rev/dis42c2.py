import pefile
from capstone import *
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read()
print('size',len(d))
o=0x42c9a0-0x400000
print('off',hex(o),'bytes',d[o:o+16].hex())
md=Cs(CS_ARCH_X86,CS_MODE_32)
n=0
for i in md.disasm(d[o:o+0xC0], 0x42c9a0):
    print(f"{i.address:06x}: {i.bytes.hex():<22} {i.mnemonic} {i.op_str}")
    n+=1
print('insns',n)
