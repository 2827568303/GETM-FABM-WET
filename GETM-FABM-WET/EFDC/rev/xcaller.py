import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
P = r"C:\Windows\SysWOW64\MSVBVM60.DLL"
d = open(P,'rb').read()
pe = pefile.PE(P, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
def off(va):
    rva = va - IB
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData):
            return s.PointerToRawData + (rva - s.VirtualAddress)
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True
start = IB + 0x1d700
o = off(start)
print('=== MSVBVM60 +0x1d700 ===')
for ins in md.disasm(d[o:o+0x120], start):
    print('  0x%08X  %-18s %-8s %s' % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))
