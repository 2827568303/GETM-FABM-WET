import sys, pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

PRISTINE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
pe = pefile.PE(PRISTINE, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
data = open(PRISTINE, 'rb').read()
def va2off(va):
    rva = va - IB
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData):
            return s.PointerToRawData + (rva - s.VirtualAddress)

start = int(sys.argv[1], 16)
end = int(sys.argv[2], 16)
o = va2off(start)
md = Cs(CS_ARCH_X86, CS_MODE_32)
targets = []
for ins in md.disasm(data[o:o + (end - start)], start):
    if ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
        t = int(ins.op_str, 16)
        targets.append((ins.address, t))
    if ins.mnemonic == 'call' and ins.op_str.startswith('dword ptr [0x'):
        t = int(ins.op_str.split('[')[1].rstrip(']'), 16)
        targets.append((ins.address, None))
uniq = sorted(set(t for _, t in targets if t is not None))
print('# call sites: %d, unique direct targets: %d' % (len(targets), len(uniq)))
print('TARGETS=' + ','.join(hex(t) for t in uniq))
for a, t in targets:
    print('  0x%08X -> %s' % (a, hex(t) if t else 'indirect'))
