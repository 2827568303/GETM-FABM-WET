import struct
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(p,'rb').read(); base=0x400000
target=0x81D870
hits=[]
for i in range(len(d)-5):
    if d[i]==0xE8:
        rel=struct.unpack_from('<i',d,i+1)[0]
        if (base+i+5+rel)&0xffffffff==target: hits.append(base+i)
print('callers of 0x81D870:', [hex(x) for x in hits][:10])
# show the disassembly before the first caller
import pefile
from capstone import *
pe=pefile.PE(p); md=Cs(CS_ARCH_X86,CS_MODE_32)
for c in hits[:1]:
    start=c-0x60
    print('=== context before', hex(c))
    for i in md.disasm(d[start-base:start-base+0x70], start):
        mark=' <<< call' if i.address==c else ''
        print(f"{i.address-base:06x}: {i.bytes.hex():<22} {i.mnemonic} {i.op_str}{mark}")
