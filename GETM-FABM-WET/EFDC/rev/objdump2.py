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


def u16(va):
    b = rd(va, 2)
    return None if not b else struct.unpack("<H", b)[0]


def astr(va, maxlen=64):
    b = rd(va, maxlen)
    if not b:
        return None
    s = b.split(b"\x00")[0]
    try:
        t = s.decode("latin1")
    except Exception:
        return None
    return t if len(t) >= 2 and all(32 <= ord(c) < 127 for c in t) else None


def wstr(va, maxlen=80):
    b = rd(va, maxlen * 2)
    if not b:
        return None
    out = []
    for i in range(0, len(b) - 1, 2):
        c = struct.unpack("<H", b[i:i + 2])[0]
        if c == 0:
            break
        if c < 32 or c > 0x2100:
            return None
        out.append(chr(c))
    t = "".join(out)
    return t if len(t) >= 2 else None


def note(v):
    if v is None:
        return ""
    if v == 0x4DD8A0:
        return " <PROJ+4 objtbl?>"
    if 0x4C0000 <= v < 0x500000:
        s = astr(v)
        if s:
            return " astr:" + s
        w = wstr(v)
        if w:
            return " wstr:" + w
        if dw(v + 4) == 0x4DD8A0:
            return " CLASSINFO?"
    if 0x400000 <= v < 0x1620000:
        s = astr(v)
        if s:
            return " astr:" + s
        w = wstr(v)
        if w:
            return " wstr:" + w
    return ""


start, end, step = 0x1626A00, 0x1626C80, 4
print("--- dump %08X..%08X ---" % (start, end))
for va in range(start, end, step):
    v = dw(va)
    print("%08X: %08X%s" % (va, v, note(v)))
