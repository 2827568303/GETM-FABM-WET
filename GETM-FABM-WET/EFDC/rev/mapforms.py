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


def find_refs(value):
    pat = struct.pack("<I", value)
    st = 0
    out = []
    while True:
        i = DATA.find(pat, st)
        if i < 0:
            break
        if i % 4 == 0:
            va = off2va(i)
            if va:
                out.append(va)
        st = i + 1
    return out


def check_classinfo(addr):
    """addr points at a dword inside a candidate class-info; return base offset if base+4 == 0x4DD8A0"""
    for delta in range(0, 0x40, 4):
        base = addr - delta
        if dw(base + 4) == 0x4DD8A0:
            return base, delta
    return None, None


TITLE_REC = 0x4DEDAC
TITLE_NAME = 0x4E4970
MAIN_REC = 0x4DF88C
MAIN_NAME = 0x4E4DD0

for label, val in (("TITLE_REC", TITLE_REC), ("TITLE_NAME", TITLE_NAME), ("MAIN_REC", MAIN_REC), ("MAIN_NAME", MAIN_NAME)):
    print("===", label, hex(val))
    for ref in find_refs(val):
        base, delta = check_classinfo(ref)
        if base:
            print("  ref@%08X  classinfo base=%08X (field +%02X)" % (ref, base, delta))
        else:
            print("  ref@%08X  (not a classinfo field)" % ref)
