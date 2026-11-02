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


def dump(va, n=20, label=""):
    print("--- %s @ %08X ---" % (label, va))
    for i in range(n):
        v = dw(va + i * 4)
        note = ""
        if v is not None and 0x400000 <= v < 0x1620000:
            s = astr(v)
            if s and len(s) >= 3:
                note = ' -> "%s"' % s
            elif dw(v + 4) == 0x4DD8A0 if dw(v) is not None else False:
                note = " -> CLASSINFO(+4=objtbl)"
        print("  +%02X %08X%s" % (i * 4, v, note))


dump(0x4D5204, 16, "title classinfo (pushed at 0x156AD58)")
dump(0x4E1CEC, 16, "TitleForm rec +8")
dump(0x4E334C, 20, "frmEFDC_Explorer rec +8")
