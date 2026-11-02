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


def in_image(x):
    return x is not None and IB <= x < IB + 0x1400000


def astr(va, maxlen=60):
    b = rd(va, maxlen)
    if not b:
        return None
    s = b.split(b"\x00")[0]
    try:
        t = s.decode("latin1")
    except Exception:
        return None
    if len(t) >= 2 and all(32 <= ord(c) < 127 for c in t):
        return t
    return None


def wstr(va, maxlen=120):
    b = rd(va, maxlen * 2)
    if not b:
        return None
    out = []
    for i in range(0, len(b) - 1, 2):
        c = struct.unpack("<H", b[i:i + 2])[0]
        if c == 0:
            break
        if c < 32 or c > 0x2122:
            return None
        out.append(chr(c))
    t = "".join(out)
    return t if len(t) >= 2 else None


VBH = 0x4528C4
SUBM = dw(VBH + 0x2C)
PROJ = dw(VBH + 0x30)
print("lpSubMain=%08X lpProjectData=%08X formCount=%d external=%d thunk=%d gui=%08X ext=%08X comreg=%08X"
      % (SUBM, PROJ, u16(VBH + 0x44), u16(VBH + 0x46), dw(VBH + 0x48), dw(VBH + 0x4C), dw(VBH + 0x50), dw(VBH + 0x54)))
print("projDesc str:", astr(dw(VBH + 0x58)), "| exeName:", astr(dw(VBH + 0x5C)),
      "| help:", astr(dw(VBH + 0x60)), "| name:", astr(dw(VBH + 0x64)))

print("--- ProjectData dwords @ %08X" % PROJ)
for i in range(16):
    v = dw(PROJ + i * 4)
    tag = ""
    if in_image(v):
        s = astr(v)
        if s:
            tag = "astr:" + s
        else:
            w = wstr(v)
            if w:
                tag = "wstr:" + w
    print("  +0x%02X = %08X %s" % (i * 4, v, tag))

objtbl = dw(PROJ + 0x04)
print("\n--- ObjectTable @ %08X" % objtbl)
for i in range(12):
    v = dw(objtbl + i * 4)
    print("  +0x%02X = %08X" % (i * 4, v))

arr = dw(objtbl)
cnt = dw(objtbl + 0x04)
print("\nobjArray=%08X count=%s" % (arr, cnt))
names = []
for i in range(0, 400):
    p = dw(arr + i * 8)
    if not in_image(p):
        print("  stop at %d (ptr %s)" % (i, p))
        break
print("dumped until stop")
