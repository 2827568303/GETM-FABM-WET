import struct, pefile, sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

PRISTINE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\_backup_EFDC84_orig\EFDC_Explorer8.4.orig_20261030_135832.exe"
pe = pefile.PE(PRISTINE, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
SECS = [(s.Name.rstrip(b"\x00").decode(), IB + s.VirtualAddress, s.Misc_VirtualSize,
         s.PointerToRawData, s.SizeOfRawData, s.Characteristics) for s in pe.sections]
DATA = open(PRISTINE, "rb").read()
TEXT = [s for s in SECS if s[0] == ".text"][0]


def va2off(va):
    for (n, base, vsize, rawptr, rawsize, ch) in SECS:
        if base <= va < base + max(vsize, rawsize):
            o = rawptr + (va - base)
            if 0 <= o < len(DATA):
                return o
    return None


def rd(va, n):
    o = va2off(va)
    return None if o is None else DATA[o:o + n]


def dw(va):
    b = rd(va, 4)
    return None if not b or len(b) < 4 else struct.unpack("<I", b)[0]


def astr(va, maxlen=200):
    b = rd(va, maxlen)
    if not b:
        return None
    return b.split(b"\x00")[0].decode("latin1", "replace")


def find_imm_refs(value):
    """find all 'push imm32' (0x68) occurrences of value and any dword equal to value in .text"""
    hits = []
    base, vsize, rawptr, rawsize, ch = TEXT[1], TEXT[2], TEXT[3], TEXT[4], TEXT[5]
    blob = DATA[rawptr:rawptr + rawsize]
    pat = struct.pack("<I", value)
    st = 0
    while True:
        i = blob.find(pat, st)
        if i < 0:
            break
        va = base + i
        prefix = blob[max(0, i - 1):i]
        hits.append((va, prefix.hex()))
        st = i + 1
    return hits


md = Cs(CS_ARCH_X86, CS_MODE_32)


def dis(va, count=40, back=0):
    start = va - back
    off = va2off(start)
    code = DATA[off:off + count * 8]
    print("--- 0x%X ---" % start)
    for ins in md.disasm(code, start):
        mark = " <<<" if abs(ins.address - va) < 8 else ""
        print("  0x%08X  %-20s %s%s" % (ins.address, ins.bytes.hex(), ins.mnemonic + " " + ins.op_str, mark))
        if ins.address > va + 200:
            break


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if arg.startswith("@"):
            target = int(arg[1:], 16)
            print("str @ 0x%X = %r" % (target, astr(target)))
            for (va, pre) in find_imm_refs(target):
                print("  ref dword @ 0x%X (prev byte %s)" % (va, pre))
        else:
            va = int(arg, 16)
            dis(va, 60, 24)
