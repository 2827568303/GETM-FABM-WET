import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
pe = pefile.PE(r"C:\Windows\SysWOW64\MSVBVM60.DLL")
base = pe.OPTIONAL_HEADER.ImageBase
data = pe.get_memory_mapped_image()
md = Cs(CS_ARCH_X86, CS_MODE_32)

def dis(rva, n=24):
    code = data[rva:rva+0x80]
    print(f"--- {rva:#x} ---")
    for ins in md.disasm(code, base+rva):
        if ins.address >= base+rva+n: break
        print(f"  {ins.address:#x}: {ins.mnemonic} {ins.op_str}")

dis(0x38460, 24)
print()
# exports mentioning pic/load
names = [(e.address, e.name.decode() if e.name else '?') for e in pe.DIRECTORY_ENTRY_EXPORT.symbols]
for a, n in names:
    ln = n.lower()
    if 'pic' in ln or 'load' in ln or 'raise' in ln or 'error' in ln:
        print(f"0x{a:06x} {n}")
