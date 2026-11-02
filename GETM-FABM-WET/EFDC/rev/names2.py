import struct, pefile, re

PRISTINE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\_backup_EFDC84_orig\EFDC_Explorer8.4.orig_20261030_135832.exe"
pe = pefile.PE(PRISTINE, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
SECS = [(s.Name.rstrip(b"\x00").decode(), IB + s.VirtualAddress, s.Misc_VirtualSize,
         s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]
DATA = open(PRISTINE, "rb").read()
DATA_SEC = [s for s in SECS if s[0] == ".data"][0]


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


def astr(va, maxlen=80):
    b = rd(va, maxlen)
    if not b:
        return None
    s = b.split(b"\x00")[0]
    try:
        t = s.decode("latin1")
    except Exception:
        return None
    return t if len(t) >= 2 and all(32 <= ord(c) < 127 for c in t) else None


def find_str_vas(s):
    out = []
    b = s.encode("latin1")
    start = 0
    while True:
        i = DATA.find(b, start)
        if i < 0:
            break
        va = None
        for (n, base, vsize, rawptr, rawsize) in SECS:
            if rawptr <= i < rawptr + rawsize:
                va = base + (i - rawptr)
                break
        out.append((i, va))
        start = i + 1
    return out


def scan_ptr(target):
    """find dwords in .data equal to target"""
    hits = []
    base, vsize, rawptr, rawsize = DATA_SEC[1], DATA_SEC[2], DATA_SEC[3], DATA_SEC[4]
    blob = DATA[rawptr:rawptr + rawsize]
    pat = struct.pack("<I", target)
    st = 0
    while True:
        i = blob.find(pat, st)
        if i < 0:
            break
        if i % 4 == 0:
            hits.append(base + i)
        st = i + 1
    return hits


TARGETS = ["frmEFDC_Explorer", "frmEFDC_Explorer_TitleForm", "frmEFDC_Run", "frmActivation"]
for name in TARGETS:
    print("=====", name)
    for (off, va) in find_str_vas(name):
        print("  str @ off %08X va %s" % (off, hex(va) if va else "?"))
        if va:
            ptrs = scan_ptr(va)
            for p in ptrs:
                print("     ptr in .data @ %08X" % p)
                # dump surroundings
                for d in (-12, -8, -4, 0, 4, 8, 12, 16, 20, 24):
                    v = dw(p + d)
                    note = ""
                    if v and 0x400000 <= v < 0x4E0000:
                        s = astr(v)
                        if s and len(s) > 2:
                            note = " -> str " + s
                        else:
                            t = dw(v + 4)
                            if t == 0x4DD8A0:
                                note = " -> CLASSINFO (objtbl ptr at +4)"
                    print("        [%+3d] %08X%s" % (d, v, note))
