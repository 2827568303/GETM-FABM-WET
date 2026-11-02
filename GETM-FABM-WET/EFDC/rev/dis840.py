import pefile
from capstone import *
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
pe=pefile.PE(exe); base=pe.OPTIONAL_HEADER.ImageBase; d=open(exe,'rb').read()
def rd(rva,n):
    o=rva-base
    return d[o:o+n]
# find nearest prologue before 0x840223
start=None
for va in range(0x840223,0x83F000,-1):
    b=rd(va,3)
    if b==b'\x55\x8b\xec':
        start=va; break
print('function start:', hex(start) if start else None)
md=Cs(CS_ARCH_X86,CS_MODE_32)
o=start-base
for i in md.disasm(d[o:o+0x120], start):
    mark=''
    if i.address==0x840223: mark='   <<< call 0x156AB70'
    print(f"{i.address-base:06x}: {i.bytes.hex():<20} {i.mnemonic} {i.op_str}{mark}")
    if i.address>0x840260: break
