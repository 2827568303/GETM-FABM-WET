import pefile
from capstone import *
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\MSVBVM60_picpatch.dll"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
md=Cs(CS_ARCH_X86,CS_MODE_32)
start=0x1D6E0
o=off(start)
print('module base',hex(base))
for i in md.disasm(d[o:o+0x140], base+start):
    rva=i.address-base
    mark=' <<< our patch' if rva==0x1D761 else ''
    print(f"{rva:06x}: {i.bytes.hex():<22} {i.mnemonic} {i.op_str}{mark}")
