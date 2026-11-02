import struct, pefile, sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

PRISTINE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
pe = pefile.PE(PRISTINE, fast_load=False)
IB = pe.OPTIONAL_HEADER.ImageBase
iat = {}
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    dll = entry.dll.decode()
    for imp in entry.imports:
        if imp.address:
            iat[imp.address] = (dll, (imp.name or b'ord%d' % imp.ordinal).decode('latin1'))

print('=== IAT slots used by license code ===')
for a in [0x401140,0x40118c,0x4011ec,0x401210,0x4012a0,0x4012a4,0x401308,0x4013f4,0x401458,
          0x401514,0x401534,0x4015b4,0x401188,0x4016a0,0x40174c,0x4012ac,0x401170,0x40112c]:
    print('  0x%X -> %s' % (a, iat.get(a, 'NOT-IN-IAT')))

print()
print('=== MSVBVM60 around +0x5908 ===')
d = None
for path in (r"C:\Windows\SysWOW64\MSVBVM60.DLL", r"C:\Windows\System32\MSVBVM60.DLL"):
    try:
        d = open(path,'rb').read()
        print('loaded', path, len(d))
        break
    except Exception as e:
        print('fail', path, e)
if d:
    mpe = pefile.PE(path, fast_load=True)
    mib = mpe.OPTIONAL_HEADER.ImageBase
    print('image base', hex(mib))
    def off_of(va):
        rva = va - mib
        for s in mpe.sections:
            if s.VirtualAddress <= rva < s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData):
                return s.PointerToRawData + (rva - s.VirtualAddress)
        return None
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    start_va = mib + 0x58c0
    o = off_of(start_va)
    for ins in md.disasm(d[o:o+140], start_va):
        print('  0x%08X  %-16s %-8s %s' % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))
