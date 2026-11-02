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


def off2va(o):
    for (n, base, vsize, rawptr, rawsize) in SECS:
        if rawptr <= o < rawptr + rawsize:
            return base + (o - rawptr)
    return None


def rd(va, n):
    o = va2off(va)
    return None if o is None else DATA[o:o + n]


def dw(va):
    b = rd(va, 4)
    return None if not b or len(b) < 4 else struct.unpack("<I", b)[0]


pat = struct.pack("<I", 0x4DD8A0)
bases = []
st = 0
while True:
    i = DATA.find(pat, st)
    if i < 0:
        break
    va = off2va(i)
    if va and (va - 4) % 4 == 0:
        bases.append(va - 4)
    st = i + 1
bases = sorted(set(bases))
print("classinfo candidates:", len(bases))
for idx, b in enumerate(bases):
    f0 = dw(b)
    print("%3d %08X  +0=%08X +8=%08X +C=%08X +18=%08X +24=%08X" % (idx, b, f0, dw(b + 8), dw(b + 0xC), dw(b + 0x18), dw(b + 0x24)))

print()
if 0x4D5204 in bases:
    print("0x4D5204 index =", bases.index(0x4D5204))
else:
    print("0x4D5204 not in candidates")
