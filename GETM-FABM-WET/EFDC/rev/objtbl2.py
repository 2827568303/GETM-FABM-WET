import struct, pefile

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


def rd(va, n):
    o = va2off(va)
    return None if o is None else DATA[o:o + n]


def dw(va):
    b = rd(va, 4)
    return None if not b or len(b) < 4 else struct.unpack("<I", b)[0]


def astr(va, maxlen=64):
    b = rd(va, maxlen)
    if not b:
        return None
    s = b.split(b"\x00")[0]
    try:
        t = s.decode("latin1")
    except Exception:
        return None
    return t if t and all(32 <= ord(c) < 127 for c in t) else None


records = []
va = 0x4DD90C
while va < 0x4DFF00:
    name = astr(dw(va)) if dw(va) else None
    if not name or len(name) < 3:
        break
    rec = [dw(va + 4 * i) for i in range(0x30 // 4)]
    records.append((va, name, rec))
    va += 0x30

print("records:", len(records))
print("%-8s %-40s %s" % ("addr", "name", "fields"))
for addr, name, rec in records:
    print("%08X %-40s %s" % (addr, name, " ".join("%08X" % x for x in rec)))

print()
for key in ("frmEFDC_Explorer", "frmEFDC_Explorer_TitleForm", "frmActivation"):
    for addr, name, rec in records:
        if name == key:
            print("MATCH", key, "rec@%08X" % addr, " ".join("%08X" % x for x in rec))
