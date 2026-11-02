import struct, pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

PRISTINE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\_backup_EFDC84_orig\EFDC_Explorer8.4.orig_20261030_135832.exe"
pe = pefile.PE(PRISTINE, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
SECS = [(s.Name.rstrip(b"\x00").decode(), IB + s.VirtualAddress, s.Misc_VirtualSize,
         s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]
DATA = open(PRISTINE, "rb").read()


def va2off(va):
    for (n, base, vsize, rawptr, rawsize) in SECS:
        if base <= va < base + max(vsize, rawsize):
            o = rawptr + (va - base)
            if 0 <= o < len(DATA):
                return o
    return None


md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

START, END = 0x81C4C0, 0x81D900
off = va2off(START)
code = DATA[off:off + (END - START) + 0x400]

sites = []
for ins in md.disasm(code, START):
    if ins.address > END:
        break
    if ins.mnemonic == 'call':
        if ins.op_str.startswith('0x'):
            sites.append((ins.address, int(ins.op_str, 16), 'direct'))
        elif ins.op_str.startswith('dword ptr [0x'):
            t = int(ins.op_str.split('[')[1].split(']')[0], 16)
            sites.append((ins.address, t, 'thunk'))

print("call sites:", len(sites))
for s in sites:
    print("  site %08X -> %08X (%s)" % s)

uniq = sorted(set(t for _, t, _ in sites))
print("unique targets:", len(uniq))
js = "var TARGETS = [" + ",".join("0x%X" % t for t in uniq) + "];\n"
js += "var BODY_START=0x%X, BODY_END=0x%X;\n" % (START, END + 0x400)
open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\targets.js", "w").write(js)
print("wrote targets.js")
