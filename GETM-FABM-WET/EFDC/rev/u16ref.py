import struct, pefile, sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

PRISTINE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\_backup_EFDC84_orig\EFDC_Explorer8.4.orig_20261030_135832.exe"
pe = pefile.PE(PRISTINE, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
SECS = [(s.Name.rstrip(b"\x00").decode(), IB + s.VirtualAddress, s.Misc_VirtualSize,
         s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]
DATA = open(PRISTINE, "rb").read()
TEXT = [s for s in SECS if s[0] == ".text"][0]
md = Cs(CS_ARCH_X86, CS_MODE_32)


def va2off(va):
    for (n, base, vsize, rawptr, rawsize) in SECS:
        if base <= va < base + max(vsize, rawsize):
            o = rawptr + (va - base)
            if 0 <= o < len(DATA):
                return o
    return None


def off2va(off):
    for (n, base, vsize, rawptr, rawsize) in SECS:
        if rawptr <= off < rawptr + rawsize:
            return base + (off - rawptr)
    return None


def rd(va, n):
    o = va2off(va)
    return None if o is None else DATA[o:o + n]


def find_u16(pattern):
    b = pattern.encode("utf-16-le")
    out = []
    st = 0
    while True:
        i = DATA.find(b, st)
        if i < 0:
            break
        out.append(off2va(i))
        st = i + 1
    return [x for x in out if x]


def refs_in_text(value):
    hits = []
    base, vsize, rawptr, rawsize = TEXT[1], TEXT[2], TEXT[3], TEXT[4]
    blob = DATA[rawptr:rawptr + rawsize]
    pat = struct.pack("<I", value)
    st = 0
    while True:
        i = blob.find(pat, st)
        if i < 0:
            break
        hits.append(base + i)
        st = i + 1
    return hits


def dis(va, count=45, back=30):
    start = va - back
    o = va2off(start)
    if o is None:
        print("  <no code at %X>" % start)
        return
    print("  --- code @ 0x%X ---" % start)
    n = 0
    for ins in md.disasm(DATA[o:o + count * 8], start):
        mark = "  <<<" if abs(ins.address - va) < 10 else ""
        print("    0x%08X  %-18s %s %s%s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str, mark))
        n += 1
        if n > count:
            break


if __name__ == "__main__":
    for pat in sys.argv[1:]:
        print("=== pattern %r" % pat)
        for va in find_u16(pat):
            print("  u16 str @ 0x%X" % va)
            for r in refs_in_text(va):
                print("   ref @ 0x%X" % r)
                dis(r, 30, 24)
