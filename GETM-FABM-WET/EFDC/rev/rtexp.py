import pefile
from capstone import *
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
# find nearest export below each interesting rva
import bisect
exps=sorted([(e.address, (e.name or b'').decode()) for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.address])
addrs=[a for a,_ in exps]
for rva in (0x2B100,0xF7C50,0x86515,0x3D5E7,0x177B2,0x119990,0x1B2D8,0x1BFA0,0x24AD0,0x18501,0x183CB,0x19B6C,0x19854,0x1986F,0x3D529,0x3D868,0x24AD0):
    i=bisect.bisect_right(addrs, rva)-1
    name=exps[i][1] if i>=0 else '?'
    print(f'RVA {rva:#08x}  nearest export: {name} (+{rva-exps[i][0]:#x})' if i>=0 else f'RVA {rva:#08x} ?')
